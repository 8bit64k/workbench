# workbench v0 Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build a CLI project scaffolding tool (`workbench`) that generates boilerplate projects from templates. Learn Python packaging, TDD, git workflows, and CLI design by building it.

**Architecture:** Single Python package with a CLI entrypoint. Templates stored as directories in `src/workbench/templates/`. Uses `argparse` for CLI, `jinja2` for template variable substitution, `pytest` for TDD. Installs via `uv pip install -e .` with a `pyproject.toml` script.

**Tech Stack:** Python 3.12+, uv, pytest, jinja2, git, GitHub CLI (gh)

**Assumptions:**
- Tool invoked as `workbench init <template> <project-name>`
- v0 supports one template: `python` (standard src-layout Python project)
- Templates include: folder structure, `pyproject.toml`, `.gitignore`, starter test, README
- No external config files or registries yet (YAGNI)

---

## Task 1: Scaffold the `workbench` repo itself

**Objective:** Create the repo structure that `workbench` itself will generate for others.

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `.gitignore`
- Create: `src/workbench/__init__.py`
- Create: `src/workbench/cli.py`
- Create: `tests/__init__.py`
- Create: `tests/test_cli.py`

**Step 1: Write `pyproject.toml`**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "workbench"
version = "0.1.0"
description = "CLI project scaffolding tool"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "jinja2>=3.1.0",
]

[project.scripts]
workbench = "workbench.cli:main"

[dependency-groups]
dev = [
    "pytest>=8.0",
]
```

**Step 2: Write minimal `.gitignore`**

```gitignore
__pycache__/
*.pyc
*.egg-info/
.env
.venv/
dist/
build/
```

**Step 3: Create empty `src/workbench/__init__.py`**

```python
__version__ = "0.1.0"
```

**Step 4: Create empty `src/workbench/cli.py`**

```python
def main():
    print("workbench v0.1.0")
```

**Step 5: Create empty `tests/__init__.py` and `tests/test_cli.py`**

```python
# tests/test_cli.py
def test_stub():
    assert True
```

**Step 6: Install in editable mode**

```bash
uv pip install -e ".[dev]"
```

Expected: Package installs successfully.

**Step 7: Verify CLI works**

```bash
workbench
```

Expected output: `workbench v0.1.0`

**Step 8: Run tests**

```bash
pytest tests/ -v
```

Expected: 1 passed (the stub)

**Step 9: Commit**

```bash
git add .
git commit -m "chore: scaffold workbench repo structure"
```

---

## Task 2: Implement `workbench --version`

**Objective:** Add real CLI argument parsing with `--version` support. First TDD cycle.

**Files:**
- Modify: `src/workbench/cli.py`
- Modify: `tests/test_cli.py`

**Step 1: Write failing test**

```python
# tests/test_cli.py
from workbench.cli import main
import sys
from io import StringIO

def test_version_flag():
    old_argv = sys.argv
    old_stdout = sys.stdout
    try:
        sys.argv = ["workbench", "--version"]
        sys.stdout = StringIO()
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0
        assert "0.1.0" in sys.stdout.getvalue()
    finally:
        sys.argv = old_argv
        sys.stdout = old_stdout
```

Run: `pytest tests/test_cli.py::test_version_flag -v`
Expected: FAIL

**Step 2: Implement `--version`**

```python
# src/workbench/cli.py
import argparse
from workbench import __version__

def main():
    parser = argparse.ArgumentParser(prog="workbench")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.parse_args()
