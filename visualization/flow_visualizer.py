"""
Flow Visualizer — Renders control flow graphs as ASCII flowcharts.
"""

from core.graph.control_flow import CFGResult, ControlFlowBuilder


def render_all_cfgs(parse_result) -> str:
    """Build and render CFGs for all functions as ASCII flowcharts."""
    builder = ControlFlowBuilder()
    cfgs = builder.build(parse_result)

    if not cfgs:
        return "(no functions found for control flow analysis)"

    sections = []
    for cfg in cfgs:
        sections.append(f"\n╔══ Control Flow: {cfg.function_name}() ══╗")
        sections.append(cfg.ascii_flow())
        sections.append("╚" + "═" * (len(f"═ Control Flow: {cfg.function_name}() ══╗") + 1) + "╝")

    return "\n".join(sections)


def render_single_cfg(cfg: CFGResult) -> str:
    """Render a single CFG as ASCII."""
    lines = [f"\n╔══ Control Flow: {cfg.function_name}() ══╗"]
    lines.append(cfg.ascii_flow())
    lines.append("╚" + "═" * 40 + "╝")
    return "\n".join(lines)
