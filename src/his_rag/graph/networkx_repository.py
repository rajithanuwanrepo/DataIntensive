"""Dependency-free in-memory graph repository used by the starter."""

from __future__ import annotations


class NetworkXRepository:
    """A small adjacency-style repository; no NetworkX dependency is required."""

    def __init__(self) -> None:
        self.patients: dict[str, dict[str, str]] = {}
        self.events: dict[str, dict[str, str]] = {}

    def add_patient(self, patient: dict[str, str]) -> None:
        self.patients[patient["patient_id"]] = dict(patient)

    def add_event(self, event: dict[str, str]) -> None:
        self.events[event["event_id"]] = dict(event)

    def events_for_patient(self, patient_id: str) -> list[dict[str, str]]:
        return [dict(event) for event in self.events.values() if event["patient_id"] == patient_id]