# workbench

> A minimal, opinionated CLI scaffolding tool for Python projects. No interactive prompts, no bloat — just fast, repeatable project generation.

## Philosophy

`workbench` exists because scaffolding should be **deterministic and fast**. You know what you want to build; workbench gives you a clean starting point in under a second. Every generated project comes with:

- **Strict TDD-ready test structure** (pytest, monkeypatch isolation patterns)
- **Modern packaging** (hatchling, `pyproject.toml`, src-layout)
- **CI from day one** (GitHub Actions with uv, Python 3.12 + 3.13 matrix)
- **Task automation** (Makefile with `test`, `install`, `clean` targets)
- **Code quality hooks** (pre-commit with ruff and standard checks where applicable)
- **Clean git init** (no commits, just a ready repo)
- **Environment variable scaffolding** (`.env.example` + `python-dotenv` pre-configured)

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

# Same as above, short flag
workbench init python my-project -n

# Output as JSON for piping to other tools
workbench list --json | jq '.[]'

# Plain output for grep/awk
workbench list --plain | grep fastapi

# Scaffold and create a private GitHub repo (requires gh CLI auth)
workbench init python my-project --github

# Validate a custom template for structural and Jinja2 correctness
workbench validate my-template

# Generate shell completions
workbench --generate-completion bash > /etc/bash_completion.d/workbench
```

---

## Feature List

### Discovery & Inspection
- **`workbench list`** — Dynamically discovers available templates from the templates directory. New templates automatically appear here.
- **`workbench info <template>`** — Shows template metadata: name, file count, and complete file tree. No surprises.
- **`workbench validate <template>`** — Validates a template for structural soundness and Jinja2 syntax errors before you use it.

### Scaffolding
- **`workbench init <template> <name>`** — Generates a complete project from a template.
- **`--output <path>` / `-o <path>`** — Scaffold into a custom directory instead of the current working directory.
- **`--json`** — Output as JSON for piping, scripting, and integration with other tools.
- **`--plain`** — Output plain line-based text (no headers or indentation) for use with grep, awk, and other UNIX tools.
- **`--no-color`** — Disable colored output. Also respects `NO_COLOR` and `TERM=dumb`.
- **`--dry-run` / `-n`** — Preview every file that would be created without writing anything to disk. Essential for scripting and sanity-checking.
- **`--github`** — Auto-creates a private GitHub repo and pushes the initial commit (requires [gh](https://cli.github.com/) authentication).
- **`--force`** — Scaffold into an existing non-empty directory. Use with caution.
- **`--verbose` / `-v`** — Show debug output (template name, target path, file count).
- **`--quiet` / `-q`** — Suppress non-error output. Useful in CI pipelines.
- **`--no-hooks`** — Skip post-init hooks (see Post-Init Hooks below).

### Configuration
- **Global config file** — `~/.config/workbench/config.toml` stores your defaults.
- **`workbench config set <key> <value>`** — Persist a default value (e.g., `author`, `email`, `license`).
- **`workbench config get <key>`** — Retrieve a config value.
- **`workbench config list`** — Show all configured values.
- **`workbench config unset <key>`** — Remove a config key.

Config values are automatically injected into every new project:

| Config key | Affects |
|------------|---------|
| `author` | `pyproject.toml` authors |
| `email` | `pyproject.toml` author email |
| `license` | `pyproject.toml` license (default: MIT) |
| `default_template_dir` | Fallback template directory |

### Custom Templates
- **`--template-dir <path>`** — Use an alternative template directory instead of the built-ins.
- **Template inheritance** — Create a `base/` template with shared files (Makefile, CI, pre-commit, .gitignore). Specific templates override base files.
- **Post-init hooks** — Templates can include `post-init.sh` or `post-init.py` that runs automatically after scaffolding (e.g., initial dependency install, code generation).

### Template System
- **Jinja2-powered rendering** — Template files use `.j2` extension and render `{{project_name}}`, `{{project_description}}`, and other variables.
- **Directory name expansion** — `{{project_name}}` in directory paths is automatically converted to `snake_case`.
- **Dynamic template discovery** — Adding a new template directory makes it immediately available — no code changes required.
- **Validation** — `workbench validate` catches syntax errors and missing required files (`pyproject.toml.j2`) before they break a scaffold.

### Human-First Design
- **Concise help for bare subcommands** — Running `workbench init` (with no args) shows a short example and a pointer to `--help`, not a raw argparse error.
- **"Get started" suggestions after `init`** — After scaffolding, workbench prints the exact commands to install dependencies and run tests in the new project.
- **Typo suggestions** — If you mistype a template name, workbench suggests the closest match (e.g., "Did you mean 'python'?").
- **Actionable error messages** — When a directory already exists, the error explicitly suggests `--dry-run` / `-n` to preview and `--force` to overwrite.
- **Shell completion** — Native completion scripts for bash, zsh, and fish via `--generate-completion`.
- **Version check** — `workbench --check-update` queries PyPI and tells you if a newer version is available.
- **src-layout** for all Python projects
- **pytest** configured with `pythonpath = ["src"]` for clean imports
- **GitHub Actions CI** with `uv` setup and Python version matrix (3.12, 3.13)
- **Makefile** with `test`, `install`, `clean` (and template-specific targets like `lint`, `run`)
- **pre-commit hooks** (ruff, trailing-whitespace, end-of-file-fixer, check-yaml, check-added-large-files)
- **Proper `.gitignore`** (`.venv`, `__pycache__`, `.pyc`)
- **Environment variables** — `.env.example` + `python-dotenv` in dev dependencies
- **Tests that don't suck** — monkeypatch-based CLI isolation, no brittle `sys.argv` mutation

---

## Templates

| Template | Best For | Key Dependencies | Makefile Targets | Pre-commit |
|----------|----------|------------------|------------------|------------|
| `python` | Bare-bones Python scripts | None | `test`, `install`, `clean` | Basic hooks |
| `library` | Reusable PyPI-ready packages | pytest, ruff | `test`, `lint`, `format`, `install`, `clean` | Ruff + basic hooks |
| `cli` | argparse-based command-line tools | pytest, ruff | `test`, `lint`, `format`, `install`, `clean`, `run` | Ruff + basic hooks |
| `fastapi` | Web APIs and microservices | fastapi, uvicorn, httpx | `test`, `install`, `clean`, `run` | Basic hooks |

---

## CLI Reference

### `workbench --version`
```bash
$ workbench --version
workbench 0.1.0
```

### `workbench --check-update`
```bash
$ workbench --check-update
A new version of workbench is available: 0.2.0 (you have 0.1.0)
Run `uv pip install -U workbench` to upgrade.
```

### `workbench --generate-completion <shell>`
```bash
# Bash
$ workbench --generate-completion bash > /etc/bash_completion.d/workbench

