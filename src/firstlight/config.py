"""User config: saved defaults so prompts don't ask the same questions every time."""

import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path

import tomli_w
from platformdirs import user_config_dir


@dataclass
class UserConfig:
    author: str = ""
    email: str = ""
    default_stack: str = ""
    default_license: str = ""
    github_user: str = ""

    def non_empty(self) -> dict[str, str]:
        return {key: value for key, value in asdict(self).items() if value}


def config_path() -> Path:
    return Path(user_config_dir("firstlight")) / "config.toml"


def load_config() -> UserConfig:
    path = config_path()
    if not path.is_file():
        return UserConfig()
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    known = set(UserConfig.__dataclass_fields__)
    return UserConfig(**{key: value for key, value in data.items() if key in known})


def save_config(config: UserConfig) -> Path:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(tomli_w.dumps(config.non_empty()), encoding="utf-8")
    return path
