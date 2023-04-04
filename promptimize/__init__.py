from textwrap import dedent

import click

from promptimize.use_case import BaseUseCase
from promptimize.suite import Suite
from promptimize.crawler import discover_objects


@click.command
@click.option(
    "--path",
    required=True,
    help="The folder containing Python code with UseCase instances.",
)
@click.option("--verbose", "-v", is_flag=True, help="Trigger more verbose output")
@click.option(
    "--style",
    "-s",
    type=click.Choice(["json", "yaml"], case_sensitive=False),
    default="yaml",
    help="json or yaml formatting",
)
def cli(path, verbose, style):
    uses_cases = discover_objects(path, BaseUseCase)
    suite = Suite(uses_cases)
    suite.execute(verbose=verbose, style=style)
