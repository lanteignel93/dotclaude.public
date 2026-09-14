---
description: Sweep un-swept journal days for project ideas → append to ~/work-journal/project-ideas.md
---

Scan the journal days not yet swept and capture project-shaped ideas into
the inbox of `~/work-journal/project-ideas.md`. Append-only — never
categorize, rank, archive, or commit. The companion `/project-clean-up`
organizes what this collects.

## Steps

1. **Resolve the ideas file:** `~/work-journal/project-ideas.md`.
   - If it doesn't exist, create it with the scaffold in *File format*
     below. Set `last_swept` to the day before the oldest
     `~/work-journal/daily_logs/<date>.md` so the first run scans every
     existing journal day.

2. **Read the watermark.** Parse `last_swept: YYYY-MM-DD` from the
   frontmatter. **Window** = every existing
   `~/work-journal/daily_logs/<date>.md` whose date `D` satisfies
   `last_swept < D < today`. Today is excluded on purpose — it may still
   be written to by later sessions, so it gets swept tomorrow.
   - If the window is empty, report `nothing to sweep` with the watermark
     and stop. Do not modify the file.

3. **Read each journal day in the window.**

4. **Extract project-shaped ideas — not tasks.** A project idea is
   something worth *building or initiating*, not a to-do. Pull from:
   - Recurring pain points or friction surfaced across multiple days
     ("hit X again").
   - Explicit "should build / automate / write a tool for X" statements.
   - `Next` / `Open` items that imply a new tool, library, dashboard, or
     initiative rather than finishing existing work.
   - Decisions that hint at follow-on work ("for now we hardcoded X; the
     real fix is Y").

   Skip: routine next-actions on existing work, one-off fixes, and
   anything already captured as a plan.

5. **Dedup against the file.** If an idea is already present (inbox or any
   category), don't re-add it. The watermark normally prevents overlap,
   but check the text anyway.

6. **Append survivors to the `## Inbox` section**, one per line:

   ```
   - <one-line idea> — _source: journal <date>[, <project>] · captured <today>_
   ```

   Keep the one-liner tight and concrete. A day with no ideas is normal.
   FORMAT: wrap at ~126 columns with 2-space continuation indents; the
   `_source ..._` metadata goes on its own indented line — never let a
   bullet run as one long line.

7. **Bump the watermark.** Set `last_swept` to yesterday — every day
   before today is now swept. Do this even if zero ideas were found.

8. **Report:** N ideas from M journal days, list them, and state the new
   watermark.

## File format (create if missing)

```markdown
---
last_swept: <date>
---

# Project ideas

Work-scoped, cross-project. Captured by /project-sweep, organized by
/project-clean-up. A mature idea graduates to a plan via /plan <slug>.

## Inbox

## Research / alpha

## Infra & data

## Tooling / dev-experience

## Archive
```

## Notes

- **Journals only.** This does not read the live session — capture an
  in-session idea by journaling it first (`/journal`), then sweep.
- **Append-only.** Never categorize, rank, archive, or commit. That's
  `/project-clean-up` and your own cadence.
- Idempotent: the watermark advances even on empty windows, so re-running
  is cheap and won't double-capture.
- Caveat: a journal file backdated to a day `≤ last_swept` won't be
  re-swept. Rare (journals are written same-day); add such ideas manually
  if it happens.
