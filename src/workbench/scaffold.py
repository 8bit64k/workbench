from pathlib import Path
import os
import shutil
import subprocess
import sys
import jinja2

TEMPLATE_DIR = Path(__file__).parent / "templates"


def _resolve_dir(template_dir: Path | None) -> Path:
    return template_dir if template_dir is not None else TEMPLATE_DIR


def get_templates(template_dir: Path | None = None) -> list[str]:
    """Return a sorted list of available template names."""
    dir_ = _resolve_dir(template_dir)
    return sorted(
        p.name for p in dir_.iterdir() if p.is_dir() and not p.name.startswith(".") and p.name != "base"
    )


def _list_template_files(template_path: Path) -> list[str]:
    files = []
    for src in template_path.rglob("*"):
        if src.is_file():
            files.append(str(src.relative_to(template_path)))
    return files


def get_template_info(template_name: str, template_dir: Path | None = None) -> dict:
    """Return metadata about a template: name, files, and variables."""
    dir_ = _resolve_dir(template_dir)
    template_path = dir_ / template_name
    if not template_path.exists():
        raise ValueError(f"Template '{template_name}' not found")

    files = set()
    base_path = dir_ / "base"
    if base_path.exists():
        files.update(_list_template_files(base_path))
    files.update(_list_template_files(template_path))

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
    j2_files = list(template_path.rglob("*.j2"))
    base_path = dir_ / "base"
    if base_path.exists():
        j2_files.extend(base_path.rglob("*.j2"))

    for src in j2_files:
        try:
            content = src.read_text()
            tpl = env.from_string(content)
            # Try rendering with dummy values
            tpl.render(project_name="test_project", project_description="Test.")
        except jinja2.TemplateSyntaxError as exc:
            rel = src.relative_to(template_path if src.is_relative_to(template_path) else base_path)
            errors.append(f"Jinja2 syntax error in {rel}: {exc.message}")
        except jinja2.UndefinedError as exc:
            rel = src.relative_to(template_path if src.is_relative_to(template_path) else base_path)
            errors.append(f"Undefined variable in {rel}: {exc}")

    return errors


def _copy_template_tree(
    source: Path,
    target: Path,
    env: jinja2.Environment,
    snake_name: str,
    project_description: str,
    author: str | None,
    email: str | None,
    license: str | None,
    dry_run: bool,
    actions: list[str],
) -> None:
    for src in source.rglob("*"):
        rel = src.relative_to(source)
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
                author=author,
                email=email,
                license=license or "MIT",
            )
            dst = dst.with_suffix("")  # strip .j2
            if not dry_run:
                dst.write_text(rendered)
            actions.append(str(dst.relative_to(target.parent) if dry_run else dst))
        else:
            if not dry_run:
                shutil.copy2(src, dst)
            actions.append(str(dst.relative_to(target.parent) if dry_run else dst))


def init_project(template_name: str, project_name: str, target: Path, github: bool = False, project_description: str | None = None, dry_run: bool = False, force: bool = False, template_dir: Path | None = None, author: str | None = None, email: str | None = None, license: str | None = None, no_hooks: bool = False) -> list[str]:
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

    base_path = dir_ / "base"
    if base_path.exists():
        _copy_template_tree(
            base_path, target, env, snake_name, project_description,
            author, email, license, dry_run, actions,
        )

    _copy_template_tree(
        template_path, target, env, snake_name, project_description,
        author, email, license, dry_run, actions,
    )

    if not dry_run:
        # Run post-init hooks if present
        if not no_hooks:
            for hook_name in ("post-init.sh", "post-init.py"):
                hook = template_path / hook_name
                if hook.exists():
                    env = os.environ.copy()
                    env["WORKBENCH_PROJECT_NAME"] = project_name
                    env["WORKBENCH_PROJECT_PATH"] = str(target.resolve())
                    if hook_name.endswith(".sh"):
                        subprocess.run(["sh", str(hook)], cwd=target, env=env, check=False)
                    else:
                        subprocess.run([sys.executable, str(hook)], cwd=target, env=env, check=False)
                    break  # Only run one hook

        subprocess.run(["git", "init"], cwd=target, check=True, capture_output=True)

        if github:
            subprocess.run(
                ["gh", "repo", "create", project_name, "--private", "--source=.", "--push"],
                cwd=target,
                check=False,
                capture_output=True,
            )

    return actions
