from promptimize import utils


class Suite:
    """a collection of use cases to be tested"""

    def __init__(self, prompts, completion_create_kwargs=None):
        self.completion_create_kwargs = completion_create_kwargs or {}
        self.prompts = {o.key: o for o in prompts}

    def execute(self, verbose=False, style="yaml", completion_create_kwargs=None):
        completion_create_kwargs = (
            completion_create_kwargs or self.completion_create_kwargs
        )
        for prompt in self.prompts.values():
            prompt.run(completion_create_kwargs)
            prompt.test()
            prompt.print(verbose=verbose, style=style)
            print("#" + "-" * 40)
        print(utils.serialize_object(self._serialize_run_summary(), style))

    def _serialize_run_summary(self, verbose=False):
        prompts = self.prompts.values()
        tested = [p for p in prompts if p.was_tested]
        suite_score = None
        if len(tested) > 0:
            suite_score = sum([p.test_results_avg for p in tested]) / len(tested)
        d = {"suite_score": suite_score}
        return d
