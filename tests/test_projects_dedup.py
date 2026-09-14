"""Tests for projects_dedup.py — newest-wins repair of projects.md."""
import subprocess
import sys
import tempfile
from pathlib import Path

ENGINE = Path(__file__).resolve().parent.parent / ".claude/bin/projects_dedup.py"

CLEAN = """# Projects

Preamble line.

## alpha — active
- **thread:** doing alpha things
- **next:** more alpha
- _updated 2026-09-10_

## beta — active
- **aka:** beta-checkout
- **thread:** beta thread
- **next:** beta next
- _updated 2026-09-12_

## Archive

## old-thing — archived
- **thread:** ancient
- _updated 2026-01-01_
"""

INTERLEAVED = """# Projects

## alpha — active
- **aka:** alpha-alt
- **thread:** OLD thread text
- **next:** old next
- _updated 2026-09-01_
- **thread:** NEW thread text
- **next:** new next
- _updated 2026-09-12_

## Archive
"""

DUP_BLOCKS = """# Projects

## alpha — active
- **thread:** old copy
- _updated 2026-09-01_

## alpha — active
- **thread:** new copy
- _updated 2026-09-12_

## Archive
"""

AMBIGUOUS = """# Projects

## alpha — active
- **thread:** one
- _updated 2026-09-01_
- _updated 2026-09-12_

## Archive
"""


def run(text, *extra):
    d = tempfile.mkdtemp()
    f = Path(d) / "projects.md"
    f.write_text(text)
    out = subprocess.run(
        [sys.executable, str(ENGINE), str(f), *extra],
        capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    return f.read_text(), out.stdout


def test_clean_untouched():
    after, out = run(CLEAN)
    assert after == CLEAN
    assert "clean" in out


def test_interleaved_newest_wins():
    after, out = run(INTERLEAVED)
    assert "NEW thread text" in after
    assert "OLD thread text" not in after
    assert "- **aka:** alpha-alt" in after
    assert "repaired: alpha" in out


def test_duplicate_blocks_newest_wins():
    after, out = run(DUP_BLOCKS)
    assert "new copy" in after and "old copy" not in after
    assert after.count("## alpha") == 1
    assert "duplicate block alpha" in out


def test_ambiguous_left_untouched():
    after, out = run(AMBIGUOUS)
    assert after == AMBIGUOUS
    assert "ambiguous" in out


def test_check_mode_no_write():
    after, out = run(INTERLEAVED, "--check")
    assert "OLD thread text" in after  # unchanged on disk
    assert "not written" in out


def test_baseline_restores_backward_revert():
    d = tempfile.mkdtemp()
    f = Path(d) / "projects.md"
    b = Path(d) / "pre-sync"
    reverted = CLEAN.replace("doing alpha things", "STALE alpha") \
                    .replace("_updated 2026-09-10_", "_updated 2026-08-27_")
    f.write_text(reverted)
    b.write_text(CLEAN)
    out = subprocess.run([sys.executable, str(ENGINE), str(f),
                          "--baseline", str(b)],
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    after = f.read_text()
    assert "doing alpha things" in after
    assert "STALE alpha" not in after
    assert "backward" in out.stdout


def test_baseline_older_untouched():
    d = tempfile.mkdtemp()
    f = Path(d) / "projects.md"
    b = Path(d) / "pre-sync"
    f.write_text(CLEAN)
    older = CLEAN.replace("_updated 2026-09-10_", "_updated 2026-08-01_")
    b.write_text(older)
    subprocess.run([sys.executable, str(ENGINE), str(f),
                    "--baseline", str(b)], capture_output=True, text=True)
    assert f.read_text() == CLEAN


def test_archive_untouched():
    after, _ = run(CLEAN)
    assert "## old-thing — archived" in after


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
