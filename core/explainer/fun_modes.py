"""
Fun Modes — Whimsical code explanations for entertainment and learning.

Modes: pirate | shakespeare | eli5 (explain like I'm 5)
"""

from core.parser.node_mapper import FunctionNode, ClassNode, ModuleNode
from core.explainer.narrative_generator import describe_function, describe_module


class PirateExplainer:
    """Arr matey! Code explained in pirate speak."""

    def explain(self, module: ModuleNode) -> str:
        lines = ["🏴‍☠️ **AHOY! Welcome to the code ship!**", ""]
        lines.append(
            f"Arr, this here treasure map ('{module.filename}') contains "
            f"{module.function_count} plunderin' functions and "
            f"{module.class_count} fearsome ship classes!"
        )
        if module.imports:
            lines.append(
                f"We've recruited {module.import_count} crew members (imports) from distant ports."
            )

        for func in module.functions:
            real_args = [a for a in func.args if a.name not in ("self", "cls")]
            arg_count = len(real_args)
            lines.append("")
            lines.append(f"⚓ **The {func.name} maneuver:**")
            if arg_count == 0:
                lines.append("This brave sailor needs no compass — it sails alone!")
            else:
                treasure = ", ".join(f"'{a.name}'" for a in real_args)
                lines.append(f"It plunders {arg_count} pieces of treasure: {treasure}.")
            if func.has_return:
                lines.append("And returns with loot from the voyage! Arrr!")
            if func.has_raise:
                lines.append("⚠️ Beware — it may fire the cannons (raise an exception)!")

        for cls in module.classes:
            lines.append("")
            lines.append(f"🚢 **The {cls.name} Galleon** has {len(cls.methods)} cannons (methods).")

        lines.append("")
        lines.append("🦜 *Yo ho ho and a bottle of clean code!*")
        return "\n".join(lines)


class ShakespeareExplainer:
    """Hark! Code explained in Shakespearean English."""

    def explain(self, module: ModuleNode) -> str:
        lines = ["🎭 **Hark! Attend thee to this code most wondrous!**", ""]
        lines.append(
            f"'Tis a file of great import, '{module.filename}', "
            f"wherein {module.function_count} noble functions dwell, "
            f"and {module.class_count} class{'es' if module.class_count != 1 else ''} "
            f"of most excellent design."
        )

        for func in module.functions:
            real_args = [a for a in func.args if a.name not in ("self", "cls")]
            lines.append("")
            lines.append(f"🌹 **Act I: The function '{func.name}'**")
            if not real_args:
                lines.append("This function, self-sufficient and proud, requireth no argument of others.")
            else:
                args_str = " and ".join(f"'{a.name}'" for a in real_args[:3])
                lines.append(f"It doth receive {args_str} — yea, passed from hand to awaiting hand.")
            if func.has_return:
                lines.append("Upon completion of its noble task, it returneth a result most prized.")
            if func.has_raise:
                lines.append("Yet beware — for it may cast forth an exception, like Hamlet's ghost!")

        for cls in module.classes:
            lines.append("")
            lines.append(
                f"🏰 **The noble class '{cls.name}'** — "
                f"a blueprint of great consequence with {len(cls.methods)} methods."
            )
            if cls.bases:
                lines.append(f"Born of '{cls.bases[0]}' — carrying forward noble lineage.")

        lines.append("")
        lines.append("*Thus ends our dramatic tour of this most scholarly code.*")
        return "\n".join(lines)


class ELI5Explainer:
    """Explain Like I'm 5 — maximum simplicity."""

    def explain(self, module: ModuleNode) -> str:
        lines = ["👶 **Let me explain this code like you're 5!**", ""]
        lines.append("Imagine a Lego set. This file is like one box of Lego pieces.")
        lines.append("")

        for func in module.functions:
            real_args = [a for a in func.args if a.name not in ("self", "cls")]
            lines.append(f"🧩 **'{func.name}'** is like a button on a toy.")
            if not real_args:
                lines.append("You press it and it just WORKS! No setup needed! 🎉")
            elif len(real_args) == 1:
                lines.append(
                    f"You give it one thing ({real_args[0].name}), like putting a battery in, "
                    "and then it works!"
                )
            else:
                lines.append(
                    f"You give it {len(real_args)} things and then it does its job. "
                    "Like a vending machine — put stuff in, get stuff out!"
                )
            if func.has_return:
                lines.append("It gives you something back when it's done — like a gift! 🎁")

        for cls in module.classes:
            lines.append("")
            lines.append(
                f"📱 **'{cls.name}'** is like a phone. "
                f"You can make MANY phones from the same design. "
                f"Each phone can do {len(cls.methods)} things."
            )

        lines.append("")
        lines.append("That's it! You're a programmer now! ⭐")
        return "\n".join(lines)


class FunModeExplainer:
    """Dispatcher for all fun explanation modes."""

    _MODES = {
        "pirate": PirateExplainer,
        "shakespeare": ShakespeareExplainer,
        "eli5": ELI5Explainer,
    }

    @classmethod
    def available_modes(cls) -> list[str]:
        return list(cls._MODES.keys())

    def explain(self, module: ModuleNode, mode: str = "pirate") -> str:
        explainer_cls = self._MODES.get(mode.lower())
        if not explainer_cls:
            raise ValueError(
                f"Unknown fun mode '{mode}'. Available: {', '.join(self.available_modes())}"
            )
        return explainer_cls().explain(module)
