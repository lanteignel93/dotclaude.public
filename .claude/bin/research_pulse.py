#!/usr/bin/env python3
"""research_pulse.py — drift-aware status table for work-journal research notes.

Reads frontmatter (topic, status, updated) from every note under
~/work-journal/research/{trading,dev}/ and prints a compact pulse:
active notes sorted stalest-first with days-since-update (flagged past
--drift-days), then one-line rosters for dormant / reference / closed.
Consumed by /briefing (Tuesdays, or any day drift exists) and /week.

--check-paths: for active notes only, verify cited absolute paths
(/..., ~/...) and research/sources/... references still
exist on disk. Missing paths are how citation rot surfaces (a cited
reference can vanish unnoticed for weeks before it was noticed).

Read-only, stdlib only, Python >= 3.8.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

DEFAULT_ROOT = Path.home() / "work-journal" / "research"
DOMAINS = ("trading", "dev")
STATUS_ORDER = ("active", "dormant", "reference", "closed")

# Path segments may embed one-level brace shorthand for citing families of
# snapshots: research/sources/2026-08-20-{es,nq}-...-report.html
_SEG = r"(?:[\w@./+-]|\{[\w@.,/+-]+\})"
PATH_RX = re.compile(r"(?:(?:/[A-Za-z][\w.-]*|~)/" + _SEG + r"+|research/sources/" + _SEG + r"+)")
# Trailing "_" strips the closing italic of "_source: ..._" lines.
TRAILING_JUNK = ".,;:)]}`'\"_"
# Lines carrying this marker are exempt from --check-paths (citations that
# legitimately live on another box, e.g. personal-machine paths).
IGNORE_MARKER = "pulse:ignore"


def parse_frontmatter(text: str) -> dict:
    """Extract topic/status/updated from a leading --- block.

    status and updated may carry trailing '# comment' annotations
    (the notes use them for flip history); topic is taken verbatim.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fm: dict = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = re.match(r"^(topic|status|updated):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if key in ("status", "updated"):
            val = val.split("#", 1)[0].strip()
        fm[key] = val
    return fm


def note_body(text: str) -> str:
    """Everything after the frontmatter block (whole text if none)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[i + 1:])
    return text


def expand_braces(p: str) -> list:
    """{a,b} shorthand -> all concrete paths (recursive over groups)."""
    m = re.search(r"\{([^{}]*)\}", p)
    if not m:
        return [p]
    out = []
    for alt in m.group(1).split(","):
        out.extend(expand_braces(p[:m.start()] + alt + p[m.end():]))
    return out


def cited_paths(body: str) -> list:
    """Unique cited filesystem paths, order-preserved, junk-trimmed."""
    seen, out = set(), []
    for line in body.splitlines():
        if IGNORE_MARKER in line:
            continue
        for raw in PATH_RX.findall(line):
            for p in expand_braces(raw.rstrip(TRAILING_JUNK)):
                if "*" in p or len(p) < 6:
                    continue
                if p not in seen:
                    seen.add(p)
                    out.append(p)
    return out


def resolve(path: str, journal_root: Path) -> Path:
    if path.startswith("~/"):
        return Path.home() / path[2:]
    if path.startswith("research/sources/"):
        return journal_root / path
    return Path(path)


def collect(root: Path, today: dt.date) -> list:
    notes = []
    for domain in DOMAINS:
        d = root / domain
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.md")):
            text = f.read_text(encoding="utf-8")
            fm = parse_frontmatter(text)
            status = fm.get("status", "?").lower() or "?"
            age = None
            try:
                age = (today - dt.date.fromisoformat(fm.get("updated", ""))).days
            except ValueError:
                pass
            notes.append({
                "name": f.stem,
                "domain": domain,
                "status": status,
                "updated": fm.get("updated"),
                "age_days": age,
                "path": str(f),
            })
    return notes


def check_paths(notes: list, journal_root: Path) -> dict:
    """Missing cited paths per active note: {note_name: [missing, ...]}."""
    missing: dict = {}
    for n in notes:
        if n["status"] != "active":
            continue
        body = note_body(Path(n["path"]).read_text(encoding="utf-8"))
        gone = [p for p in cited_paths(body)
                if not resolve(p, journal_root).exists()]
        if gone:
            missing[n["name"]] = gone
    return missing


def render(notes: list, drift_days: int, missing: dict) -> str:
    lines = []
    by_status: dict = {}
    for n in notes:
        by_status.setdefault(n["status"], []).append(n)

    active = sorted(by_status.get("active", []),
                    key=lambda n: -(n["age_days"] if n["age_days"] is not None else 10**6))
    lines.append(f"## Active ({len(active)})")
    if not active:
        lines.append("- none")
    for n in active:
        if n["age_days"] is None:
            age_str, flag = "updated: unparseable", " [FIX FRONTMATTER]"
        else:
            age_str = f"updated {n['age_days']}d ago"
            flag = f" [DRIFT >{drift_days}d]" if n["age_days"] > drift_days else ""
        lines.append(f"- {n['name']} ({n['domain']}): {age_str}{flag}")

    for status in ("dormant", "reference", "closed"):
        group = by_status.get(status, [])
        if group:
            roster = ", ".join(n["name"] for n in group)
            lines.append(f"## {status.capitalize()} ({len(group)}): {roster}")
    other = [n for n in notes if n["status"] not in STATUS_ORDER]
    if other:
        roster = ", ".join(f"{n['name']} [{n['status']}]" for n in other)
        lines.append(f"## Unrecognized status ({len(other)}): {roster}")

    if missing:
        lines.append("## Missing cited paths (active notes)")
        for name, gone in missing.items():
            for p in gone:
                lines.append(f"- {name}: {p}")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT,
                    help="research dir (default: ~/work-journal/research)")
    ap.add_argument("--drift-days", type=int, default=21,
                    help="flag active notes untouched longer than this (default 21)")
    ap.add_argument("--check-paths", action="store_true",
                    help="verify cited paths in active notes still exist")
    ap.add_argument("--today", type=dt.date.fromisoformat, default=dt.date.today(),
                    help="override today (tests)")
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args(argv)

    if not args.root.is_dir():
        print(f"no research dir at {args.root}", file=sys.stderr)
        return 1

    notes = collect(args.root, args.today)
    journal_root = args.root.parent
    missing = check_paths(notes, journal_root) if args.check_paths else {}

    if args.as_json:
        print(json.dumps({"notes": notes, "missing_paths": missing}, indent=2))
    else:
        print(f"# Research pulse — {args.today}")
        print(render(notes, args.drift_days, missing))
    return 0


if __name__ == "__main__":
    sys.exit(main())
