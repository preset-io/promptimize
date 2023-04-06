from textwrap import dedent
from typing import Any, Callable, Dict, List, Optional, Union

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

    response_is_json: bool = False

    def __init__(
        self,
        input: Optional[str] = None,  # raw input
        evaluators: Optional[Union[Callable, List[Callable]]] = None,
        key: Optional[str] = None,
        system_input: Optional[str] = None,
        user_input: Optional[str] = None,
    ) -> None:
        if input is None and (system_input is None and user_input is None):
            raise Exception("Gotta provide some input here friend")

        self.input = input
        self.system_input = system_input
        self.user_input = user_input
        self.key = key or "prompt-" + utils.short_hash(
            "||".join([str(s) for s in [input, system_input, user_input]])
        )

        self.response = None
        self.response_text = None
        self.response_json = None
        self.prompt = None
        self.has_run = False
        self.was_tested = False
        self.test_results = None
        self.evaluators = evaluators or []

        if not utils.is_iterable(self.evaluators):
            self.evaluators = [self.evaluators]  # type: ignore

    def test(self):
        test_results = []
        for evaluator in self.evaluators:
            result = evaluator(self.response_text)
            if not (utils.is_numeric(result) and 0 <= result <= 1):
                raise Exception("Value should be between 0 and 1")
            test_results.append(result)

        self.test_results = test_results
        self.test_results_avg = None
        if len(self.test_results):
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
                }
            )
        return d

    def print(self, verbose=False, style="yaml"):
        style = style or "yaml"
        output = self._serialize_for_print(verbose)
        highlighted = utils.serialize_object(output, style)
        print(highlighted)

    def _generate_prompt(self):
        prompt = None
        # if the user provided user_input and system_input
        if self.user_input:
            return [
                {
                    "role": "user",
                    "content": self.user_input,
                },
                {
                    "role": "system",
                    "content": self.system_input,
                },
            ]
        # if not just passing the normal input
        return self.input

    def run(self, completion_create_kwargs):
        self.prompt = self._generate_prompt()
        self.response = execute_prompt(self.prompt, completion_create_kwargs)
        self.raw_response_text = self.response.choices[0].text
        self.response_text = self.raw_response_text.strip("\n")
        if self.response_is_json:
            d = utils.extract_json(self.response.choices[0].text)
            if d:
                self.response_json = d
        self.has_run = True


class TemplatedPrompt(SimplePrompt):
    template_defaults: dict = {}

    def __init__(
        self,
        input: Optional[str] = None,  # raw input
        evaluators: Optional[Union[Callable, List[Callable]]] = None,
        key: Optional[str] = None,
        system_input: Optional[str] = None,
        user_input: Optional[str] = None,
        **template_kwargs
    ) -> None:
        self.template_kwargs = template_kwargs
        return super().__init__(
            input=input,
            evaluators=evaluators,
            key=key,
            system_input=system_input,
            user_input=user_input,
        )

    def get_extra_template_context(self):
        """meant to be overriden in derived classes to add logic/context"""
        return {}

    @property
    def jinja_context(self):
        context_kwargs = self.template_defaults.copy()
        context_kwargs.update(self.get_extra_template_context())
        context_kwargs.update(self.template_kwargs)
        return context_kwargs

    def _generate_prompt(self, **kwargs):
        prompt = super()._generate_prompt()
        f = lambda x: process_template(x, input=self.input, **self.jinja_context)
        return utils.transform_strings(prompt, f)
