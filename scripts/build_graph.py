"""Build the in-memory graph from bundled synthetic JSON."""

import json
from pathlib import Path

from his_rag.graph.graph_builder import build_graph
from his_rag.graph.networkx_repository import NetworkXRepository

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    data = ROOT / "data" / "synthetic"
    patients = json.loads((data / "patients.json").read_text(encoding="utf-8"))
    events = json.loads((data / "events.json").read_text(encoding="utf-8"))
    graph = build_graph(patients, events, NetworkXRepository())
    print(f"Loaded {len(graph.patients)} patients and {len(graph.events)} events")


if __name__ == "__main__":
    main()