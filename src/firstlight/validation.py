"""Early input validation — bad names and existing directories fail before anything renders."""

import re
from pathlib import Path

# Lowercase kebab-case: valid as a PyPI name, npm name, Go module element, and directory.
NAME_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
MAX_NAME_LENGTH = 64

# Names that make a confusing or broken project (import shadowing, tooling collisions).
RESERVED_NAMES = frozenset({"src", "test", "tests", "dist", "build", "node_modules", "main"})


class ValidationError(ValueError):
    """A user-input problem with a message suitable for direct display."""


def validate_project_name(name: str) -> None:
    if len(name) > MAX_NAME_LENGTH:
        raise ValidationError(f"Project name is too long (max {MAX_NAME_LENGTH} characters).")
    if not NAME_RE.match(name):
        raise ValidationError(
            f"Invalid project name {name!r}: use lowercase letters, digits, and hyphens, "
            "starting with a letter (e.g. 'my-project')."
        )
    if name in RESERVED_NAMES:
        raise ValidationError(f"{name!r} is a reserved name — pick something more distinctive.")


def validate_target_dir(target: Path) -> None:
    if target.exists():
        raise ValidationError(f"Directory {target} already exists — refusing to overwrite.")
