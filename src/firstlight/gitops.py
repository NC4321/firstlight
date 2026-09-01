"""Git and GitHub integration. Every step degrades gracefully when a binary is missing."""

import shutil
import subprocess


def _git(*args: str, cwd: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)


def get_git_identity() -> tuple[str, str]:
    """(name, email) from git config, empty strings when unavailable."""
    if shutil.which("git") is None:
        return "", ""
    name = _git("config", "--get", "user.name").stdout.strip()
    email = _git("config", "--get", "user.email").stdout.strip()
    return name, email
