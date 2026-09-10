# Python (package + CLI)

General best practice for a Python distribution package, especially one that
exposes a command-line interface. Project-agnostic: when a repository already
has a layout, match it (see the root skill, "Lookup" rule 5); this file is the
default for new layout only.

## Sources

- Python Packaging User Guide — Packaging Python Projects:
  https://packaging.python.org/en/latest/tutorials/packaging-projects/
- Python Packaging User Guide — src layout vs flat layout:
  https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
- Python Packaging User Guide — Creating command-line tools:
  https://packaging.python.org/en/latest/guides/creating-command-line-tools/
- pytest — Good Integration Practices:
  https://docs.pytest.org/en/stable/explanation/goodpractices.html

## When it applies

Any importable Python package, and any project that ships a console entry
point (a CLI). Use it when adding modules, subcommands, or tests to such a
project.

## Folder tree

Prefer the **src layout** — the import package lives under `src/`, so tests
run against the installed package, not stray top-level modules.

```
pyproject.toml          # build backend + [project] metadata + tool config
README.md
LICENSE
src/
    <package>/
        __init__.py
        __main__.py     # only if `python -m <package>` is wanted
        <module>.py     # one module per cohesive job
        <subpackage>/   # group related modules; each has __init__.py
            __init__.py
            <module>.py
tests/
    <test_module>.py    # mirrors the package; see Testing
```

Rules:

- One module = one cohesive job. Do not put several unrelated jobs in one
  file, and do not split a single job across files for its own sake.
- Group related modules into a subpackage (a folder with `__init__.py`) once
  a flat set of modules gets hard to scan. Do not create a subpackage with a
  single module "for later".
- Keep the CLI's argument wiring (parser/subcommands/dispatch) separate from
  the logic each subcommand runs, so the logic is importable and testable
  without going through `argv`.

## Dependency direction

- The CLI entry point (argument parsing + dispatch) imports the command
  logic; command logic does not import the entry point.
- Shared helpers live in their own module that both commands import; a
  command module does not import a sibling command module.
- Nothing under `src/` imports from `tests/`.

## Where the CLI, logic, and shared code live

- **Entry point / argument parsing:** one module (commonly `__main__.py` or a
  `cli`/`main` module) that builds the parser, registers subcommands, and
  dispatches to a handler. Declared as a console script under
  `[project.scripts]` in `pyproject.toml`.
- **Per-command logic:** one module per command, each exposing a small,
  directly-callable surface (a function or a handler object) that takes plain
  arguments — not the raw parsed namespace where avoidable — so it can be
  unit-tested and reused by other programs without a subprocess.
- **Shared code:** a helpers/core module imported by the commands that need
  it. Do not reach into one command from another.

## Testing

- **Runner:** `pytest`. Configure it in `pyproject.toml` under
  `[tool.pytest.ini_options]` (set `testpaths`, and prefer
  `--import-mode=importlib` for new projects). Install the package editable
  (`pip install -e .`) so tests exercise the real package.
- **Location:** tests live **outside** the application code, in a top-level
  `tests/` directory (works with the src layout above). Name files
  `test_*.py`; name test functions `test_*`. Give test modules unique names
  unless you add `__init__.py` packages under `tests/`.
- **Unit vs integration:** separate fast, dependency-free unit tests from
  slower tests that need external systems (live services, hardware, network).
  A common split is `tests/unit/` and `tests/integration/`; alternatively use
  pytest markers (registered in config) and select with `-m`. Keep unit tests
  hermetic.
- **Fixtures & temp files:** use pytest's `tmp_path` for files a test writes,
  and fixtures for shared setup; do not write into the repository tree or
  depend on test execution order. Close resources (open files under `with`).
- **CLI tests:** test each command's logic by calling its function/handler
  directly with constructed arguments (fast, precise). Add a thin
  end-to-end test that invokes the built parser/entry point for the
  user-visible flow (arguments in, exit code and output out); assert exit
  codes for commands that gate on success/failure.
- **What to assert:** the observable contract — return/exit codes, files
  created or left untouched, and printed report lines — not internal call
  order.

## What not to add

- No flat layout with the package directly in the repo root when starting
  fresh (src layout avoids import-shadowing pitfalls).
- No empty `utils/`, `helpers/`, `core/`, or `types/` packages created before
  there is code to put in them.
- No `setup.py test` / `pytest-runner`; drive tests with `pytest` directly.
- No re-export barrel `__init__.py` that only exists to shorten imports,
  unless the project already uses that pattern.
- No test that depends on another test having run first.
