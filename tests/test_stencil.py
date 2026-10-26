from his_rag.privacy.stencil_engine import apply_stencil


def test_stencil_projects_only_permitted_entity_attributes_and_relationships() -> None:
    record = {
        "event_id": "E-1", "patient_id": "P-1", "event_type": "lab_order",
        "encounter_id": "ENC-1", "order_status": "ordered", "order_name": "CBC",
        "ordering_provider_id": "PROV-1",
    }
    stencil = {
        "entities": {"Order": ["orderId", "orderType", "status"]},
        "relationships": ["hasLabOrderEvent"],
    }
    projected = apply_stencil(record, stencil)
    assert projected == {
        "entity": "Order",
        "id": "E-1",
        "attributes": {"orderId": "E-1", "orderType": "lab_order", "status": "ordered"},
        "relationships": [{"type": "hasLabOrderEvent", "sourceId": "ENC-1", "targetId": "E-1"}],
    }


def test_stencil_omits_unpermitted_relationships_and_unknown_event_types() -> None:
    stencil = {"entities": {"Patient": ["patientId"]}, "relationships": []}
    projected = apply_stencil({"event_type": "patient_registration", "patient_id": "P-1"}, stencil)
    assert projected["attributes"] == {"patientId": "P-1"}
    assert projected["relationships"] == []
    assert apply_stencil({"event_type": "unknown"}, stencil) is None