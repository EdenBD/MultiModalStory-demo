import story_generator.constants as constants

# Text Generation
from story_generator.ranking_utils import score_text, sort_scores
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
from story_generator.helper_functions import generate_prompt


def _sample_demo_sequence(model, tokenizer, prompts, max_length, num_return_sequences, device, first_idx=False):
    """
    One forward pass generation that ends at end of sentence mark. 

    Args:
        model (PyTorch): Fine-tuned GPT2 model for generation.
        tokenizer (PyTorch): GPT2 tokenizer for generation.
        prompts (list): For demo purposes, list of one string representing the current story.
        max_length (int): How long the generated text should be. 
        num_return_sequences (int): Number of generated texts to return per prompt. 
        first_idx (bool): True if want to remove given prompt from the returned generation.

    Returns:
        List of num_return_sequences generated texts, each with approximate length max_length.

    Uses hugginface generate (https://huggingface.co/transformers/main_classes/model.html?highlight=generate#transformers.TFPreTrainedModel.generate)
    With tokenizer.padding size = left, otherwise generation is random (issue https://github.com/huggingface/transformers/issues/3021)
    """

    encodings_dict = tokenizer(
        prompts, truncation=True, max_length=constants.MAX_SEQ_LEN)
    prompts_ids = torch.tensor(
        encodings_dict['input_ids'], device=device, dtype=torch.long)
    first_idx = len(prompts_ids[0]) if first_idx else 0

    sample_outputs = model.generate(
        prompts_ids,  # Long tensor of size (batch_size, max_prompt_length)
        do_sample=True,  # activate top-k, top-p sampling
        max_length=max_length+first_idx,
        min_length=first_idx + max_length//2 if first_idx else 10,
        top_k=constants.TOP_K,
        top_p=constants.TOP_P,
        temperature=constants.TEMPERATURE,
        repetition_penalty=1.0,  # no penalty
        num_return_sequences=num_return_sequences,
        pad_token_id=tokenizer.pad_token_id,
    )  # returns tensor of shape (len(prompts)*num_return_sequences x max_length)
    generated = np.array(list(map(lambda sample: tokenizer.decode(
        sample[first_idx:], skip_special_tokens=True).strip(), sample_outputs)))
    return generated


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
        # print(
        #     f'Retrieved a duplicate images: {duplicate_images}, trying others.')
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
