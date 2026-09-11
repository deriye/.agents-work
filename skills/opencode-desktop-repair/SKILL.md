---
name: opencode-desktop-repair
description: Diagnose and repair OpenCode desktop state when a renamed/deleted project directory keeps getting reopened, sessions hang with no assistant reply, a "ghost" directory keeps spawning on open, or projects disappear from the sidebar and must be re-added every launch. Use when a folder was renamed (e.g. .agents-old -> .agents-work -> .agents) and the app still references the old path, when opening a project spawns a dead directory with ENOENT/realPath errors, when new sessions produce no response, when projects vanish from the UI, or when a prior hand-edit left a state file with a UTF-8 BOM so the app stops persisting. Triggers on: OpenCode desktop broken, ghost project, stale directory, ENOENT realPath, prompt_async failed, session hangs, projects disappear every launch, projects not saved, opencode.db, opencode.global.dat, BOM, project keeps reopening old folder.
disable-model-invocation: true
---

# OpenCode Desktop Repair

Repairs OpenCode **desktop** app state after a project directory is renamed or
deleted and the app keeps referencing the old path. Symptoms: opening a project
spawns a now-deleted "ghost" directory, ENOENT/`realPath` errors, new sessions
hang with no reply, or projects disappear from the UI.

## Critical constraints

- **You (the agent) run inside the desktop app.** You CANNOT close it and you
  CANNOT reliably edit files it has open. All fixes that mutate app state must
  run in an EXTERNAL terminal AFTER the user fully quits the app.
- The sidecar HTTP API requires an internal token — treat it as unusable (401).
- Windows PowerShell 5.1: scripts must be **all-ASCII** (no em-dashes/smart
  quotes) or the tokenizer throws "missing terminator". Verify before handing off.
- **NEVER edit `.dat`/JSON state with `Set-Content -Encoding UTF8` on PS 5.1** —
  it writes a **UTF-8 BOM** (`EF BB BF`) and CRLF. The app writes these files
  with **no BOM + LF**; a BOM makes the app fail to parse on startup, show an
  empty project list, and stop persisting (projects vanish every launch). To
  write JSON state, use `System.Text.UTF8Encoding($false)` +
  `[IO.File]::WriteAllText(...)`. See Fix D and `reference.md`.
- Always **back up** before mutating, and operate on a **copy** for diagnosis.

## State locations (Windows)

| What | Path |
|---|---|
| Core log (source of truth) | `~/.local/share/opencode/log/opencode.log` |
| Sidecar SQLite DB (projects, sessions, messages) | `~/.local/share/opencode/opencode.db` (+ `-wal`, `-shm`) |
| Desktop JSON state (project list, lastProject, layout, notifications) | `%APPDATA%/ai.opencode.desktop/opencode.global.dat` |
| Window/tab state | `%APPDATA%/ai.opencode.desktop/opencode.window.*.dat` |
| Per-workspace state | `%APPDATA%/ai.opencode.desktop/opencode.workspace.*.dat` |
| Drafts (usually NOT the cause) | `%APPDATA%/ai.opencode.desktop/drafts.sqlite` |

## Diagnosis workflow

Copy this checklist and track progress:

```
- [ ] 1. Read the log to identify the failing directory + mechanism
- [ ] 2. Rule out folder-side causes (symlink, config, git worktree/submodule)
- [ ] 3. Inspect opencode.db project table (the usual root cause)
- [ ] 4. Inspect opencode.db session table (ghost dirs + corrupt rows)
- [ ] 5. Inspect opencode.global.dat (lastProject, layout.handoff, notifications)
- [ ] 6. Apply the minimal fix that matches the evidence
- [ ] 7. User relaunches; verify log shows only the correct directory
```

### Step 1: Read the log

```powershell
Get-Content "$env:USERPROFILE\.local\share\opencode\log\opencode.log" -Tail 60
```

Look for the tell-tale sequence: opening the GOOD dir, then ~1-3s later
`creating instance` / `bootstrapping` a DEAD dir, then
`FileSystem.realPath (...) ENOENT` and `prompt_async failed`. Note the
`projectID=<hash>` on the `project copy refresh` line — that hash is the
poisoned project row.

