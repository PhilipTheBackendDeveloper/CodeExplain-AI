"""
Explanation Engine — Master orchestrator for all explanation modes.

Routes explanation requests to the appropriate mode engine (beginner, developer, fun).
"""

from core.parser.node_mapper import ModuleNode
from core.explainer.beginner_mode import BeginnerExplainer
from core.explainer.developer_mode import DeveloperExplainer
from core.explainer.fun_modes import FunModeExplainer

VALID_MODES = ["developer", "beginner", "fun:pirate", "fun:shakespeare", "fun:eli5"]


class ExplanationEngine:
    """
    Master explanation dispatcher. Routes to the correct mode.

    Usage:
        engine = ExplanationEngine()
        text = engine.explain(module_node, mode="developer")
    """

    def __init__(self):
        self._beginner = BeginnerExplainer()
        self._developer = DeveloperExplainer()
        self._fun = FunModeExplainer()

    def explain(self, module: ModuleNode, mode: str = "developer") -> str:
        """Generate an explanation for a module in the given mode."""
        mode = mode.lower().strip()

        if mode == "beginner":
            return self._beginner.explain(module)
        elif mode == "developer":
            return self._developer.explain(module)
        elif mode.startswith("fun:"):
            fun_submode = mode.split(":", 1)[1]
            return self._fun.explain(module, mode=fun_submode)
        else:
            raise ValueError(
                f"Unknown mode '{mode}'. Valid modes: {', '.join(VALID_MODES)}"
            )

    @staticmethod
    def list_modes() -> list[str]:
        return VALID_MODES.copy()
