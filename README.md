# 💡 ¡promptimize! 💡
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI version](https://badge.fury.io/py/promptimize.svg)](https://badge.fury.io/py/promptimize)

<img src="https://user-images.githubusercontent.com/487433/229948453-36cbc2d1-e71f-4e87-9111-ab428bc96f4c.png" width=300/>

Promptimize is a prompt engineering **evaluation** and **testing** toolkit.

It accelerates and provides structure around prompt engineering at scale
with confidence, bringing some of the ideas behind test-driven
development (TDD) to engineering prompts.

With promptimize, you can:

- Define your "prompt cases" (think "test cases" but specific to evaluating
  prompts) as code and associate them with evaluation functions
- Generate prompt variations dynamically
- Execute and rank prompts test suites across different
  engines/models/temperature/settings and compare results, brining
  the hyperparameter tuning mindset to prompt engineering
- Get reports on your prompts' performance as you iterate. Answer question
  around how different prompt suites are performing against one-another.
  Which individual cases or categories of cases improved? regressed?
- Minimize API calls! only re-assess what changed as you change it
- Perform human if and where needed, introspected failed cases, overriding
  false negatives

In essence, promptimize provides a programmatic way to execute and fine-tune
your prompts and evaluation functions in Python, allowing you to iterate
quickly and with confidence.

## Hello world - the simplest prompt examples
[more examples on GitHub](https://github.com/preset-io/promptimize/tree/main/examples)
```python
# Brining some "prompt generator" classes - note that you can derive and extend those
from promptimize.prompts import SimplePrompt

# Bringing some useful eval function that help evaluating and scoring responses
# eval functions have a handle on the prompt object and are expected
# to return a score between 0 and 1
from promptimize import evals

# Promptimize will scan the target folder and find all Prompt objects
# and derivatives that are in the python modules
simple_prompts = [

    # Prompting "hello there" and making sure there's "hi" or "hello"
    # somewhere in the answer
    PromptCase("hello there!", lambda x: evals.any_word(x, ["hi", "hello"])),
    PromptCase(
        "name the top 50 guitar players!", lambda x: evals.all_words(x, ["frank zappa"])
    ),
]
```

### The CLI's `run` command
```
$ promptimize run --help
Usage: promptimize run [OPTIONS] PATH

  run some prompts

Options:
  -v, --verbose             Trigger more verbose output
  -f, --force               Force run, do not skip
  -h, --human               Human review, allowing a human to review and force
                            pass/fail each prompt case
  -r, --repair              Only re-run previously failed
  -x, --dry-run             DRY run, don't call the API
  --shuffle                 Shuffle the prompts in a random order
  -s, --style [json|yaml]   json or yaml formatting
  -m, --max-tokens INTEGER  max_tokens passed to the model
  -l, --limit INTEGER       limit how many prompt cases to run in a single
                            batch
  -t, --temperature FLOAT   max_tokens passed to the model
  -e, --engine TEXT         model as accepted by the openai API
  -k, --key TEXT            The keys to run
  -o, --output PATH
  -s, --silent
```

Let's run those examples and produce a report `./report.yaml`
```
$ promptimize run examples/ --output ./report.yaml
```

```yaml
💡 ¡promptimize! 💡
# ----------------------------------------
# (1/2) [RUN] prompt: prompt-115868ef
# ----------------------------------------
key: prompt-115868ef
user_input: hello there!
prompt_hash: 115868ef
response: Hi there! How are you doing today?
execution:
  api_call_duration_ms: 883.8047981262207
  run_at: '2023-04-25T02:21:40.443077'
  score: 1.0

# ----------------------------------------
# (2/2) [RUN] prompt: prompt-5c085656
# ----------------------------------------
key: prompt-5c085656
user_input: name the top 10 guitar players!
prompt_hash: 5c085656
response: |-
  1. Jimi Hendrix
  2. Eric Clapton
  {{ ... }}
  11. Carlos Santana
weight: 2
execution:
  api_call_duration_ms: 2558.135747909546
  run_at: '2023-04-25T02:21:43.007529'
  score: 0.0

# ----------------------------------------
# Suite summary
# ----------------------------------------
suite_score: 0.3333333333333333
git_info:
  sha: 2cf28498ba0f
  branch: main
  dirty: true
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

Any prompt-generator logic that's going to be let loose in the wild inside
a product should be thoroughly tested and evaluated with "prompt cases" that
cover the breath of what people may do in a product.

In short, Promptimize allows you to test prompts at industrial scale,
so that you can confidently use them in the products you are building.

## Information Architecture

- **Prompt:** A Prompt instance is a certain test case, a single prompt
  with an associated set of evaluation functions to rate its success.
- **Evaluation:** An evaluation function that reads the response and returns
  a success rate between `0` and `1`.
- **Suite:** A Suite is a collection of Prompt; it's able to run things,
  accumulate results, and print reports about its collection of use cases.
- **Report**: a report is the compiled results of running a certain prompt
  `Suite` or set of suites. Reports can be consumed, compared, and expanded.

## Principles

- **Configuration as code:** All prompt cases, suites, and evaluations are
  defined as code, which makes it easy to dynamically generate all sorts
  of use cases and suites.
- **Expressive**: a clean DSL that's to-the-point -> user prompt + assertions.
  the actually prompt creation logic lives in the derivative class of `PromptCase`,
  so that we can have clean, dense files that contain nice `Suite`s
- **Support the iteration mindset:** making it easy for people to try things,
  get suggestions from the AI, adapt, compare, and push forward
- **Extensibility:** the toolkit is designed to be extremely hackable and
  extensible. Hooks, extensions, high API surface.
- **AI-powered:** the framework offers ways to expand your suites based
  on the examples that exists. Use AI to generate more prompt cases!


## Interesting features / facts

Listing out a few features you should know about that you can start using as your
suites of prompts become larger / more complex

* evaluation functions are assumed to return a value between 0 and 1.
  contrarily to unit tests, prompt cases aren't boolean
* prompts can be assigned a `weight` (default 1) this enables you to define
  which prompts are more important than others for reporting purposes and suite evaluation
* prompts can be assigned a `category`, this can be used in the reporting.
  That helps understanding which categories are performing better than
  others, or are most affected by iterations
* The `Prompt` class `pre_run` and `post_run` hooks if you want to do
  post-processing for instance. An example of that would be if you do a prompt
  that expects GPT to generate code, and you'd like actually say run that code
  and test it. In our SQL implementation, we run the SQL against the database
  for instance and get a pandas dataframe back, and allow doing assertions
  on the dataframe itself



## Getting started

To install the Promptimize package, use the following command:
```bash
pip install promptimize
```

First you'll need an openai API key, let's set it as an env var
```bash
export OPENAI_API_KEY=sk-{{ REDACTED }}
```

Find the examples executed below
[here](https://github.com/preset-io/promptimize/blob/main/examples/readme_examples.py)

```bash
# Clone the repo
git clone git@github.com:preset-io/promptimize.git
cd promptimize

# NOTE: CLI is `promptimize`, but `p9e` is a shorter synonym, can be used interchangibly
# First let's run some of the examples
p9e run ./examples

# Now the same but with verbose output
p9e run ./examples --verbose --output ./report.yaml

```
## Langchain

How does promptimize relate to `langchain`?

We think langchain is amazing and promptimize uses langchain under the
hood to interact with openai, and has integration with langchain
(see `LangchainPromptCase`, and the upcoming `LangchainChainPromptCase`
and `LangchainAgntPromptCase`)
While you don't have to use
langchain, and could use promptimize on top of any python prompt generation
whether it'd be another library or some home grown thing.


## Context

<img src="https://user-images.githubusercontent.com/487433/230508578-456a7040-1184-433a-a555-dceb7c28c32c.png" width="75" title="Max"/>

Where is `promptimize` coming from!? I'm (Maxime Beauchemin) a startup
founder at <a href="www.preset.io">Preset</a> working on brining AI to BI
(data exploration,
and visualization). At Preset, we use `promptimize` to generate
complex SQL based on natural language, and to suggest charts to users. We
derive the `SimpleQuery` class to make it fitted to our specific use
cases in our own prompt engineering repo. It's not my first open source project
as the creator of
[Apache Superset](https://github.com/apache/superset/) and
[Apache Airflow](https://github.com/apache/airflow/)


## Contribute

This project is in its super early stages as of `0.2.0`, and contributions,
contributors, and maintainers are highly encouraged. While it's a great time
to onboard and influence the direction of the project, things are still
evolving quickly. To get involved, open a GitHub issue
or submit a pull request!

## Links
* [Blog - Mastering AI-Powered Product Development: Introducing Promptimize for Test-Driven Prompt Engineering](https://preset.io/blog/introducing-promptimize/)
* [Preset Blog](https://preset.io/blog/)
* [Promptimize DOCS](https://preset-io.github.io/promptimize/)
