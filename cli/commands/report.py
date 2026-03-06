"""
Report Command — Generate full analysis reports in HTML/JSON/Markdown.
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

app = typer.Typer()
console = Console()


@app.command()
def main(
    file: Path = typer.Argument(..., help="Python file to report on", exists=True),
    format: str = typer.Option("html", "--format", "-f", help="Output format: html | json | markdown"),
    output: Path = typer.Option(None, "--output", "-o", help="Output file path"),
    mode: str = typer.Option("developer", "--mode", "-m", help="Explanation mode"),
    open_browser: bool = typer.Option(False, "--open", help="Open HTML report in browser"),
) -> None:
    """📄 Generate a full analysis report for a Python file."""
    from core.parser.ast_parser import ASTParser
    from core.parser.node_mapper import NodeMapper
    from core.analyzer.complexity_analyzer import ComplexityAnalyzer
    from core.analyzer.code_smells import CodeSmellDetector
    from core.analyzer.metrics import MetricsComputer
    from core.explainer.explanation_engine import ExplanationEngine
    from core.scoring.difficulty_score import DifficultyScorer
    from core.scoring.maintainability_score import MaintainabilityScorer
    from utils.formatter import to_html, to_json, to_markdown

    console.print(f"\n[bold cyan]📄 Generating {format.upper()} Report:[/bold cyan] [white]{file}[/white]\n")

    parser = ASTParser()
    parse_result = parser.parse_file(file)

    if not parse_result.success:
        for err in parse_result.errors:
            console.print(f"[red]❌ {err}[/red]")
        raise typer.Exit(1)

    mapper = NodeMapper()
    module = mapper.map(parse_result)

    metrics_comp = MetricsComputer()
    m = metrics_comp.compute(parse_result)

    complexity_analyzer = ComplexityAnalyzer()
    complexity = complexity_analyzer.analyze(parse_result)

    smell_detector = CodeSmellDetector()
    smells = smell_detector.detect(parse_result)

    engine = ExplanationEngine()
    explanation = engine.explain(module, mode=mode)

    diff = DifficultyScorer().score(complexity, smells_count=smells.total_count)
    maint = MaintainabilityScorer().score(m, complexity)

    data = {
        "file": str(file),
        "metrics": {
            **m.summary(),
            "async_function_count": m.async_function_count,
        },
        "complexity": {
            "overall_label": complexity.overall_label,
            "average_complexity": round(complexity.average_complexity, 2),
            "max_complexity": complexity.max_complexity,
            "functions": [
                {
                    "name": f.name,
                    "cyclomatic_complexity": f.cyclomatic_complexity,
                    "nesting_depth": f.nesting_depth,
                    "loop_count": f.loop_count,
                    "has_recursion": f.has_recursion,
                    "complexity_label": f.complexity_label,
                }
                for f in complexity.functions
            ],
        },
        "smells": [
            {"kind": s.kind, "severity": s.severity, "message": s.message, "lineno": s.lineno}
            for s in smells.smells
        ],
        "explanation": explanation,
        "scores": {"difficulty": round(diff.score, 1), "maintainability": maint.rounded},
    }

    if format == "html":
        content = to_html(data)
        ext = ".html"
    elif format == "json":
        content = to_json(data)
        ext = ".json"
    elif format == "markdown":
        content = to_markdown(data)
        ext = ".md"
    else:
        console.print(f"[red]Unknown format '{format}'. Use: html | json | markdown[/red]")
        raise typer.Exit(1)

    if output is None:
        stem = Path(file).stem
        output = Path(f"report_{stem}{ext}")

    output.write_text(content, encoding="utf-8")
    console.print(
        Panel(
            f"[bold green]✅ Report saved to:[/bold green] [cyan]{output.resolve()}[/cyan]\n"
            f"  Format: {format.upper()}\n"
            f"  Size: {len(content):,} bytes",
            border_style="green",
        )
    )

    if open_browser and format == "html":
        import webbrowser
        webbrowser.open(str(output.resolve()))
