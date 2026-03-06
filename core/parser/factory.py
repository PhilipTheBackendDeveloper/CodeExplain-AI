"""
Parser Factory — Dispatcher for multi-language source code parsing.
"""

from pathlib import Path
from typing import Protocol

from core.parser.ast_parser import ASTParser, ParseResult
from core.parser.node_mapper import ModuleNode, NodeMapper


class Parser(Protocol):
    def parse_file(self, file_path: Path) -> ParseResult:
        ...


class UniversalParser:
    """
    Detects file types and routes to the appropriate parser.
    Supports Python (.py) and TypeScript/JavaScript (.ts, .js, .tsx, .jsx).
    """

    def __init__(self):
        self._python_parser = ASTParser()
        self._python_mapper = NodeMapper()

    def parse_and_map(self, file_path: Path) -> ModuleNode:
        suffix = file_path.suffix.lower()

        if suffix == ".py":
            result = self._python_parser.parse_file(file_path)
            if not result.success:
                raise ValueError(f"Python Parse Error: {result.errors[0]}")
            return self._python_mapper.map(result)

        elif suffix in (".ts", ".tsx", ".js", ".jsx"):
            # Import here to avoid circular dependencies
            from core.parser.typescript_parser import TypeScriptParser
            ts_parser = TypeScriptParser()
            return ts_parser.parse_to_module(file_path)

        else:
            raise ValueError(f"Unsupported file extension: {suffix}")
