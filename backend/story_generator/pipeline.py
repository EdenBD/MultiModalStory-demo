# Local imports
import story_generator.constants as constants
from story_generator.generation_utils import sample_stories_texts, retrieve_images_for_one_story, retrieve_images_for_one_extract, get_retreival_info, load_style_transfer_model, story_style_transfer, _sample_sequence
from story_generator.ranking_utils import score_text, images_coherency, KLDIV_error_per_text, sort_scores
from story_generator.helper_functions import split_to_extracts

# ML imports
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

# Save plot
from math import ceil
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Ranking
import numpy as np
import time

# Image ranking by ResNet logits.
from torchvision import models
import os


class Pipeline():
    """
    Defines the entire procedure for generating a text-and-images story. Kepps NO state (besides loaded models), to be used as a backend service. 
    Attributes:
        top: Number of top stories to output, after generation and ranking. 
        text_ranking: Number of topgenerated texts to keep during re-ranking.
        load_all_model: Load all models, needed for story generation, but not minimal image/ text retreival. 

    To output one default style graphical story with your prompt run:
        $ python pipline.py [free_prompts = 'The Wonders of the Sun\n']
    """

    def __init__(self, top: int = constants.NUM_GENREATED_STORIES, text_ranking: int = 10, load_all_model=False):
        start_time = time.time()
        # Used to return the top number of stories
        self.top = top
        # To control results speed.
        self.text_ranking = text_ranking

        # Private attributes to load once.
        self._device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        # Print device info
        print('Using device:', self._device)
        self._tokenizer = GPT2Tokenizer.from_pretrained(
            constants.TOKENIZER_PATH)
        self._tokenizer.pad_token = self._tokenizer.eos_token
        self._tokenizer.padding_side = "left"
        # print('Loaded GPT2 Tokenizer')

        self._gpt2 = GPT2LMHeadModel.from_pretrained(
            constants.FINETUNED_GPT2_PATH)
        self._gpt2 = self._gpt2.to(self._device)
        # print(f'Loaded GPT2 fine-tuned Model: {constants.FINETUNED_GPT2_PATH}')

        # LSA TF-IDF word embeddings for image retrieval.
        self._captions_embedding, self._lsa_embedder, self._caption_image_df, self._nlp = get_retreival_info(
            captions=constants.IMAGE_TO_CAPTION_CSV)

        # Preset model for evalutaion
        self._preset_model = GPT2LMHeadModel.from_pretrained(
            constants.PRESET_GPT2_PATH)
        self._preset_model = self._preset_model.to(self._device)

        if load_all_model:
            # Image style transfer.
            self._original_images_path = constants.ORIGINAL_IMAGES_PATH
            self._styled_images_path = constants.STYLED_IMAGES_PATH

            # Image re-ranking by Torchvision classification model
            self._resnet152 = models.resnet152(pretrained=True)
            self._resnet152 = self._resnet152.to(self._device)

        print(
            f"Loading models Time : {round((time.time() - start_time), 2)}s \n")

    def generate_text(self, title, num_samples):
        """
        Genreates and Rankes num_samples stories, where each story is partitioned to extracts, corresponding to the number of images. 
        Shape: (num_samples x NUM_IMAGES_PER_STORY).

        Args:
            title (List<str>): e.g ['This is a title\n']
            num_samples (int): number of stories to generate.

        Returns: list of generated texts. 
        """
        # Returns ranked stories if self.text_ranking > 0.
        texts = sample_stories_texts(
            self._gpt2, self._preset_model, self._tokenizer, num_samples, constants.GENERATION_MAX_LENGTH, self._lsa_embedder, title, self.text_ranking, tokens_each_generation=50)
        # partition text to extracts according to the number of images.
        return list(map(lambda text: split_to_extracts(
            text, constants.NUM_IMAGES_PER_STORY), texts))

    def generate_images(self, num_texts_to_consider, texts):
        """
        Generates images after the text generation for the top num_texts_to_consider ranked stories. 
        Shape: (num_texts_to_consider x NUM_IMAGES_PER_STORY).

        Args:
            num_texts_to_consider (int): number of text samples to generate images for.
            texts: (List<str>): generated texts. 
        Returns:
            List of list of generated images e.g [[(id, PIL img), ()] ...] 
        """
        num_texts_to_consider = min(num_texts_to_consider, len(texts))
        images = []
        for idx in range(num_texts_to_consider):
            id_img_arr = retrieve_images_for_one_story(
                texts[idx], constants.NUM_IMAGES_PER_STORY, self._captions_embedding, self._lsa_embedder, self._caption_image_df, self._nlp, self._original_images_path)
            images.append(id_img_arr)
        print(f'Generated images for {len(images)} texts', flush=True)
        return images

    def retrieve_images(self, extract, num_images, current_images_ids):
        """
        Args:
            extract (str): retrieve image for the given extract.
            num_images (int): Number of images to retreive. 
            current_images_ids (List<str>): List of images ids that already exists in story. 

        Returns the list of ids of the retrived, non-duplicate images.
        """
        return retrieve_images_for_one_extract(
            extract, num_images, self._captions_embedding, self._lsa_embedder, self._caption_image_df, self._nlp, current_images_ids)

    def autocomplete_text(self, extracts, max_length, num_return_sequences, re_ranking=0):
        """
        Args:
            extracts (str): given text to continue. 
            max_length (int): generated text/s max length.
            num_return_sequences (int): number of generated texts to return. 
            re_ranking (int): number of texts to generate to be able to re-rank. 

        Returns num_return_sequences list of generated texts, each of max_length according to given extracts.

        """
        start_time = time.time()
        if re_ranking > num_return_sequences:
            generated = _sample_sequence(
                self._gpt2, self._tokenizer, [extracts], max_length, re_ranking, self._device, first_idx=True)
            print(
                f"Generation Time : {round((time.time() - start_time), 2)}s \n")
            # Re-rank generated stories.
            stories_scores = np.array(list(map(lambda text: score_text(
                text, self._lsa_embedder, self._tokenizer, self._preset_model, self._gpt2), generated)))
            sorted_idx = sort_scores(stories_scores)
            print("autocomplete_text: sorted_idx", sorted_idx)
            # Apply ranking and Keep best <num_return_sequences>.
            print(
                f"Ranking Time : {round((time.time() - start_time), 2)}s \n")
            return list(generated[sorted_idx])[:num_return_sequences]

        generated = list(_sample_sequence(
            self._gpt2, self._tokenizer, [extracts], max_length, num_return_sequences, self._device, first_idx=True))
        print(
            f"Generation Time : {round((time.time() - start_time), 2)}s \n")
        return generated

    def send_first_story(self, texts, images):
        """
        Prepare story for sending according to maiApi expectations.
        Args:
            texts: List<str> e.g [story1_extract1, story1_extract2...]
            images: List[tuples<str>]
        Returns extracts of top story: List<str> and corresponding images: List<str>
        """
        #  Remove title from text
        idx_title = texts[0].index('\n')
        texts[0] = texts[0] if idx_title == - \
            1 else texts[0][idx_title + 1:]
        # Remove multpile spaces/ tabs/ new lines from texts | list of imgs ids.
        return list(
            map(lambda extract: ' '.join(extract.split()), texts)), list(
            map(lambda id_img: id_img[0], images))

    def generate_graphic_story(self, title):
        """ 
        Generates and optionally saves grahic story images in current directory. 
        Number of generated stories equals self.top.
        Args:
            title (str): Given title to genetate story by. 
        """

        title = [title.strip() + '\n']
        print("Starting text generation for prompt: ", title[0])
        start_time = time.time()

        texts = self.generate_text(
            title, num_samples=constants.MAX_NUM_TEXTS_SAMPLES)
        print(
            f'Generated {len(texts)} texts in {int(time.time()- start_time)}s.', flush=True)
        img_time = time.time()
        images = self.generate_images(
            constants.NUM_TEXTS_TO_SAMPLE_IMAGES_FOR, texts)
        print(
            f'Generated images in {int(time.time()- img_time)}s.', flush=True)
        # Optimize all images by coherency, lower is better since it's a smaller difference.
        texts, images = zip(
            *sorted(zip(texts, images), key=lambda tup: images_coherency(self._resnet152, tup[1]), reverse=False))

        return self.send_first_story(texts[0], images[0])


if __name__ == "__main__":
    # ADD ARGS for user to change PROMPT/top
    start_time = time.time()
    storyGenerator = Pipeline()
    print(
        f"Loading models Time : {round((time.time() - start_time), 2)}s \n", flush=True)
    top_story_extracts, top_story_imgs = storyGenerator.generate_graphic_story(
        title='The Truth is Written in the Stars')
    end_time = time.time()
    print('top_story_extracts', top_story_extracts)
    print('top_story_imgs', top_story_imgs)
    print(
        f"Calculation Time: {round(((end_time - start_time) / 60), 2)}m", flush=True)
