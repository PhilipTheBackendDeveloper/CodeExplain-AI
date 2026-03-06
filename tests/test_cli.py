"""
Tests for CLI commands using Typer's test runner.
"""

import pytest
from typer.testing import CliRunner
from pathlib import Path

from cli.main_cli import app

runner = CliRunner()


@pytest.fixture
def sample_file(tmp_path) -> Path:
    """Create a temporary Python file for testing."""
    code = '''"""Sample module for CLI testing."""

import os


class Calculator:
    """A simple calculator class."""

    def add(self, a: int, b: int) -> int:
        """Return the sum of a and b."""
        return a + b

    def divide(self, a: float, b: float) -> float:
        """Divide a by b. Raises ValueError if b is 0."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b


def greet(name: str) -> str:
    """Return a greeting string."""
    return f"Hello, {name}!"


def fibonacci(n: int) -> int:
    """Return the nth Fibonacci number (recursive)."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
'''
    f = tmp_path / "sample.py"
    f.write_text(code)
    return f


class TestMainCLI:
    def test_no_args_shows_banner(self):
        result = runner.invoke(app, [])
        # Should exit 0 and show some output
        assert result.exit_code == 0

    def test_help(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "explain" in result.output.lower() or "CodeExplain" in result.output


class TestExplainCommand:
    def test_explain_developer_mode(self, sample_file):
        result = runner.invoke(app, ["explain", str(sample_file), "--mode", "developer"])
        assert result.exit_code == 0

    def test_explain_beginner_mode(self, sample_file):
        result = runner.invoke(app, ["explain", str(sample_file), "--mode", "beginner"])
        assert result.exit_code == 0

    def test_explain_pirate_mode(self, sample_file):
        result = runner.invoke(app, ["explain", str(sample_file), "--mode", "fun:pirate"])
        assert result.exit_code == 0

    def test_explain_json_output(self, sample_file):
        result = runner.invoke(app, ["explain", str(sample_file), "--output", "json"])
        assert result.exit_code == 0
        # JSON output should contain braces
        assert "{" in result.output

    def test_explain_save_to_file(self, sample_file, tmp_path):
        out_file = tmp_path / "explanation.md"
        result = runner.invoke(
            app, ["explain", str(sample_file), "--output", "markdown", "--save", str(out_file)]
        )
        assert result.exit_code == 0
        assert out_file.exists()


class TestAnalyzeCommand:
    def test_analyze_default(self, sample_file):
        result = runner.invoke(app, ["analyze", str(sample_file)])
        assert result.exit_code == 0

    def test_analyze_no_smells(self, sample_file):
        result = runner.invoke(app, ["analyze", str(sample_file), "--no-smells"])
        assert result.exit_code == 0

    def test_analyze_no_complexity(self, sample_file):
        result = runner.invoke(app, ["analyze", str(sample_file), "--no-complexity"])
        assert result.exit_code == 0

    def test_analyze_no_metrics(self, sample_file):
        result = runner.invoke(app, ["analyze", str(sample_file), "--no-metrics"])
        assert result.exit_code == 0


class TestVisualizeCommand:
    def test_visualize_default_tree(self, sample_file):
        result = runner.invoke(app, ["visualize", str(sample_file)])
        assert result.exit_code == 0

    def test_visualize_call_graph(self, sample_file):
        result = runner.invoke(app, ["visualize", str(sample_file), "--call-graph"])
        assert result.exit_code == 0

    def test_visualize_control_flow(self, sample_file):
        result = runner.invoke(app, ["visualize", str(sample_file), "--control-flow"])
        assert result.exit_code == 0

    def test_visualize_dependency_graph(self, sample_file):
        result = runner.invoke(app, ["visualize", str(sample_file), "--dependency-graph"])
        assert result.exit_code == 0


class TestReportCommand:
    def test_report_json(self, sample_file, tmp_path):
        out = tmp_path / "report.json"
        result = runner.invoke(
            app, ["report", str(sample_file), "--format", "json", "--output", str(out)]
        )
        assert result.exit_code == 0
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "{" in content

    def test_report_html(self, sample_file, tmp_path):
        out = tmp_path / "report.html"
        result = runner.invoke(
            app, ["report", str(sample_file), "--format", "html", "--output", str(out)]
        )
        assert result.exit_code == 0
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "<html" in content or "<!DOCTYPE" in content

    def test_report_markdown(self, sample_file, tmp_path):
        out = tmp_path / "report.md"
        result = runner.invoke(
            app, ["report", str(sample_file), "--format", "markdown", "--output", str(out)]
        )
        assert result.exit_code == 0
        assert out.exists()
