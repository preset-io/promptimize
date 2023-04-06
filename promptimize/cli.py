from textwrap import dedent

import click

from promptimize.prompt import BasePrompt
from promptimize.suite import Suite
from promptimize.crawler import discover_objects


@click.command(help="💡¡promptimize!💡 CLI. `p9e` works too! ")
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
    "--max-tokens",
    "-m",
    type=click.INT,
    default=1000,
    help="max_tokens passed to the model",
)
@click.option(
    "--temperature",
    "-t",
    type=click.FLOAT,
    default=0.5,
    help="max_tokens passed to the model",
)
@click.option(
    "--engine",
    "-e",
    type=click.STRING,
    default="text-davinci-003",
    help="model as accepted by the openai API",
)
def cli(path, verbose, style, temperature, max_tokens, engine):
    click.secho("💡 ¡promptimize! 💡", fg="cyan")
    uses_cases = discover_objects(path, BasePrompt)
    completion_create_kwargs = {
        "engine": engine,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    suite = Suite(uses_cases, completion_create_kwargs)
    suite.execute(verbose=verbose, style=style)
