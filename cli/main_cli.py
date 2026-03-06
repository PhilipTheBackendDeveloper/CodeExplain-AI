"""
Main CLI — Entry point for CodeExplain AI command-line interface.

Features:
- pyfiglet banner
- Rich-styled output panels
- Commands: explain, analyze, visualize, report, serve
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box
from typing import Optional

try:
    from pyfiglet import figlet_format
    _HAS_FIGLET = True
except ImportError:
    _HAS_FIGLET = False

try:
    from colorama import init as colorama_init
    colorama_init()
except ImportError:
    pass

app = typer.Typer(
    name="codeexplain",
    help="🧠 CodeExplain AI — Static code analysis and explanation engine",
    add_completion=False,
    rich_markup_mode="rich",
    pretty_exceptions_show_locals=False,
)

console = Console()


def _print_banner() -> None:
    if _HAS_FIGLET:
        try:
            banner = figlet_format("CodeExplain AI", font="slant")
        except Exception:
            banner = "CodeExplain AI"
        console.print(f"[bold cyan]{banner}[/bold cyan]", highlight=False)
    console.print(
        Panel(
            "[bold white]Professional Static Code Analysis & Explanation Engine[/bold white]\n"
            "[dim]Version 1.0.0 | Python AST-powered | Fully Offline[/dim]",
            border_style="cyan",
            box=box.ROUNDED,
            expand=False,
        )
    )


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context) -> None:
    """🧠 CodeExplain AI — Understand any Python file instantly."""
    if ctx.invoked_subcommand is None:
        _print_banner()
        console.print("\n[bold]Available Commands:[/bold]")
        console.print("  [cyan]explain[/cyan]    Explain code in human language")
        console.print("  [cyan]analyze[/cyan]    Analyze complexity and code smells")
        console.print("  [cyan]visualize[/cyan]  Visualize code structure and flow")
        console.print("  [cyan]report[/cyan]     Generate HTML/JSON/Markdown reports")
        console.print("  [cyan]serve[/cyan]      Start the local API server")
        console.print("\n[dim]Run 'codeexplain <command> --help' for details.[/dim]")


@app.command("explain")
def explain(
    file: Path = typer.Argument(..., help="Python file to explain", exists=True),
    mode: str = typer.Option(
        "developer", "--mode", "-m",
        help="Mode: developer | beginner | fun:pirate | fun:shakespeare | fun:eli5",
    ),
    output: str = typer.Option(
        "cli", "--output", "-o",
        help="Output format: cli | json | markdown",
    ),
    save: Optional[Path] = typer.Option(None, "--save", "-s", help="Save output to file"),
) -> None:
    """📖 Explain a Python file in human-readable language."""
    from core.parser.ast_parser import ASTParser
    from core.parser.node_mapper import NodeMapper
    from core.explainer.explanation_engine import ExplanationEngine

    console.print(f"\n[bold cyan]🧠 Explaining:[/bold cyan] [white]{file}[/white]")
    console.print(f"[dim]Mode: {mode}[/dim]\n")

    try:
        parser = ASTParser()
        parse_result = parser.parse_file(file)

        if not parse_result.success:
            for err in parse_result.errors:
                console.print(f"[red]❌ Parse error: {err}[/red]")
            raise typer.Exit(1)

        module = NodeMapper().map(parse_result)
        engine = ExplanationEngine()
        explanation = engine.explain(module, mode=mode)

        if output == "cli":
            console.print(
                Panel(Markdown(explanation), title=f"[bold]Explanation ({mode})[/bold]",
                      border_style="cyan", box=box.ROUNDED)
            )
        elif output == "json":
            import json
            content = json.dumps({"file": str(file), "mode": mode, "explanation": explanation}, indent=2)
            console.print(content)
            if save:
                save.write_text(content)
        elif output == "markdown":
            if save:
                save.write_text(explanation)
                console.print(f"[green]✅ Saved to {save}[/green]")
            else:
                console.print(explanation)

        if save and output == "cli":
            save.write_text(explanation)
            console.print(f"[green]✅ Saved to {save}[/green]")

    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(1)


@app.command("analyze")
def analyze(
    file: Path = typer.Argument(..., help="Python file to analyze", exists=True),
    smells: bool = typer.Option(True, "--smells/--no-smells"),
    complexity: bool = typer.Option(True, "--complexity/--no-complexity"),
    metrics: bool = typer.Option(True, "--metrics/--no-metrics"),
    scores: bool = typer.Option(True, "--scores/--no-scores"),
) -> None:
    """🔍 Analyze a Python file for complexity, smells, and metrics."""
    from core.parser.ast_parser import ASTParser
    from core.analyzer.complexity_analyzer import ComplexityAnalyzer
    from core.analyzer.code_smells import CodeSmellDetector
    from core.analyzer.metrics import MetricsComputer
    from core.scoring.difficulty_score import DifficultyScorer
    from core.scoring.maintainability_score import MaintainabilityScorer
    from visualization.graph_renderer import render_complexity_table
    from rich.table import Table

    console.print(f"\n[bold cyan]🔍 Analyzing:[/bold cyan] [white]{file}[/white]\n")

    parser = ASTParser()
    parse_result = parser.parse_file(file)
    if not parse_result.success:
        for err in parse_result.errors:
            console.print(f"[red]❌ {err}[/red]")
        raise typer.Exit(1)

    if metrics:
        m = MetricsComputer().compute(parse_result)
        tbl = Table(title="📊 Code Metrics", box=box.ROUNDED, border_style="blue")
        tbl.add_column("Metric", style="bold")
        tbl.add_column("Value", style="cyan", justify="right")
        for k, v in [("Total Lines", m.total_lines), ("SLOC", m.source_lines),
                     ("Functions", m.function_count), ("Classes", m.class_count),
                     ("Comment Ratio", f"{m.comment_ratio*100:.1f}%"),
                     ("Halstead Volume", f"{m.halstead_volume:.1f}")]:
            tbl.add_row(k, str(v))
        console.print(tbl)

    complexity_result = None
    if complexity:
        complexity_result = ComplexityAnalyzer().analyze(parse_result)
        console.print(render_complexity_table(complexity_result.functions))
        console.print(f"  Overall: [bold]{complexity_result.overall_label}[/bold] | "
                      f"Avg CC: [cyan]{complexity_result.average_complexity:.1f}[/cyan]\n")

    smell_result = None
    if smells:
        smell_result = CodeSmellDetector().detect(parse_result)
        if smell_result.smells:
            console.print(Panel(
                "\n".join(f"  {s.severity_emoji} [L{s.lineno}] {s.message}" for s in smell_result.smells),
                title=f"[bold]🔍 Code Smells ({smell_result.total_count})[/bold]",
                border_style="yellow", box=box.ROUNDED,
            ))
        else:
            console.print("[green]✅ No code smells detected![/green]")

    if scores and complexity_result:
        m2 = MetricsComputer().compute(parse_result)
        smells_count = smell_result.total_count if smell_result else 0
        diff = DifficultyScorer().score(complexity_result, smells_count=smells_count)
        maint = MaintainabilityScorer().score(m2, complexity_result)
        score_tbl = Table(title="🎯 Scores", box=box.ROUNDED, border_style="magenta")
        score_tbl.add_column("Score", style="bold")
        score_tbl.add_column("Value", justify="center")
        score_tbl.add_column("Label", justify="center")
        score_tbl.add_row("Difficulty", f"[bold red]{diff.rounded}/10[/bold red]", f"{diff.emoji} {diff.label}")
        score_tbl.add_row("Maintainability", f"[bold green]{maint.rounded}/100[/bold green]", f"{maint.emoji} {maint.label}")
        console.print(score_tbl)


@app.command("visualize")
def visualize(
    file: Path = typer.Argument(..., help="Python file to visualize", exists=True),
    call_graph: bool = typer.Option(False, "--call-graph", "-c"),
    control_flow: bool = typer.Option(False, "--control-flow", "-f"),
    dependency_graph: bool = typer.Option(False, "--dependency-graph", "-d"),
    module_tree: bool = typer.Option(True, "--tree/--no-tree"),
) -> None:
    """🌐 Visualize code structure, call graph, and control flow."""
    from core.parser.ast_parser import ASTParser
    from core.parser.node_mapper import NodeMapper
    from core.graph.call_graph import CallGraphBuilder
    from core.graph.dependency_graph import DependencyGraphBuilder
    from core.analyzer.dependency_analyzer import DependencyAnalyzer
    from visualization.graph_renderer import render_module_tree, render_call_graph
    from visualization.flow_visualizer import render_all_cfgs

    console.print(f"\n[bold cyan]🌐 Visualizing:[/bold cyan] [white]{file}[/white]\n")

    parser = ASTParser()
    parse_result = parser.parse_file(file)
    if not parse_result.success:
        for err in parse_result.errors:
            console.print(f"[red]❌ {err}[/red]")
        raise typer.Exit(1)

    module = NodeMapper().map(parse_result)

    if module_tree:
        console.print(render_module_tree(module))

    if call_graph:
        cg = CallGraphBuilder().build(parse_result)
        if cg.edges:
            console.print(render_call_graph(cg))
            console.print(Panel(cg.ascii_tree(), title="[bold]Call Tree[/bold]",
                                border_style="green", box=box.ROUNDED))
        else:
            console.print("[dim]No inter-function calls detected.[/dim]")

    if control_flow:
        console.print(Panel(render_all_cfgs(parse_result), title="[bold]Control Flow[/bold]",
                            border_style="magenta", box=box.ROUNDED))

    if dependency_graph:
        dep_report = DependencyAnalyzer().analyze(parse_result)
        dep_graph = DependencyGraphBuilder().build(dep_report)
        console.print(Panel(dep_graph.ascii_tree(), title="[bold]Dependencies[/bold]",
                            border_style="blue", box=box.ROUNDED))


@app.command("report")
def report(
    file: Path = typer.Argument(..., help="Python file to report on", exists=True),
    format: str = typer.Option("html", "--format", "-f", help="html | json | markdown"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    mode: str = typer.Option("developer", "--mode", "-m"),
    open_browser: bool = typer.Option(False, "--open"),
) -> None:
    """📄 Generate a full analysis report."""
    from core.parser.ast_parser import ASTParser
    from core.parser.node_mapper import NodeMapper
    from core.analyzer.complexity_analyzer import ComplexityAnalyzer
    from core.analyzer.code_smells import CodeSmellDetector
    from core.analyzer.metrics import MetricsComputer
    from core.explainer.explanation_engine import ExplanationEngine
    from core.scoring.difficulty_score import DifficultyScorer
    from core.scoring.maintainability_score import MaintainabilityScorer
    from utils.formatter import to_html, to_json, to_markdown

    console.print(f"\n[bold cyan]📄 {format.upper()} Report:[/bold cyan] [white]{file}[/white]\n")

    parser = ASTParser()
    parse_result = parser.parse_file(file)
    if not parse_result.success:
        for err in parse_result.errors:
            console.print(f"[red]❌ {err}[/red]")
        raise typer.Exit(1)

    module = NodeMapper().map(parse_result)
    m = MetricsComputer().compute(parse_result)
    complexity = ComplexityAnalyzer().analyze(parse_result)
    smells = CodeSmellDetector().detect(parse_result)
    explanation = ExplanationEngine().explain(module, mode=mode)
    diff = DifficultyScorer().score(complexity, smells_count=smells.total_count)
    maint = MaintainabilityScorer().score(m, complexity)

    data = {
        "file": str(file),
        "metrics": {**m.summary(), "async_function_count": m.async_function_count},
        "complexity": {
            "overall_label": complexity.overall_label,
            "average_complexity": round(complexity.average_complexity, 2),
            "max_complexity": complexity.max_complexity,
            "functions": [
                {"name": f.name, "cyclomatic_complexity": f.cyclomatic_complexity,
                 "nesting_depth": f.nesting_depth, "loop_count": f.loop_count,
                 "has_recursion": f.has_recursion, "complexity_label": f.complexity_label}
                for f in complexity.functions
            ],
        },
        "smells": [{"kind": s.kind, "severity": s.severity, "message": s.message, "lineno": s.lineno}
                   for s in smells.smells],
        "explanation": explanation,
        "scores": {"difficulty": round(diff.score, 1), "maintainability": maint.rounded},
    }

    fmt = format.lower()
    if fmt == "html":
        content, ext = to_html(data), ".html"
    elif fmt == "json":
        content, ext = to_json(data), ".json"
    elif fmt == "markdown":
        content, ext = to_markdown(data), ".md"
    else:
        console.print(f"[red]Unknown format '{fmt}'[/red]")
        raise typer.Exit(1)

    out_path = output or Path(f"report_{Path(file).stem}{ext}")
    out_path.write_text(content, encoding="utf-8")
    console.print(Panel(
        f"[bold green]✅ Report saved:[/bold green] [cyan]{out_path.resolve()}[/cyan]\n"
        f"  Size: {len(content):,} bytes",
        border_style="green",
    ))

    if open_browser and fmt == "html":
        import webbrowser
        webbrowser.open(str(out_path.resolve()))


@app.command("serve")
def serve(
    host: str = typer.Option("127.0.0.1", help="API server host"),
    port: int = typer.Option(8000, help="API server port"),
) -> None:
    """🌐 Start the CodeExplain AI local API server."""
    try:
        import uvicorn
        from api.local_api import create_app
        console.print(Panel(
            f"[bold green]🚀 Starting API Server[/bold green]\n"
            f"  URL: [cyan]http://{host}:{port}[/cyan]\n"
            f"  Docs: [cyan]http://{host}:{port}/docs[/cyan]",
            border_style="green", box=box.ROUNDED,
        ))
        uvicorn.run(create_app(), host=host, port=port, log_level="info")
    except ImportError:
        console.print("[red]❌ uvicorn not installed. Run: pip install uvicorn[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
