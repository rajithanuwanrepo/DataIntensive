"""Evidence container for retrieved graph facts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Evidence:
    source_id: str
    fields: dict[str, str]