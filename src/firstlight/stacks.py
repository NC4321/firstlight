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
        Stack(
            id="node",
            display="Node/TypeScript",
            template_dir="node",
            next_steps=(
                "cd {name}",
                "npm install",
                "npm test",
            ),
        ),
        Stack(
            id="go",
            display="Go",
            template_dir="go",
            next_steps=(
                "cd {name}",
                "go mod tidy",
                "go test ./...",
            ),
        ),
    )
}
