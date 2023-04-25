import os
from typing import Any, Callable, List, Optional, Union

from langchain.llms import OpenAI

from box import Box

from promptimize import utils
from promptimize.simple_jinja import process_template


class BasePromptCase:
    """Abstract base prompt case"""

    attributes_used_for_hash = set()
    verbose_attrs = {"prompt"}

    def __init__(
        self,
        evaluators: Optional[Union[Callable, List[Callable]]] = None,
        key: Optional[str] = None,
        weight=1,
        category: str = None,  # used for info/reporting purposes only
        prompt_executor: Any = None,
        prompt_executor_kwargs: dict = None,
        prompt_hash=None,
        *args,
        **kwargs,
    ) -> None:
        """
        Initialize a SimplePromptCase instance.

        Args:
            user_input (str): Raw user_input for the prompt.
            evaluators (Optional[Union[Callable, List[Callable]]]): Optional
                callable or list of callables used for evaluation.
            key (Optional[str]): Optional unique key for the prompt.
            weight (int, optional): Optional weight for the prompt (default: 1).
            category (Optional[str], optional): Optional category for
                the prompt (used for info/reporting purposes only).
        """
        self.extra_args = args
        self.extra_kwargs = kwargs
        self.response = None
        self.has_run = False
        self.was_tested = False
        self.test_results = None
        self.evaluators = evaluators or []
        self.weight = weight or 1
        self.category = category
        self.pre_run_output = None
        self.post_run_output = None
        self.prompt_executor = prompt_executor or self.get_prompt_executor()
        self.prompt_executor_kwargs = prompt_executor_kwargs or {}

        self._prompt_hash = prompt_hash

        self.execution = Box()

        self.prompt = utils.literal_str(self.render()).strip()

        self.key = key or "prompt-" + self.prompt_hash

        if not utils.is_iterable(self.evaluators):
            self.evaluators = [self.evaluators]  # type: ignore

    def get_prompt_executor(self):
        model_name = os.environ.get("OPENAI_MODEL") or "text-davinci-003"
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.prompt_executor_kwargs = {"model_name": model_name}
        return OpenAI(model_name=model_name, openai_api_key=openai_api_key)

    def execute_prompt(self, prompt_str):
        self.response = self.prompt_executor(prompt_str)
        return self.response

    def pre_run(self):
        pass

    def post_run(self):
        pass

    @property
    def hash(self):
        return utils.short_hash(hash(self))

    def __hash__(self):
        attrs = self.attributes_used_for_hash
        s = "|".join([utils.short_hash(utils.hashable_repr(getattr(self, attr))) for attr in attrs])
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
            "prompt_hash": self.prompt_hash,
            "prompt": self.prompt,
            "category": self.category,
            "response": self.response,
            "weight": self.weight,
            "execution": self.execution.to_dict(),
        }
        return d

    def print(self, verbose=False, style="yaml"):
        style = style or "yaml"
        output = self.to_dict(verbose)
        if not verbose:
            for attr in self.verbose_attrs:
                del output[attr]
        if self.weight == 1:
            del output["weight"]
        highlighted = utils.serialize_object(output, style)
        print(highlighted)

    def test(self):
        test_results = []
        for evaluator in self.evaluators:
            result = evaluator(self)
            if not (utils.is_numeric(result) and 0 <= result <= 1):
                raise Exception("Value should be between 0 and 1")
            test_results.append(result)

        if len(test_results):
            self.execution.score = sum(test_results) / len(test_results)
        self.was_tested = True

    @property
    def prompt_hash(self):
        if self._prompt_hash:
            return self._prompt_hash
        return utils.short_hash(hash(self))

    def _run(self, dry_run):
        pre_run_output = self.pre_run()
        if pre_run_output:
            self.execution.pre_run_output = pre_run_output

        if not dry_run:
            with utils.MeasureDuration() as md:
                self.response = self.execute_prompt(self.prompt).strip()

            self.execution.api_call_duration_ms = md.duration

            post_run_output = self.post_run()
            if post_run_output:
                self.execution.post_run_output = post_run_output
            self.has_run = True
            self.execution.run_at = utils.current_iso_timestamp()
            return self.response


class PromptCase(BasePromptCase):
    """A simple prompt case"""

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
    template = "{{ user_input }}"

    def __init__(
        self,
        user_input=None,
        *args,
        **kwargs,
    ) -> None:
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
        context_kwargs.update({"user_input": self.user_input})
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
