import re
from abc import ABC, abstractmethod
from typing import Any, Text

from transformers import pipeline


class Model(ABC):
    def __init__(self, model: Any):
        self.model = model

    # TODO: fix the inputs and the outputs
    def generate(self, message: Text) -> Text:
        return ''

    # TODO: fix the inputs and the outputs
    def encode(self, sentence: Text):
        pass


# TODO: fix the types of the model and the tokenizer to work with huggingface transformers
class AutoRegressiveModel(Model):
    def __init__(self, model: Any, tokenizer: Any, max_new_tokens: int = 1_000_000, do_sample: bool = True, temperature: float = 0.7, top_p: float = 0.95, top_k: float = 40, repetition_penalty: float = 1.1):
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

    # TODO: specifiy the prompt or use the default one
    def generate(self, message: Text) -> Text:

        messages = [
            {"role": "user", "content": message},
        ]
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False)
        model_reply = self.pipeline(prompt)[0]['generated_text']
        return model_reply


class Encoder(Model):
    def __init__(self, model: Any):
        super().__init__(model)

    def encode(self, sentence: Text):
        result = self.model.encode(sentence, normalize_embeddings=True)
        return result
