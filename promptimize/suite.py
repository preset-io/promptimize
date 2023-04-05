class Suite:
    """a collection of use cases to be tested"""

    def __init__(self, prompts, model_id="text-davinci-003", max_tokens=1000):
        self.prompts = {o.key: o for o in prompts}
        self.model_id = model_id
        self.max_tokens = max_tokens

    def execute(self, verbose, style, model_id=None, max_tokens=None):
        model_id = model_id or self.model_id
        max_tokens = max_tokens or self.max_tokens
        for prompt in self.prompts.values():
            prompt.run(model_id=model_id, max_tokens=max_tokens)
            prompt.test()
            prompt.print(verbose=verbose, style=style)
        print(self._serialize_run_summary())

    def _serialize_run_summary(self, verbose=False):
        prompts = self.prompts.values()
        suite_score = sum([p.self.test_results_avg for p in prompts]) / len(prompts)
        d = {"suite_score": suite_score}
        return d
