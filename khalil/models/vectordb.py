import random
from abc import ABC, abstractmethod

# NOTE: maybe change the place for these importance
from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb.utils import embedding_functions

REFERENCE_DISTANCE = 0.4
NUMBERS_TO_RETREIVE = 20
TOP_K = 3


class VectorDB(ABC):
    # TODO: types
    def __init__(self, vectordb, embedding_model) -> None:
        self.vectordb = vectordb
        self.embedding_model = embedding_model

    # TODO: types

    @abstractmethod
    def get_all(self):
        pass

    # TODO: types
    @abstractmethod
    def get_random(self):
        pass

    # TODO: types
    @abstractmethod
    def get_similiar_results(self, text: str):
        pass

    # TODO: types
    @abstractmethod
    def get_similar_to_random(self):
        pass


class Chroma(VectorDB):
    def __init__(self, vectordb, embedding_model) -> None:
        super().__init__(vectordb, embedding_model)
        # TODO: fix
        self.collection = self.load_collection(collection_name='langchain')

    def load_collection(self, collection_name: str) -> None:
        class MyEmbeddingFunction(EmbeddingFunction[Documents]):
            def __call__(self, input: Documents) -> Embeddings:
                sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                    # TODO: fix the embeddor model
                    model_name="BAAI/bge-base-en-v1.5")
                embeddings = sentence_transformer_ef(input)
                return embeddings

        custom = MyEmbeddingFunction()
        return self.vectordb.get_collection(name=collection_name, embedding_function=custom)

    def get_all(self):
        results_all = self.collection.get()
        return results_all

    def get_random(self):
        results_all = self.get_all()
        # TODO: do the below part differently to return everything not just the document
        return random.choice(results_all["documents"])

    # TODO: types
    def get_similiar_results(self, text: str):
        return self.collection.query(
            query_texts=[text],
            n_results=NUMBERS_TO_RETREIVE
        )

    # TODO: types
    def get_similar_to_random(self):
        random_choice = self.get_random()
        similiar_to_chosen_context = self.get_similiar_results(random_choice)
        similiar_to_chosen_context = self.get_less_than_distance(
            similiar_to_chosen_context)

    # TODO: REDO THE ENTIRE FUNTION IN A PROPER WAY GARBAAAAAAAAAAAAAAAAAAAAAAAAAGE
    # TODO: also fix the types

    # TODO: maybe make this an abstract function in the above class?!
    def get_less_than_distance(self, similiar_to_chosen_context) -> dict[str, list[list[str]]]:

        results_distances = similiar_to_chosen_context['distances'][0]
        results_documents = similiar_to_chosen_context['documents'][0]
        results_metadatas = similiar_to_chosen_context['metadatas'][0]
        # NOTE: the case where nothing should be done
        if max(results_distances) < REFERENCE_DISTANCE:
            print('nothing  could be done')
            results_distances = results_distances[:TOP_K]
            results_documents = results_documents[:TOP_K]
            results_metadatas = results_metadatas[:TOP_K]
            result = {
                'distances': [results_distances],
                'documents': [results_documents],
                'metadatas': [results_metadatas]
            }
            return result

            # NOTE: get the ids to delete
        to_delete: list[int] = []
        for index, distance in enumerate(results_distances):
            if distance < REFERENCE_DISTANCE:
                to_delete.append(index)

        results_distances = [element for index, element in enumerate(
            results_distances) if index in to_delete][:TOP_K]
        results_documents = [element for index, element in enumerate(
            results_documents) if index in to_delete][:TOP_K]
        results_metadatas = [element for index, element in enumerate(
            results_metadatas) if index in to_delete][:TOP_K]

        # NOTE: match chromadb's output
        result = {
            'distances': [results_distances],
            'documents': [results_documents],
            'metadatas': [results_metadatas]
        }
        return result
