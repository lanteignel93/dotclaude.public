---
description: Interactively organize ~/work-journal/project-ideas.md — categorize, rank, archive stale ideas
---

Walk through `~/work-journal/project-ideas.md` **with the user**, organizing it conversationally. This is a discussion, not a batch job: propose, ask, adjust, then apply. Never silently restructure the file.

## Steps

1. **Read** `~/work-journal/project-ideas.md`. If it's missing or the Inbox is empty and nothing looks stale, say so, suggest `/project-sweep` first, and stop.

2. **Show the lay of the land** before changing anything:
   - Inbox count, per-category counts, archive count.
   - Stale candidates: any idea whose latest date (`updated` if present, else `captured`) is more than 8 weeks before today.

3. **Triage the Inbox — conversationally, in small batches.** Take 3–5 inbox ideas at a time to keep momentum. For each:
   - Propose a **category** (Research/alpha · Infra & data · Trading/execution · Tooling/dev-experience) and an **impact × effort** tag (`quick-win` / `big-bet` / `fill-in` / `time-sink`), each with a one-line rationale.
   - Ask the user to confirm or change the category, tag, or wording. Let them merge duplicates, split an idea, or drop one outright.
   - Don't move anything until they've weighed in on the batch.

4. **Review stale candidates.** Present the >8-week ideas and ask — per idea, or as a batch — whether to **archive**, **keep** (resets its clock: bump `updated` to today), or **promote**. Archive nothing you weren't told to.

5. **Status changes & promotions.** Surface ideas that look ready:
   - "X is concrete and high-impact — promote to a plan?" If yes, tell the user to run `/plan <slug>` (do **not** create the plan here) and annotate the idea line, e.g. `→ /plan <slug>`.
   - Apply any re-ranking the user asks for (an idea's impact/effort changed).

6. **Apply the agreed changes.** Rewrite the file:
   - Move inbox items into their categories with the `[tag]` and dates.
   - Move agreed-stale items into `## Archive` with an `archived <today>` note — keep the text; never delete.
   - Bump `updated` dates where status changed.
   - **Preserve every idea.** Nothing vanishes without an explicit "drop it" from the user.

7. **Summarize** what changed: N categorized, N archived, N flagged for `/plan`, N kept.

8. **Do not commit.** `~/work-journal` is committed at the user's own cadence. Offer the command — `cd ~/work-journal && git add -A && git commit -m "ideas: clean-up <date>"` — but don't run it.

## Idea line format

```
- <one-liner> [quick-win] — _Research/alpha · captured 2026-05-01 · updated 2026-06-18_
```

Archived:

```
- <one-liner> [time-sink] — _Tooling/dev-ex · captured 2026-01-04 · archived 2026-06-18_
```

## Notes

- **Conversational by design.** When in doubt, ask rather than decide. The user's judgment on category, importance, and staleness overrides every proposal you make.
- The domain categories and the 8-week staleness line are defaults — the user can override per idea or for the whole run.
- Idempotent: re-running on an already-clean file just reviews stale candidates and any new inbox items.
- The boundary with plans: this file holds one-liners. Structured thinking belongs in a plan — that's what the `/plan` promotion is for.

## Line format (keep files readable)

Wrap every idea at ~84 columns, 2-space continuation indents, metadata
(`_<category> · captured ... · updated/archived ...(reason)_`) on its own
indented line. When rewriting the file, re-wrap anything that has grown
past that.
