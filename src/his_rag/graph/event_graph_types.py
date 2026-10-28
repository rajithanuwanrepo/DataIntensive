"""Shared event-to-graph relationship definitions."""

from __future__ import annotations

EVANT_GRAPH_RELATIONSHIPS = {
    "AppointmentEncounterEvent": "hasAppointmentEncounterEvent",
    "ImagingOrderEvent": "hasImagingOrderEvent",
    "LabOrderEvent": "hasLabOrderEvent",
    "ObservationResultEvent": "hasObservationResultEvent",
    "PatientRegistrationEvent": "hasPatientRegistrationEvent",
}

class EventGraphTypes:
    EVANT_GRAPH_RELATIONSHIPS = EVANT_GRAPH_RELATIONSHIPS

    @classmethod
    def relationship_for_record(cls, event: dict[str, object]) -> str:
        event_type = str(event.get("event_type", ""))
        try:
            return cls.EVANT_GRAPH_RELATIONSHIPS[event_type]
        except KeyError as error:
            raise ValueError(f"Unsupported event type: {event_type}") from error