import openai
import json
import os

class Batch:
    def __init__(self, *args):
        self.files = args
        self.api_key = os.environ["OPENAI_API_KEY"]


class Model:
    def __init__(self, batch: Batch, api_key: str):
        self.batch = batch
        self.api_key = api_key

    def call():
        stream = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": ""}],
            stream=True
        )
