# Local imports
import story_generator.constants as constants
from story_generator.generation_utils import load_clip, search_unsplash, _sample_demo_sequence
from story_generator.ranking_utils import score_text, sort_scores

# ML imports
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

# Ranking
import numpy as np
import time

# Style Transfer
import os


class Pipeline():
    """
    Leaner vesion of pipeline for the demo.
    Defines the entire procedure for generating a text-and-images story. Kepps NO state (besides loaded models), to be used as a backend service. 
    Attributes:
        top: Number of top stories to output, after generation and ranking. 
        text_ranking: Number of topgenerated texts to keep during re-ranking.

    To output one default style graphical story with your prompt run:
        $ python pipline.py [free_prompts = 'The Wonders of the Sun\n']
    """

    def __init__(self, top: int = constants.NUM_GENREATED_STORIES, text_ranking: int = 10):
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

        # Preset model for evalutaion
        self._preset_model = GPT2LMHeadModel.from_pretrained(
            constants.PRESET_GPT2_PATH)
        self._preset_model = self._preset_model.to(self._device)

        # Image retreival using CLIP embeddings
        self._clip, self._photo_ids, self._photo_features = load_clip(
            self._device)

        print(
            f"Loading models Time : {round((time.time() - start_time), 2)}s \n")

    def _model_from_str(self, chosen_style):
        """
        Args:
            chosen_style (str): one of none, comics, sketch or anime style.
        Returns a style model instance or None if no exisiting chosen_style.
        """
        INT_TO_MODEL = {"none": None, "comics": self._comics_model,
                        "sketch": self._sketch_model, "anime": self._anime_model}
        return INT_TO_MODEL.get(chosen_style)

    def retrieve_images(self, extract, num_images, current_images_ids):
        """
        Args:
            extract (str): retrieve image for the given extract.
            num_images (int): Number of images to retreive. 
            current_images_ids (List<str>): List of images ids that already exists in story. 

        Returns the list of ids of the retrived, non-duplicate images.
        """
        start_time = time.time()
        best_imgs_ids = search_unsplash(extract, self._photo_features, self._photo_ids,
                                        self._clip, self._device, num_images, current_images_ids)
        print(
            f"CLIP Time: {round((time.time() - start_time), 4)}s \n")
        return best_imgs_ids

    def autocomplete_text(self, extracts, max_length, num_return_sequences, re_ranking=0):
        """
        Args:
            extracts (str): given text to continue. 
            max_length (int): generated text/s max length.
            num_return_sequences (int): number of generated texts to return. 
            re_ranking (int): number of texts to generate to be able to re-rank. 

        Returns num_return_sequences list of generated texts, each of max_length according to given extracts.
        Might return less than num_return_sequences if some are empty/ include only \s. 

        """
        start_time = time.time()
        if re_ranking > num_return_sequences:
            generated = _sample_demo_sequence(
                self._gpt2, self._tokenizer, [extracts], max_length, re_ranking, self._device, first_idx=True)
            # Re-rank generated stories.
            stories_scores = np.array(list(map(lambda text: score_text(
                text, self._tokenizer, self._preset_model, self._gpt2), generated)))
            sorted_idx = sort_scores(stories_scores)
            # Apply ranking and Keep best <num_return_sequences>.
            # print(
            #     f"Total Genration time with Re-Ranking Time : {round((time.time() - start_time), 2)}s \n")
            return list(generated[sorted_idx])[:num_return_sequences]

        generated = list(_sample_demo_sequence(
            self._gpt2, self._tokenizer, [extracts], max_length, num_return_sequences, self._device, first_idx=True))
        # print(
        #     f"Generation Time : {round((time.time() - start_time), 2)}s \n")
        return generated


if __name__ == "__main__":
    # ADD ARGS for user to change PROMPT/top
    start_time = time.time()
    storyGenerator = Pipeline()
    print(
        f"Loading models Time : {round((time.time() - start_time), 2)}s \n", flush=True)
