"""
Beginner Mode — Jargon-free, friendly code explanations with analogies.
"""

from core.parser.node_mapper import FunctionNode, ClassNode, ModuleNode
from utils.helpers import snake_to_words, pluralize


def _friendly_name(name: str) -> str:
    return snake_to_words(name).title()


def explain_function_beginner(func: FunctionNode) -> str:
    """Explain a function in friendly, beginner-level language."""
    name = _friendly_name(func.name)
    real_args = [a for a in func.args if a.name not in ("self", "cls")]
    lines = []

    lines.append(f"🔧 **{name}**")
    lines.append(f"Think of this like a recipe or instruction set called '{func.name}'.")

    if not real_args:
        lines.append("It doesn't need any information to start — it works on its own.")
    elif len(real_args) == 1:
        lines.append(
            f"It needs one piece of information: '{real_args[0].name}' — like giving it an ingredient."
        )
    else:
        ingredients = ", ".join(f"'{a.name}'" for a in real_args)
        lines.append(
            f"It needs {len(real_args)} pieces of information ({ingredients}) — like ingredients for a recipe."
        )

    if func.has_return:
        lines.append("When it's done, it hands back a result — like a chef handing you a finished dish.")
    elif func.has_yield:
        lines.append("It produces results one-by-one, like a conveyor belt handing you items.")
    else:
        lines.append("It does its work without handing anything back — like a helper that cleans up quietly.")

    if func.is_async:
        lines.append("⚡ This is an 'async' function — it can do tasks in the background without blocking.")

    if func.docstring:
        lines.append(f"📖 The author says: \"{func.docstring.strip()[:150]}\"")

    return "\n".join(lines)


def explain_class_beginner(cls: ClassNode) -> str:
    """Explain a class in beginner terms."""
    name = _friendly_name(cls.name)
    lines = [f"📦 **{name}**"]
    lines.append(
        f"A class is like a blueprint or cookie cutter. "
        f"'{cls.name}' is a blueprint that can create objects."
    )
    if cls.bases:
        lines.append(
            f"It's based on '{cls.bases[0]}' — like a specialized version of a general concept."
        )
    method_count = len(cls.methods)
    if method_count:
        lines.append(
            f"It has {method_count} {pluralize(method_count, 'action', 'actions')} (called methods) "
            f"that the objects created from it can perform."
        )
    if cls.docstring:
        lines.append(f"📖 \"{cls.docstring.strip()[:150]}\"")
    return "\n".join(lines)


def explain_module_beginner(module: ModuleNode) -> str:
    """Explain the overall module in beginner terms."""
    lines = ["🗂️ **What does this file do?**"]
    if module.docstring:
        lines.append(f"The author says: \"{module.docstring.strip()[:200]}\"")
    else:
        lines.append("This is a Python file containing code that does one or more jobs.")

    if module.functions:
        lines.append(f"It has {len(module.functions)} action(s) (functions) it can perform.")
    if module.classes:
        lines.append(f"It defines {len(module.classes)} blueprint(s) (classes) for creating objects.")
    if module.imports:
        lines.append(
            f"It uses {len(module.imports)} external tool(s) — "
            "like importing a library book to help with a task."
        )
    return "\n".join(lines)


class BeginnerExplainer:
    """Generates beginner-friendly explanations."""

    def explain(self, module: ModuleNode) -> str:
        sections = [explain_module_beginner(module)]
        for cls in module.classes:
            sections.append(explain_class_beginner(cls))
        for func in module.functions:
            sections.append(explain_function_beginner(func))
        return "\n\n".join(sections)
