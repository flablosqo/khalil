

# AFTER REFACTORING


SIMPLE_QUESTION_PROMPT: str = """
from this context can I infer that answer ? Please utilize only the provided context and not the general information. 
If your response is no, {{verdict: 0}}; otherwise, {{verdict: 1}}.
the variable verdict should be the last thing in your answer.
"""

MULTIPLE_CONTEXT_QUESTION_PROMPT: str = """ Generate one and only one question that can be fully answered from the given context,
your answer should not contain anything other than the question. the question should not contain any information from the context, it also should not be too precise but should be fully answered from the provided context. 
"""


TYPES = {
    'simple': SIMPLE_QUESTION_PROMPT,
    'multiple': MULTIPLE_CONTEXT_QUESTION_PROMPT
}
