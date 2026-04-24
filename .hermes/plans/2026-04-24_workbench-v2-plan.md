# workbench v2 — Next Iteration Bucket

> **Status:** PLANNED — Awaiting review before execution
> **Planned session:** Follow-up to 2026-04-24 v1 session

**Goal:** Harden generated projects with standard developer-experience tooling, improve workbench CLI polish, and expand the template system.

**Principles:** Same as v1 — TDD for every change, frequent commits, docs follow code, no breaking changes.

---

## Candidate Iterations (ranked by value)

### 1. `Makefile` in All Templates
**Why:** Every Python project needs a standard set of commands. Typing `make test` is faster and more discoverable than `uv run pytest tests/ -v`.

**What:** Add a `Makefile` to `python`, `library`, `cli`, and `fastapi` templates with targets:
- `make test` → `uv run pytest tests/ -v`
- `make lint` → `uv run ruff check src/ tests/` (where applicable)
- `make format` → `uv run ruff format src/ tests/` (where applicable)
- `make install` → `uv pip install -e ".[dev]"`
- `make clean` → remove `__pycache__`, `.pytest_cache`, `.ruff_cache`
- `make run` → template-specific (e.g. `uvicorn` for fastapi, bare run for cli)

**Tests:** Verify `Makefile` exists and contains expected targets in each template test.

---

### 2. `.pre-commit-config.yaml` in All Templates
**Why:** Catches formatting and linting issues before they hit CI. Standard in modern Python projects.

**What:** Add `.pre-commit-config.yaml` to all templates with:
- `ruff` check and format
- `trailing-whitespace` fixer
- `end-of-file-fixer`
- `check-yaml`
- `check-added-large-files`

Include a note in README about `uv run pre-commit install`.

**Tests:** Verify config exists and contains ruff + basic hooks.

---

### 3. Flesh Out the `python` Template
**Why:** Currently it's embarrassingly bare — just `__init__.py` and a `test_stub.py` that asserts `True`. It should be a real starting point.

**What:** Give it the same baseline as `library` and `cli`:
- A `core.py` with a trivial but real function (e.g., `def greet(name: str) -> str`)
- Real tests using that function
- `ruff` dev dependency and config in `pyproject.toml`
- Classifiers and MIT license block
- README with usage example

Keep it simpler than `library` (no `[project.optional-dependencies]` complexity), but not a hollow shell.

**Tests:** Update `test_init_python_creates_structure` to verify `core.py`, real tests, and ruff config exist.

---

### 4. `--verbose` / `--quiet` on workbench CLI
**Why:** Right now `workbench` is silent except for success messages. When something goes wrong, there's no context. When scripting, you want less noise.

**What:** Add global parser arguments:
- `--verbose` / `-v` — print debug info (template path, file count, git init output)
- `--quiet` / `-q` — suppress all non-error output

Pipe these through to `init_project()` so it can log what it's doing. Use Python's `logging` module with a simple setup.

**Tests:** Verify `--verbose` produces more output. Verify `--quiet` suppresses `Created ...` message.

---

### 5. `--force` Flag for `init`
**Why:** Sometimes you want to re-scaffold over a directory that exists (e.g., you initialized a repo on GitHub first, cloned it empty, now want to populate it).

**What:** Add `--force` to `init`. When present:
- Skip `FileExistsError` if target exists
- If target is non-empty, warn (or error unless `--force` is really force)
- Actually, better behavior: if target exists and is empty (just `.git` or nothing), proceed. If non-empty, require `--force` to overwrite.

**Tests:**
- `test_init_into_empty_existing_dir_succeeds`
- `test_init_into_nonempty_dir_without_force_raises`
- `test_init_into_nonempty_dir_with_force_succeeds`

---

### 6. `workbench validate <template>`
**Why:** Before shipping a new template, you want to verify it's structurally sound — all `.j2` files are valid Jinja2, all referenced variables are defined, etc.

**What:** New command that checks:
- Template directory exists
- No orphaned `.j2` files with syntax errors
- All `{{variables}}` used in templates are standard (project_name, project_description)
- At minimum, `pyproject.toml.j2` exists
- Can render successfully with dummy values

**Tests:** `test_validate_passes_for_good_template`, `test_validate_fails_for_broken_jinja`.

---

### 7. Custom Template Directory (`--templates`)
**Why:** Users will want their own templates without forking workbench. This is the path to a plugin ecosystem.

**What:** Add `--templates <path>` global option or env var `WORKBENCH_TEMPLATES`. `get_templates()` merges built-in + custom directories. Custom templates shadow built-ins by name.

**Tests:** `test_custom_template_is_discovered`, `test_custom_template_shadows_builtin`.

---

### 8. Richer Error Messages and Exit Codes
**Why:** Currently workbench just re-raises exceptions or lets argparse print generic errors. A polished CLI explains what went wrong and how to fix it.

**What:**
- `ValueError: Template 'foo' not found` → suggest running `workbench list`
- `FileExistsError` → suggest `--force` or choosing a different name
- `subprocess.CalledProcessError` on `git init` → explain git is required
- Standardize exit codes: 0 = success, 1 = user error (bad args, missing template), 2 = system error (git missing, permission denied), 130 = interrupted

**Tests:** Verify error messages contain helpful suggestions. Verify correct exit codes.

---

## Deferred to v3 (bigger architectural work)

| Feature | Why Deferred |
|---------|-------------|
| Remote templates (fetch from GitHub repos) | Requires caching, versioning, network error handling — large surface area |
| Interactive prompts (author, license, description) | Changes the CLI from non-interactive to potentially interactive — breaks scripting |
| Config file (`~/.config/workbench/config.toml`) | Needs config parsing, schema validation, migration story |
| Template versioning / pinning | Needs semver resolution, lock files |
| Plugin system for custom renderers | Over-engineering at current scale |

---

## Execution Order Recommendation

1. → **Makefile** (immediate DX win, easy)
2. → **Flesh out python template** (fixes an embarrassment, easy)
3. → **Pre-commit hooks** (standard tooling, easy)
4. → **Richer error messages** (polish, medium)
5. → **--verbose / --quiet** (CLI maturity, medium)
6. → **--force** (unblocks real workflows, medium)
7. → **validate command** (template author DX, medium)
8. → **Custom template directory** (extensibility, medium-hard)

---

## Success Criteria for v2

- [ ] Every generated project has `make test`, `make lint`, `make install`
- [ ] Every generated project has `.pre-commit-config.yaml`
- [ ] `python` template is no longer a hollow shell
- [ ] `workbench` CLI has `--verbose` and `--quiet`
- [ ] `workbench init` has `--force` for overwriting
- [ ] `workbench validate <template>` exists and catches broken templates
- [ ] Custom templates can live outside the workbench package
- [ ] Error messages tell you what to do next, not just what broke
- [ ] All tests pass, README updated, commits clean
