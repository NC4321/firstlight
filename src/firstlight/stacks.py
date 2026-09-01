"""Stack registry: each supported stack is pure data, no code paths branch on stack id."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Stack:
    id: str
    display: str
    template_dir: str
    next_steps: tuple[str, ...] = field(default=())


STACKS: dict[str, Stack] = {
    stack.id: stack
    for stack in (
        Stack(
            id="python",
            display="Python",
            template_dir="python",
            next_steps=(
                "cd {name}",
                "python -m venv .venv && source .venv/bin/activate",
                "pip install -e .[dev]",
                "pytest",
            ),
        ),
    )
}
