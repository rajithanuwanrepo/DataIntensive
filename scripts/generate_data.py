"""Generate reproducible fictional patient and event JSON files."""

import json
from pathlib import Path

from his_rag.generator.event_generator import generate_events
from his_rag.generator.patient_generator import generate_patients

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "synthetic"


def main() -> None:
    patients = generate_patients()
    events = generate_events(patients)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, records in (("patients.json", patients), ("events.json", events)):
        (OUTPUT / name).write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(patients)} fictional patients and {len(events)} events in {OUTPUT}")


if __name__ == "__main__":
    main()