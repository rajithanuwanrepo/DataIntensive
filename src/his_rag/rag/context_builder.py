"""Convert evidence into a privacy-filtered context string."""

from __future__ import annotations

import json

from his_rag.privacy.stencil_engine import apply_stencil


def build_context(evidence: list[dict[str, str]], stencil: dict[str, object]) -> str:
    filtered = [apply_stencil(item, stencil) for item in evidence]
    return "\n".join(json.dumps(item, sort_keys=True) for item in filtered if item is not None)