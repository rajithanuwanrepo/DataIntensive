from datetime import datetime, timedelta

from his_rag.generator.event_generator import generate_events
from his_rag.generator.patient_generator import generate_patients


def test_patient_generation_is_deterministic_and_fictional() -> None:
    assert generate_patients(2) == generate_patients(2)
    assert len(generate_events(generate_patients(2))) == 12


def test_events_form_a_linked_patient_workflow() -> None:
    events = generate_events(generate_patients(1))
    assert [event["event_type"] for event in events] == [
        "PatientRegistrationEvent",
        "AppointmentEncounterEvent",
        "LabOrderEvent",
        "ImagingOrderEvent",
        "ObservationResultEvent",
        "AppointmentEncounterEvent",
    ]
    assert [event["related_event_id"] for event in events] == [
        "",
        events[0]["event_id"],
        events[1]["event_id"],
        events[1]["event_id"],
        events[2]["event_id"],
        events[4]["event_id"],
    ]
    assert all("generated_datetime" in event and "status" not in event for event in events)
    assert events[4]["order_id"] == events[2]["event_id"]
    assert "modality" not in events[2]
    assert events[3]["modality"] == "x_ray"
    encounter_events = events[1:]
    assert len({event["encounter_id"] for event in encounter_events}) == 1
    assert events[0]["encounter_id"] is None
    assert events[1]["appointment_status"] == "completed"
    assert events[1]["appointment_datetime"] == events[1]["generated_datetime"]
    assert events[5]["appointment_status"] == "pending"
    follow_up_generated = datetime.fromisoformat(events[5]["generated_datetime"].replace("Z", "+00:00"))
    follow_up_scheduled = datetime.fromisoformat(events[5]["appointment_datetime"].replace("Z", "+00:00"))
    assert follow_up_scheduled - follow_up_generated == timedelta(days=7)
    assert events[5]["appointment_datetime"] > events[1]["appointment_datetime"]


def test_negative_patient_count_is_rejected() -> None:
    try:
        generate_patients(-1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative counts should be rejected")
