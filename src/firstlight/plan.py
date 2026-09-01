"""ScaffoldPlan: the in-memory result of rendering, consumed by dry-run preview and execute."""

from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from rich.console import Console
from rich.tree import Tree


@dataclass(frozen=True)
class FileEntry:
    path: str  # POSIX-style path relative to the project root
    content: str


@dataclass(frozen=True)
class ScaffoldPlan:
    project_name: str
    files: list[FileEntry]

    def preview(self, console: Console) -> None:
        tree = Tree(f"[bold]{self.project_name}/[/bold]")
        branches: dict[str, Tree] = {"": tree}
        for entry in self.files:
            parts = PurePosixPath(entry.path).parts
            parent_key = ""
            for part in parts[:-1]:
                key = f"{parent_key}/{part}"
                if key not in branches:
                    branches[key] = branches[parent_key].add(f"[cyan]{part}/[/cyan]")
                parent_key = key
            size = len(entry.content.encode("utf-8"))
            branches[parent_key].add(f"{parts[-1]} [dim]({size} bytes)[/dim]")
        console.print(tree)

    def execute(self, parent_dir: Path) -> Path:
        """Write all files under parent_dir/project_name. Refuses to overwrite anything."""
        root = parent_dir / self.project_name
        if root.exists():
            raise FileExistsError(f"{root} already exists")
        for entry in self.files:
            target = root / PurePosixPath(entry.path)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                raise FileExistsError(f"{target} already exists")
            target.write_text(entry.content, encoding="utf-8")
        return root
