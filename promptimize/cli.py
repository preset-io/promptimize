import click

from promptimize.crawler import discover_objects
from promptimize.prompt_cases import BasePromptCase
from promptimize.reports import Report
from promptimize.suite import Suite


@click.group(help="💡¡promptimize!💡 CLI. `p9e` works too!")
def cli():
    pass


@click.command(help="run some prompts")
@click.argument(
    "path",
    required=True,
    type=click.Path(exists=True),
)
@click.option("--verbose", "-v", is_flag=True, help="Trigger more verbose output")
@click.option("--force", "-f", is_flag=True, help="Force run, do not skip")
@click.option(
    "--human",
    "-h",
    is_flag=True,
    help="Human review, allowing a human to review and force pass/fail each prompt case",
)
@click.option("--repair", "-r", is_flag=True, help="Only re-run previously failed")
@click.option("--dry-run", "-x", is_flag=True, help="DRY run, don't call the API")
@click.option("--shuffle", is_flag=True, help="Shuffle the prompts in a random order")
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
    "--limit",
    "-l",
    type=click.INT,
    default=0,
    help="limit how many prompt cases to run in a single batch",
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
@click.option("--key", "-k", multiple=True, help="The keys to run")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
)
@click.option("--silent", "-s", is_flag=True)
def run(
    path,
    verbose,
    force,
    dry_run,
    style,
    temperature,
    max_tokens,
    engine,
    key,
    output,
    silent,
    repair,
    human,
    shuffle,
    limit,
):
    """Run some prompts/suites!"""
    click.secho("💡 ¡promptimize! 💡", fg="cyan")
    if dry_run:
        click.secho("# DRY RUN MODE ACTIVATED!", fg="red")
    uses_cases = discover_objects(path, BasePromptCase)
    completion_create_kwargs = {
        "engine": engine,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    report = None
    if output:
        report = Report.from_path(output)

    suite = Suite(uses_cases, completion_create_kwargs)
    suite.execute(
        verbose=verbose,
        style=style,
        silent=silent,
        report=report,
        dry_run=dry_run,
        keys=key,
        force=force,
        repair=repair,
        human=human,
        shuffle=shuffle,
        limit=limit,
    )

    if output:
        output_report = Report.from_suite(suite)
        if report:
            output_report.merge(report)
        click.secho(f"# Writing file output to {output}", fg="yellow")
        output_report.write(output, style=style)


cli.add_command(run)


@click.command(help="report on how your suites of prompts are performing")
@click.argument(
    "path",
    required=True,
    type=click.Path(exists=True),
)
@click.option("--groupby", "-g", help="GROUPBY", default="category")
def report(path, groupby):
    """Get some summary of how your prompt suites are performing"""
    click.secho(f"# Reading report @ {path}", fg="yellow")
    report = Report.from_path(path)
    report.print_summary(groupby)


cli.add_command(report)
