"""Shared Rich consoles for all commands."""

from rich.console import Console

console = Console()
err_console = Console(stderr=True)
