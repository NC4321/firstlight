"""Render on-disk templates into an in-memory ScaffoldPlan.

Conventions:
- Every template file ends in ``.j2``; the suffix is stripped on output.
- A directory (or file) segment named ``__package_name__`` becomes the project's
  package name via plain string replacement — no Jinja in paths.
- Output layering: ``shared/`` first, then the stack's directory (stack wins on
  conflicts), then the chosen license file as ``LICENSE``.
"""

from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import PurePosixPath

from jinja2 import BaseLoader, Environment, StrictUndefined

from firstlight.context import ProjectContext
from firstlight.plan import FileEntry, ScaffoldPlan
from firstlight.stacks import STACKS

TEMPLATE_SUFFIX = ".j2"
PACKAGE_NAME_TOKEN = "__package_name__"

# Output paths only included when the context enables them.
_OPTIONAL_OUTPUTS = {".pre-commit-config.yaml": lambda ctx: ctx.use_pre_commit}


def _environment() -> Environment:
    return Environment(
        loader=BaseLoader(),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
    )


def _template_root() -> Traversable:
    return files("firstlight") / "templates"


def _walk(
    node: Traversable, prefix: PurePosixPath | None = None
) -> list[tuple[PurePosixPath, Traversable]]:
    prefix = prefix if prefix is not None else PurePosixPath(".")
    entries: list[tuple[PurePosixPath, Traversable]] = []
    for child in node.iterdir():
        path = prefix / child.name
        if child.is_dir():
            entries.extend(_walk(child, path))
        else:
            entries.append((path, child))
    return sorted(entries)


def _render_dir(env: Environment, root: Traversable, ctx: ProjectContext) -> dict[str, str]:
    rendered: dict[str, str] = {}
    for rel_path, entry in _walk(root):
        out_path = str(rel_path)
        out_path = out_path.removesuffix(TEMPLATE_SUFFIX)
        out_path = out_path.replace(PACKAGE_NAME_TOKEN, ctx.package_name)
        include = _OPTIONAL_OUTPUTS.get(out_path)
        if include is not None and not include(ctx):
            continue
        source = entry.read_text(encoding="utf-8")
        rendered[out_path] = env.from_string(source).render(**ctx.template_vars())
    return rendered


def render_project(ctx: ProjectContext) -> ScaffoldPlan:
    env = _environment()
    root = _template_root()
    stack = STACKS[ctx.stack_id]

    outputs: dict[str, str] = {}
    outputs.update(_render_dir(env, root / "shared", ctx))
    outputs.update(_render_dir(env, root / stack.template_dir, ctx))

    if ctx.has_license:
        license_source = (root / "licenses" / f"{ctx.license_id}.txt.j2").read_text(
            encoding="utf-8"
        )
        outputs["LICENSE"] = env.from_string(license_source).render(**ctx.template_vars())

    file_entries = [
        FileEntry(path=path, content=content) for path, content in sorted(outputs.items())
    ]
    return ScaffoldPlan(project_name=ctx.project_name, files=file_entries)
