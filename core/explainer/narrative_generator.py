"""
Narrative Generator — Core natural language generation engine.

Converts CodeNode objects into human-readable narrative sentences using
template-based generation with placeholder interpolation.
"""

from utils.helpers import snake_to_words, camel_to_words, pluralize
from core.parser.node_mapper import FunctionNode, ClassNode, ModuleNode


def _describe_args(func: FunctionNode) -> str:
    """Generate a description of function arguments."""
    real_args = [a for a in func.args if a.name not in ("self", "cls")]
    if not real_args:
        return "no inputs"
    if len(real_args) == 1:
        return f"one input called '{real_args[0].name}'"
    names = ", ".join(f"'{a.name}'" for a in real_args[:-1])
    return f"{len(real_args)} inputs: {names} and '{real_args[-1].name}'"


def _describe_return(func: FunctionNode) -> str:
    if func.has_yield:
        return "yields values one at a time (it's a generator)"
    if func.has_return:
        if func.return_annotation:
            return f"returns a result of type {func.return_annotation}"
        return "returns a result"
    return "does not return a value"


def describe_function(func: FunctionNode, include_calls: bool = True) -> str:
    """Generate a plain English description of a function."""
    name_words = snake_to_words(func.name)
    arg_desc = _describe_args(func)
    return_desc = _describe_return(func)
    prefix = "async function" if func.is_async else ("method" if func.is_method else "function")

    parts = [f"The {prefix} '{func.name}' accepts {arg_desc} and {return_desc}."]

    if func.docstring:
        parts.append(f"According to its documentation: \"{func.docstring.strip()[:200]}\"")

    if func.has_raise:
        parts.append("It may raise an exception under certain conditions.")

    if include_calls and func.calls:
        call_list = ", ".join(f"'{c}'" for c in func.calls[:5])
        parts.append(f"It calls: {call_list}.")

    if func.decorators:
        dec_list = ", ".join(f"@{d}" for d in func.decorators[:3])
        parts.append(f"It is decorated with: {dec_list}.")

    return " ".join(parts)


def describe_class(cls: ClassNode) -> str:
    """Generate a plain English description of a class."""
    parts = [f"The class '{cls.name}'"]

    if cls.bases:
        bases_str = ", ".join(cls.bases[:3])
        parts.append(f"extends {bases_str}")

    parts[0] = " ".join(parts)

    if cls.docstring:
        parts = [f"The class '{cls.name}': \"{cls.docstring.strip()[:200]}\""]

    method_count = len(cls.methods)
    parts.append(f"It has {method_count} {pluralize(method_count, 'method')}.")

    if cls.class_variables:
        vars_str = ", ".join(f"'{v}'" for v in cls.class_variables[:5])
        parts.append(f"Class-level variables: {vars_str}.")

    return " ".join(parts)


def describe_module(module: ModuleNode) -> str:
    """Generate a high-level description of an entire module."""
    parts = []
    if module.docstring:
        parts.append(f"Module: \"{module.docstring.strip()[:300]}\"")
    else:
        parts.append(f"This module ('{module.filename}') contains Python source code.")

    fc = module.function_count
    cc = module.class_count
    ic = module.import_count

    summary = []
    if fc:
        summary.append(f"{fc} {pluralize(fc, 'function')}")
    if cc:
        summary.append(f"{cc} {pluralize(cc, 'class', 'classes')}")
    if ic:
        summary.append(f"{ic} {pluralize(ic, 'import')}")

    if summary:
        parts.append(f"It defines {', '.join(summary)}.")

    return " ".join(parts)
