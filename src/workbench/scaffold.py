from pathlib import Path
import shutil
import subprocess
import jinja2

TEMPLATE_DIR = Path(__file__).parent / "templates"


def _resolve_dir(template_dir: Path | None) -> Path:
    return template_dir if template_dir is not None else TEMPLATE_DIR


def get_templates(template_dir: Path | None = None) -> list[str]:
    """Return a sorted list of available template names."""
    dir_ = _resolve_dir(template_dir)
    return sorted(
        p.name for p in dir_.iterdir() if p.is_dir() and not p.name.startswith(".")
    )


def get_template_info(template_name: str, template_dir: Path | None = None) -> dict:
    """Return metadata about a template: name, files, and variables."""
    dir_ = _resolve_dir(template_dir)
    template_path = dir_ / template_name
    if not template_path.exists():
        raise ValueError(f"Template '{template_name}' not found")

    files = []
    for src in template_path.rglob("*"):
        if src.is_file():
            rel = src.relative_to(template_path)
            files.append(str(rel))

    return {
        "name": template_name,
        "files": sorted(files),
    }


def validate_template(template_name: str, template_dir: Path | None = None) -> list[str]:
    """Validate a template for structural soundness. Returns list of error messages."""
    dir_ = _resolve_dir(template_dir)
    template_path = dir_ / template_name
    errors: list[str] = []

    if not template_path.exists():
        errors.append(f"Template directory '{template_name}' not found")
        return errors

    if not (template_path / "pyproject.toml.j2").exists():
        errors.append("Missing required file: pyproject.toml.j2")

    env = jinja2.Environment()
    for src in template_path.rglob("*.j2"):
        try:
            content = src.read_text()
            tpl = env.from_string(content)
            # Try rendering with dummy values
            tpl.render(project_name="test_project", project_description="Test.")
        except jinja2.TemplateSyntaxError as exc:
            rel = src.relative_to(template_path)
            errors.append(f"Jinja2 syntax error in {rel}: {exc.message}")
        except jinja2.UndefinedError as exc:
            rel = src.relative_to(template_path)
            errors.append(f"Undefined variable in {rel}: {exc}")

    return errors


def init_project(template_name: str, project_name: str, target: Path, github: bool = False, project_description: str | None = None, dry_run: bool = False, force: bool = False, template_dir: Path | None = None) -> list[str]:
    dir_ = _resolve_dir(template_dir)
    template_path = dir_ / template_name
    if not template_path.exists():
        raise ValueError(f"Template '{template_name}' not found")

    if not dry_run:
        if target.exists():
            # Allow empty dirs (just .git or nothing) without force
            existing_files = [f for f in target.iterdir() if f.name != ".git"]
            if existing_files and not force:
                raise FileExistsError(
                    f"Target directory '{target}' already exists and is not empty. "
                    f"Use --force to scaffold into it anyway."
                )
        else:
            target.mkdir(parents=True, exist_ok=False)
    snake_name = project_name.replace("-", "_").lower()

    env = jinja2.Environment()
    actions: list[str] = []

    for src in template_path.rglob("*"):
        rel = src.relative_to(template_path)
        dst = target / rel

        # Expand {{project_name}} in directory names
        dst_str = str(dst).replace("{{project_name}}", snake_name)
        dst = Path(dst_str)

        if src.is_dir():
            if not dry_run:
                dst.mkdir(parents=True, exist_ok=True)
            continue

        if src.suffix == ".j2":
            content = src.read_text()
            template = env.from_string(content)
            rendered = template.render(
                project_name=snake_name,
                project_description=project_description or "A Python project.",
            )
            dst = dst.with_suffix("")  # strip .j2
            if not dry_run:
                dst.write_text(rendered)
            actions.append(str(dst.relative_to(target.parent) if dry_run else dst))
        else:
            if not dry_run:
                shutil.copy2(src, dst)
            actions.append(str(dst.relative_to(target.parent) if dry_run else dst))

    if not dry_run:
        subprocess.run(["git", "init"], cwd=target, check=True, capture_output=True)

        if github:
            subprocess.run(
                ["gh", "repo", "create", project_name, "--private", "--source=.", "--push"],
                cwd=target,
                check=False,
                capture_output=True,
            )

    return actions
