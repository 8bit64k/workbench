import tempfile
from pathlib import Path
from workbench.scaffold import init_project
import pytest


def test_init_cli_creates_structure():
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "my-cli"
        init_project("cli", "my-cli", target)
        assert (target / "pyproject.toml").exists()
        assert (target / "README.md").exists()
        assert (target / "src" / "my_cli" / "__init__.py").exists()
        assert (target / "src" / "my_cli" / "cli.py").exists()
        assert (target / "tests" / "test_cli.py").exists()
        assert (target / ".git").is_dir()
        assert (target / ".github" / "workflows" / "test.yml").exists()
        # Verify pyproject.toml has CLI entry point
        pyproject = (target / "pyproject.toml").read_text()
        assert "[project.scripts]" in pyproject
        assert 'my_cli = "my_cli.cli:main"' in pyproject
        # Verify CLI has argparse structure
        cli_code = (target / "src" / "my_cli" / "cli.py").read_text()
        assert "argparse" in cli_code
        assert "subparsers" in cli_code
        # Verify tests use monkeypatch (not brittle sys.argv mutation)
        test_code = (target / "tests" / "test_cli.py").read_text()
        assert "monkeypatch" in test_code
        assert "test_bare_invocation_prints_help" in test_code
        assert "test_unknown_subcommand_exits_with_error" in test_code


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
        assert (target / ".github" / "workflows" / "test.yml").exists()
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
        assert (target / ".github" / "workflows" / "test.yml").exists()


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


def test_init_dry_run_does_not_create_files():
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "dry-test"
        init_project("python", "dry-test", target, dry_run=True)
        assert not target.exists()


def test_init_dry_run_returns_actions():
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "dry-test"
        actions = init_project("python", "dry-test", target, dry_run=True)
        assert isinstance(actions, list)
        assert any("pyproject.toml" in str(a) for a in actions)
        assert any("README.md" in str(a) for a in actions)


def test_get_templates_discovers_templates():
    from workbench.scaffold import get_templates
    templates = get_templates()
    assert "python" in templates
    assert "library" in templates
    assert "cli" in templates
