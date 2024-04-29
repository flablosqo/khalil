# NOTE: why use this instead of object
from typing import Any

import numpy as np
import pandas as pd
from numpy.linalg import norm

import random

from khalil.models.base import Encoder

ACCEPTANCE_THRESHOLD: float = 0.5

# TODO:  fix the default encoder


class Finetune_dataset():
    # NOTE: why am i not able to put Encoder as the type for the encoder
    def __init__(self, dataset: list[dict[str, str]] | pd.DataFrame, encoder=Encoder) -> None:
        self.encoder = encoder

        if isinstance(dataset, pd.DataFrame):
            dataset = dataset.to_dict('records')
        self.dataset: list[dict[str, str]] = dataset
        self.full_dataset: list[dict[str, str]] = []

    # TODO: update the return type with the correct one

    def encode_text(self, text: str) -> Any:
        # TODO: WHY THE BELOW ERROR
        return self.encoder.encode(text)

    # TODO: fix the types for the vectors
    # NOTE: maybe this shouldn't be a method?
    # TODO: change the vect type to accept python lists too
    def calculate_cosine_similarity(self, vect1: np.ndarray, vect2: np.ndarray) -> float:
        return np.dot(vect1, vect2)/(norm(vect1)*norm(vect2))

    # NOTE: maybe this shouldn't be a method?
    def get_negative_sample(self, sample: dict[str, str]) -> dict[str, str]:
        found: bool = False
        while not found:
            choice = random.choice(self.dataset)
            # NOTE: fix the types below
            encoded_original = self.encode_text(sample['context'])
            encoded_chosen = self.encode_text(choice['context'])
            cos_sim = self.calculate_cosine_similarity(
                encoded_original, encoded_chosen)
            if cos_sim < ACCEPTANCE_THRESHOLD:
                sample['wrong_context'] = choice['context']
                found = True
        return sample

    def get_full_dataset(self) -> list[dict[str, str]]:
        dataset = self.dataset
        for index, element in enumerate(dataset):
            dataset[index] = self.get_negative_sample(element)
        self.full_dataset = dataset
        return self.full_dataset
