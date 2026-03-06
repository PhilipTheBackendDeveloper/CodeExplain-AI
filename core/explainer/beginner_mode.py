"""
Beginner Mode — Narrative, story-like code explanations for absolute beginners.
"""

from core.parser.node_mapper import FunctionNode, ClassNode, ModuleNode
from utils.helpers import snake_to_words, pluralize


def _friendly_name(name: str) -> str:
    return snake_to_words(name).title()


def explain_function_beginner(func: FunctionNode) -> str:
    """Explain a function in friendly, story-like language."""
    name = _friendly_name(func.name)
    real_args = [a for a in func.args if a.name not in ("self", "cls")]
    lines = []

    lines.append(f"🔧 **Building a Mini-Command: {name}**")
    lines.append(
        f"Imagine you have a small, loyal helper named '{func.name}'. This helper has one specific job to do, "
        "almost like a secret recipe inside a cookbook."
    )

    if not real_args:
        lines.append(
            "This helper is very independent! It doesn't need you to give it anything to start. "
            "You just call its name, and it gets straight to work."
        )
    elif len(real_args) == 1:
        lines.append(
            f"To get this helper started, you need to hand them exactly one thing: **{real_args[0].name}**. "
            f"Think of it like giving a toy to a child or an ingredient to a chef — they can't start without it!"
        )
    else:
        ingredients = " and ".join([", ".join(f"**{a.name}**" for a in real_args[:-1]), f"**{real_args[-1].name}**"]) if len(real_args) > 1 else f"**{real_args[0].name}**"
        lines.append(
            f"This is a team effort! The helper needs {len(real_args)} different things to begin: {ingredients}. "
            "It's like assembling all the pieces of a puzzle before you can see the big picture."
        )

    if func.has_return:
        lines.append(
            "Once the helper finishes the task, they don't just stop — they actually **hand something back to you**. "
            "It's like a delivery person bringing a package to your door or a baker giving you a fresh loaf of bread."
        )
    elif func.has_yield:
        lines.append(
            "This helper works like a vending machine! Instead of giving you everything at once, it gives you items "
            "one-by-one, pausing between each one until you're ready for the next."
        )
    else:
        lines.append(
            "This helper is a silent worker. They do their job perfectly behind the scenes, but they don't bring anything back to you. "
            "Think of it like someone who comes in to water your plants while you're away — the job is done, but nothing is added to your hands."
        )

    if func.is_async:
        lines.append(
            "⚡ **Magic Multi-tasking**: This is a special 'async' helper! This means they can start a long task (like waiting for water to boil) "
            "and while they wait, they can do other small chores instead of just standing still. It makes the whole app feel much faster!"
        )

    if func.docstring:
        lines.append(
            f"📖 **A Note from the Creator**: The person who wrote this code left a message: \"{func.docstring.strip()[:200]}\""
        )

    return "\n".join(lines)


def explain_class_beginner(cls: ClassNode) -> str:
    """Explain a class in narrative terms."""
    name = _friendly_name(cls.name)
    lines = [f"📦 **The Blueprint: {name}**"]
    lines.append(
        f"In the world of code, we have 'Blueprints' called Classes. This blueprint is named '{cls.name}'. "
        "Just like a blueprint for a house tells you where the windows and doors go, this code tells the computer "
        "exactly how to build a new object."
    )
    
    if cls.bases:
        lines.append(
            f"This blueprint wasn't started from scratch! It's actually a specialized version of **{cls.bases[0]}**. "
            "It's like saying 'A Racecar is a type of Car' — it inherits all the basic car parts but adds its own fast engine!"
        )
    
    method_count = len(cls.methods)
    if method_count:
        lines.append(
            f"Objects built from this blueprint know how to do {method_count} different {pluralize(method_count, 'trick', 'tricks')}. "
            "These are like the 'skills' a character might have in a video game."
        )
    
    if cls.docstring:
        lines.append(f"📖 **The Designer's Vision**: \"{cls.docstring.strip()[:200]}\"")
        
    return "\n\n".join(lines)


def explain_module_beginner(module: ModuleNode) -> str:
    """Explain the overall module as a story."""
    lines = ["**The Big Picture: What's happening in this file?**"]
    
    if module.docstring:
        lines.append(
            f"This file is like a chapter in a book, and the author says it's about: \"{module.docstring.strip()[:250]}\""
        )
    else:
        lines.append(
            "Think of this file like a toolbox. Inside, someone has carefully organized tools and instructions "
            "to help the computer solve a specific problem."
        )

    if module.functions:
        lines.append(
            f"It contains **{len(module.functions)} specific instructions** (functions). Each one is a step-by-step guide "
            "on how to complete a small part of the big job."
        )
    
    if module.classes:
        lines.append(
            f"It also has **{len(module.classes)} master blueprints** (classes). These act like templates for creating "
            "complex things that can remember information and perform their own tasks."
        )
    
    if module.imports:
        lines.append(
            f"To get the job done, it borrows **{len(module.imports)} extra sets of tools** from other libraries. "
            "It's like a chef using a special imported spice or an artist using a rare paint that they didn't make themselves."
        )

    return "\n".join(lines)


class BeginnerExplainer:
    """Generates narrative, beginner-friendly explanations."""

    def explain(self, module: ModuleNode) -> str:
        sections = [explain_module_beginner(module)]
        
        if module.classes:
            sections.append("---")
            for cls in module.classes:
                sections.append(explain_class_beginner(cls))
        
        if module.functions:
            sections.append("---")
            for func in module.functions:
                sections.append(explain_function_beginner(func))
                
        return "\n\n".join(sections)
