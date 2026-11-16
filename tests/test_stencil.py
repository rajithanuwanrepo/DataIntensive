import json
from copy import deepcopy
from pathlib import Path

import pytest

from his_rag.graph.event_graph_types import EventGraphTypes
from his_rag.privacy.stencil_engine import apply_stencil_to_subgraph
from his_rag.privacy.stencil_loader import load_stencil, validate_stencil

ROOT = Path(__file__).resolve().parents[1]


def test_event_graph_types_map_all_supported_records() -> None:
    assert EventGraphTypes.EVANT_GRAPH_RELATIONSHIPS == {
        "AppointmentEncounterEvent": "hasAppointmentEncounterEvent",
        "ImagingOrderEvent": "hasImagingOrderEvent",
        "LabOrderEvent": "hasLabOrderEvent",
        "ObservationResultEvent": "hasObservationResultEvent",
        "PatientRegistrationEvent": "hasPatientRegistrationEvent",
    }
    assert EventGraphTypes.relationship_for_record({"event_type": "LabOrderEvent"}) == "hasLabOrderEvent"


@pytest.fixture
def stencil():
    return {
        "role": "test_role",
        "root_type": "Patient",
        "nodes": {
            "Patient": {"properties": ["patient_id"]},
            "CustomEvent": {"properties": ["status", "count", "flag", "optional", "missing"]},
        },
        "relationships": [
            {"source_type": "Patient", "type": "hasCustomEvent", "target_type": "CustomEvent"}
        ],
    }


@pytest.fixture
def subgraph():
    return {
        "nodes": [
            {"id": "P-1", "type": "Patient", "properties": {"patient_id": "P-1", "name": "Private"}},
            {"id": "E-1", "type": "CustomEvent", "properties": {
                "status": "pending", "count": 0, "flag": False, "optional": None, "secret": "Private"
            }},
        ],
        "relationships": [
            {"sourceId": "P-1", "targetId": "E-1", "type": "hasCustomEvent", "secret": "Private"}
        ],
    }


def test_generic_filter_projects_properties_without_mutating_input(stencil, subgraph):
    original = deepcopy(subgraph)
    filtered = apply_stencil_to_subgraph(subgraph, stencil)
    assert filtered == {
        "nodes": [
            {"id": "P-1", "type": "Patient", "properties": {"patient_id": "P-1"}},
            {"id": "E-1", "type": "CustomEvent", "properties": {
                "status": "pending", "count": 0, "flag": False, "optional": None
            }},
        ],
        "relationships": [{"sourceId": "P-1", "targetId": "E-1", "type": "hasCustomEvent"}],
    }
    assert subgraph == original
    assert apply_stencil_to_subgraph(filtered, stencil) == filtered


@pytest.mark.parametrize("case", [
    "forbidden_relationship", "disconnected_event", "wrong_target_type",
    "reversed_relationship", "missing_endpoint", "unknown_node_type", "missing_root",
])
def test_disallowed_or_disconnected_events_are_not_exposed(stencil, subgraph, case):
    if case == "forbidden_relationship":
        stencil["relationships"] = []
    elif case == "disconnected_event":
        subgraph["relationships"] = []
    elif case == "wrong_target_type":
        stencil["relationships"][0]["target_type"] = "Patient"
    elif case == "reversed_relationship":
        subgraph["relationships"][0].update(sourceId="E-1", targetId="P-1")
    elif case == "missing_endpoint":
        subgraph["relationships"][0]["targetId"] = "missing"
    elif case == "unknown_node_type":
        subgraph["nodes"][1]["type"] = "UnknownEvent"
    elif case == "missing_root":
        subgraph["nodes"] = subgraph["nodes"][1:]

    filtered = apply_stencil_to_subgraph(subgraph, stencil)
    assert filtered["relationships"] == []
    assert [node["id"] for node in filtered["nodes"]] == ([] if case == "missing_root" else ["P-1"])


