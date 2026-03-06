"""
Graph Renderer — Rich-based tree and panel visualizations.

Uses Rich's Tree widget for colorized, Unicode-bordered output.
"""

from rich.tree import Tree
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from core.parser.node_mapper import ModuleNode
from core.graph.call_graph import CallGraphResult


console = Console()


def render_module_tree(module: ModuleNode) -> Tree:
    """Render a Rich tree showing module structure."""
    root = Tree(
        f"[bold cyan]📁 {module.filename}[/bold cyan]",
        guide_style="dim cyan",
    )

    if module.imports:
        imp_branch = root.add("[bold yellow]📦 Imports[/bold yellow]")
        for imp in module.imports[:10]:
            category_color = "blue" if imp.is_stdlib else "magenta"
            label = imp.module
            if imp.names:
                label += f" → {', '.join(imp.names[:3])}"
            imp_branch.add(f"[{category_color}]{label}[/{category_color}]")

    if module.classes:
        cls_branch = root.add("[bold magenta]🏗️  Classes[/bold magenta]")
        for cls in module.classes:
            cls_node = cls_branch.add(f"[magenta]class [bold]{cls.name}[/bold][/magenta]")
            for method in cls.methods[:8]:
                flag = "⚡ " if method.is_async else ""
                cls_node.add(f"[blue]{flag}def {method.name}()[/blue]")

    if module.functions:
        fn_branch = root.add("[bold green]⚙️  Functions[/bold green]")
        for func in module.functions:
            flag = "⚡ " if func.is_async else ""
            rec = " [dim red](recursive)[/dim red]" if func.has_recursion else ""
            fn_branch.add(f"[green]{flag}def [bold]{func.name}()[/bold]{rec}[/green]")

    return root


def render_call_graph(call_graph: CallGraphResult) -> Table:
    """Render a call graph as a Rich table."""
    table = Table(title="📞 Call Graph", box=box.ROUNDED, border_style="cyan")
    table.add_column("Caller", style="bold green", no_wrap=True)
    table.add_column("→ Calls", style="cyan")

    adj = call_graph.to_adjacency()
    for caller, callees in sorted(adj.items()):
        if callees:
            table.add_row(caller, ", ".join(callees))
        else:
            table.add_row(f"[dim]{caller}[/dim]", "[dim](no outbound calls)[/dim]")

    return table


def render_complexity_table(functions) -> Table:
    """Render a complexity table for all functions."""
    table = Table(title="🔄 Complexity Analysis", box=box.ROUNDED, border_style="yellow")
    table.add_column("Function", style="bold")
    table.add_column("CC", justify="center")
    table.add_column("Depth", justify="center")
    table.add_column("Loops", justify="center")
    table.add_column("Recursive", justify="center")
    table.add_column("Level", justify="center")

    for f in functions:
        cc_color = "green" if f.cyclomatic_complexity <= 5 else (
            "yellow" if f.cyclomatic_complexity <= 10 else "red"
        )
        table.add_row(
            f.name,
            f"[{cc_color}]{f.cyclomatic_complexity}[/{cc_color}]",
            str(f.nesting_depth),
            str(f.loop_count),
            "🔁" if f.has_recursion else "—",
            f"[{cc_color}]{f.complexity_label}[/{cc_color}]",
        )
    return table
