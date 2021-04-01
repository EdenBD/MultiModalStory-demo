# Local imports
import story_generator.constants as constants
from story_generator.generation_utils import load_clip, search_unsplash, _sample_demo_sequence, load_style_transfer_model, _get_image, _image_style_transfer
from story_generator.ranking_utils import score_text, sort_scores

# ML imports
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

# Ranking
import numpy as np
import time


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

        # Image retreival using CLIP embeddings
        self._clip, self._photo_ids, self._photo_features = load_clip(
            self._device)

        # Loading Image style transfer models
        self._sketch_model = load_style_transfer_model(
            self._device, style_model_path=constants.SKETCH_STYLE_MODEL)
        self._anime_model = load_style_transfer_model(
            self._device, style_model_path=constants.ANIME_STYLE_MODEL)
        self._comics_model = load_style_transfer_model(
            self._device, style_model_path=constants.COMICS_STYLE_MODEL)

        # Preset model for evalutaion
        self._preset_model = GPT2LMHeadModel.from_pretrained(
            constants.PRESET_GPT2_PATH)
        self._preset_model = self._preset_model.to(self._device)

        print(
            f"Loading models Time : {round((time.time() - start_time), 2)}s \n")

    def retrieve_images(self, extract, num_images, current_images_ids, chosen_style=0):
        """
        Args:
            extract (str): retrieve image for the given extract.
            num_images (int): Number of images to retreive. 
            current_images_ids (List<str>): List of images ids that already exists in story. 
            chosen_style (int): represents the style chosen by user. 

        Returns the list of ids of the retrived, non-duplicate images.
        """
        start_time = time.time()
        best_imgs_ids = search_unsplash(extract, self._photo_features, self._photo_ids,
                                        self._clip, self._device, num_images, current_images_ids)
        # Download original images if not in folder.

        # Style images from downloaded images.
        chosen_style_model = _model_from_style(chosen_style)
        if chosen_style_model is not None:
            # Return a tuple per image (img_id, PIL_IMAGE)
            ids_pil_images = list(
                map(lambda img_id: (img_id, _get_image(img_id), best_imgs_ids)))
            styled_ids_imgs = list(map(lambda id_pil_img: (id_pil_img[0], _image_style_transfer(
                id_pil_img[1], chosen_style_model, self._device)), ids_pil_images))
            # Save styled images
            print("Styled Image path: ", os.path.join(
                constants.UNSPLASH_IMG_FOLDER, _style_from_int(chosen_style), styled_id_img[0], '.jpg'))

            list(map(lambda styled_id_img: styled_id_img[1].save(os.path.join(
                constants.UNSPLASH_IMG_FOLDER, _style_from_int(chosen_style), styled_id_img[0], '.jpg')), styled_ids_imgs))
        print(
            f"Images IDs + Download + Style Time : {round((time.time() - start_time), 4)}s \n")
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
                text, self._lsa_embedder, self._tokenizer, self._preset_model, self._gpt2), generated)))
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

    def _model_from_style(chosen_style):
        """
        Must correspond to _style_from_int.
        Args:
            chosen_style (int): represents none, comics, sketch or anime style.
        Returns a style model instance
        """
        INT_TO_MODEL = {0: None, 1: self._comics_model,
                        2: self._sketch_model, 3: self._anime_model}
        return INT_TO_MODEL[chosen_style]

    def _style_from_int(chosen_style):
        """
        Must correspond to _model_from_style.
        Args:
            chosen_style (int): represents none, comics, sketch or anime style.
        Returns (str): the style name. 
        """
        INT_TO_STYLE = {0: None, 1: "comics",
                        2: "sketch", 3: "anime"}
        return INT_TO_STYLE[chosen_style]


if __name__ == "__main__":
    # ADD ARGS for user to change PROMPT/top
    start_time = time.time()
    storyGenerator = Pipeline()
    print(
        f"Loading models Time : {round((time.time() - start_time), 2)}s \n", flush=True)
