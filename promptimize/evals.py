"""
Eval functions that be used/reused with Prompts

All functions here are expected to:
* receive a response string
* [optional] receive arbitrary extra context
* return a value from 0 to 1, 0 representing failing at the task, 1 full
success, and a range in-between
"""

import os
from typing import List, Optional

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate


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
    >>> percentage_of_words_in_response(
        "This is an Example string.", ["Example"], case_sensitive=True)
    1.0
    >>> percentage_of_words_in_response(
        "This is an Example string.", ["example"], case_sensitive=True)
    0.0
    >>> percentage_of_words_in_response("This is an Example string.", ["notfound"])
    0.0
    """
    if not case_sensitive:
        response = response.lower()
        words = [w.lower() for w in words]

    return sum(1 if w in response else 0 for w in words) / len(words)


def _common_word_search(
    response: str, words: List[str], case_sensitive: bool, match_type: str
) -> int:
    if not case_sensitive:
        response = response.lower()
        words = [w.lower() for w in words]

    if match_type == "any":
        return 1 if any(w in response for w in words) else 0
    elif match_type == "all":
        return 1 if all(w in response for w in words) else 0
    else:
        raise ValueError("Invalid match_type. Accepted values are 'any' or 'all'.")


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
    >>> any_word("This is an Example string.", ["example", "test"])
    1
    >>> any_word("This is an Example string.", ["Example"], case_sensitive=True)
    1
    >>> any_word("This is an Example string.", ["example"], case_sensitive=True)
    0
    >>> any_word("This is an Example string.", ["notfound"])
    0
    """
    return _common_word_search(response, words, case_sensitive, match_type="any")


def all_words(response: str, words: List[str], case_sensitive: bool = False) -> int:
    """
    Check if all words from a list of words are present in the given response and return 1 or 0.

    Args:
        response (str): The string to search for words.
        words (List[str]): A list of words to check for their presence in the response.
        case_sensitive (bool, optional): If True, the search will be case-sensitive;
                                         otherwise, it will be case-insensitive. Defaults to False.

    Returns:
        int: 1 if all words from the list are found in the response; otherwise, 0.

    Examples:
    >>> all_words("This is an Example string with test.", ["example", "test"])
    1
    >>> all_words("This is an Example string with Test.", ["Example", "Test"], case_sensitive=True)
    1
    >>> all_words("This is an Example string.", ["example", "test"], case_sensitive=True)
    0
    >>> all_words("This is an Example string.", ["example", "notfound"])
    0
    """
    return _common_word_search(response, words, case_sensitive, match_type="all")


base_all = all
base_any = any


def all(iteratable):
    return 1 if base_all([i == 1 for i in iteratable]) else 0


def any(iteratable):
    return 1 if base_any([i == 1 for i in iteratable]) else 0


def is_correct(
    response: str, question: str, expected: str, model_name: Optional[str] = None
) -> int:
    """
    Query a LLM to calculate the correctness of the expected and the given response.

    Args:
        question (str): The question to be answered.
        response (str): The answer given by the LLM.
        expected (str): The expected answer.

    Returns:
        int: 1 if the answer in the response is CORRECT to the expected one; otherwise, 0.

    Examples:
    >>> is_correct("5", "7")
    0
    >>> is_correct("5", "5.0")
    1
    >>> is_correct("a dog", "a cat")
    0
    """
    model_name = model_name or "gpt-4"  # GPT-4 works great for evaluating correctness
    llm = ChatOpenAI(model_name=model_name, openai_api_key=os.environ.get("OPENAI_API_KEY"))
    prompt = PromptTemplate(
        input_variables=["response", "expected", "question"],
        template=IS_CORRECT_TEMPLATE,
    ).format(response=response, expected=expected, question=question)

    response = llm.predict(prompt)

    return 0 if "INCORRECT" in response else 1


IS_CORRECT_TEMPLATE = """
You are a teacher grading an answer.
You are given a expected anwer and the actual answer. You are asked to score the answer as either CORRECT or INCORRECT, based on the context.

Example Format:
QUESTION: question here
EXPECTED ANSWER: expected answer here
ANSWER: actual answer here
GRADE: CORRECT or INCORRECT here

Grade the answers based ONLY on their accuracy compared with the expected ones, no matter of the actual accuracy. Ignore differences in punctuation and phrasing between the answer and true answer. It is OK if the answer contains more information than the true answer, as long as it does not contain any conflicting statements. Begin!

QUESTION: {question}
EXPECTED ANSWER: {expected}
ANSWER: {response}
GRADE: """
