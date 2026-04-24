import argparse
import sys
from pathlib import Path
from workbench import __version__
from workbench.scaffold import init_project, get_templates, get_template_info


def main():
    parser = argparse.ArgumentParser(prog="workbench")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show debug output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress non-error output")
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("--verbose", "-v", action="store_true", help="Show debug output")
    init_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress non-error output")
    init_parser.add_argument("template", choices=get_templates())
    init_parser.add_argument("name")
    init_parser.add_argument("--github", action="store_true", help="Create a private GitHub repo and push")
    init_parser.add_argument("--dry-run", action="store_true", help="Show what would be created without writing files")
    init_parser.add_argument("--output", "-o", type=str, default=".", help="Target directory (default: current directory)")

    list_parser = subparsers.add_parser("list", help="List available templates")
    list_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress non-error output")

    info_parser = subparsers.add_parser("info", help="Show template details")
    info_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress non-error output")
    info_parser.add_argument("template", choices=get_templates())

    args = parser.parse_args()

    if args.command == "init":
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
        templates = get_templates()
        if not args.quiet:
            print("Available templates:")
            for name in templates:
                print(f"  {name}")
    elif args.command == "info":
        info = get_template_info(args.template)
        if not args.quiet:
            print(f"Template: {info['name']}")
            print(f"Files: {len(info['files'])}")
            for f in info['files']:
                print(f"  {f}")
    else:
        parser.print_help()
        sys.exit(1)
