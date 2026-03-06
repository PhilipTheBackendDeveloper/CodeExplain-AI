"""
Call Graph Builder — Constructs a directed function call graph.

Nodes = function names. Edges = A calls B.
"""

import ast
from dataclasses import dataclass, field

try:
    import networkx as nx
    _HAS_NX = True
except ImportError:
    _HAS_NX = False


@dataclass
class CallEdge:
    caller: str
    callee: str


@dataclass
class CallGraphResult:
    """Result of call graph analysis."""
    nodes: list[str] = field(default_factory=list)
    edges: list[CallEdge] = field(default_factory=list)

    def to_adjacency(self) -> dict[str, list[str]]:
        """Return adjacency list representation."""
        adj: dict[str, list[str]] = {n: [] for n in self.nodes}
        for edge in self.edges:
            if edge.caller in adj:
                adj[edge.caller].append(edge.callee)
        return adj

    def to_networkx(self):
        """Return a networkx DiGraph (if networkx is available)."""
        if not _HAS_NX:
            raise ImportError("networkx is required: pip install networkx")
        G = nx.DiGraph()
        G.add_nodes_from(self.nodes)
        G.add_edges_from((e.caller, e.callee) for e in self.edges)
        return G

    def ascii_tree(self, root: str | None = None) -> str:
        """Render a simple ASCII call tree from the given root."""
        adj = self.to_adjacency()
        visited: set[str] = set()

        def _render(node: str, prefix: str = "", is_last: bool = True) -> list[str]:
            if node in visited:
                return [f"{prefix}{'└── ' if is_last else '├── '}{node} (...)"]
            visited.add(node)
            connector = "└── " if is_last else "├── "
            lines = [f"{prefix}{connector}{node}"]
            children = adj.get(node, [])
            child_prefix = prefix + ("    " if is_last else "│   ")
            for i, child in enumerate(children):
                lines.extend(_render(child, child_prefix, i == len(children) - 1))
            return lines

        # If no root, find nodes with no in-edges (true root functions)
        if root is None:
            called = {e.callee for e in self.edges}
            roots = [n for n in self.nodes if n not in called]
            if not roots:
                roots = self.nodes[:1]
        else:
            roots = [root]

        output = []
        for r in roots:
            output.extend(_render(r))
        return "\n".join(output) if output else "(empty graph)"


class CallGraphBuilder:
    """
    Builds a function call graph from a parsed Python module.

    Usage:
        builder = CallGraphBuilder()
        result = builder.build(parse_result)
    """

    def build(self, parse_result) -> CallGraphResult:
        """Build the call graph from an AST ParseResult."""
        tree = parse_result.tree
        function_names: set[str] = set()
        edges: list[CallEdge] = []

        # Collect all defined function names
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_names.add(node.name)

        # Find calls within each function
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                caller = node.name
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            callee = child.func.id
                            if callee in function_names and callee != caller:
                                edges.append(CallEdge(caller=caller, callee=callee))
                        elif isinstance(child.func, ast.Attribute):
                            callee = child.func.attr
                            if callee in function_names and callee != caller:
                                edges.append(CallEdge(caller=caller, callee=callee))

        # Deduplicate edges
        seen = set()
        unique_edges = []
        for edge in edges:
            key = (edge.caller, edge.callee)
            if key not in seen:
                seen.add(key)
                unique_edges.append(edge)

        return CallGraphResult(nodes=list(function_names), edges=unique_edges)
