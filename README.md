# workbench

> A minimal, opinionated CLI scaffolding tool for Python projects. No interactive prompts, no bloat — just fast, repeatable project generation.

## Philosophy

`workbench` exists because scaffolding should be **deterministic and fast**. You know what you want to build; workbench gives you a clean starting point in under a second. Every generated project comes with:

- **Strict TDD-ready test structure** (pytest, monkeypatch isolation patterns)
- **Modern packaging** (hatchling, `pyproject.toml`, src-layout)
- **CI from day one** (GitHub Actions with uv, Python 3.12 + 3.13 matrix)
- **Clean git init** (no commits, just a ready repo)

---

## Install

```bash
cd ~/Code/workbench
uv pip install -e ".[dev]"
```

Requires Python ≥ 3.12 and [uv](https://github.com/astral-sh/uv).

---

## Quick Start

```bash
# See what templates are available
workbench list

# Inspect a template before using it
workbench info fastapi

# Scaffold a project in the current directory
workbench init cli my-tool

# Scaffold into a specific directory
workbench init library my-lib --output ~/Code/

# Preview what would be created (no files written)
workbench init python my-project --dry-run

# Scaffold and create a private GitHub repo (requires gh CLI auth)
workbench init python my-project --github
```

---

## Feature List

### Discovery & Inspection
- **`workbench list`** — Dynamically discovers available templates from the templates directory. New templates automatically appear here.
- **`workbench info &lt;template&gt;`** — Shows template metadata: name, file count, and complete file tree. No surprises.

### Scaffolding
- **`workbench init &lt;template&gt; &lt;name&gt;`** — Generates a complete project from a template.
- **`--output &lt;path&gt;` / `-o &lt;path&gt;`** — Scaffold into a custom directory instead of the current working directory.
- **`--dry-run`** — Preview every file that would be created without writing anything to disk. Essential for scripting and sanity-checking.
- **`--github`** — Auto-creates a private GitHub repo and pushes the initial commit (requires [gh](https://cli.github.com/) authentication).

### Template System
- **Jinja2-powered rendering** — Template files use `.j2` extension and render `{{project_name}}`, `{{project_description}}`, and other variables.
- **Directory name expansion** — `{{project_name}}` in directory paths is automatically converted to `snake_case`.
- **Dynamic template discovery** — Adding a new template directory to `src/workbench/templates/` makes it immediately available — no code changes required.

### Generated Project Quality
- **src-layout** for all Python projects
- **pytest** configured with `pythonpath = ["src"]` for clean imports
- **GitHub Actions CI** with `uv` setup and Python version matrix (3.12, 3.13)
- **Proper `.gitignore`** (`.venv`, `__pycache__`, `.pyc`)
- **Tests that don't suck** — monkeypatch-based CLI isolation, no brittle `sys.argv` mutation

---

## Templates

| Template | Best For | Key Dependencies |
|----------|----------|------------------|
| `python` | Bare-bones Python scripts | None |
| `library` | Reusable PyPI-ready packages | pytest, ruff |
| `cli` | argparse-based command-line tools | pytest, ruff |
| `fastapi` | Web APIs and microservices | fastapi, uvicorn, httpx |

---

## CLI Reference

### `workbench --version`
```bash
$ workbench --version
workbench 0.1.0
```

### `workbench list`
```bash
$ workbench list
Available templates:
  cli
  fastapi
  library
  python
```

### `workbench info &lt;template&gt;`
```bash
$ workbench info cli
Template: cli
Files: 8
  .github/workflows/test.yml
  .gitignore
  README.md
  pyproject.toml
  src/my_cli/__init__.py
  src/my_cli/cli.py
  tests/__init__.py
  tests/test_cli.py
```

### `workbench init &lt;template&gt; &lt;name&gt; [options]`

**Basic usage:**
```bash
$ workbench init cli todo-cli
Created cli project 'todo-cli' at /home/nick/Code/todo-cli
```

**Custom output directory:**
```bash
$ workbench init library string-utils --output ~/Code/libs
Created library project 'string-utils' at /home/nick/Code/libs/string-utils
```

**Dry run (preview only):**
```bash
$ workbench init fastapi metrics-api --dry-run
Would create fastapi project 'metrics-api' at /home/nick/Code/metrics-api
  /home/nick/Code/metrics-api/.github/workflows/test.yml
  /home/nick/Code/metrics-api/.gitignore
  /home/nick/Code/metrics-api/README.md
  ...
```

**With GitHub repo creation:**
```bash
$ workbench init python data-pipeline --github
Created python project 'data-pipeline' at /home/nick/Code/data-pipeline
GitHub repo created (if gh is authenticated)
```

---

## Usage Examples

### Building a reusable library

```bash
workbench init library text-stats --output ~/Code/
cd ~/Code/text-stats
uv pip install -e ".[dev]"
# ... implement your features ...
uv run pytest tests/ -v
```

### Starting a web service

```bash
workbench init fastapi weather-api --output ~/Code/
cd ~/Code/weather-api
uv pip install -e ".[dev]"
uv run uvicorn weather_api.main:app --reload
# In another terminal:
# curl http://localhost:8000/health
```

### Team standardization

```bash
# Put this in a team onboarding script
workbench init cli deploy-tool --output /tmp/preview --dry-run
# Review the output, then:
workbench init cli deploy-tool --github
```

---

## Development

```bash
# Run the test suite
uv run pytest tests/ -v

# All tests must pass before committing
uv run pytest tests/ -q
```

### Project Structure

```
workbench/
├── src/
│   └── workbench/
│       ├── __init__.py      # Version
│       ├── cli.py           # argparse entrypoint
│       └── scaffold.py      # Template discovery + project generation
├── src/workbench/templates/
│   ├── cli/                 # CLI tool template
│   ├── fastapi/             # FastAPI service template
│   ├── library/             # Reusable package template
│   └── python/              # Bare-bones Python template
├── tests/
│   ├── test_cli.py          # CLI behavior tests
│   └── test_scaffold.py     # Template generation tests
└── pyproject.toml
```

---

## Changelog

| Date | Commit | Change |
|------|--------|--------|
| 2026-04-24 | `ce78d10` | **feat:** Add `fastapi` template with uvicorn, health endpoint, and TestClient tests |
| 2026-04-24 | `3a5fe70` | **feat:** Inject GitHub Actions CI workflow into all templates |
| 2026-04-24 | `c92f257` | **feat:** Add `--output/-o` flag for custom target directory |
| 2026-04-24 | `34b3e53` | **feat:** Add `--dry-run` flag to preview init without writing files |
| 2026-04-24 | `15bc479` | **feat:** Add `workbench info` command for template inspection |
| 2026-04-24 | `84db099` | **feat:** Add `workbench list` command for dynamic template discovery |
| 2026-04-24 | `da9f5f4` | **refactor:** Use monkeypatch for CLI test isolation |
| 2026-04-23 | `b3938b0` | **refactor:** CLI template tests use monkeypatch for isolation |
| 2026-04-23 | `b063834` | **fix:** Add pytest pythonpath for src-layout imports |
| 2026-04-23 | `227f188` | **feat:** Add `cli` template |
| 2026-04-23 | `fdcd74a` | **feat:** Add `library` template |
| 2026-04-23 | `79d7145` | **docs:** Add README with install and usage instructions |
| 2026-04-23 | `df4f87f` | **feat:** Add `--github` flag for auto repo creation |
| 2026-04-23 | `199ee81` | **feat:** Error handling for unknown templates and existing dirs |
| 2026-04-23 | `9d231d1` | **feat:** Run `git init` in scaffolded projects |
| 2026-04-23 | `fb15fb2` | **feat:** Implement `workbench init python &lt;name&gt;` |

---

## Feedback

This is a personal learning project. If something is broken, unclear, or missing — open an issue or PR. Your feedback shapes the next iteration.
