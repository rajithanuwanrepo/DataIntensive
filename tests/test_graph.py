from his_rag.graph.graph_builder import build_graph
from his_rag.graph.networkx_repository import NetworkXRepository


def test_graph_connects_events_to_patients() -> None:
    repository = build_graph(
        [{"patient_id": "P-1"}],
        [{"event_id": "E-1", "patient_id": "P-1", "event_type": "visit"}],
        NetworkXRepository(),
    )
    assert len(repository.events_for_patient("P-1")) == 1
    assert repository.events_for_patient("P-2") == []