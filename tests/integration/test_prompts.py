from pathlib import Path

import pytest
from typer.testing import CliRunner

from firstlight.cli import app
from firstlight.config import UserConfig, save_config


def test_interactive_flow(runner: CliRunner, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    # stack, license, description, pre-commit, git
    result = runner.invoke(app, ["new", "demo-app"], input="python\nmit\nA demo.\ny\nn\n")
    assert result.exit_code == 0, result.output
    root = tmp_path / "demo-app"
    assert (root / ".pre-commit-config.yaml").exists()
    assert "A demo." in (root / "README.md").read_text()


def test_prompts_accept_defaults(runner: CliRunner, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["new", "demo-app"], input="\n\n\n\nn\n")
    assert result.exit_code == 0, result.output
    assert (tmp_path / "demo-app" / "pyproject.toml").exists()  # built-in default stack


def test_config_seeds_prompt_defaults(runner: CliRunner, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    save_config(UserConfig(default_license="apache-2.0", author="Ada Lovelace"))
    result = runner.invoke(app, ["new", "demo-app"], input="\n\n\n\nn\n")
    assert result.exit_code == 0, result.output
    license_text = (tmp_path / "demo-app" / "LICENSE").read_text()
    assert "Apache License" in license_text
    assert "Ada Lovelace" in license_text


def test_invalid_prompt_answer_reasks(runner: CliRunner, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["new", "demo-app"], input="cobol\npython\nmit\nA demo.\nn\nn\n")
    assert result.exit_code == 0, result.output
    assert (tmp_path / "demo-app").exists()


@pytest.mark.parametrize("command", [["config", "show"], ["config", "path"]])
def test_config_readonly_commands(runner: CliRunner, command: list[str]) -> None:
    result = runner.invoke(app, command)
    assert result.exit_code == 0


def test_config_init_and_show(runner: CliRunner) -> None:
    result = runner.invoke(
        app, ["config", "init"], input="Ada\nada@example.com\npython\nmit\nada-gh\n"
    )
    assert result.exit_code == 0, result.output
    shown = runner.invoke(app, ["config", "show"])
    assert "Ada" in shown.output
    assert "python" in shown.output
