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

    args = parser.parse_args()

    if args.command == "init":
        target = Path.cwd() / args.name
        init_project(args.template, args.name, target)
        print(f"Created {args.template} project '{args.name}' at {target}")
    else:
        parser.print_help()
        sys.exit(1)
