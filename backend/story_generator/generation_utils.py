import constants

# Text Generation
from ranking_utils import score_text, sort_scores
import torch
from math import ceil

# Image retrieval
import os
import pandas as pd
import numpy as np
from PIL import Image

# TF-IDF + LSA
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from helper_functions import generate_prompt

# Image style transfer
from torchvision import transforms
from style_transfer.transformer_net import TransformerNet


def _last_stop_token(tokenizer, tokens_output):
    end_of_sentence_tokens = tokenizer.encode([".", ";", "?", "!", ".\""])

    # Default ending at the end of generation
    index_last_eos = len(tokens_output) - 1
    # Check eos_token in reverse to find a [". ; ." ? !] ending.
    for i in range(len(tokens_output)-1, -1, -1):
        token = tokens_output[i]
        for stop_stoken in end_of_sentence_tokens:
            if token == stop_stoken:
                index_last_eos = i
                return index_last_eos

    return index_last_eos


def _sample_sequence(model, tokenizer, prompts, max_length, num_return_sequences, device, first_idx=False):
    """
    One forward pass generation that ends at end of sentence mark. 

    Args:
        model (PyTorch): Fine-tuned GPT2 model for generation.
        tokenizer (PyTorch): GPT2 tokenizer for generation.
        prompts (list): List of starting sentences e.g [title 1, title 2].
        max_length (int): How long the generated text should be. 
        num_return_sequences (int): Number of generated texts to return per prompt. 
        first_idx (bool): True if want to remove given prompt from the returned generation.

    Returns:
        List of num_return_sequences generated texts, each with approximate length max_length.

    Uses hugginface generate (https://huggingface.co/transformers/main_classes/model.html?highlight=generate#transformers.TFPreTrainedModel.generate)
    With tokenizer.padding size = left, otherwise generation is random (issue https://github.com/huggingface/transformers/issues/3021)
    """

    encodings_dict = tokenizer(prompts, padding='longest')
    prompts_ids = torch.tensor(
        encodings_dict['input_ids'], device=device, dtype=torch.long)
    attantion_masks = torch.tensor(
        encodings_dict['attention_mask'], device=device, dtype=torch.long)
    first_idx = len(prompts_ids[0]) if first_idx else 0
    # assert any(mask == 0 for mask in attantion_masks[:, -1]
    #            ) is False, "Attention masks are on the right, add tokenizer.padding_side = 'left' to fix."

    sample_outputs = model.generate(
        prompts_ids,  # Long tensor of size (batch_size, max_prompt_length)
        do_sample=True,  # activate top-k, top-p sampling
        max_length=max_length+first_idx,
        min_length=max_length if first_idx else 10,
        top_k=constants.TOP_K,
        top_p=constants.TOP_P,
        temperature=constants.TEMPERATURE,
        repetition_penalty=1.0,  # no penalty
        num_return_sequences=num_return_sequences,
        attention_mask=attantion_masks,
        pad_token_id=tokenizer.pad_token_id,
    )  # returns tensor of shape (len(prompts)*num_return_sequences x max_length)

    indices_last_eos = map(
        lambda sample: _last_stop_token(tokenizer, sample), sample_outputs)
    generated = np.array(list(map(lambda sample, idx: tokenizer.decode(
        sample[first_idx:idx + 1], skip_special_tokens=True), sample_outputs, indices_last_eos)))
    return generated


