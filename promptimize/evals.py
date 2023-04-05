"""
Eval functions that be used/reused with Prompts

All functions here are expected to:
* receive a response string
* [optional] receive arbitrary extra context
* return a value from 0 to 1, 0 representing failing at the task, 1 full
  success, and a range in-between
"""

from typing import List

def percentage_of_words(response: str, words: List[str], case_sensitive: bool = False) -> float:
    """
    Calculate the percentage of words from a list that are present in the given response.

    Args:
        response (str): The string to search for words.
        words (List[str]): A list of words to check for their presence in the response.
        case_sensitive (bool, optional): If True, the search will be case-sensitive;
                                         otherwise, it will be case-insensitive. Defaults to False.

    Returns:
        float: The percentage of words found in the response (0.0 to 1.0).

    Examples:
    >>> percentage_of_words_in_response("This is an Example string.", ["example", "test"])
    0.5
    >>> percentage_of_words_in_response("This is an Example string.", ["Example"], case_sensitive=True)
    1.0
    >>> percentage_of_words_in_response("This is an Example string.", ["example"], case_sensitive=True)
    0.0
    >>> percentage_of_words_in_response("This is an Example string.", ["notfound"])
    0.0
    """
    if not case_sensitive:
        response = response.lower()
        words = [w.lower() for w in words]

    return sum(1 if w in response else 0 for w in words) / len(words)

def any_word(response: str, words: List[str], case_sensitive: bool = False) -> int:
    """
    Check if any word from a list of words is present in the given response and return 1 or 0.

    Args:
        response (str): The string to search for words.
        words (List[str]): A list of words to check for their presence in the response.
        case_sensitive (bool, optional): If True, the search will be case-sensitive;
                                         otherwise, it will be case-insensitive. Defaults to False.

    Returns:
        int: 1 if any word from the list is found in the response; otherwise, 0.

    Examples:
    >>> any_word_in_response("This is an Example string.", ["example", "test"])
    1
    >>> any_word_in_response("This is an Example string.", ["Example"], case_sensitive=True)
    1
    >>> any_word_in_response("This is an Example string.", ["example"], case_sensitive=True)
    0
    >>> any_word_in_response("This is an Example string.", ["notfound"])
    0
    """
    if not case_sensitive:
        response = response.lower()
        words = [w.lower() for w in words]

    return 1 if any(w in response for w in words) else 0
