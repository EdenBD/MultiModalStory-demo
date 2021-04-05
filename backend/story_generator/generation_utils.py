import story_generator.constants as constants

# Text Generation
from story_generator.ranking_utils import score_text, sort_scores
import torch
from math import ceil

# Text pre-processing
import re
# Image retrieval
import os
import pandas as pd
import numpy as np
from PIL import Image
# To download image from URL
from urllib import request
from io import BytesIO

# CLIP Image retrieval
import clip

# Image style transfer
from torchvision import transforms
from story_generator.transformer_net import TransformerNet
import multiprocessing


def _preprocess_generated_text(sample, tokenizer, has_space):
    decoded = tokenizer.decode(
        sample, skip_special_tokens=True)
    # Removing spaces.
    decoded = decoded.strip()
    # Adding a space at the beginning if needed.
    if not has_space:
        decoded = ' ' + decoded
    # Filtering � globally
    return re.sub(u'\uFFFD', '', decoded)


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
    has_space = prompts[0][-1].isspace()
    generated = map(lambda sample: _preprocess_generated_text(
        sample[first_idx:], tokenizer, has_space), sample_outputs)
    generated = np.array(
        list(filter(lambda sample: len(sample.strip()) > 2, generated)))
    return generated


def encode_search_query(clip_model, device, search_query):
    """
    Takes a text description and encodes it into a feature vector using the CLIP model.
    Code taken from https://github.com/haltakov/natural-language-image-search.
    """
    with torch.no_grad():
        # Encode and normalize the search query using CLIP
        text_encoded = clip_model.encode_text(
            clip.tokenize(search_query).to(device))
        text_encoded /= text_encoded.norm(dim=-1, keepdim=True)

    # Retrieve the feature vector converted to Half
    return text_encoded.half()


def find_best_matches(text_features, photo_features, photo_ids, num_images, prev_idx):
    """
    Compares the text feature vector to the feature vectors of all images and finds the best matches. 
    Returns the IDs of the best matching photos.
    Code taken from https://github.com/haltakov/natural-language-image-search.
    """
    # Compute the similarity between the search query and each photo using the Cosine similarity
    similarities = (photo_features @ text_features.T).squeeze(1)

    # Sort the photos by their similarity score
    best_photo_idx = (-similarities).argsort()

    # Get extra images ids to handle duplicates.
    BUFFER_SIZE = 30

    retreived_img_idx = [photo_ids[i] for i in best_photo_idx[:BUFFER_SIZE]]

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
                f'Not enough images to try, increase buffer size = {BUFFER_SIZE} to retrieve non-duplicate')

    # Return the photo IDs of the best matches, without duplicates.
    return unique_idx


def load_clip(device):
    """
    Code taken from https://github.com/haltakov/natural-language-image-search.
    """
    clip_model, _ = clip.load("ViT-B/32", device=device)
    # Load the photo IDs
    photo_ids = pd.read_csv("backend/unsplash-dataset/photo_ids.csv")
    photo_ids = list(photo_ids['photo_id'])

    # Load the features vectors
    photo_features = np.load("backend/unsplash-dataset/features.npy")

    # Convert features to Tensors: Float32 on CPU and Float16 on GPU
    if device == "cpu":
        photo_features = torch.from_numpy(photo_features).float().to(device)
    else:
        photo_features = torch.from_numpy(photo_features).to(device)

    return clip_model, photo_ids, photo_features


def search_unsplash(search_query, photo_features, photo_ids, clip_model, device, num_images=3, prv_ids=[]):
    """
    Get num_images images from Unsplash
    """
    # Encode the search query
    # Slice from the end, according to CLIP max number of tokens.
    MAX_LENGTH = 300
    text_features = encode_search_query(
        clip_model, device, search_query[-MAX_LENGTH:])

    # Find the best matches
    return find_best_matches(text_features, photo_features, photo_ids, num_images, prv_ids)


def load_style_transfer_model(device, style_model_path):
    style_model = TransformerNet()
    style_model.load_state_dict(torch.load(style_model_path))
    # Set model for inference.
    style_model.eval()
    style_model.to(device)
    return style_model


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


