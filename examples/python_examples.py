"""An example of how to test Python code generating prompts"""
import re

# Brining some "prompt generator" classes
from promptimize.prompt_cases import LangchainPromptCase

# Bringing some useful eval function that help evaluating and scoring responses
# eval functions have a handle on the prompt object and are expected
# to return a score between 0 and 1
from langchain import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import demjson

from RestrictedPython import compile_restricted, safe_globals, safe_builtins
from RestrictedPython.Guards import guarded_unpack_sequence
from RestrictedPython.Eval import default_guarded_getiter


response_schemas = [
    ResponseSchema(
        name="python_function",
        description="the python function itself",
    ),
    ResponseSchema(
        name="functon_name",
        description="the name of the function",
    ),
    ResponseSchema(name="test_cases", description="test cases"),
    ResponseSchema(
        name="hints",
        description="if any, any recommendations to the users about clarifying their prompt",
    ),
]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = output_parser.get_format_instructions().replace("\t", "  ")
"""
* you include great useful docstrings and doctests that follow the Google conventions
"""

template = """\
System: you are an AI that writes python function that accomplish specific tasks

Python guidelines:
* you follow the PEP8 conventions
* use 4 spaces indent, no tabs!
* use snake case (using underscores)

The output should be a VALID JSON blob with the following keys:
* "python_function" as a string with the python function code
* "function_name" as the name of the function
* "hints": as some hints about how to use the function

User: write a function that multipllies a number by 2 and returns the result

System:
{
    "python_function": "def multiply_by_two(number):\\n    return number * 2\\n"
	"function_name": "multiply_by_two",
	"hints": "This function is not that helpful as you can simply mulitply by two\\ninstead of calling this function"
}

User: {{ user_input }}

System:
"""  # noqa

lc_template = PromptTemplate(
    input_variables=["user_input"],
    partial_variables={"format_instructions": format_instructions},
    template=template,
    template_format="jinja2",
)


def function_from_string(function_as_string, function_name):
    restricted_code = compile_restricted(function_as_string, "<inline code>", "exec")

    # Define a separate environment for the code to run in
    execution_globals = safe_globals.copy()
    execution_globals.update(
        {
            "__builtins__": safe_builtins,
            "_unpack_sequence_": guarded_unpack_sequence,
            "_getiter_": default_guarded_getiter,
        }
    )

    # Execute the code in the restricted environment
    exec(restricted_code, execution_globals)

    # Access the function from the restricted environment
    return execution_globals[function_name]


def test(func, args, expected_result):
    if func:
        if not isinstance(args, (list, tuple)):
            args = [args]
        try:
            result = func(*args)
            if expected_result == result:
                return 1
        except Exception:
            return 0
    return 0


def decode_shitty_json(s):
    json_match = re.search(r"\{[\s\S]*\}", s)

    if json_match:
        json_string = json_match.group()

        # Parse the JSON string using demjson
        json_data = demjson.decode(json_string)

        return json_data
    return None


def test_is_prime(prompt_case, val, exp):
    return test(prompt_case.python_function, val, exp)


class PythonGeneratorPrompt(LangchainPromptCase):
    def post_run(self):
        success = False
        self.python_function = None
        self.f = None
        try:
            self.response = decode_shitty_json(self.response)
            success = True
        except Exception as e:
            self.error = str(e)

        if success:
            # try:
            f = function_from_string(
                self.response.get("python_function"), self.response.get("function_name")
            )
            self.python_function = f
            self.f = f
            # except Exception as e:
            # self.error = str(e)


