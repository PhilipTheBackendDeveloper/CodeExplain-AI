"""
Symbol Table Builder — Tracks name definitions and references across scopes.

The symbol table provides name resolution and scope-aware lookups that
analyzers use for detecting undefined references and unused variables.
"""

import ast
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class SymbolKind(Enum):
    FUNCTION = auto()
    CLASS = auto()
    VARIABLE = auto()
    IMPORT = auto()
    PARAMETER = auto()
    BUILTIN = auto()


@dataclass
class Symbol:
    """Represents a single named symbol in the program."""
    name: str
    kind: SymbolKind
    lineno: int
    scope: str = "module"
    is_used: bool = False
    is_defined: bool = True
    annotation: Optional[str] = None


@dataclass
class Scope:
    """Represents a single lexical scope (module, function, class)."""
    name: str
    kind: str  # "module" | "function" | "class"
    symbols: dict[str, Symbol] = field(default_factory=dict)
    parent: Optional["Scope"] = None
    children: list["Scope"] = field(default_factory=list)

    def define(self, symbol: Symbol) -> None:
        self.symbols[symbol.name] = symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        """Resolve a name in this scope or any parent scope."""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def mark_used(self, name: str) -> bool:
        """Mark a symbol as used. Returns True if found."""
        sym = self.lookup(name)
        if sym:
            sym.is_used = True
            return True
        return False


_PYTHON_BUILTINS = {
    "print", "len", "range", "enumerate", "zip", "map", "filter", "sorted",
    "reversed", "list", "tuple", "dict", "set", "frozenset", "type", "isinstance",
    "issubclass", "hasattr", "getattr", "setattr", "delattr", "vars", "dir",
    "callable", "repr", "str", "int", "float", "bool", "bytes", "bytearray",
    "memoryview", "complex", "abs", "round", "min", "max", "sum", "pow", "divmod",
    "hash", "id", "hex", "oct", "bin", "chr", "ord", "format", "open",
    "input", "exec", "eval", "compile", "globals", "locals", "super", "object",
    "property", "staticmethod", "classmethod", "next", "iter", "any", "all",
    "help", "exit", "quit", "breakpoint", "NotImplemented", "Ellipsis",
    "True", "False", "None", "__name__", "__file__", "__doc__",
    "Exception", "ValueError", "TypeError", "KeyError", "IndexError",
    "AttributeError", "RuntimeError", "StopIteration", "GeneratorExit",
    "ImportError", "OSError", "IOError", "NotImplementedError",
}


class SymbolTableBuilder(ast.NodeVisitor):
    """Builds a hierarchical symbol table by walking an AST."""

    def __init__(self):
        self._module_scope = Scope(name="<module>", kind="module")
        self._current_scope = self._module_scope
        self._scope_stack: list[Scope] = [self._module_scope]

        # Seed builtins into module scope
        for name in _PYTHON_BUILTINS:
            self._module_scope.define(Symbol(
                name=name, kind=SymbolKind.BUILTIN, lineno=0, scope="<builtins>"
            ))

    @property
    def root_scope(self) -> Scope:
        return self._module_scope

    def _enter_scope(self, name: str, kind: str) -> Scope:
        new_scope = Scope(name=name, kind=kind, parent=self._current_scope)
        self._current_scope.children.append(new_scope)
        self._scope_stack.append(new_scope)
        self._current_scope = new_scope
        return new_scope

    def _exit_scope(self) -> None:
        self._scope_stack.pop()
        self._current_scope = self._scope_stack[-1]

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._current_scope.define(Symbol(
            name=node.name, kind=SymbolKind.FUNCTION,
            lineno=node.lineno, scope=self._current_scope.name
        ))
        self._enter_scope(node.name, "function")
        for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
            self._current_scope.define(Symbol(
                name=arg.arg, kind=SymbolKind.PARAMETER,
                lineno=arg.col_offset, scope=self._current_scope.name
            ))
        self.generic_visit(node)
        self._exit_scope()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._current_scope.define(Symbol(
            name=node.name, kind=SymbolKind.CLASS,
            lineno=node.lineno, scope=self._current_scope.name
        ))
        self._enter_scope(node.name, "class")
        self.generic_visit(node)
        self._exit_scope()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            bound_name = alias.asname or alias.name.split(".")[0]
            self._current_scope.define(Symbol(
                name=bound_name, kind=SymbolKind.IMPORT,
                lineno=node.lineno, scope=self._current_scope.name
            ))

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            bound_name = alias.asname or alias.name
            self._current_scope.define(Symbol(
                name=bound_name, kind=SymbolKind.IMPORT,
                lineno=node.lineno, scope=self._current_scope.name
            ))

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name):
                self._current_scope.define(Symbol(
                    name=target.id, kind=SymbolKind.VARIABLE,
                    lineno=node.lineno, scope=self._current_scope.name
                ))
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if isinstance(node.target, ast.Name):
            annotation = None
            try:
                annotation = ast.unparse(node.annotation)
            except Exception:
                pass
            self._current_scope.define(Symbol(
                name=node.target.id, kind=SymbolKind.VARIABLE,
                lineno=node.lineno, scope=self._current_scope.name,
                annotation=annotation,
            ))
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            self._current_scope.mark_used(node.id)


class SymbolTable:
    """
    High-level interface for building and querying a program symbol table.

    Usage:
        table = SymbolTable()
        table.build(parse_result.tree)
        unused = table.get_unused_imports()
    """

    def __init__(self):
        self._builder: Optional[SymbolTableBuilder] = None

    def build(self, tree: ast.Module) -> "SymbolTable":
        """Build the symbol table from an AST module."""
        self._builder = SymbolTableBuilder()
        self._builder.visit(tree)
        return self

    @property
    def root(self) -> Scope:
        if not self._builder:
            raise RuntimeError("SymbolTable.build() must be called first.")
        return self._builder.root_scope

    def get_all_symbols(self) -> list[Symbol]:
        """Return all symbols across all scopes (excluding builtins)."""
        results = []
        def _collect(scope: Scope):
            for sym in scope.symbols.values():
                if sym.kind != SymbolKind.BUILTIN:
                    results.append(sym)
            for child in scope.children:
                _collect(child)
        _collect(self.root)
        return results

    def get_unused_imports(self) -> list[Symbol]:
        """Return import symbols that were never referenced."""
        return [
            sym for sym in self.get_all_symbols()
            if sym.kind == SymbolKind.IMPORT and not sym.is_used
        ]

    def get_undefined_names(self) -> list[str]:
        """Return names that are used but never defined (best-effort)."""
        defined = {sym.name for sym in self.get_all_symbols()}
        defined |= _PYTHON_BUILTINS
        used_but_undefined = []
        def _check(scope: Scope):
            for name, sym in scope.symbols.items():
                if sym.is_used and name not in defined:
                    used_but_undefined.append(name)
            for child in scope.children:
                _check(child)
        _check(self.root)
        return used_but_undefined

    def lookup(self, name: str) -> Optional[Symbol]:
        """Lookup a symbol by name in the root scope."""
        return self.root.lookup(name)
