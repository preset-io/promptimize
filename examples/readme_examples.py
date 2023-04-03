"""
Some basic examples for promptimize.

to run, simply execute `p9e ./examples/readme_examples.py`
"""
# Brining some "prompt generator" classes
from promptimize.prompt_cases import PromptCase, TemplatedPromptCase

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
    # Making sure 3 specific guitar players are in the top 10
    # the score here is a percentage of the words found
    PromptCase(
        "who are the top 10 best guitar players of all time?",
        lambda x: evals.percentage_of_words(
            x.response, ["frank zappa", "david gilmore", "carlos santana"]
        ),
    ),
    # GPT-ing myself and making sure the response mentions Superset and Airflow
    PromptCase(
        "who is Maxime Beauchemin, (the data guy...)?",
        lambda x: evals.percentage_of_words(
            x.response, ["superset", "airflow"], case_sensitive=False
        ),
    ),
]

# deriving TemplatedPromptCase to generate prompts that ask GPT to generate SQL
# based on table schemas. The point here is you can derive the `Prompt`
# class to create more specialized Prompt generators
# For instance, the SqlPropt class defined bellow could be extended to fetch
# schema definitions dynamically, acutally run the SQL, and allow
# doing evals against the resultset.


class SqlPrompt(TemplatedPromptCase):
    # the TemplatedPromptCase expects a dict of defaults that can be overriden in the constructor
    template_defaults = {"dialect": "Postgres"}
    # The actual Jinja2 template
    template = """\
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
        # you can pass a unique key that can we used to reference a prompt
        key="sql-top-10-inc",
        # the user input that'll be added in place of {{ input }} in the template above
        user_input="give me the top 10 countries with the highest net increase of population over the past 25 years?",
        # the dialect template parameter, overriding the default set above
        dialect="BigQuery",
        # a simple validation function making sure the SQL starts with SELECT
        evaluators=lambda x: 1 if x.response.strip().startswith("SELECT") else 0,
    ),
]
