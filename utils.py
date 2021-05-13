#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue April 20 2021

@author: Xiaoyu Lu
"""
from typing import Dict, Union, List, Generator, DefaultDict, Set, Tuple, Any
import os
import json
import xml.etree.ElementTree as ET
from collections import defaultdict
import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
import bisect
from nltk.tokenize.treebank import TreebankWordDetokenizer
from hyphenate import hyphenate_word
import string

PUNC = set(string.punctuation)
lemmatizer = WordNetLemmatizer()
detokenizer = TreebankWordDetokenizer()


def load_clean_wapo_with_embedding(
        wapo_jl_path: Union[str, os.PathLike]
) -> Generator[Dict, None, None]:
    """
    load wapo docs as a generator
    :param wapo_jl_path:
    :return: yields each document as a dict
    """
    with open(wapo_jl_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            yield json.loads(line)


def parse_wapo_topics(xml_file: str) -> Dict[str, List[str]]:
    """
    parse topics2018.xml
    :param xml_file:
    :return: a dict that maps the topic id to its title. narrative and description
    """
    text = open(xml_file, "r").read()
    topic_mapping = defaultdict(list)

    for xml_str in text.strip().split("\n\n"):
        tree = ET.fromstring(xml_str)
        topic_id = ""
        for child in tree:
            if child.text:
                if child.tag == "num":
                    # get topic id
                    topic_id = child.text.split(":")[-1].strip()
                else:
                    # append others to this topic id
                    topic_mapping[topic_id].append(child.text.strip().split("\n")[-1])
    return topic_mapping


def get_wordnet_pos(word: str) -> Dict[str, Any]:
    """
    Map POS tag to first character lemmatize() accepts
    reference: https://www.machinelearningplus.com/nlp/lemmatization-examples-python/
    """
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}

    return tag_dict.get(tag, wordnet.NOUN)


def normalize_func(text: str) -> List[str]:
    """telling -> tell, are-> be"""
    tokens = nltk.word_tokenize(text)  # need to be consistent with the basic tokenize used in other functions
    return [lemmatizer.lemmatize(w.lower(), get_wordnet_pos(w.lower())) for w in tokens]


def normalize_query(text: str) -> List[str]:
    """telling -> tell, are-> be, remove punctuation"""
    tokens = nltk.word_tokenize(text.lower())
    return [lemmatizer.lemmatize(w, get_wordnet_pos(w)) for w in tokens if w not in PUNC]


def get_word_dict(doc: str) -> DefaultDict[str, Set[int]]:
    # doc_tokens_basic = nltk.word_tokenize(doc)
    doc_tokens = normalize_func(doc)
    # assert len(doc_tokens) == len(doc_tokens_basic)
    word_idx_dict = defaultdict(set)
    for i, token in enumerate(doc_tokens):
        if token not in PUNC and len(token) > 4:
            split_words: List[str] = hyphenate_word(token)
            for word in split_words:
                if len(word) >= 4:
                    word_idx_dict[word].add(i)  # hyphenate_word can help handle fish vs. Frankenfish
        if token in [".", "?", "!"]:
            word_idx_dict["eos_sign"].add(i)
        else:
            word_idx_dict[token].add(i)  # cannot handle fish vs. Frankenfish alone
    return word_idx_dict


def get_seg(seg_idx: List[int], breakpoints: List[int]) -> Tuple[Union[int, Any], Union[int, Any], int, int]:
    """
    get the subset with maximum length
    Example1:
    seg_idx =  [4, 10, 19]
    breakpoints = [2,3,5,9,11,13,15,18]
    res: 4, 8 => [11,13,15,18]
    Example2:
    seg_idx = [32, 60, 88, 118, 134, 144, 196, 204, 233, 265, 279, 313]
    breakpoints = [6, 8, 65, 253]
    res: 0, 2 => [6,8]
    """
    l, r = 0, 0
    left, right = 0, 0
    bos_i, eos_i = 0, 0
    n = len(breakpoints)
    i, flag = 0, 0
    for j, idx in enumerate(seg_idx):
        i = bisect.bisect(breakpoints, idx, lo=i)
        if i >= n - 1 and flag:  # optimize: reach the end of break-point, no needs to keep counting
            break
        elif i >= n - 1 and not flag:
            flag += 1
        if i - r > right - left:
            left, right = r, i
            bos_i, eos_i = j - 1, j
        if i > r:
            l, r = r, i
    return left, right, bos_i, eos_i


def add_bold(sent_pieces: List[str], bold_indices: List[int]) -> str:
    """Untokenize a sentence with bold tags"""
    for idx in bold_indices[::-1]:
        sent_pieces[idx] = "<strong>" + sent_pieces[idx] + "</strong>"
    return detokenizer.detokenize(sent_pieces)


if __name__ == "__main__":
    pass
