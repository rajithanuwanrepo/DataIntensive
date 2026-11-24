import io
import json
from unittest.mock import MagicMock

import pytest

from his_rag.graph.graph_builder import build_graph
from his_rag.rag import llm_client
from his_rag.rag.llm_client import OllamaLLMClient
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
            nodes.append({"id": event["event_id"], "type": event["event_type"], "properties": event})
            relationships.append({
                "type": "hasPatientRegistrationEvent",
                "sourceId": patient_id,
                "targetId": event["event_id"],
            })
        return {"nodes": nodes, "relationships": relationships}


@pytest.mark.parametrize("allow_relationship", [False, True])
@pytest.mark.parametrize("use_ollama", [False, True])
def test_pipeline_only_exposes_stencil_allowed_fields(allow_relationship, use_ollama, monkeypatch) -> None:
    repository = build_graph(
        [{"patient_id": "P-1"}],
        [{"event_id": "E-1", "patient_id": "P-1", "event_type": "PatientRegistrationEvent", "name": "Private"}],
        FakeRepository(),
    )
    stencil = {
        "root_type": "Patient",
        "nodes": {
            "Patient": {"properties": ["patient_id"]},
            "PatientRegistrationEvent": {"properties": ["patient_id"]},
        },
        "relationships": [{
            "source_type": "Patient", "type": "hasPatientRegistrationEvent",
            "target_type": "PatientRegistrationEvent",
        }] if allow_relationship else [],
    }
    client = None
    if use_ollama:
        transport = MagicMock()
        transport.return_value.__enter__.return_value = io.BytesIO(b'{"response": "Patient P-1."}')
        monkeypatch.setattr(llm_client, "urlopen", transport)
        client = OllamaLLMClient("llama3.2:3b")
    result = RAGPipeline(repository, stencil, llm=client).ask("P-1")
    if use_ollama:
        payload = json.loads(transport.call_args.args[0].data)
        assert "Private" not in payload["prompt"]
        assert result["context"] in payload["prompt"]
        assert result["answer"] == "Patient P-1."
    assert "P-1" in result["answer"]
    assert "Private" not in json.dumps(result)
    assert json.loads(result["context"]) == result["evidence"]
    assert len(result["evidence"]["nodes"]) == (2 if allow_relationship else 1)
    assert len(result["evidence"]["relationships"]) == int(allow_relationship)
    assert repository.events["E-1"]["name"] == "Private"


def test_pipeline_can_disable_masking_for_one_question() -> None:
    repository = build_graph(
        [{"patient_id": "P-1", "name": "Private"}], [], FakeRepository(),
    )
    stencil = {
        "root_type": "Patient",
        "nodes": {"Patient": {"properties": ["patient_id"]}},
        "relationships": [],
    }
    client = MagicMock()
    pipeline = RAGPipeline(repository, stencil, llm=client)

    unmasked = pipeline.ask("P-1", mask=False)
    assert unmasked["evidence"] == repository.subgraph_for_patient("P-1")
    assert "Private" in client.generate.call_args.args[0]

    masked = pipeline.ask("P-1", mask=True)
    assert "Private" not in masked["context"]
    assert "Private" not in client.generate.call_args.args[0]
