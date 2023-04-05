from textwrap import dedent

import click

from promptimize.use_case import BaseUseCase
from promptimize.suite import Suite
from promptimize.crawler import discover_objects


@click.command(help="The `promptimize` CLI. `p9e` works too! ")
@click.argument(
    "path",
    required=True,
    type=click.Path(exists=True),
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
