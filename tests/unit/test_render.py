from importlib.resources import files

import pytest

from firstlight.context import ProjectContext
from firstlight.render import render_project
from firstlight.stacks import STACKS


def make_context(**overrides: object) -> ProjectContext:
    defaults: dict = {
        "project_name": "demo-app",
        "package_name": "demo_app",
        "description": "A demo.",
        "stack_id": "python",
        "license_id": "mit",
        "author": "Test Author",
        "email": "test@example.com",
        "year": 2026,
        "github_user": "tester",
        "use_git": True,
        "use_github": False,
        "use_pre_commit": False,
    }
    defaults.update(overrides)
    return ProjectContext(**defaults)


@pytest.mark.parametrize("stack_id", sorted(STACKS))
def test_render_produces_clean_output(stack_id: str) -> None:
    plan = render_project(make_context(stack_id=stack_id))
    assert plan.files
    for entry in plan.files:
        assert not entry.path.endswith(".j2"), entry.path
        assert "__package_name__" not in entry.path, entry.path
        assert "{%" not in entry.content, entry.path
        assert "__package_name__" not in entry.content, entry.path


def test_package_name_substituted_in_paths() -> None:
    plan = render_project(make_context())
    paths = {entry.path for entry in plan.files}
    assert "src/demo_app/__init__.py" in paths


def test_license_rendered_with_author_and_year() -> None:
    plan = render_project(make_context(license_id="mit"))
    license_file = next(entry for entry in plan.files if entry.path == "LICENSE")
    assert "Test Author" in license_file.content
    assert "2026" in license_file.content


def test_no_license_means_no_license_file() -> None:
    plan = render_project(make_context(license_id="none"))
    paths = {entry.path for entry in plan.files}
    assert "LICENSE" not in paths
    readme = next(entry for entry in plan.files if entry.path == "README.md")
    assert "License" not in readme.content


def test_pre_commit_only_when_requested() -> None:
    without = {e.path for e in render_project(make_context(use_pre_commit=False)).files}
    with_pc = {e.path for e in render_project(make_context(use_pre_commit=True)).files}
    assert ".pre-commit-config.yaml" not in without
    assert ".pre-commit-config.yaml" in with_pc


def test_actions_expressions_survive() -> None:
    plan = render_project(make_context(stack_id="python"))
    ci = next(entry for entry in plan.files if entry.path == ".github/workflows/ci.yml")
    assert "${{ matrix.python-version }}" in ci.content


@pytest.mark.parametrize("stack_id", sorted(STACKS))
def test_template_dirs_ship_with_package(stack_id: str) -> None:
    template_dir = files("firstlight") / "templates" / STACKS[stack_id].template_dir
    assert any(template_dir.iterdir())
