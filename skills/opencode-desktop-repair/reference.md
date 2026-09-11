# OpenCode Desktop Repair - Reference

Detailed schema, techniques, and gotchas backing `SKILL.md`. Read this when the
top-level workflow is not enough.

## opencode.db schema (relevant tables)

WAL-mode SQLite at `~/.local/share/opencode/opencode.db` (+ `-wal`, `-shm`).
Large (100s of MB). Locked while the app runs; copy with shared-read to inspect.

### project

Columns: `id, worktree, vcs, name, icon_url, icon_color, time_created,
time_updated, time_initialized, sandboxes, commands, icon_url_override`.

- `id` is a git-repo hash. **Two directories in the same git repo share the same
  hash**, so a renamed folder can collide with a stale row.
- `worktree` = the actual path the app bootstraps. If this points at a deleted
  dir, opening ANY dir that matches this project (via `sandboxes`) spawns the
  dead worktree -> `FileSystem.realPath ENOENT` -> `prompt_async failed`.
- `sandboxes` = JSON array of dirs that resolve to this project. The poison
  pattern: `worktree = <dead dir>` but `sandboxes = ["<good dir>"]` and
  `name = "<good dir basename>"`, so it masquerades as the good project.
- The clean project (correct `worktree`) usually also exists; keep it.

### project_directory

Columns: `project_id, directory, type, strategy, time_created`. Maps dirs to
projects. A duplicate here (two project_ids -> same directory) is a symptom of
the poison. Fix A removes the poisoned project's row, leaving the good mapping.

### session

Columns include `id, project_id, directory, path, title, ...`.

- Dead-dir sessions (`directory` LIKE a dead marker) re-bootstrap the ghost on
  reopen.
- **Corrupt rows**: non-UTF8 `directory` (garbage bytes) or NULL `path`. These
  break `session.list` with "Path is not absolute" and cause a **silent** hang
  (no popup, no reply) because list fails before any UI error path.
- Children (delete alongside a session): `message.session_id`, `part.session_id`
  (no declared FK but 1:1 by convention), `todo`, `session_share`,
  `session_message`, `session_input`, `session_context_epoch`.

### workspace

Has `project_id`. Usually empty for the poisoned project, but Fix A clears it
defensively.

## Safe DB mutation procedure

1. Confirm app closed: `Get-Process OpenCode` returns nothing.
2. Back up `opencode.db`, `-wal`, `-shm` to a timestamped temp dir.
3. Open with Python `sqlite3`, `con.text_factory = bytes` (paths may be non-UTF8
   -> decode with `errors='replace'`, never assume valid UTF-8).
4. `PRAGMA wal_checkpoint(TRUNCATE)` before AND after so changes land in the main
   file and `-wal` does not resurrect old state.
5. Do all deletes in a single `BEGIN`/`commit` transaction.
6. Verify `PRAGMA integrity_check` == `ok` and `PRAGMA foreign_key_check` == 0.
7. Always dry-run on a copy first (`shutil.copyfile`) and print BEFORE/AFTER.

## Copying a WAL-locked DB (app running, for inspection only)

```powershell
$src="$env:USERPROFILE\.local\share\opencode"; $dst="$env:LOCALAPPDATA\Temp\opencode\db-inspect"
New-Item -ItemType Directory -Path $dst -Force | Out-Null
foreach($f in 'opencode.db','opencode.db-wal','opencode.db-shm'){
  $s=Join-Path $src $f
  if(Test-Path $s){
    $fs=[IO.File]::Open($s,'Open','Read','ReadWrite')  # ReadWrite share = read while locked
    $ms=New-Object IO.MemoryStream; $fs.CopyTo($ms); $fs.Close()
    [IO.File]::WriteAllBytes((Join-Path $dst $f),$ms.ToArray())
  }
}
```

The copy reflects committed state; uncommitted WAL frames may lag, which is fine
for diagnosis. Never mutate this copy expecting it to affect the app.

## opencode.global.dat (desktop JSON state)

Plain JSON (despite `.dat`). Keys seen: `server`, `layout`, `notification`, etc.

