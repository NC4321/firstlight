from pathlib import Path

import pytest

from firstlight.plan import FileEntry, ScaffoldPlan


def make_plan() -> ScaffoldPlan:
    return ScaffoldPlan(
        project_name="demo",
        files=[
            FileEntry(path="README.md", content="# demo\n"),
            FileEntry(path="src/demo/__init__.py", content=""),
        ],
    )


def test_execute_writes_tree(tmp_path: Path) -> None:
    root = make_plan().execute(tmp_path)
    assert root == tmp_path / "demo"
    assert (root / "README.md").read_text() == "# demo\n"
    assert (root / "src/demo/__init__.py").exists()


def test_execute_refuses_existing_root(tmp_path: Path) -> None:
    (tmp_path / "demo").mkdir()
    with pytest.raises(FileExistsError):
        make_plan().execute(tmp_path)
