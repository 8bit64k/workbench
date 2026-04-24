import os
from pathlib import Path
import pytest
from workbench import config as config_module


@pytest.fixture
def isolated_config(monkeypatch, tmp_path):
    """Redirect config directory to a temp path."""
    monkeypatch.setattr(config_module, "_get_config_dir", lambda: tmp_path / "workbench")
    yield tmp_path / "workbench"


def test_default_config(isolated_config):
    cfg = config_module.load_config()
    assert cfg["author"] is None
    assert cfg["email"] is None
    assert cfg["license"] == "MIT"
    assert cfg["default_output_format"] == "ansi"
    assert cfg["default_template_dir"] is None


def test_save_and_load_config(isolated_config):
    config_module.save_config({"author": "8bit64k", "license": "Apache-2.0"})
    cfg = config_module.load_config()
    assert cfg["author"] == "8bit64k"
    assert cfg["license"] == "Apache-2.0"
    assert cfg["email"] is None


def test_get_config_value(isolated_config):
    config_module.save_config({"author": "Test Author"})
    assert config_module.get_config_value("author") == "Test Author"
    assert config_module.get_config_value("nonexistent_key") is None


def test_xdg_config_home_respected(monkeypatch, tmp_path):
    xdg_dir = tmp_path / "xdg"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_dir))
    assert config_module._get_config_dir() == xdg_dir / "workbench"


def test_fallback_config_dir(monkeypatch, tmp_path):
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    assert config_module._get_config_dir() == tmp_path / ".config" / "workbench"