Confirm the LLM itself works: a session in another dir (e.g. `.tmp`) that
completes `loop -> process -> stream` proves the provider is fine and the issue
is directory/project-scoped.

### Step 2: Rule out folder-side causes

The app loading dir B when you open dir A is almost never caused by the folder
contents, but rule it out:

```powershell
$root = "<the GOOD project path>"
# symlinks/reparse points
Get-ChildItem $root -Recurse -Force -EA SilentlyContinue | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }
# opencode config
Get-ChildItem $root -Recurse -Force -EA SilentlyContinue -Include "opencode.json","opencode.jsonc",".opencode"
# git submodules/worktrees
Get-Content "$root\.gitmodules" -EA SilentlyContinue; Get-ChildItem "$root\.git\worktrees" -EA SilentlyContinue
```

If all empty, the cause is app state (DB / .dat). Proceed.

### Step 3-4: Inspect opencode.db (requires Python 3, has built-in sqlite3)

The DB is WAL-locked while the app runs, so **copy it first** (shared-read works
even when locked) and inspect the copy:

```powershell
$src="$env:USERPROFILE\.local\share\opencode"; $dst="$env:LOCALAPPDATA\Temp\opencode\db-inspect"
New-Item -ItemType Directory -Path $dst -Force | Out-Null
foreach($f in 'opencode.db','opencode.db-wal','opencode.db-shm'){ $s=Join-Path $src $f; if(Test-Path $s){ $fs=[IO.File]::Open($s,'Open','Read','ReadWrite'); $ms=New-Object IO.MemoryStream; $fs.CopyTo($ms); $fs.Close(); [IO.File]::WriteAllBytes((Join-Path $dst $f),$ms.ToArray()) } }
python scripts/inspect_db.py "$dst\opencode.db"
```

`inspect_db.py` reports:
- **`project` rows** whose `worktree` points at a dead dir. THE USUAL ROOT
  CAUSE: a duplicate project for the same git repo where one row has
  `worktree = <dead dir>` but `name`/`sandboxes` reference the good dir. Opening
  the good dir matches this poisoned project (via its `sandboxes` list) and
  bootstraps its dead `worktree`.
- **`session` rows** bound to the dead dir (re-bootstrap the ghost on open).
- **corrupt `session` rows** (non-UTF8 `directory`, NULL `path`) that make
  `session.list` fail with "Path is not absolute" -> the app hangs with NO error
  popup and NO reply.

### Step 5: Inspect opencode.global.dat (JSON)

```powershell
$c = Get-Content "$env:APPDATA\ai.opencode.desktop\opencode.global.dat" -Raw | ConvertFrom-Json
# server: lastProject + project registry
$c.server
# layout.handoff: base64-encoded dir the app hands new tabs off to
[string]$c.layout | Select-String 'handoff'
```

Dead dirs may hide **base64-encoded** in the `layout` key (`handoff.tabs.dir`,
`sessionView`/`sessionTabs` keys). `.agents-work` base64 =
`QzpcVXNlcnNc...` prefix; decode with
`[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($b64))`.

### Step 5b: Check for a BOM (if projects disappear every launch)

Distinct symptom: **projects vanish from the sidebar on every launch and you
re-add them each time.** This is usually not a DB problem -- it means the app
cannot parse `opencode.global.dat`, so it comes up empty and refuses to persist.

Tell-tale signs:
- `opencode.global.dat`'s **write timestamp is frozen** at the moment of a prior
  hand-edit (the app never rewrites a file it cannot read), while the DB and
  `opencode.workspace.*.dat` files ARE updated on recent launches.
- The file starts with a **UTF-8 BOM** (`EF BB BF`) instead of `{` (`7B`).

