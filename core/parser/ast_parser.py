"""
AST Parser — Parses Python source code into an Abstract Syntax Tree.

This is the entry point of the parsing pipeline. It converts raw source code
strings into structured ast.Module objects that downstream components consume.
"""

import ast
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Generator, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ParseResult:
    """Holds the result of a parse operation."""
    source: str
    tree: ast.Module
    filename: str = "<unknown>"
    lines: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def line_count(self) -> int:
        return len(self.lines)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


class ASTParser:
    """
    Parses Python source code files or strings into AST trees.

    Usage:
        parser = ASTParser()
        result = parser.parse_file("my_script.py")
        result = parser.parse_source("def foo(): pass")
    """

    def __init__(self, type_comments: bool = False):
        self.type_comments = type_comments

    def parse_file(self, filepath: str | Path) -> ParseResult:
        """Parse a Python source file from disk."""
        filepath = Path(filepath)
        logger.debug(f"Parsing file: {filepath}")

        try:
            source = filepath.read_text(encoding="utf-8")
        except FileNotFoundError:
            return ParseResult(
                source="",
                tree=ast.parse(""),
                filename=str(filepath),
                errors=[f"File not found: {filepath}"],
            )
        except UnicodeDecodeError as e:
            return ParseResult(
                source="",
                tree=ast.parse(""),
                filename=str(filepath),
                errors=[f"Encoding error reading {filepath}: {e}"],
            )

        return self.parse_source(source, filename=str(filepath))

    def parse_source(self, source: str, filename: str = "<string>") -> ParseResult:
        """Parse a Python source string."""
        source = textwrap.dedent(source)
        lines = source.splitlines()

        try:
            tree = ast.parse(source, filename=filename, type_comments=self.type_comments)
            logger.debug(f"Successfully parsed {filename} ({len(lines)} lines)")
            return ParseResult(source=source, tree=tree, filename=filename, lines=lines)

        except SyntaxError as e:
            logger.warning(f"Syntax error in {filename}: {e}")
            return ParseResult(
                source=source,
                tree=ast.parse(""),  # empty fallback
                filename=filename,
                lines=lines,
                errors=[f"SyntaxError at line {e.lineno}: {e.msg}"],
            )

    def walk(self, result: ParseResult) -> Generator[ast.AST, None, None]:
        """Walk all nodes in the AST tree."""
        yield from ast.walk(result.tree)

    def iter_functions(self, result: ParseResult) -> Generator[ast.FunctionDef, None, None]:
        """Yield all top-level and nested function definitions."""
        for node in ast.walk(result.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                yield node

    def iter_classes(self, result: ParseResult) -> Generator[ast.ClassDef, None, None]:
        """Yield all class definitions."""
        for node in ast.walk(result.tree):
            if isinstance(node, ast.ClassDef):
                yield node

    def iter_imports(
        self, result: ParseResult
    ) -> Generator[ast.Import | ast.ImportFrom, None, None]:
        """Yield all import statements."""
        for node in ast.walk(result.tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                yield node

    def get_source_segment(self, result: ParseResult, node: ast.AST) -> Optional[str]:
        """Extract the source code segment for a given AST node."""
        try:
            return ast.get_source_segment(result.source, node)
        except Exception:
            return None

    def dump(self, result: ParseResult, indent: int = 2) -> str:
        """Return a pretty-printed AST dump string."""
        return ast.dump(result.tree, indent=indent)
