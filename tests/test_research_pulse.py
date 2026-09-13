#!/usr/bin/env python3
"""Test suite for .claude/bin/research_pulse.py — run: python tests/test_research_pulse.py"""

import datetime as dt
import io
import os
import sys
import tempfile
import traceback
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", ".claude", "bin")))

import research_pulse as rp  # noqa: E402

TODAY = dt.date(2026, 8, 25)

NOTE_ACTIVE = """---
topic: ES-anchor spread TV
status: active
sources:
  - meeting 2026-08-17
updated: 2026-08-20
---

# Body

Cited: /data/example/exists.csv and research/sources/2026-08-20-x.pdf.
Also ~/work-journal/tasks.md, plus a glob /data/example/*.parquet (skipped).
Braces: research/sources/2026-08-20-{es,nq}-{a,b}-rep.html
Personal box: ~/github/cpp_practice/spsc/tmp.cpp <!-- pulse:ignore -->

_source: snapshotted research/sources/2026-08-20-x.pdf_
"""

NOTE_DRIFTED = """---
topic: Signal lead-lag study
status: active  # consultant track
updated: 2026-07-20
---
body
"""

NOTE_DORMANT = """---
topic: Pairs study
status: dormant  # flipped 2026-08-25
updated: 2026-08-06
---
body
"""

NOTE_BAD_DATE = """---
topic: Broken frontmatter
status: active
updated: soonish
---
body
"""


def make_tree(tmp):
    root = Path(tmp) / "research"
    (root / "trading").mkdir(parents=True)
    (root / "dev").mkdir()
    (root / "trading" / "es-anchor.md").write_text(NOTE_ACTIVE, encoding="utf-8")
    (root / "trading" / "signal-lag.md").write_text(NOTE_DRIFTED, encoding="utf-8")
    (root / "trading" / "pairs-study.md").write_text(NOTE_DORMANT, encoding="utf-8")
    (root / "dev" / "broken.md").write_text(NOTE_BAD_DATE, encoding="utf-8")
    (root / "sources").mkdir()
    (root / "sources" / "2026-08-20-x.pdf").write_text("x", encoding="utf-8")
    return root


def test_frontmatter_strips_status_comment():
    fm = rp.parse_frontmatter(NOTE_DORMANT)
    assert fm["status"] == "dormant", fm
    assert fm["updated"] == "2026-08-06", fm
    assert fm["topic"] == "Pairs study", fm


def test_no_frontmatter_is_empty():
    assert rp.parse_frontmatter("# just a body\n") == {}


def test_collect_ages_and_statuses():
    with tempfile.TemporaryDirectory() as tmp:
        notes = rp.collect(make_tree(tmp), TODAY)
    by = {n["name"]: n for n in notes}
    assert by["es-anchor"]["age_days"] == 5, by["es-anchor"]
    assert by["signal-lag"]["age_days"] == 36
    assert by["broken"]["age_days"] is None
    assert by["pairs-study"]["status"] == "dormant"


def test_cited_paths_trim_and_skip_globs():
    body = rp.note_body(NOTE_ACTIVE)
    paths = rp.cited_paths(body)
    assert "/data/example/exists.csv" in paths, paths
    assert "research/sources/2026-08-20-x.pdf" in paths, paths
    assert "~/work-journal/tasks.md" in paths, paths
    assert not any("*" in p for p in paths), paths
    assert not any(p.endswith("_") for p in paths), paths


def test_brace_expansion():
    assert rp.expand_braces("a-{es,nq}-{1,2}.html") == [
        "a-es-1.html", "a-es-2.html", "a-nq-1.html", "a-nq-2.html"]
    body = rp.note_body(NOTE_ACTIVE)
    paths = rp.cited_paths(body)
    assert "research/sources/2026-08-20-es-a-rep.html" in paths, paths
    assert "research/sources/2026-08-20-nq-b-rep.html" in paths, paths
    assert not any("{" in p for p in paths), paths


def test_pulse_ignore_marker_skips_line():
    body = rp.note_body(NOTE_ACTIVE)
    paths = rp.cited_paths(body)
    assert not any("cpp_practice" in p for p in paths), paths


def test_check_paths_flags_only_missing_in_active():
    with tempfile.TemporaryDirectory() as tmp:
        root = make_tree(tmp)
        notes = rp.collect(root, TODAY)
        missing = rp.check_paths(notes, root.parent)
    gone = missing.get("es-anchor", [])
    assert "/data/example/exists.csv" in gone, missing  # not on test box
    assert "research/sources/2026-08-20-x.pdf" not in gone, missing  # created
    assert "pairs-study" not in missing  # dormant notes not checked


def test_render_drift_flag_boundary():
    with tempfile.TemporaryDirectory() as tmp:
        notes = rp.collect(make_tree(tmp), TODAY)
    out = rp.render(notes, 21, {})
    assert "signal-lag (trading): updated 36d ago [DRIFT >21d]" in out, out
    assert "es-anchor (trading): updated 5d ago\n" in out + "\n", out
    assert "[FIX FRONTMATTER]" in out, out
    assert "Dormant (1): pairs-study" in out, out


def test_main_json_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        root = make_tree(tmp)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = rp.main(["--root", str(root), "--today", "2026-08-25", "--json"])
    assert rc == 0
    import json
    data = json.loads(buf.getvalue())
    assert len(data["notes"]) == 4, data


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
