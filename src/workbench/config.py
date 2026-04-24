from pathlib import Path
from typing import Any
import os
import tomllib
import tomli_w

DEFAULTS: dict[str, Any] = {
    "author": None,
    "email": None,
    "license": "MIT",
    "default_output_format": "ansi",
    "default_template_dir": None,
}


def _get_config_dir() -> Path:
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        return Path(xdg_config) / "workbench"
    return Path.home() / ".config" / "workbench"


def _ensure_config_dir() -> Path:
    cfg_dir = _get_config_dir()
    cfg_dir.mkdir(parents=True, exist_ok=True)
    return cfg_dir


def get_config_path() -> Path:
    return _get_config_dir() / "config.toml"


def load_config() -> dict[str, Any]:
    """Load config from disk, merging with defaults."""
    config = dict(DEFAULTS)
    path = get_config_path()
    if path.exists():
        with open(path, "rb") as f:
            data = tomllib.load(f)
        config.update(data)
    return config


def save_config(config: dict[str, Any]) -> None:
    """Atomically write config to disk."""
    path = get_config_path()
    _ensure_config_dir()
    # Filter out None values — tomli_w cannot serialize None
    clean = {k: v for k, v in config.items() if v is not None}
    tmp = path.with_suffix(".tmp")
    with open(tmp, "wb") as f:
        tomli_w.dump(clean, f)
    tmp.replace(path)


def get_config_value(key: str) -> Any:
    """Get a single config value. Returns None if unset."""
    return load_config().get(key)
