"""Basic checks for sensitive-field leakage in filtered contexts."""


def leakage_count(context: str, sensitive_values: list[str]) -> int:
    return sum(1 for value in sensitive_values if value and value in context)