"""Tests for LLM client."""

from rental_application.llm_client import LocalLLMClient


def test_local_llm_client_initialization():
    """Test LocalLLMClient initialization."""
    client = LocalLLMClient(
        host="localhost:11434",
        model="mistral",
        timeout=30,
    )
    assert client.host == "localhost:11434"
    assert client.model == "mistral"
    assert client.timeout == 30
    assert client.base_url == "http://localhost:11434"


def test_local_llm_client_availability_check():
    """Test LLM availability check (will fail if Ollama not running)."""
    client = LocalLLMClient()
    # This will return False if Ollama is not running, which is expected in tests
    available = client.is_available()
    # We just check it returns a boolean
    assert isinstance(available, bool)


def test_custom_host_and_model():
    """Test custom LLM host and model."""
    client = LocalLLMClient(host="192.168.1.100:11434", model="neural-chat")
    assert client.base_url == "http://192.168.1.100:11434"
    assert client.model == "neural-chat"
