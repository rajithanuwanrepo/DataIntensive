"""Lightweight event model used by the JSON-based starter."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


@dataclass(frozen=True)
class Event:
    event_id: str
    patient_id: str
    event_type: str
    occurred_at: str
    department: str
    actor_id: str
    related_event_id: str
    description: str
    encounter_id: str | None

    def to_dict(self) -> dict[str, str | None]:
        return asdict(self)


@dataclass(frozen=True)
class PatientRegistrationEvent(Event):
    registration_type: str
    registration_source: str
    consent_status: str
    external_record_id: str


@dataclass(frozen=True)
class AppointmentEncounterEvent(Event):
    encounter_class: str
    appointment_id: str
    appointment_status: Literal["pending", "scheduled", "confirmed", "checked_in", "completed", "cancelled", "no_show"]
    appointment_datetime: str
    chief_complaint: str
    location: str
    disposition: str


@dataclass(frozen=True)
class LabOrderEvent(Event):
    order_code: str
    code_system: str
    order_name: str
    specimen: str
    collection_method: str
    fasting_required: bool
    order_status: Literal["ordered", "in_progress", "completed", "cancelled"]
    priority: str
    ordering_provider_id: str


@dataclass(frozen=True)
class ImagingOrderEvent(Event):
    order_code: str
    code_system: str
    order_name: str
    modality: str
    body_site: str
    laterality: str
    contrast: str
    order_status: Literal["ordered", "in_progress", "completed", "cancelled"]
    priority: str
    ordering_provider_id: str


@dataclass(frozen=True)
class ObservationResultEvent(Event):
    order_id: str
    completion_status: Literal["pending", "completed", "cancelled"]
    completed_at: str
    result_code: str
    result_value: str
    unit: str
    reference_range: str
    interpretation: str
    abnormal_flag: str