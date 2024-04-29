# NOTE: all  the metrics are available
import re
from abc import ABC, abstractmethod

from khalil.evaluation.context_relevancy import context_relevany_many
from khalil.evaluation.faithfulness import faithfulness_many
from khalil.models.Prompt import Prompt

METRICS: list[str] = [
    'CONTEXT RELEVENCY',
    'FAITHFULNESS',
]


def summary(judge, data: list[dict[str, str | list[str]]]) -> dict[str, float]:
    context_relevany_score: float = context_relevany_many(judge, data)
    faithfulness_score: float = faithfulness_many(judge, data)
    return {
        'faithfulness': faithfulness_score,
        'context relevency': context_relevany_score
    }


# NOTE: everything starts here


class Metric(ABC):

    # TODO: FIX the types
    def __init__(self, judge) -> None:
        self.judge = judge
        self.base_prompt = None

    @abstractmethod
    def parse_output(self, text: str) -> int:
        """
        * defines how to parse the output of the judge
        * will be used in the prompt
        """
        pass

    @abstractmethod
    def create_prompt(self, data: dict[str, str | list[str]]) -> Prompt:
        # NOTE: make sure to affect the prompt to the object
        pass

    def calculate_one(self, data: dict[str, str | list[str]]) -> float:
        """
        calculates the metric for one example 
        """
        prompt = self.create_prompt(data)
        print(prompt.get_text())
        verdict: int = self.judge.generate(prompt)
        print('**************')
        print('judge verdict: ', verdict)
        # TODO: make this a oneliner??
        return verdict

    def calculate_many(self, data: list[dict[str, str | list[str]]]) -> float:
        """
        calculates the metric for multiple examples
        """
        # NOTE: maybe not use a lot variables and still make it somehow readable??
        sum_verdicts: float = 0
        for element in data:
            sum_verdicts += self.calculate_one(element)
        score: float = sum_verdicts / len(data)
        return score


CONTEXT_RELEVANCY: str = """from this context can I infer that answer ? Please utilize only the provided context and not the general information. 
If your response is no, {{verdict: 0}}; otherwise, {{verdict: 1}}.
the variable verdict should be the last thing in your answer.
"""


class Context_Relevancy(Metric):
    def __init__(self, judge) -> None:
        super().__init__(judge)
        self.base_prompt = CONTEXT_RELEVANCY

    def parse_output(self, text: str) -> int:
        """
        * parses the judges output that comes out of the prompt context_relevency
        * return: 0 or 1 (the veridict  and -1 if there is no verdict)
        """
        pattern = r'verdict: (\d)'
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
        else:
            return -1

    def create_prompt(self, data: dict[str, str | list[str]]) -> Prompt:
        # NOTE: make sure to affect the prompt to the object

        prompt = Prompt(base=self.base_prompt,
                        data=data, parse=self.parse_output)
        return prompt


FAITHFULNESS: str = """from this context can I infer that answer ? Please utilize only the provided context and not the general information. 
If your response is no, {{verdict: 0}}; otherwise, {{verdict: 1}}.
the variable verdict should be the last thing in your answer."""


class Faithfulness(Metric):
    def __init__(self, judge) -> None:
        super().__init__(judge)
        self.base_prompt = FAITHFULNESS

    def parse_output(self, text: str) -> int:
        """
        this function answer this question: how should the output of the judge be parsed
        * parses the judges output that comes out of the prompt context_relevency
        * return: 0 or 1 (the veridict  and -1 if there is no verdict)
        """
        pattern = r'verdict: (\d)'
        matches = re.findall(pattern, text)

        if matches:
            return int(matches[-1])
        else:
            return -1

    def create_prompt(self, data: dict[str, str | list[str]]) -> Prompt:
        # NOTE: make sure to affect the prompt to the object

        prompt = Prompt(base=self.base_prompt,
                        data=data, parse=self.parse_output)
        return prompt
