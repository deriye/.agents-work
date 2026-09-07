---
name: aigr-annotator
description: 'Use AIGR (AI Generated Review) to annotate source code with inline review comments that a VS Code extension renders as visual overlays.  Use this skill whenever you need to: mark code for review, flag potential bugs, highlight areas that need attention, document technical debt, or leave structured review notes in any source file.  Triggers on: "annotate", "review this code", "flag this", "mark for review", "add AIGR", "leave review comments", "document issues in the code".'
---

# AIGR Annotator

Add structured review annotations to source files by writing special comment
blocks, then run the extractor to produce `.aigr` sidecar files.  The VS Code
extension renders them as coloured gutter icons, line highlights, and hover
tooltips.

## Block Format

Wrap the code under review between an opening and closing marker, using the
file's native comment syntax:

```
<comment> <<<AIGR <ID> [<category>:<LEVEL>] <note>
<comment> <optional description line(s)>
<code to annotate>
<comment> AIGR>>>
```

### Rules

- **Opening marker**: a comment line containing `<<<AIGR`, followed by three
  space-separated fields on the same line: `ID`, `[category:LEVEL]`, `note`.
- **ID**: any non-whitespace token.  Use a ticket number, short label, or
  sequential tag — whatever fits the project.
- **Label**: `[category:LEVEL]` in square brackets.  The category and level are
  separated by a colon.  Both are single words (alphanumeric, no spaces).
  - **Built-in categories:**
    - `severity` — levels: `CRITICAL`, `MAJOR`, `MINOR`, `INFO`
    - `confidence` — levels: `HIGH`, `MEDIUM`, `LOW`
  - You can use any custom category/level (e.g. `[priority:URGENT]`,
    `[risk:HIGH]`).  Unknown categories render in grey by default; configure
    colours in VS Code settings (`aigr.labels`).
- **Note**: a short one-line summary (rest of the line after the label).
- **Description** (optional): commented lines between the header and the first
  code line.  These become the `description` field in the `.aigr` output.
  Use them for multi-line explanations.
- **Code**: all non-comment lines between the markers.  Kept verbatim after
  extraction.
- **Closing marker**: a comment line containing `AIGR>>>`.
- Each block **must** contain at least one code line.
- Each ID **must** be unique within a file.
- The comment prefix must match the file's language (`#` for Python/Shell,
  `//` for JS/TS/C/C++/Rust/Go, `--` for SQL/Lua, etc.).

### Examples

Python (severity):

```python
# <<<AIGR BUG-204 [severity:CRITICAL] Missing null check
# user can be None here, will raise AttributeError
def get_name(user):
    return user.name
# AIGR>>>
```

TypeScript (confidence):

```typescript
// <<<AIGR PERF-12 [confidence:MEDIUM] N+1 query in loop
// Each iteration hits the database. Batch the IDs and query once.
for (const id of ids) {
    const user = await db.users.findById(id);
    results.push(user);
}
// AIGR>>>
```

Go (severity):

```go
// <<<AIGR SEC-3 [severity:MAJOR] Error value discarded
f, _ := os.Open(path)
buf := make([]byte, 1024)
n, _ := f.Read(buf)
// AIGR>>>
```

No description (note only):

```python
# <<<AIGR STYLE-1 [severity:INFO] Consider using f-string
greeting = "Hello, " + name + "!"
# AIGR>>>
```

Custom category:

```python
# <<<AIGR DEBT-7 [priority:HIGH] Needs refactoring
# This module grew organically and should be split.
def do_everything():
    pass
# AIGR>>>
```

## Workflow

### Step 1 — Write Blocks

Insert `<<<AIGR ... AIGR>>>` blocks around the code to annotate, using the
comment syntax of the file's language.  Add as many blocks as needed.  Always
validate the format mentally before moving on:

- Does the header have all three fields: `ID [category:LEVEL] note`?
- Is the label in `[word:WORD]` format?
- Is there at least one code line between the markers?
- Is the closing `AIGR>>>` present and commented?

### Step 2 — Validate

Run the bundled extractor in validate mode to catch formatting mistakes
before extraction:

```bash
python <skill-path>/scripts/extract_aigr.py --validate <file-or-directory>
```

If there are errors, the script prints them to stderr in the format:

```
ERROR filename:line: description of the problem
```

Fix every reported error before proceeding.  Common mistakes:

| Error | Fix |
|---|---|
| `Malformed header` | Ensure the line after `<<<AIGR` has `ID [category:LEVEL] note` |
| `Unclosed block` | Add the missing `AIGR>>>` closing marker |
| `No code lines` | There must be at least one non-comment line in the block |
| `Duplicate ID` | Each block in a file needs a unique ID |

### Step 3 — Extract

Run the extractor to strip markers and produce the `.aigr` sidecar:

```bash
python <skill-path>/scripts/extract_aigr.py <file-or-directory>
```

This modifies the source files in-place (removes marker and description
lines, keeps code) and writes `<file>.aigr` JSON sidecars alongside them.

Use `--dry-run` to preview without writing:

```bash
python <skill-path>/scripts/extract_aigr.py --dry-run <file-or-directory>
```

### Step 4 — Verify

After extraction, confirm the `.aigr` files were created:

```bash
ls *.aigr
```

The VS Code extension picks up `.aigr` files automatically and renders the
annotations.

## Choosing Labels

### severity (recommended for bug reports)

- **CRITICAL** — Bugs, security issues, crashes, data loss, correctness problems.
- **MAJOR** — Performance issues, race conditions, missing edge cases that
  degrade behaviour but don't crash.
- **MINOR** — Code smell, missing validation, minor logic gaps.
- **INFO** — Style, readability, naming, minor improvements, tech debt notes.

### confidence (for uncertain findings)

- **HIGH** — Very likely a real issue.
- **MEDIUM** — Probable issue, needs investigation.
- **LOW** — Possible issue, may be a false positive.

### Custom categories

Use any `[category:LEVEL]` pair.  Examples: `[priority:URGENT]`,
`[risk:HIGH]`, `[debt:MODERATE]`.  Configure colours in VS Code settings.

## Tips

- Annotate in batches: add all blocks to a file, then run the extractor once.
- Use `--validate` first to catch formatting errors cheaply.
- Keep IDs meaningful to the project (ticket numbers, categories, etc.).
- Keep notes concise (one line).  Put detail in description lines.
- The extractor handles any file extension listed in `SUPPORTED_EXTENSIONS`
  (`.py`, `.js`, `.ts`, `.tsx`, `.jsx`, `.cpp`, `.c`, `.h`, `.hpp`, `.rs`,
  `.go`, `.java`, `.kt`, `.cs`, `.rb`, `.sh`, `.bash`, `.yaml`, `.yml`,
  `.toml`, `.txt`, `.md`).  Add more with `--ext .vue`.
