#!/usr/bin/env python3
"""Test suite for .claude/bin/session_context.py — run: python tests/test_session_context.py"""

import json
import os
import sys
import traceback

sys.path.insert(0, os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", ".claude", "bin")))

import session_context as sc  # noqa: E402

PROJECTS_MD = """# Projects

Intro prose.

## acme-core — active
- **aka:** acme-core-checkout
- **thread:** alpha-sidecar productionization
- **next:** systemd-ize, cut release
- _updated 2026-08-25_

## pipeline-x — active
- **thread:** RV proposal
- _updated 2026-08-25_
"""

LOG_MONDAY = """# 2026-08-24

## 09:21 — onesystem (manual /journal)

**cwd:** `/mnt/flashdata/onedte_trading/onesystem`

### Next
- wrong project, should not match

## 11:51 — core / prod incident (manual /journal)

**cwd:** `/data/example/acme-core` (no git)

### What was done
- incident handled

### Next
- verify Sunday weekly cleanup
- patch Session.hpp

## 16:19 — acme-core (manual /journal)

**cwd:** `~/checkouts/acme-core`

### What was done
- sidecar day 2

### Next
- monitor sidecar overnight

### Open / blocked
- waiting on a teammate for fleet page
"""

LOG_SUNDAY = """# 2026-08-23

## 10:00 — acme-core (manual /journal)

**cwd:** `~/checkouts/acme-core`

### Next
- stale item from Sunday, must not win over Monday
"""

HOME = "/home/tester"


def test_find_project_block():
    block = sc.find_project_block(PROJECTS_MD, "acme-core")
    assert block.startswith("## acme-core — active"), block
    assert "alpha-sidecar" in block
    assert "pipeline-x" not in block
    assert sc.find_project_block(PROJECTS_MD, "nonexistent") == ""


def test_block_match_is_exact_slug():
    assert sc.find_project_block(PROJECTS_MD, "core") == ""  # substring of slug must not match
    assert sc.find_project_block(PROJECTS_MD, "ACME-CORE") != ""


def test_block_match_via_aka():
    block = sc.find_project_block(PROJECTS_MD, "acme-core-checkout")
    assert "alpha-sidecar" in block, block
    assert sc.find_project_block(PROJECTS_MD, "checkout") == ""


def test_entry_matches_by_cwd_under_root():
    entry = ["## 16:19 — someothername (manual /journal)", "",
             "**cwd:** `~/checkouts/acme-core/subdir`"]
    assert sc.entry_matches(entry, "zzz", HOME + "/checkouts/acme-core", HOME)
    assert not sc.entry_matches(entry, "zzz", HOME + "/checkouts/other", HOME)


def test_entry_matches_by_header_project():
    entry = ["## 11:51 — core / prod incident (manual /journal)"]
    assert sc.entry_matches(entry, "core", None, HOME)
    assert not sc.entry_matches(entry, "otherproj", None, HOME)


def test_continuity_newest_entry_wins():
    logs = [("2026-08-24", LOG_MONDAY), ("2026-08-23", LOG_SUNDAY)]
    date, lines = sc.find_continuity(
        logs, "acme-core", HOME + "/checkouts/acme-core", HOME)
    assert date == "2026-08-24", (date, lines)
    assert "- monitor sidecar overnight" in lines, lines
    assert "Open/blocked:" in lines, lines
    assert "- waiting on a teammate for fleet page" in lines, lines
    assert not any("stale item" in ln for ln in lines), lines
    assert not any("wrong project" in ln for ln in lines), lines


def test_continuity_no_match_is_empty():
    logs = [("2026-08-24", LOG_MONDAY)]
    date, lines = sc.find_continuity(logs, "unrelated", None, HOME)
    assert date is None and lines == [], (date, lines)


def test_extract_drops_empty_section_labels():
    entry = ["## 10:00 — x (manual /journal)",
             "### Next", "### Open / blocked", "- blocked on y"]
    lines = sc.extract_next_open(entry)
    assert lines == ["Open/blocked:", "- blocked on y"], lines


def test_compose_and_envelope():
    ctx = sc.compose("TASKS", "acme-core", "## acme-core — active",
                     "2026-08-24", ["Next:", "- x"])
    assert ctx.startswith("TASKS\n\n=== PROJECT STATE"), ctx
    assert "=== CONTINUITY (2026-08-24 journal — acme-core) ===" in ctx
    assert sc.compose("", "p", "", None, []) == ""


def test_main_silent_when_nothing(monkey_home_missing=None):
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    old_home = os.environ.get("HOME")
    os.environ["HOME"] = "/nonexistent-home-for-test"
    try:
        with redirect_stdout(buf):
            rc = sc.main(["--tasks-json", "", "--cwd", "/tmp"])
    finally:
        if old_home is not None:
            os.environ["HOME"] = old_home
    assert rc == 0
    assert buf.getvalue() == "", buf.getvalue()


def test_main_passes_tasks_through():
    import io
    from contextlib import redirect_stdout
    tasks = json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart", "additionalContext": "TASKBLOCK"}})
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = sc.main(["--tasks-json", tasks, "--cwd", "/tmp"])
    assert rc == 0
    out = json.loads(buf.getvalue())
    assert "TASKBLOCK" in out["hookSpecificOutput"]["additionalContext"]


def main():
    fns = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_")]
    failures = 0
    for name, fn in fns:
        try:
            fn()
            print("PASS  " + name)
        except Exception:
            failures += 1
            print("FAIL  " + name)
            traceback.print_exc()
    print("\n{} passed, {} failed, {} total".format(
        len(fns) - failures, failures, len(fns)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
