import os
import shutil
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from firstlight.cli import app

needs_git = pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")


@pytest.fixture()
def fake_gh(tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A gh stand-in on PATH that records its argv and prints a repo URL."""
    bin_dir = tmp_path_factory.mktemp("fake-bin")
    log = bin_dir / "gh-args.log"
    script = bin_dir / "gh"
    script.write_text(f'#!/bin/sh\necho "$@" >> "{log}"\necho "https://example.com/fake/repo"\n')
    script.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    return log


@needs_git
def test_git_init_and_first_commit(runner: CliRunner, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["new", "demo-app", "--no-input", "--git"])
    assert result.exit_code == 0, result.output
    root = tmp_path / "demo-app"
    assert (root / ".git").is_dir()
    log = subprocess.run(
        ["git", "log", "--oneline"], cwd=root, capture_output=True, text=True, check=True
    )
    assert "firstlight" in log.stdout


@needs_git
def test_github_repo_created_via_gh(
    runner: CliRunner, tmp_path: Path, monkeypatch, fake_gh: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["new", "demo-app", "--no-input", "--git", "--github", "--public"])
    assert result.exit_code == 0, result.output
    recorded = fake_gh.read_text()
    assert "repo create demo-app" in recorded
    assert "--public" in recorded


@needs_git
def test_missing_gh_warns_but_succeeds(runner: CliRunner, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PATH", str(tmp_path / "empty-bin"))  # no gh here (and no git either)
    result = runner.invoke(app, ["new", "demo-app", "--no-input", "--git", "--github"])
    assert result.exit_code == 0, result.output
    assert "warning" in result.output.lower()
    assert (tmp_path / "demo-app" / "pyproject.toml").exists()  # scaffold still completed


def test_github_without_git_fails(runner: CliRunner, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["new", "demo-app", "--no-input", "--no-git", "--github"])
    assert result.exit_code == 1
    assert not (tmp_path / "demo-app").exists()
