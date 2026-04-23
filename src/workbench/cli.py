import argparse
import sys
from pathlib import Path
from workbench import __version__
from workbench.scaffold import init_project


def main():
    parser = argparse.ArgumentParser(prog="workbench")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("template", choices=["python"])
    init_parser.add_argument("name")
    init_parser.add_argument("--github", action="store_true", help="Create a private GitHub repo and push")

    args = parser.parse_args()

    if args.command == "init":
        target = Path.cwd() / args.name
        init_project(args.template, args.name, target, github=args.github)
        print(f"Created {args.template} project '{args.name}' at {target}")
        if args.github:
            print("GitHub repo created (if gh is authenticated)")
    else:
        parser.print_help()
        sys.exit(1)