# Zsh
$ workbench --generate-completion zsh > /usr/local/share/zsh/site-functions/_workbench

# Fish
$ workbench --generate-completion fish > ~/.config/fish/completions/workbench.fish
```

### `workbench config`
```bash
# Set your defaults once, use them forever
$ workbench config set author "Ada Lovelace"
$ workbench config set email "ada@example.com"
$ workbench config set license "Apache-2.0"

# Check what you've set
$ workbench config get author
Ada Lovelace

# See everything
$ workbench config list
author = "Ada Lovelace"
email = "ada@example.com"
license = "Apache-2.0"

# Remove a key
$ workbench config unset email
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

**With custom template directory:**
```bash
$ workbench --template-dir ~/my-templates list
Available templates:
  internal-api
  data-pipeline
```

### `workbench info <template>`
```bash
$ workbench info cli
Template: cli
Files: 10
  .github/workflows/test.yml
  .gitignore
  Makefile
  README.md
  pyproject.toml
  src/my_cli/__init__.py
  src/my_cli/cli.py
  tests/__init__.py
  tests/test_cli.py
  .pre-commit-config.yaml
```

### `workbench validate <template>`
```bash
$ workbench validate python
Template 'python' is valid.

$ workbench validate broken-template
Template 'broken-template' is invalid:
  - Jinja2 syntax error in pyproject.toml.j2: unexpected 'end of template'
```

### `workbench init <template> <name> [options]`

**Basic usage:**
```bash
$ workbench init cli todo-cli
Created cli project 'todo-cli' at /home/8bit64k/Code/todo-cli
```

**Custom output directory:**
```bash
$ workbench init library string-utils --output ~/Code/libs
Created library project 'string-utils' at /home/8bit64k/Code/libs/string-utils
```

**Dry run (preview only):**
```bash
$ workbench init fastapi metrics-api --dry-run
Would create fastapi project 'metrics-api' at /home/8bit64k/Code/metrics-api
  /home/8bit64k/Code/metrics-api/.github/workflows/test.yml
  /home/8bit64k/Code/metrics-api/.gitignore
  /home/8bit64k/Code/metrics-api/Makefile
  /home/8bit64k/Code/metrics-api/README.md
  ...
```

