"""Convert evidence into a privacy-filtered context string."""

from __future__ import annotations

import json

from his_rag.privacy.stencil_engine import apply_stencil_to_subgraph


def build_context(evidence: dict[str, list[dict[str, object]]], stencil: dict[str, object]) -> str:
    filtered_subgraph = apply_stencil_to_subgraph(evidence, stencil)
    return json.dumps(filtered_subgraph, sort_keys=True)