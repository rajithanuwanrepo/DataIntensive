"""Load and validate JSON graph-template privacy stencils."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def validate_stencil(stencil: dict[str, Any]) -> None:
    """Reject incomplete rules instead of accidentally broadening permissions."""
    if not isinstance(stencil, dict):
        raise ValueError("stencil must be an object")
    nodes = stencil.get("nodes")
    if not isinstance(nodes, dict):
        raise ValueError("stencil must define nodes as an object")
    for node_type, rule in nodes.items():
        if not isinstance(node_type, str) or not node_type or not isinstance(rule, dict):
            raise ValueError("each node rule must have a nonempty type and an object definition")
        properties = rule.get("properties")
        if not isinstance(properties, list) or any(
            not isinstance(name, str) or not name for name in properties
        ):
            raise ValueError(f"node {node_type} must define properties as a list of property names")
    root_type = stencil.get("root_type")
    if not isinstance(root_type, str) or root_type not in nodes:
        raise ValueError("root_type must reference a configured node type")
    relationships = stencil.get("relationships")
    if not isinstance(relationships, list):
        raise ValueError("stencil must define relationships as a list")
    for rule in relationships:
        if not isinstance(rule, dict) or any(
            not isinstance(rule.get(key), str) or not rule[key]
            for key in ("source_type", "type", "target_type")
        ):
            raise ValueError("each relationship rule must define source_type, type, and target_type")
        if rule["source_type"] not in nodes or rule["target_type"] not in nodes:
            raise ValueError("relationship endpoints must reference configured node types")


def load_stencil(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as source:
        stencil = json.load(source)
    validate_stencil(stencil)
    return stencil
