from textwrap import dedent

import click

from promptimize.use_case import SimpleUseCase, SqlUseCase
from promptimize.suite import Suite


uses_cases = [
    SimpleUseCase("hello there!", lambda x: "hi" in x.lower()),
    SqlUseCase("can you tell me the current population of each country?"),
    SqlUseCase("which country have the fastest growth rate over the past 10 years?"),
    SqlUseCase(
        "which country have the fastest growth rate over the most recent 10 years of available data?"
    ),
    SqlUseCase(
        "give me the top 10 countries with the highest net increase of population over the past 25 years?"
    ),
]

@click.command
@click.option('--folder', prompt='Folder with Python code', help='The folder containing Python code with CustomObject instances.')
def cli():
    suite = Suite(uses_cases)
    suite.execute(verbose=False)


