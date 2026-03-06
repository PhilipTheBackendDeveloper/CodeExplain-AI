"""
File Loader — Reads source files from disk with encoding detection.
"""

from pathlib import Path
from typing import Optional


SUPPORTED_EXTENSIONS = {".py"}


def load_file(filepath: str | Path) -> tuple[str, list[str]]:
    """
    Read a source file and return (source_string, lines_list).

    Raises:
        FileNotFoundError: if path does not exist
        ValueError: if file extension is not supported
        IOError: on read failure
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    # Try UTF-8 first, then Latin-1 as fallback
    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            source = path.read_text(encoding=encoding)
            return source, source.splitlines()
        except UnicodeDecodeError:
            continue

    raise IOError(f"Could not decode {path} with any supported encoding.")


def is_valid_python_file(filepath: str | Path) -> bool:
    """Return True if the path points to a readable .py file."""
    path = Path(filepath)
    return path.is_file() and path.suffix.lower() == ".py"


def find_python_files(directory: str | Path, recursive: bool = True) -> list[Path]:
    """Find all .py files in a directory."""
    directory = Path(directory)
    pattern = "**/*.py" if recursive else "*.py"
    return sorted(directory.glob(pattern))