@pytest.mark.parametrize("reverse_edges", [False, True])
def test_only_direct_root_connections_are_retained(stencil, subgraph, reverse_edges):
    stencil["relationships"].append({
        "source_type": "CustomEvent", "type": "next", "target_type": "CustomEvent"
    })
    subgraph["nodes"].extend([
        {"id": node_id, "type": "CustomEvent", "properties": {"status": "pending"}}
        for node_id in ["E-2", "E-3", "E-4"]
    ])
    subgraph["relationships"].extend([
        {"sourceId": source, "targetId": target, "type": "next"}
        for source, target in [("E-1", "E-2"), ("E-2", "E-1"), ("E-3", "E-4"), ("E-4", "E-3")]
    ])
    if reverse_edges:
        subgraph["relationships"].reverse()
    filtered = apply_stencil_to_subgraph(subgraph, stencil)
    assert [node["id"] for node in filtered["nodes"]] == ["P-1", "E-1"]
    assert filtered["relationships"] == [
        {"sourceId": "P-1", "targetId": "E-1", "type": "hasCustomEvent"}
    ]


def test_empty_property_allowlist_retains_only_structural_fields(stencil, subgraph):
    stencil["nodes"]["CustomEvent"]["properties"] = []
    filtered = apply_stencil_to_subgraph(subgraph, stencil)
    assert filtered["nodes"][1] == {"id": "E-1", "type": "CustomEvent", "properties": {}}
    assert apply_stencil_to_subgraph({"nodes": [], "relationships": []}, stencil) == {
        "nodes": [], "relationships": []
    }


@pytest.mark.parametrize("invalid", [
    [],
    {"entities": {}, "relationships": []},
    {"root_type": "Missing", "nodes": {}, "relationships": []},
    {"root_type": "Patient", "nodes": {"Patient": {"properties": "name"}}, "relationships": []},
    {"root_type": "Patient", "nodes": {"Patient": {"properties": [1]}}, "relationships": []},
    {"root_type": "Patient", "nodes": {"Patient": {"properties": []}}, "relationships": ["hasEvent"]},
    {"root_type": "Patient", "nodes": {"Patient": {"properties": []}}, "relationships": [
        {"source_type": "Patient", "type": "hasEvent", "target_type": "Unknown"}
    ]},
])
def test_loader_rejects_invalid_stencils(tmp_path, invalid):
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(invalid), encoding="utf-8")
    with pytest.raises(ValueError):
        load_stencil(path)
    with pytest.raises(ValueError):
        apply_stencil_to_subgraph({"nodes": [], "relationships": []}, invalid)


def test_bundled_stencil_filters_all_synthetic_event_types():
    stencil = load_stencil(ROOT / "config/stencils/outpatient_clerk.json")
    validate_stencil(stencil)
    patients = json.loads((ROOT / "data/synthetic/patients.json").read_text())
    events = json.loads((ROOT / "data/synthetic/events.json").read_text())
    patient = patients[0]
    patient_id = patient["patient_id"]
    events = [event for event in events if event["patient_id"] == patient_id]
    subgraph = {
        "nodes": [{"id": patient_id, "type": "Patient", "properties": patient}] + [
            {"id": event["event_id"], "type": event["event_type"], "properties": event}
            for event in events
        ],
        "relationships": [
            {"sourceId": patient_id, "targetId": event["event_id"],
             "type": EventGraphTypes.relationship_for_record(event)}
            for event in events
        ],
    }
    filtered = apply_stencil_to_subgraph(subgraph, stencil)
    assert len(filtered["nodes"]) == len(events) + 1
    assert filtered["relationships"] == subgraph["relationships"]
    assert {node["type"] for node in filtered["nodes"]} == set(stencil["nodes"])
    for node in filtered["nodes"]:
        source = next(item for item in subgraph["nodes"] if item["id"] == node["id"])
        expected = {
            key: source["properties"][key]
            for key in stencil["nodes"][node["type"]]["properties"]
            if key in source["properties"]
        }
        assert node["properties"] == expected
