# workbench v3 Plan — CLIG Compliance Iterations

## Scope
Address items 1–10 from the clig.dev assessment, excluding item 7 (`.env`/configuration — deferred for discussion).

## Iterations

### Iteration 1: `-n` short flag for `--dry-run`
- Add `"-n"` to the `--dry-run` argument in `init_parser`.
- Test: `workbench init python test -n` should behave identically to `--dry-run`.

### Iteration 2: Bug report link in help text
- Create a custom `HelpFormatter` or add `epilog=` to the main parser.
- Include: `Report issues: https://github.com/8bit64k/workbench/issues`
- Appears in `workbench --help`, `workbench init --help`, etc.

### Iteration 3: Concise help for bare subcommands
- Running `workbench init` (no args) currently prints a raw argparse error.
- Override parser behavior to show concise help instead: description + example + `--help` pointer.

### Iteration 4: `--json` flag for machine-readable output
- Add `--json` to `list` and `info` subcommands.
- `workbench list --json` → `["cli", "fastapi", "library", "python"]`
- `workbench info python --json` → `{"name": "python", "files": [...]}`

### Iteration 5: `--plain` flag for unformatted output
- Add `--plain` to `list`, `info`, `validate`.
- Disables human-friendly formatting (headers, indentation) for pipe-friendly use.

### Iteration 6: Post-init "next steps" suggestion
- After successful `init`, print a "Get started" block:
  ```
  Get started:
    cd <target>
    make install
    make test
  ```

### Iteration 7: `NO_COLOR` + `--no-color` support
- Check `NO_COLOR` env var, `TERM=dumb`, `--no-color` flag.
- Add a color utility module (or simple helper).
- Wrap all `print()` calls that should use color.

### Iteration 8: More actionable error messages
- `FileExistsError` → mention `--dry-run` and `--force` explicitly.
- `ValueError` (unknown template) → suggest `workbench list`.
- Group similar errors under a single header.

### Iteration 9: Rich help text with examples
- Create a custom `argparse.RawDescriptionHelpFormatter` subclass.
- Add examples section to help output (init, list, info, validate).
- Format with bold/underline via ANSI escape codes (respecting color settings).

### Iteration 10: Full test suite, README update, push
- Run full test suite.
- Update README with new flags (`-n`, `--json`, `--plain`, `--no-color`).
- Update CLI reference examples.
- Commit and push.
