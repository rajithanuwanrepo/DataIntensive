"""Ask the offline privacy-aware RAG demo."""

import argparse
import json
from pathlib import Path

from his_rag.graph.graph_builder import build_graph
from his_rag.graph.networkx_repository import NetworkXRepository
from his_rag.privacy.stencil_loader import load_stencil
from his_rag.rag.rag_pipeline import RAGPipeline

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("question", nargs="?", default="What happened during the outpatient visit?")
    parser.add_argument("--patient-id", default="P-1001")
    args = parser.parse_args()
    data = ROOT / "data" / "synthetic"
    patients = json.loads((data / "patients.json").read_text(encoding="utf-8"))
    events = json.loads((data / "events.json").read_text(encoding="utf-8"))
    repository = build_graph(patients, events, NetworkXRepository())
    stencil = load_stencil(ROOT / "config" / "stencils" / "outpatient_clerk.json")
    print(json.dumps(RAGPipeline(repository, stencil).ask(args.question, args.patient_id), indent=2))


if __name__ == "__main__":
    main()