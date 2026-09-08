#!/usr/bin/env python3
"""Read-only diagnosis of OpenCode desktop's opencode.db.

Usage:
    python inspect_db.py <path-to-opencode.db>

Reports:
  * project rows whose worktree references a deleted directory (the usual root
    cause: a duplicate project for the same git repo pointing at a dead worktree)
  * session rows bound to a dead directory (re-bootstrap the ghost on open)
  * corrupt session rows (non-UTF8 directory / NULL path) that break session.list

Operate on a COPY of the DB; do not point this at the live file while the app
is running. Read-only: it never writes.
"""
import sqlite3
import sys

# Substrings that indicate a deleted/renamed directory. Extend as needed.
DEAD_MARKERS = ("agents-work", "agents-old")


def txt(v):
    if v is None:
        return ""
    if isinstance(v, bytes):
        return v.decode("utf-8", "replace")
    return str(v)


def is_dead(s):
    return any(m in s for m in DEAD_MARKERS)


def main(db):
    con = sqlite3.connect(db)
    con.text_factory = bytes
    cur = con.cursor()

    print("=== PROJECT rows ===")
    cur.execute("SELECT id, worktree, name, sandboxes FROM project")
    projects = cur.fetchall()
    poisoned = []
    for pid, wt, nm, sb in projects:
        pid_s, wt_s, nm_s, sb_s = txt(pid), txt(wt), txt(nm), txt(sb)
        flag = ""
        if is_dead(wt_s):
            flag = "   <<< POISONED (worktree is a dead dir)"
            poisoned.append(pid_s)
        print(f"  id={pid_s}")
        print(f"     worktree={wt_s}  name={nm_s}{flag}")
        if sb_s and sb_s not in ("[]", "None"):
            print(f"     sandboxes={sb_s}")
    print(f"\n  poisoned projects: {len(poisoned)}")

    print("\n=== SESSION rows referencing dead dirs / corrupt ===")
    cur.execute("SELECT id, project_id, directory, path, title FROM session")
    dead, corrupt = [], []
    for sid, pjid, d, p, t in cur.fetchall():
        sid_s, d_s = txt(sid), txt(d)
        if is_dead(d_s):
            dead.append(sid_s)
        bad = False
        try:
            if isinstance(d, bytes):
                d.decode("utf-8")
            if isinstance(p, bytes):
                p.decode("utf-8")
        except Exception:
            bad = True
        if "\ufffd" in d_s or bad:
            corrupt.append((sid_s, repr(d), repr(p), txt(t)))
    print(f"  dead-dir sessions: {len(dead)}")
    for s in dead[:40]:
        print(f"    {s}")
    print(f"  corrupt sessions: {len(corrupt)}")
    for s, dr, pr, t in corrupt[:40]:
        print(f"    {s}  dir(raw)={dr} path(raw)={pr} title={t}")

    print("\n=== project_directory referencing dead / duplicate dirs ===")
    cur.execute("SELECT project_id, directory FROM project_directory")
    for pjid, d in cur.fetchall():
        d_s = txt(d)
        if is_dead(d_s) or txt(pjid) in poisoned:
            print(f"  project_id={txt(pjid)} directory={d_s}")

    print("\n=== SUMMARY / suggested fixes ===")
    if poisoned:
        print(f"  -> run fix-project.ps1 (removes {len(poisoned)} poisoned project row(s))")
    if dead or corrupt:
        print(f"  -> run fix-sessions.ps1 ({len(dead)} ghost + {len(corrupt)} corrupt session row(s))")
    if not (poisoned or dead or corrupt):
        print("  DB looks clean. Check opencode.global.dat (server.lastProject / layout.handoff).")

    con.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python inspect_db.py <path-to-opencode.db>")
        sys.exit(2)
    main(sys.argv[1])
