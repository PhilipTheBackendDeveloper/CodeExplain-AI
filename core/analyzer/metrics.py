"""
Metrics — Computes software quality metrics for a Python module.

Provides: LOC, SLOC, comment ratio, blank ratio, function/class counts,
and a Halstead volume proxy for maintainability scoring.
"""

import ast
import math
from dataclasses import dataclass


@dataclass
class CodeMetrics:
    """Comprehensive code quality metrics for a module."""
    filename: str
    total_lines: int = 0
    source_lines: int = 0        # SLOC (non-blank, non-comment)
    blank_lines: int = 0
    comment_lines: int = 0
    docstring_lines: int = 0
    function_count: int = 0
    async_function_count: int = 0
    class_count: int = 0
    import_count: int = 0
    global_variable_count: int = 0
    lambda_count: int = 0
    decorator_count: int = 0
    # Halstead approximation
    unique_operators: int = 0
    unique_operands: int = 0
    total_operators: int = 0
    total_operands: int = 0

    @property
    def comment_ratio(self) -> float:
        """Ratio of comment+docstring lines to total lines."""
        if self.total_lines == 0:
            return 0.0
        return (self.comment_lines + self.docstring_lines) / self.total_lines

    @property
    def blank_ratio(self) -> float:
        if self.total_lines == 0:
            return 0.0
        return self.blank_lines / self.total_lines

    @property
    def halstead_vocabulary(self) -> int:
        return self.unique_operators + self.unique_operands

    @property
    def halstead_length(self) -> int:
        return self.total_operators + self.total_operands

    @property
    def halstead_volume(self) -> float:
        vocab = self.halstead_vocabulary
        if vocab <= 0:
            return 0.0
        return self.halstead_length * math.log2(vocab)

    @property
    def halstead_difficulty(self) -> float:
        if self.unique_operands == 0:
            return 0.0
        return (self.unique_operators / 2) * (self.total_operands / self.unique_operands)

    @property
    def halstead_effort(self) -> float:
        return self.halstead_difficulty * self.halstead_volume

    def summary(self) -> dict:
        return {
            "total_lines": self.total_lines,
            "source_lines": self.source_lines,
            "blank_lines": self.blank_lines,
            "comment_lines": self.comment_lines,
            "comment_ratio": round(self.comment_ratio * 100, 1),
            "function_count": self.function_count,
            "class_count": self.class_count,
            "import_count": self.import_count,
            "halstead_volume": round(self.halstead_volume, 2),
            "halstead_difficulty": round(self.halstead_difficulty, 2),
        }


# AST operator node types used for Halstead
_OPERATOR_NODES = (
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.MatMult, ast.BitAnd, ast.BitOr, ast.BitXor, ast.LShift, ast.RShift,
    ast.And, ast.Or, ast.Not, ast.Invert, ast.UAdd, ast.USub,
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Is, ast.IsNot,
    ast.In, ast.NotIn, ast.If, ast.For, ast.While, ast.Return, ast.Assign,
    ast.AugAssign, ast.Delete, ast.Import, ast.ImportFrom, ast.Call,
)


class MetricsComputer:
    """
    Computes code metrics from a ParseResult.

    Usage:
        computer = MetricsComputer()
        metrics = computer.compute(parse_result)
    """

    def compute(self, parse_result) -> CodeMetrics:
        """Compute all metrics from a ParseResult."""
        source = parse_result.source
        lines = parse_result.lines
        tree = parse_result.tree

        metrics = CodeMetrics(filename=parse_result.filename)
        metrics.total_lines = len(lines)

        # Line-level analysis
        blank = 0
        comment = 0
        source_lines = 0
        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank += 1
            elif stripped.startswith("#"):
                comment += 1
            else:
                source_lines += 1

        metrics.blank_lines = blank
        metrics.comment_lines = comment
        metrics.source_lines = source_lines

        # Count docstring lines via AST
        ds_lines = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                ds = ast.get_docstring(node)
                if ds:
                    ds_lines += ds.count("\n") + 1
        metrics.docstring_lines = ds_lines

        # AST-level counts
        func_count = 0
        async_count = 0
        class_count = 0
        import_count = 0
        global_var_count = 0
        lambda_count = 0
        decorator_count = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_count += 1
                decorator_count += len(node.decorator_list)
            elif isinstance(node, ast.AsyncFunctionDef):
                func_count += 1
                async_count += 1
                decorator_count += len(node.decorator_list)
            elif isinstance(node, ast.ClassDef):
                class_count += 1
                decorator_count += len(node.decorator_list)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                import_count += 1
            elif isinstance(node, ast.Lambda):
                lambda_count += 1

        # Top-level global var assignments
        for stmt in tree.body:
            if isinstance(stmt, ast.Assign):
                global_var_count += sum(
                    1 for t in stmt.targets if isinstance(t, ast.Name)
                )

        metrics.function_count = func_count
        metrics.async_function_count = async_count
        metrics.class_count = class_count
        metrics.import_count = import_count
        metrics.global_variable_count = global_var_count
        metrics.lambda_count = lambda_count
        metrics.decorator_count = decorator_count

        # Halstead: operators and operands
        operators: list[str] = []
        operands: list[str] = []

        for node in ast.walk(tree):
            # Operands: names and constants
            if isinstance(node, ast.Name):
                operands.append(node.id)
            elif isinstance(node, ast.Constant):
                operands.append(repr(node.value))
            # Operators: AST operator types
            elif isinstance(node, _OPERATOR_NODES):
                operators.append(type(node).__name__)

        metrics.unique_operators = len(set(operators))
        metrics.unique_operands = len(set(operands))
        metrics.total_operators = len(operators)
        metrics.total_operands = len(operands)

        return metrics
