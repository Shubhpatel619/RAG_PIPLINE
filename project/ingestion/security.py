import re
from typing import List


class PromptInjectionGuard:
    """
    Security module providing basic resistance against instructions embedded
    inside documents (prompt injection attacks).
    """

    SUSPECT_PATTERNS = [
        r"(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions",
        r"(?i)disregard\s+(all\s+)?system\s+prompts?",
        r"(?i)you\s+are\s+now\s+(a|an)",
        r"(?i)override\s+system\s+instructions",
        r"(?i)system\s+prompt:",
        r"(?i)say\s+[\"']?system\s+compromised[\"']?",
        r"(?i)act\s+as\s+a\s+jailbroken",
    ]

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """
        Sanitizes text by neutralizing detected prompt injection attempt phrases.
        """
        sanitized = text
        for pattern in cls.SUSPECT_PATTERNS:
            sanitized = re.sub(pattern, "[BLOCKED_INSTRUCTION_ATTEMPT]", sanitized)
        return sanitized

    @classmethod
    def wrap_context(cls, context_str: str) -> str:
        """
        Wraps context in strict data-isolation tags to signal untrusted document input.
        """
        return f"<untrusted_document_context>\n{context_str}\n</untrusted_document_context>"
