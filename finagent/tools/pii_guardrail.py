from __future__ import annotations

import re
from typing import Any


PATTERNS: dict[str, re.Pattern[str]] = {
    "email": re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b"),
    "phone": re.compile(r"\b(?:\d{2,3}-\d{3,4}-\d{4}|\d{10,11})\b"),
    "resident_id": re.compile(r"\b\d{6}-\d{7}\b"),
}


def mask_pii(text: str) -> dict[str, Any]:
    masked = text
    counts: dict[str, int] = {}

    for name, pattern in PATTERNS.items():
        matches = pattern.findall(masked)
        if not matches:
            continue
        counts[name] = len(matches)
        masked = pattern.sub(f"[{name.upper()}]", masked)

    return {
        "original": text,
        "masked": masked,
        "counts": counts,
    }