```powershell
$f = "$env:APPDATA\ai.opencode.desktop\opencode.global.dat"
(Get-Item $f).LastWriteTime                                   # frozen?
$b = [IO.File]::ReadAllBytes($f)
($b[0..2] | % { $_.ToString('X2') }) -join ' '                # EF BB BF = BOM (bad)
# compare against an app-written file (should start 7B .. = open-brace):
$d = [IO.File]::ReadAllBytes((Join-Path (Split-Path $f) 'default.dat'))
($d[0..2] | % { $_.ToString('X2') }) -join ' '
```

If `global.dat` has a BOM, apply **Fix D**. The BOM is almost always
self-inflicted by a prior `Set-Content -Encoding UTF8` edit (see Fix C warning).
`opencode.window.*.dat` edited the same way carry the same BOM.

## Fixes

Apply ONLY what the evidence shows. In practice the **project-table fix (A) is
the definitive one**; the others are supplementary.

All fix scripts: refuse to run if `OpenCode` process is alive, back up first,
verify `integrity_check` + `foreign_key_check` after.

### Fix A — poisoned project row (most common root cause)

Deletes any `project` whose `worktree` references the dead dir, plus its
`project_directory`/`workspace`/`session` children. Leaves the clean project
(correct `worktree`) intact.

```powershell
# user runs AFTER fully quitting OpenCode:
powershell -ExecutionPolicy Bypass -File "<skill>/scripts/fix-project.ps1"
```

### Fix B — ghost sessions + corrupt session rows

Deletes `session` rows bound to the dead dir and any corrupt-path rows (with
their `message`/`part` children). Fixes the silent no-reply hang.

```powershell
powershell -ExecutionPolicy Bypass -File "<skill>/scripts/fix-sessions.ps1"
```

### Fix C — desktop JSON state (lastProject / handoff / notifications)

If the app auto-opens the dead dir on launch (`server.lastProject`) or hands new
tabs to it (`layout.handoff`), edit `opencode.global.dat`. **Only rewrite the
single key you change** via raw-text replacement — re-serializing the whole
outer JSON with PowerShell 5.1 `ConvertTo-Json` can drop/mangle other keys (it
made the project list vanish once). **Write the result with NO BOM and LF
endings** (`UTF8Encoding($false)` + `WriteAllText`); `Set-Content -Encoding UTF8`
adds a BOM that breaks the app (see Fix D). See `reference.md` for the exact
technique.

### Fix D: strip BOM / fix .dat encoding (projects disappear every launch)

If Step 5b shows a BOM, rewrite the affected `.dat` files without a BOM and with
LF endings, preserving the JSON content exactly. Fixes the empty-sidebar /
projects-not-persisting loop. Covers `opencode.global.dat` and any
`opencode.window.*.dat` that carry a BOM.

```powershell
powershell -ExecutionPolicy Bypass -File "<skill>/scripts/fix-global-bom.ps1"
```

After running, `opencode.global.dat` should start with `7B` (open-brace) not
`EF BB BF`, and its timestamp should advance on the next launch (the app can
persist again).

## Verification

After the user relaunches and opens the project, confirm the log shows only the
correct directory:

```powershell
Get-Content "$env:USERPROFILE\.local\share\opencode\log\opencode.log" -Tail 40 | Select-String 'agents|ENOENT|prompt_async|creating instance'
```

Success = the good dir bootstraps, NO dead-dir `creating instance`, NO
`realPath ENOENT`, and a new session completes `loop -> process -> stream`.

## Handing off scripts to the user

Because you run inside the app, you cannot execute the fix. Give the user the
exact command and tell them to:
1. Fully quit OpenCode desktop (all `OpenCode.exe` — this ends your session).
2. Run the script in an external PowerShell.
3. Paste the output back so you verify from fresh logs on next launch.

## Additional resources

- `reference.md` — detailed DB schema, the safe JSON-edit technique, and gotchas.
- `scripts/inspect_db.py` — read-only diagnosis of project/session tables.
- `scripts/fix-project.ps1` — Fix A (poisoned project row).
- `scripts/fix-sessions.ps1` — Fix B (ghost + corrupt sessions).
- `scripts/fix-global-bom.ps1` — Fix D (strip BOM / fix .dat encoding).
