import argparse
import difflib
import json
import os
import sys
from pathlib import Path
from workbench import __version__
from workbench.scaffold import init_project, get_templates, get_template_info
from workbench.config import load_config, save_config, DEFAULTS

BUG_REPORT_URL = "https://github.com/8bit64k/workbench/issues"

# ANSI escape codes
_BOLD = "\033[1m"
_RED = "\033[31m"
_RESET = "\033[0m"


def _should_use_color(no_color_flag: bool) -> bool:
    if no_color_flag:
        return False
    if os.environ.get("NO_COLOR", ""):
        return False
    if os.environ.get("TERM", "") == "dumb":
        return False
    return sys.stdout.isatty()


def _fmt(text: str, color: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{color}{text}{_RESET}"


def _template_dir_from_args(args) -> Path | None:
    if args.template_dir:
        return Path(args.template_dir)
    env = os.environ.get("WORKBENCH_TEMPLATE_DIR")
    if env:
        return Path(env)
    cfg = load_config()
    cfg_dir = cfg.get("default_template_dir")
    if cfg_dir:
        return Path(cfg_dir)
    return None


def _show_bare_subcommand_help(prog: str, description: str, example: str, extra_examples: list[str] | None = None):
    print(f"{prog}\n")
    print(f"{description}\n")
    print("Example:")
    print(f"  $ {example}")
    if extra_examples:
        for ex in extra_examples:
            print(f"  $ {ex}")
    print("\nPass --help for full usage information.")


_BASH_COMPLETION = '''_workbench_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts="--version --verbose --quiet --no-color --template-dir --generate-completion -v -q"
    commands="init list info validate config"

    if [[ ${COMP_CWORD} -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "${opts} ${commands}" -- ${cur}) )
        return 0
    fi

    case "${COMP_WORDS[1]}" in
        init)
            local init_opts="--github --dry-run --output --force --verbose --quiet -n -o -v -q"
            COMPREPLY=( $(compgen -W "${init_opts}" -- ${cur}) )
            ;;
        list)
            local list_opts="--json --plain --quiet"
            COMPREPLY=( $(compgen -W "${list_opts}" -- ${cur}) )
            ;;
        info|validate)
            local info_opts="--json --plain --quiet"
            COMPREPLY=( $(compgen -W "${info_opts}" -- ${cur}) )
            ;;
        config)
            local config_cmds="set get list unset"
            COMPREPLY=( $(compgen -W "${config_cmds}" -- ${cur}) )
            ;;
    esac
}
complete -F _workbench_completion workbench
'''

_ZSH_COMPLETION = '''#compdef workbench

local curcontext="$curcontext" state line
typeset -A opt_args

_workbench_commands() {
    local commands
    commands=(
        'init:Initialize a new project'
        'list:List available templates'
        'info:Show template details'
        'validate:Validate a template'
        'config:Manage workbench configuration'
    )
    _describe -t commands 'workbench command' commands
}

_arguments -C \\
    '(-v --verbose)'{-v,--verbose}'[Show debug output]' \\
    '(-q --quiet)'{-q,--quiet}'[Suppress non-error output]' \\
    '--no-color[Disable colored output]' \\
    '--template-dir[Custom template directory]:directory:_directories' \\
    '--generate-completion[Print shell completion]:shell:(bash zsh fish)' \\
    '1: :_workbench_commands' \\
    '*:: :->args'

case "$line[1]" in
    init)
        _arguments \\
            '--github[Create a private GitHub repo]' \\
            '(-n --dry-run)'{-n,--dry-run}'[Preview without writing files]' \\
            '(-o --output)'{-o,--output}'[Target directory]:directory:_directories' \\
            '--force[Scaffold into existing directory]'
        ;;
    list)
        _arguments \\
            '--json[Output as JSON]' \\
            '--plain[Output as plain text]'
        ;;
    info|validate)
        _arguments \\
            '--json[Output as JSON]' \\
            '--plain[Output as plain text]'
        ;;
    config)
        local config_cmds
        config_cmds=(
            'set:Set a config value'
            'get:Get a config value'
            'list:List all config values'
            'unset:Remove a config key'
        )
        _describe -t commands 'config command' config_cmds
        ;;
esac
'''

_FISH_COMPLETION = '''complete -c workbench -f
complete -c workbench -l version -d "Show version"
complete -c workbench -l verbose -s v -d "Show debug output"
complete -c workbench -l quiet -s q -d "Suppress non-error output"
complete -c workbench -l no-color -d "Disable colored output"
complete -c workbench -l template-dir -d "Custom template directory"
complete -c workbench -l generate-completion -a "bash zsh fish" -d "Print completion script"

complete -c workbench -n "not __fish_seen_subcommand_from init list info validate config" -a "init" -d "Initialize a new project"
complete -c workbench -n "not __fish_seen_subcommand_from init list info validate config" -a "list" -d "List available templates"
complete -c workbench -n "not __fish_seen_subcommand_from init list info validate config" -a "info" -d "Show template details"
complete -c workbench -n "not __fish_seen_subcommand_from init list info validate config" -a "validate" -d "Validate a template"
complete -c workbench -n "not __fish_seen_subcommand_from init list info validate config" -a "config" -d "Manage configuration"

complete -c workbench -n "__fish_seen_subcommand_from init" -l github -d "Create a private GitHub repo"
complete -c workbench -n "__fish_seen_subcommand_from init" -l dry-run -s n -d "Preview without writing files"
complete -c workbench -n "__fish_seen_subcommand_from init" -l output -s o -d "Target directory"
complete -c workbench -n "__fish_seen_subcommand_from init" -l force -d "Scaffold into existing directory"

complete -c workbench -n "__fish_seen_subcommand_from list" -l json -d "Output as JSON"
complete -c workbench -n "__fish_seen_subcommand_from list" -l plain -d "Output as plain text"

complete -c workbench -n "__fish_seen_subcommand_from info validate" -l json -d "Output as JSON"
complete -c workbench -n "__fish_seen_subcommand_from info validate" -l plain -d "Output as plain text"

complete -c workbench -n "__fish_seen_subcommand_from config" -a "set" -d "Set a config value"
complete -c workbench -n "__fish_seen_subcommand_from config" -a "get" -d "Get a config value"
complete -c workbench -n "__fish_seen_subcommand_from config" -a "list" -d "List all config values"
complete -c workbench -n "__fish_seen_subcommand_from config" -a "unset" -d "Remove a config key"
'''


def _print_completion(shell: str) -> None:
    if shell == "bash":
        print(_BASH_COMPLETION)
    elif shell == "zsh":
        print(_ZSH_COMPLETION)
    elif shell == "fish":
        print(_FISH_COMPLETION)


def main():
    parser = argparse.ArgumentParser(
        prog="workbench",
        description="A minimal, opinionated CLI scaffolding tool for Python projects.",
        epilog=f"Report issues: {BUG_REPORT_URL}",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show debug output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress non-error output")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("--template-dir", type=str, default=None, help="Custom template directory (or set WORKBENCH_TEMPLATE_DIR)")
    parser.add_argument("--generate-completion", choices=["bash", "zsh", "fish"], help="Print shell completion script to stdout")
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser(
        "init",
        help="Initialize a new project",
        description="Initialize a new project from a template.",
        epilog=f"\nExamples:\n  $ workbench init python my-project\n  $ workbench init cli todo-cli --github --dry-run\n\nReport issues: {BUG_REPORT_URL}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    init_parser.add_argument("--verbose", "-v", action="store_true", help="Show debug output")
    init_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress non-error output")
    init_parser.add_argument("template", nargs="?", help="Template to use")
    init_parser.add_argument("name", nargs="?", help="Project name")
    init_parser.add_argument("--github", action="store_true", help="Create a private GitHub repo and push")
    init_parser.add_argument("--dry-run", "-n", action="store_true", help="Show what would be created without writing files")
    init_parser.add_argument("--output", "-o", type=str, default=".", help="Target directory (default: current directory)")
    init_parser.add_argument("--force", action="store_true", help="Scaffold into an existing non-empty directory")
    init_parser.add_argument("--no-hooks", action="store_true", help="Skip post-init hooks")

    list_parser = subparsers.add_parser(
        "list",
        help="List available templates",
        epilog=f"Report issues: {BUG_REPORT_URL}",
    )
    list_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress non-error output")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")
    list_parser.add_argument("--plain", action="store_true", help="Output as plain text (one per line)")

    info_parser = subparsers.add_parser(
        "info",
        help="Show template details",
        description="Show template details including file count and complete file tree.",
        epilog=f"\nExample:\n  $ workbench info python\n\nReport issues: {BUG_REPORT_URL}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    info_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress non-error output")
    info_parser.add_argument("--json", action="store_true", help="Output as JSON")
    info_parser.add_argument("--plain", action="store_true", help="Output as plain text (one per line)")
    info_parser.add_argument("template", nargs="?", help="Template name")

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a template",
        description="Validate a template for structural soundness and Jinja2 correctness.",
        epilog=f"\nExample:\n  $ workbench validate python\n\nReport issues: {BUG_REPORT_URL}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    validate_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress non-error output")
    validate_parser.add_argument("--json", action="store_true", help="Output as JSON")
    validate_parser.add_argument("--plain", action="store_true", help="Output as plain text (one per line)")
    validate_parser.add_argument("template", nargs="?", help="Template name")

    config_parser = subparsers.add_parser(
        "config",
        help="Manage workbench configuration",
        description="Get, set, or list configuration values.",
        epilog=f"\nExamples:\n  $ workbench config set author '8bit64k'\n  $ workbench config get license\n  $ workbench config list\n\nReport issues: {BUG_REPORT_URL}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    config_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress non-error output")
    config_subparsers = config_parser.add_subparsers(dest="config_command")

    config_set_parser = config_subparsers.add_parser("set", help="Set a config value")
    config_set_parser.add_argument("key", help="Config key")
    config_set_parser.add_argument("value", help="Config value")

    config_get_parser = config_subparsers.add_parser("get", help="Get a config value")
    config_get_parser.add_argument("key", help="Config key")

    config_list_parser = config_subparsers.add_parser("list", help="List all config values")

    config_unset_parser = config_subparsers.add_parser("unset", help="Remove a config key")
    config_unset_parser.add_argument("key", help="Config key")

    args = parser.parse_args()

    if args.generate_completion:
        _print_completion(args.generate_completion)
        sys.exit(0)

    use_color = _should_use_color(args.no_color)
    custom_dir = _template_dir_from_args(args)

    if args.command == "init":
        if not args.template or not args.name:
            _show_bare_subcommand_help(
                "workbench init <template> <name> [options]",
                "Initialize a new project from a template.",
                "workbench init python my-project",
                extra_examples=["workbench init cli todo-cli --github --dry-run"],
            )
            sys.exit(1)

        templates = get_templates(custom_dir)
        if args.template not in templates:
            msg = _fmt(f"Error: Unknown template '{args.template}'.", _RED + _BOLD, use_color)
            close = difflib.get_close_matches(args.template, templates, n=1)
            if close:
                msg += _fmt(f"\nDid you mean '{close[0]}'?", _BOLD, use_color)
            if templates:
                msg += f"\nRun '{_fmt('workbench list', _BOLD, use_color)}' to see available templates."
            print(msg, file=sys.stderr)
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
        try:
            cfg = load_config()
            actions = init_project(
                args.template,
                args.name,
                target,
                github=args.github,
                project_description=descriptions.get(args.template, "A Python project."),
                dry_run=args.dry_run,
                force=args.force,
                template_dir=custom_dir,
                author=cfg.get("author"),
                email=cfg.get("email"),
                license=cfg.get("license"),
                no_hooks=args.no_hooks,
            )
        except FileExistsError as exc:
            msg = _fmt(f"Error: {exc}", _RED, use_color)
            msg += _fmt("\n\nTo preview changes, run with --dry-run or -n.", _BOLD, use_color)
            if not args.force:
                msg += _fmt("\nTo force overwrite, run with --force.", _BOLD, use_color)
            print(msg, file=sys.stderr)
            sys.exit(1)
        except ValueError as exc:
            print(_fmt(f"Error: {exc}", _RED, use_color), file=sys.stderr)
            sys.exit(1)

        if args.verbose:
            print(f"[debug] Files generated: {len(actions)}")

        if not args.quiet:
            action_word = "Would create" if args.dry_run else "Created"
            print(f"{action_word} {_fmt(args.template, _BOLD, use_color)} project '{_fmt(args.name, _BOLD, use_color)}' at {target}")
            if args.dry_run and actions:
                for action in actions:
                    print(f"  {action}")
            if args.github and not args.dry_run:
                print("GitHub repo created (if gh is authenticated)")
            if not args.dry_run:
                print()
                print(_fmt("Get started:", _BOLD, use_color))
                print(f"  cd {target}")
                if (target / "Makefile").exists():
                    print("  make install")
                    print("  make test")
                else:
                    print("  uv pip install -e \".[dev]\"")
                    print("  uv run pytest tests/ -v")

    elif args.command == "list":
        templates = get_templates(custom_dir)
        if not templates:
            print("Warning: No templates found.")
            sys.exit(0)
        if args.json:
            print(json.dumps(templates))
        elif args.plain:
            for name in templates:
                print(name)
        elif not args.quiet:
            print("Available templates:")
            for name in templates:
                print(f"  {name}")

    elif args.command == "info":
        if not args.template:
            _show_bare_subcommand_help(
                "workbench info <template>",
                "Show template details including file count and complete file tree.",
                "workbench info python",
            )
            sys.exit(1)
        if args.template not in get_templates(custom_dir):
            print(_fmt(f"Error: Unknown template '{args.template}'.", _RED, use_color), file=sys.stderr)
            sys.exit(1)
        info = get_template_info(args.template, custom_dir)
        if args.json:
            print(json.dumps(info))
        elif args.plain:
            print(info["name"])
            print(len(info["files"]))
            for f in info["files"]:
                print(f)
        elif not args.quiet:
            print(f"Template: {info['name']}")
            print(f"Files: {len(info['files'])}")
            for f in info["files"]:
                print(f"  {f}")

    elif args.command == "validate":
        if not args.template:
            _show_bare_subcommand_help(
                "workbench validate <template>",
                "Validate a template for structural soundness and Jinja2 correctness.",
                "workbench validate python",
            )
            sys.exit(1)
        if args.template not in get_templates(custom_dir):
            print(_fmt(f"Error: Unknown template '{args.template}'.", _RED, use_color), file=sys.stderr)
            sys.exit(1)
        from workbench.scaffold import validate_template
        errors = validate_template(args.template, custom_dir)
        if errors:
            if args.json:
                print(json.dumps({"valid": False, "errors": errors}))
            elif args.plain:
                for err in errors:
                    print(err)
            elif not args.quiet:
                print(_fmt(f"Template '{args.template}' is invalid:", _RED + _BOLD, use_color))
                for err in errors:
                    print(f"  - {err}")
            sys.exit(1)
        else:
            if args.json:
                print(json.dumps({"valid": True, "errors": []}))
            elif args.plain:
                pass  # Nothing to print in plain mode for success
            elif not args.quiet:
                print(_fmt(f"Template '{args.template}' is valid.", _BOLD, use_color))

    elif args.command == "config":
        if not args.config_command:
            _show_bare_subcommand_help(
                "workbench config <command>",
                "Manage workbench configuration. Commands: set, get, list, unset.",
                "workbench config set author '8bit64k'",
                extra_examples=[
                    "workbench config get license",
                    "workbench config list",
                    "workbench config unset email",
                ],
            )
            sys.exit(1)

        cfg = load_config()

        if args.config_command == "set":
            cfg[args.key] = args.value
            save_config(cfg)
            if not args.quiet:
                print(f"Set {args.key} = {args.value}")

        elif args.config_command == "get":
            val = cfg.get(args.key)
            if val is None:
                print(_fmt(f"Error: '{args.key}' is not set.", _RED, use_color), file=sys.stderr)
                sys.exit(1)
            print(val)

        elif args.config_command == "list":
            for key in sorted(DEFAULTS.keys()):
                val = cfg.get(key)
                print(f"{key} = {val}")

        elif args.config_command == "unset":
            if args.key in cfg:
                del cfg[args.key]
                save_config(cfg)
                if not args.quiet:
                    print(f"Unset {args.key}")
            else:
                print(_fmt(f"Error: '{args.key}' is not set.", _RED, use_color), file=sys.stderr)
                sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)
