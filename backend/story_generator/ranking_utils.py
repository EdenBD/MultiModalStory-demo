# Sentiment score
import story_generator.constants as constants
# Get stem of words
from nltk.stem import WordNetLemmatizer
# Find synonyms, nltk.download('wordnet')
from nltk.corpus import wordnet as wn
# Get sentiment from SentiWordNet lexicon, nltk.download('sentiwordnet'
from nltk.corpus import sentiwordnet as swn
from nltk import pos_tag

# Readibility
from story_generator.helper_functions import split_to_sentences, split_words
import re

# Diversity
from stop_words import get_stop_words

# Extracts coherency
from sklearn.metrics.pairwise import cosine_similarity

# Image difference
import numpy as np
from torchvision import transforms
import torch

# KLDIV text evaluation & image difference.
from torch.nn import KLDivLoss, Softmax, LogSoftmax


def _readabilty(text, texts_sentences):
    """
    Uses length of sentences and length of words.
    Higher is for more advanced readers.
    If text is sparse i.e. mostly new lines, and doesn't end with an eos -> add a negative cost.  
    Args:
        text (str): original text to return score for.
        texts_sentences (list): text split to sentences. 
    """
    txt_words = split_words(text)
    num_letters = sum(len(word) for word in txt_words)
    num_words = len(txt_words)
    num_sent = len(texts_sentences)

    # check if a "sparse" sentence
    if num_sent == 1:
        new_line_threshold = 0 if num_words == 0 else num_words // 4
        if texts_sentences[0].count('\n') > new_line_threshold or not re.search(r'(?<![A-Z])[.!?;"]+', texts_sentences[0]):
            num_sent = 0

    letters_per_word = -10 if num_words == 0 else num_letters/num_words
    words_per_sentence = -10 if num_sent == 0 else num_words/num_sent
    # 0.5 to weight words_per_sentence higher
    return 0.5*letters_per_word + words_per_sentence


def _diversity(filtered_words, filtered_words_set):
    """
    Fraction of unique words from the total number of words (exclusing stop words).
    Higher is more diversified.
    Args:
        filtered_words (list): set of non-stop tokenized words. 
        filtered_words_set (set): unique filtered words.
    """
    # If empty sentence or only white space or \n or too repetitive.
    if len(filtered_words_set) < constants.MIN_WORDS_PER_STORY:
        return 0

    return len(filtered_words_set) / len(filtered_words)


def _simplicity(filtered_words_set):
    """
    Fraction of most frequent words from generated text.
    Args:
        filtered_words_set (set): set of non-stop, non-punctuation words. 
    """
    return len(filtered_words_set.intersection(constants.SEVEN_PREC_MOST_FREQ_WORDS))


def _coherency(texts_sentences, embedder):
    """
    Args:
        texts_sentences (list): one story text split to sentences.
        lsa (sklearn Vectorizer).
    Based on LSA (TF-IDF -> Truncated SVD), returns the similarity within the story setences in comparison to the first sentence.
    """
    # Compute tf-idf per extract.
    transformed_sentences = embedder(texts_sentences)
    # Compute cosine max similarity per extract, shape (#texts_sentences x #texts_sentences).
    similarity = cosine_similarity(transformed_sentences)
    # Compute similarity scores with first sentence of the rest of the sentences.
    return sum(similarity[0][1:])


def _sentiment_polarity(filtered_words):
    """
    Returns a positive sentiment polarity in range 0 = negative/objective to 100 = positive of the entire text.
    Uses SentiWordnet to compute the positiveness polarity of the words and average that value.
    Based on https://nlpforhackers.io/sentiment-analysis-intro/

    Args:
        filtered_words (set): set of non-stop, non-punctuation words. 
    """
    # If  empty
    if len(filtered_words) < 2:
        return 0

    POS_TAG_TO_WN = {'J': wn.ADJ, 'N': wn.NOUN, 'R': wn.ADV, 'V': wn.VERB}
    lemmatizer = WordNetLemmatizer()

    text_sentiment = []
    tagged_words = pos_tag(filtered_words)

    for word, tag in tagged_words:
        wn_tag = POS_TAG_TO_WN.get(tag[0], None)
        if not wn_tag:
            continue

        lemma = lemmatizer.lemmatize(word, pos=wn_tag)
        if not lemma:
            continue

        synsets = wn.synsets(lemma, pos=wn_tag)
        if not synsets:
            continue

        # Take the most common of the synthsets
        synset = synsets[0]
        pos_sentiment = swn.senti_synset(synset.name()).pos_score(
        ) - swn.senti_synset(synset.name()).neg_score()
        text_sentiment.append(pos_sentiment)
    return 0 if not text_sentiment else max(int(np.mean(text_sentiment)*100), 0)


def _load_KLDIV_loss_function(device):
    """
    Load loss function and its utilities.
    """
    loss_fct = torch.nn.KLDivLoss(reduction='batchmean')
    softmax = Softmax(dim=-1)
    logSoftmax = LogSoftmax(dim=-1)
    loss_fct.to(device)
    softmax.to(device)
    logSoftmax.to(device)
    return loss_fct, softmax, logSoftmax


