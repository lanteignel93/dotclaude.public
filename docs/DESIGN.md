# Design rationale

Why the kit is shaped the way it is — the lessons are earned, keep them.

## systemd user timers over cron
`Persistent=true` catches up runs missed while a box was down (cron
silently skips them, which loses cross-box sync days); journald captures
output without per-line redirects; `OnFailure=` turns silent breakage into
an email/push. Boxes without a systemd user manager keep the cron
fallback installer.

## Union-merge journal sync
Two machines appending to the same daily log or task board must never
conflict destructively. `.gitattributes` (`*.md`/`*.tsv` merge=union)
keeps both sides' lines; `/journal`'s conflict rule is the same policy by
hand. Cost: a line edited in place on both boxes can survive duplicated —
`tasks_dedup.py` auto-fixes provable ghosts (same section + core text),
anything ambiguous is left for a human. Accept the occasional duplicate;
never accept silent data loss.

## Engine-owned task state
Completion stamps and recurrence math go through `tasks.py`, never
free-hand edits — deterministic date arithmetic, lintable board
(`check`), and an archive trail (`prune`). Rewording and reorganizing by
hand stays allowed; state changes don't.

## Budget ceilings on headless runs
The nightly journal writer calls the `claude` CLI with an explicit
`--max-budget-usd`. Learned the hard way: without a ceiling a
large-transcript night silently costs multiples; with too low a ceiling
the job dies silently for days. Set a ceiling, alert on failure, and read
the log weekly until you trust it.

## Holiday/absence awareness in scheduled jobs
Weekend guards are not enough — market holidays, vacations, and quiet
days all look like "the upstream data never arrived" to a polling job.
Distinguish "expected silence" (exit 0 with a note) from "broken pipeline"
(exit 1, alert). Every scheduled job in this kit that waits on external
data should carry a calendar guard appropriate to your domain.

## Collector false-positive discipline
A morning health report that cries wolf trains you to skip it. Three
failure modes are handled by design: (1) error text lingering in a tail
window after the job recovered — the success_regex column suppresses it;
(2) mtime-only freshness checks calling a failed-but-writing job healthy —
pair age checks with error greps; (3) once-a-day logs where a line-count
tail spans weeks — date-filter error lines to the last ~3 days.

## Plans live with their project
A plan is part of the repo it changes; the journal only points at it.
Speculative by default — most plans are captured thinking, not
commitments.
