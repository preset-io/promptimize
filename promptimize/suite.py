from promptimize import utils

import click


def separator():
    click.secho("# " + "-" * 40, fg="cyan")


class Suite:
    """a collection of use cases to be tested"""

    def __init__(self, prompts, completion_create_kwargs=None, name=None):
        self.completion_create_kwargs = completion_create_kwargs or {}
        self.name = name
        self.prompts = {o.key: o for o in prompts}
        self.last_run_completion_create_kwargs = {}

    def execute(
        self, verbose=False, style="yaml", completion_create_kwargs=None, silent=False
    ):
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

    def _serialize_run_summary(self, verbose=False):
        prompts = self.prompts.values()
        tested = [p for p in prompts if p.was_tested and p.test_results_avg is not None]
        suite_score = None
        if len(tested) > 0:
            total_weight = sum([p.weight for p in tested])
            suite_score = sum([p.test_results_avg for p in tested]) / total_weight
        d = {
            "suite_score": suite_score,
            "completion_create_kwargs": self.last_run_completion_create_kwargs,
        }

        return d

    def to_dict(self):
        return {
            "completion_create_kwargs": self.completion_create_kwargs,
            "name": self.name,
            "prompts": {p.key: p.to_dict() for p in self.prompts.values()},
        }
