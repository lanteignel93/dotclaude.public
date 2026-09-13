# Operator's guide

How the pieces of this repo compose into the daily work workflow. This is the
"start here" doc — depth lives in the linked files, not here.

## The mental model

Three homes, three jobs:

| Repo | Job | Synced how |
|---|---|---|
| `~/dotclaude` | **Machinery** — commands, hooks, engine, templates, practices | git push/pull; symlinked into `~/.claude/` by `deploy/setup-server.sh` |
| `~/work-journal` | **State** — daily logs, tasks, project ideas, command log | `/journal` commits + pushes (pull-merge keeps both sides on conflict); other changes ride its next commit or are committed manually |
| each project repo | **Plans** — `plans/` lifecycle per project | with the project |

Machinery changes propagate with `git pull` in `~/dotclaude` — the symlinks do
the rest, no re-setup. State never rides along; `~/work-journal/` is opt-in
per machine, and every hook gates silently where it doesn't exist.

## A day

**Morning — `/briefing`.** The exec-assistant pass: overdue and due-today
tasks, unresolved Next/blocked from recent journal days, PRs needing review or
fixing, in-flight plans, cadence alerts ("no `/sweep` in 12d"). Read-only.

**Session start — automatic.** Opening Claude on a machine with
`~/work-journal/tasks.md` injects overdue/due/lead-time tasks into context
(`session-start-tasks.sh`). Nothing due → nothing injected.

**During work.**
- Something with a date or recurrence comes up → `/task add renew vpn cert
  every year starting Dec 1`. Single dated actions only — multi-step work
  gets a plan (`/plan <slug>`), undated someday-ideas go to
  `project-ideas.md` (usually via `/project-sweep` later).
- Done something dated → `/task done <substring>`. Recurring tasks spawn
  their next occurrence automatically; slipping ones get `/task defer`.
- Every slash command you type is logged to `~/work-journal/command-log.tsv`
  (`log-command.sh`) — that's what powers the rhythm alerts.

**Session end — automatic + optional.** The SessionEnd hook appends a
structural stub (cwd, branch, commits, dirty state) to today's
`daily_logs/<date>.md`. For a synthesized entry — decisions, blockers, next —
run `/journal` before closing. A nightly job (22:00 local, if installed via
`deploy/install-journal-cron.sh`) consolidates anything the hooks missed.

## A week

**Friday (or Monday) review:**

```
/sweep      # plans drift report — what's rotting, what to promote/archive
/week       # last 7 days: projects touched, highlights, decisions,
            # open/blocked, tasks completed + overdue carrying forward
```

Act on the sweep via `/promote-plan <slug> <status>`. About monthly, add
`/task prune` (archives closed task lines older than 30 days to
`~/work-journal/tasks_archive.md`), `/project-clean-up` (triage the idea
inbox), and `/memory-clean` (validate auto-memory against the journal
record — evidence-based keep/update/delete).

**Idea flow:** journal entries → `/project-sweep`
extracts project-shaped ideas into `project-ideas.md` → `/project-clean-up`
categorizes → a mature idea graduates via `/plan <slug>` into the plans
lifecycle.

## The three tiers

| Thing | Home | Managed by |
|---|---|---|
| Dated/recurring next-action (< half a day) | `~/work-journal/tasks.md` | `/task` — grammar in [practices/tasks.md](../practices/tasks.md) |
| Multi-step initiative with a design | `<project>/plans/<slug>.md` | `/plan`, `/promote-plan` — lifecycle in [practices/plan-driven-workflow.md](../practices/plan-driven-workflow.md) |
| Undated someday/maybe idea | `~/work-journal/project-ideas.md` | `/project-sweep`, `/project-clean-up` |
| Cumulative research knowledge (per topic) | `~/work-journal/research/{trading,dev}/` | `/note` + standing rule (CLAUDE.md) |
| Cited source artifacts (reports, PDFs, one-off notes) | `~/work-journal/research/sources/` | snapshot-on-cite via `/note` step 4 — convention in its README |
| Received feedback (advice, review nuggets) | `~/work-journal/feedback.md` | `/feedback` + on-sight extraction (CLAUDE.md) |

Tasks can carry `#project/<slug>` tags — reserved for a future cross-project
dashboard; harmless today.

## Tool reference

Commands (details: [practices/commands.md](../practices/commands.md)):

