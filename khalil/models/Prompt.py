from typing import Callable


class Prompt:
    # TODO: update the data to work with any time of data (not just question, contexts and answer)
    # TODO: update to work with multiple examples (few shot)
    # TODO: docs

    def __init__(self, base: str, data: dict[str, str | list[str]] = {}, parse: Callable = lambda x: x, example_data: list[dict[str, str | list[str]]] = []) -> None:
        """
        prompts always follow this format:

        1- Base prompt (the part of the prompt where you tell the llm what to do)
        2- data (see below)

        *********
        3 cases for data:
            Case 1: only question 
            Case 2: only examples (contexts), should always be a list
            Case 3: question and contexts and **answer**
        """

        self.base = base
        self.data = data
        self.example_data = example_data
        self.parse = parse

        # create the prompt
        self._create_prompt()

    def _create_prompt(self) -> None:
        # beginning of creating the prompt
        self.prompt = self.base
        # NOTE: add the examples if the exist
        if self.example_data:
            self.prompt += "here's some examples to give you an idea on what your answer should be, do not follow by heart."
            for example in self.example_data:
                if 'contexts' in example:
                    bs = '\n'
                    self.prompt += f'\ncontext: {bs.join(context for context in example["contexts"])}'

                if 'question' in example:
                    self.prompt += f'\nquestion: {example["question"]}'

                if 'answer' in example:
                    self.prompt += f'\nanswer: {example["answer"]}'

        self.prompt += "here's the data you should use to answer"
        # NOTE: add the data needed if it exists
        if 'question' in self.data:
            self.prompt += f'\nquestion: {self.data["question"]}'
        if 'contexts' in self.data:
            bs = '\n'
            self.prompt += f'\ncontext: {bs.join(context for context in self.data["contexts"])}'
        if 'answer' in self.data:
            self.prompt += f'\nanswer: {self.data["answer"]}'


    def get_text(self) -> str:
        return self.prompt

    def parse_output(self, output: str) -> str:
        return self.parse(output)
