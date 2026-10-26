"""Load patient and event records into a graph repository."""

from __future__ import annotations

from his_rag.graph.graph_repository import GraphRepository


def build_graph(patients: list[dict[str, str]], events: list[dict[str, str]], repository: GraphRepository) -> GraphRepository:
    for patient in patients:
        repository.add_patient(patient)
    for event in events:
        repository.add_event(event)
    return repository