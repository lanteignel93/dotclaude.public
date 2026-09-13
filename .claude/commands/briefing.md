---
description: Morning briefing — due tasks, in-flight work, PRs, rhythm alerts
---

The 15-minute morning chat with an executive assistant, compressed: what
should be on my mind, what's due, what needs review, what's drifting.
Read-only — output to stdout, write nothing.

## Gather (skip any source that's absent, without comment)

0. **Collector cache** — `~/.claude/logs/briefing-cache.md`, written by
   `briefing-collect.timer` at 07:15 on weekdays (source:
   `.claude/bin/briefing-collect.sh`). If present and generated within
   ~24h, use its sections instead of gathering live: overnight job
   health (flag any RECENT ERRORS / STALE lines under Top of mind — a
   silently dead pipeline is exactly what mornings should catch), failed
   systemd user units, repo dirty/ahead/behind state, and the GitHub PR
   landscape (replaces step 4's `gh pr status`). If the cache is missing
   or stale on a box that has the timer installed, say so in Rhythm
   (`briefing-collect stale — check systemctl --user list-timers`) and
   fall back to live gathering.

1. **Tasks** — `python3 ~/dotclaude/.claude/bin/tasks.py list --all --json`
   (no `~/work-journal/tasks.md` → skip). From the JSON: overdue (oldest
   first), due today, and upcoming within 7 days. Closed tasks whose ✅ stamp
   is in the last day or two are useful "already handled" context.

2. **Journal continuity** — today's and the last ~3 days of
   `~/work-journal/daily_logs/<date>.md`. Pull unresolved "Next" /
   "Open/blocked" items from `/journal` entries that haven't shown up as done
   since.

4. **Current repo** (skip if cwd is not a git repo) — `git status`, current
   branch, unpushed commits (`git log @{u}..` where an upstream exists);
   PRs from the collector cache (step 0), or `gh pr status` live if the
   cache is absent.

5. **Plans pulse** (skip if no `plans/` in the repo) — status headers of
   plans in `plans/` root: in-flight items are the active work; flag
   actionable plans with `Owner: unassigned`. Pulse only — drift analysis
   belongs to `/sweep`.

6. **Rhythm** — `~/work-journal/command-log.tsv` (tab-separated: timestamp,
   host, cwd, command). Last-run times vs expected cadence:

   | Command | Cadence |
   |---|---|
   | `/journal` | on active days |
   | `/week` | weekly (by Friday) |
   | `/project-sweep` | weekly-ish |
   | `/task prune` | monthly |
   | `/memory-clean` | monthly |

   Alert on misses, e.g. `/week last ran 12d ago (weekly) — review overdue`.
   No log file → skip silently. `/sweep` has NO cadence: it is on-demand
   only, and only for repos where someone else owns the plans
  — never alert on it.

7. **Research pulse** — skip if `~/work-journal/research/` is absent. Run
   `python3 ~/dotclaude/.claude/bin/research_pulse.py --check-paths`.
   Daily: surface only exceptions — `[DRIFT]`-flagged active notes,
   `[FIX FRONTMATTER]`, unrecognized statuses, missing cited paths. On
   your weekly team-meeting day also include the full Active table as
   pre-meeting research context (adjust the day to your team rhythm). Clean pulse on a non-Tuesday → nothing.

8. **Day awareness** — Friday: remind `/week` if not yet run this week.
   Monday: surface last week's open/blocked carryovers from the journal.

## Output (terse, in this order; drop empty sections)

- **Top of mind** — 3–5 synthesized bullets: the answer to "what should I be
  thinking about today", drawn from overdue + in-flight + blocked. Judgment,
  not a dump.
- **Tasks** — overdue / due today / upcoming ≤7d, one line each.
  one line each.
- **In flight** — plans in flight, branches with unpushed work, PRs needing
  my action or review.
- **Waiting on / blocked** — from journal entries and PR states.
- **Research pulse** — drift/rot exceptions (and the Active table on
  Tuesdays), per gather step 7.
- **One thing to protect** — the single highest-leverage item; name it and
  say why.
- **Rhythm** — cadence alerts and day-of-week reminders, if any.

Style: work-focused, no filler, `file:line` / PR numbers where they sharpen a
point. If a source is empty and that's itself signal (journal silent for
days), say so in one line.
