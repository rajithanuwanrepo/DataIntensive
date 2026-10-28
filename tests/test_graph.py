from his_rag.graph.graph_builder import build_graph


class FakeRepository:
    def __init__(self) -> None:
        self.patients: dict[str, dict[str, str]] = {}
        self.events: dict[str, dict[str, str]] = {}

    def add_patient(self, patient: dict[str, str]) -> None:
        self.patients[patient["patient_id"]] = dict(patient)

    def add_event(self, event: dict[str, str]) -> None:
        self.events[event["event_id"]] = dict(event)

    def events_for_patient(self, patient_id: str) -> list[dict[str, str]]:
        return [dict(event) for event in self.events.values() if event["patient_id"] == patient_id]


def test_graph_connects_events_to_patients() -> None:
    repository = build_graph(
        [{"patient_id": "P-1"}],
        [{"event_id": "E-1", "patient_id": "P-1", "event_type": "visit"}],
        FakeRepository(),
    )
    assert len(repository.events_for_patient("P-1")) == 1
    assert repository.events_for_patient("P-2") == []