**With GitHub repo creation:**
```bash
$ workbench init python data-pipeline --github
Created python project 'data-pipeline' at /home/8bit64k/Code/data-pipeline
GitHub repo created (if gh is authenticated)
```

**Force into existing directory:**
```bash
$ workbench init python existing-project --force
Created python project 'existing-project' at /home/8bit64k/Code/existing-project
```

**Skip post-init hooks:**
```bash
$ workbench init cli my-tool --no-hooks
Created cli project 'my-tool' at /home/8bit64k/Code/my-tool
```

**Verbose output:**
```bash
$ workbench init python verbose-proj --verbose
[debug] Using template: python
[debug] Target path: /home/8bit64k/Code/verbose-proj
[debug] Files generated: 9
Created python project 'verbose-proj' at /home/8bit64k/Code/verbose-proj
```

**Custom templates:**
```bash
$ workbench --template-dir ~/my-templates init internal-api billing-api
Created internal-api project 'billing-api' at /home/8bit64k/Code/billing-api
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
make lint
```

### Starting a web service

```bash
workbench init fastapi weather-api --output ~/Code/
cd ~/Code/weather-api
uv pip install -e ".[dev]"
make run
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

### Validating a custom template

```bash
# Before sharing your template with the team
workbench validate my-custom-template
# Fix any errors, then:
workbench --template-dir ~/templates init my-custom-template new-project
```

### Setting up personal defaults

```bash
# One-time setup
workbench config set author "8bit64k"
workbench config set email "8bit64k@example.com"
workbench config set license "MIT"

# From now on, every project is pre-personalized
workbench init python my-script
# pyproject.toml will already have your name, email, and license
```

### Creating a template with a post-init hook

```bash
# In your custom template directory:
mkdir -p ~/templates/custom-cli
cp -r ~/Code/workbench/src/workbench/templates/cli/* ~/templates/custom-cli/

# Add a hook that runs after scaffolding
cat > ~/templates/custom-cli/post-init.sh << 'EOF'
#!/bin/sh
echo "Setting up pre-commit..."
cd "$WORKBENCH_TARGET"
pre-commit install
EOF
chmod +x ~/templates/custom-cli/post-init.sh

# Use it
workbench --template-dir ~/templates init custom-cli my-tool
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
│       ├── config.py        # Global config (TOML, XDG-compliant)
│       └── scaffold.py      # Template discovery + project generation
├── src/workbench/templates/
│   ├── base/                # Shared files (CI, Makefile, pre-commit, .gitignore)
│   ├── cli/                 # CLI tool template
│   ├── fastapi/             # FastAPI service template
│   ├── library/             # Reusable package template
│   └── python/              # Bare-bones Python template
├── tests/
│   ├── test_cli.py          # CLI behavior tests
│   ├── test_config.py       # Config persistence tests
│   └── test_scaffold.py     # Template generation tests
└── pyproject.toml
```

---

## Changelog

| Date | Commit | Change |
|------|--------|--------|
| 2026-04-24 | — | **v4** Add global config (`~/.config/workbench/config.toml`), `workbench config` command, template inheritance with `base/` skeleton, shell completion generation, `--check-update`, post-init hooks, `.env.example` scaffolding |
| 2026-04-24 | — | **v3** Add `-n` short flag for `--dry-run`; `--json`, `--plain`, and `--no-color` flags; concise help for bare subcommands; "Get started" suggestions after `init`; actionable error messages with `--dry-run` / `--force` hints |
| 2026-04-24 | `b08af15` | **feat:** Richer error messages with difflib typo suggestions and empty-dir warnings |
| 2026-04-24 | `6f948f0` | **feat:** Support custom template directories via `--template-dir` |
| 2026-04-24 | `24ed93a` | **feat:** Add `workbench validate` command for template structural and Jinja2 checking |
| 2026-04-24 | `afe1729` | **feat:** Add `--force` flag for scaffolding into existing directories |
| 2026-04-24 | — | **feat:** Add `--verbose` and `--quiet` flags to all CLI commands |
| 2026-04-24 | — | **feat:** Add `Makefile` and `.pre-commit-config.yaml` to all templates |
| 2026-04-24 | — | **feat:** Flesh out `python` template with real `core.py`, ruff, classifiers, MIT license |
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
| 2026-04-23 | `fb15fb2` | **feat:** Implement `workbench init python <name>` |

---

## Feedback

This is a personal learning project. If something is broken, unclear, or missing — open an issue or PR. Your feedback shapes the next iteration.
