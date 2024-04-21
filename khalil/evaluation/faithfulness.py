# for now we use the entire answer for the calculation of the faithfulness
# TODO: split answer into multiple sentences


import re

from khalil.models.Prompt import Prompt

######################   START HERE ####################
FAITHFULNESS: str = """from this context can I infer that answer ? Please utilize only the provided context and not the general information. 
If your response is no, {{verdict: [[0]]}}; otherwise, {{verdict: [[1]]}}.
the variable verdict should be the last thing in your answer."""


# TODO: remake this to be a function that works everywhere
def parse_failfulness_output(text: str) -> int:
    """
    parses the judges output that comes out of the prompt context_relevency
    return: 0 or 1 (the veridict  and -1 if there is no verdict)
    """
    pattern = r'{verdict:(\d)}'
    matches = re.findall(pattern, text)

    if matches:
        return int(matches[-1])
    else:
        return -1

# TODO: types


def faithfulness_one(judge, data: dict[str, str | list[str]]) -> int:
    prompt = Prompt(base=FAITHFULNESS, data=data,
                    parse=parse_failfulness_output
                    )
    print('STARTING FAITHFULNESS\n$$$$$$$$$$$$$$$$$$$$$$\n')

    judge_reply = judge.generate(prompt.get_text())
    print('*******')
    verdict: int = parse_failfulness_output(judge_reply)
    print('verdict', verdict)
    print('DONE WITH FAITHFULNESS\n$$$$$$$$$$$$$$$$$$$$$$\n')
    return verdict


def faithfulness_many(judge, data: list[dict[str, str | list[str]]]) -> float:
    """
    calculates the metrics faithfulness for multiple questions
    """
    faithfulness_score: float = 0
    for element in data:
        faithfulness_score += faithfulness_one(judge, element)
    faithfulness_score = faithfulness_score / len(data)
    return faithfulness_score
