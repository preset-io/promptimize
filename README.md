<img src="https://user-images.githubusercontent.com/487433/229948453-36cbc2d1-e71f-4e87-9111-ab428bc96f4c.png" width=300/>

**Promptimize** is a framework that accelerates prompt engineering,
crafting, and evaluation.

Use `promptimize` to define your prompts as code, tie them to evaluation functions,
generate prompt variations dynamically, execute and rank across different
engines, and get reporting on how your prompts perform.

Promptimize offers a programmatic way to define and tune your prompt and evaluation
functions in Python in a way that allows you to iterate quickly and confidently.

## Problem + POV

Millions of product builders are currently trying to figure out how to
bring the power of AI into the products and experiences they are building.
The probabilistic (often semi-random, sometimes hectic) nature of LLMs
makes this a challenge.

Prompt engineering is a huge piece of the puzzle in terms of how to do this
right, especially given the complexity, risks, and drawbacks around
model tuning.

We believe product builders need to tame AI through proper, rigorous
**prompt engineering**. This allows making the probabilistic nature of
AI more deterministic, or somewhat predictable, and allows builders to apply
a hyperparameter tuning-type mindset and approach to prompt engineering.

In short, Promptimize allows you to generate and test prompts at industrial scale,
so that you can confidently use them in the products you are building.

## Information Architecture

- **Prompt:** A Prompt instance is a certain test case, a single prompt
  with an associated set of evaluation functions to rate its success.
- **Eval:** An evaluation function that reads the response and returns
  a success rate between `0` and `1`.
- **Suite:** A Suite is a collection of Prompt; it's able to run things,
  accumulate results, and print reports about its collection of use cases.

## Principles

- **Configuration as code:** All use cases, suites, and evaluations are defined as code,
  which makes it easy to dynamically generate all sorts of use cases and suites.
- **Support the iteration mindset:** making it easy for people to try things,
  get suggestions from the AI, adapt, compare, and push forward
- **Extensibility:** the framework is designed to be extremely hackable and
  extensible. Hooks, extensions, high API surface.

## Setup

To install the Promptimize package, use the following command:
```bash
pip install promptimize
```

## Getting started

First you'll need an openai API key, let's set it as an env var
```bash
export OPENAI_API_KEY=sk-{REDACTED}
```

Find the examples bellow [here](https://github.com/preset-io/promptimize/blob/master/examples/readme_examples.py)

```python
# Brining some "prompt generator" classes
from promptimize.prompt import SimplePrompt, TemplatedPrompt

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

    # Making sure 3 specific guitar players are in the top 50
    # the score here is a percentage of the words found
    SimplePrompt(
        "who are the top 50 best guitar players of all time?",
        lambda x: evals.percentage_of_words(
            x, ["frank zappa", "david gilmore", "carlos santana"]
        ),
    ),
    # GPT-ing myself and making sure the response mentions Superset and Airflow
    SimplePrompt(
        "who is Maxime Beauchemin, (the data guy...)?",
        lambda x: evals.percentage_of_words(x, ["superset", "airflow"], case_sensitive=False),
    ),
]

# deriving TemplatedPrompt to generate prompts that ask GPT to generate SQL
# based on table schemas. The point here is you can derive the `Prompt`
# class to create more specialized Prompt generators
# For instance, the SqlPropt class defined bellow could be extended to fetch
# schema definitions dynamically, acutally run the SQL, and allow
# doing evals against the resultset.

class SqlPrompt(TemplatedPrompt):
    # the TemplatedPrompt expects a dict of defaults that can be overriden in the constructor
    template_defaults = {"dialect": "Postgres"}
    # The actual Jinja2 template
    prompt_template = """\
    given these SQL table schemas:
        CREATE TABLE world_population (
            country_name STRING,
            year DATE,
            population_total INT,
        );

    So, can you write a SQL query for {{ dialect }} that answers this user prompt:
    {{ input }}
    """

# Generating a few SQL prompts
sql_prompts = [
    SqlPrompt(
        # the user input that'll be added in place of {{ input }} in the template above
        "give me the top 10 countries with the highest net increase of population over the past 25 years?",
        # the dialect template parameter, overriding the default set above
        dialect="BigQuery",
        # a simple validation function making sure the SQL starts with SELECT
        evaluators=[lambda x: x.trim().startswith("SELECT")],
    ),
]

```

```bash
# NOTE: CLI is `promptimize`, but `p9e` is a shorter synonym, can be used interchangibly

# First let's run some of the examples
p9e ./examples

# Now the same but with verbose output
p9e ./examples --verbose

```

Now take a look at the definitions of what you just ran here ->
[Promptimize examples on GitHub](https://github.com/preset-io/promptimize/tree/master/examples)

## Resources
* [GPT interactive playground](https://platform.openai.com/playground/p/default-adv-tweet-classifier)

## TODO
* allow to actually run the SQL
* do assertions on result sets
* parameterize your run, pick your engine, temperatur
* bring in the system message
* parallel execution
* pypi
