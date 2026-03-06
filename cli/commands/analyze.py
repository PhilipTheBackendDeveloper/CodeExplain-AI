"""
Analyze Command — Run complexity, smell, and metric analysis on Python files.
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich import box

app = typer.Typer()
console = Console()


@app.command()
def main(
    file: Path = typer.Argument(..., help="Python file to analyze", exists=True),
    smells: bool = typer.Option(True, "--smells/--no-smells", help="Detect code smells"),
    complexity: bool = typer.Option(True, "--complexity/--no-complexity", help="Compute complexity"),
    metrics: bool = typer.Option(True, "--metrics/--no-metrics", help="Compute code metrics"),
    scores: bool = typer.Option(True, "--scores/--no-scores", help="Show difficulty/maintainability scores"),
) -> None:
    """🔍 Analyze a Python file for complexity, smells, and metrics."""
    from core.parser.ast_parser import ASTParser
    from core.parser.node_mapper import NodeMapper
    from core.analyzer.complexity_analyzer import ComplexityAnalyzer
    from core.analyzer.code_smells import CodeSmellDetector
    from core.analyzer.metrics import MetricsComputer
    from core.scoring.difficulty_score import DifficultyScorer
    from core.scoring.maintainability_score import MaintainabilityScorer
    from visualization.graph_renderer import render_complexity_table

    console.print(f"\n[bold cyan]🔍 Analyzing:[/bold cyan] [white]{file}[/white]\n")

    parser = ASTParser()
    parse_result = parser.parse_file(file)

    if not parse_result.success:
        for err in parse_result.errors:
            console.print(f"[red]❌ {err}[/red]")
        raise typer.Exit(1)

    # ── Metrics ──────────────────────────────────────────────────────────────
    if metrics:
        from core.analyzer.metrics import MetricsComputer
        mc = MetricsComputer()
        m = mc.compute(parse_result)
        from rich.table import Table
        tbl = Table(title="📊 Code Metrics", box=box.ROUNDED, border_style="blue")
        tbl.add_column("Metric", style="bold")
        tbl.add_column("Value", style="cyan", justify="right")
        tbl.add_row("Total Lines", str(m.total_lines))
        tbl.add_row("Source Lines (SLOC)", str(m.source_lines))
        tbl.add_row("Blank Lines", str(m.blank_lines))
        tbl.add_row("Comment Lines", str(m.comment_lines))
        tbl.add_row("Comment Ratio", f"{m.comment_ratio * 100:.1f}%")
        tbl.add_row("Functions", str(m.function_count))
        tbl.add_row("Async Functions", str(m.async_function_count))
        tbl.add_row("Classes", str(m.class_count))
        tbl.add_row("Imports", str(m.import_count))
        tbl.add_row("Halstead Volume", f"{m.halstead_volume:.1f}")
        console.print(tbl)

    # ── Complexity ────────────────────────────────────────────────────────────
    complexity_result = None
    if complexity:
        ca = ComplexityAnalyzer()
        complexity_result = ca.analyze(parse_result)
        tbl = render_complexity_table(complexity_result.functions)
        console.print(tbl)
        console.print(
            f"\n  Overall: [bold]{complexity_result.overall_label}[/bold] | "
            f"Avg CC: [cyan]{complexity_result.average_complexity:.1f}[/cyan] | "
            f"Max CC: [cyan]{complexity_result.max_complexity}[/cyan]\n"
        )

    # ── Code Smells ───────────────────────────────────────────────────────────
    smell_result = None
    if smells:
        detector = CodeSmellDetector()
        smell_result = detector.detect(parse_result)
        if smell_result.smells:
            console.print(
                Panel(
                    "\n".join(
                        f"  {s.severity_emoji} [L{s.lineno}] {s.message}"
                        for s in smell_result.smells
                    ),
                    title=f"[bold]🔍 Code Smells ({smell_result.total_count} found)[/bold]",
                    border_style="yellow",
                    box=box.ROUNDED,
                )
            )
        else:
            console.print("[green]✅ No code smells detected![/green]")

    # ── Scores ────────────────────────────────────────────────────────────────
    if scores and complexity_result:
        from rich.table import Table
        mc2 = MetricsComputer()
        m2 = mc2.compute(parse_result)

        diff_scorer = DifficultyScorer()
        smells_count = smell_result.total_count if smell_result else 0
        diff = diff_scorer.score(complexity_result, smells_count=smells_count)

        maint_scorer = MaintainabilityScorer()
        maint = maint_scorer.score(m2, complexity_result)

        score_tbl = Table(title="🎯 Scores", box=box.ROUNDED, border_style="magenta")
        score_tbl.add_column("Score", style="bold")
        score_tbl.add_column("Value", justify="center")
        score_tbl.add_column("Label", justify="center")
        score_tbl.add_row(
            "Difficulty",
            f"[bold red]{diff.rounded}/10[/bold red]",
            f"{diff.emoji} {diff.label}",
        )
        score_tbl.add_row(
            "Maintainability",
            f"[bold green]{maint.rounded}/100[/bold green]",
            f"{maint.emoji} {maint.label}",
        )
        console.print(score_tbl)
