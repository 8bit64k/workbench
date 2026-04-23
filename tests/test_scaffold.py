import tempfile
from pathlib import Path
from workbench.scaffold import init_project
import pytest


def test_init_library_creates_structure():
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "my-lib"
        init_project("library", "my-lib", target)
        assert (target / "pyproject.toml").exists()
        assert (target / "README.md").exists()
        assert (target / "src" / "my_lib" / "__init__.py").exists()
        assert (target / "src" / "my_lib" / "core.py").exists()
        assert (target / "tests" / "test_core.py").exists()
        assert (target / ".git").is_dir()
        # Verify pyproject.toml has library-specific content
        pyproject = (target / "pyproject.toml").read_text()
        assert "classifiers" in pyproject
        assert "[project.optional-dependencies]" in pyproject
        # Verify README has usage example
        readme = (target / "README.md").read_text()
        assert "from my_lib.core import greet" in readme


def test_init_python_creates_structure():
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "my-project"
        init_project("python", "my-project", target)
        assert (target / "pyproject.toml").exists()
        assert (target / "README.md").exists()
        assert (target / "src" / "my_project" / "__init__.py").exists()
        assert (target / "tests" / "test_stub.py").exists()
        assert (target / ".git").is_dir()


def test_init_with_github_calls_gh():
    from unittest.mock import patch, MagicMock
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "gh-test"
        with patch("workbench.scaffold.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            init_project("python", "gh-test", target, github=True)
            calls = [c for c in mock_run.call_args_list if "gh" in str(c)]
            assert len(calls) >= 1


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
