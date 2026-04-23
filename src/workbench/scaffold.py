from pathlib import Path
import shutil
import subprocess
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
            rendered = template.render(
                project_name=snake_name,
                project_description="A Python project.",
            )
            dst = dst.with_suffix("")  # strip .j2
            dst.write_text(rendered)
        else:
            shutil.copy2(src, dst)

    subprocess.run(["git", "init"], cwd=target, check=True, capture_output=True)
