"""Evaluation aggregation helpers."""

from __future__ import annotations

from his_rag.evaluation.accuracy_metrics import term_recall


def evaluate_answer(answer: str, expected_terms: list[str]) -> dict[str, float]:
    return {"term_recall": term_recall(answer, expected_terms)}