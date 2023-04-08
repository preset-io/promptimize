"""
Some basic examples for promptimize.

to run, simply execute `p9e ./examples/readme_examples.py`
"""
# Brining some "prompt generator" classes
from promptimize.prompts import SimplePrompt, TemplatedPrompt

# Bringing some useful eval function that help evaluating and scoring responses
# eval functions have a handle on the prompt object and are expected
# to return a score between 0 and 1
from promptimize import evals

# Promptimize will scan the target folder and find all Prompt objects
# and derivatives that are in the python modules
simple_prompts = [
    # Prompting "hello there" and making sure there's "hi" or "hello"
    # somewhere in the answer
    SimplePrompt("hello there!", lambda x: evals.any_word(x, ["hi", "hello"])),
    SimplePrompt(
        "name the top 10 guitar players!",
        lambda x: evals.all_words(x, ["frank zappa"]),
        weight=2,
    ),
]
