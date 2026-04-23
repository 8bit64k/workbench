import tempfile
from pathlib import Path
from workbench.scaffold import init_project


def test_init_python_creates_structure():
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "my-project"
        init_project("python", "my-project", target)
        assert (target / "pyproject.toml").exists()
        assert (target / "README.md").exists()
        assert (target / "src" / "my_project" / "__init__.py").exists()
        assert (target / "tests" / "test_stub.py").exists()
        assert (target / ".git").is_dir()
