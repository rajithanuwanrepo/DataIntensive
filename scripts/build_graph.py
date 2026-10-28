"""Load bundled synthetic JSON into Neo4j."""

import json
from pathlib import Path

from his_rag.graph.graph_builder import build_graph
from his_rag.graph.neo4j_repository import Neo4jRepository

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    data = ROOT / "data" / "synthetic"
    patients = json.loads((data / "patients.json").read_text(encoding="utf-8"))
    events = json.loads((data / "events.json").read_text(encoding="utf-8"))
    repository = Neo4jRepository()
    try:
        build_graph(patients, events, repository)
        print(f"Loaded {len(patients)} patients and {len(events)} events into Neo4j")
    finally:
        repository.close()


if __name__ == "__main__":
    main()