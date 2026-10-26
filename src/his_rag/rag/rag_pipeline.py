"""End-to-end privacy-filtered retrieval and mock generation."""

from __future__ import annotations

from his_rag.graph.graph_repository import GraphRepository
from his_rag.rag.context_builder import build_context
from his_rag.rag.llm_client import MockLLMClient
from his_rag.rag.prompt_builder import build_prompt
from his_rag.retrieval.evidence_retriever import retrieve_evidence
from his_rag.retrieval.query_analyzer import analyze_query


class RAGPipeline:
    def __init__(self, repository: GraphRepository, stencil: dict[str, object], llm: MockLLMClient | None = None) -> None:
        self.repository = repository
        self.stencil = stencil
        self.llm = llm or MockLLMClient()

    def ask(self, question: str, patient_id: str | None = None) -> dict[str, object]:
        query = analyze_query(question)
        selected_patient = patient_id or query["patient_id"]
        evidence = retrieve_evidence(selected_patient, self.repository)
        context = build_context(evidence, self.stencil)
        answer = self.llm.generate(build_prompt(question, context))
        return {"answer": answer, "evidence": evidence, "context": context}