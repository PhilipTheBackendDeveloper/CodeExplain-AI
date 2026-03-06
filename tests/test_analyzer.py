"""
Tests for core/analyzer/ — Complexity, Dependency, Smells, Metrics
"""

import pytest
from core.parser.ast_parser import ASTParser
from core.analyzer.complexity_analyzer import ComplexityAnalyzer
from core.analyzer.dependency_analyzer import DependencyAnalyzer
from core.analyzer.code_smells import CodeSmellDetector, Severity
from core.analyzer.metrics import MetricsComputer


COMPLEX_CODE = """
def simple():
    return 1

def medium_complexity(x, y, z):
    if x > 0:
        if y > 0:
            for i in range(z):
                if i % 2 == 0:
                    pass
    elif y < 0:
        while z > 0:
            z -= 1
    return x + y

def recursive_func(n):
    if n <= 0:
        return 0
    return recursive_func(n - 1) + 1

def too_many_args(a, b, c, d, e, f, g):
    pass

def long_function():
    x = 1
    y = 2
    z = 3
    a = 4
    b = 5
    c = 6
    d = 7
    e = 8
    f = 9
    g = 10
    h = 11
    i = 12
    j = 13
    k = 14
    l = 15
    m = 16
    n = 17
    o = 18
    p = 19
    q = 20
    return x + y + z + a + b + c + d + e + f + g
"""

SMELL_CODE = """
import os
import json

def bad_func():
    try:
        pass
    except:
        pass

def no_docstring(a, b, c, d, e, f):
    return a + b
"""

IMPORT_CODE = """
import os
import sys
import json
from pathlib import Path
from rich import print
from mymodule import helper
"""


class TestComplexityAnalyzer:
    def _parse(self, code: str):
        return ASTParser().parse_source(code)

    def test_simple_function_low_cc(self):
        result = self._parse("def simple(): return 1")
        ca = ComplexityAnalyzer()
        report = ca.analyze(result)
        simple = next(f for f in report.functions if f.name == "simple")
        assert simple.cyclomatic_complexity == 1
        assert simple.complexity_label == "Low"

    def test_complex_function_higher_cc(self):
        result = self._parse(COMPLEX_CODE)
        ca = ComplexityAnalyzer()
        report = ca.analyze(result)
        medium = next(f for f in report.functions if f.name == "medium_complexity")
        assert medium.cyclomatic_complexity > 3

    def test_recursive_detection(self):
        result = self._parse(COMPLEX_CODE)
        ca = ComplexityAnalyzer()
        report = ca.analyze(result)
        rec = next(f for f in report.functions if f.name == "recursive_func")
        assert rec.has_recursion

    def test_non_recursive_no_flag(self):
        result = self._parse(COMPLEX_CODE)
        ca = ComplexityAnalyzer()
        report = ca.analyze(result)
        simple = next(f for f in report.functions if f.name == "simple")
        assert not simple.has_recursion

    def test_loop_count(self):
        code = "def f():\n    for i in range(10):\n        while True:\n            break"
        result = self._parse(code)
        ca = ComplexityAnalyzer()
        report = ca.analyze(result)
        assert report.functions[0].loop_count == 2

    def test_overall_label_exists(self):
        result = self._parse(COMPLEX_CODE)
        report = ComplexityAnalyzer().analyze(result)
        assert report.overall_label in ("Low", "Medium", "High", "Very High")

    def test_average_complexity_positive(self):
        result = self._parse(COMPLEX_CODE)
        report = ComplexityAnalyzer().analyze(result)
        assert report.average_complexity > 0

    def test_most_complex_function(self):
        result = self._parse(COMPLEX_CODE)
        report = ComplexityAnalyzer().analyze(result)
        most_complex = report.most_complex_function
        assert most_complex is not None


class TestDependencyAnalyzer:
    def test_finds_imports(self):
        result = ASTParser().parse_source(IMPORT_CODE)
        report = DependencyAnalyzer().analyze(result)
        modules = report.module_names
        assert "os" in modules
        assert "sys" in modules
        assert "json" in modules

    def test_categorizes_stdlib(self):
        result = ASTParser().parse_source(IMPORT_CODE)
        report = DependencyAnalyzer().analyze(result)
        stdlib = [d.module for d in report.stdlib_deps]
        assert "os" in stdlib
        assert "sys" in stdlib

    def test_categorizes_third_party(self):
        result = ASTParser().parse_source(IMPORT_CODE)
        report = DependencyAnalyzer().analyze(result)
        third = [d.module for d in report.third_party_deps]
        assert "rich" in third

    def test_total_count(self):
        result = ASTParser().parse_source(IMPORT_CODE)
        report = DependencyAnalyzer().analyze(result)
        assert report.total_count >= 5

    def test_from_import_flag(self):
        result = ASTParser().parse_source("from pathlib import Path")
        report = DependencyAnalyzer().analyze(result)
        dep = report.dependencies[0]
        assert dep.is_from_import
        assert "Path" in dep.names


class TestCodeSmellDetector:
    def test_detects_bare_except(self):
        result = ASTParser().parse_source(SMELL_CODE)
        report = CodeSmellDetector().detect(result)
        kinds = [s.kind for s in report.smells]
        assert "bare_except" in kinds

    def test_detects_too_many_args(self):
        result = ASTParser().parse_source(COMPLEX_CODE)
        report = CodeSmellDetector().detect(result)
        kinds = [s.kind for s in report.smells]
        assert "too_many_arguments" in kinds

    def test_detects_missing_docstring(self):
        result = ASTParser().parse_source(SMELL_CODE)
        report = CodeSmellDetector().detect(result)
        kinds = [s.kind for s in report.smells]
        assert "missing_docstring" in kinds

    def test_clean_code_no_errors(self):
        clean = '''
def add(a: int, b: int) -> int:
    """Add two numbers and return the result."""
    return a + b
'''
        result = ASTParser().parse_source(clean)
        report = CodeSmellDetector().detect(result)
        error_smells = [s for s in report.smells if s.severity == Severity.ERROR]
        assert len(error_smells) == 0

    def test_severity_levels(self):
        result = ASTParser().parse_source(SMELL_CODE)
        report = CodeSmellDetector().detect(result)
        severities = {s.severity for s in report.smells}
        # At minimum should have info or warning
        assert len(severities) > 0


class TestMetricsComputer:
    def test_line_counts(self):
        result = ASTParser().parse_source(COMPLEX_CODE)
        metrics = MetricsComputer().compute(result)
        assert metrics.total_lines > 0
        assert metrics.source_lines > 0
        assert metrics.total_lines >= metrics.source_lines

    def test_function_count(self):
        result = ASTParser().parse_source(COMPLEX_CODE)
        metrics = MetricsComputer().compute(result)
        assert metrics.function_count >= 5

    def test_halstead_volume_positive(self):
        result = ASTParser().parse_source(COMPLEX_CODE)
        metrics = MetricsComputer().compute(result)
        assert metrics.halstead_volume >= 0

    def test_comment_ratio_between_zero_and_one(self):
        code = "# This is a comment\nx = 1\n# Another\ny = 2"
        result = ASTParser().parse_source(code)
        metrics = MetricsComputer().compute(result)
        assert 0.0 <= metrics.comment_ratio <= 1.0

    def test_summary_dict_shape(self):
        result = ASTParser().parse_source("x = 1")
        metrics = MetricsComputer().compute(result)
        summary = metrics.summary()
        assert "total_lines" in summary
        assert "source_lines" in summary
        assert "function_count" in summary