def _get_image(image_id):
    """
    Args:
        image_id (str): id of Unsplash image
    Returns PIL image from file name, file name consists of directory from constants + id.
    """
    image = Image.open(os.path.join(
        constants.NONE_IMAGES_PATH, image_id+'.jpg'))
    return image.resize((constants.IMAGE_WIDTH, constants.IMAGE_HEIGHT))


def download_image(image_id, img_target_size=constants.IMAGE_HEIGHT, img_quality=constants.IMAGE_QUALITY):
    """
    Args:
        image_id (str): Unsplash image id.
        img_target_size (int): downloaded image resolution/ dimensions. 
        img_quality (int): JPEG quality in range 1 (worst) to 95 (best). 
    Download an image from Unsplash according to image_url to a image_id.jpg file.
    Compresses the HD image to jpeg with resolution/size img_target_size and JPG quality img_quality.
    From https://www.kaggle.com/lyakaap/fast-resized-image-download-python-3
    """
    image_url = f'{constants.UNSPLASH_URL}{image_id}'
    filename = os.path.join(constants.NONE_IMAGES_PATH, f'{image_id}.jpg')

    if os.path.exists(filename):
        # print(f'Image {image_id} already exists. Skipping download.')
        return 0
    try:
        # referer to circumvant hot-linking
        req = request.Request(image_url, headers={
                              'Referer': 'https://images.unsplash.com'})
        response = request.urlopen(req)
        image_data = response.read()
    except:
        print('Warning: Could not download image {} from {}'.format(
            image_id, image_url))
        return 1
    try:
        pil_image = Image.open(BytesIO(image_data))
    except:
        print('Warning: Failed to parse image {}'.format(image_id))
        return 1
    try:
        pil_image = pil_image.convert('RGB')
    except:
        print('Warning: Failed to convert image {} to RGB'.format(image_id))
        return 1
    try:
        pil_image = pil_image.resize((img_target_size, img_target_size))
    except:
        print('Warning: Failed to resize image {}'.format(image_id))
        return 1
    try:
        pil_image.save(filename, format='JPEG', quality=img_quality)
    except:
        print('Warning: Failed to save image {}'.format(filename))
        return 1

    return 0


def _download_image_style_transfer(image_id, style_model, style, device, img_quality=constants.IMAGE_QUALITY):
    """
    Download style transferre image from exisiting file.
    Args:
        image_id (str): Unsplash image id.
        style_model (model): preset model instance from downloaded models directory.
        style (str): chosen style, corresponds to folder name. 
        img_quality (int): JPEG quality in range 1 (worst) to 95 (best).         
    """
    org_file = os.path.join(constants.NONE_IMAGES_PATH, f'{image_id}.jpg')
    if os.path.exists(org_file):
        pil_image = _get_image(image_id)
        styled_img = _image_style_transfer(pil_image, style_model, device)
        try:
            filename = os.path.join(
                constants.UNSPLASH_IMG_FOLDER, style, f'{image_id}.jpg')
            styled_img.save(filename,
                            format='JPEG', quality=img_quality)
        except:
            print('Warning: Failed to save image {}'.format(image_id))
            return 1
        return 0
    return 1


def _style_loader(imgs_ids, num_workers=3):
    """
    Downloading with multi-processing
    Args:
        imgs_ids (list[str]): Unsplash images ids.
        num_workers (int): Numnber of proccesses.
    """
    pool = multiprocessing.Pool(processes=num_workers)
    failures = sum(pool.imap_unordered(
        download_image, imgs_ids))
    print('Total number of download failures:', failures)
    pool.close()
    pool.terminate()


if __name__ == "__main__":
    # Debugging
    img_ids = ["HxhSVDapt-I", "h2LMXbpvwCw",
               "I9EhRx3oQ7Q", "QAgOqt7M8_E", "7YdPCUbbb9M"]
    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu")
    style = "anime"
    style_model = load_style_transfer_model(
        device, style_model_path=constants.ANIME_STYLE_MODEL)
    [_download_image_style_transfer(
        image_id, style_model, style) for image_id in img_ids]
