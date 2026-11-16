"""Filter a patient subgraph using a role's graph-template allowlists."""

from __future__ import annotations

import json
from typing import Any

from his_rag.privacy.stencil_loader import validate_stencil


def apply_stencil_to_subgraph(
    subgraph: dict[str, list[dict[str, Any]]],
    stencil: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    """Keep the root and events directly linked by permitted relationships.

    Node IDs and types remain structural metadata. Only explicitly allowed
    properties are copied; unknown node and relationship types are excluded.
    """
    validate_stencil(stencil)
    print("Evidence subgraph before masking:")
    print(json.dumps(subgraph, indent=2, ensure_ascii=False, default=str))

    node_rules = stencil["nodes"]
    nodes_by_id = {
        str(node["id"]): node
        for node in subgraph.get("nodes", [])
        if node.get("id") is not None and node.get("type") in node_rules
    }
    allowed_relationships = {
        (rule["source_type"], rule["type"], rule["target_type"])
        for rule in stencil["relationships"]
    }
    permitted_edges: list[dict[str, str]] = []
    for relationship in subgraph.get("relationships", []):
        source_id = str(relationship.get("sourceId"))
        target_id = str(relationship.get("targetId"))
        source = nodes_by_id.get(source_id)
        target = nodes_by_id.get(target_id)
        if source is None or target is None:
            continue
        rule = (source["type"], relationship.get("type"), target["type"])
        if rule not in allowed_relationships:
            continue
        permitted_edges.append({
            "sourceId": source_id,
            "targetId": target_id,
            "type": relationship["type"],
        })

    # The retrieval query returns only direct patient-to-event connections.
    root_ids = {
        node_id for node_id, node in nodes_by_id.items()
        if node["type"] == stencil["root_type"]
    }
    permitted_edges = [
        edge for edge in permitted_edges if edge["sourceId"] in root_ids
    ]
    retained_ids = root_ids | {edge["targetId"] for edge in permitted_edges}

    filtered_nodes = []
    for node_id, node in nodes_by_id.items():
        if node_id not in retained_ids:
            continue
        allowed_properties = node_rules[node["type"]]["properties"]
        filtered_nodes.append({
            "id": node_id,
            "type": node["type"],
            "properties": {
                key: value for key, value in node.get("properties", {}).items()
                if key in allowed_properties
            },
        })

    return {
        "nodes": filtered_nodes,
        "relationships": permitted_edges,
    }
