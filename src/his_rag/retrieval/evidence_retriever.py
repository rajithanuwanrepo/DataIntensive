"""Retrieve graph evidence for a patient-scoped question."""

from __future__ import annotations

from his_rag.graph.graph_repository import GraphRepository


def retrieve_evidence(patient_id: str | None, repository: GraphRepository) -> list[dict[str, str]]:
    if not patient_id:
        return []
    return repository.events_for_patient(patient_id)