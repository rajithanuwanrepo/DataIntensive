"""Canonical event labels and order for a synthetic outpatient workflow."""

PATIENT_REGISTRATION = "patient_registration"
ENCOUNTER = "encounter"
LAB_ORDER = "lab_order"
IMAGING_ORDER = "imaging_order"
OBSERVATION_RESULT = "observation_result"
FOLLOW_UP_APPOINTMENT = "follow_up_appointment"

EVENT_TYPES = (
	PATIENT_REGISTRATION,
	ENCOUNTER,
	LAB_ORDER,
	IMAGING_ORDER,
	OBSERVATION_RESULT,
	FOLLOW_UP_APPOINTMENT,
)

OUTPATIENT_WORKFLOW = EVENT_TYPES

