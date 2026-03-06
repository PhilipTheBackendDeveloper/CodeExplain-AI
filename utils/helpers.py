"""
Helpers — General-purpose utility functions.
"""

import hashlib
import re
from pathlib import Path
from typing import Any


def camel_to_words(name: str) -> str:
    """Convert CamelCase to 'camel case' words."""
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", name).lower()


def snake_to_words(name: str) -> str:
    """Convert snake_case to 'snake case' words."""
    return name.replace("_", " ").strip()


def truncate(text: str, max_len: int = 80, suffix: str = "...") -> str:
    """Truncate a string to max_len characters."""
    if len(text) <= max_len:
        return text
    return text[: max_len - len(suffix)] + suffix


def pluralize(count: int, singular: str, plural: str | None = None) -> str:
    """Return singular or plural form based on count."""
    if plural is None:
        plural = singular + "s"
    return singular if count == 1 else plural


def file_hash(filepath: str | Path) -> str:
    """Compute SHA-256 hash of a file's content."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max."""
    return max(min_val, min(max_val, value))


def percentage(value: float, total: float, decimals: int = 1) -> float:
    """Compute percentage safely."""
    if total == 0:
        return 0.0
    return round((value / total) * 100, decimals)


def flatten(nested: list[list[Any]]) -> list[Any]:
    """Flatten one level of nesting."""
    return [item for sublist in nested for item in sublist]
