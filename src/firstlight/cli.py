"""Typer application entry point."""

from typing import Annotated

import typer

from firstlight import __version__
from firstlight.commands.config import config_app
from firstlight.commands.new import new
from firstlight.console import console

app = typer.Typer(
    name="firstlight",
    help="Scaffold a new project — structure, README, license, CI, git — in one command.",
    no_args_is_help=True,
)
app.command()(new)
app.add_typer(config_app, name="config")


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"firstlight {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option("--version", callback=_version_callback, is_eager=True, help="Show version."),
    ] = False,
) -> None:
    """firstlight — every project's first light."""
