"""Gemini API client for LLM chat interactions."""
from typing import Any

from src.llm.exceptions import LLMError

try:
    from google import genai
except ImportError:
    genai = None  # type: ignore[assignment]


class GeminiClient:
    """Client for interacting with Gemini API.

    Uses google-genai package with API key authentication.
    """

    def __init__(
        self, api_key: str, model_name: str = "gemini-3-flash-preview"
    ) -> None:
        """Initialize GeminiClient.

        Args:
            api_key: Gemini API key.
            model_name: Model name to use.

        Raises:
            LLMError: If api_key is empty or genai is not available.
        """
        if not api_key:
            raise LLMError("Gemini API key is required")

        if genai is None:
            raise LLMError("google-genai package is not installed")

        self.model_name = model_name
        self._client = genai.Client(api_key=api_key)

    def send_message(
        self,
        user_message: str,
        history: list[dict[str, str]],
        system_prompt: str,
    ) -> str:
        """Send a message to Gemini and get a response.

        Args:
            user_message: The user's message.
            history: Conversation history as list of {role, content} dicts.
            system_prompt: System prompt with data context.

        Returns:
            The model's response text.

        Raises:
            LLMError: If API call fails.
        """
        # Build contents list for Gemini API
        contents: list[dict[str, Any]] = []

        # Add history
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(
                {"role": role, "parts": [{"text": msg["content"]}]}
            )

        # Add current user message
        contents.append(
            {"role": "user", "parts": [{"text": user_message}]}
        )

        try:
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config={
                    "system_instruction": system_prompt,
                    "temperature": 0.3,
                    "max_output_tokens": 4096,
                },
            )
        except Exception as e:
            raise LLMError(f"Gemini API error: {e}") from e
        text = response.text
        if text is None:
            raise LLMError("Gemini API returned empty response")
        return text

    def summarize_result(self, prompt: str) -> str:
        """Summarize code execution result into natural language.

        This is a simpler call without history or system prompt,
        used to convert raw Python output into a user-friendly response.
        Uses lower temperature for accuracy.

        Args:
            prompt: The summarization prompt (from build_summarize_prompt).

        Returns:
            Natural language summary of the execution result.

        Raises:
            LLMError: If API call fails.
        """
        contents = [{"role": "user", "parts": [{"text": prompt}]}]

        try:
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config={
                    "temperature": 0.1,
                    "max_output_tokens": 1024,
                },
            )
        except Exception as e:
            raise LLMError(f"Gemini API error during summarization: {e}") from e

        text = response.text
        if text is None:
            raise LLMError("Gemini API returned empty summarization response")
        return text
