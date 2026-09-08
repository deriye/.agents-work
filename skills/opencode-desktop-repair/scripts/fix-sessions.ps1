#requires -version 5.1
<#
  fix-sessions.ps1  (Fix B - ghost sessions + corrupt session rows)

  Deletes from opencode.db:
    - session rows whose 'directory' references a deleted directory
      (default markers: agents-work, agents-old); these re-bootstrap the ghost
      directory when the app reopens.
    - corrupt session rows: non-UTF8 'directory' or NULL 'path'. These make
      session.list throw "Path is not absolute" so the app hangs on open with
      NO error popup and NO assistant reply.
  For every deleted session it also removes child rows in
  message/part/todo/session_share/session_message/session_input/
  session_context_epoch.

  OpenCode desktop MUST be fully closed (DB is WAL-locked while running).
  Requires Python 3 on PATH.

  Optional: pass extra dead-dir substrings as arguments, e.g.
    powershell -File fix-sessions.ps1 my-old-folder
#>
$ErrorActionPreference = 'Stop'

$dbDir  = Join-Path $env:USERPROFILE '.local\share\opencode'
$db     = Join-Path $dbDir 'opencode.db'
$stamp  = Get-Date -Format 'yyyyMMdd-HHmmss'
$bakDir = Join-Path $env:LOCALAPPDATA "Temp\opencode\sessions-fix-$stamp"

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

cur.execute("SELECT id, directory, path FROM session")
targets = set()
for sid, d, p in cur.fetchall():
    sid_s, d_s = txt(sid), txt(d)
    reason = None
    if dead(d_s):
        reason = "dead-dir"
    else:
        bad = False
        try:
            if isinstance(d, bytes): d.decode("utf-8")
            if isinstance(p, bytes): p.decode("utf-8")
        except Exception:
            bad = True
        if "\ufffd" in d_s or bad or p is None:
            reason = "corrupt"
    if reason:
        targets.add(sid_s); print(f"target session ({reason}): {sid_s} dir={d_s!r} path={txt(p)!r}")

if not targets:
    print("No ghost/corrupt sessions found. Nothing to do."); con.close(); sys.exit(0)

sess = list(targets); sph = ",".join("?"*len(sess))
cur.execute("BEGIN")
for tbl in ('message','part','todo','session_share','session_message','session_input','session_context_epoch'):
    try:
        cur.execute(f"DELETE FROM {tbl} WHERE session_id IN ({sph})", sess); print(f"deleted {tbl}: {cur.rowcount}")
    except sqlite3.OperationalError as e:
        print(f"skip {tbl}: {e}")
cur.execute(f"DELETE FROM session WHERE id IN ({sph})", sess); print("deleted session:", cur.rowcount)
con.commit()

remaining = " OR ".join(["directory LIKE ?"]*len(markers))
cur.execute(f"SELECT COUNT(*) FROM session WHERE {remaining}", [f"%{m}%" for m in markers])
print("remaining dead-dir sessions:", cur.fetchone()[0])
cur.execute("PRAGMA integrity_check"); ic=cur.fetchone()[0]; print("integrity_check:", txt(ic))
cur.execute("PRAGMA foreign_key_check"); print("foreign_key_check violations:", len(cur.fetchall()))
cur.execute("PRAGMA wal_checkpoint(TRUNCATE)"); con.commit(); con.close(); print("OK")
'@
$pyTmp = Join-Path $env:LOCALAPPDATA 'Temp\opencode\_sessions_cleanup.py'
Set-Content -Path $pyTmp -Value $pyScript -Encoding UTF8

Write-Host "==> Running session cleanup..." -ForegroundColor Cyan
& $py.Source $pyTmp $db @args
if ($LASTEXITCODE -ne 0) {
  Write-Host "ERROR: cleanup failed. Restore from backup if needed: $bakDir" -ForegroundColor Red; exit 1
}
Write-Host ""
Write-Host "DONE. Relaunch OpenCode desktop and open the project." -ForegroundColor Green
Write-Host ("Backup: " + $bakDir) -ForegroundColor DarkGray
