"""
ASCII Diagrams — Pure text tree and structure renderers.

Used for terminal output without Rich dependency.
"""

from core.parser.node_mapper import ModuleNode


def module_tree(module: ModuleNode) -> str:
    """Render a module structure as an ASCII tree."""
    lines = [f"📁 {module.filename}"]

    if module.imports:
        lines.append("│")
        lines.append("├── 📦 Imports")
        stdlib = [i for i in module.imports if i.is_stdlib]
        third = [i for i in module.imports if i.category == "third_party"]
        local = [i for i in module.imports if i.category == "local"]

        def _import_group(label: str, items) -> None:
            if items:
                lines.append(f"│   ├── [{label}]")
                for i in items[:6]:
                    lines.append(f"│   │    └── {i.module}")

        _import_group("stdlib", stdlib)
        _import_group("third-party", third)
        _import_group("local", local)

    if module.classes:
        lines.append("│")
        lines.append("├── 🏗️  Classes")
        for i, cls in enumerate(module.classes):
            is_last = i == len(module.classes) - 1
            connector = "└──" if is_last else "├──"
            lines.append(f"│   {connector} class {cls.name}")
            for j, method in enumerate(cls.methods[:5]):
                m_last = j == min(len(cls.methods), 5) - 1
                m_conn = "    └──" if m_last else "    ├──"
                lines.append(f"│   {' ' if is_last else '│'}{m_conn} def {method.name}()")

    if module.functions:
        lines.append("│")
        lines.append("└── ⚙️  Functions")
        for i, func in enumerate(module.functions):
            is_last = i == len(module.functions) - 1
            connector = "    └──" if is_last else "    ├──"
            async_mark = "async " if func.is_async else ""
            lines.append(f"{connector} {async_mark}def {func.name}()")

    return "\n".join(lines)


def function_signature_table(module: ModuleNode) -> str:
    """Render a simple table of all function signatures."""
    funcs = module.all_functions
    if not funcs:
        return "(no functions)"

    rows = []
    for f in funcs:
        args = ", ".join(a.name for a in f.args if a.name not in ("self", "cls"))
        ret = f" → {f.return_annotation}" if f.return_annotation else ""
        flag = "⚡" if f.is_async else ("🔁" if f.has_recursion else " ")
        rows.append(f"  {flag}  {f.name}({args}){ret}")

    header = "  FLAGS  FUNCTION SIGNATURE"
    separator = "  " + "-" * 60
    return "\n".join([header, separator] + rows)
