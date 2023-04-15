import os
from textwrap import dedent
from typing import Any, Callable, Dict, List, Optional, Union

from langchain.llms import OpenAI

from promptimize import utils
from promptimize.simple_jinja import process_template


class BasePromptCase:
    attributes_used_for_hash = {"evaluators"}

    def __init__(
        self,
        evaluators: Optional[Union[Callable, List[Callable]]] = None,
        key: Optional[str] = None,
        weight=1,
        category: str = None,  # used for info/reporting purposes only
        prompt_executor: Any = None,
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
        self.prompt_executor = prompt_executor or self.get_prompt_executor()

        self.key = key or "prompt-" + utils.short_hash(hash(self))

        if not utils.is_iterable(self.evaluators):
            self.evaluators = [self.evaluators]  # type: ignore

    def get_prompt_executor(self):
        model_name = os.environ.get("OPENAI_MODEL") or "text-davinci-003"
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        return OpenAI(model_name=model_name, openai_api_key=openai_api_key)

    def execute_prompt(self, prompt_str):
        self.response = self.prompt_executor(prompt_str)
        return self.response

    def pre_run(self):
        pass

    def post_run(self):
        pass

    def __hash__(self):
        attrs = self.attributes_used_for_hash
        s = "|".join([utils.hashable_repr(getattr(self, attr)) for attr in attrs])
        return utils.int_hash(s)

    def render(self):
        raise NotImplementedError()

    def get_unique_hash(self, extra_context=None):
        """Returns a unique identifier, determined by the run

        Generally, the actual call sent to GPT (prompt, execution params)
        represent something unique.
        """
        return utils.short_hash(str(self.extra_kwargs))

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

        d.update(
            {
                "api_call_duration_ms": self.api_call_duration_ms,
                "run_at": self.run_at,
            }
        )
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

    def _run(self, completion_create_kwargs=None):
        completion_create_kwargs = completion_create_kwargs or {}
        self.pre_run_output = self.pre_run()
        self.prompt = self.render()

        with utils.MeasureDuration() as md:
            self.raw_response_text = self.execute_prompt(self.prompt)

        self.api_call_duration_ms = md.duration
        self.response_text = self.raw_response_text.strip("\n")

        self.post_run_output = self.post_run()
        self.has_run = True
        self.run_at = utils.current_iso_timestamp()
        return self.response_text


class PromptCase(BasePromptCase):
    attributes_used_for_hash = BasePromptCase.attributes_used_for_hash | {"user_input"}

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
    attributes_used_for_hash = BasePromptCase.attributes_used_for_hash | {
        "user_input",
        "extra_kwargs",
    }

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


class LangchainPromptCase(BasePromptCase):
    attributes_used_for_hash = BasePromptCase.attributes_used_for_hash | {
        "extra_kwargs",
        "langchain_prompt",
    }

    def __init__(
        self,
        langchain_prompt,
        *args,
        **kwargs,
    ) -> None:
        self.langchain_prompt = langchain_prompt
        return super().__init__(*args, **kwargs)

    def to_dict(self, verbose=False, *args, **kwargs):
        d = super().to_dict(*args, **kwargs)
        d = utils.insert_in_dict(d, "prompt_kwargs", self.extra_kwargs, after_key="key")
        return d

    def render(self):
        return self.langchain_prompt.format(**self.extra_kwargs)
