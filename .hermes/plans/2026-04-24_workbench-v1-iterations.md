# workbench v1 — Continuous Improvement Plan

> **Status:** IN PROGRESS — 3-hour continuous iteration session
> **Session:** 2026-04-24

**Goal:** Improve `workbench` through 8 focused iterations, each adding or refining a feature. All changes pushed to GitHub for remote review.

**Architecture:** Single Python package with CLI entrypoint. Templates stored as directories in `src/workbench/templates/`. Uses `argparse` for CLI, `jinja2` for template rendering, `pytest` for TDD.

**Tech Stack:** Python 3.12+, uv, pytest, jinja2, git

---

## Iteration Roadmap

| # | Feature | Description | Est. Time |
|---|---------|-------------|-----------|
| 1 | **Fix test hygiene** | Replace `sys.argv` mutation in `test_cli.py` with `monkeypatch` | 10 min |
| 2 | **`workbench list`** | Show all available templates with descriptions | 20 min |
| 3 | **`workbench info <template>`** | Inspect a template: files, variables, description | 25 min |
| 4 | **`--dry-run` flag** | Preview what `init` would create without writing files | 20 min |
| 5 | **`--output/-o` flag** | Specify custom target directory for `init` | 15 min |
| 6 | **CI template injection** | Add `.github/workflows/test.yml` to python, library, cli templates | 25 min |
| 7 | **`fastapi` template** | New template for FastAPI web services | 30 min |
| 8 | **Comprehensive README** | Feature list, use cases, architecture diagram, changelog | 30 min |

---

## Principles

- **TDD for every change:** Write failing test first, watch it fail, implement minimal code, verify pass.
- **Frequent commits:** One commit per iteration with conventional commit messages.
- **Docs follow code:** README updated in iteration 8 to reflect all new features.
- **No breaking changes:** Existing `workbench init <template> <name>` continues to work.

---

## Verification Checklist

- [ ] All 7 existing tests still pass
- [ ] New tests added for each iteration
- [ ] Full test suite passes: `uv run pytest`
- [ ] Each iteration committed and pushed
- [ ] README documents all features with examples
