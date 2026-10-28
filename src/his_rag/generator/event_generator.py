"""Fictional event generation helpers."""

from __future__ import annotations

from his_rag.models.events import (
    AppointmentEncounterEvent,
    ImagingOrderEvent,
    LabOrderEvent,
    ObservationResultEvent,
    PatientRegistrationEvent,
)


def generate_events(patients: list[dict[str, str]]) -> list[dict[str, str]]:
    """Create a linked registration-to-follow-up timeline per patient."""
    events: list[dict[str, str]] = []
    for patient_index, patient in enumerate(patients):
        patient_id = patient["patient_id"]
        prefix = f"E-{2000 + patient_index}"
        event_ids = [f"{prefix}-{step:02d}" for step in range(1, 7)]
        encounter_id = f"ENC-{patient_index + 1:05d}"
        day = patient_index % 28 + 1
        times = [f"2025-01-{day:02d}T{hour:02d}:00:00Z" for hour in range(9, 15)]

        registration = PatientRegistrationEvent(
            event_id=event_ids[0], patient_id=patient_id, event_type=PatientRegistrationEvent.__name__,
            occurred_at=times[0], department="Patient Access",
            actor_id="STAFF-REG-01", related_event_id="", description="Fictional outpatient registration.",
            encounter_id=None,
            registration_type="outpatient", registration_source="scheduled_referral",
            consent_status="documented", external_record_id=f"EXT-{patient_index + 1:05d}",
        )
        encounter = AppointmentEncounterEvent(
            event_id=event_ids[1], patient_id=patient_id, event_type=AppointmentEncounterEvent.__name__,
            occurred_at=times[1], department="Family Medicine",
            actor_id="PROV-001", related_event_id=event_ids[0],
            encounter_id=encounter_id,
            description="Fictional initial outpatient assessment.", encounter_class="outpatient",
            appointment_id=f"APT-{patient_index + 1:05d}", appointment_status="completed",
            appointment_datetime=times[1], chief_complaint="Routine follow-up",
            location="Clinic Room 4", disposition="testing_ordered",
        )
        lab_order = LabOrderEvent(
            event_id=event_ids[2], patient_id=patient_id, event_type=LabOrderEvent.__name__,
            occurred_at=times[2], department="Laboratory",
            actor_id="PROV-001", related_event_id=event_ids[1],
            encounter_id=encounter_id,
            description="Fictional complete blood count order.", order_code="CBC",
            code_system="LOCAL", order_name="Complete blood count", specimen="whole_blood",
            collection_method="venipuncture", fasting_required=False,
            order_status="ordered",
            priority="routine", ordering_provider_id="PROV-001",
        )
        imaging_order = ImagingOrderEvent(
            event_id=event_ids[3], patient_id=patient_id, event_type=ImagingOrderEvent.__name__,
            occurred_at=times[3], department="Radiology",
            actor_id="PROV-001", related_event_id=event_ids[1],
            encounter_id=encounter_id,
            description="Fictional chest imaging order.", order_code="XR-CHEST-2V",
            code_system="LOCAL", order_name="Chest radiograph, two views", modality="x_ray",
            body_site="chest", laterality="not_applicable", contrast="none",
            order_status="ordered",
            priority="routine", ordering_provider_id="PROV-001",
        )
        result = ObservationResultEvent(
            event_id=event_ids[4], patient_id=patient_id, event_type=ObservationResultEvent.__name__,
            occurred_at=times[4], department="Laboratory",
            actor_id="LAB-TECH-01", related_event_id=event_ids[2],
            encounter_id=encounter_id,
            description="Fictional laboratory result.", order_id=event_ids[2],
            completion_status="completed", completed_at=times[4],
            result_code="HGB", result_value="13.8", unit="g/dL",
            reference_range="12.0-16.0", interpretation="within_reference_range",
            abnormal_flag="false",
        )
        follow_up = AppointmentEncounterEvent(
            event_id=event_ids[5], patient_id=patient_id, event_type=AppointmentEncounterEvent.__name__,
            occurred_at=times[5], department="Family Medicine",
            actor_id="STAFF-SCHED-01", related_event_id=event_ids[4],
            encounter_id=encounter_id,
            description="Fictional appointment to review results.", encounter_class="appointment",
            appointment_id=f"APT-{patient_index + 1:05d}-F", appointment_status="pending",
            appointment_datetime=times[5], chief_complaint="Review test results",
            location="Clinic Room 4", disposition="planned",
        )
        events.extend(
            event.to_dict()
            for event in (registration, encounter, lab_order, imaging_order, result, follow_up)
        )
    return events