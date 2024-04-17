# NOTE: all  the metrics are available
from khalil.evaluation.context_relevancy import context_relevany_many
from khalil.evaluation.faithfulness import faithfulness_many

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
