import argparse
import sys
from pathlib import Path
from workbench import __version__
from workbench.scaffold import init_project, get_templates


def main():
    parser = argparse.ArgumentParser(prog="workbench")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("template", choices=["python", "library", "cli"])
    init_parser.add_argument("name")
    init_parser.add_argument("--github", action="store_true", help="Create a private GitHub repo and push")

    list_parser = subparsers.add_parser("list", help="List available templates")

    args = parser.parse_args()

    if args.command == "init":
        descriptions = {
            "python": "A Python project.",
            "library": "A reusable Python library package.",
            "cli": "A command-line interface tool.",
        }
        target = Path.cwd() / args.name
        init_project(
            args.template,
            args.name,
            target,
            github=args.github,
            project_description=descriptions[args.template],
        )
        print(f"Created {args.template} project '{args.name}' at {target}")
        if args.github:
            print("GitHub repo created (if gh is authenticated)")
    elif args.command == "list":
        templates = get_templates()
        print("Available templates:")
        for name in templates:
            print(f"  {name}")
    else:
        parser.print_help()
        sys.exit(1)
