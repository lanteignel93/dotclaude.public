#!/usr/bin/env python3
"""projects_dedup.py — newest-wins repair for projects.md after union merges.

Two failure modes this fixes (both observed in production, 4 clobbers of
one block between 2026-09-01 and 2026-09-14):

1. UNION GHOSTS: git's union merge driver keeps both sides' lines, so a
   block edited on two boxes can end up with two interleaved versions
   (duplicate `- **thread:**` / `_updated` lines). Repair: when a block
   splits cleanly into exactly two candidates, keep the one with the newer
   `_updated` date. Anything messier is left untouched and reported.

2. BACKWARD REVERTS: a stale writer (another box's session holding an old
   copy) legitimately commits an older version of a block over a newer
   one. With `--baseline <pre-sync snapshot>`, any block whose `_updated`
   went BACKWARD versus the snapshot is restored from the snapshot.

Duplicate whole blocks with the same slug: newer `_updated` wins.
The `## Archive` section is never touched. Conservative by design: no
confident repair -> no change, and the reason is printed.

Usage: projects_dedup.py FILE [--baseline SNAPSHOT] [--check]
Prints "clean — no ghosts" or one line per repair. Always exits 0 unless
FILE is unreadable.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DATE_RX = re.compile(r"_updated (\d{4}-\d{2}-\d{2})")
HDR_RX = re.compile(r"^## (\S.*?)\s*$")
FIELD_THREAD = "- **thread:**"


def split_blocks(text: str):
    """-> (preamble, [(slug, block_text)], archive_text)."""
    lines = text.splitlines(keepends=True)
    idx = [i for i, l in enumerate(lines) if HDR_RX.match(l)]
    if not idx:
        return text, [], ""
    preamble = "".join(lines[: idx[0]])
    blocks, archive = [], ""
    bounds = idx + [len(lines)]
    for a, b in zip(bounds, bounds[1:]):
        slug = HDR_RX.match(lines[a]).group(1)
        chunk = "".join(lines[a:b])
        if slug.lower().startswith("archive"):
            archive = "".join(lines[a:])  # archive runs to EOF, untouched
            break
        blocks.append((slug, chunk))
    return preamble, blocks, archive


def block_date(block: str):
    dates = DATE_RX.findall(block)
    return max(dates) if dates else None


def try_split_two_versions(slug: str, block: str):
    """If a block holds two interleaved versions, return (a, b) else None."""
    lines = block.splitlines(keepends=True)
    thread_idx = [i for i, l in enumerate(lines) if l.startswith(FIELD_THREAD)]
    if len(thread_idx) != 2:
        return None
    header = lines[0]
    aka = [l for l in lines[1:thread_idx[0]] if l.startswith("- **aka:**")]
    a = header + "".join(aka) + "".join(lines[thread_idx[0]:thread_idx[1]])
    b = header + "".join(aka) + "".join(lines[thread_idx[1]:])
    if block_date(a) and block_date(b):
        return a, b
    return None


def newest_wins(slug: str, block: str, notes: list):
    two = try_split_two_versions(slug, block)
    if not two:
        if len(DATE_RX.findall(block)) > 1:
            notes.append(f"ambiguous: {slug} has multiple _updated lines but "
                         f"no clean two-version split — left untouched")
        return block
    a, b = two
    keep = a if block_date(a) >= block_date(b) else b
    notes.append(f"repaired: {slug} — two interleaved versions, kept "
                 f"_updated {block_date(keep)}")
    if not keep.endswith("\n\n") and keep.endswith("\n"):
        keep += "\n"
    return keep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--baseline")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    path = Path(args.file).expanduser()
    try:
        text = path.read_text()
    except OSError as e:
        print(f"unreadable: {e}", file=sys.stderr)
        return 1

    notes: list = []
    preamble, blocks, archive = split_blocks(text)

    # 1. in-block interleave repair
    blocks = [(slug, newest_wins(slug, blk, notes)) for slug, blk in blocks]

    # 2. duplicate-slug repair (whole block duplicated)
    seen: dict = {}
    order: list = []
    for slug, blk in blocks:
        if slug in seen:
            old = seen[slug]
            d_old, d_new = block_date(old) or "", block_date(blk) or ""
            keep = blk if d_new >= d_old else old
            seen[slug] = keep
            notes.append(f"repaired: duplicate block {slug} — kept "
                         f"_updated {block_date(keep)}")
        else:
            seen[slug] = blk
            order.append(slug)

    # 3. baseline backward-revert repair
    if args.baseline:
        bpath = Path(args.baseline).expanduser()
        if bpath.is_file():
            _, bblocks, _ = split_blocks(bpath.read_text())
            bmap = dict(bblocks)
            for slug in order:
                d_file = block_date(seen[slug])
                d_base = block_date(bmap.get(slug, ""))
                if d_file and d_base and d_base > d_file:
                    seen[slug] = bmap[slug]
                    notes.append(f"repaired: {slug} — merge moved _updated "
                                 f"backward ({d_file} < {d_base}), restored "
                                 f"pre-sync version")

    new_text = preamble + "".join(seen[s] for s in order) + archive
    if not notes:
        print("clean — no ghosts")
        return 0
    for n in notes:
        print(n)
    changed = new_text != text
    if changed and not args.check:
        path.write_text(new_text)
        print(f"wrote {path}")
    elif changed:
        print("(--check: not written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
