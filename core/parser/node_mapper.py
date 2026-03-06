"""
Node Mapper — Maps raw AST nodes to structured semantic CodeNode objects.

Provides a clean, typed representation of code structure that analyzers
and explainers can consume without directly handling raw AST internals.
"""

import ast
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ArgumentInfo:
    """Represents a single function argument."""
    name: str
    annotation: Optional[str] = None
    default: Optional[str] = None
    kind: str = "positional"  # positional | keyword | vararg | kwarg


@dataclass
class FunctionNode:
    """Semantic representation of a function or method definition."""
    name: str
    lineno: int
    end_lineno: int
    args: list[ArgumentInfo] = field(default_factory=list)
    return_annotation: Optional[str] = None
    docstring: Optional[str] = None
    decorators: list[str] = field(default_factory=list)
    is_async: bool = False
    is_method: bool = False
    calls: list[str] = field(default_factory=list)  # functions this function calls
    has_return: bool = False
    has_yield: bool = False
    has_raise: bool = False
    has_recursion: bool = False

    @property
    def line_count(self) -> int:
        return (self.end_lineno or self.lineno) - self.lineno + 1

    @property
    def arg_count(self) -> int:
        return len(self.args)

    @property
    def signature(self) -> str:
        args_str = ", ".join(
            f"{a.annotation + ' ' if a.annotation else ''}{a.name}"
            + (f"={a.default}" if a.default else "")
            for a in self.args
        )
        ret = f" -> {self.return_annotation}" if self.return_annotation else ""
        prefix = "async def" if self.is_async else "def"
        return f"{prefix} {self.name}({args_str}){ret}"


@dataclass
class ClassNode:
    """Semantic representation of a class definition."""
    name: str
    lineno: int
    end_lineno: int
    bases: list[str] = field(default_factory=list)
    docstring: Optional[str] = None
    decorators: list[str] = field(default_factory=list)
    methods: list[FunctionNode] = field(default_factory=list)
    class_variables: list[str] = field(default_factory=list)

    @property
    def method_count(self) -> int:
        return len(self.methods)

    @property
    def is_abstract(self) -> bool:
        return "ABC" in self.bases or "ABCMeta" in self.bases

    @property
    def inherits_from(self) -> list[str]:
        return [b for b in self.bases if b not in ("object",)]


@dataclass
class ImportNode:
    """Semantic representation of an import statement."""
    module: str
    alias: Optional[str] = None
    names: list[str] = field(default_factory=list)  # for "from x import a, b"
    lineno: int = 0
    is_from_import: bool = False
    is_stdlib: bool = False
    is_third_party: bool = False


@dataclass
class ModuleNode:
    """Top-level semantic representation of a parsed Python module."""
    filename: str
    source: str
    docstring: Optional[str] = None
    functions: list[FunctionNode] = field(default_factory=list)
    classes: list[ClassNode] = field(default_factory=list)
    imports: list[ImportNode] = field(default_factory=list)
    global_variables: list[str] = field(default_factory=list)
    line_count: int = 0

    @property
    def function_count(self) -> int:
        return len(self.functions)

    @property
    def class_count(self) -> int:
        return len(self.classes)

    @property
    def import_count(self) -> int:
        return len(self.imports)

    @property
    def all_functions(self) -> list[FunctionNode]:
        """All functions including class methods."""
        funcs = list(self.functions)
        for cls in self.classes:
            funcs.extend(cls.methods)
        return funcs


# ── Standard library module names (partial list for detection) ──────────────
_STDLIB_MODULES = {
    "abc", "ast", "asyncio", "builtins", "collections", "contextlib",
    "copy", "csv", "dataclasses", "datetime", "decimal", "enum", "functools",
    "gc", "glob", "hashlib", "hmac", "http", "importlib", "inspect", "io",
    "itertools", "json", "logging", "math", "mimetypes", "operator", "os",
    "pathlib", "pickle", "platform", "pprint", "queue", "random", "re",
    "shutil", "signal", "socket", "sqlite3", "ssl", "stat", "string",
    "struct", "subprocess", "sys", "tempfile", "textwrap", "threading",
    "time", "traceback", "typing", "unicodedata", "unittest", "urllib",
    "uuid", "warnings", "weakref", "xml", "zipfile",
}


def _annotation_to_str(node: Optional[ast.expr]) -> Optional[str]:
    """Convert an annotation AST node to a string representation."""
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:
        return None


def _get_docstring(node: ast.AST) -> Optional[str]:
    """Extract docstring from a function/class/module node."""
    return ast.get_docstring(node)


