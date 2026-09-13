---
description: Weekly plans sweep — surface drift, draft journal entry
---

Run the weekly plans sweep per `~/dotclaude/practices/plan-driven-workflow.md`. Goal: keep `plans/` from rotting.

## Steps

1. **Verify** you're in a project with a `plans/` directory (cwd or parent). If not, abort with a clear message.

2. **Scan every plan.** For each `.md` under `plans/`, `plans/speculative/`, `plans/complete/`, `plans/archived/`:
   - Parse the status header at the top: `Status:`, `Prepared:`, `Owner:` lines.
   - Last commit touching the file: `git log -1 --format='%cs|%s' -- <file>` (ISO date + subject). If the file isn't tracked yet, note it as "uncommitted draft."

3. **Classify drift candidates.** For each plan, decide which (if any) of these apply:

   | Category | Trigger |
   |---|---|
   | demote-or-assign | `Status: actionable` AND `Owner: unassigned` AND `Prepared:` > 3 weeks ago |
   | blocked-or-stopped | `Status: in-flight` AND no commit touching the file in the last 7 days |
   | archive-candidate | `Status: speculative` AND `Prepared:` > 4 months ago |
   | back-annotate | `Status: complete` AND `## Closeout / as-built` section is missing or only placeholder text |

4. **Output:**
   - A short summary table grouped by category:
     ```
     plan                          status        last touched    issue
     ----                          ------        ------------    -----
     slot-arena-v2.md              in-flight     14d ago         no recent commits
     tail-attribution.md           speculative   2026-01-04      stale (>4 months)
     ...
     ```
   - A drafted journal entry. Use ISO week number for today:
     ```
     plans sweep 2026-WNN: <N> speculative → archived, <N> actionable → in-flight, <N> complete back-annotated
     ```
     The N values are counts of *candidates*, not actions you took.

5. **Do not move files or commit anything.** This is a surface-and-suggest command. The user runs `/promote-plan` per item or moves things manually.

## Notes

- A plan in the wrong directory for its `Status:` is itself drift — surface it too.
- "Uncommitted draft" plans (modified-or-untracked) are fine, just note them so the user remembers they exist.
