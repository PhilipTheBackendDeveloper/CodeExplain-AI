"""
Control Flow Graph — Simplified per-function control flow visualization.

Represents control flow as a sequence of labeled blocks with edges showing
branches (if/else/loop) and exception handling paths.
"""

import ast
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CFGBlock:
    """A single basic block in a control flow graph."""
    id: int
    label: str
    kind: str     # entry | exit | if | else | loop | try | except | return
    lineno: int = 0
    successors: list[int] = field(default_factory=list)


@dataclass
class CFGResult:
    """Control flow graph for a single function."""
    function_name: str
    blocks: list[CFGBlock] = field(default_factory=list)

    def ascii_flow(self) -> str:
        """Render a linear ASCII flowchart of the control flow."""
        lines = [f"  ┌─ {self.function_name}() ─┐"]
        block_map = {b.id: b for b in self.blocks}

        for block in self.blocks:
            kind_symbols = {
                "entry": "●  START",
                "exit":  "■  END",
                "if":    "◆  IF",
                "else":  "◇  ELSE",
                "loop":  "↻  LOOP",
                "try":   "⊞  TRY",
                "except":"⊟  EXCEPT",
                "return":"→  RETURN",
                "call":  "⊙  CALL",
            }
            symbol = kind_symbols.get(block.kind, f"□  {block.kind.upper()}")
            lines.append(f"  │  [{block.id}] {symbol}: {block.label}")
            if block.successors:
                for succ_id in block.successors:
                    succ = block_map.get(succ_id)
                    if succ:
                        lines.append(f"  │      └─▶ [{succ_id}] {succ.label}")

        lines.append("  └──────────────────┘")
        return "\n".join(lines)


class ControlFlowBuilder:
    """
    Builds simplified control flow graphs for each function in a module.

    Usage:
        builder = ControlFlowBuilder()
        cfgs = builder.build(parse_result)
    """

    def __init__(self):
        self._counter = 0

    def _new_id(self) -> int:
        self._counter += 1
        return self._counter

    def build(self, parse_result) -> list[CFGResult]:
        """Build CFGs for all functions in the module."""
        results = []
        for node in ast.walk(parse_result.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._counter = 0
                cfg = self._build_function_cfg(node)
                results.append(cfg)
        return results

    def _build_function_cfg(self, func: ast.FunctionDef) -> CFGResult:
        blocks: list[CFGBlock] = []

        # Entry block
        entry = CFGBlock(id=self._new_id(), label=f"enter {func.name}", kind="entry", lineno=func.lineno)
        blocks.append(entry)

        prev_id = entry.id

        for stmt in func.body:
            block, prev_id = self._process_stmt(stmt, blocks, prev_id)

        # Exit block
        exit_block = CFGBlock(id=self._new_id(), label=f"exit {func.name}", kind="exit")
        if prev_id is not None:
            prev_block = next((b for b in blocks if b.id == prev_id), None)
            if prev_block:
                prev_block.successors.append(exit_block.id)
        blocks.append(exit_block)

        return CFGResult(function_name=func.name, blocks=blocks)

    def _process_stmt(
        self, stmt: ast.stmt, blocks: list[CFGBlock], prev_id: Optional[int]
    ) -> tuple[Optional[CFGBlock], Optional[int]]:
        """Process a single statement and return its block + new prev_id."""

        if isinstance(stmt, ast.Return):
            b = CFGBlock(id=self._new_id(), label="return", kind="return", lineno=stmt.lineno)
            self._link(blocks, prev_id, b.id)
            blocks.append(b)
            return b, b.id

        elif isinstance(stmt, (ast.If,)):
            label = f"if ({ast.unparse(stmt.test)[:40]})"
            b = CFGBlock(id=self._new_id(), label=label, kind="if", lineno=stmt.lineno)
            self._link(blocks, prev_id, b.id)
            blocks.append(b)
            then_prev = b.id
            for s in stmt.body:
                _, then_prev = self._process_stmt(s, blocks, then_prev)
            if stmt.orelse:
                else_b = CFGBlock(id=self._new_id(), label="else", kind="else", lineno=stmt.lineno)
                b.successors.append(else_b.id)
                blocks.append(else_b)
                else_prev = else_b.id
                for s in stmt.orelse:
                    _, else_prev = self._process_stmt(s, blocks, else_prev)
            return b, then_prev

        elif isinstance(stmt, (ast.For, ast.While, ast.AsyncFor)):
            label = f"loop (L{stmt.lineno})"
            b = CFGBlock(id=self._new_id(), label=label, kind="loop", lineno=stmt.lineno)
            b.successors.append(b.id)  # back edge
            self._link(blocks, prev_id, b.id)
            blocks.append(b)
            loop_prev = b.id
            for s in stmt.body:
                _, loop_prev = self._process_stmt(s, blocks, loop_prev)
            return b, b.id

        elif isinstance(stmt, ast.Try):
            b = CFGBlock(id=self._new_id(), label="try", kind="try", lineno=stmt.lineno)
            self._link(blocks, prev_id, b.id)
            blocks.append(b)
            try_prev = b.id
            for s in stmt.body:
                _, try_prev = self._process_stmt(s, blocks, try_prev)
            for handler in stmt.handlers:
                exc_label = f"except {handler.type and ast.unparse(handler.type) or 'Exception'}"
                exc_b = CFGBlock(id=self._new_id(), label=exc_label, kind="except", lineno=handler.lineno)
                b.successors.append(exc_b.id)
                blocks.append(exc_b)
            return b, try_prev

        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            label = ast.unparse(stmt.value)[:50]
            b = CFGBlock(id=self._new_id(), label=label, kind="call", lineno=stmt.lineno)
            self._link(blocks, prev_id, b.id)
            blocks.append(b)
            return b, b.id

        else:
            return None, prev_id

    def _link(self, blocks: list[CFGBlock], from_id: Optional[int], to_id: int) -> None:
        if from_id is not None:
            block = next((b for b in blocks if b.id == from_id), None)
            if block and to_id not in block.successors:
                block.successors.append(to_id)
