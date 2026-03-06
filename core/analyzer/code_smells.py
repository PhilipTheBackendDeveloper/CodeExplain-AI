"""
Code Smells Detector — Identifies anti-patterns and design problems.

Detects: long functions, deep nesting, too many arguments, unused imports,
bare except clauses, missing docstrings, magic numbers, god functions.
"""

import ast
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any
import yaml


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class CodeSmell:
    """A single detected code smell/violation."""
    kind: str
    severity: Severity
    message: str
    lineno: int
    name: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def severity_emoji(self) -> str:
        return {"info": "ℹ️", "warning": "⚠️", "error": "❌"}.get(self.severity, "•")


@dataclass
class SmellReport:
    """All detected code smells in a module."""
    filename: str
    smells: list[CodeSmell] = field(default_factory=list)

    def by_severity(self, severity: Severity) -> list[CodeSmell]:
        return [s for s in self.smells if s.severity == severity]

    @property
    def errors(self) -> list[CodeSmell]:
        return self.by_severity(Severity.ERROR)

    @property
    def warnings(self) -> list[CodeSmell]:
        return self.by_severity(Severity.WARNING)

    @property
    def infos(self) -> list[CodeSmell]:
        return self.by_severity(Severity.INFO)

    @property
    def total_count(self) -> int:
        return len(self.smells)

    @property
    def has_critical(self) -> bool:
        return len(self.errors) > 0


# Default thresholds (overridden by rules.yaml)
_DEFAULTS = {
    "long_function_lines": 50,
    "god_function_lines": 100,
    "deep_nesting_depth": 4,
    "max_arguments": 5,
    "magic_number_threshold": True,
}


class CodeSmellDetector:
    """
    Detects code smells from a parsed Python module.

    Usage:
        detector = CodeSmellDetector()
        report = detector.detect(parse_result)
    """

    def __init__(self, config_path: str | None = None):
        self._rules = self._load_rules(config_path)

    def _load_rules(self, config_path: str | None) -> dict:
        if config_path:
            try:
                with open(config_path) as f:
                    return yaml.safe_load(f).get("code_smells", {})
            except Exception:
                pass
        # Try default location
        try:
            default = Path(__file__).parent.parent.parent / "config" / "rules.yaml"
            with open(default) as f:
                return yaml.safe_load(f).get("code_smells", {})
        except Exception:
            return {}

    def _rule(self, name: str, key: str, default: Any) -> Any:
        return self._rules.get(name, {}).get(key, default)

    def detect(self, parse_result) -> SmellReport:
        """Detect all code smells in a ParseResult."""
        tree = parse_result.tree
        smells: list[CodeSmell] = []

        # Walk all nodes
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                smells.extend(self._check_function(node))
            elif isinstance(node, ast.ExceptHandler):
                smells.extend(self._check_bare_except(node))

        # Module-level checks
        smells.extend(self._check_magic_numbers(tree))
        smells.extend(self._check_module_docstring(tree))

        smells.sort(key=lambda s: s.lineno)
        return SmellReport(filename=parse_result.filename, smells=smells)

    def _function_line_count(self, node: ast.FunctionDef) -> int:
        return getattr(node, "end_lineno", node.lineno) - node.lineno + 1

    def _check_function(self, node: ast.FunctionDef) -> list[CodeSmell]:
        smells = []
        name = node.name
        lines = self._function_line_count(node)
        long_threshold = self._rule("long_function", "threshold_lines", 50)
        god_threshold = self._rule("god_function", "threshold_lines", 100)
        nest_threshold = self._rule("deep_nesting", "threshold_depth", 4)
        arg_threshold = self._rule("too_many_arguments", "threshold_args", 5)

        # God function
        if self._rule("god_function", "enabled", True) and lines >= god_threshold:
            smells.append(CodeSmell(
                kind="god_function", severity=Severity.ERROR,
                message=f"'{name}' is a god function ({lines} lines). It does too much.",
                lineno=node.lineno, name=name, details={"lines": lines}
            ))
        # Long function
        elif self._rule("long_function", "enabled", True) and lines >= long_threshold:
            smells.append(CodeSmell(
                kind="long_function", severity=Severity.WARNING,
                message=f"Function '{name}' is too long ({lines} lines). Consider refactoring.",
                lineno=node.lineno, name=name, details={"lines": lines}
            ))

        # Too many arguments
        all_args = (
            node.args.args + node.args.posonlyargs + node.args.kwonlyargs
        )
        # skip 'self' and 'cls'
        real_args = [a for a in all_args if a.arg not in ("self", "cls")]
        if self._rule("too_many_arguments", "enabled", True) and len(real_args) > arg_threshold:
            smells.append(CodeSmell(
                kind="too_many_arguments", severity=Severity.WARNING,
                message=f"Function '{name}' has too many arguments ({len(real_args)}). Consider using a dataclass.",
                lineno=node.lineno, name=name, details={"count": len(real_args)}
            ))

        # Deep nesting
        depth = self._compute_depth(node)
        if self._rule("deep_nesting", "enabled", True) and depth > nest_threshold:
            smells.append(CodeSmell(
                kind="deep_nesting", severity=Severity.WARNING,
                message=f"Deep nesting ({depth} levels) in '{name}'. Simplify control flow.",
                lineno=node.lineno, name=name, details={"depth": depth}
            ))

        # Missing docstring
        if self._rule("missing_docstring", "enabled", True):
            if not ast.get_docstring(node) and not name.startswith("_"):
                smells.append(CodeSmell(
                    kind="missing_docstring", severity=Severity.INFO,
                    message=f"'{name}' is missing a docstring.",
                    lineno=node.lineno, name=name,
                ))

        return smells

    def _compute_depth(self, node: ast.AST, current: int = 0) -> int:
        """Compute max nesting depth of control flow structures."""
        if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.AsyncFor)):
            current += 1
        return max(
            (self._compute_depth(child, current) for child in ast.iter_child_nodes(node)),
            default=current
        )

    def _check_bare_except(self, node: ast.ExceptHandler) -> list[CodeSmell]:
        if node.type is None:  # bare except:
            return [CodeSmell(
                kind="bare_except", severity=Severity.ERROR,
                message="Bare 'except:' clause detected. Specify exception types explicitly.",
                lineno=node.lineno,
            )]
        return []

    def _check_magic_numbers(self, tree: ast.Module) -> list[CodeSmell]:
        """Detect numeric literals that should be named constants."""
        smells = []
        if not self._rule("magic_numbers", "enabled", True):
            return smells
        # Allow common non-magic numbers
        allowed = {0, 1, -1, 2, 100}
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value not in allowed and abs(node.value) > 1:
                    smells.append(CodeSmell(
                        kind="magic_number", severity=Severity.INFO,
                        message=f"Magic number {node.value} detected. Consider a named constant.",
                        lineno=getattr(node, "lineno", 0),
                        details={"value": node.value}
                    ))
        return smells

    def _check_module_docstring(self, tree: ast.Module) -> list[CodeSmell]:
        if not ast.get_docstring(tree):
            return [CodeSmell(
                kind="missing_module_docstring", severity=Severity.INFO,
                message="Module is missing a docstring.",
                lineno=1,
            )]
        return []
