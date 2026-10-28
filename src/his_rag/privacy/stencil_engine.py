"""Project event records into the entities and links allowed by a role stencil."""

from __future__ import annotations

from typing import Any

from his_rag.graph.event_graph_types import EventGraphTypes


def _attributes_for(record: dict[str, Any], event_type: str) -> dict[str, Any]:
    if event_type == "PatientRegistrationEvent":
        values = {"patientId": record.get("patient_id")}
    elif event_type == "AppointmentEncounterEvent":
        values = {
            "appointmentId": record.get("appointment_id"),
            "scheduledDate": record.get("appointment_datetime"),
            "status": record.get("appointment_status"),
        }
    elif event_type in {"LabOrderEvent", "ImagingOrderEvent"}:
        values = {
            "orderId": record.get("event_id"),
            "orderType": record.get("event_type"),
            "status": record.get("order_status"),
        }
    elif event_type == "ObservationResultEvent":
        values = {
            "completionStatus": record.get("completion_status"),
            "completedAt": record.get("completed_at"),
        }
    else:
        values = {}
    return values


def apply_stencil(record: dict[str, Any], stencil: dict[str, Any]) -> dict[str, Any] | None:
    event_type = str(record.get("event_type", ""))
    if event_type not in stencil.get("entities", {}):
        return None

    permitted = set(stencil["entities"][event_type])
    attributes = {
        key: value for key, value in _attributes_for(record, event_type).items()
        if key in permitted and value is not None
    }
    entity_id_field = {
        "PatientRegistrationEvent": "patient_id",
        "AppointmentEncounterEvent": "appointment_id",
        "LabOrderEvent": "event_id",
        "ImagingOrderEvent": "event_id",
        "ObservationResultEvent": "event_id",
    }[event_type]
    entity_id = record.get(entity_id_field)
    relationships: list[dict[str, str]] = []
    relationship_names = set(stencil.get("relationships", []))
    event_type = record.get("event_type")
    relationship_type = EventGraphTypes.relationship_for_record(record)
    if relationship_type in relationship_names:
        if event_type == "PatientRegistrationEvent":
            source_id, target_id = record.get("patient_id"), record.get("event_id")
        elif event_type == "AppointmentEncounterEvent":
            source_id, target_id = record.get("patient_id"), record.get("appointment_id")
        elif event_type in {"LabOrderEvent", "ImagingOrderEvent"}:
            source_id, target_id = record.get("encounter_id"), record.get("event_id")
        else:
            source_id, target_id = record.get("order_id"), record.get("event_id")
        if source_id is not None and target_id is not None:
            relationships.append({
                "type": relationship_type,
                "sourceId": str(source_id),
                "targetId": str(target_id),
            })

    return {"entity": event_type, "id": entity_id, "attributes": attributes, "relationships": relationships}


def apply_stencil_to_subgraph(
    subgraph: dict[str, list[dict[str, Any]]],
    stencil: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    allowed_relationships = set(stencil.get("relationships", []))
    filtered_nodes: list[dict[str, Any]] = []
    retained_ids: set[str] = set()

    for node in subgraph.get("nodes", []):
        properties = node.get("properties", {})
        node_type = node.get("type")
        node_id = str(node.get("id", ""))
        if node_type == "Patient":
            permitted = set(stencil.get("entities", {}).get("PatientRegistrationEvent", []))
            attributes = {
                "patientId": properties["patient_id"]
            } if "patientId" in permitted and properties.get("patient_id") is not None else {}
            projected = {"entity": "Patient", "attributes": attributes}
        else:
            projected = apply_stencil(properties, stencil)
            if projected is None:
                continue

        filtered_nodes.append({
            "id": node_id,
            "type": node_type,
            "entity": projected["entity"],
            "attributes": projected["attributes"],
        })
        retained_ids.add(node_id)

    filtered_relationships = [
        dict(relationship)
        for relationship in subgraph.get("relationships", [])
        if relationship.get("type") in allowed_relationships
        and str(relationship.get("sourceId")) in retained_ids
        and str(relationship.get("targetId")) in retained_ids
    ]
    return {"nodes": filtered_nodes, "relationships": filtered_relationships}