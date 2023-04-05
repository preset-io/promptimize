from promptimize.prompt import SimplePrompt, TemplatedPrompt
from promptimize import evals

# Promptimize will scan the folder and find all Prompt objects and derivatives
uses_cases = [
    # Prompting "hello there" and making sure there's "hi" somewhere in the answer
    SimplePrompt("hello there!", lambda x: evals.any_word(x, ["hi", "hello"])),
    # making sure zappa is in the list of top 50 guitar players!
    SimplePrompt(
        "who are the top 50 best guitar players of all time?",
        lambda x: evals.percentage_of_words(
            x, ["frank zappa", "david gilmore", "carlos santana"]
        ),
    ),
]

# deriving TemplatedPrompt to do some sql stuff
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
    SqlPrompt(
        "give me the top 10 countries with the highest net increase of population over the past 25 years?",
        dialect="BigQuery",
        evaluators=[lambda x: x.trim().startswith("SELECT")],
    ),
    SimplePrompt(
        "who is Maxime Beauchemin, (the data guy...)?",
        lambda x: evals.percentage_of_words(x, ["airflow", "superset"]),
    ),
]
