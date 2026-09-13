---
description: Append a research finding to a topic note in ~/work-journal/research/
---

Append a research finding to the per-topic notes under
`~/work-journal/research/` (`trading/` and `dev/` subdirectories — the
domain IS the directory). Template: `~/dotclaude/templates/research-note.md`.

Arguments: `<topic hint> <finding text>` — or no finding text, in which case
synthesize the durable findings from the current session.

## Steps

1. **Resolve the topic.** List `~/work-journal/research/*/*.md` and
   fuzzy-match the topic hint against filenames and frontmatter `topic:`
   fields. One clear match → use it. Ambiguous → show candidates and ask.
   No match → propose creating a new note (name, domain subdir, status)
   from the template and confirm with the user before creating. Route to
   `trading/` vs `dev/` by content; ask only when genuinely ambiguous.

2. **Check the pointer rule.** If the note says an in-repo research log is
   canonical-while-active, keep the append to distilled conclusions and
   remind that detail belongs in the in-repo log.

3. **Append a dated section** (`## YYYY-MM-DD — <what>`): the finding(s),
   numbers preserved, failed experiments recorded as first-class content,
   ending with a `_source: ..._` provenance line (repo path, journal date,
   or "session" + date). Bump frontmatter `updated:`.

4. **Snapshot cited artifacts.** If a `_source:` or frontmatter `sources:`
   entry points at a box-local or regenerable path (`/tmp`, `~/tmp`,
   regenerable network-share reports, received PDFs/notes), copy the file to
   `~/work-journal/research/sources/YYYY-MM-DD-<slug>.<ext>` (artifact
   date; immutable — a regenerated report is a NEW dated file; >10MB →
   pointer file per that folder's README) and cite the repo-relative
   `research/sources/...` path instead. Paths already inside work-journal
   or in a durable git repo need no snapshot.

5. **Report** the file and section added in one line.

## Do not

- Do not commit — work-journal is committed at the user's cadence.
- Do not duplicate content already in the note; extend or refine instead.
- Do not write outside `~/work-journal/research/`.
