import random

from khalil.evaluation.context_relevancy import context_relevany
from khalil.evaluation.faithfulness import faithfulness
from khalil.models.base import AutoRegressiveModel, Encoder
from khalil.models.Prompt import Prompt
from khalil.synthetic_data.prompt import SIMPLE_QUESTION_PROMPT


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
    def generate_from_vector_db(self,  vector_db, num_questions: int = 3) -> dict[str, list[str]]:
        """
        generates synthetic data from an already existing vectordb by follwing the following steps:
        1- gets a random context partially done
        2- gets top K similar to the chosen context DONE ( requires some verifications)
        3- passes them to the llm to generate a question
        4- verifies the generated question
        5- repeates for the number of question to generate
        """
        self.vector_db = vector_db

        synthetic_data: dict[str, list[str]] = {}
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
            contexts = similiar_to_chosen_context['documents'][0]
            synthetic_data_sample = self._generate(contexts)
            synthetic_data = synthetic_data | synthetic_data_sample
            i += 1
        return synthetic_data

    # TODO: finish the logic for the judge
    # TODO: refactor the part inside the while and really think about it
    # TODO: add the POOR feature
    # TODO: check if the dict type works on 3.9>

    def _generate(self, contexts: list[str]) -> dict[str, list[str]]:
        """
        generates one question and verifies it for the given list of contexts
        """
        synthetic_data_sample: dict[str, list[str]] = {}
        question: str = ''
        not_verified: bool = True

        # prompts
        generation_data: dict[str, str | list[str]] = {'contexts': contexts}
        generation_prompt: Prompt = Prompt(
            base=SIMPLE_QUESTION_PROMPT,
            data=generation_data
        )
        print('GENERATION PROMPT', generation_prompt.get_text())

        # TODO: fail safe in case it never gets verified
        while (not_verified):

            print('*******\nTRYING')
            question: str = self.generator.generate(
                generation_prompt.get_text())
            print('\nCHOSEN QUESTION:', question, '\n')
            # verify the quality of the question
            judge_data: dict[str, str | list[str]] = {
                'question': question,
                'contexts': contexts
            }
            # verdict: int = context_relevany(self.judge, judge_data)
            del judge_data['question']
            print('*****')
            judge_data['answer'] = 'Alexandra Thompson is 19 years old'
            print('judge data: ', judge_data)
            print('*****')
            verdict: int = faithfulness(self.judge, judge_data)

            if verdict == 1:
                synthetic_data_sample[question] = contexts
                not_verified = False

        return synthetic_data_sample
