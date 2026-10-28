"""Run the bundled single-question smoke evaluation."""

import json
from pathlib import Path

from his_rag.evaluation.evaluator import evaluate_answer
from his_rag.graph.graph_builder import build_graph
from his_rag.graph.neo4j_repository import Neo4jRepository
from his_rag.privacy.stencil_loader import load_stencil
from his_rag.rag.rag_pipeline import RAGPipeline

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    data = ROOT / "data"
    patients = json.loads((data / "synthetic" / "patients.json").read_text(encoding="utf-8"))
    events = json.loads((data / "synthetic" / "events.json").read_text(encoding="utf-8"))
    questions = json.loads((data / "evaluation" / "questions.json").read_text(encoding="utf-8"))
    expected = json.loads((data / "evaluation" / "expected_answers.json").read_text(encoding="utf-8"))
    repository = Neo4jRepository()
    try:
        pipeline = RAGPipeline(
            build_graph(patients, events, repository),
            load_stencil(ROOT / "config" / "stencils" / "outpatient_clerk.json"),
        )
        expected_by_id = {item["question_id"]: item for item in expected}
        report = []
        for item in questions:
            result = pipeline.ask(item["question"], item["patient_id"])
            metrics = evaluate_answer(result["answer"], expected_by_id[item["question_id"]]["expected_terms"])
            report.append({"question_id": item["question_id"], **metrics})
        output = ROOT / "results" / "masking_on.json"
        output.parent.mkdir(exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
    finally:
        repository.close()


if __name__ == "__main__":
    main()