from his_rag.graph.event_graph_types import EventGraphTypes
from his_rag.privacy.stencil_engine import apply_stencil, apply_stencil_to_subgraph


def test_event_graph_types_map_all_supported_records() -> None:
    assert EventGraphTypes.EVANT_GRAPH_RELATIONSHIPS == {
        "AppointmentEncounterEvent": "hasAppointmentEncounterEvent",
        "ImagingOrderEvent": "hasImagingOrderEvent",
        "LabOrderEvent": "hasLabOrderEvent",
        "ObservationResultEvent": "hasObservationResultEvent",
        "PatientRegistrationEvent": "hasPatientRegistrationEvent",
    }
    assert EventGraphTypes.relationship_for_record({"event_type": "LabOrderEvent"}) == "hasLabOrderEvent"


def test_stencil_filters_subgraph_nodes_and_relationships_as_a_whole() -> None:
    subgraph = {
        "nodes": [
            {"id": "P-1", "type": "Patient", "properties": {"patient_id": "P-1", "name": "Private"}},
            {
                "id": "E-1",
                "type": "PatientRegistrationEvent",
                "properties": {
                    "event_id": "E-1",
                    "patient_id": "P-1",
                    "event_type": "PatientRegistrationEvent",
                    "name": "Private",
                },
            },
        ],
        "relationships": [
            {"type": "hasPatientRegistrationEvent", "sourceId": "P-1", "targetId": "E-1"},
            {"type": "hasPrivateRelation", "sourceId": "P-1", "targetId": "E-1"},
        ],
    }
    stencil = {
        "entities": {"PatientRegistrationEvent": ["patientId"]},
        "relationships": ["hasPatientRegistrationEvent"],
    }

    filtered = apply_stencil_to_subgraph(subgraph, stencil)

    assert filtered["relationships"] == [
        {"type": "hasPatientRegistrationEvent", "sourceId": "P-1", "targetId": "E-1"}
    ]
    assert all("Private" not in str(node) for node in filtered["nodes"])


def test_stencil_projects_only_permitted_entity_attributes_and_relationships() -> None:
    record = {
        "event_id": "E-1", "patient_id": "P-1", "event_type": "LabOrderEvent",
        "encounter_id": "ENC-1", "order_status": "ordered", "order_name": "CBC",
        "ordering_provider_id": "PROV-1",
    }
    stencil = {
        "entities": {"LabOrderEvent": ["orderId", "orderType", "status"]},
        "relationships": ["hasLabOrderEvent"],
    }
    projected = apply_stencil(record, stencil)
    assert projected == {
        "entity": "LabOrderEvent",
        "id": "E-1",
        "attributes": {"orderId": "E-1", "orderType": "LabOrderEvent", "status": "ordered"},
        "relationships": [{"type": "hasLabOrderEvent", "sourceId": "ENC-1", "targetId": "E-1"}],
    }


def test_stencil_omits_unpermitted_relationships_and_unknown_event_types() -> None:
    stencil = {"entities": {"PatientRegistrationEvent": ["patientId"]}, "relationships": []}
    projected = apply_stencil({"event_type": "PatientRegistrationEvent", "patient_id": "P-1"}, stencil)
    assert projected["attributes"] == {"patientId": "P-1"}
    assert projected["relationships"] == []
    assert apply_stencil({"event_type": "unknown"}, stencil) is None