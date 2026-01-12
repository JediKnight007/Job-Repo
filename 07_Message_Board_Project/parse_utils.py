import math
import re
import sys
import xml.etree.ElementTree as et

from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from tqdm import tqdm

from collections.abc import Callable

STOP_WORDS = set(stopwords.words("english"))
nltk_ps = PorterStemmer()
tokenization_regex = r"\[\[[^\[]+?\]\]|[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+"


def stem_and_stop(word: str):
    """
    Checks if word is a stop word, converts to lowercase, and stems

    Parameters:
        word            the word to check
    Returns:
        ""              if the word is a stop word
        stemmed_word    otherwise
    """
    if word.lower() in STOP_WORDS:
        return ""

    return nltk_ps.stem(word.lower())


def word_is_link(word: str) -> bool:
        """
        Checks if the word is a link (surrounded by '[[' and ']]')

        Parameters:
            word            the word to check
        Returns:
            true            if the word is a link
            false           otherwise
        """
        link_regex = r"\[\[[^\[]+?\]\]"
        return bool(re.match(link_regex, word))


def split_link(link: str) -> "tuple[list[str], str]":
    """
    Splits a link (assumed to be surrounded by '[[' and ']]') into the text
    and the destination of the link

    Parameters:
        link            the link to split
    Returns:
        a tuple of the format (link text, link destination)
    """
    is_word_regex = r"[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+"

    # assume that the link is surrounded by '[[' and ']]'
    link_stripped_brackets = link[2:-2]

    title_raw = link_stripped_brackets
    text_raw = link_stripped_brackets

    # text and title differ
    if '|' in link_stripped_brackets:
        link_split = link_stripped_brackets.split("|")
        text_raw = link_split[0]
        title_raw = link_split[1]

    return (re.findall(is_word_regex, text_raw), title_raw.strip())


def get_tokens(text: str) -> list:
    """
    Uses a regular expression to split the title and page text into a 
    list of individual words and link structures

    Parameters:
        text       the string to split into tokens

    Returns:  
        a list of all the word and link tokens in the string
    """
    return re.findall(tokenization_regex, f"{text}")
        
        
# the type Callable represents a function. In this case, the function 
# takes a single string as input and returns None
def parse(wiki: str, process_page: Callable[[str], None]) -> None:
    """
    Reads in an xml file, parses titles and ids, tokenizes text, removes stop words, does stemming, and processes links.

    Updates ids_to_titles, titles_to_ids, words_to_doc_frequency, ids_to_max_counts, and ids_to_links

    Parameters:
        input_file            path to the XML file to parse
    """

    # load XML + root
    wiki_tree = et.parse(wiki)
    wiki_xml_root = wiki_tree.getroot()

    # For each page: get titles and ids
    for wiki_page in tqdm(wiki_xml_root):
        process_page(wiki_page)
