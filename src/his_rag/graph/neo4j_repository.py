"""Optional Neo4j adapter connection point."""


class Neo4jRepository:
    """Raises a helpful error until a Neo4j driver-backed adapter is configured."""

    def __init__(self, *_: object, **__: object) -> None:
        try:
            import neo4j  # noqa: F401
        except ImportError as error:
            raise RuntimeError("Install the optional dependency with pip install -e '.[neo4j]'") from error
        raise NotImplementedError("Configure Neo4j connection and persistence before selecting this backend.")