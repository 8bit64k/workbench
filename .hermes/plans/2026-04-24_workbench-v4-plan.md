# workbench v4 Plan — Configuration & Personalization

**Date:** 2026-04-24  
**Theme:** Make `workbench` remember your preferences so every `init` is pre-personalized.

---

## Iteration 1: Global Config File (`~/.config/workbench/config.toml`)

**Goal:** Load and save a TOML config file at `~/.config/workbench/config.toml` (XDG compliant, falls back to `~/.workbench/config.toml` on non-XDG systems).

**Fields:**
- `author` (str) — default author name for `pyproject.toml`
- `email` (str) — default author email
- `license` (str) — default SPDX license identifier (e.g., "MIT", "Apache-2.0")
- `default_output_format` (str) — "ansi", "plain", or "json"
- `default_template_dir` (str | null) — persistent custom template directory

**Implementation:**
- New module: `src/workbench/config.py`
- `load_config() -> dict` — returns merged dict with defaults
- `save_config(config: dict)` — atomically writes TOML
- `get_config_value(key: str) -> Any` — convenience accessor
- CLI reads config on startup and passes values to `init_project()`

**Tests:** 3 tests — default config, custom config read, config save roundtrip.

---

## Iteration 2: `workbench config` Command

**Goal:** Mimic `git config`. Let users get/set/list config values without hand-editing TOML.

**Commands:**
- `workbench config set <key> <value>` — set a value
- `workbench config get <key>` — get a value (exit 1 if unset)
- `workbench config list` — dump all key=value pairs
- `workbench config unset <key>` — remove a key

**Example:**
```bash
workbench config set author "8bit64k"
workbench config set email "8bit64k@example.com"
workbench config set license "MIT"
workbench config list
```

**Integration:** After `init`, if config has `author`/`email`, those are injected into `pyproject.toml` and any `README.md.j2` that references them.

**Tests:** 5 tests — set, get, list, unset, unknown key.

---

## Iteration 3: `.env` File Support in Generated Projects

**Goal:** Add `--env` flag to `init` (default: False). When set, include:
- `.env` file (gitignored by default)
- `.env.example` file
- `python-dotenv` in dev dependencies
- `src/<project>/config.py` with `pydantic-settings` or `os.getenv` loader (for fastapi/cli templates)

**Rationale:** CLIG deferred item #7 was about `.env`/configuration support for `workbench` itself. This iteration provides `.env` scaffolding for the *generated projects* instead, which is more universally useful.

**Tests:** 2 tests — `--env` creates .env files, default init does not.

---

## Iteration 4: Template Inheritance / Shared Base Skeleton

**Goal:** Stop duplicating Makefile, CI, pre-commit across 4 templates. Extract a `base/` template that other templates inherit from.

**Mechanics:**
- `templates/base/` — shared files: `Makefile`, `.pre-commit-config.yaml`, `.github/workflows/test.yml`, `README.md.j2` (generic), `LICENSE.j2`
- Each specific template (`python/`, `cli/`, etc.) only contains its delta: `pyproject.toml.j2`, `src/...`, `tests/...`
- `init_project()` merges base + template: copies base first, then overlays template files (template wins on conflict)
- `get_template_info()` shows merged file list
- `validate_template()` validates both base and overlay

**Benefits:**
- Adding a new template = 3-4 files instead of 15
- Updating CI or Makefile = 1 location

**Tests:** 3 tests — base files present, template overrides base, validate works with inheritance.

---

## Iteration 5: Shell Completion Generation

**Goal:** `workbench --generate-completion bash|zsh|fish` prints a completion script to stdout.

**Implementation:**
- Use `argparse`’s built-in completion support or hand-roll simple completions since our CLI is straightforward.
- CLIG recommends completion generation, not shipping static completion files.

**Tests:** 2 tests — bash completion contains known subcommands, zsh completion is non-empty.

---

## Iteration 6: Self-Update / Version Check

**Goal:** `workbench --version` (or a new `--check-update`) queries PyPI and prints a non-blocking stderr notice if a newer version is available.

**Implementation:**
- `urllib.request` to `https://pypi.org/pypi/workbench/json` (or the actual package name)
- Cache last-check timestamp in config to avoid hammering PyPI
- `--check-update` flag for explicit check
- Non-blocking, silent on network failure

**Tests:** 2 tests — mock PyPI response shows update, network failure is silent.

---

## Iteration 7: Post-Init Hooks

**Goal:** Allow a `post-init.sh` or `post-init.py` inside a template directory that runs after scaffolding completes (but before git init / GitHub push).

**Mechanics:**
- After file copy/render, check for `post-init.sh` or `post-init.py` in template dir
- If present, run it with `target` as working directory
- Pass env vars: `WORKBENCH_PROJECT_NAME`, `WORKBENCH_PROJECT_PATH`
- Only runs if not `--dry-run`
- `--no-hooks` flag to skip

**Use cases:**
- Run `chmod +x` on scripts
- Generate additional derived files
- Custom git initialization logic

**Tests:** 2 tests — hook runs, `--no-hooks` skips it.

---

## Iteration 8: `workbench upgrade <path>`

**Goal:** Detect an existing project and selectively re-apply template files (CI, Makefile, pre-commit) without overwriting user code.

**Mechanics:**
- `workbench upgrade <path> --template <name>`
- Only copies files from `base/` + template that are "safe" — i.e., files we consider "infrastructure" (Makefile, CI, pre-commit, .gitignore)
- Never overwrites `src/`, `tests/`, `README.md` unless `--force`
- Shows diff preview (like `--dry-run`) by default; requires `--apply` to actually write

**Tests:** 3 tests — dry-run preview, apply works, force overwrites user files.

---

## Final: Full Test Suite, README Update, Push

- Run full test suite (target: 50+ tests)
- Update README with all v4 features
- Update CHANGELOG
- Commit as `feat: v4 — config, template inheritance, completions, hooks, upgrade`
- Push to origin/master

---

## Notes
- All paths in docs: `/home/8bit64k/...` not `~` or `/home/nick/`
- TDD: write test first, watch it fail, implement, watch it pass
- Atomic commits: one per iteration minimum
- Backward compatibility: v3 commands must work identically without config file present
