"""
This module provides a Suite class to manage and execute a collection of
use cases (prompts) to be tested. It allows running the tests, displaying
results, and serializing the summary of the suite.
"""

from typing import Any, Dict, List, Optional, Union
from promptimize import utils
from promptimize.prompt_cases import BasePromptCase
import click


def separator() -> None:
    """Print a separator line."""
    click.secho("# " + "-" * 40, fg="cyan")


class Suite:
    """A collection of use cases to be tested.

    Attributes:
        completion_create_kwargs (Dict[str, Any]): Keyword arguments for completion creation.
        name (Optional[str]): The name of the suite.
        prompts (Dict[str, Prompt]): Dictionary of prompts to be tested, keyed by the prompt key.
        last_run_completion_create_kwargs (Dict[str, Any]): Keyword arguments used in the last run for completion creation.
    """

    def __init__(
        self,
        prompts: List["BasePromptCase"],
        completion_create_kwargs: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
    ) -> None:
        """
        Args:
            prompts (List[Prompt]): List of prompts to be tested.
            completion_create_kwargs (Optional[Dict[str, Any]]): Keyword arguments for completion creation. Defaults to None.
            name (Optional[str]): The name of the suite. Defaults to None.
        """
        self.completion_create_kwargs = completion_create_kwargs or {}
        self.name = name
        self.prompts = {o.key: o for o in prompts}
        self.last_run_completion_create_kwargs: dict = {}

    def execute(
        self,
        verbose: bool = False,
        style: str = "yaml",
        completion_create_kwargs: Optional[Dict[str, Any]] = None,
        silent: bool = False,
    ) -> None:
        """
        Execute the suite with the given settings.

        Args:
            verbose (bool): If True, print verbose output. Defaults to False.
            style (str): Output style for serialization. Defaults to "yaml".
            completion_create_kwargs (Optional[Dict[str, Any]]): Keyword arguments for completion creation. Defaults to None.
            silent (bool): If True, suppress output. Defaults to False.
        """
        completion_create_kwargs = (
            completion_create_kwargs or self.completion_create_kwargs
        )
        for prompt in self.prompts.values():
            if not silent:
                separator()
                click.secho(f"# Prompt {prompt.key}", fg="cyan")
                separator()
            prompt.run(completion_create_kwargs)
            prompt.test()
            if not silent:
                prompt.print(verbose=verbose, style=style)

        self.last_run_completion_create_kwargs = completion_create_kwargs
        if not silent:
            separator()
            click.secho("# Suite summary", fg="cyan")
            separator()
            click.echo(utils.serialize_object(self._serialize_run_summary(), style))

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
        tested = [p for p in prompts if p.was_tested and p.test_results_avg is not None]
        suite_score = None
        if len(tested) > 0:
            total_weight = sum([p.weight for p in tested])
            suite_score = sum([p.test_results_avg for p in tested]) / total_weight
        d = {
            "suite_score": suite_score,
            "completion_create_kwargs": self.last_run_completion_create_kwargs,
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
            "completion_create_kwargs": self.completion_create_kwargs,
            "name": self.name,
            "prompts": {p.key: p.to_dict() for p in self.prompts.values()},
            "run_summary": self._serialize_run_summary(),
        }
