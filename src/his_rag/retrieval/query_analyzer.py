"""Extract simple structured constraints from a question."""

from __future__ import annotations

import re


def analyze_query(question: str) -> dict[str, str | None]:
    match = re.search(r"\bP-\d+\b", question, flags=re.IGNORECASE)
    return {"patient_id": match.group(0).upper() if match else None, "text": question.strip()}