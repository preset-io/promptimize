# 💡 ¡promptimize! 💡
<img src="https://user-images.githubusercontent.com/487433/229948453-36cbc2d1-e71f-4e87-9111-ab428bc96f4c.png" width=300/>

**Promptimize** is a framework that accelerates prompt engineering,
crafting, and evaluation.

Use `promptimize` to
- define your prompts as code and tie them to evaluation functions
- generate prompt variations dynamically
- execute and rank across different engines
- get reporting on how your prompts perform

In short, `promptimize` offers a programmatic way to define and tune
your prompt and evaluation functions in Python in a way that allows
you to iterate quickly and confidently.

## Hello world - the simplest prompt examples
[more examples on GitHub](https://github.com/preset-io/promptimize/tree/master/examples)
```python
# Brining some "prompt generator" classes - note that you can derive and extend those
from promptimize.prompt import SimplePrompt

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
        "name the top 50 guitar players!", lambda x: evals.all_words(x, ["frank zappa"])
    ),
]
```

### The CLI
```bash
$ promptimize examples/readme_hello_world.py
💡 ¡promptimize! 💡
# ----------------------------------------
# Prompt prompt-c6950959
# ----------------------------------------
key: prompt-c6950959
input: hello there!
response_text: Hi there! How are you?
test_results_avg: 1.0

# ----------------------------------------
# Prompt prompt-7bfe4487
# ----------------------------------------
key: prompt-7bfe4487
input: name the top 50 guitar players!
response_text: |-
  1. Jimi Hendrix
  2. Eric Clapton
  3. Jimmy Page
  {...}
  50. Jerry Garcia
test_results_avg: 0.0

# ----------------------------------------
# Suite summary
# ----------------------------------------
suite_score: 0.5
completion_create_kwargs:
  engine: text-davinci-003
  max_tokens: 1000
  temperature: 0.5
```

## Problem + POV

Thousands of product builders are currently trying to figure out how to
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

## The CLI
```bash
$ promptimize --help
Usage: promptimize [OPTIONS] PATH


Options:
  -v, --verbose             Trigger more verbose output
  -s, --style [json|yaml]   json or yaml formatting
  -m, --max-tokens INTEGER  max_tokens passed to the model
  -t, --temperature FLOAT   max_tokens passed to the model
  -e, --engine TEXT         model as accepted by the openai API
  --help                    Show this message and exit.
```

## Resources
* [GPT interactive playground](https://platform.openai.com/playground/p/default-adv-tweet-classifier)

## Context

<img src="https://user-images.githubusercontent.com/487433/230508578-456a7040-1184-433a-a555-dceb7c28c32c.png" width="75" title="Max"/>

Where is `promptimize` coming from!? I'm (Maxime Beauchemin) a startup
founder at <a href="www.preset.io">Preset</a> working on brining AI to BI
(data exploration,
and visualization). At Preset, we use `promptimize` to generate
complex SQL based on natural language, and to suggest charts to users. We
derive the `SimpleQuery` class to make it fitted to our specific use
cases in our own prompt engineering repo. Not my first open source project
as the creator of
[Apache Superset](https://github.com/apache/superset/) and
[Apache Airflow](https://github.com/apache/airflow/)

## Disclaimer

"Publish early, publish often!" This project is pretty much at `0.1.0`
and the creator is a busy man
(running www.preset.io), and actually extending and using this framework
to work on bringing AI to BI. Contributions, contributors and maintainers
are more than welcomed! Looking forward to engage directly with all
contributors! To get involved, open an GitHub issue detailing how you'd
like to get involved, or just open a PR!
