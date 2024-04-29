# TODO: handle different types of models differently
import re
from abc import ABC, abstractmethod
from typing import Any

import ollama  # NOTE: conditional imports?
from transformers import pipeline

from khalil.models.Prompt import Prompt


class Model(ABC):
    def __init__(self, model: Any, model_name: str = ''):
        self.model_name = model_name
        self.model = model
        self.is_ollama = False

    # TODO: fix the inputs and the outputs
    def generate(self, prompt: Prompt | str) -> str:
        return ''

    # TODO: fix the inputs and the outputs
    def encode(self, sentence: str):
        pass


# TODO: fix the types of the model and the tokenizer to work with huggingface transformers
class AutoRegressiveModel(Model):
    def __init__(self, model: Any, tokenizer: Any = None, max_new_tokens: int = 1_000_000, do_sample: bool = True, temperature: float = 0.7, top_p: float = 0.95, top_k: float = 40, repetition_penalty: float = 1.1, model_name: str = '', is_ollama: bool = False):
        if is_ollama:
            if model_name == '':
                raise ValueError(
                    'model name cannot be empty if the is_ollama is True')
            self.model_name = model_name
            self.model = None
            self.is_ollama = True

        else:
            super().__init__(model)
            self.tokenizer = tokenizer
            self.pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=max_new_tokens,
                do_sample=do_sample,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repetition_penalty=repetition_penalty
            )

    # TODO: Parse the output and return only the model reply
    # TODO: specifiy the prompt or use the default one
    def generate(self, prompt: Prompt | str) -> str:

        # check if the user passed in a string, if yes convert it into a prompt
        if isinstance(prompt, str):
            prompt = Prompt(prompt)

        reply: str
        if self.is_ollama:
            response = ollama.chat(model=self.model_name, messages=[
                {
                    'role': 'user',
                    'content': prompt.get_text(),
                },
            ])
            reply = response['message']['content']

        else:
            messages = [
                {"role": "user", "content": prompt.get_text()},
            ]
            prompt = self.tokenizer.apply_chat_template(
                messages, tokenize=False)
            model_reply = self.pipeline(
                # TODO: how to get rid of this error
                prompt)[0]['generated_text'][len(prompt):]

            reply = model_reply

        # TODO: how to get rid of this error too since the prompt should always be str
        print(reply)
        return prompt.parse_output(reply)


class Encoder(Model):
    def __init__(self, model: Any):
        super().__init__(model)

    def encode(self, sentence: str):
        result = self.model.encode(sentence, normalize_embeddings=True)
        return result
