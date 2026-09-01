from pathlib import Path

import pytest

from firstlight.validation import (
    MAX_NAME_LENGTH,
    ValidationError,
    validate_project_name,
    validate_target_dir,
)


@pytest.mark.parametrize("name", ["demo", "my-project", "web2png", "a", "x-1-y"])
def test_valid_names(name: str) -> None:
    validate_project_name(name)


@pytest.mark.parametrize(
    "name",
    [
        "My-Project",  # uppercase
        "my project",  # space
        "1st-app",  # leading digit
        "-app",  # leading hyphen
        "app-",  # trailing hyphen
        "my--app",  # double hyphen
        "my_app",  # underscore
        "app!",  # punctuation
        "",  # empty
        "a" * (MAX_NAME_LENGTH + 1),  # too long
        "tests",  # reserved
        "src",  # reserved
    ],
)
def test_invalid_names(name: str) -> None:
    with pytest.raises(ValidationError):
        validate_project_name(name)


def test_target_dir_free(tmp_path: Path) -> None:
    validate_target_dir(tmp_path / "new-project")


def test_target_dir_exists(tmp_path: Path) -> None:
    (tmp_path / "taken").mkdir()
    with pytest.raises(ValidationError, match="already exists"):
        validate_target_dir(tmp_path / "taken")
