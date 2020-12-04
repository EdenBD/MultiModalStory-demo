# Clean/ Split text.
import re
import numpy as np

# Generate prompts.
import spacy
from collections import Counter


def clean_text(string, pattern, replacement):
    """
    Args: pattern to match globally i.e '<newline>'
    """
    pattern_object = re.compile(pattern, flags=re.IGNORECASE)
    return pattern_object.sub(replacement, string)


def split_to_extracts(text, num_extracts):
    """
    Splits a given text to num_extracts at the end of sentence marks: .!?;"
    """
    sentences = split_to_sentences(text)
    extracts = np.array_split(sentences, num_extracts)
    extracts = [' '.join(extract) for extract in extracts]
    return extracts


def split_to_sentences(text):
    """
    Args: 
        text (str): raw text to split to sentences on end of sentences marks.
    Returns:
        List of sentences from text.
    """
    # Multiple options Negative lookbehind to prevent splitting on Mr. or Mrs.
    split_pattern = r'(?<!Mr)(?<!Mrs)[.!?;"]+'
    # Split on end of sentence, but keep the punctuation marks.
    sentences = list(map(str.strip, re.sub(
        split_pattern, r'\g<0>[cut]', text.strip()).split('[cut]')))
    # If the last sentence is ''
    if len(sentences) > 1 and len(sentences[-1]) < 3:
        sentences.pop()
    return sentences


def split_words(text):
    return re.split(r'[ ](?=[\w])', text)


def generate_prompt(nlp, example):
    """
    Per text example, returns a string prompt consisting of the most_freq_num most frequent noun chunks.
    Args:
        nlp (Spacy parser model): used to generate doc.
        stop_words (set): A set of words to ignore such as who, he ..
        example (str): the input text to check for noun chunks.
        most_freq_num (int): the number of noun chunks to return
    """
    doc = nlp(example)
    prompt_nouns = []
    for token in doc:
        if token.is_alpha and not token.is_stop and (token.pos_ == 'NOUN' or token.pos_ == 'PROPN') and token.text.lower() not in set(['chapter']):
            prompt_nouns.append(token.text)
    freq_chunks = Counter(prompt_nouns).most_common()
    return " ".join(map(lambda tup: tup[0], freq_chunks))
