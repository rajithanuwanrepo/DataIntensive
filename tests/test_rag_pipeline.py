from his_rag.graph.graph_builder import build_graph
from his_rag.graph.networkx_repository import NetworkXRepository
from his_rag.rag.rag_pipeline import RAGPipeline


def test_pipeline_only_exposes_stencil_allowed_fields() -> None:
    repository = build_graph(
        [{"patient_id": "P-1"}],
        [{"event_id": "E-1", "patient_id": "P-1", "event_type": "patient_registration", "name": "Private"}],
        NetworkXRepository(),
    )
    stencil = {"entities": {"Patient": ["patientId"]}, "relationships": []}
    result = RAGPipeline(repository, stencil).ask("P-1")
    assert "P-1" in result["answer"]
    assert "Private" not in result["context"]