def sample_stories_texts(model, preset_model, tokenizer, num_samples, max_length, lsa_embedder, use_user_prompts=None, inter_ranking=10, tokens_each_generation=constants.NUM_TOKENS_PER_GENERATION):
    """
    Generates num_samples stories each round, returns num_samples generated texts with/out ranking.

    Defaults to generating from pre-set prompts, and generating tokens_each_generation new tokens sequentially.
    if use_user_prompts != None, will generate from user's given prompt/s instead.

    Defaults to do intermediate ranking after each sequential generation, and choose the best inter_ranking out of num_samples.

    Args:
        model (PyTorch): Fine-tuned GPT2 model for generation.
        preset_model (PyTorch): Preset, before fine-tunining GPT2 model to compare results to. 
        tokenizer (PyTorch): GPT2 tokenizer for generation.
        num_samples (int): Max number of strories to generate each round.
        max_length (int): How long the longest text should be. 
        lsa_embedder (sklearn Vectorizer): For ranking.
        use_user_prompts (None/ str/list): if not None, generation is based on user's given prompts.
        inter_ranking (int/ False): if 0 or False - generates without re-ranking.
        tokens_each_generation (int): Number of tokens to generate each re-ranking cycle. 
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    # Using pre-set starting prompts OR user input.
    if use_user_prompts:
        if isinstance(use_user_prompts, str):
            use_user_prompts = [use_user_prompts]
        assert isinstance(
            use_user_prompts, list), f'User prompt must be a list or string, but got {type(use_user_prompts)}.'

    generated_texts = use_user_prompts if use_user_prompts else constants.STARTING_PROMPTS

    # While most sequences are below target max_length.
    current_text_tokens_len = list(
        map(lambda txt: len(tokenizer.encode(txt)), generated_texts))
    mean_text_len, max_text_len = int(
        np.mean(current_text_tokens_len)), int(max(current_text_tokens_len))
    while mean_text_len < max_length:

        num_return_per_txt = ceil(num_samples/len(generated_texts))
        generated_texts = _sample_sequence(
            model, tokenizer,
            generated_texts, max_length=max_text_len+tokens_each_generation, num_return_sequences=num_return_per_txt, device=device)
        # Choose best inter_ranking
        if inter_ranking > 0:
            # Rank.
            stories_scores = np.array(list(map(lambda text: score_text(
                text, lsa_embedder, tokenizer, preset_model, model), generated_texts)))
            sorted_idx = sort_scores(stories_scores)
            # Apply ranking and Keep best <inter_ranking>.
            generated_texts = list(generated_texts[sorted_idx])[:inter_ranking]
        else:
            generated_texts = list(generated_texts)

        # Update according to new generated texts.
        current_text_tokens_len = list(
            map(lambda txt: len(tokenizer.encode(txt)), generated_texts))
        mean_text_len, max_text_len = int(
            np.mean(current_text_tokens_len)), int(max(current_text_tokens_len))

    # To return num_samples stories when 0 < inter-ranking < num_samples
    generated_texts = list(_sample_sequence(
        model, tokenizer,
        generated_texts, max_length=max_text_len+tokens_each_generation, num_return_sequences=num_return_per_txt, device=device))[:num_samples]

    return generated_texts


def load_style_transfer_model(device, style_model_path):
    style_model = TransformerNet()
    style_model.load_state_dict(torch.load(style_model_path))
    # Set model for inference.
    style_model.eval()
    style_model.to(device)
    # print('Loaded style tranfer model: ', style_model_path)
    return style_model


def get_retreival_info(captions):
    """
    Args:
        captions (str): path to a csv file that has |image_id | ai_description| columns 
    Returns:
        dt (sklearn sparse matrix): LSA tf-idf document-term matrix, trained on captions file of shape (#captions x |vocab|).
        sklearn_tfidf: Vectorizer.
        lsa_vector: Vectorizer.
        caption_image_df (pandas df): loaded captions df.
    """
    caption_image_df = pd.read_csv(captions)
    tf_idf_vector = TfidfVectorizer(
        norm='l2', use_idf=True, smooth_idf=False, sublinear_tf=True, stop_words='english')
    lsa_vector = TruncatedSVD(n_components=500)
    dt = lsa_vector.fit_transform(
        tf_idf_vector.fit_transform(caption_image_df['ai_description']))

    def lsa_embedder(texts): return lsa_vector.transform(
        tf_idf_vector.transform(texts))
    nlp = spacy.load("en_core_web_sm")

    # print('Loaded LSA Tf-IDF and document-term matrix successfully for captions file: ', captions)
    return dt, lsa_embedder, caption_image_df, nlp


def _image_style_transfer(image, style_model, device):
    """
    Convert an original image to a certain style.
    Args:
        image (PIL Image instance): image to covert style to. 
        style_model_path (Pytorch model): trained neural style transfer model.
        device (str): cuda or cpu

    From: https://github.com/pytorch/examples/blob/master/fast_neural_style/neural_style/neural_style.py
    """
    content_transform = transforms.Compose([
        transforms.ToTensor(),
        # Convert from range [0,1] to [0,255]
        transforms.Lambda(lambda x: x.mul(255))
    ])

    content_image = content_transform(image)
    content_image = content_image.unsqueeze(0).to(device)

    with torch.no_grad():
        styled_img = style_model(content_image).cpu()[0]
        # Change the range to 0-255
        styled_img = styled_img.clamp(0, 255).numpy()
        styled_img = styled_img.transpose(1, 2, 0).astype("uint8")
        styled_img = Image.fromarray(styled_img)
    return styled_img


def story_style_transfer(story, style_model, device):
    """
    Transfer images styles for a given story.
    Args:
        story (list of tuples): [(caption, <IMG>), (caption, <IMG>)...]
        style_model_path (Pytorch model): trained neural style transfer model.
        device (str): cuda or cpu
    Returns:
        story with styled images, with the same shape as input story. 
    """
    return list(map(lambda catpion_img: (catpion_img[0], _image_style_transfer(catpion_img[1], style_model, device)), story))


def _get_image(image_id, path):
    """
    Args:
        image_id (str): id of Unsplash image
    Returns file image from given id name using image path from constants file.
    """
    image = Image.open(os.path.join(
        path, image_id+'.jpg'))
    return image.resize((constants.IMAGE_WIDTH, constants.IMAGE_HEIGHT))


def _encode_image(pil_img):
    """
    Encodes image to base64 to display in frontend.
    Taken from: https://jdhao.github.io/2020/03/17/base64_opencv_pil_image_conversion/

    Args:
        pil_img (PIL.Image.Image): same as what _get_image_() returns. 
    Returns a base64 encoded image 
    """
    im_file = BytesIO()
    # Save to file like object
    pil_img.save(im_file, format="JPEG")
    im_bytes = im_file.getvalue()  # im_bytes: image in binary format.
    return base64.b64encode(im_bytes)


def retrieve_images_for_one_story(generated_text, num_images, captions_embeddings, lsa_embedder, df, nlp, images_path):
    """
    Args:
        generated_text (list): one story text to generate images sequence for.
        num_images (int): how many images per text. 
        captions_embeddings (matric): embeddings.
        lsa_embedder (sklearn Vectorizer).
        df (pandas df): caption_image data frame. 
        nlp (spacy model): nlp model to get most frequent nouns from given extract.
    Returns:
        id-image pairs (list<tuple>): the corresponding images for generated_text, before style transfer.
    """
    # Compute LSA tf-idf per extract by extracting extract's top nouns.
    prompts_text = list(
        map(lambda txt: generate_prompt(nlp, txt), generated_text))
    transformed_texts = lsa_embedder(prompts_text)
    # Compute cosine max similarity per text, shape (#captions x #generated texts).
    similarity = cosine_similarity(captions_embeddings, transformed_texts)

    # Compute num_images most similar images per extract, to handle duplicates.
    most_similar_idx = similarity.argsort(axis=0)[-num_images:][::-1]

    # check for duplicates
    unique_idx = []
    # Duplicate out of multiple extracts OR duplicate when retrieving image of one extract.
    if len(most_similar_idx[0]) != len(set(most_similar_idx[0])):
        print('Retrieved a duplicate image, trying another one.')
        seen = set()
        for i, idx in enumerate(most_similar_idx[0]):
            replace_i = 1
            # As long as the image idx already exists in story.
            while idx in seen and replace_i < most_similar_idx.shape[0]:
                # Replace idx of image
                idx = most_similar_idx[replace_i][i]
                # Try next idx.
                replace_i += 1
            else:
                seen.add(idx)
                unique_idx.append(idx)

    # No duplicates, return the most similar per extract
    else:
        unique_idx = most_similar_idx[0]

    # [(image_id, corresponding_caption), (1.jpg, "a child holding a flower")].
    file_caption = df.iloc[unique_idx].to_numpy()

    # get PIL Image from file name. Each tuple in file_caption is (img_id, caption)
    # Convert to  [(id, PIL img)...]
    return list(map(lambda img_caption: (img_caption[0], _get_image(img_caption[0], images_path)), file_caption))


def retrieve_images_for_one_extract(generated_text, num_images, captions_embeddings, lsa_embedder, df, nlp, prev_idx=[]):
    """
    Args:
        generated_text (list/str): one extract text to generate images sequence for.
        num_images (int): how many images per text. 
        captions_embeddings (matric): embeddings.
        lsa_embedder (sklearn Vectorizer).
        df (pandas df): caption_image data frame. 
        nlp (spacy model): nlp model to get most frequent nouns from given extract.
        prev_idx (List[str]): previously retreived images ids, used with API to retreive one non-duplicate image.
    Returns:
        ids (list<str>): the corresponding images ids for generated_text.
    """
    # Compute LSA tf-idf per extract by extracting extract's top nouns.
    generated_text = [generated_text] if isinstance(
        generated_text, str) else generated_text
    prompts_text = list(
        map(lambda txt: generate_prompt(nlp, txt), generated_text))
    transformed_texts = lsa_embedder(prompts_text)
    # Compute cosine max similarity per text, shape (#captions x #extract).
    similarity = cosine_similarity(captions_embeddings, transformed_texts)

    # Compute num_images*buffer_images most similar images per extract, to handle duplicates.
    buffer_images = 5*num_images
    most_similar_idx = similarity.argsort(axis=0)[-buffer_images:][::-1]
    retreived_idx = most_similar_idx[:, 0]
    # Covert retreived images indices to their corresponding image ids.
    retreived_img_idx = list(
        map(lambda img_caption: img_caption[0], df.iloc[retreived_idx].to_numpy()))
    # Check for duplicates.
    prev_idx_set = set(prev_idx)
    duplicate_images = set(retreived_img_idx).intersection(prev_idx_set)

    # No duplicates.
    if not duplicate_images:
        unique_idx = retreived_img_idx[:num_images]
    # Found duplicates, retrieve images from buffer_images in order.
    else:
        print(
            f'Retrieved a duplicate images: {duplicate_images}, trying others.')
        unique_idx = []
        for idx in retreived_img_idx:
            if idx not in prev_idx_set:
                unique_idx.append(idx)
            if len(unique_idx) == num_images:
                break
        else:
            print(
                f'Not enough images to try, increase buffer size of {buffer_images} to retrieve non-duplicate')

    # Convert to [id1, id2]
    return unique_idx


if __name__ == "__main__":
    # Debugging
    captions_tfidf, lsa_embedder, caption_image_df, nlp = get_retreival_info(
        captions=constants.IMAGE_TO_CAPTION_CSV)
    print(retrieve_images_for_one_extract(
        ['Pandas were famous for their bravery and their fierce pride, but their real star was their big horned heads.'], 3, captions_tfidf, lsa_embedder, caption_image_df, nlp))
