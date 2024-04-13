import random
from typing import Text


from khalil.models.base import AutoRegressiveModel, Encoder
from khalil.synthetic_data.prompt import (
    context_relevancy, simple_question_prompt, parse_context_relevency_output)


class Synthetic_data_generator:

    # TODO: fix the constructor's parameters
    # TODO: fix the types
    def __init__(self, generator: AutoRegressiveModel, judge: AutoRegressiveModel, encoder: Encoder) -> None:
        self.generator = generator
        self.judge = judge
        self.encoder = encoder
        self.vector_db = None

    # TODO: Fix the type of the vectordb
    # TODO: refactor the code below
    def generate_from_vector_db(self,  vector_db, num_questions: int = 3,) -> dict[Text, list[Text]]:
        """
        generates synthetic data from an already existing vectordb by follwing the following steps:
        1- gets a random context partially done
        2- gets top K similar to the chosen context DONE ( requires some verifications)
        3- passes them to the llm to generate a question
        4- verifies the generated question
        5- repeates for the number of question to generate
        """
        self.vector_db = vector_db

        synthetic_data: dict[Text, list[Text]] = {}
        # TODO: deal with Chromadb collections
        collection = self.vector_db.get_collection(name="Students")
        results_all = collection.get()
        i = 0
        while (i < num_questions):

            choice = random.choice(
                results_all["documents"]) if results_all["documents"] else None

            similiar_to_chosen_context = collection.query(
                query_texts=[choice] if choice else None,
                n_results=3
            )
            contexts = []
            contexts.append(choice)
            contexts.extend(
                similiar_to_chosen_context['documents']) if similiar_to_chosen_context['documents'] else None
            synthetic_data_sample = self._generate(contexts)
            synthetic_data = synthetic_data | synthetic_data_sample
            i += 1
        return synthetic_data

    # TODO: finish the logic for the judge
    # TODO: refactor the part inside the while and really think about it
    # TODO: add the POOR feature
    # TODO: check if the dict type works on 3.9>

    def _generate(self, contexts: list[str]) -> dict[Text, list[Text]]:
        """
        generates one question and verifies it for the given list of contexts
        """
        synthetic_data_sample: dict[Text, list[Text]] = {}
        question: Text = ''
        not_verified: bool = True
        while (not_verified):
            prompt = simple_question_prompt(contexts)
            question = self.generator.generate(prompt)
            # verify the quality of the question
            prompt = context_relevancy(question, contexts)
            judge_reply = self.judge.generate(prompt)
            verdict: int = parse_context_relevency_output(judge_reply)

            if verdict == 1:
                synthetic_data_sample[question] = contexts
                not_verified = False

        return synthetic_data_sample
