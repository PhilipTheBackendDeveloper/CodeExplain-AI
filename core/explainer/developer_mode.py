"""
Developer Mode — Technical, detail-rich code explanations.
"""

from core.parser.node_mapper import FunctionNode, ClassNode, ModuleNode
from core.explainer.narrative_generator import describe_function, describe_class, describe_module


def explain_function_developer(func: FunctionNode) -> str:
    """Generate a technical explanation of a function."""
    lines = [f"### `{func.signature}`"]
    lines.append(f"**Location:** Line {func.lineno} ({func.line_count} lines)")

    type_info = []
    for arg in func.args:
        if arg.name in ("self", "cls"):
            continue
        desc = arg.name
        if arg.annotation:
            desc += f": `{arg.annotation}`"
        if arg.default:
            desc += f" = `{arg.default}`"
        type_info.append(desc)
    if type_info:
        lines.append(f"**Parameters:** {', '.join(type_info)}")

    if func.return_annotation:
        lines.append(f"**Returns:** `{func.return_annotation}`")

    if func.decorators:
        lines.append(f"**Decorators:** {', '.join(f'`@{d}`' for d in func.decorators)}")

    behavior = []
    if func.is_async:
        behavior.append("async (awaitable)")
    if func.has_return:
        behavior.append("returns a value")
    if func.has_yield:
        behavior.append("is a generator")
    if func.has_raise:
        behavior.append("may raise exceptions")
    if behavior:
        lines.append(f"**Behavior:** {', '.join(behavior)}")

    if func.calls:
        call_list = ", ".join(f"`{c}`" for c in func.calls[:8])
        lines.append(f"**Calls:** {call_list}")

    if func.docstring:
        lines.append(f"\n*{func.docstring.strip()}*")

    return "\n".join(lines)


def explain_class_developer(cls: ClassNode) -> str:
    """Generate a technical explanation of a class."""
    lines = [f"### `class {cls.name}`"]
    if cls.bases:
        lines.append(f"**Inherits from:** {', '.join(f'`{b}`' for b in cls.bases)}")
    if cls.decorators:
        lines.append(f"**Decorators:** {', '.join(f'`@{d}`' for d in cls.decorators)}")
    if cls.class_variables:
        lines.append(f"**Class vars:** {', '.join(f'`{v}`' for v in cls.class_variables)}")
    lines.append(f"**Methods:** {len(cls.methods)}")
    if cls.is_abstract:
        lines.append("**Abstract:** Yes — must be subclassed")
    if cls.docstring:
        lines.append(f"\n*{cls.docstring.strip()}*")

    for method in cls.methods:
        lines.append("")
        lines.append(explain_function_developer(method))

    return "\n".join(lines)


def explain_module_developer(module: ModuleNode) -> str:
    """Generate a technical explanation of the full module."""
    lines = [f"## Module: `{module.filename}`"]
    if module.docstring:
        lines.append(f"*{module.docstring.strip()}*")
    lines.append(
        f"**Stats:** {module.line_count} lines | "
        f"{module.function_count} functions | "
        f"{module.class_count} classes | "
        f"{module.import_count} imports"
    )
    if module.imports:
        stdlib = [i.module for i in module.imports if i.is_stdlib]
        third = [i.module for i in module.imports if not i.is_stdlib]
        if stdlib:
            lines.append(f"**Stdlib deps:** {', '.join(f'`{m}`' for m in stdlib[:8])}")
        if third:
            lines.append(f"**Third-party deps:** {', '.join(f'`{m}`' for m in third[:8])}")
    return "\n".join(lines)


class DeveloperExplainer:
    """Generates technical, developer-focused explanations."""

    def explain(self, module: ModuleNode) -> str:
        sections = [explain_module_developer(module)]
        for cls in module.classes:
            sections.append(explain_class_developer(cls))
        for func in module.functions:
            sections.append(explain_function_developer(func))
        return "\n\n".join(sections)
