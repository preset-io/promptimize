<img src="https://user-images.githubusercontent.com/487433/229948453-36cbc2d1-e71f-4e87-9111-ab428bc96f4c.png" width=300/>

**Promptimize** is a framework that accelerates prompt enginering,
crafting and evaluation.

Use `promptimize` to define your prompts as code, tie them to eval functions,
generate prompt variations dynamically, execute and rank across different
engines, and get reporting on how your prompts perform.

Promptimize offers a programmatic way to define and tune your prompt and eval
functions in python quickly, this allows you to iterate quickly.

## Information architecture
* **Prompt:** a Prompt instance is a certain test case, a single prompt
  with an associated set of eval functions to rate it's success
* **Eval:** an evaluation function that reads the response and returns
  a success rate between `0` and `1`
* **Suite:**: a Suite is a collection of Prompt, it's able to run things
  accumulate results, and print reports about its collection of use cases

## Princicples
* **Configuration as code:** all use cases, suites and evals are defined as code,
  this makes it easy to dynamically generate all sorts of use cases and suites
* **Constant suggestion**: the framework is great at running your use cases
  and evaluating them, but GPT engines are great at suggesting improvements
  on each prompt too

## Setup
```bash
# in dev mode
git clone git@github.com:preset-io/promptimize.git
pip -e .
```

## Getting started

First you'll need an openai API key, let's set it as an env var
```bash
export OPENAI_API_KEY=sk-{REDACTED}
```

## Example
```python
from promptimize.prompt import SimplePrompt, TemplatedPrompt

# Promptimize will scan the folder and find all Prompt objects and derivatives
uses_cases = [

    # Prompting "hello there" and making sure there's "hi" somewhere in the answer
    SimplePrompt("hello there!", lambda x: "hi" in x.lower()),

    # making sure zappa is in the list of top 50 guitar players!
    SimplePrompt("who are the top 50 best guitar players of all time?", lambda x: "zappa" in x.lower()),

    SimplePrompt("who is Maxime Beauchemin?", lambda x: 0.5 if "superset in x.lower()" else 0 +  0.5 if "airflow in x.lower()")
]

# deriving TemplatedPrompt to get GPT to generate some SQL
class SqlPrompt(TemplatedPrompt):
    template_defaults = {"dialect": "Postgres"}
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

another_list = [
    TemplatedPrompt(
        "give me the top 10 countries with the highest net increase of population over the past 25 years?",
        dialect="BigQuery",
        evaluators=[lambda x: x.trim().startswith('SELECT')],
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
