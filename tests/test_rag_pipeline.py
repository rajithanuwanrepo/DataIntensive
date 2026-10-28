from his_rag.graph.graph_builder import build_graph
from his_rag.rag.rag_pipeline import RAGPipeline


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

    def subgraph_for_patient(self, patient_id: str) -> dict[str, list[dict[str, object]]]:
        patient = self.patients.get(patient_id)
        events = self.events_for_patient(patient_id)
        nodes: list[dict[str, object]] = []
        relationships: list[dict[str, object]] = []
        if patient is not None:
            nodes.append({"id": patient_id, "type": "Patient", "properties": dict(patient)})
        for event in events:
            nodes.append({"id": event["event_id"], "type": "PatientRegistrationEvent", "properties": event})
            relationships.append({
                "type": "hasPatientRegistrationEvent",
                "sourceId": patient_id,
                "targetId": event["event_id"],
            })
        return {"nodes": nodes, "relationships": relationships}


def test_pipeline_only_exposes_stencil_allowed_fields() -> None:
    repository = build_graph(
        [{"patient_id": "P-1"}],
        [{"event_id": "E-1", "patient_id": "P-1", "event_type": "patient_registration", "name": "Private"}],
        FakeRepository(),
    )
    stencil = {"entities": {"PatientRegistrationEvent": ["patientId"]}, "relationships": []}
    result = RAGPipeline(repository, stencil).ask("P-1")
    assert "P-1" in result["answer"]
    assert "Private" not in result["context"]