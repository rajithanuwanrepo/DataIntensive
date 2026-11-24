"""Ask questions using the Neo4j-backed privacy-aware RAG pipeline."""

import argparse
import json
from pathlib import Path

from his_rag.graph.neo4j_repository import Neo4jRepository
from his_rag.privacy.stencil_loader import load_stencil
from his_rag.rag.llm_client import create_llm_client
from his_rag.rag.rag_pipeline import RAGPipeline

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("question", nargs="?")
    parser.add_argument("--patient-id", default="P-1000")
    args = parser.parse_args()
    stencil = load_stencil(ROOT / "config" / "stencils" / "outpatient_clerk.json")
    llm = create_llm_client()
    repository = Neo4jRepository()

    try:
        pipeline = RAGPipeline(repository, stencil, llm=llm)
        if args.question:
            result = pipeline.ask(args.question, args.patient_id)
            print(json.dumps(result, indent=2))
            return

        print("RAG question session. Type 'exit' or 'quit' to finish.")
        while True:
            try:
                question = input("Question: ").strip()
            except EOFError:
                print()
                break

            if question.lower() in {"exit", "quit"}:
                break
            if not question:
                continue

            result = pipeline.ask(question, args.patient_id)
            print("************************************************************************")
            print(result["answer"])
    finally:
        repository.close()


if __name__ == "__main__":
    main()
