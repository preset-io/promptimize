from textwrap import dedent

from promptimize.openai_api import execute_prompt
from promptimize import utils
from promptimize.simple_jinja import process_template


class BasePrompt:
    """Abstract base class for a use case"""

    def run(self):
        return NotImplementedError

    def test(self):
        return NotImplementedError

    def print(self):
        return NotImplementedError


class SimplePrompt(BasePrompt):
    """A generic class where each instance represents a specific use case"""

    response_is_json = False

    def __init__(self, input, evaluators=None, key=None):
        self.key = key or utils.short_hash(input)
        self.input = input
        self.response = None
        self.response_text = None
        self.response_json = None
        self.prompt = None
        self.has_run = False
        self.was_tested = False
        self.test_results = None

        self.evaluators = evaluators or []
        if not utils.is_iterable(self.evaluators):
            self.evaluators = [self.evaluators]

    def test(self):
        test_results = []
        for evaluator in self.evaluators:
            result = evaluator(self.response_text)
            if not (utils.is_numeric(result) and 0 <= result <= 1):
                raise Exception("Value should be between 0 and 1")
            test_results.append(result)

        self.test_results = test_results
        self.test_results_avg = sum(self.test_results) / len(self.test_results)
        self.was_tested = True

    def _serialize_for_print(self, verbose=False):
        d = {
            "key": self.key,
            "input": self.input,
        }
        if self.response_json:
            d.update(
                {
                    "response_json": self.response_json,
                }
            )
        else:
            d.update(
                {
                    "response_text": self.response_text,
                }
            )

        if verbose:
            d.update(
                {
                    "response": self.response,
                    "prompt": self.prompt,
                }
            )
        if self.was_tested:
            d.update(
                {
                    "test_results_avg": self.test_results_avg,
                    "test_results": self.test_results,
                }
            )
        return d

    def print(self, verbose=False, style="yaml"):
        style = style or "yaml"
        output = self._serialize_for_print(verbose)
        highlighted = None
        if style == "yaml":
            highlighted = utils.to_yaml(data)
        elif style == "json":
            highlighted = utils.to_json(data)
        print("-" * 80)
        print(highlighted)

    def _generate_prompt(self):
        return self.input

    def run(self, model_id="text-davinci-003", max_tokens=1000):
        self.prompt = self._generate_prompt()
        self.response = execute_prompt(
            self.prompt, model_id=model_id, max_tokens=max_tokens
        )
        self.raw_response_text = self.response.choices[0].text
        self.response_text = self.raw_response_text.strip("\n")
        if self.response_is_json:
            self.response_json = utils.try_to_json_parse(self.response.choices[0].text)
        self.has_run = True


class TemplatedPrompt(SimplePrompt):
    template_defaults = {}
    prompt_template = "{{ input }}"

    def __init__(self, input, evaluators=None, **template_kwargs):
        self.template_kwargs = template_kwargs
        return super().__init__(input)

    def get_extra_template_context(self):
        return {}

    def test(self):
        if self.response_text != "" and self.response_text is not None:
            return True

    def _process_template(self):
        context_kwargs = self.template_defaults.copy()
        context_kwargs.update(self.get_extra_template_context())
        context_kwargs.update(self.template_kwargs)
        return process_template(
            self.prompt_template, input=self.input, **context_kwargs
        )

    def _generate_prompt(self, **kwargs):
        return self._process_template()
