"""Deterministic fictional patient record generator."""

from __future__ import annotations

from random import Random


def generate_patients(count: int = 10, seed: int = 17) -> list[dict[str, str]]:
    """Generate fictional patients; values are never sourced from real records."""
    if count < 0:
        raise ValueError("count must be non-negative")
    random = Random(seed)
    return [
        {
            "patient_id": f"P-{1000 + index}",
            "name": f"Fictional Patient {index + 1}",
            "date_of_birth": f"{1950 + random.randrange(55)}-01-01",
            "phone": f"555-{index:04d}",
        }
        for index in range(count)
    ]