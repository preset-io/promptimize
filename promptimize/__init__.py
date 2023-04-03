from textwrap import dedent

import click

from promptimize.use_case import BaseUseCase
from promptimize.suite import Suite
from promptimize.crawler import discover_objects


@click.command
@click.option('--path', required=True, help='The folder containing Python code with UseCase instances.')
def cli(path):
    uses_cases = discover_objects(path, BaseUseCase)
    suite = Suite(uses_cases)
    suite.execute(verbose=False)


