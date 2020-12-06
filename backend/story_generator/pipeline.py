# Local imports
import constants
from generation_utils import sample_stories_texts, retrieve_images_for_one_story, retrieve_images_for_one_extract, get_retreival_info, load_style_transfer_model, story_style_transfer, _sample_sequence
from ranking_utils import score_text, images_coherency, KLDIV_error_per_text
from helper_functions import split_to_extracts

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
    Defines the entire procedure for generating a text-and-images story.
    Attributes:
        top: Number of top stories to output, after generation and ranking. 
        text_ranking: Number of topgenerated texts to keep during re-ranking.
        free_prompts: User free-form prompt/s to generate by. If none, defaults to constants.STARTING_PROMPTS.
        style_transfer: What style transfer model to apply to images, if any.

    To output one default style graphical story with your prompt run:
        $ python pipline.py [free_prompts = 'The Wonders of the Sun\n']
    """

    def __init__(self, top: int = constants.NUM_GENREATED_STORIES, text_ranking: int = 10, free_prompts=None, style_transfer=constants.STYLE_TRANSFER_MODEL_PATH):
        # Used to return the top number of stories
        self.top = top
        # To control results speed.
        self.text_ranking = text_ranking
        # Allow user's prompts.
        self.free_prompts = free_prompts

        # list of generated texts, each text is a list of text extracts [[start1, middle1, end1],[start2, middle2, end2]...].
        self.texts = []

        # list of list of captions,images pairs. Each images list corresponds to one text. Each image is an array.
        # [(corresponding_id, img/styled_image), ("__1Mu7EZXOM",<PIL.JpegImageFile>)],[...]]
        self.images = []

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

        # Image style transfer.
        self.style_transfer = style_transfer
        if style_transfer is not None:
            self._style_model = load_style_transfer_model(
                self._device, style_model_path=style_transfer)

        # Image re-ranking by Torchvision classification model
        self._resnet152 = models.resnet152(pretrained=True)
        self._resnet152 = self._resnet152.to(self._device)

        # LSA TF-IDF word embeddings for image retrieval.
        self._captions_embedding, self._lsa_embedder, self._caption_image_df, self._nlp = get_retreival_info(
            captions=constants.IMAGE_TO_CAPTION_CSV)

        # Preset model for evalutaion
        self._preset_model = GPT2LMHeadModel.from_pretrained(
            constants.PRESET_GPT2_PATH)
        self._preset_model = self._preset_model.to(self._device)

        self.current_images_ids = []
        self.current_extracts = []

    def update_prompt(self, title):
        """
        Args:
            title (str): title given after init, or new title. 
        """
        self.free_prompts = [title.strip() + '\n']

    def clear_prev_story(self):
        """
        To generate a new story
        """
        self.current_images_ids = []
        self.current_extracts = []

    def generate_text(self, num_samples):
        """
        Genreates and Rankes num_samples stories, where each story is partitioned to extracts, corresponding to the number of images. 
        Shape: (num_samples x NUM_IMAGES_PER_STORY).

        Args:
            num_samples (int): number of stories to generate.
        """
        # Returns ranked stories if self.text_ranking > 0.
        self.texts = sample_stories_texts(
            self._gpt2, self._preset_model, self._tokenizer, num_samples, constants.GENERATION_MAX_LENGTH, self._lsa_embedder, self.free_prompts, self.text_ranking, tokens_each_generation=50)
        # partition text to extracts according to the number of images.
        self.texts = list(map(lambda text: split_to_extracts(
            text, constants.NUM_IMAGES_PER_STORY), self.texts))

    def generate_images(self, texts_to_consider):
        """
        Generates images after the text generation for the top texts_to_consider ranked stories. 
        Shape: (texts_to_consider x NUM_IMAGES_PER_STORY).

        Args:
            texts_to_consider (int): number of text samples to generate images for.
        """
        texts_to_consider = min(texts_to_consider, len(self.texts))

        for idx in range(texts_to_consider):
            id_img_arr = retrieve_images_for_one_story(
                self.texts[idx], constants.NUM_IMAGES_PER_STORY, self._captions_embedding, self._lsa_embedder, self._caption_image_df, self._nlp)
            self.images.append(id_img_arr)
        print(f'Generated images for {len(self.images)} texts', flush=True)

    def retrieve_images(self, extract, num_images):
        """
        Returns the ids of the retrived, non-duplicate images.
        Args:
            extract (str): retrieve image for the given extract.
            num_images (int): Number of images to retreive. 
        """
        return retrieve_images_for_one_extract(
            extract, num_images, self._captions_embedding, self._lsa_embedder, self._caption_image_df, self._nlp, self.current_images_ids)

    def update_current_story_images(self, image_id, delete=False):
        """
        Update current class instance image ids.
        Args:
            image_id (str): id to add/ remove from current list.
            delete (boolean): whether to remove the image_id. 
        """
        if delete:
            self.current_images_ids.remove(image_id)
        else:
            self.current_images_ids.append(image_id)
        print('current_images_ids= ', self.current_images_ids)
        return f'Updated image {image_id}'

    def autocomplete_text(self, extracts, max_length, num_return_sequences):
        """
        Returns num_return_sequences generated texts of max_length according to given extracts.
        Args:
            extracts (str): given text to continue. 
            max_length (int): generated text/s max length.
            num_return_sequences (int): number of generated texts to return. 
        """

        return list(_sample_sequence(
            self._gpt2, self._tokenizer, [extracts], max_length, num_return_sequences, self._device, first_idx=True))

    def update_extracts(self, extract):
        """
        Add extract to current instance extracts. 
        Args:
            extract (str): text to add. 
        """
        self.current_extracts.append(extract)
        print('current_extracts= ', self.current_extracts)
        return f'Added extract {extract}'

    def save_text_and_images_plot(self):
        """ 
        Save self.top ranked graphic stories with their corresponding ranking. 
        Used suring development. 
        """
        assert self.top <= len(
            self.images), f"Top should be <= number of images but got top={self.top} for len(images)={len(self.images)}"
        assert len(self.images) <= len(
            self.texts), f"Number of  texts should be <= number of images, but got len(images)={len(self.images)} and len(texts)={len(self.texts)}"

        for idx in range(self.top):

            # One top ranked story.
            id_img_arr, generated_text = self.images[idx], self.texts[idx]
            # Specifying the overall grid size.
            num_rows, num_cols = 1, len(id_img_arr)
            fig, axes = plt.subplots(num_rows, num_cols, figsize=(
                constants.GENERATED_IMG_WIDTH, constants.GENERATED_IMG_HEIGHT))

            for i, ax in enumerate(axes):
                img_id, image = id_img_arr[i]
                ax.set_title(img_id, loc='center', fontsize=10, wrap=True)
                ax.imshow(image, interpolation='nearest')

                # Add text below wach subplot.
                # ax.annotate(generated_text[i][:100], (0.5, -0.1), xycoords='axes fraction', size=20, ha="center", va='top', wrap=True,
                #             transform=ax.transAxes, bbox={'facecolor': 'linen', 'alpha': 0.5, 'pad': 2})

                ax.set_aspect('equal')
                ax.axis('off')

            # Add ranking results
            scores = score_text(
                generated_text, self._lsa_embedder, self._tokenizer, self._preset_model, self._gpt2)
            scores_str = "\n\nScores: " + \
                " | ".join(f'{key}: {score:.2f}' for key,
                           score in zip(constants.FEATURES, scores))

            # Add the story to the image
            plt.figtext(0.5, 0.2, '\n\n'.join(generated_text) + scores_str,  bbox={
                'facecolor': 'linen', 'alpha': 0.5, 'pad': 2}, wrap=True, fontsize=16, fontweight='heavy', ha='center', va='center')

            # position the bottom edge of subplots
            plt.subplots_adjust(wspace=0.2, hspace=0.01)
            fig.savefig(
                f'story_image_grid_rank_{idx+1}.png')

    def send_first_story(self):
        """
        Prepare story for sending according to maiApi expectations.
        Returns texts: List<str> and images: List<base64 encoded PIL.Image.Image>
        """
        #  Remove title from text
        idx_title = self.texts[0][0].index('\n')
        self.texts[0][0] = self.texts[0][0] if idx_title == - \
            1 else self.texts[0][0][idx_title + 1:]
        # Remove multpile spaces/ tabs/ new lines from texts
        self.current_extracts.extend(list(
            map(lambda extract: ' '.join(extract.split()), self.texts[0])))
        # Get ids of  all images
        self.current_images_ids.extend(list(
            map(lambda id_img: id_img[0], self.images[0])))
        self.texts, self.images = [], []

        return self.current_extracts, self.current_images_ids

    def generate_graphic_story(self, save_story=False, send_story=True):
        """ 
        Generates and optionally saves grahic story images in current directory. 
        Number of generated stories equals self.top.
        Args:
            save_story (boolean): Whether to save the graphic story as a plt image in curreent directory.
            send_story (boolean): Whether to return the first story text and base64 encoded images.
        """

        print("Starting text generation for prompts: ", self.free_prompts)
        start_time = time.time()

        self.generate_text(num_samples=constants.MAX_NUM_TEXTS_SAMPLES)
        print(
            f'Generated {len(self.texts)} texts in {int(time.time()- start_time)}s.', flush=True)
        img_time = time.time()
        self.generate_images(
            texts_to_consider=constants.NUM_TEXTS_TO_SAMPLE_IMAGES_FOR)
        print(
            f'Generated images in {int(time.time()- img_time)}s.', flush=True)
        # Optimize all images by coherency, lower is better since it's a smaller difference.
        self.texts, self.images = zip(
            *sorted(zip(self.texts, self.images), key=lambda tup: images_coherency(self._resnet152, tup[1]), reverse=False))

        # Style transfer to images after re-ranking.
        if self.style_transfer:
            self.images = list(map(lambda story: story_style_transfer(
                story, self._style_model, self._device), self.images))

        # Save top options
        if save_story:
            self.save_text_and_images_plot()

        if send_story:
            return self.send_first_story()


if __name__ == "__main__":
    # ADD ARGS for user to change PROMPT/top
    start_time = time.time()
    storyGenerator = Pipeline(
        free_prompts='The Truth is Written in the Stars\n')
    print(
        f"Loading models Time : {round((time.time() - start_time), 2)}s \n", flush=True)
    storyGenerator.generate_graphic_story(save_story=False)
    end_time = time.time()
    print(
        f"Calculation Time: {round(((end_time - start_time) / 60), 2)}m", flush=True)
