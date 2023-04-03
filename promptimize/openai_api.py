import openai
import os

MODEL_ID = "ada"
MODEL_ID = "text-davinci-003"
MAX_TOKENS = 1000

openai.api_key = os.environ.get("OPENAI_API_KEY")

# print(openai.Model.list())
# model = openai.Model.retrieve(MODEL_ID)


def execute_prompt(prompt):
    completion = openai.Completion.create(
        model=MODEL_ID, prompt=prompt, max_tokens=MAX_TOKENS
    )
    return completion
