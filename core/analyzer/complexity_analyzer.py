"""
Complexity Analyzer — Computes cyclomatic complexity, nesting depth, and loop metrics.

Uses McCabe's cyclomatic complexity algorithm: CC = edges - nodes + 2*connected_components
Simplified version: CC = number of branches + 1
"""

import ast
from dataclasses import dataclass, field

from core.parser.node_mapper import FunctionNode, ModuleNode


@dataclass
class FunctionComplexity:
    """Complexity metrics for a single function."""
    name: str
    lineno: int
    cyclomatic_complexity: int = 1
    nesting_depth: int = 0
    loop_count: int = 0
    branch_count: int = 0
    return_count: int = 0
    has_recursion: bool = False

    @property
    def complexity_label(self) -> str:
        cc = self.cyclomatic_complexity
        if cc <= 5:
            return "Low"
        elif cc <= 10:
            return "Medium"
        elif cc <= 20:
            return "High"
        else:
            return "Very High"

    @property
    def complexity_emoji(self) -> str:
        labels = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Very High": "🔴"}
        return labels.get(self.complexity_label, "⚪")


@dataclass
class ModuleComplexity:
    """Aggregated complexity metrics for an entire module."""
    filename: str
    functions: list[FunctionComplexity] = field(default_factory=list)

    @property
    def average_complexity(self) -> float:
        if not self.functions:
            return 0.0
        return sum(f.cyclomatic_complexity for f in self.functions) / len(self.functions)

    @property
    def max_complexity(self) -> int:
        if not self.functions:
            return 0
        return max(f.cyclomatic_complexity for f in self.functions)

    @property
    def most_complex_function(self) -> FunctionComplexity | None:
        if not self.functions:
            return None
        return max(self.functions, key=lambda f: f.cyclomatic_complexity)

    @property
    def overall_label(self) -> str:
        avg = self.average_complexity
        if avg <= 5:
            return "Low"
        elif avg <= 10:
            return "Medium"
        elif avg <= 20:
            return "High"
        else:
            return "Very High"


# Branch-inducing AST node types for cyclomatic complexity
_BRANCH_NODES = (
    ast.If, ast.For, ast.AsyncFor, ast.While,
    ast.ExceptHandler, ast.With, ast.AsyncWith,
    ast.Assert, ast.comprehension,
)
# Operators that count as branches (and, or ternary)
_BOOL_OPS = (ast.And, ast.Or)


def _compute_cyclomatic(func_ast: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Compute McCabe cyclomatic complexity for a single function AST node."""
    complexity = 1  # base path
    for node in ast.walk(func_ast):
        if isinstance(node, _BRANCH_NODES):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            # Each operator in a boolean chain adds one path
            complexity += len(node.values) - 1
        elif isinstance(node, ast.IfExp):  # ternary
            complexity += 1
    return complexity


def _compute_nesting_depth(func_ast: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Compute the maximum nesting depth of control flow in a function."""
    def _depth(node: ast.AST, current_depth: int) -> int:
        if isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.With,
                              ast.AsyncWith, ast.Try, ast.ExceptHandler)):
            current_depth += 1
        max_depth = current_depth
        for child in ast.iter_child_nodes(node):
            max_depth = max(max_depth, _depth(child, current_depth))
        return max_depth

    return _depth(func_ast, 0)


def _count_loops(func_ast: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    return sum(
        1 for node in ast.walk(func_ast)
        if isinstance(node, (ast.For, ast.AsyncFor, ast.While))
    )


def _count_branches(func_ast: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    return sum(1 for node in ast.walk(func_ast) if isinstance(node, ast.If))


def _count_returns(func_ast: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    return sum(1 for node in ast.walk(func_ast) if isinstance(node, ast.Return))


def _is_recursive(func_ast: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Detect direct recursion by looking for self-calls within the function."""
    func_name = func_ast.name
    for node in ast.walk(func_ast):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == func_name:
                return True
    return False


class ComplexityAnalyzer:
    """
    Computes complexity metrics for Python modules.

    Usage:
        analyzer = ComplexityAnalyzer()
        result = analyzer.analyze(parse_result)
    """

    def analyze(self, parse_result) -> ModuleComplexity:
        """Analyze complexity metrics from a ParseResult."""
        tree = parse_result.tree
        functions: list[FunctionComplexity] = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fc = FunctionComplexity(
                    name=node.name,
                    lineno=node.lineno,
                    cyclomatic_complexity=_compute_cyclomatic(node),
                    nesting_depth=_compute_nesting_depth(node),
                    loop_count=_count_loops(node),
                    branch_count=_count_branches(node),
                    return_count=_count_returns(node),
                    has_recursion=_is_recursive(node),
                )
                functions.append(fc)

        return ModuleComplexity(
            filename=parse_result.filename,
            functions=functions,
        )