def KLDIV_error_per_text(tokenizer, preset_model, finetuned_model, text):
    """
    Computes the difference in prediction scores of the given text between the two models.
    The preset_model scores are the input distribution and the finetuned_model scores are the target distribution.
    The forward pass of each model returns the "prediction scores of the language modeling head (scores for each vocabulary token before SoftMax)" (from: https://huggingface.co/transformers/model_doc/gpt2.html).

    Args:
        tokenizer (Pytroch tokenizer): GPT2 Byte Tokenizer. 
        preset_model (Pytorch model): preset GPT2 model of the same/ different size of the finetuned model. Assumes model max_length < num_of_words(text).
        finetuned_model (Pytorch model): fine-tuned GPT2 model. Assumes model max_length < num_of_words(text).
        text (str): generated text to check predictions scores for.
    Returns:
        float representing the difference in scores. Bigger is probably better since it usually means the text is closer to the finetuned distribution.
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Text is divided to extracts e.g. start, middle, end.
    if isinstance(text, (list, np.ndarray)):
        text = ' '.join(text)

    # if too short return 0
    if len(text) < 10:
        return 0

    # Prepare text to forward pass.
    encodings_dict = tokenizer(text)
    text_ids = torch.tensor(
        encodings_dict['input_ids'], device=device, dtype=torch.long)

    # Load loss function, the losses are averaged over batch dimension.
    loss_fct, softmax, logSoftmax = _load_KLDIV_loss_function(device)
    # unsqueeze to add batch_size =1
    # zero index to logits, logits shape (batch_size, len(text_ids), config.vocab_size)
    logists_preset = preset_model(text_ids.to(device).unsqueeze(0))[0]
    logits_finetuned = finetuned_model(text_ids.to(device).unsqueeze(0))[0]

    # input should be in log-probabilities, and target in probabilities.
    return loss_fct(logSoftmax(logists_preset), softmax(logits_finetuned)).item()


def score_text(text, tokenizer, preset_model, finetuned_model):
    """ Uses rule-based rankings. Higher is better, but different features have different scales.

    Args:
        text (str/ List[str]): one story to rank.
        tokenizer (Pytroch tokenizer): GPT2 Byte Tokenizer. 
        preset_model (Pytorch model): preset GPT2 model of the same/ different size of the finetuned model. 
        finetuned_model (Pytorch model): fine-tuned GPT2 model. 

    Returns a scores np.array of corresponding to text.
    """
    assert isinstance(
        text, (str, list)), f"score_text accepts type(text) = str/list, but got {type(text)}"

    if isinstance(text, list):
        text = ' '.join(text)

    # Keep same order as in constants.FEATURES
    scores = [0 for _ in range(len(constants.FEATURES))]
    texts_sentences = split_to_sentences(text)
    # scores[0] = _coherency(texts_sentences, lsa_embedder)
    scores[1] = _readabilty(text, texts_sentences)

    # Set of text words without punctuation and stop words.
    filtered_words = list(filter(
        lambda word: word not in constants.STOP_WORDS, split_words(text.lower().strip())))
    filtered_words_set = set(filtered_words)
    # Sentiment.
    scores[2] = _sentiment_polarity(filtered_words)

    # Set based measures.
    scores[3], scores[4] = _simplicity(filtered_words_set), _diversity(
        filtered_words, filtered_words_set)

    # The bigger differene, the more tale-like, similar to the fine-tuned model, the text is.
    scores[5] = KLDIV_error_per_text(
        tokenizer, preset_model, finetuned_model, text)

    # print(" | ".join(f'{key}: {score:.2f}' for key,
    #                  score in zip(constants.FEATURES, scores)))

    return np.array(scores)


def sort_scores(stories_scores):
    """
    Args:
        stories_scores (np.array): 2D matrix of shpae (#stories x #ranking_features).
    Returns the indices of top stories accroding to scores, from highest to lowest (descending).
    """
    # Rescale each feature column across all stories, so that all featues contribute equally.
    # stories_scores_std = (stories_scores - np.mean(stories_scores,axis=0))/np.std(stories_scores,axis=0)
    stories_scores_normalized = stories_scores - \
        np.min(stories_scores, axis=0)
    min_max_denominator = np.max(
        stories_scores, axis=0) - np.min(stories_scores, axis=0)
    # Avoid devision by zero, out to initialize idices where denominator ==0.
    stories_scores_normalized = np.divide(
        stories_scores_normalized, min_max_denominator, out=np.zeros_like(stories_scores_normalized), where=min_max_denominator != 0)

    # Sort by mean story score, shape: (num_stories)
    return np.argsort(np.mean(stories_scores_normalized, axis=1))[::-1]


if __name__ == "__main__":
    text = "The Special Frog\n\nKite in the River Water\n\nHorn\n\nThe Old Toad\n\nToad at End of a Night\n\nTHE STORY OF THE TIGER AND THE CRUISER"
    texts_sentences = split_to_sentences(text)
    print(_readabilty(text, texts_sentences))
