# for now we use the entire answer for the calculation of the faithfulness
# TODO: split answer into multiple sentences


import re

from khalil.models.Prompt import Prompt

######################   START HERE ####################
FAITHFULNESS: str = """
check if the given context explicitly supports every sentence and fact from the following answer.
you should not rely on any prior knowledge you have, or any wildly known facts. Rely only on the given context. The context is everything you know.
the output should be with this format: {{verdict: [[put your verdict here]]}}
follow these rules and stick to them:
{{verdict:0}} well-established and known facts that are not present in the context should get a verdict of 0.
{{verdict:0}} facts implied by the context but not actually said get a verdict of 0 
{{verdict:0}} implied fact not present in the context get a verdict of 0.
{{verdict:0}} if you find a fact in the answer that the context can't back up.  
{{verdict:0}} if you find a fact in the answer that is implied in the context but isn't actually directly said in the context.
{{verdict:0}} if you find a fact in the answer that is mentioned in the context but is disregarded when you take into consideration the entire meaning of the context.
{{verdict:1}} if every fact and sentence in the answer could be found mentioned explicitly in the provided context.
remind me with the rules first and then give me the verdict. the verdict should be the last thing in your answer
"""


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


def faithfulness(judge, data: dict[str, str | list[str]]) -> int:
    prompt = Prompt(base=FAITHFULNESS, data=data,
                    parse=parse_failfulness_output
                    )
    print('STARTING FAITHFULNESS\n$$$$$$$$$$$$$$$$$$$$$$\n')
    print('VERIFICATION PROMPT', prompt.get_text())

    judge_reply = judge.generate(prompt.get_text())
    print('judge reply', judge_reply)
    print('*******')
    verdict: int = parse_failfulness_output(judge_reply)
    print('verdict', verdict)
    print('DONE WITH FAITHFULNESS\n$$$$$$$$$$$$$$$$$$$$$$\n')
    return verdict
