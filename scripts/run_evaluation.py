"""Save masked and unmasked answers and evidence for the evaluation questions."""

import json
from pathlib import Path
from time import sleep

from his_rag.graph.neo4j_repository import Neo4jRepository
from his_rag.privacy.stencil_loader import load_stencil
from his_rag.rag.llm_client import create_llm_client
from his_rag.rag.rag_pipeline import RAGPipeline

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    data = ROOT / "data"
    questions = json.loads((data / "evaluation" / "questions.json").read_text(encoding="utf-8"))
    llm = create_llm_client()
    repository = Neo4jRepository()
    try:
        pipeline = RAGPipeline(
            repository,
            load_stencil(ROOT / "config" / "stencils" / "outpatient_clerk.json"),
            llm=llm,
        )
        results_dir = ROOT / "results"
        results_dir.mkdir(exist_ok=True)
        for mode, mask in (("masking_on", True), ("masking_off", False)):
            report = []
            evidence_report = []
            for item in questions:
                result = pipeline.ask(item["question"], item["patient_id"], mask=mask)
                report.append(f'{item["question_id"]}\n{result["answer"]}')
                evidence_report.append({
                    "question_id": item["question_id"],
                    "evidence": result["evidence"],
                })
            output = results_dir / f"{mode}.txt"
            payload = "\n\n".join(report)
            output.write_text(payload + "\n" if report else "", encoding="utf-8")
            (results_dir / f"{mode}.json").write_text(
                json.dumps(evidence_report, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print("successfully wrote results to", output and results_dir / f"{mode}.json")
            # print(f"{output.name}\n{payload}")
            if mask:
                print("Starting the unmasked run in 5 seconds.", flush=True)
                sleep(5)
    finally:
        repository.close()


if __name__ == "__main__":
    main()
