# NOTE: why use this instead of object
import random
from typing import Any

import numpy as np
import pandas as pd
from numpy.linalg import norm

from khalil.models.base import Encoder

ACCEPTANCE_THRESHOLD = 0.5

# TODO:  add a default encoder


class Finetune_dataset():
    # NOTE: why am i not able to put Encoder as the type for the encoder
    def __init__(self, dataset: list[dict[str, str]] | pd.DataFrame, encoder: Encoder) -> None:
        """
        columns should include "question, context and answer"
        """

        self.encoder = encoder

        if isinstance(dataset, pd.DataFrame):
            dataset = dataset.to_dict('records')
        MANDATORY_COLUMNS = ['question', 'context', 'answer']
        if not all(element in dataset[0].keys() for element in MANDATORY_COLUMNS):
            raise ValueError(
                'the format of the dataset you entered is invalid, make sure kuestion, context and answer are present as columns')

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
    def get_negative_sample(self, sample: dict[str, str], column: str) -> dict[str, str]:
        found: bool = False
        while not found:
            choice = random.choice(self.dataset)
            # NOTE: the element chosen randomly is the same element give by the user
            if sample == choice:
                continue
            # NOTE: fix the types below
            encoded_original = self.encode_text(sample[column])
            encoded_chosen = self.encode_text(choice[column])
            cos_sim = self.calculate_cosine_similarity(
                encoded_original, encoded_chosen)
            if cos_sim < ACCEPTANCE_THRESHOLD:
                sample['wrong_'+column] = choice[column]
                found = True
        return sample

    def _add_wrongContext_feature(self) -> list[dict[str, str]]:
        dataset = self.dataset
        for index, element in enumerate(dataset):
            dataset[index] = self.get_negative_sample(element, 'context')
        return dataset

    # NOTE: doing it like this is possibly dumb? maybe integrate the entire thing in the above function
    # NOTE: affect the new dataset and make sure not to do the same thing multiple times??
    # TODO: refactor this
    def get_contextRelevency_dataset(self):
        data = self._add_wrongContext_feature()
        print('lenData', len(data))
        final_data: list[dict[str, str]] = []
        for element in data:

            new_true: dict[str, str] = {}
            new_true['text'] = '[question]' + element['question'] + \
                '[context]' + element['context']
            new_true['target'] = '1'
            final_data.append(new_true)

            new_false: dict[str, str] = {}
            new_false['text'] = '[question]' + element['question'] + \
                '[context]' + element['wrong_context']
            new_false['target'] = '0'
            final_data.append(new_false)

        return final_data

    def _add_wrongAnswer_feature(self) -> list[dict[str, str]]:
        dataset = self.dataset
        for index, element in enumerate(dataset):
            dataset[index] = self.get_negative_sample(element, 'answer')
        return dataset

    # NOTE: same as above
    def get_answerRelevency_dataset(self):
        data = self._add_wrongAnswer_feature()
        final_data: list[dict[str, str]] = []
        for element in data:
            new_true: dict[str, str] = {}
            new_true['text'] = '[question]' + element['question'] + \
                '[answer]' + element['answer']
            new_true['target'] = '1'
            final_data.append(new_true)

            new_false: dict[str, str] = {}
            new_false['text'] = '[question]' + element['question'] + \
                '[answer]' + element['wrong_answer']
            new_false['target'] = '0'
            final_data.append(new_false)

        return final_data

    # NOTE: Maybe do this function using the above two functions?
    def get_full_dataset(self) -> list[dict[str, str]]:
        dataset = self.dataset
        for index, element in enumerate(dataset):
            dataset[index] = self.get_negative_sample(element, 'context')
            dataset[index] = self.get_negative_sample(element, 'answer')
        self.full_dataset = dataset
        return self.full_dataset
