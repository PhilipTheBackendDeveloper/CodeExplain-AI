"""
Beginner Mode — Narrative, story-like code explanations for absolute beginners.
"""

from core.parser.node_mapper import FunctionNode, ClassNode, ModuleNode
from utils.helpers import snake_to_words, pluralize


def _friendly_name(name: str) -> str:
    return snake_to_words(name).title()


def explain_function_beginner(func: FunctionNode) -> str:
    """Explain a function in a highly detailed story-like way."""
    name = _friendly_name(func.name)
    real_args = [a for a in func.args if a.name not in ("self", "cls")]
    lines = []

    lines.append(f"🔧 **Building a Mini-Command: {name}**")
    lines.append(
        f"Imagine you have a small, loyal helper named **'{func.name}'**. This helper has one specific job to do, "
        "almost like a secret recipe tucked away inside a grand cookbook. Whenever the computer needs this job done, "
        f"it calls out for '{func.name}' to step forward!"
    )

    if not real_args:
        lines.append(
            "This helper is very independent! It doesn't need you to give it anything to start its work. "
            "As soon as you call its name, it jumps right into action, knowing exactly what to do without any extra instructions."
        )
    elif len(real_args) == 1:
        lines.append(
            f"To get this helper started, you need to hand them exactly one piece of equipment: **{real_args[0].name}**. "
            f"Think of it like giving a specific toy to a child or a required ingredient to a chef. They are ready and willing, "
            f"but they simply cannot begin their magic until you provide that one important item: '{real_args[0].name}'."
        )
    else:
        ingredients = " and ".join([", ".join(f"**{a.name}**" for a in real_args[:-1]), f"**{real_args[-1].name}**"]) if len(real_args) > 1 else f"**{real_args[0].name}**"
        lines.append(
            f"This helper likes to be well-prepared! Before they start, you need to give them a few different things: {ingredients}. "
            f"It's like a builder needing a hammer, some nails, and a piece of wood. Once they have all {len(real_args)} items in their hands, "
            "they can begin building something wonderful."
        )

    if func.has_return:
        lines.append(
            "Once the helper finishes their hard work, they don't just walk away. Instead, they **bring a gift back to you**! "
            "Imagine a delivery person bringing a special package to your front door, or a baker handing you a warm, fresh loaf of bread. "
            "The helper does the work and then gives you the result to use however you like."
        )
    elif func.has_yield:
        lines.append(
            "This helper works like a friendly vending machine or a candy dispenser! Instead of giving you everything at once, "
            "it produces its results one by one. It gives you one item, waits for you to take it, and then prepares the next one. "
            "It's great for when you only need one thing at a time!"
        )
    else:
        lines.append(
            "This helper is a quiet, behind-the-scenes worker. They do their job perfectly (like tidying up a messy room), "
            "but they don't bring anything back to your hands when they're finished. You'll see that the work is done, but your hands stay empty."
        )

    if func.is_async:
        lines.append(
            "⚡ **The Magic of Patience**: This is a special 'async' helper! This means they are incredibly smart at multi-tasking. "
            "If they are doing a task that takes a while (like waiting for a letter to arrive in the mail), they don't just stand there staring! "
            "Instead, they set a timer and go do other helpful chores while they wait. It makes everything in the app feel smooth and fast."
        )

    if func.docstring:
        lines.append(
            f"📖 **A Secret Message**: The person who created this helper left a little note to explain their vision: \"{func.docstring.strip()[:300]}\""
        )

    return "\n".join(lines)


def explain_class_beginner(cls: ClassNode) -> str:
    """Explain a class in narrative terms for kids/beginners."""
    name = _friendly_name(cls.name)
    lines = [f"📦 **The Master Template: {name}**"]
    lines.append(
        f"In the magical world of code, we use 'Templates' called Classes. This specific template is named **'{cls.name}'**. "
        "Think of it like a master blueprint for a toy robot. The blueprint itself isn't a robot, but it contains all the "
        "secrets on how to build as many robots as you want!"
    )
    
    if cls.bases:
        lines.append(
            f"This blueprint wasn't just pulled out of thin air! It's actually a specialized version of a more general plan called **{cls.bases[0]}**. "
            "It's like having a basic blueprint for a 'Vehicle' and then adding special instructions to turn it into a 'Supersonic Jet'. "
            "It knows everything the original plan knew, but adds its own special flair!"
        )
    
    method_count = len(cls.methods)
    if method_count:
        lines.append(
            f"Any object built from this template will automatically know how to do **{method_count} different tricks**. "
            f"Whether it's {pluralize(method_count, 'dancing', 'performing various actions')}, these 'methods' are the skills "
            "that make the objects come to life."
        )
    
    if cls.docstring:
        lines.append(f"📖 **The Template's Purpose**: \"{cls.docstring.strip()[:300]}\"")
        
    return "\n\n".join(lines)


def explain_module_beginner(module: ModuleNode) -> str:
    """Explain the overall module as a grand story."""
    lines = ["**🌟 The Chapter Overview: What's inside this file?**"]
    
    if module.docstring:
        lines.append(
            f"This file is like a detailed chapter in a big adventure book. The author says this chapter is all about: \"{module.docstring.strip()[:400]}\""
        )
    else:
        lines.append(
            "Imagine this file is a specialized Toolbox. Instead of hammers and screwdrivers, it's filled with digital tools "
            "and careful instructions that work together to help the computer solve one big, important puzzle."
        )

    if module.functions:
        lines.append(
            f"Inside, you'll find **{len(module.functions)} specific sets of instructions** (called functions). Each one is a "
            "mini-story that teaches the computer exactly how to perform one individual task perfectly."
        )
    
    if module.classes:
        lines.append(
            f"It also contains **{len(module.classes)} master blueprints** (called classes). These are like creative templates "
            "that allow the computer to 'remember' things and act like independent characters in a game."
        )
    
    if module.imports:
        lines.append(
            f"To get the job done, this file 'borrows' **{len(module.imports)} extra boxes of tools** from other expert workshops. "
            "It's like a chef using a rare spice from across the ocean or a knight borrowing a legendary sword to win a battle."
        )

    return "\n".join(lines)


class BeginnerExplainer:
    """Generates narrative, story-book style explanations for absolute beginners."""

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
