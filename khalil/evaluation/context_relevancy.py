
# TODO: maybe ask it to provide answer as well
import re

from khalil.models.Prompt import Prompt

######################   START HERE ####################
CONTEXT_RELEVANCY: str = """check if the following question can be answered fully from the provided context.
you should not rely on any prior knowledge you have, rely only on the context.
your answer should always start with the verdict following this exact format note the number of the {{ and }}: {{verdict:1}} if the context was useful and {{verdict:0}} if it was not, then give me the reasoning behind your verdict.
"""


def parse_context_relevency_output(text: str) -> int:
    """
    parses the judges output that comes out of the prompt context_relevency
    return: 0 or 1 (the veridict  and -1 if there is no verdict)
    """
    pattern = r'{verdict:(\d)}'
    match = re.search(pattern, text)
    if match:
        return int(match.group(1))
    else:
        return -1

# TODO: types


def context_relevany_one(judge, data: dict[str, str | list[str]]) -> int:
    """
    calculates the metrics context relevency for one question
    """
    prompt = Prompt(base=CONTEXT_RELEVANCY, data=data,
                    parse=parse_context_relevency_output
                    )
    print('VERIFICATION PROMPT', prompt.get_text())

    judge_reply = judge.generate(prompt.get_text())
    print('judge reply', judge_reply)
    print('*******')
    verdict: int = parse_context_relevency_output(judge_reply)
    print('verdict', verdict)
    return verdict


def context_relevany_many(judge, data: list[dict[str, str | list[str]]]) -> float:
    """
    calculates the metrics context relevency for multiple questions
    """
    context_relevany_score: float = 0
    for element in data:
        context_relevany_score += context_relevany_one(judge, element)
    context_relevany_score = context_relevany_score / len(data)
    return context_relevany_score
