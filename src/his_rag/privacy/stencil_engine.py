"""Project event records into the entities and links allowed by a role stencil."""

from __future__ import annotations

from typing import Any


EVENT_ENTITY = {
    "patient_registration": "Patient",
    "encounter": "Appointment",
    "follow_up_appointment": "Appointment",
    "lab_order": "Order",
    "imaging_order": "Order",
    "observation_result": "Result",
}


def _attributes_for(record: dict[str, Any], entity: str) -> dict[str, Any]:
    if entity == "Patient":
        values = {"patientId": record.get("patient_id")}
    elif entity == "Appointment":
        values = {
            "appointmentId": record.get("appointment_id"),
            "scheduledDate": record.get("appointment_datetime"),
            "status": record.get("appointment_status"),
        }
    elif entity == "Order":
        values = {
            "orderId": record.get("event_id"),
            "orderType": record.get("event_type"),
            "status": record.get("order_status"),
        }
    else:
        values = {
            "completionStatus": record.get("completion_status"),
            "completedAt": record.get("completed_at"),
        }
    return values


def apply_stencil(record: dict[str, Any], stencil: dict[str, Any]) -> dict[str, Any] | None:
    entity = EVENT_ENTITY.get(str(record.get("event_type", "")))
    if entity is None or entity not in stencil.get("entities", {}):
        return None

    permitted = set(stencil["entities"][entity])
    attributes = {
        key: value
        for key, value in _attributes_for(record, entity).items()
        if key in permitted and value is not None
    }
    entity_id_field = {
        "Patient": "patient_id",
        "Appointment": "appointment_id",
        "Order": "event_id",
        "Result": "event_id",
    }[entity]
    entity_id = record.get(entity_id_field)
    relationships: list[dict[str, str]] = []
    relationship_names = set(stencil.get("relationships", []))

    event_type = record.get("event_type")
    if event_type == "patient_registration" and "hasPatientRegistrationEvent" in relationship_names:
        relationships.append({
            "type": "hasPatientRegistrationEvent",
            "sourceId": str(record["patient_id"]),
            "targetId": str(record["event_id"]),
        })
    elif event_type in {"encounter", "follow_up_appointment"} and "hasAppointmentEncounterEvent" in relationship_names:
        relationships.append({
            "type": "hasAppointmentEncounterEvent",
            "sourceId": str(record["patient_id"]),
            "targetId": str(record["appointment_id"]),
        })
    elif event_type == "lab_order" and "hasLabOrderEvent" in relationship_names:
        relationships.append({
            "type": "hasLabOrderEvent",
            "sourceId": str(record["encounter_id"]),
            "targetId": str(record["event_id"]),
        })
    elif event_type == "imaging_order" and "hasImagingOrderEvent" in relationship_names:
        relationships.append({
            "type": "hasImagingOrderEvent",
            "sourceId": str(record["encounter_id"]),
            "targetId": str(record["event_id"]),
        })
    elif event_type == "observation_result" and "hasObservationResultEvent" in relationship_names:
        relationships.append({
            "type": "hasObservationResultEvent",
            "sourceId": str(record["order_id"]),
            "targetId": str(record["event_id"]),
        })

    return {"entity": entity, "id": entity_id, "attributes": attributes, "relationships": relationships}