prompts = [
    PythonGeneratorPrompt(
        lc_template,
        key="is_prime",
        user_input="write a function that tests if an number is a prime number, returns a boolean",
        evaluators=[
            lambda x: test(x.f, 2, True),
            lambda x: test(x.f, 4, False),
            lambda x: test(x.f, 7, True),
            lambda x: test(x.f, 10, False),
            lambda x: test(x.f, 11, True),
            lambda x: test(x.f, 113, True),
        ],
    ),
    PythonGeneratorPrompt(
        lc_template,
        key="gcd",
        user_input="write a function that finds the greatest common divisor (GCD) of two numbers?",
        evaluators=[
            lambda x: test(x.f, [14, 28], 14),
            lambda x: test(x.f, [56, 98], 14),
            lambda x: test(x.f, [81, 153], 9),
        ],
    ),
    PythonGeneratorPrompt(
        lc_template,
        key="factorial",
        user_input="write a function that calculates the factorial of a given number",
        evaluators=[
            lambda x: test(x.f, 0, 1),
            lambda x: test(x.f, 1, 1),
            lambda x: test(x.f, 5, 120),
            lambda x: test(x.f, 7, 5040),
            lambda x: test(x.f, 10, 3628800),
        ],
    ),
    PythonGeneratorPrompt(
        lc_template,
        key="is_palindrome",
        user_input="write a function that determines if a given string is a palindrome",
        evaluators=[
            lambda x: test(x.f, "racecar", True),
            lambda x: test(x.f, "hello", False),
            lambda x: test(x.f, "madam", True),
            lambda x: test(x.f, "python", False),
            lambda x: test(x.f, "Aibohphobia", True),
        ],
    ),
    PythonGeneratorPrompt(
        lc_template,
        key="fibonacci",
        user_input=(
            "write a function that generates the Fibonacci sequence ",
            "up to a specified number of terms",
        ),
        evaluators=[
            lambda x: test(x.f, 1, [0]),
            lambda x: test(x.f, 2, [0, 1]),
            lambda x: test(x.f, 5, [0, 1, 1, 2, 3]),
            lambda x: test(x.f, 10, [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]),
            lambda x: test(x.f, 7, [0, 1, 1, 2, 3, 5, 8]),
        ],
    ),
    PythonGeneratorPrompt(
        lc_template,
        key="sum_of_multiples",
        user_input=(
            "write a function that calculates the sum of all multiples ",
            "of 3 and 5 below a given number",
        ),
        evaluators=[
            lambda x: test(x.f, 10, 23),
            lambda x: test(x.f, 20, 78),
            lambda x: test(x.f, 30, 195),
            lambda x: test(x.f, 50, 543),
            lambda x: test(x.f, 100, 2418),
        ],
    ),
    PythonGeneratorPrompt(
        lc_template,
        key="is_leap_year",
        user_input="write a function that checks whether a given year is a leap year",
        evaluators=[
            lambda x: test(x.f, 2000, True),
            lambda x: test(x.f, 1900, False),
            lambda x: test(x.f, 2020, True),
            lambda x: test(x.f, 2021, False),
            lambda x: test(x.f, 2400, True),
        ],
    ),
    PythonGeneratorPrompt(
        lc_template,
        key="longest_substring_without_repeating_chars",
        user_input=(
            "write a function that finds the longest substring of a ",
            "given string without repeating characters",
        ),
        evaluators=[
            lambda x: test(x.f, "abcabcbb", "abc"),
            lambda x: test(x.f, "bbbbbb", "b"),
            lambda x: test(x.f, "pwwkew", "wke"),
            lambda x: test(x.f, "abcdefgh", "abcdefgh"),
            lambda x: test(x.f, "abcbdacf", "bdacf"),
        ],
    ),
    PythonGeneratorPrompt(
        lc_template,
        key="longest_common_prefix",
        user_input="write a function that finds the longest common prefix of a list of strings",
        evaluators=[
            lambda x: test(x.f, ["flower", "flow", "flight"], "fl"),
            lambda x: test(x.f, ["dog", "racecar", "car"], ""),
            lambda x: test(x.f, ["interspecies", "interstellar", "interstate"], "inter"),
            lambda x: test(x.f, ["prefix", "suffix", "infix"], ""),
            lambda x: test(x.f, ["geeksforgeeks", "geeks", "geek"], "geek"),
        ],
    ),
    PythonGeneratorPrompt(
        lc_template,
        key="sum_of_digits",
        user_input="write a function that calculates the sum of the digits of a given number",
        evaluators=[
            lambda x: test(x.f, 123, 6),
            lambda x: test(x.f, 456, 15),
            lambda x: test(x.f, 789, 24),
            lambda x: test(x.f, 1001, 2),
            lambda x: test(x.f, 54321, 15),
        ],
    ),
    PythonGeneratorPrompt(
        lc_template,
        key="decimal_to_binary",
        user_input=(
            "write a function that converts a given decimal number to " "its binary representation"
        ),
        evaluators=[
            lambda x: test(x.f, 2, "10"),
            lambda x: test(x.f, 7, "111"),
            lambda x: test(x.f, 10, "1010"),
            lambda x: test(x.f, 16, "10000"),
            lambda x: test(x.f, 31, "11111"),
        ],
    ),
]
