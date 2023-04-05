import openai
import os


def execute_prompt(prompt, completion_create_kwargs):
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    completion = openai.Completion.create(
        prompt=prompt,
        **completion_create_kwargs,
    )
    return completion
