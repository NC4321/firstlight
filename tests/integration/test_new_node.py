import json
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from firstlight.cli import app

EXPECTED_NODE_FILES = {
    ".github/workflows/ci.yml",
    ".gitignore",
    "LICENSE",
    "README.md",
    "eslint.config.js",
    "package.json",
    "src/index.ts",
    "tests/index.test.ts",
    "tsconfig.json",
}


@pytest.fixture()
def scaffolded(runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        app, ["new", "demo-app", "--stack", "node", "--license", "mit", "--no-input", "--no-git"]
    )
    assert result.exit_code == 0, result.output
    return tmp_path / "demo-app"


def test_exact_tree(scaffolded: Path) -> None:
    files = {str(p.relative_to(scaffolded)) for p in scaffolded.rglob("*") if p.is_file()}
    assert files == EXPECTED_NODE_FILES


def test_generated_json_parses(scaffolded: Path) -> None:
    package = json.loads((scaffolded / "package.json").read_text())
    assert package["name"] == "demo-app"
    assert package["license"] == "MIT"
    json.loads((scaffolded / "tsconfig.json").read_text())


def test_no_license_keeps_json_valid(runner: CliRunner, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        app, ["new", "demo-app", "--stack", "node", "--license", "none", "--no-input", "--no-git"]
    )
    assert result.exit_code == 0, result.output
    package = json.loads((tmp_path / "demo-app" / "package.json").read_text())
    assert "license" not in package


def test_ci_yaml_valid(scaffolded: Path) -> None:
    ci = (scaffolded / ".github/workflows/ci.yml").read_text()
    yaml.safe_load(ci)
