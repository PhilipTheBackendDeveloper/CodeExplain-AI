"""
Dependency Graph Builder — Module-level import dependency graph.
"""

from dataclasses import dataclass, field
from core.analyzer.dependency_analyzer import DependencyReport

try:
    import networkx as nx
    _HAS_NX = True
except ImportError:
    _HAS_NX = False


@dataclass
class DependencyGraphResult:
    """Result of dependency graph analysis."""
    source_module: str
    nodes: list[str] = field(default_factory=list)
    edges: list[tuple[str, str]] = field(default_factory=list)

    def ascii_tree(self) -> str:
        """Render imports as an ASCII dependency tree."""
        if not self.nodes:
            return "(no imports)"
        lines = [f"[{self.source_module}]"]
        stdlib = [(s, t) for s, t in self.edges if t.startswith("stdlib:")]
        third = [(s, t) for s, t in self.edges if t.startswith("third_party:")]
        local = [(s, t) for s, t in self.edges if t.startswith("local:")]
        other = [(s, t) for s, t in self.edges if not any(
            t.startswith(p) for p in ("stdlib:", "third_party:", "local:")
        )]

        def _render_group(label: str, items: list[tuple[str, str]]) -> None:
            if items:
                lines.append(f"  ├── [{label}]")
                for i, (_, module) in enumerate(items):
                    mod_name = module.split(":", 1)[-1] if ":" in module else module
                    connector = "└── " if i == len(items) - 1 else "├── "
                    lines.append(f"  │   {connector}{mod_name}")

        _render_group("Standard Library", stdlib)
        _render_group("Third Party", third)
        _render_group("Local", local)
        _render_group("Unknown", other)
        return "\n".join(lines)


class DependencyGraphBuilder:
    """
    Builds a module dependency graph from a DependencyReport.

    Usage:
        builder = DependencyGraphBuilder()
        result = builder.build(dep_report, source_module="my_module")
    """

    def build(self, dep_report: DependencyReport) -> DependencyGraphResult:
        source = dep_report.filename
        nodes = [source]
        edges = []

        for dep in dep_report.dependencies:
            node_id = f"{dep.category}:{dep.module}"
            if node_id not in nodes:
                nodes.append(node_id)
            edges.append((source, node_id))

        return DependencyGraphResult(source_module=source, nodes=nodes, edges=edges)
