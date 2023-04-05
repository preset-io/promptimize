from textwrap import dedent

from promptimize.prompt import SimplePrompt, TemplatedPrompt
from promptimize.suite import Suite


class SqlPrompt(TemplatedPrompt):
    template_defaults = {"dialect": "BigQuery"}
    prompt_template = dedent(
        """\
    given these SQL table schemas:
    ```
        {{ table_schemas }}
    ```
    please answer the following question with SQL:
      * uses lowercase characters for reserve words
      * uses 2 indents, no tabs!
    So, can you write a SQL query for {{ dialect }} that answers this user prompt:
    {{ input }}
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


class SqlJsonPrompt(SqlPrompt):
    response_is_json = True
    prompt_template = dedent(
        """\
    using SQL code, answer the following user question:
    {{input}}


    here's some information about the database schema:


    CREATE TABLE world_population (
        country_name STRING,
        year DATE,
        population_total INT
    );
    your answer should be JSON and only valid JSON, following this format:
    ```json
    {
        "sql": "the SQL you generated",
        "tables": ["the tables you used in the query"]
        "hints": "some hints to the user to improve or clarify their prompt",
    }
    ```

    SQL Formatting rules:
    1. dialect / syntax should be {{ dialect }}
    2. Use lowercase for all SQL reserved words (e.g., 'SELECT' should be 'select').
    3. Indent your SQL using 2 spaces, no tabs.
    4. use fully qualified table and column names

    """
    )
    pass


uses_cases = [
    SqlPrompt(
        "can you tell me the current population of each country?",
        lambda x: "SELECT" in x,
    ),
    SqlPrompt("which country have the fastest growth rate over the past 10 years?"),
    SqlPrompt(
        "which country have the fastest growth rate over the most recent 10 years of available data?"
    ),
    SqlJsonPrompt(
        "give me the top 10 countries with the highest net increase of population over the past 25 years?"
    ),
]
