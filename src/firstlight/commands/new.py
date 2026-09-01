"""The `firstlight new` command: resolve inputs → validate → render → preview or write.

Input precedence, highest first: explicit flag → interactive prompt (default seeded
from the config file) → config file value → built-in default.
"""

import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.markup import escape
from rich.panel import Panel

from firstlight import prompts
from firstlight.config import load_config
from firstlight.console import console, err_console
from firstlight.context import LICENSES, ProjectContext, derive_package_name
from firstlight.gitops import get_git_identity
from firstlight.render import render_project
from firstlight.stacks import STACKS
from firstlight.validation import ValidationError, validate_project_name, validate_target_dir

DEFAULT_STACK = "python"
DEFAULT_LICENSE = "mit"


def _fail(message: str) -> typer.Exit:
    err_console.print(Panel(message, title="error", border_style="red", title_align="left"))
    return typer.Exit(code=1)


def new(
    name: Annotated[str, typer.Argument(help="Project name (lowercase-kebab-case).")],
    stack: Annotated[str | None, typer.Option("--stack", "-s", help="Target stack.")] = None,
    license_id: Annotated[
        str | None, typer.Option("--license", "-l", help="License: mit, apache-2.0, or none.")
    ] = None,
    description: Annotated[
        str | None, typer.Option("--description", "-d", help="One-line project description.")
    ] = None,
    pre_commit: Annotated[
        bool | None,
        typer.Option("--pre-commit/--no-pre-commit", help="Include a pre-commit config."),
    ] = None,
    no_input: Annotated[
        bool, typer.Option("--no-input", help="Never prompt; use flags, config, and defaults.")
    ] = False,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Preview the files without writing anything.")
    ] = False,
    target_dir: Annotated[
        Path, typer.Option("--dir", help="Parent directory to create the project in.")
    ] = Path("."),
) -> None:
    """Scaffold a new project."""
    try:
        validate_project_name(name)
        if not dry_run:
            validate_target_dir(target_dir / name)
    except ValidationError as exc:
        raise _fail(str(exc)) from exc

    config = load_config()
    interactive = not no_input

    if stack is None:
        seeded = config.default_stack or DEFAULT_STACK
        stack = prompts.prompt_stack(seeded) if interactive else seeded
    if stack not in STACKS:
        raise _fail(f"Unknown stack {stack!r}. Available: {', '.join(sorted(STACKS))}.")

    if license_id is None:
        seeded = config.default_license or DEFAULT_LICENSE
        license_id = prompts.prompt_license(seeded) if interactive else seeded
    if license_id not in LICENSES:
        raise _fail(f"Unknown license {license_id!r}. Available: {', '.join(LICENSES)}.")

    if description is None:
        if interactive:
            description = prompts.prompt_description(name)
        else:
            description = f"{name} — a new {STACKS[stack].display} project."

    if pre_commit is None:
        pre_commit = prompts.prompt_pre_commit() if interactive else False

    git_name, git_email = get_git_identity()
    ctx = ProjectContext(
        project_name=name,
        package_name=derive_package_name(name),
        description=description,
        stack_id=stack,
        license_id=license_id,
        author=config.author or git_name,
        email=config.email or git_email,
        year=datetime.datetime.now(tz=datetime.UTC).year,
        github_user=config.github_user,
        use_git=False,
        use_github=False,
        use_pre_commit=pre_commit,
    )
    plan = render_project(ctx)

    if dry_run:
        console.print("[bold yellow]dry run[/bold yellow] — nothing will be written\n")
        plan.preview(console)
        return

    try:
        root = plan.execute(target_dir)
    except FileExistsError as exc:
        raise _fail(str(exc)) from exc

    console.print(f"[bold green]✨ created[/bold green] {root}")
    steps = "\n".join(escape(step.format(name=name)) for step in STACKS[stack].next_steps)
    console.print(Panel(steps, title="next steps", border_style="green", title_align="left"))
