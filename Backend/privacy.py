"""Small, dependency-free redaction layer for text sent to hosted models."""

from __future__ import annotations

import re

_SENSITIVE_PATTERNS = (
    ("email", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)),
    ("card", re.compile(r"\b(?:\d[ -]*?){13,19}\b")),
    ("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("phone", re.compile(r"(?<!\w)(?:\+?\d[\d .()-]{7,}\d)(?!\w)")),
    ("secret", re.compile(
        r"\b(?:sk-[A-Za-z0-9_-]{16,}|xai-[A-Za-z0-9_-]{16,}|"
        r"gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|"
        r"Bearer\s+[A-Za-z0-9._~+/=-]{16,}|"
        r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})\b"
    )),
    ("private_key", re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----.*?"
        r"-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        re.I | re.S,
    )),
    ("credential", re.compile(
        r"(?i)\b(password|passwd|api[_ -]?key|secret|token)\b"
        r"(\s*[:=]\s*)([^\s,;]+)"
    )),
)


def redact_sensitive_text(text: str) -> tuple[str, int]:
    """Replace common personal identifiers and credentials before cloud use.

    Returns the sanitized text and the number of replacements. Redacted values
    are deliberately not restored in model output.
    """
    count = 0
    for label, pattern in _SENSITIVE_PATTERNS:
        if label == "credential":
            text, replacements = pattern.subn(lambda m: f"{m.group(1)}{m.group(2)}[REDACTED]", text)
        else:
            text, replacements = pattern.subn(f"[{label.upper()}_REDACTED]", text)
        count += replacements
    return text, count
