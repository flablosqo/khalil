# TODO: DEAL WITH DICT TYPES
import random

from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb.utils import embedding_functions

from khalil.evaluation.context_relevancy import context_relevany_one
from khalil.evaluation.faithfulness import faithfulness_one
from khalil.models.base import AutoRegressiveModel, Encoder
from khalil.models.Prompt import Prompt
from khalil.synthetic_data.prompt import TYPES

# NOTE: chroma part


class MyEmbeddingFunction(EmbeddingFunction[Documents]):
    def __call__(self, input: Documents) -> Embeddings:
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="BAAI/bge-base-en-v1.5")
        embeddings = sentence_transformer_ef(input)
        return embeddings


custom = MyEmbeddingFunction()


class Synthetic_data_generator:

    # TODO: fix the constructor's parameters
    # TODO: fix the types
    def __init__(self, generator: AutoRegressiveModel, judge: AutoRegressiveModel, encoder: Encoder) -> None:
        self.generator = generator
        self.judge = judge
        self.encoder = encoder
        self.vector_db = None

    # TODO: Fix the type of the vectordb and the dict
    # TODO: refactor the code below
    # TODO: don't like this
    def generate_from_vector_db(self,
                                vector_db,
                                num_questions: int = 3,
                                distribution: dict[str, float] = {'simple': 0.7, 'multiple': 0.3}) -> list[dict[str, str | list[str]]]:
        """
        generates synthetic data from an already existing vectordb by follwing the following steps:
        1- gets a random context partially done
        2- gets top K similar to the chosen context DONE ( requires some verifications)
        3- passes them to the llm to generate a question
        4- verifies the generated question
        5- repeates for the number of question to generate
        """
        if sum(distribution.values()) != 1:
            raise ValueError('distribution must sum up to 1')
        simple_question: int = round(num_questions*distribution['simple'])
        multiple_context_question: int = round(
            num_questions*distribution['multiple']
        )
        print('simple questions', simple_question)
        print('multiple context questions', multiple_context_question)

        self.vector_db = vector_db

        # synthetic_data: dict[int, dict[str, str | list[str]]] = {}
        synthetic_data: list[dict[str, str | list[str]]] = []

        # TODO: deal with Chromadb collections
        collection = self.vector_db.get_collection(
            name="langchain", embedding_function=custom)
        results_all = collection.get()

        i: int = 0
        while i < simple_question:
            synthetic_data_sample = self._generate(results_all, 'simple')
            synthetic_data.append(synthetic_data_sample)
            i += 1

        # TODO: Really don't like the 2 while loops
        i = 0
        while i < multiple_context_question:
            synthetic_data_sample = self._generate(results_all, 'multiple')
            synthetic_data.append(synthetic_data_sample)
            i += 1
        return synthetic_data

    # TODO: finish the logic for the judge
    # TODO: refactor the part inside the while and really think about it
    # TODO: add the POOR feature
    # TODO: check if the dict type works on 3.9>

    # TODO: deal with the type of results all
    def _generate(self, results_all, type: str) -> dict[str, str | list[str]]:
        """
        generates one question and verifies it for the given list of contexts
        """
        generated_sample: dict[str, str | list[str]] = {}
        question: str
        # TODO: deal with this when dealing with new vectordb
        collection = self.vector_db.get_collection(
            name="langchain", embedding_function=custom) if self.vector_db else None
        verdict: int = 0
        while verdict == 0:
            choice = random.choice(
                results_all["documents"]) if results_all["documents"] else None

            # NOTE: THE ASSUMPTION IS THAT THE CONTEXT PROVIDE SIMILAR BUT SOMEWHAT DIFFERENT INFORMATION/// verify with multiple context quesetion
            similiar_to_chosen_context = collection.query(
                query_texts=[choice] if choice else None,
                n_results=3
            ) if collection else None
            contexts: list[str] = similiar_to_chosen_context['documents'][0] if similiar_to_chosen_context else []
            # prompts
            generation_data: dict[str, str | list[str]] = {
                'contexts': contexts}
            generation_prompt: Prompt = Prompt(
                base=TYPES[type],
                data=generation_data
            )

            question: str = self.generator.generate(
                generation_prompt.get_text())
            print('\nCHOSEN QUESTION:', question, '\n')
            # verify the quality of the question
            generated_sample = {
                'question': question,
                'contexts': contexts
            }
            verdict = context_relevany_one(self.judge, generated_sample)

            if verdict == 1:
                return generated_sample
        return {}  # LSP IS ANNOYING
