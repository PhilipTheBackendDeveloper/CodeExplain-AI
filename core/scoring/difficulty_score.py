"""
Difficulty Score — Computes a 0–10 difficulty score for a Python module.

Higher score = harder to read, understand, and modify.
"""

from dataclasses import dataclass
from utils.helpers import clamp
from core.analyzer.complexity_analyzer import ModuleComplexity


@dataclass
class DifficultyScore:
    """Difficulty analysis result."""
    score: float           # 0–10
    breakdown: dict[str, float]

    @property
    def label(self) -> str:
        s = self.score
        if s <= 2: return "Trivial"
        if s <= 4: return "Easy"
        if s <= 6: return "Moderate"
        if s <= 8: return "Hard"
        return "Expert"

    @property
    def emoji(self) -> str:
        return {"Trivial": "🟢", "Easy": "🟢", "Moderate": "🟡",
                "Hard": "🟠", "Expert": "🔴"}.get(self.label, "⚪")

    @property
    def rounded(self) -> float:
        return round(self.score, 1)

    def reason_lines(self) -> list[str]:
        lines = []
        for key, val in self.breakdown.items():
            display_key = key.replace("_", " ").title()
            lines.append(f"  • {display_key}: {val:.1f}/10")
        return lines


class DifficultyScorer:
    """
    Computes a difficulty score from complexity metrics.

    Usage:
        scorer = DifficultyScorer()
        score = scorer.score(complexity_result, smells_count=3)
    """

    def score(
        self,
        complexity: ModuleComplexity,
        smells_count: int = 0,
        recursion_count: int = 0,
    ) -> DifficultyScore:
        """Produce a 0–10 difficulty score."""

        # Cyclomatic complexity contribution (0–10)
        avg_cc = complexity.average_complexity
        cc_score = clamp(avg_cc / 2.0, 0, 10)

        # Nesting depth contribution
        max_depth = max((f.nesting_depth for f in complexity.functions), default=0)
        depth_score = clamp(max_depth / 0.8, 0, 10)  # depth of 8 = max

        # Recursion (boolean contribution +2 if present)
        recursion = any(f.has_recursion for f in complexity.functions)
        recursion_score = 4.0 if recursion else 0.0

        # Smells penalty (each smell adds 0.3)
        smells_score = clamp(smells_count * 0.3, 0, 4.0)

        # Function count penalty
        func_count = len(complexity.functions)
        func_score = clamp(func_count / 5.0, 0, 3.0)

        # Weighted average
        breakdown = {
            "cyclomatic_complexity": round(cc_score, 2),
            "nesting_depth": round(depth_score, 2),
            "recursion": recursion_score,
            "code_smells": round(smells_score, 2),
            "function_count": round(func_score, 2),
        }

        raw = (
            cc_score * 0.40 +
            depth_score * 0.25 +
            recursion_score * 0.20 +
            smells_score * 0.10 +
            func_score * 0.05
        )
        final = clamp(raw, 0, 10)
        return DifficultyScore(score=final, breakdown=breakdown)
