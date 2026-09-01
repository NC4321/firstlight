from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from firstlight.cli import app
from firstlight.config import UserConfig, save_config

EXPECTED_GO_FILES = {
    ".github/workflows/ci.yml",
    ".gitignore",
    "LICENSE",
    "README.md",
    "go.mod",
    "main.go",
    "main_test.go",
}


@pytest.fixture()
def scaffolded(runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        app, ["new", "demo-app", "--stack", "go", "--license", "mit", "--no-input", "--no-git"]
    )
    assert result.exit_code == 0, result.output
    return tmp_path / "demo-app"


def test_exact_tree(scaffolded: Path) -> None:
    files = {str(p.relative_to(scaffolded)) for p in scaffolded.rglob("*") if p.is_file()}
    assert files == EXPECTED_GO_FILES


def test_module_path_without_github_user(scaffolded: Path) -> None:
    assert (scaffolded / "go.mod").read_text().startswith("module demo-app\n")


def test_module_path_with_github_user(runner: CliRunner, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    save_config(UserConfig(github_user="octocat"))
    result = runner.invoke(app, ["new", "demo-app", "--stack", "go", "--no-input", "--no-git"])
    assert result.exit_code == 0, result.output
    go_mod = (tmp_path / "demo-app" / "go.mod").read_text()
    assert go_mod.startswith("module github.com/octocat/demo-app\n")


def test_ci_yaml_valid(scaffolded: Path) -> None:
    yaml.safe_load((scaffolded / ".github/workflows/ci.yml").read_text())
