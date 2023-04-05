from textwrap import dedent

import click

from promptimize.prompt import BasePrompt
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
@click.option(
    "--max-tokens", "-t", type=click.INT, help="max_tokens passed to the model"
)
@click.option(
    "--model-id", "-m", type=click.STRING, help="model_id as accepted by the openai API"
)
def cli(path, verbose, style, max_tokens, model_id):
    uses_cases = discover_objects(path, BasePrompt)
    suite = Suite(uses_cases)
    suite.execute(verbose=verbose, style=style)
