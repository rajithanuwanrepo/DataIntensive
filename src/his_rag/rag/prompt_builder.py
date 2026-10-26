"""Build a grounded prompt from a question and retrieved context."""


def build_prompt(question: str, context: str) -> str:
    return f"Answer using only the evidence below. If it is insufficient, say so.\nEvidence:\n{context}\nQuestion: {question}"