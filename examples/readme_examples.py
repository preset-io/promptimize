"""
Some basic examples for promptimize.

to run, simply execute `p9e ./examples/readme_examples.py`
"""
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
        lambda x: evals.percentage_of_words(
            x, ["superset", "airflow"], case_sensitive=False
        ),
    ),
]

# deriving TemplatedPrompt to generate prompts that ask GPT to generate SQL
# based on table schemas
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


# Generating a few SQL prompts
sql_prompts = [
    SqlPrompt(
        "give me the top 10 countries with the highest net increase of population over the past 25 years?",
        dialect="BigQuery",
        evaluators=[lambda x: x.trim().startswith("SELECT")],
    ),
]
