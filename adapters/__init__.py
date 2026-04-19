"""ATP adapter registry — import all adapters here."""

from .claude_code import AdapterResult, ClaudeCodeAdapter, ClaudeCodeAdapterConfig

__all__ = [
    "AdapterResult",
    "ClaudeCodeAdapter",
    "ClaudeCodeAdapterConfig",
]
