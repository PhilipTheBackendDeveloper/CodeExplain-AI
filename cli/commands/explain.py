"""
Explain Command — Generate human-readable explanations for Python files.
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box

app = typer.Typer()
console = Console()


@app.command()
def main(
    file: Path = typer.Argument(..., help="Python file to explain", exists=True),
    mode: str = typer.Option(
        "developer",
        "--mode", "-m",
        help="Explanation mode: developer | beginner | fun:pirate | fun:shakespeare | fun:eli5",
    ),
    output: str = typer.Option(
        "cli",
        "--output", "-o",
        help="Output format: cli | json | markdown",
    ),
    save: Path = typer.Option(None, "--save", "-s", help="Save output to file"),
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

        mapper = NodeMapper()
        module = mapper.map(parse_result)

        engine = ExplanationEngine()
        explanation = engine.explain(module, mode=mode)

        if output == "cli":
            console.print(
                Panel(
                    Markdown(explanation),
                    title=f"[bold]Explanation ({mode})[/bold]",
                    border_style="cyan",
                    box=box.ROUNDED,
                )
            )
        elif output == "json":
            import json
            result = json.dumps({"file": str(file), "mode": mode, "explanation": explanation}, indent=2)
            console.print(result)
            if save:
                save.write_text(result)
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
