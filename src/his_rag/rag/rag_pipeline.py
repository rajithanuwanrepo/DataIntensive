"""End-to-end privacy-filtered retrieval and answer generation."""

from __future__ import annotations

import json

from his_rag.graph.graph_repository import GraphRepository
from his_rag.privacy.stencil_engine import apply_stencil_to_subgraph
from his_rag.rag.context_builder import build_context
from his_rag.rag.llm_client import LLMClient, MockLLMClient
from his_rag.rag.prompt_builder import build_prompt
from his_rag.retrieval.evidence_retriever import retrieve_evidence
from his_rag.retrieval.query_analyzer import analyze_query


class RAGPipeline:
    def __init__(self, repository: GraphRepository, stencil: dict[str, object], llm: LLMClient | None = None) -> None:
        self.repository = repository
        self.stencil = stencil
        self.llm = llm or MockLLMClient()

    def ask(
        self, question: str, patient_id: str | None = None, *, mask: bool = True,
    ) -> dict[str, object]:
        query = analyze_query(question)
        selected_patient = patient_id or query["patient_id"]
        raw_evidence = retrieve_evidence(selected_patient, self.repository)
        if mask is False:
            evidence = raw_evidence
            print("Unmasked evidence subgraph:")
        else:
            evidence = apply_stencil_to_subgraph(raw_evidence, self.stencil)
            print("Filtered evidence subgraph after masking:")
        context = build_context(evidence)
        print(json.dumps(evidence, indent=2, ensure_ascii=False, default=str))
        answer = self.llm.generate(build_prompt(question, context))
        return {"answer": answer, "evidence": evidence, "context": context}
