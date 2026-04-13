"""LLM client for interacting with local and remote models."""

import json
from abc import ABC, abstractmethod
from typing import Optional

import requests

from rental_application.config import config


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate text from a prompt.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0 to 1.0)

        Returns:
            Generated text
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM service is available.

        Returns:
            True if service is available
        """
        pass


class LocalLLMClient(LLMClient):
    """Client for local LLMs via Ollama."""

    def __init__(
        self,
        host: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        """Initialize Ollama client.

        Args:
            host: Ollama server address (e.g., localhost:11434)
            model: Model name (e.g., mistral, neural-chat)
            timeout: Request timeout in seconds
        """
        self.host = host or config.ollama_host
        self.model = model or config.ollama_model
        self.timeout = timeout or config.timeout_seconds
        self.base_url = f"http://{self.host}"

    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate text using Ollama.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature

        Returns:
            Generated text

        Raises:
            RuntimeError: If API call fails
        """
        if not self.is_available():
            raise RuntimeError(
                f"Ollama not available at {self.base_url}. "
                "Make sure Ollama is running: ollama serve"
            )

        endpoint = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False,
        }

        try:
            response = requests.post(
                endpoint,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except requests.exceptions.Timeout:
            raise RuntimeError(f"Ollama request timed out after {self.timeout}s")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API error: {e}")

    def is_available(self) -> bool:
        """Check if Ollama is running.

        Returns:
            True if Ollama is accessible
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except (requests.exceptions.RequestException, Exception):
            return False

    def generate_json(self, prompt: str, temperature: float = 0.3) -> dict:
        """Generate JSON output from a prompt.

        Args:
            prompt: Input prompt (should ask for JSON output)
            temperature: Lower temperature for more deterministic output

        Returns:
            Parsed JSON dictionary

        Raises:
            RuntimeError: If generation fails or output isn't valid JSON
        """
        text = self.generate(prompt, temperature=temperature)

        # Try to extract JSON from the response
        try:
            # First try direct JSON parsing
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            start_idx = text.find("{")
            end_idx = text.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                try:
                    return json.loads(text[start_idx:end_idx])
                except json.JSONDecodeError:
                    pass

        raise RuntimeError(f"Failed to parse JSON from LLM response: {text[:200]}")
