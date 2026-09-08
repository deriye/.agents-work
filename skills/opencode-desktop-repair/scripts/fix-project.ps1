#requires -version 5.1
<#
  fix-project.ps1  (Fix A - poisoned project row)

  Removes any 'project' row in opencode.db whose worktree references a deleted
  directory (default markers: agents-work, agents-old), along with its
  project_directory / workspace / session (+message/part/...) children. The
  clean project row for the real directory is left intact.

  This is the usual root cause: a duplicate project for the same git repo where
  one row's worktree points at a dead dir but its sandboxes reference the good
  dir, so opening the good dir bootstraps the dead worktree -> ENOENT -> hang.

  OpenCode desktop MUST be fully closed (DB is WAL-locked while running).
  Requires Python 3 on PATH.

  Optional: pass extra dead-dir substrings as arguments, e.g.
    powershell -File fix-project.ps1 my-old-folder
#>
$ErrorActionPreference = 'Stop'
$extraMarkers = $args  # optional extra substrings

$dbDir  = Join-Path $env:USERPROFILE '.local\share\opencode'
$db     = Join-Path $dbDir 'opencode.db'
$stamp  = Get-Date -Format 'yyyyMMdd-HHmmss'
$bakDir = Join-Path $env:LOCALAPPDATA "Temp\opencode\project-fix-$stamp"

Write-Host "==> Checking OpenCode desktop is closed..." -ForegroundColor Cyan
if (Get-Process OpenCode -ErrorAction SilentlyContinue) {
  Write-Host "ERROR: OpenCode is still running. Fully quit it and re-run." -ForegroundColor Red; exit 1
}
if (-not (Test-Path $db)) { Write-Host "ERROR: $db not found" -ForegroundColor Red; exit 1 }
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { Write-Host "ERROR: python not on PATH." -ForegroundColor Red; exit 1 }

New-Item -ItemType Directory -Path $bakDir -Force | Out-Null
foreach ($f in 'opencode.db','opencode.db-wal','opencode.db-shm') {
  $s = Join-Path $dbDir $f; if (Test-Path $s) { Copy-Item $s (Join-Path $bakDir $f) -Force }
}
Write-Host "==> Backup: $bakDir" -ForegroundColor Green

$pyScript = @'
import sqlite3, sys
db = sys.argv[1]
markers = ["agents-work", "agents-old"] + sys.argv[2:]
con = sqlite3.connect(db); con.text_factory = bytes; cur = con.cursor()
cur.execute("PRAGMA wal_checkpoint(TRUNCATE)")

def txt(v):
    return "" if v is None else (v.decode("utf-8","replace") if isinstance(v,bytes) else str(v))
def dead(s):
    return any(m in s for m in markers)

cur.execute("SELECT id, worktree, name FROM project")
bad = []
for pid, wt, nm in cur.fetchall():
    if dead(txt(wt)):
        bad.append(txt(pid)); print(f"poisoned project: id={txt(pid)} worktree={txt(wt)} name={txt(nm)}")
if not bad:
    print("No poisoned project rows found. Nothing to do."); con.close(); sys.exit(0)

ph = ",".join("?"*len(bad))
cur.execute(f"SELECT id FROM session WHERE project_id IN ({ph})", bad)
sess = [txt(r[0]) for r in cur.fetchall()]
print("sessions under poisoned projects:", len(sess))

cur.execute("BEGIN")
if sess:
    sph = ",".join("?"*len(sess))
    for tbl in ('message','part','todo','session_share','session_message','session_input','session_context_epoch'):
        try:
            cur.execute(f"DELETE FROM {tbl} WHERE session_id IN ({sph})", sess); print(f"  deleted {tbl}: {cur.rowcount}")
        except sqlite3.OperationalError as e:
            print(f"  skip {tbl}: {e}")
    cur.execute(f"DELETE FROM session WHERE id IN ({sph})", sess); print("  deleted session:", cur.rowcount)
for tbl in ('project_directory','workspace'):
    try:
        cur.execute(f"DELETE FROM {tbl} WHERE project_id IN ({ph})", bad); print(f"deleted {tbl}: {cur.rowcount}")
    except sqlite3.OperationalError as e:
        print(f"skip {tbl}: {e}")
cur.execute(f"DELETE FROM project WHERE id IN ({ph})", bad); print("deleted project:", cur.rowcount)
con.commit()

remaining = " OR ".join(["worktree LIKE ?"]*len(markers))
cur.execute(f"SELECT COUNT(*) FROM project WHERE {remaining}", [f"%{m}%" for m in markers])
print("remaining poisoned projects:", cur.fetchone()[0])
cur.execute("PRAGMA integrity_check"); ic=cur.fetchone()[0]; print("integrity_check:", txt(ic))
cur.execute("PRAGMA foreign_key_check"); print("foreign_key_check violations:", len(cur.fetchall()))
cur.execute("PRAGMA wal_checkpoint(TRUNCATE)"); con.commit(); con.close(); print("OK")
'@
$pyTmp = Join-Path $env:LOCALAPPDATA 'Temp\opencode\_project_cleanup.py'
Set-Content -Path $pyTmp -Value $pyScript -Encoding UTF8

Write-Host "==> Running project cleanup..." -ForegroundColor Cyan
& $py.Source $pyTmp $db @extraMarkers
if ($LASTEXITCODE -ne 0) {
  Write-Host "ERROR: cleanup failed. Restore from backup if needed: $bakDir" -ForegroundColor Red; exit 1
}
Write-Host ""
Write-Host "DONE. Relaunch OpenCode desktop and open the project." -ForegroundColor Green
Write-Host ("Backup: " + $bakDir) -ForegroundColor DarkGray
