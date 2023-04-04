from textwrap import dedent
import json

import yaml
from pygments import highlight
from pygments.lexers import YamlLexer, JsonLexer
from pygments.formatters import TerminalFormatter

from promptimize.openai_api import execute_prompt
from promptimize import utils
from promptimize.simple_jinja import process_template


class BaseUseCase:
    """Abstract base class for a use case"""

    def run(self):
        return NotImplementedError

    def test(self):
        return NotImplementedError

    def print(self):
        return NotImplementedError


class SimpleUseCase(BaseUseCase):
    """A generic class where each instance represents a specific use case"""
    response_is_json = False

    def __init__(self, user_input, validators=None):
        self.user_input = user_input
        self.response = None
        self.response_text = None
        self.response_json = None
        self.prompt = None
        self.has_run = False
        self.was_tested = False
        self.test_results = None

        self.validators = validators or []
        if not utils.is_iterable(self.validators):
            self.validators = [self.validators]

    def test(self):
        for validator in self.validators:
            self.test_results = validator(self.response_text)

        self.was_tested = True

    def _serialize_for_print(self, verbose=False):
        d = {
            "user_input": self.user_input,
        }
        if self.response_json:
            d.update({
                "response_json": self.response_json,
            })
        else:
            d.update({
                "response_text": self.response_text,
            })

        if verbose:
            d.update({
                "response": self.response,
                "prompt": self.prompt,
            })
        if self.was_tested:
            d.update({
                "test_results": self.test_results,
            })
        return d

    def print(self, verbose=False, style="yaml"):
        style = style or "yaml"
        output = self._serialize_for_print(verbose)
        highlighted = None
        if style == "yaml":
            data = yaml.dump(output, Dumper=utils.CustomDumper)
            highlighted = highlight(data, YamlLexer(), TerminalFormatter())
            highlighted = data
        elif style == "json":
            data = json.dumps(output, indent=2)
            highlighted = highlight(data, JsonLexer(), TerminalFormatter())
        print("-" * 80)
        print(highlighted)

    def _generate_prompt(self):
        return self.user_input

    def run(self):
        self.prompt = self._generate_prompt()
        self.response = execute_prompt(self.prompt)
        self.response_text = self.response.choices[0].text.strip()
        if self.response_is_json:
            self.response_json = utils.try_to_json_parse(self.response.choices[0].text)
        self.has_run = True


##########################################################################
class JsonUseCase(SimpleUseCase):

    def _generate_prompt(self):
        return json.dumps({
            "user_input": self.user_input,
        })



class TemplatedUseCase(SimpleUseCase):
    template_defaults = {}
    prompt_template = "{{ user_input }}"

    def __init__(self, user_input, validators=None, **template_kwargs):
        self.template_kwargs = template_kwargs
        return super().__init__(user_input)

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
            self.prompt_template, user_input=self.user_input, **context_kwargs
        )

    def _generate_prompt(self, **kwargs):
        return self._process_template()


