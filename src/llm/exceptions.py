"""Exceptions for the LLM module."""


class LLMError(Exception):
    """Base exception for LLM module."""

    pass


class SandboxError(LLMError):
    """Raised when sandbox execution fails."""

    pass


class SandboxTimeoutError(SandboxError):
    """Raised when sandbox execution exceeds time limit."""

    pass