def _is_recursive(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Detect direct recursion by looking for self-calls."""
    name = node.name
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name) and child.func.id == name:
                return True
    return False


def _map_arguments(args: ast.arguments) -> list[ArgumentInfo]:
    """Map ast.arguments to a list of ArgumentInfo objects."""
    result: list[ArgumentInfo] = []
    defaults = args.defaults
    offset = len(args.args) - len(defaults)

    for i, arg in enumerate(args.args):
        default_node = defaults[i - offset] if i >= offset else None
        default_str = ast.unparse(default_node) if default_node else None
        result.append(ArgumentInfo(
            name=arg.arg,
            annotation=_annotation_to_str(arg.annotation),
            default=default_str,
            kind="positional",
        ))

    if args.vararg:
        result.append(ArgumentInfo(name=args.vararg.arg, kind="vararg"))

    for kwarg in args.kwonlyargs:
        result.append(ArgumentInfo(name=kwarg.arg, kind="keyword"))

    if args.kwarg:
        result.append(ArgumentInfo(name=args.kwarg.arg, kind="kwarg"))

    return result


def _get_calls(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """Extract names of all functions called inside this function."""
    calls = []
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.append(f"{ast.unparse(node.func.value)}.{node.func.attr}")
    return list(dict.fromkeys(calls))  # deduplicated, preserving order


def _map_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    is_method: bool = False
) -> FunctionNode:
    """Map an AST FunctionDef node to a FunctionNode."""
    has_return = any(
        isinstance(n, ast.Return) and n.value is not None for n in ast.walk(node)
    )
    has_yield = any(isinstance(n, (ast.Yield, ast.YieldFrom)) for n in ast.walk(node))
    has_raise = any(isinstance(n, ast.Raise) for n in ast.walk(node))
    decorators = [ast.unparse(d) for d in node.decorator_list]

    return FunctionNode(
        name=node.name,
        lineno=node.lineno,
        end_lineno=getattr(node, "end_lineno", node.lineno),
        args=_map_arguments(node.args),
        return_annotation=_annotation_to_str(node.returns),
        docstring=_get_docstring(node),
        decorators=decorators,
        is_async=isinstance(node, ast.AsyncFunctionDef),
        is_method=is_method,
        calls=_get_calls(node),
        has_return=has_return,
        has_yield=has_yield,
        has_raise=has_raise,
        has_recursion=_is_recursive(node),
    )


def _map_class(node: ast.ClassDef) -> ClassNode:
    """Map an AST ClassDef node to a ClassNode."""
    bases = [ast.unparse(b) for b in node.bases]
    decorators = [ast.unparse(d) for d in node.decorator_list]
    methods = [
        _map_function(child, is_method=True)
        for child in ast.walk(node)
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
        and child is not node
    ]
    class_vars = [
        target.id
        for stmt in node.body
        if isinstance(stmt, ast.Assign)
        for target in stmt.targets
        if isinstance(target, ast.Name)
    ]

    return ClassNode(
        name=node.name,
        lineno=node.lineno,
        end_lineno=getattr(node, "end_lineno", node.lineno),
        bases=bases,
        docstring=_get_docstring(node),
        decorators=decorators,
        methods=methods,
        class_variables=class_vars,
    )


def _map_import(node: ast.Import | ast.ImportFrom) -> list[ImportNode]:
    """Map import nodes to ImportNode objects."""
    result = []
    if isinstance(node, ast.Import):
        for alias in node.names:
            module = alias.name
            result.append(ImportNode(
                module=module,
                alias=alias.asname,
                lineno=node.lineno,
                is_from_import=False,
                is_stdlib=module.split(".")[0] in _STDLIB_MODULES,
            ))
    elif isinstance(node, ast.ImportFrom):
        module = node.module or ""
        names = [alias.name for alias in node.names]
        result.append(ImportNode(
            module=module,
            names=names,
            lineno=node.lineno,
            is_from_import=True,
            is_stdlib=module.split(".")[0] in _STDLIB_MODULES,
        ))
    return result


class NodeMapper:
    """
    Maps raw AST nodes to structured, typed CodeNode objects.

    Usage:
        mapper = NodeMapper()
        module = mapper.map(parse_result)
    """

    def map(self, parse_result) -> ModuleNode:
        """Convert a ParseResult into a fully-mapped ModuleNode."""
        from core.parser.ast_parser import ParseResult  # avoid circular at module level
        tree = parse_result.tree

        # Top-level functions (not inside classes)
        top_level_functions = [
            _map_function(node)
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        # Classes
        classes = [
            _map_class(node)
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
        ]

        # Imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.extend(_map_import(node))

        # Global variables (top-level assignments to simple names)
        global_vars = [
            target.id
            for stmt in tree.body
            if isinstance(stmt, ast.Assign)
            for target in stmt.targets
            if isinstance(target, ast.Name)
        ]

        return ModuleNode(
            filename=parse_result.filename,
            source=parse_result.source,
            docstring=_get_docstring(tree),
            functions=top_level_functions,
            classes=classes,
            imports=imports,
            global_variables=global_vars,
            line_count=parse_result.line_count,
        )
