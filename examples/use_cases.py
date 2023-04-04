from textwrap import dedent

from promptimize.use_case import SimpleUseCase, TemplatedUseCase
from promptimize.suite import Suite

class SqlUseCase(TemplatedUseCase):
    template_defaults = {"dialect": "BigQuery"}
    prompt_template = dedent("""\
    given these SQL table schemas:
    ```
        {{ table_schemas }}
    ```
    please answer the following question with SQL:
      * uses lowercase characters for reserve words
      * uses 2 indents, no tabs!
    So, can you write a SQL query for {{ dialect }} that answers this user prompt:
    {{ user_input }}
    """
    )

    def get_table_schemas(self):
        return dedent(
            """\
        CREATE TABLE world_population (
            country_name STRING,
            year DATE,
            population_total INT,
        );"""
        )

    def get_extra_template_context(self):
        return {"table_schemas": self.get_table_schemas()}

class SqlUseCase2(SqlUseCase):
    response_is_json = True
    prompt_template = dedent("""\
    using SQL code, answer the following user question:
    {{user_input}}


    here's some information about the database schema:


    CREATE TABLE world_population (
            country_name STRING,
                year DATE,
                    population_total INT
                    );

    SQL Formatting rules:
    1. dialect / syntax should be {{ dialect }}
    2. Use lowercase for all SQL reserved words (e.g., 'SELECT' should be 'select').
    3. Indent your SQL using 2 spaces, no tabs.
    4. use fully qualified table and column names

    please provide your answer in a pure JSON blob (no other output please!) with the following keys:
        "sql": the SQL you generated,
        "hints": some hints as to how to improve the user prompt for better results

    """)
    pass

uses_cases = [
    SimpleUseCase("hello there!", lambda x: "hi" in x.lower()),
    #SqlUseCase("can you tell me the current population of each country?", lambda x: 'SELECT' in x),
    #SqlUseCase("which country have the fastest growth rate over the past 10 years?"),
    #SqlUseCase(
    #    "which country have the fastest growth rate over the most recent 10 years of available data?"
    #),
    SqlUseCase2(
        "give me the top 10 countries with the highest net increase of population over the past 25 years?"
    ),
]