- `server.lastProject.local` -> dir opened on launch. Reset to a safe dir (e.g.
  `.tmp`) to stop auto-opening a dead dir.
- `server` also holds the project registry shown in the UI project list.
- `notification` -> array; stale entries can reference dead dirs (harmless but
  noisy). Safe to clear.
- `layout` -> a big string/object holding tab + handoff state. Dead dirs often
  hide **base64-encoded** here: `handoff.tabs.dir`, `sessionView[<dir>]`,
  `sessionTabs`. Decode:
  ```powershell
  [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($b64))
  ```

### Safe edit technique (critical gotcha)

Do NOT `ConvertFrom-Json` -> modify -> `ConvertTo-Json` the whole file in
PowerShell 5.1: it silently drops/reorders keys and mangled the project list
once (projects vanished from the UI). Instead, **raw-text replace only the exact
substring you are changing** so every other byte is preserved:

```powershell
$path = "$env:APPDATA\ai.opencode.desktop\opencode.global.dat"
# back up first
Copy-Item $path "$path.bak-$(Get-Date -f yyyyMMdd-HHmmss)"
$raw = [IO.File]::ReadAllText($path)                          # preserves bytes/encoding
$raw = $raw.Replace($oldExactSubstring, $newExactSubstring)   # targeted, key-preserving
# write WITHOUT a BOM, LF endings -- matches how the app writes these files
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText($path, $raw, $utf8NoBom)
```

Verify unaffected keys are byte-identical afterward (compare against the backup).

### Never write these files with a BOM (the trap we hit)

**`Set-Content -Encoding UTF8` on PowerShell 5.1 prepends a UTF-8 BOM
(`EF BB BF`) and uses CRLF.** The desktop app writes `opencode.global.dat` /
`opencode.window.*.dat` with **no BOM and LF**. A BOM'd file makes the app:

1. fail to parse the file on startup -> empty project sidebar;
2. **refuse to overwrite** the file it could not read -> the write timestamp
   freezes at the moment of your edit, and any project the user re-adds is lost
   on the next launch (the classic "I re-add my projects every time" symptom).

Detect and confirm:

```powershell
$b = [IO.File]::ReadAllBytes($path)
$hasBom = ($b.Length -ge 3 -and $b[0]-eq 0xEF -and $b[1]-eq 0xBB -and $b[2]-eq 0xBF)
```

Fix by rewriting without a BOM (strip the leading 3 bytes, normalize CRLF->LF,
`WriteAllText` with `UTF8Encoding($false)`) — this is exactly what
`scripts/fix-global-bom.ps1` does. Prevent it by always using the
`WriteAllText` + `UTF8Encoding($false)` pattern above, never
`Set-Content -Encoding UTF8`, for any `.dat`/JSON state file.

## PowerShell 5.1 gotchas

- Scripts MUST be all-ASCII. Em-dashes/smart quotes/non-breaking spaces cause
  "missing terminator" tokenizer errors. Validate:
  ```powershell
  $e=$null; [Management.Automation.PSParser]::Tokenize((Get-Content $f -Raw),[ref]$e); $e
  ```
- No `sqlite3.exe` CLI on PATH by default; use Python's built-in `sqlite3`.
- Prefer full cmdlet names; quote all paths with spaces.

## Log signatures cheat sheet

| Log line | Meaning |
|---|---|
| `project copy refresh projectID=<hash>` | app resolved the open dir to project `<hash>` |
| `creating instance` / `bootstrapping` `<dead dir>` | it is spawning the ghost |
| `FileSystem.realPath (...) ENOENT` | the dead worktree does not exist |
| `prompt_async failed ... ENOENT` | session died before reaching the model |
| `session.list ... Path is not absolute` | a corrupt session row (Fix B) |
| `loop -> process -> stream` (in a good dir) | provider/model is healthy; issue is dir-scoped |

## Rollback

Every fix backs up `opencode.db`/`-wal`/`-shm` (or `opencode.global.dat`) to a
timestamped folder under `%LOCALAPPDATA%\Temp\opencode\`. To roll back: quit the
app, copy the backed-up files back over the originals, relaunch.
