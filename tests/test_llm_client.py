import io
import json
from unittest.mock import MagicMock
from urllib.error import HTTPError, URLError

import pytest

from his_rag.rag import llm_client
from his_rag.rag.llm_client import MockLLMClient, OllamaLLMClient, create_llm_client


def stub_response(monkeypatch, payload):
    transport = MagicMock()
    transport.return_value.__enter__.return_value = io.BytesIO(json.dumps(payload).encode())
    monkeypatch.setattr(llm_client, "urlopen", transport)
    return transport


def test_ollama_posts_prompt_and_reads_answer(monkeypatch):
    transport = stub_response(monkeypatch, {"response": "The appointment is next week.", "done": True})
    client = OllamaLLMClient("llama3.2:3b", base_url="http://localhost:11434/")
    assert client.generate("Filtered evidence and question") == "The appointment is next week."
    request = transport.call_args.args[0]
    payload = json.loads(request.data)
    assert request.full_url == "http://localhost:11434/api/generate"
    assert request.get_method() == "POST"
    assert request.get_header("Content-type") == "application/json"
    assert payload["model"] == "llama3.2:3b"
    assert payload["prompt"] == "Filtered evidence and question"
    assert payload["stream"] is False
    assert transport.call_args.kwargs["timeout"] == 180


@pytest.mark.parametrize("error", [URLError("connection refused"), TimeoutError()])
def test_ollama_connection_errors_explain_how_to_start_server(monkeypatch, error):
    monkeypatch.setattr(llm_client, "urlopen", MagicMock(side_effect=error))
    with pytest.raises(RuntimeError, match="ollama serve"):
        OllamaLLMClient("llama3.2:3b").generate("question")


def test_ollama_http_error_includes_model_error(monkeypatch):
    error = HTTPError("http://localhost:11434/api/generate", 404, "Not Found", {},
                      io.BytesIO(b'{"error": "model not found"}'))
    monkeypatch.setattr(llm_client, "urlopen", MagicMock(side_effect=error))
    with pytest.raises(RuntimeError, match="HTTP 404.*model not found"):
        OllamaLLMClient("missing-model").generate("question")


@pytest.mark.parametrize("payload, message", [
    ({"error": "model failed to load"}, "model failed to load"),
    ({"response": ""}, "no answer text"),
    ({"response": "  "}, "no answer text"),
    ({}, "no answer text"),
    ([], "invalid response object"),
])
def test_ollama_rejects_unsuccessful_responses(monkeypatch, payload, message):
    stub_response(monkeypatch, payload)
    with pytest.raises(RuntimeError, match=message):
        OllamaLLMClient("llama3.2:3b").generate("question")


def test_ollama_rejects_invalid_json(monkeypatch):
    transport = MagicMock()
    transport.return_value.__enter__.return_value = io.BytesIO(b'not json')
    monkeypatch.setattr(llm_client, "urlopen", transport)
    with pytest.raises(RuntimeError, match="invalid JSON"):
        OllamaLLMClient("llama3.2:3b").generate("question")


def test_factory_defaults_to_mock_without_ollama_configuration(monkeypatch):
    monkeypatch.delenv("HIS_RAG_LLM_MODE", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    assert isinstance(create_llm_client(), MockLLMClient)


def test_factory_uses_exported_ollama_configuration(monkeypatch):
    monkeypatch.setenv("HIS_RAG_LLM_MODE", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2:3b")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    client = create_llm_client()
    assert isinstance(client, OllamaLLMClient)
    assert client.model == "llama3.2:3b"
    assert client.base_url == "http://127.0.0.1:11434"


def test_factory_rejects_missing_model(monkeypatch):
    monkeypatch.setenv("HIS_RAG_LLM_MODE", "ollama")
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    with pytest.raises(ValueError, match="OLLAMA_MODEL"):
        create_llm_client()


def test_factory_rejects_unknown_mode(monkeypatch):
    monkeypatch.setenv("HIS_RAG_LLM_MODE", "unknown")
    with pytest.raises(ValueError, match="mock.*ollama"):
        create_llm_client()
