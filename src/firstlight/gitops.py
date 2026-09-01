"""Git and GitHub integration. Every step degrades gracefully when a binary is missing:
the scaffold has already been written, so failures here warn (with the manual command
to run) instead of erroring."""

import shutil
import subprocess
from pathlib import Path

from firstlight.console import console


def _run(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)


def _warn(message: str) -> None:
    console.print(f"[yellow]warning:[/yellow] {message}")


def get_git_identity() -> tuple[str, str]:
    """(name, email) from git config, empty strings when unavailable."""
    if shutil.which("git") is None:
        return "", ""
    name = _run(["git", "config", "--get", "user.name"]).stdout.strip()
    email = _run(["git", "config", "--get", "user.email"]).stdout.strip()
    return name, email


def init_repo(root: Path) -> bool:
    """git init + first commit in root. Returns True on success."""
    if shutil.which("git") is None:
        _warn("git not found — skipping repo init. Run `git init` yourself later.")
        return False
    steps = (
        ["git", "init", "-b", "main"],
        ["git", "add", "-A"],
        ["git", "commit", "-m", "Initial commit (scaffolded by firstlight)"],
    )
    for step in steps:
        result = _run(step, cwd=root)
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip()
            _warn(f"`{' '.join(step)}` failed: {detail}\nFinish the git setup manually.")
            return False
    console.print("[green]✓[/green] git repo initialized with first commit")
    return True


def create_github_repo(root: Path, name: str, public: bool) -> bool:
    """Create a GitHub repo from root via the gh CLI and push. Returns True on success."""
    visibility = "--public" if public else "--private"
    manual = f"gh repo create {name} --source . --push {visibility}"
    if shutil.which("gh") is None:
        _warn(f"gh CLI not found — skipping GitHub repo. Run `{manual}` yourself later.")
        return False
    result = _run(["gh", "repo", "create", name, "--source", ".", "--push", visibility], cwd=root)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        _warn(f"GitHub repo creation failed: {detail}\nRun `{manual}` yourself later.")
        return False
    url = result.stdout.strip().splitlines()[0] if result.stdout.strip() else name
    console.print(f"[green]✓[/green] GitHub repo created: {url}")
    return True
