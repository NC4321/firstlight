"""ProjectContext: the single immutable object handed to templates."""

from dataclasses import dataclass

LICENSES = ("mit", "apache-2.0", "none")

LICENSE_DISPLAY = {
    "mit": "MIT",
    "apache-2.0": "Apache-2.0",
    "none": "No license",
}


@dataclass(frozen=True)
class ProjectContext:
    project_name: str
    package_name: str
    description: str
    stack_id: str
    license_id: str
    author: str
    email: str
    year: int
    github_user: str
    use_git: bool
    use_github: bool
    use_pre_commit: bool

    @property
    def license_display(self) -> str:
        return LICENSE_DISPLAY[self.license_id]

    @property
    def has_license(self) -> bool:
        return self.license_id != "none"

    def template_vars(self) -> dict[str, object]:
        return {
            "project_name": self.project_name,
            "package_name": self.package_name,
            "description": self.description,
            "stack_id": self.stack_id,
            "license_id": self.license_id,
            "license_display": self.license_display,
            "has_license": self.has_license,
            "author": self.author,
            "email": self.email,
            "year": self.year,
            "github_user": self.github_user,
            "use_pre_commit": self.use_pre_commit,
        }


def derive_package_name(project_name: str) -> str:
    """my-cool-project -> my_cool_project (importable module name)."""
    return project_name.replace("-", "_")
