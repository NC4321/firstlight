"""Interactive prompting — only for values the user didn't supply as flags."""

import typer

from firstlight.context import LICENSES
from firstlight.stacks import STACKS


def prompt_stack(default: str) -> str:
    choices = ", ".join(sorted(STACKS))
    while True:
        answer = typer.prompt(f"Stack ({choices})", default=default)
        if answer in STACKS:
            return answer
        typer.echo(f"  pick one of: {choices}")


def prompt_license(default: str) -> str:
    choices = ", ".join(LICENSES)
    while True:
        answer = typer.prompt(f"License ({choices})", default=default)
        if answer in LICENSES:
            return answer
        typer.echo(f"  pick one of: {choices}")


def prompt_description(project_name: str) -> str:
    return typer.prompt("Description", default=f"{project_name} — a new project.")


def prompt_pre_commit() -> bool:
    return typer.confirm("Include pre-commit config?", default=False)
