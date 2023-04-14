from textwrap import dedent
from typing import Any, Callable, Dict, List, Optional, Union

from promptimize.openai_api import execute_prompt
from promptimize import utils
from promptimize.simple_jinja import process_template


class BasePromptCase:
    parent_class_kwargs = ("evaluators", "key", "weight", "category")

    def __init__(
        self,
        evaluators: Optional[Union[Callable, List[Callable]]] = None,
        key: Optional[str] = None,
        weight=1,
        category: str = None,  # used for info/reporting purposes only
        *args,
        **kwargs,
    ) -> None:
        """
        Initialize a SimplePromptCase instance.

        Args:
            user_input (str): Raw user_input for the prompt.
            evaluators (Optional[Union[Callable, List[Callable]]]): Optional callable or list of callables used for evaluation.
            key (Optional[str]): Optional unique key for the prompt.
            weight (int, optional): Optional weight for the prompt (default: 1).
            category (Optional[str], optional): Optional category for the prompt (used for info/reporting purposes only).
        """
        self.extra_args = args
        self.extra_kwargs = kwargs
        self.response = None
        self.response_text = None
        self.prompt = None
        self.has_run = False
        self.was_tested = False
        self.test_results = None
        self.evaluators = evaluators or []
        self.weight = weight or 1
        self.category = category
        self.pre_run_output = None
        self.post_run_output = None

        self.key = key or "prompt-" + self.make_a_key()

        if not utils.is_iterable(self.evaluators):
            self.evaluators = [self.evaluators]  # type: ignore

    def pre_run(self):
        pass

    def post_run(self):
        pass

    def make_a_key(self):
        return utils.short_hash(str(self.extra_kwargs))

    def render(self):
        raise NotImplementedError()

    def to_dict(self, verbose=False):
        d = {
            "key": self.key,
            "response_text": self.response_text,
        }
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
        if self.weight != 1:
            d.update(
                {
                    "weight": self.weight,
                }
            )
        if self.post_run_output:
            d["post_run_output"] = self.post_run_output

        if self.pre_run_output:
            d["pre_run_output"] = self.pre_run_output

        d.update({"api_call_duration_ms": self.api_call_duration_ms})
        return d

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

    def print(self, verbose=False, style="yaml"):
        style = style or "yaml"
        output = self.to_dict(verbose)
        highlighted = utils.serialize_object(output, style)
        print(highlighted)

    def run(self, completion_create_kwargs=None):
        completion_create_kwargs = completion_create_kwargs or {}
        self.pre_run_output = self.pre_run()
        answer = None
        self.prompt = self.render()
        with utils.MeasureDuration() as md:
            self.response = execute_prompt(self.prompt, completion_create_kwargs)
        self.api_call_duration_ms = md.duration
        self.raw_response_text = self.response.choices[0].text
        self.response_text = self.raw_response_text.strip("\n")
        answer = self.response_text

        self.post_run_output = self.post_run()
        self.has_run = True
        self.answer = answer
        return answer


class PromptCase(BasePromptCase):
    def __init__(
        self,
        user_input,
        *args,
        **kwargs,
    ) -> None:
        self.user_input = user_input
        super().__init__(*args, **kwargs)

    def to_dict(self, verbose=False, *args, **kwargs):
        d = super().to_dict(*args, **kwargs)
        d = utils.insert_in_dict(d, "user_input", self.user_input, after_key="key")
        return d

    def render(self):
        return self.user_input


class TemplatedPromptCase(BasePromptCase):
    template_defaults: dict = {}

    def __init__(
        self,
        template,
        user_input=None,
        *args,
        **kwargs,
    ) -> None:
        self.template = template
        self.user_input = user_input
        return super().__init__(*args, **kwargs)

    def to_dict(self, verbose=False, *args, **kwargs):
        d = super().to_dict(*args, **kwargs)
        d = utils.insert_in_dict(d, "user_input", self.user_input, after_key="key")
        return d

    def get_extra_template_context(self):
        """meant to be overriden in derived classes to add logic/context"""
        return {}

    @property
    def jinja_context(self):
        context_kwargs = self.template_defaults.copy()
        context_kwargs.update(self.get_extra_template_context())
        context_kwargs.update(self.extra_kwargs)
        return context_kwargs

    def render(self, **kwargs):
        return process_template(self.template, **self.jinja_context)


class LangchainPromptCase(PromptCase):
    def __init__(
        self,
        langchain_prompt,
        *args,
        **kwargs,
    ) -> None:
        self.template = template
        return super().__init__(*args, **kwargs)

    def render(self):
        return langchain_prompt.render(**self.extra_kwargs)
