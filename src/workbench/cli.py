import argparse
import os
import sys
from pathlib import Path
from workbench import __version__
from workbench.scaffold import init_project, get_templates, get_template_info


def _template_dir_from_args(args) -> Path | None:
    if args.template_dir:
        return Path(args.template_dir)
    env = os.environ.get("WORKBENCH_TEMPLATE_DIR")
    if env:
        return Path(env)
    return None


def main():
    parser = argparse.ArgumentParser(prog="workbench")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show debug output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress non-error output")
    parser.add_argument("--template-dir", type=str, default=None, help="Custom template directory (or set WORKBENCH_TEMPLATE_DIR)")
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("--verbose", "-v", action="store_true", help="Show debug output")
    init_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress non-error output")
    init_parser.add_argument("template")
    init_parser.add_argument("name")
    init_parser.add_argument("--github", action="store_true", help="Create a private GitHub repo and push")
    init_parser.add_argument("--dry-run", action="store_true", help="Show what would be created without writing files")
    init_parser.add_argument("--output", "-o", type=str, default=".", help="Target directory (default: current directory)")
    init_parser.add_argument("--force", action="store_true", help="Scaffold into an existing non-empty directory")

    list_parser = subparsers.add_parser("list", help="List available templates")
    list_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress non-error output")

    info_parser = subparsers.add_parser("info", help="Show template details")
    info_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress non-error output")
    info_parser.add_argument("template")

    validate_parser = subparsers.add_parser("validate", help="Validate a template")
    validate_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress non-error output")
    validate_parser.add_argument("template")

    args = parser.parse_args()

    custom_dir = _template_dir_from_args(args)

    if args.command == "init":
        if args.template not in get_templates(custom_dir):
            print(f"Error: Unknown template '{args.template}'.", file=sys.stderr)
            sys.exit(1)
        descriptions = {
            "python": "A Python project.",
            "library": "A reusable Python library package.",
            "cli": "A command-line interface tool.",
            "fastapi": "A FastAPI web service.",
        }
        target = Path(args.output).resolve() / args.name
        if args.verbose:
            print(f"[debug] Using template: {args.template}")
            print(f"[debug] Target path: {target}")
        actions = init_project(
            args.template,
            args.name,
            target,
            github=args.github,
            project_description=descriptions.get(args.template, "A Python project."),
            dry_run=args.dry_run,
            force=args.force,
            template_dir=custom_dir,
        )
        if args.verbose:
            print(f"[debug] Files generated: {len(actions)}")
        if not args.quiet:
            if args.dry_run:
                print(f"Would create {args.template} project '{args.name}' at {target}")
                for action in actions:
                    print(f"  {action}")
            else:
                print(f"Created {args.template} project '{args.name}' at {target}")
                if args.github:
                    print("GitHub repo created (if gh is authenticated)")
    elif args.command == "list":
        templates = get_templates(custom_dir)
        if not args.quiet:
            print("Available templates:")
            for name in templates:
                print(f"  {name}")
    elif args.command == "info":
        if args.template not in get_templates(custom_dir):
            print(f"Error: Unknown template '{args.template}'.", file=sys.stderr)
            sys.exit(1)
        info = get_template_info(args.template, custom_dir)
        if not args.quiet:
            print(f"Template: {info['name']}")
            print(f"Files: {len(info['files'])}")
            for f in info['files']:
                print(f"  {f}")
    elif args.command == "validate":
        if args.template not in get_templates(custom_dir):
            print(f"Error: Unknown template '{args.template}'.", file=sys.stderr)
            sys.exit(1)
        from workbench.scaffold import validate_template
        errors = validate_template(args.template, custom_dir)
        if errors:
            if not args.quiet:
                print(f"Template '{args.template}' is invalid:")
                for err in errors:
                    print(f"  - {err}")
            sys.exit(1)
        else:
            if not args.quiet:
                print(f"Template '{args.template}' is valid.")
    else:
        parser.print_help()
        sys.exit(1)
