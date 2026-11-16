"""Serialize an already filtered evidence subgraph for the prompt."""

from __future__ import annotations

import json


def build_context(evidence: dict[str, list[dict[str, object]]]) -> str:
    return json.dumps(evidence, sort_keys=True)
