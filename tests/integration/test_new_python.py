import ast
import json  # noqa: F401  (used for node stack later)
import tomllib
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from firstlight.cli import app

EXPECTED_PYTHON_FILES = {
    ".github/workflows/ci.yml",
    ".gitignore",
    "LICENSE",
    "README.md",
    "pyproject.toml",
    "src/demo_app/__init__.py",
    "tests/test_smoke.py",
}


@pytest.fixture()
def scaffolded(runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["new", "demo-app", "--stack", "python", "--license", "mit"])
    assert result.exit_code == 0, result.output
    return tmp_path / "demo-app"


def _files(root: Path) -> set[str]:
    return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}


def test_exact_tree(scaffolded: Path) -> None:
    assert _files(scaffolded) == EXPECTED_PYTHON_FILES


def test_generated_python_parses(scaffolded: Path) -> None:
    for py in scaffolded.rglob("*.py"):
        ast.parse(py.read_text(), filename=str(py))


def test_generated_configs_parse(scaffolded: Path) -> None:
    tomllib.loads((scaffolded / "pyproject.toml").read_text())
    ci = (scaffolded / ".github/workflows/ci.yml").read_text()
    yaml.safe_load(ci)
    assert "${{" in ci  # Actions expressions survived Jinja


def test_license_filled_in(scaffolded: Path) -> None:
    license_text = (scaffolded / "LICENSE").read_text()
    assert "2026" in license_text or "20" in license_text  # current year present
    assert "Copyright" in license_text


def test_existing_dir_fails_cleanly(runner: CliRunner, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "demo-app").mkdir()
    result = runner.invoke(app, ["new", "demo-app"])
    assert result.exit_code == 1
    assert "already exists" in result.output


def test_bad_name_fails_cleanly(runner: CliRunner, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["new", "Bad Name"])
    assert result.exit_code == 1
    assert not (tmp_path / "Bad Name").exists()


def test_unknown_stack_fails(runner: CliRunner, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["new", "demo", "--stack", "cobol"])
    assert result.exit_code == 1
