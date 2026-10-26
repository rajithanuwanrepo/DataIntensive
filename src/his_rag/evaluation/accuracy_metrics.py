"""Small keyword-recall metric for the bundled example."""


def term_recall(answer: str, expected_terms: list[str]) -> float:
    if not expected_terms:
        return 1.0
    normalized = answer.casefold()
    return sum(term.casefold() in normalized for term in expected_terms) / len(expected_terms)