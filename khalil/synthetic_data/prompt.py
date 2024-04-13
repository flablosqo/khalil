import re
from typing import Text


def simple_question_prompt(contexts: list[Text]) -> Text:
    print(contexts)
    bs = '\n'

    return f""" Generate one and only one question that can be fully answered from the given context,
your answer should not contain anything other than the question. the question should not contain any information from the context, it also should not be too precise but should be fully answered from the provided context. 
context: {bs.join(context for context in contexts)}
"""


# TODO: move it to a the eval package
# TODO: maybe ask it to provide answer as well
def context_relevancy(question: Text, contexts: list[Text]) -> Text:
    bs = '\n'
    return f"""check if the following question can be answered fully from the provided context.
you should not rely on any prior knowledge you have, rely only on the context.
Your answer should be in this format: [[verdict:1]] if the context was useful and [[verdict:0]] if it was not.
question: {question}
context: {bs.join(context for context in contexts)}
"""


# TODO: move this somewhere else
def parse_context_relevency_output(output: Text) -> int:
    """
    parses the judges output that comes out of the prompt context_relevency
    return: 0 or 1 (the veridict  and -1 if there is no verdict)
    """
    # Regular expression pattern
    pattern = r'\[/INST\].*?\[\[verdict:(\d+)\]\]'

    # Search for the pattern
    match = re.search(pattern, output)

    # Extract the number
    if match:
        verdict_number = match.group(1)
        return int(verdict_number)
    else:
        return -1
