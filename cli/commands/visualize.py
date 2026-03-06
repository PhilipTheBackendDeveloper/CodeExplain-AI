"""
Visualize Command — Render call graph, control flow, and dependency graphs.
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
    file: Path = typer.Argument(..., help="Python file to visualize", exists=True),
    call_graph: bool = typer.Option(False, "--call-graph", "-c", help="Show call graph"),
    control_flow: bool = typer.Option(False, "--control-flow", "-f", help="Show control flow"),
    dependency_graph: bool = typer.Option(False, "--dependency-graph", "-d", help="Show dependency graph"),
    module_tree: bool = typer.Option(True, "--tree/--no-tree", help="Show module tree"),
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

    mapper = NodeMapper()
    module = mapper.map(parse_result)

    # Module tree (always shown by default)
    if module_tree:
        tree = render_module_tree(module)
        console.print(tree)

    # Call graph
    if call_graph:
        builder = CallGraphBuilder()
        cg = builder.build(parse_result)
        if cg.edges:
            table = render_call_graph(cg)
            console.print(table)
            console.print(
                Panel(
                    cg.ascii_tree(),
                    title="[bold]Call Tree[/bold]",
                    border_style="green",
                    box=box.ROUNDED,
                )
            )
        else:
            console.print("[dim]No inter-function calls detected.[/dim]")

    # Control flow
    if control_flow:
        cfg_output = render_all_cfgs(parse_result)
        console.print(
            Panel(
                cfg_output,
                title="[bold]Control Flow Graphs[/bold]",
                border_style="magenta",
                box=box.ROUNDED,
            )
        )

    # Dependency graph
    if dependency_graph:
        dep_analyzer = DependencyAnalyzer()
        dep_report = dep_analyzer.analyze(parse_result)
        dep_builder = DependencyGraphBuilder()
        dep_graph = dep_builder.build(dep_report)
        console.print(
            Panel(
                dep_graph.ascii_tree(),
                title="[bold]Dependency Graph[/bold]",
                border_style="blue",
                box=box.ROUNDED,
            )
        )