| Command | One-line |
|---|---|
| `/briefing` | Morning synthesis: tasks, journal carryovers, PRs, plans pulse, rhythm |
| `/task` | Add / complete / defer / list dated + recurring tasks |
| `/plan` | Bootstrap a plan from the template |
| `/promote-plan` | Move a plan through its lifecycle, with validation |
| `/journal` | Rich session summary → today's daily log |
| `/sweep` | Weekly plans drift report |
| `/week` | Weekly cross-project summary (includes tasks) |
| `/project-sweep` | Journal days + meeting notes → idea inbox |
| `/project-clean-up` | Triage the idea inbox |
| `/note` | Append a research finding to a topic note (`research/{trading,dev}/`) |
| `/feedback` | Record received feedback into `feedback.md` |
| `/memory-clean` | Monthly memory hygiene — validate auto-memory vs the journal |

Hooks (all in `.claude/hooks/`, wired in `.claude/settings.json`, silent
no-ops where their preconditions are absent):

| Hook | Event | Effect |
|---|---|---|
| `session-start-tasks.sh` | SessionStart | Inject due tasks + this repo's projects.md block + last journal Next/Open (via `session_context.py`) |
| `session-end-journal.sh` | SessionEnd | Structural stub → daily log |
| `log-command.sh` | UserPromptSubmit | Slash commands → `command-log.tsv` |
| `read-track.sh` / `read-before-edit.sh` | PostToolUse / PreToolUse | Enforce read-before-edit |

Cross-box sync (`.claude/bin/journal-sync.sh`, `journal-sync.timer`
18:30 + 22:30 local weekdays per box, also runnable manually any time a
mid-day sync is wanted): commits local work-journal state, pulls, pushes. Conflicts are
auto-resolved by git's union merge driver (`.gitattributes`: `*.md`/`*.tsv`
keep BOTH sides' lines — the same keep-both policy `/journal` mandates);
anything union can't cover aborts the merge, keeps the local commit, and
logs to `~/.local/state/journal-sync.log` for interactive resolution.
Caveat: a line edited in place on both boxes (tasks.md date changes) can
survive as a duplicate — `journal-sync.sh` auto-fixes provable ghosts via
`.claude/bin/tasks_dedup.py` (conservative: same section + core text,
recurring lines untouched) and commits `sync: dedup union-merge ghosts`;
anything ambiguous is left for `/task`.

Engine: `python3 ~/dotclaude/.claude/bin/tasks.py` —
`list [--all] [--json]` · `add` · `done` · `start` · `cancel` · `defer` ·
`move` · `prune` · `check` · `hook-context`. `--file`/`--today` override for tests and
backfill. Tests: `python3 tests/test_tasks.py`.

Research pulse: `python3 ~/dotclaude/.claude/bin/research_pulse.py
[--check-paths] [--json]` — drift flags for active research notes +
citation-rot detection, read by `/briefing` and `/week`. Tests:
`python3 tests/test_research_pulse.py`.

Scheduling: `deploy/install-systemd-timers.sh` installs four systemd
user timers — `journal-sync` (18:30/22:30 M-F), `journal-cron` (nightly
journal consolidator, 22:00, logs to `~/.claude/logs/journal-cron.log`),
`briefing-collect` (07:15 M-F, writes the overnight-health/PR cache
`/briefing` reads: `~/.claude/logs/briefing-cache.md`; jobs configured in
`~/.config/dotclaude/briefing-jobs.tsv`), and `config-pull` (05:30 daily:
ff-only pull of the repos listed in `~/.config/dotclaude/config-repos`,
logs to `~/.local/state/config-pull.log`). Persistent=true catches up
runs missed while a box was down; any unit failure emails the address in
`~/.config/dotclaude/alert.conf` via `failure-alert@` (fallback: ntfy).
Boxes without a systemd user manager keep cron:
`deploy/install-journal-cron.sh`.

## New machine, in brief

```bash
git clone <your-fork-url>/dotclaude.git ~/dotclaude
bash ~/dotclaude/deploy/setup-server.sh
# opt in to journaling + tasks on this machine:
mkdir -p ~/work-journal && cp ~/dotclaude/templates/tasks.md ~/work-journal/tasks.md
# scheduled jobs (journal-sync, nightly journal, briefing collector):
bash ~/dotclaude/deploy/install-systemd-timers.sh
# (no systemd user manager? fallback: deploy/install-journal-cron.sh)
```

Full walkthrough incl. `gh auth`: [../INSTALL.md](../INSTALL.md). Per-project
patterns (where a CLAUDE.md lives, plans bootstrap): [workflow.md](workflow.md).
Something misbehaving: [troubleshooting.md](troubleshooting.md). Why things
are the way they are: [DESIGN.md](DESIGN.md).
