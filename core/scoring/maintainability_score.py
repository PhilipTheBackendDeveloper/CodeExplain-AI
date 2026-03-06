"""
Maintainability Score — Computes a 0–100 maintainability index.

Based on the classic Maintainability Index formula, adapted for Python.
Higher = more maintainable code.
"""

import math
from dataclasses import dataclass
from utils.helpers import clamp
from core.analyzer.metrics import CodeMetrics
from core.analyzer.complexity_analyzer import ModuleComplexity


@dataclass
class MaintainabilityScore:
    """Maintainability analysis result."""
    score: float    # 0–100
    breakdown: dict[str, float]

    @property
    def label(self) -> str:
        s = self.score
        if s >= 85: return "Excellent"
        if s >= 65: return "Good"
        if s >= 40: return "Fair"
        return "Poor"

    @property
    def emoji(self) -> str:
        return {"Excellent": "🟢", "Good": "🟢", "Fair": "🟡", "Poor": "🔴"}.get(
            self.label, "⚪"
        )

    @property
    def rounded(self) -> int:
        return round(self.score)


class MaintainabilityScorer:
    """
    Computes a maintainability index from metrics and complexity.

    The classic MI formula:
      MI = 171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC) + 50 * sin(sqrt(2.4 * CM))

    Where:
      V  = Halstead volume
      G  = average cyclomatic complexity
      LOC = source lines of code
      CM = comment ratio

    Scaled to 0–100.

    Usage:
        scorer = MaintainabilityScorer()
        result = scorer.score(metrics, complexity)
    """

    def score(self, metrics: CodeMetrics, complexity: ModuleComplexity) -> MaintainabilityScore:
        V = max(metrics.halstead_volume, 1.0)
        G = max(complexity.average_complexity, 1.0)
        LOC = max(metrics.source_lines, 1)
        CM = metrics.comment_ratio

        # Classic MI formula
        try:
            mi_raw = (
                171.0
                - 5.2 * math.log(V)
                - 0.23 * G
                - 16.2 * math.log(LOC)
                + 50.0 * math.sin(math.sqrt(2.4 * CM))
            )
        except (ValueError, ZeroDivisionError):
            mi_raw = 100.0

        # Scale raw (0–171) to 0–100
        normalized = clamp((mi_raw / 171.0) * 100.0, 0.0, 100.0)

        breakdown = {
            "halstead_volume": round(V, 2),
            "avg_cyclomatic": round(G, 2),
            "source_lines": float(LOC),
            "comment_ratio_pct": round(CM * 100, 1),
            "raw_mi": round(mi_raw, 2),
        }

        return MaintainabilityScore(score=normalized, breakdown=breakdown)
