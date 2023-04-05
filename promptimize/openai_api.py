import openai
import os


def execute_prompt(prompt, model_id="text-davinci-003", max_tokens=1000):
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    completion = openai.Completion.create(
        model=model_id, prompt=prompt, max_tokens=max_tokens,
    )
    return completion