```

Run: `pytest tests/test_cli.py::test_version_flag -v`
Expected: PASS

**Step 3: Commit**

```bash
git add src/workbench/cli.py tests/test_cli.py
git commit -m "feat: add --version flag"
```

---

## Task 3: Implement `workbench init python <name>` (happy path)

**Objective:** Scaffold a Python project into a new directory.

**Files:**
- Create: `src/workbench/templates/python/pyproject.toml.j2`
- Create: `src/workbench/templates/python/README.md.j2`
- Create: `src/workbench/templates/python/.gitignore`
- Create: `src/workbench/templates/python/src/{{project_name}}/__init__.py.j2`
- Create: `src/workbench/templates/python/tests/__init__.py`
- Create: `src/workbench/templates/python/tests/test_stub.py`
- Create: `src/workbench/scaffold.py`
- Modify: `src/workbench/cli.py`
- Create: `tests/test_scaffold.py`

**Step 1: Write templates**

```toml
{# src/workbench/templates/python/pyproject.toml.j2 #}
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{{project_name}}"
version = "0.1.0"
description = "{{project_description or 'A Python project'}}"
readme = "README.md"
requires-python = ">=3.12"
```

```markdown
{# src/workbench/templates/python/README.md.j2 #}
# {{project_name}}

{{project_description or 'A Python project.'}}
```

```python
{# src/workbench/templates/python/src/{{project_name}}/__init__.py.j2 #}
__version__ = "0.1.0"
```

`.gitignore`, `tests/__init__.py`, and `tests/test_stub.py` are static (no Jinja).

**Step 2: Write failing scaffold test**

```python
# tests/test_scaffold.py
import tempfile
import os
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
```

Run: `pytest tests/test_scaffold.py::test_init_python_creates_structure -v`
Expected: FAIL

**Step 3: Implement `scaffold.py`**

```python
# src/workbench/scaffold.py
from pathlib import Path
import shutil
import jinja2

TEMPLATE_DIR = Path(__file__).parent / "templates"

def init_project(template_name: str, project_name: str, target: Path) -> None:
    template_path = TEMPLATE_DIR / template_name
    if not template_path.exists():
        raise ValueError(f"Template '{template_name}' not found")

    target.mkdir(parents=True, exist_ok=False)
    snake_name = project_name.replace("-", "_").lower()

    env = jinja2.Environment()

    for src in template_path.rglob("*"):
        rel = src.relative_to(template_path)
        dst = target / rel

        # Expand {{project_name}} in directory names
        dst_str = str(dst).replace("{{project_name}}", snake_name)
        dst = Path(dst_str)

        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            continue

        if src.suffix == ".j2":
            content = src.read_text()
            template = env.from_string(content)
            rendered = template.render(project_name=snake_name, project_description="")
            dst = dst.with_suffix("")  # strip .j2
            dst.write_text(rendered)
        else:
            shutil.copy2(src, dst)
```

**Step 4: Wire into CLI**

```python
# src/workbench/cli.py
import argparse
import sys
from pathlib import Path
from workbench import __version__
from workbench.scaffold import init_project

def main():
    parser = argparse.ArgumentParser(prog="workbench")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("template", choices=["python"])
    init_parser.add_argument("name")

    args = parser.parse_args()

    if args.command == "init":
        target = Path.cwd() / args.name
        init_project(args.template, args.name, target)
        print(f"Created {args.template} project '{args.name}' at {target}")
    else:
        parser.print_help()
        sys.exit(1)
```

Run: `pytest tests/test_scaffold.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/workbench/templates/ src/workbench/scaffold.py src/workbench/cli.py tests/test_scaffold.py
git commit -m "feat: implement workbench init python <name>"
```

---

## Task 4: Run `git init` in the scaffolded project

**Objective:** After generating files, automatically `git init` the new project.

**Files:**
- Modify: `src/workbench/scaffold.py`
- Modify: `tests/test_scaffold.py`

**Step 1: Write failing test**

Add to `test_init_python_creates_structure`:

```python
assert (target / ".git").is_dir()
```

Run: `pytest tests/test_scaffold.py -v`
Expected: FAIL

**Step 2: Add `git init` to scaffold.py**

```python
import subprocess

def init_project(...):
    # ... existing code ...
    subprocess.run(["git", "init"], cwd=target, check=True, capture_output=True)
```

Run: `pytest tests/test_scaffold.py -v`
Expected: PASS

**Step 3: Commit**

```bash
git add src/workbench/scaffold.py tests/test_scaffold.py
git commit -m "feat: run git init in scaffolded projects"
```

---

## Task 5: Error handling and edge cases

**Objective:** Handle bad inputs gracefully.

**Files:**
- Modify: `src/workbench/scaffold.py`
- Modify: `tests/test_scaffold.py`

**Step 1: Test unknown template**

```python
def test_unknown_template_raises():
    with tempfile.TemporaryDirectory() as tmp:
        with pytest.raises(ValueError, match="not found"):
            init_project("nonexistent", "x", Path(tmp) / "x")
```

**Step 2: Test target already exists**

```python
def test_target_exists_raises():
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "exists"
        target.mkdir()
        with pytest.raises(FileExistsError):
            init_project("python", "exists", target)
```

Run tests, fix code, commit.

```bash
git add src/workbench/scaffold.py tests/test_scaffold.py
git commit -m "feat: error handling for unknown templates and existing dirs"
```

---

## Task 6: GitHub repo creation (optional, v0.1 stretch)

**Objective:** After scaffolding, optionally create a GitHub repo via `gh`.

**Files:**
- Modify: `src/workbench/cli.py`
- Modify: `tests/test_cli.py`

**Approach:** Add `--github` flag to `init`. If present, run `gh repo create <name> --private --source=. --push` inside the target dir.

Skip if `gh` not installed. Skip tests if `GH_TOKEN` not set (mock with `unittest.mock`).

**Step 1: Add flag and test mock**

```python
# tests/test_cli.py
from unittest.mock import patch, MagicMock

def test_init_with_github_flag():
    with tempfile.TemporaryDirectory() as tmp:
        with patch("workbench.scaffold.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            target = Path(tmp) / "gh-test"
            init_project("python", "gh-test", target, github=True)
            # assert gh repo create was called
```

Implement, test, commit.

---

## Task 7: Polish and push to GitHub

**Objective:** Clean README, add basic usage docs, push repo.

**Files:**
- Modify: `README.md`

**README should include:**
- What workbench is
- Install: `uv pip install -e .`
- Usage: `workbench init python my-project`
- Development: `pytest tests/ -v`

**Push:**

```bash
gh repo create workbench --public --source=. --push
```

---

## Verification Checklist

- [ ] `workbench --version` prints version
- [ ] `workbench init python test-proj` creates a valid Python project
- [ ] Generated project passes its own `pytest` run
- [ ] Generated project is a valid git repo
- [ ] Unknown template raises clear error
- [ ] Existing dir raises clear error
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Repo is on GitHub with clean commit history

---

## Open Questions

1. **More templates?** `node`, `rust`, `go`? (defer to v1)
2. **Config file support?** `.workbenchrc` or similar? (defer)
3. **Template registry / remote templates?** (defer)
4. **Pre/post hooks?** (defer)
