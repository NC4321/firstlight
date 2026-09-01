from pathlib import Path

import pytest
from typer.testing import CliRunner

from firstlight.cli import app


def test_dry_run_writes_nothing(runner: CliRunner, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["new", "demo-app", "--dry-run"])
    assert result.exit_code == 0, result.output
    assert list(tmp_path.iterdir()) == []
    assert "pyproject.toml" in result.output


def test_dry_run_works_even_if_dir_exists(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "demo-app").mkdir()
    result = runner.invoke(app, ["new", "demo-app", "--dry-run"])
    assert result.exit_code == 0, result.output
