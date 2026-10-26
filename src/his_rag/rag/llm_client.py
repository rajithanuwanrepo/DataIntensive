"""LLM client interface with a deterministic local mock."""


class MockLLMClient:
    """Return the filtered context so the pipeline works offline."""

    def generate(self, prompt: str) -> str:
        evidence = prompt.partition("Evidence:\n")[2].partition("\nQuestion:")[0].strip()
        return evidence or "Insufficient evidence."