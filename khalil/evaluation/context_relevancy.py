
# TODO: maybe ask it to provide answer as well
import re

from khalil.models.Prompt import Prompt

######################   START HERE ####################
CONTEXT_RELEVANCY: str = """from this context can I infer that answer ? Please utilize only the provided context and not the general information. 
If your response is no, {{verdict: 0}}; otherwise, {{verdict: 1}}.
the variable verdict should be the last thing in your answer.
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

    judge_reply = judge.generate(prompt.get_text())
    print('*******')
    print(judge_reply)
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
