# workbench v0 Implementation Plan

> **Status:** v0 COMPLETE — 3 templates working, 7 tests passing, pushed to GitHub.
> **Next focus:** Expand CLI template capabilities.

**Goal:** Build a CLI project scaffolding tool (`workbench`) that generates boilerplate projects from templates. Learn Python packaging, TDD, git workflows, and CLI design by building it.

**Architecture:** Single Python package with a CLI entrypoint. Templates stored as directories in `src/workbench/templates/`. Uses `argparse` for CLI, `jinja2` for template variable substitution, `pytest` for TDD. Installs via `uv pip install -e .` with a `pyproject.toml` script.

**Tech Stack:** Python 3.12+, uv, pytest, jinja2, git, GitHub CLI (gh)

---

## Completed Tasks

### Task 1: Scaffold the `workbench` repo itself ✓
- Created repo structure with src-layout
- `pyproject.toml` with hatchling, pytest dev deps
- `README.md`, `.gitignore`
- Committed: `chore: scaffold workbench repo structure`

### Task 2: Implement `workbench --version` ✓
- argparse with `--version` action
- TDD: wrote failing test first, then implemented
- Committed: `feat: add --version flag`

### Task 3: Implement `workbench init python <name>` ✓
- Jinja2 template rendering
- `scaffold.py` with directory creation and file processing
- Template variable substitution (`{{project_name}}`)
- Committed: `feat: implement workbench init python <name>`

### Task 4: Run `git init` in scaffolded project ✓
- Auto-initializes git repo in generated project
- Committed: `feat: run git init in scaffolded projects`

### Task 5: Error handling and edge cases ✓
- Unknown template → `ValueError`
- Existing target dir → `FileExistsError`
- Committed: `feat: error handling for unknown templates and existing dirs`

### Task 6: GitHub repo creation via `--github` flag ✓
- `--github` triggers `gh repo create --private --source=. --push`
- Mocked in tests with `unittest.mock`
- Committed: `feat: add --github flag for auto repo creation`

### Task 7: Polish and push to GitHub ✓
- README with install/usage/development instructions
- Pushed to `https://github.com/8bit64k/workbench`

### Task 8: Add `library` template ✓
- `workbench init library <name>` — PyPI-ready package
- Classifiers, optional dev deps, `core.py` stub, real tests
- Committed: `feat: add library template for PyPI-ready packages`

### Task 9: Add `cli` template ✓
- `workbench init cli <name>` — argparse-based CLI tool
- Entry point, subcommands, `--version`, capsys tests
- Committed: `feat: add cli template for argparse-based command-line tools`

### Task 10: Fix pytest path resolution ✓
- Added `pythonpath = ["src"]` to `pyproject.toml`
- `uv run pytest` now works cleanly from project root
- Committed: `fix: add pytest pythonpath for src-layout imports`

---

## Current Template Inventory

| Template | Command | Best For |
|----------|---------|----------|
| `python` | `workbench init python <name>` | Bare bones Python project |
| `library` | `workbench init library <name>` | Reusable installable package |
| `cli` | `workbench init cli <name>` | Command-line tools |

---

## CLI Template: Current Features

- `argparse` scaffold with `--version`
- Single subcommand: `hello` with optional `name` argument
- `[project.scripts]` entry point (`pip install` → runnable command)
- `pytest` tests using `capsys` to verify stdout
- `ruff` linting configured

## CLI Template: Current Limitations

1. **No global options.** `--verbose`, `--quiet`, `--config` don't exist. Each subcommand would need to re-declare them.
2. **No config file support.** No pattern for `.toml` or `.yaml` config loading.
3. **No environment variable integration.** No `MYTOOL_FOO` → `--foo` mapping.
4. **Tests mutate `sys.argv`.** This is brittle; if a test fails mid-run, subsequent tests see polluted state.
5. **No logging setup.** Print statements only. No `--verbose` / `--debug` / `--quiet` levels.
6. **No output formatting.** Plain text only — no colors, tables, or progress indicators.
7. **No CI template.** No `.github/workflows/pytest.yml` generated.
8. **No pre-commit hooks.** No `.pre-commit-config.yaml`.
9. **Single subcommand only.** No pattern for adding N subcommands cleanly.
10. **No subcommand groups.** `my-tool db migrate` vs `my-tool db rollback` not demonstrated.
11. **No input validation.** No type coercion beyond argparse basics.
12. **No error handling pattern.** No custom exception classes or clean exit codes.

---

## Upcoming: CLI Template Expansion

### Option A: Rich CLI (recommended next)
Add `rich` for colors, tables, progress bars, and pretty tracebacks. Update template to include:
- `rich.console.Console` for output
- `rich.traceback.install()` for pretty errors
- `rich.progress` for long-running operations
- Colored `--help` output

### Option B: Config + Environment Support
- Add `pydantic-settings` or plain `os.environ` mapping
- Default config file path: `~/.config/{project_name}/config.toml`
- `--config` override flag
- `.env` file loading with `python-dotenv`

### Option C: Multiple Subcommands Pattern
- Refactor `cli.py` to use a plugin-like pattern
- `src/{name}/commands/` directory with one file per subcommand
- Auto-discovery instead of one giant `cli.py`

### Option D: Test Hygiene ✓ COMPLETED
- Replaced `sys.argv` mutation with `pytest`'s `monkeypatch` fixture
- Added `test_bare_invocation_prints_help` for no-args path
- Added `test_unknown_subcommand_exits_with_error` for invalid input
- Generated CLI projects now have 5 passing tests with clean isolation

### Option E: CI/DevEx (QUEUED for next session)
- `.github/workflows/test.yml` template
- `.pre-commit-config.yaml` with ruff + trailing-whitespace
- `Makefile` or `justfile` with common commands

---

## Verification Checklist (v0)

- [x] `workbench --version` prints version
- [x] `workbench init python test-proj` creates a valid Python project
- [x] `workbench init library test-lib` creates a valid library
- [x] `workbench init cli test-tool` creates a valid CLI tool
- [x] Generated projects pass their own `pytest` run
- [x] Generated projects are valid git repos
- [x] Unknown template raises clear error
- [x] Existing dir raises clear error
- [x] All tests pass: `uv run pytest`
- [x] Repo is on GitHub with clean commit history

---

## Open Questions

1. **More templates?** `fastapi`, `data-science`, `rust`, `node`? (defer until CLI is mature)
2. **Template customization?** Interactive prompts for author, license, description? (v1 consideration)
3. **Remote templates?** Fetch templates from GitHub repos instead of bundling? (v1)
4. **Template versioning?** Pin to specific template versions? (v1)
