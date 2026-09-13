#!/usr/bin/env python3
"""session_context.py — SessionStart context: tasks + project block + continuity.

Called by hooks/session-start-tasks.sh. Composes the additionalContext a
session boots with:

  1. the due-tasks block (passed in via --tasks-json, produced by
     tasks.py hook-context — unchanged behavior),
  2. the ~/work-journal/projects.md block matching the repo this session
     opened in (cross-project dashboard state),
  3. continuity: the newest daily-log entry for this repo that carries
     "### Next" / "### Open / blocked" bullets — what the previous
     session said comes next.

Harness payload arrives on stdin (JSON with "cwd"); fall back to the
process cwd. Every gate fails silent: no journal, no git, no match — the
section is simply absent. Output: the SessionStart hook JSON envelope,
or nothing at all if there is no context to inject.

Read-only, stdlib only, Python >= 3.8.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

LOOKBACK_DAYS = 7
BLOCK_CAP = 15
CONTINUITY_CAP = 12

CWD_LINE_RX = re.compile(r"^\*\*cwd:\*\*\s*`([^`]+)`")
HEADER_PROJECT_RX = re.compile(r"^##\s+(?:\d{2}:\d{2}\s+—\s+)?([^(]+?)(?:\s*\(|$)")


def repo_identity(cwd: str) -> tuple:
    """(project_name, repo_root or None) for the session's cwd."""
    try:
        root = subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip()
    except Exception:
        root = ""
    if root:
        return Path(root).name, root
    return Path(cwd).name, None


AKA_RX = re.compile(r"\*\*aka:\*\*\s*(.+)$")


def find_project_block(text: str, project: str) -> str:
    """The '## <slug> — ...' block for project, capped, or ''.

    A block matches on its header slug, or on any name in its
    '- **aka:** name1, name2' line — checkout basenames vary per box
    (the same repo may have different checkout names per machine).
    """
    proj = project.lower()
    blocks: list = []
    cur: list = []
    for line in text.splitlines():
        if line.startswith("## "):
            if cur:
                blocks.append(cur)
            cur = [line]
        elif cur:
            cur.append(line)
    if cur:
        blocks.append(cur)

    for block in blocks:
        slug = block[0][3:].split("—", 1)[0].strip().lower()
        akas: list = []
        for line in block[1:]:
            m = AKA_RX.search(line)
            if m:
                akas = [a.strip().lower() for a in m.group(1).split(",")]
                break
        if proj == slug or proj in akas:
            out = list(block)
            while out and not out[-1].strip():
                out.pop()
            return "\n".join(out[:BLOCK_CAP])
    return ""


def entry_matches(entry_lines: list, project: str, repo_root, home: str) -> bool:
    """Does a journal entry belong to this project?

    Primary: its **cwd:** path sits at/under the repo root. Fallback:
    the header's project segment (before any ' / ' qualifier) equals
    the project name.
    """
    header = entry_lines[0]
    m = HEADER_PROJECT_RX.match(header)
    if m:
        head_proj = m.group(1).split("/", 1)[0].strip().lower()
        if head_proj == project.lower():
            return True
    if repo_root:
        for line in entry_lines[1:6]:
            cm = CWD_LINE_RX.match(line.strip())
            if cm:
                p = cm.group(1)
                if p.startswith("~"):
                    p = home + p[1:]
                p = os.path.normpath(p)
                root = os.path.normpath(repo_root)
                return p == root or p.startswith(root + os.sep)
    return False


def extract_next_open(entry_lines: list) -> list:
    """Bullets under '### Next' and '### Open / blocked', labeled."""
    out: list = []
    section = None
    for line in entry_lines[1:]:  # [0] is the entry's own '## ' header
        if line.startswith("### "):
            title = line[4:].strip().lower()
            if title.startswith("next"):
                section = "Next"
                out.append("Next:")
            elif title.startswith("open"):
                section = "Open/blocked"
                out.append("Open/blocked:")
            else:
                section = None
            continue
        if line.startswith("## "):
            break
        if section and line.lstrip().startswith("-"):
            out.append(line.rstrip())
    # Drop labels that collected no bullets.
    cleaned: list = []
    for i, line in enumerate(out):
        if line.endswith(":") and (i + 1 >= len(out) or out[i + 1].endswith(":")):
            continue
        cleaned.append(line)
    return cleaned


def split_entries(text: str) -> list:
    """A daily log as a list of entries (each a list of lines)."""
    entries: list = []
    cur: list = []
    for line in text.splitlines():
        if line.startswith("## "):
            if cur:
                entries.append(cur)
            cur = [line]
        elif cur:
            cur.append(line)
    if cur:
        entries.append(cur)
    return entries


def find_continuity(daily_logs: list, project: str, repo_root, home: str) -> tuple:
    """(date_str, bullet lines) from the newest matching entry with content.

    daily_logs: [(date_str, text)] newest first; entries within a file are
    scanned last-first.
    """
    for date_str, text in daily_logs:
        for entry in reversed(split_entries(text)):
            if not entry_matches(entry, project, repo_root, home):
                continue
            bullets = extract_next_open(entry)
            if bullets:
                return date_str, bullets[:CONTINUITY_CAP]
    return None, []


def load_recent_logs(journal: Path, today: dt.date) -> list:
    out: list = []
    for i in range(LOOKBACK_DAYS + 1):
        d = today - dt.timedelta(days=i)
        f = journal / "daily_logs" / (d.isoformat() + ".md")
        if f.is_file():
            try:
                out.append((d.isoformat(), f.read_text(encoding="utf-8")))
            except OSError:
                pass
    return out


def compose(base: str, project: str, block: str, cont_date, cont_lines: list) -> str:
    parts = [p for p in [base] if p]
    if block:
        parts.append("=== PROJECT STATE (~/work-journal/projects.md — %s) ===\n%s"
                      % (project, block))
    if cont_lines:
        parts.append("=== CONTINUITY (%s journal — %s) ===\n%s"
                      % (cont_date, project, "\n".join(cont_lines)))
    return "\n\n".join(parts)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks-json", default="",
                    help="hook-context JSON from tasks.py (may be empty)")
    ap.add_argument("--cwd", default=None, help="override cwd (tests)")
    args = ap.parse_args(argv)

    base = ""
    if args.tasks_json.strip():
        try:
            base = (json.loads(args.tasks_json)
                    .get("hookSpecificOutput", {})
                    .get("additionalContext", ""))
        except (json.JSONDecodeError, AttributeError):
            pass

    cwd = args.cwd
    if cwd is None:
        try:
            payload = json.loads(sys.stdin.read() or "{}")
            cwd = payload.get("cwd") or os.getcwd()
        except (json.JSONDecodeError, OSError):
            cwd = os.getcwd()

    home = str(Path.home())
    journal = Path.home() / "work-journal"
    block, cont_date, cont_lines, project = "", None, [], ""
    if journal.is_dir():
        project, repo_root = repo_identity(cwd)
        pf = journal / "projects.md"
        if pf.is_file():
            block = find_project_block(pf.read_text(encoding="utf-8"), project)
        logs = load_recent_logs(journal, dt.date.today())
        cont_date, cont_lines = find_continuity(logs, project, repo_root, home)

    ctx = compose(base, project, block, cont_date, cont_lines)
    if ctx:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": ctx,
        }}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
