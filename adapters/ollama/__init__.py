"""ATP Ollama adapter — local LLM inference."""

from adapters.ollama.ollama_adapter import execute_ollama, OllamaAdapterError

__all__ = ["execute_ollama", "OllamaAdapterError"]
