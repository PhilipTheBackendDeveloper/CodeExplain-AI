"""
TypeScript Parser — Best-effort semantic mapping for TS/TSX files.
Uses regex/pattern matching to extract functions, classes, and imports.
"""

import re
from pathlib import Path
from typing import Optional
from core.parser.node_mapper import (
    ModuleNode, FunctionNode, ClassNode, ImportNode, ArgumentInfo
)


class TypeScriptParser:
    """
    Parses TypeScript/TSX/JSX files into the standard ModuleNode format.
    """

    def parse_to_module(self, file_path: Path) -> ModuleNode:
        source = file_path.read_text(encoding="utf-8")
        lines = source.splitlines()

        module = ModuleNode(
            filename=file_path.name,
            source=source,
            line_count=len(lines),
            docstring=self._extract_top_docstring(source)
        )

        # 1. Extract Imports
        module.imports = self._extract_imports(source)

        # 2. Extract Classes
        module.classes = self._extract_classes(source)

        # 3. Extract Functions (Top-level)
        module.functions = self._extract_functions(source)

        return module

    def _extract_top_docstring(self, source: str) -> Optional[str]:
        match = re.match(r'^\s*/\*\*(.*?)\*/', source, re.DOTALL)
        if match:
            return match.group(1).strip("* \n")
        return None

    def _extract_imports(self, source: str) -> list[ImportNode]:
        imports = []
        # Pattern for: import { a, b } from 'module'
        pattern = re.compile(r'import\s+(?:([\w*,\s{}]+)\s+from\s+)?[\'"](.+?)[\'"]', re.MULTILINE)
        for match in pattern.finditer(source):
            bound_names, module_path = match.groups()
            names = []
            if bound_names:
                # Clean up { a, b } -> [a, b]
                clean_names = re.sub(r'[\s{}]', '', bound_names).split(',')
                names = [n for n in clean_names if n]
            
            imports.append(ImportNode(
                module=module_path,
                names=names,
                is_stdlib=module_path in ("react", "react-native", "path", "fs"), # Common pseudo-stdlib
                is_from_import=True if names else False
            ))
        return imports

    def _extract_functions(self, source: str) -> list[FunctionNode]:
        functions = []
        # Basic pattern for: function name(args) { ... } or const name = (args) => { ... }
        # This is simplified and avoids nested regex pitfalls by just looking for declarations
        
        # 1. Standard functions
        fn_pattern = re.compile(r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\((.*?)\)', re.MULTILINE)
        for match in fn_pattern.finditer(source):
            name, args_str = match.groups()
            functions.append(FunctionNode(
                name=name,
                lineno=source[:match.start()].count('\n') + 1,
                end_lineno=source[:match.end()].count('\n') + 1, # Placeholder
                args=self._parse_args(args_str),
                is_async="async" in match.group(0)
            ))

        # 2. Arrow functions assigned to const/let
        arrow_pattern = re.compile(r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\((.*?)\)\s*=>', re.MULTILINE)
        for match in arrow_pattern.finditer(source):
            name, args_str = match.groups()
            functions.append(FunctionNode(
                name=name,
                lineno=source[:match.start()].count('\n') + 1,
                end_lineno=source[:match.end()].count('\n') + 1,
                args=self._parse_args(args_str),
                is_async="async" in match.group(0)
            ))

        return functions

    def _extract_classes(self, source: str) -> list[ClassNode]:
        classes = []
        pattern = re.compile(r'(?:export\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?\s*{', re.MULTILINE)
        for match in pattern.finditer(source):
            name, base = match.groups()
            classes.append(ClassNode(
                name=name,
                lineno=source[:match.start()].count('\n') + 1,
                end_lineno=source[:match.end()].count('\n') + 1,
                bases=[base] if base else []
            ))
        return classes

    def _parse_args(self, args_str: str) -> list[ArgumentInfo]:
        args = []
        if not args_str.strip():
            return args
        for part in args_str.split(','):
            clean = part.strip()
            if not clean: continue
            # Handle name: type = default
            name_part = clean.split(':')[0].strip()
            name = name_part.split('=')[0].strip()
            args.append(ArgumentInfo(name=name))
        return args
