"""
Tests for core/parser/ — ASTParser, NodeMapper, SymbolTable
"""

import ast
import pytest
from pathlib import Path

from core.parser.ast_parser import ASTParser, ParseResult
from core.parser.node_mapper import NodeMapper, ModuleNode, FunctionNode, ClassNode
from core.parser.symbol_table import SymbolTable, SymbolKind


# ── Fixtures ──────────────────────────────────────────────────────────────────

SIMPLE_CODE = """
\"\"\"A simple test module.\"\"\"

import os
from pathlib import Path

CONSTANT = 42

class MyClass:
    \"\"\"A test class.\"\"\"
    class_var = "hello"

    def __init__(self, value: int):
        self.value = value

    def compute(self, x: int, y: int = 0) -> int:
        \"\"\"Compute something.\"\"\"
        if x > 0:
            return x + y
        return 0


def standalone(a, b):
    result = a + b
    return result


async def async_func(data: list) -> None:
    for item in data:
        pass
"""

RECURSIVE_CODE = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""

INVALID_CODE = "def broken(:"


# ── ASTParser Tests ───────────────────────────────────────────────────────────

class TestASTParser:
    def test_parse_valid_source(self):
        parser = ASTParser()
        result = parser.parse_source(SIMPLE_CODE)
        assert result.success
        assert isinstance(result.tree, ast.Module)
        assert result.line_count > 0

    def test_parse_invalid_source(self):
        parser = ASTParser()
        result = parser.parse_source(INVALID_CODE)
        assert not result.success
        assert len(result.errors) > 0
        assert "SyntaxError" in result.errors[0]

    def test_parse_file_not_found(self):
        parser = ASTParser()
        result = parser.parse_file("/nonexistent/file.py")
        assert not result.success
        assert "not found" in result.errors[0].lower()

    def test_iter_functions(self):
        parser = ASTParser()
        result = parser.parse_source(SIMPLE_CODE)
        funcs = list(parser.iter_functions(result))
        func_names = [f.name for f in funcs]
        assert "standalone" in func_names
        assert "async_func" in func_names
        assert "__init__" in func_names
        assert "compute" in func_names

    def test_iter_classes(self):
        parser = ASTParser()
        result = parser.parse_source(SIMPLE_CODE)
        classes = list(parser.iter_classes(result))
        assert len(classes) == 1
        assert classes[0].name == "MyClass"

    def test_iter_imports(self):
        parser = ASTParser()
        result = parser.parse_source(SIMPLE_CODE)
        imports = list(parser.iter_imports(result))
        assert len(imports) == 2

    def test_dump(self):
        parser = ASTParser()
        result = parser.parse_source("x = 1")
        dump = parser.dump(result)
        assert "Module" in dump


# ── NodeMapper Tests ──────────────────────────────────────────────────────────

class TestNodeMapper:
    def setup_method(self):
        parser = ASTParser()
        self.parse_result = parser.parse_source(SIMPLE_CODE)
        self.mapper = NodeMapper()
        self.module = self.mapper.map(self.parse_result)

    def test_maps_module(self):
        assert isinstance(self.module, ModuleNode)
        assert self.module.docstring == "A simple test module."

    def test_maps_functions(self):
        func_names = [f.name for f in self.module.functions]
        assert "standalone" in func_names
        assert "async_func" in func_names

    def test_maps_classes(self):
        assert len(self.module.classes) == 1
        cls = self.module.classes[0]
        assert cls.name == "MyClass"
        assert cls.docstring == "A test class."

    def test_maps_class_methods(self):
        cls = self.module.classes[0]
        method_names = [m.name for m in cls.methods]
        assert "__init__" in method_names
        assert "compute" in method_names

    def test_maps_function_args(self):
        standalone = next(f for f in self.module.functions if f.name == "standalone")
        assert standalone.arg_count == 2
        arg_names = [a.name for a in standalone.args]
        assert "a" in arg_names
        assert "b" in arg_names

    def test_maps_return_annotation(self):
        cls = self.module.classes[0]
        compute = next(m for m in cls.methods if m.name == "compute")
        assert compute.return_annotation == "int"

    def test_maps_async(self):
        async_f = next(f for f in self.module.functions if f.name == "async_func")
        assert async_f.is_async

    def test_maps_has_return(self):
        standalone = next(f for f in self.module.functions if f.name == "standalone")
        assert standalone.has_return

    def test_maps_imports(self):
        import_modules = [i.module for i in self.module.imports]
        assert "os" in import_modules
        assert "pathlib" in import_modules

    def test_maps_global_variables(self):
        assert "CONSTANT" in self.module.global_variables

    def test_all_functions_includes_methods(self):
        all_funcs = self.module.all_functions
        all_names = [f.name for f in all_funcs]
        assert "standalone" in all_names
        assert "__init__" in all_names

    def test_recursive_detection(self):
        parser = ASTParser()
        result = parser.parse_source(RECURSIVE_CODE)
        module = NodeMapper().map(result)
        factorial = next(f for f in module.functions if f.name == "factorial")
        # calls should include factorial (self-reference)
        assert "factorial" in factorial.calls


# ── SymbolTable Tests ─────────────────────────────────────────────────────────

class TestSymbolTable:
    def setup_method(self):
        parser = ASTParser()
        self.parse_result = parser.parse_source(SIMPLE_CODE)
        self.table = SymbolTable()
        self.table.build(self.parse_result.tree)

    def test_finds_function_symbols(self):
        sym = self.table.lookup("standalone")
        assert sym is not None
        assert sym.kind == SymbolKind.FUNCTION

    def test_finds_class_symbols(self):
        sym = self.table.lookup("MyClass")
        assert sym is not None
        assert sym.kind == SymbolKind.CLASS

    def test_finds_import_symbols(self):
        sym = self.table.lookup("os")
        assert sym is not None
        assert sym.kind == SymbolKind.IMPORT

    def test_finds_variable_symbols(self):
        sym = self.table.lookup("CONSTANT")
        assert sym is not None
        assert sym.kind == SymbolKind.VARIABLE

    def test_get_all_symbols_excludes_builtins(self):
        symbols = self.table.get_all_symbols()
        kinds = [s.kind for s in symbols]
        assert SymbolKind.BUILTIN not in kinds

    def test_unused_imports_detection(self):
        code = "import os\nimport sys\nprint(sys.version)"
        parser = ASTParser()
        result = parser.parse_source(code)
        table = SymbolTable()
        table.build(result.tree)
        unused = table.get_unused_imports()
        unused_names = [s.name for s in unused]
        # 'os' is not used, 'sys' is used
        assert "os" in unused_names
