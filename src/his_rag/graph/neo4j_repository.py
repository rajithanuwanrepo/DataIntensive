"""Neo4j-backed persistent graph repository."""

from __future__ import annotations

from his_rag.graph.event_graph_types import EventGraphTypes


class Neo4jRepository:
    """Store patient and event records in a Neo4j database."""

    def __init__(self) -> None:
        try:
            from neo4j import GraphDatabase
        except ImportError as error:
            raise RuntimeError("Install the project dependencies with pip install -e .") from error

        self.database = "his"
        self.driver = GraphDatabase.driver(
            "neo4j://127.0.0.1:7687",
            auth=("neo4j", "12345678"),
        )
        self.driver.verify_connectivity()
        with self.driver.session(database=self.database) as session:
            session.run(
                "CREATE CONSTRAINT patient_id_unique IF NOT EXISTS "
                "FOR (p:Patient) REQUIRE p.patient_id IS UNIQUE"
            ).consume()
            session.run(
                "CREATE CONSTRAINT event_id_unique IF NOT EXISTS "
                "FOR (e:Event) REQUIRE e.event_id IS UNIQUE"
            ).consume()

    def add_patient(self, patient: dict[str, str]) -> None:
        with self.driver.session(database=self.database) as session:
            session.run(
                "MERGE (p:Patient {patient_id: $patient_id}) "
                "SET p += $properties",
                patient_id=patient["patient_id"],
                properties=patient,
            ).consume()

    def add_event(self, event: dict[str, str]) -> None:
        graph_type = event["event_type"]
        relationship_type = EventGraphTypes.relationship_for_record(event)
        with self.driver.session(database=self.database) as session:
            session.run(
                f"MERGE (e:Event {{event_id: $event_id}}) "
                f"SET e += $properties SET e:{graph_type}",
                event_id=event["event_id"],
                properties=event,
            ).consume()

            session.run(
                "MATCH (source:Patient {patient_id: $patient_id}) "
                "MATCH (target:Event {event_id: $event_id}) "
                f"MERGE (source)-[:{relationship_type}]->(target)",
                patient_id=event["patient_id"],
                event_id=event["event_id"],
            ).consume()

    def subgraph_for_patient(self, patient_id: str) -> dict[str, list[dict[str, object]]]:
        relationship_types = list(EventGraphTypes.EVANT_GRAPH_RELATIONSHIPS.values())
        with self.driver.session(database=self.database) as session:
            result = session.run(
                "MATCH (patient:Patient {patient_id: $patient_id})-[link]->(event:Event) "
                "WHERE type(link) IN $relationship_types "
                "RETURN [{labels: labels(patient), properties: properties(patient)}, "
                "{labels: labels(event), properties: properties(event)}] AS nodes, "
                "[{type: type(link), "
                "sourceId: coalesce(startNode(link).patient_id, startNode(link).event_id), "
                "targetId: coalesce(endNode(link).patient_id, endNode(link).event_id)}] AS relationships",
                patient_id=patient_id,
                relationship_types=relationship_types,
            )

            nodes_by_id: dict[str, dict[str, object]] = {}
            relationships_by_key: dict[tuple[str, str, str], dict[str, object]] = {}
            for record in result:
                for node in record["nodes"]:
                    properties = dict(node["properties"])
                    labels = set(node["labels"])
                    node_id = properties.get("patient_id") or properties.get("event_id")
                    if node_id is None:
                        continue
                    node_type = "Patient" if "Patient" in labels else next(
                        (label for label in EventGraphTypes.EVANT_GRAPH_RELATIONSHIPS if label in labels),
                        "Event",
                    )
                    nodes_by_id[str(node_id)] = {
                        "id": str(node_id),
                        "type": node_type,
                        "properties": properties,
                    }
                for relationship in record["relationships"]:
                    edge = dict(relationship)
                    key = (str(edge["sourceId"]), str(edge["type"]), str(edge["targetId"]))
                    relationships_by_key[key] = edge

            return {
                "nodes": list(nodes_by_id.values()),
                "relationships": list(relationships_by_key.values()),
            }

    def events_for_patient(self, patient_id: str) -> list[dict[str, str]]:
        subgraph = self.subgraph_for_patient(patient_id)
        return [
            node["properties"]
            for node in subgraph["nodes"]
            if node["type"] != "Patient"
        ]

    def close(self) -> None:
        self.driver.close()