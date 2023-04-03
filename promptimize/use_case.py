from textwrap import dedent

from promptimize.openai_api import execute_prompt
from promptimize.utils import is_iterable
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

    def __init__(self, user_input, validators=None):
        self.user_input = user_input
        self.response = None
        self.response_text = None
        self.prompt = None
        self.has_run = False
        self.was_tested = False
        self.test_results = None

        self.validators = validators or []
        if not is_iterable(self.validators):
            self.validators = [self.validators]

    def test(self):
        for validator in self.validators:
            self.test_results = validator(self.response_text)
            if not self.test_results:
                print("FAILED!")

        self.was_tested = True

    def print(self, verbose=False):
        if verbose:
            print("=" * 80)
            print(self.prompt)
            print("-" * 80)
            print(self.response)
            print("-" * 80)
        else:
            print("=" * 80)
            print(self.user_input)
            print("-" * 80)
            print(self.response_text)
        if self.was_tested:
            if not self.test_results:
                print("TEST: SUCCESS")
            else:
                print("TEST: FAILED!")
                print(self.test_results)
        print("." * 80)

    def _generate_prompt(self):
        return self.user_input

    def run(self):
        self.prompt = self._generate_prompt()
        self.response = execute_prompt(self.prompt)
        self.response_text = self.response.choices[0].text.strip()
        self.has_run = True


##########################################################################
class TemplatedUseCase(SimpleUseCase):
    template_defaults = {}
    prompt_template = "{{ user_input }}"

    def __init__(self, user_input, **template_kwargs):
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


class SqlUseCase(TemplatedUseCase):
    template_defaults = {"dialect": "BigQuery"}
    prompt_template = dedent(
        """\
    given the following set of table schemas:
    ```
        {{ table_schemas }}
    ```
    can you write a SQL query for {{ dialect }} that answers:
    {{ user_input }}
    """
    )

    def get_table_schemas(self):
        return dedent(
            """\
        CREATE TABLE world_population (
            country_name STRING,
            year DATE,
            population_total INT,
        );"""
        )

    def get_extra_template_context(self):
        return {"table_schemas": self.get_table_schemas()}
