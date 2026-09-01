"""The `firstlight config` subcommands: show, init, path."""

import typer
from rich.table import Table

from firstlight.config import UserConfig, config_path, load_config, save_config
from firstlight.console import console
from firstlight.context import LICENSES
from firstlight.gitops import get_git_identity
from firstlight.stacks import STACKS

config_app = typer.Typer(
    help="Manage saved defaults (author, license, stack).", no_args_is_help=True
)


@config_app.command()
def show() -> None:
    """Show the current saved defaults."""
    config = load_config()
    values = config.non_empty()
    if not values:
        console.print("No config saved yet — run [bold]firstlight config init[/bold].")
        return
    table = Table(show_header=False, box=None, pad_edge=False)
    for key, value in values.items():
        table.add_row(f"[bold]{key}[/bold]", value)
    console.print(table)


@config_app.command()
def path() -> None:
    """Print the config file location."""
    console.print(str(config_path()))


@config_app.command()
def init() -> None:
    """Interactively create (or update) the config file."""
    current = load_config()
    git_name, git_email = get_git_identity()

    author = typer.prompt("Author name", default=current.author or git_name or "")
    email = typer.prompt("Email", default=current.email or git_email or "")
    stack = typer.prompt(
        f"Default stack ({', '.join(sorted(STACKS))}, blank for none)",
        default=current.default_stack,
        show_default=bool(current.default_stack),
    )
    license_id = typer.prompt(
        f"Default license ({', '.join(LICENSES)}, blank for none)",
        default=current.default_license,
        show_default=bool(current.default_license),
    )
    github_user = typer.prompt(
        "GitHub username (blank for none)",
        default=current.github_user,
        show_default=bool(current.github_user),
    )

    stack = stack.strip()
    if stack and stack not in STACKS:
        console.print(f"[yellow]ignoring unknown stack {stack!r}[/yellow]")
        stack = ""
    license_id = license_id.strip()
    if license_id and license_id not in LICENSES:
        console.print(f"[yellow]ignoring unknown license {license_id!r}[/yellow]")
        license_id = ""

    config = UserConfig(
        author=author.strip(),
        email=email.strip(),
        default_stack=stack,
        default_license=license_id,
        github_user=github_user.strip(),
    )
    saved_to = save_config(config)
    console.print(f"[bold green]saved[/bold green] {saved_to}")
