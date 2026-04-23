# workbench

CLI project scaffolding tool. Generates boilerplate projects from templates with git init and optional GitHub repo creation.

## Install

```bash
cd ~/Code/workbench
uv pip install -e ".[dev]"
```

## Usage

```bash
# Scaffold a Python project
workbench init python my-project

# Scaffold + create private GitHub repo (requires gh CLI auth)
workbench init python my-project --github

# Show version
workbench --version
```

## Development

```bash
uv run pytest tests/ -v
```

## Feedback
