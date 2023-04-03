"""
Some basic examples for promptimize.

to run, simply execute `p9e ./examples/readme_examples.py`
"""
# Brining some "prompt generator" classes
from promptimize.prompt_cases import PromptCase

# Bringing some useful eval function that help evaluating and scoring responses
# eval functions have a handle on the prompt object and are expected
# to return a score between 0 and 1
from promptimize import evals

# Promptimize will scan the target folder and find all Prompt objects
# and derivatives that are in the python modules
simple_prompts = [
    # Prompting "hello there" and making sure there's "hi" or "hello"
    # somewhere in the answer
    PromptCase("hello there!", lambda x: evals.any_word(x.response, ["hi", "hello"])),
    PromptCase(
        "name the top 10 guitar players!",
        lambda x: evals.all_words(x.response, ["zappa", "hendrix"]),
        weight=2,
    ),
]
