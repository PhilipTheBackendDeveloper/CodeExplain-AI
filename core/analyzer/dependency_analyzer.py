"""
Dependency Analyzer — Builds import dependency maps for a Python module.

Tracks which modules are imported, categorizes them (stdlib/third-party/local),
and surfaces circular dependency candidates.
"""

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Dependency:
    """A single import dependency."""
    module: str
    names: list[str]       # specific names imported (empty = whole module)
    lineno: int
    is_from_import: bool
    category: str          # "stdlib" | "third_party" | "local" | "unknown"
    alias: Optional[str] = None


@dataclass
class DependencyReport:
    """Full dependency analysis for a module."""
    filename: str
    dependencies: list[Dependency] = field(default_factory=list)

    @property
    def stdlib_deps(self) -> list[Dependency]:
        return [d for d in self.dependencies if d.category == "stdlib"]

    @property
    def third_party_deps(self) -> list[Dependency]:
        return [d for d in self.dependencies if d.category == "third_party"]

    @property
    def local_deps(self) -> list[Dependency]:
        return [d for d in self.dependencies if d.category == "local"]

    @property
    def module_names(self) -> list[str]:
        return [d.module for d in self.dependencies]

    @property
    def total_count(self) -> int:
        return len(self.dependencies)


# Partial stdlib list for fast categorization
_STDLIB = {
    "abc", "ast", "asyncio", "builtins", "collections", "contextlib", "copy",
    "csv", "dataclasses", "datetime", "decimal", "enum", "functools", "gc",
    "glob", "hashlib", "hmac", "http", "importlib", "inspect", "io", "itertools",
    "json", "logging", "math", "mimetypes", "operator", "os", "pathlib", "pickle",
    "platform", "pprint", "queue", "random", "re", "shutil", "signal", "socket",
    "sqlite3", "ssl", "stat", "string", "struct", "subprocess", "sys", "tempfile",
    "textwrap", "threading", "time", "traceback", "types", "typing", "unicodedata",
    "unittest", "urllib", "uuid", "warnings", "weakref", "xml", "zipfile",
    "_thread", "concurrent", "email", "html", "tkinter", "argparse", "cmd",
    "code", "codeop", "dis", "token", "tokenize", "keyword", "linecache",
}

# Well-known third-party packages
_KNOWN_THIRD_PARTY = {
    "rich", "typer", "fastapi", "uvicorn", "pydantic", "yaml", "networkx",
    "colorama", "pyfiglet", "jinja2", "requests", "numpy", "pandas", "flask",
    "django", "sqlalchemy", "pytest", "click", "httpx", "aiohttp", "celery",
    "redis", "boto3", "PIL", "cv2", "torch", "tensorflow", "sklearn",
}


def _categorize_module(module_name: str) -> str:
    root = module_name.split(".")[0]
    if root in _STDLIB:
        return "stdlib"
    if root in _KNOWN_THIRD_PARTY:
        return "third_party"
    # Relative imports or local-looking names
    if module_name.startswith(".") or module_name.startswith("core") or module_name.startswith("utils"):
        return "local"
    return "unknown"


class DependencyAnalyzer:
    """
    Analyzes import dependencies in a parsed Python module.

    Usage:
        analyzer = DependencyAnalyzer()
        report = analyzer.analyze(parse_result)
    """

    def analyze(self, parse_result) -> DependencyReport:
        """Extract all import dependencies from the module AST."""
        tree = parse_result.tree
        deps: list[Dependency] = []
        seen: set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    key = alias.name
                    if key not in seen:
                        seen.add(key)
                        deps.append(Dependency(
                            module=alias.name,
                            names=[],
                            lineno=node.lineno,
                            is_from_import=False,
                            category=_categorize_module(alias.name),
                            alias=alias.asname,
                        ))

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                names = [alias.name for alias in node.names]
                key = f"{module}::{','.join(names)}"
                if key not in seen:
                    seen.add(key)
                    deps.append(Dependency(
                        module=module,
                        names=names,
                        lineno=node.lineno,
                        is_from_import=True,
                        category=_categorize_module(module),
                    ))

        # Sort by line number
        deps.sort(key=lambda d: d.lineno)

        return DependencyReport(filename=parse_result.filename, dependencies=deps)
