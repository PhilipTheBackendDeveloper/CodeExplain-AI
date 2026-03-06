"""
Logger — Structured, rich-styled logging for CodeExplain AI.

Provides a centralized logger factory that all modules use.
"""

import logging
import sys
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler


_console = Console(stderr=True)
_configured = False


def _configure_logging(level: str = "INFO") -> None:
    global _configured
    if _configured:
        return
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=_console,
                show_time=True,
                show_path=False,
                markup=True,
                rich_tracebacks=True,
            )
        ],
    )
    _configured = True


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Return a named logger, initializing rich handler on first call."""
    _configure_logging(level)
    return logging.getLogger(name)
