"""
This module provides a Suite class to manage and execute a collection of
use cases (prompts) to be tested. It allows running the tests, displaying
results, and serializing the summary of the suite.
"""
import random
from typing import Any, Dict, List, Optional, Union

import click

from promptimize import utils
from promptimize.prompt_cases import BasePromptCase


def separator(fg=None) -> None:
    """Print a separator line."""
    click.secho("# " + "-" * 40, fg=fg)


def separated_section(s, fg=None):
    separator(fg)
    click.secho(s, fg=fg)
    separator(fg)


class Suite:
    """A collection of use cases to be tested.

    Attributes:
        name (Optional[str]): The name of the suite.
        prompts (Dict[str, Prompt]): Dictionary of prompts to be tested,
            keyed by the prompt key.
        last_run_completion_create_kwargs (Dict[str, Any]): Keyword arguments
            used in the last run for completion creation.
    """

    def __init__(
        self,
        prompts: List["BasePromptCase"],
        name: Optional[str] = None,
    ) -> None:
        """
        Args:
            prompts (List[Prompt]): List of prompts to be tested.
            name (Optional[str]): The name of the suite. Defaults to None.
        """
        self.name = name
        self.prompts = {o.key: o for o in prompts}
        self.last_run_completion_create_kwargs: dict = {}

    def execute(  # noqa
        self,
        verbose: bool = False,
        style: str = "yaml",
        silent: bool = False,
        report=None,
        dry_run: bool = False,
        keys: list = None,
        force: bool = False,
        repair: bool = False,
        human: bool = False,
        shuffle: bool = False,
        limit: int = 0,
    ) -> None:
        """
        Execute the suite with the given settings.

        Args:
            verbose (bool): If True, print verbose output. Defaults to False.
            style (str): Output style for serialization. Defaults to "yaml".
            silent (bool): If True, suppress output. Defaults to False.
        """
        prompts = list(self.prompts.values())
        if keys:
            prompts = [p for p in prompts if p.key in keys]
        if repair and report:
            failed_keys = report.failed_keys
            prompts = [p for p in prompts if p.key in failed_keys]

        if shuffle:
            random.shuffle(prompts)

        if limit:
            prompts = prompts[:limit]

        for i, prompt in enumerate(prompts):
            should_run = force or self.should_prompt_execute(prompt, report)
            progress = f"({i+1}/{len(prompts)})"
            if not silent:
                if should_run:
                    separated_section(f"# {progress} [RUN] prompt: {prompt.key}", fg="cyan")
                else:
                    separated_section(f"# {progress} [SKIP] prompt: {prompt.key}", fg="yellow")

            if should_run:
                prompt._run(dry_run)
                if not dry_run:
                    prompt.test()

            if not silent and should_run:
                prompt.print(verbose=verbose, style=style)

            if should_run and human:
                v = click.prompt(
                    'Press Enter to continue, "Y" to force success, "N" to force fail, "X" to exit',
                    default="",
                    show_default=False,
                )
                v = v.lower()
                if v == "":
                    click.secho("Leaving result unaltered", fg="yellow")
                elif v == "y":
                    prompt.execution.score = 1
                    prompt.execution.human_override = True
                    click.secho("Forcing SUCCESS", fg="green")
                elif v == "n":
                    prompt.execution.score = 0
                    prompt.execution.human_override = True
                    click.secho("Forcing FAILURE", fg="red")
                elif v == "x":
                    break

        # `self.last_run_completion_create_kwargs = completion_create_kwargs
        if not silent:
            separated_section("# Suite summary", fg="cyan")
            click.echo(utils.serialize_object(self._serialize_run_summary(), style))

    def should_prompt_execute(self, prompt, report):
        if not report or not report.prompts:
            return True
        report_prompt = report.prompts.get(prompt.key)
        if not report_prompt:
            return True
        else:
            if not report_prompt.execution:
                return True

        if report_prompt.prompt_hash == prompt.prompt_hash:
            return False

        return True

    def _serialize_run_summary(
        self, verbose: bool = False
    ) -> Dict[str, Union[Optional[float], Dict[str, Any]]]:
        """
        Serialize the run summary of the suite.

        Args:
            verbose (bool): If True, include verbose output. Defaults to False.

        Returns:
            Dict[str, Union[Optional[float], Dict[str, Any]]]: Serialized run summary of the suite.
        """
        prompts = self.prompts.values()
        tested = [p for p in prompts if p.was_tested and p.execution.score is not None]
        suite_score = None
        if len(tested) > 0:
            total_weight = sum([p.weight for p in tested])
            suite_score = sum([p.execution.score for p in tested]) / total_weight
        d = {
            "suite_score": suite_score,
            "git_info": utils.get_git_info(),
        }

        return d

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the suite to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the suite.
        """
        return {
            "name": self.name,
            "prompts": {p.key: p.to_dict() for p in self.prompts.values()},
            "run_summary": self._serialize_run_summary(),
        }
