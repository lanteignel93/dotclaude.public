#!/usr/bin/env python3
"""tasks_dedup.py — collapse union-merge ghost duplicates in tasks.md.

The failure mode (observed 2026-08-07 / 2026-08-10): a task line edited in
place on both boxes survives the union merge twice — typically the open
copy on one box and the closed (checked/stamped) copy on the other. This
pass removes ONLY provable ghosts; anything ambiguous is left alone and
reported.

Ghost definition (conservative, all conditions required):
  * two lines in the SAME section
  * whose text is identical after stripping the checkbox status and any
    completion stamp (checkmark/cross emoji + date)
  * where at most one distinct completion state exists among them
  * and none of the lines carries a recurrence marker (recurring tasks
    legitimately re-spawn the same text; never touched)

Resolution: keep the most-advanced line (closed beats in-progress beats
open); for exact byte-identical duplicates keep one. Everything else —
including same-text lines in different sections — is untouched.

Usage: tasks_dedup.py [--dry-run] [path-to-tasks.md]
Exit 0 = clean or fixed; prints one line per action.
"""
import re
import sys

RECUR = "\U0001F501"  # recurrence emoji
DONE_STAMP = re.compile(r"\s*[✅❌]\s*\d{4}-\d{2}-\d{2}")
CHECKBOX = re.compile(r"^- \[(.)\]\s*")
RANK = {"x": 3, "-": 3, "/": 2, " ": 1}


def core(line: str) -> str:
    """Normalized identity: text minus status minus completion stamp."""
    m = CHECKBOX.match(line)
    body = line[m.end():] if m else line
    body = DONE_STAMP.sub("", body)
    return " ".join(body.split())


def status(line: str) -> str:
    m = CHECKBOX.match(line)
    return m.group(1) if m else " "


def dedup(lines: list[str]) -> tuple[list[str], list[str]]:
    out: list[str] = []
    actions: list[str] = []
    section = ""
    # first pass: index task lines by (section, core)
    groups: dict[tuple[str, str], list[int]] = {}
    sections: list[str] = []
    for i, line in enumerate(lines):
        if line.startswith("## "):
            section = line.strip()
        sections.append(section)
        if line.startswith("- [") and RECUR not in line:
            groups.setdefault((section, core(line)), []).append(i)

    drop: set[int] = set()
    for (_, _), idxs in groups.items():
        if len(idxs) < 2:
            continue
        # exact-duplicate lines: keep first occurrence
        seen_exact: dict[str, int] = {}
        for i in idxs:
            key = lines[i].rstrip()
            if key in seen_exact:
                drop.add(i)
                actions.append(f"drop exact dup L{i+1}: {key[:70]}")
            else:
                seen_exact[key] = i
        # status-divergent ghosts: keep the most advanced, drop the rest
        live = [i for i in idxs if i not in drop]
        if len(live) > 1:
            ranked = sorted(live, key=lambda i: (RANK.get(status(lines[i]), 0), i))
            keep = ranked[-1]
            for i in ranked[:-1]:
                # only drop if strictly less advanced (never tie-break guesses)
                if RANK.get(status(lines[i]), 0) < RANK.get(status(lines[keep]), 0):
                    drop.add(i)
                    actions.append(
                        f"drop ghost L{i+1} [{status(lines[i])}] kept L{keep+1} "
                        f"[{status(lines[keep])}]: {core(lines[i])[:60]}"
                    )
    out = [l for i, l in enumerate(lines) if i not in drop]
    return out, actions


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    dry = "--dry-run" in sys.argv
    path = args[0] if args else f"{__import__('os').path.expanduser('~')}/work-journal/tasks.md"
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    out, actions = dedup(lines)
    for a in actions:
        print(a)
    if not actions:
        print("clean — no ghosts")
        return 0
    if dry:
        print(f"dry-run: would remove {len(lines) - len(out)} line(s)")
        return 0
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print(f"removed {len(lines) - len(out)} line(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
