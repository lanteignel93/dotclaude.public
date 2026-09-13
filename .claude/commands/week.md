---
description: Weekly summary from ~/work-journal/daily_logs/ — cross-project, themes, what's blocked
---

Produce a weekly summary from the last 7 daily journal files in `~/work-journal/daily_logs/`.

## Steps

1. **Compute the date range.** Today and the 6 prior days (inclusive 7-day window). List the dates explicitly so missing files are visible.

2. **Read every existing `~/work-journal/daily_logs/<date>.md` in the range.** Missing days are fine — note them only if a gap is worth flagging (`no entries Thu–Fri`).

3. **Synthesize the summary** with these sections (drop any that genuinely have nothing):

   ### Projects touched
   - List each repo/project that appeared this week, in rough order of activity volume. One line each.

   ### Highlights
   - What shipped: PRs merged, plans promoted to complete, significant commits.
   - Cross-project moves: started a new initiative, completed a migration, etc.

   ### Decisions of the week
   - Choices captured in `/journal` entries that affect future weeks. Brief context for each.

   ### Open / blocked carrying forward
   - In-flight items not yet landed.
   - Things waiting on others.
   - Group by project where helpful.

   ### Plans sweep status
   - If a `plans sweep YYYY-WNN: ...` journal line appeared this week, surface it.
   - If not, flag: `no plans sweep recorded this week`.

   ### Tasks
   - Skip this section entirely if `~/work-journal/tasks.md` doesn't exist.
   - Run `python3 ~/dotclaude/.claude/bin/tasks.py list --all --json`.
   - Completed this week: items whose done date falls in the window — count, plus the notable ones.
   - Overdue carrying forward: open items past due — list with age, oldest first.

   ### Projects dashboard
   - Skip if `~/work-journal/projects.md` doesn't exist.
   - Blocks whose `_updated_` is older than the window while the journal
     shows activity for that repo → propose refreshed thread/next lines.
   - Blocks with no journal activity for 2+ weeks → propose `paused` or
     a move to Archive. Propose; the user disposes.

   ### Research pulse
   - Skip if `~/work-journal/research/` doesn't exist.
   - Run `python3 ~/dotclaude/.claude/bin/research_pulse.py --check-paths`.
   - Surface: active notes with `[DRIFT]` flags (a note claiming active but
     silent for weeks either needs an append or a status flip — propose
     which, per note), any `[FIX FRONTMATTER]` / unrecognized statuses, and
     missing cited paths. A clean pulse gets one line, not the full table.
   - Cross-box citations legitimately absent on this box get a
     `<!-- pulse:ignore -->` marker on their line, not deletion.

   ### Bench
   - Read `~/work-journal/project-ideas.md` (skip if missing).
   - Pick at most 1–2 *parked* ideas (categorized, not archived) that are
     adjacent to this week's active threads — same instrument, same
     subsystem, same technique — and say in one line why this week's work
     makes each timely. Judgment, not a listing; zero adjacent ideas is a
     normal outcome and gets no section.

   ### Feedback received
   - Read `~/work-journal/feedback.md` (skip if missing).
   - One line per entry dated within the window: who, and the distilled
     point. No entries → drop the section. This keeps the log alive and
     compounds toward reviews.

4. **Output to stdout.** Don't write a file — this is for reading and deciding what to act on (paste into a status update, file a follow-up plan, archive a stale item).

5. **Style:** terse, work-focused, no fluff. Quote `file:line` or commit SHAs where it tightens a point.

## Notes

- The window is 7 calendar days, not 5 business days. Weekends with no activity are normal.
- If the journal is sparse (most days missing), say so. The summary's job is to reflect what the journal actually contains, not to manufacture content.
- This command never writes. Read-only by design — the Tasks section reads via `tasks.py list`, which doesn't mutate either.
