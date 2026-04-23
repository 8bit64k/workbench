import tempfile
from pathlib import Path
from workbench.scaffold import init_project
import pytest


def test_init_python_creates_structure():
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "my-project"
        init_project("python", "my-project", target)
        assert (target / "pyproject.toml").exists()
        assert (target / "README.md").exists()
        assert (target / "src" / "my_project" / "__init__.py").exists()
        assert (target / "tests" / "test_stub.py").exists()
        assert (target / ".git").is_dir()


def test_unknown_template_raises():
    with tempfile.TemporaryDirectory() as tmp:
        with pytest.raises(ValueError, match="not found"):
            init_project("nonexistent", "x", Path(tmp) / "x")


def test_target_exists_raises():
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "exists"
        target.mkdir()
        with pytest.raises(FileExistsError):
            init_project("python", "exists", target)
