

from typing import Callable


class Prompt:
    # TODO: update the data to work with any time of data (not just question, contexts and answer)
    # TODO: update to work with multiple examples (few shot)
    # TODO: docs

    def __init__(self, base: str, data: dict[str, str | list[str]], parse: Callable = lambda x: x) -> None:
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
        self.parse = parse

        # beginning of creating the prompt
        self.prompt = base
        if 'question' in data:
            self.prompt += f'\nquestion: {data["question"]}'
        if 'contexts' in data:
            bs = '\n'
            self.prompt += f'\ncontext: {bs.join(context for context in data["contexts"])}'
        if 'answer' in data:
            self.prompt += f'\nanswer: {data["answer"]}'

    def get_text(self) -> str:
        return self.prompt

    def parse_output(self, output: str) -> str:
        return self.parse(output)
