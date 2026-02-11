"""Parse LLM responses into text and code components."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedResponse:
    """Parsed LLM response with separated text and code.

    Attributes:
        text: The text content with code blocks removed.
        code: Extracted Python code (first python block), or None.
    """

    text: str
    code: Optional[str] = None


# Match ```python ... ``` blocks
_PYTHON_CODE_PATTERN = re.compile(
    r"```python\s*\n(.*?)```",
    re.DOTALL,
)


def parse_response(raw: str) -> ParsedResponse:
    """Parse an LLM response into text and optional code.

    Extracts the first ```python code block as executable code.
    Only that first python block is removed from the text field.
    All other code blocks (sql, json, language-less, and subsequent
    python blocks) are preserved in the text for Markdown rendering.

    Args:
        raw: Raw LLM response string.

    Returns:
        ParsedResponse with text and optional code.
    """
    if not raw:
        return ParsedResponse(text="", code=None)

    # Extract first python code block
    code_match = _PYTHON_CODE_PATTERN.search(raw)
    code: Optional[str] = None

    if code_match:
        code = code_match.group(1).strip()
        # Remove only the first python block from text (positional removal)
        text = (raw[: code_match.start()] + raw[code_match.end() :]).strip()
    else:
        text = raw.strip()

    return ParsedResponse(text=text, code=code)
