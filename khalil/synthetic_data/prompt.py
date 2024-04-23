

# AFTER REFACTORING


SIMPLE_QUESTION_PROMPT: str = """ Generate one and only one question that can be fully answered from the given context, assume the person answing this context does not have the context when answring. you answer should only contain the question
"""

MULTIPLE_CONTEXT_QUESTION_PROMPT: str = """ Generate one and only one question that can be fully answered from the given context,
your answer should not contain anything other than the question. the question should not contain any information from the context, it also should not be too precise but should be fully answered from the provided context. 
"""


TYPES = {
    'simple': SIMPLE_QUESTION_PROMPT,
    'multiple': MULTIPLE_CONTEXT_QUESTION_PROMPT
}
