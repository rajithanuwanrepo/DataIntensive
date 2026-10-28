"""Repository contract for the graph backends."""

from __future__ import annotations

from typing import Protocol


class GraphRepository(Protocol):
    def add_patient(self, patient: dict[str, str]) -> None: ...

    def add_event(self, event: dict[str, str]) -> None: ...

    def events_for_patient(self, patient_id: str) -> list[dict[str, str]]: ...

    def subgraph_for_patient(self, patient_id: str) -> dict[str, list[dict[str, object]]]: ...