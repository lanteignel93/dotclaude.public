# Task tracking

Dated, recurring next-actions for work. This is the "TODO system" the GTD
mapping in `plan-driven-workflow.md` delegates to.

## What lives where

- **State**: `~/work-journal/tasks.md` — one markdown file, per server, never
  committed by tooling (same posture as the journal). Bootstrap on a new
  server: `mkdir -p ~/work-journal && cp ~/dotclaude/templates/tasks.md
  ~/work-journal/tasks.md`. No tasks file → no surfacing, no logging; opt-in
  is deliberate.
- **Machinery**: `~/dotclaude/.claude/bin/tasks.py` (engine, stdlib Python ≥
  3.8), `/task` and `/briefing` commands, `session-start-tasks.sh` hook. All
  deployed by the existing symlinks; servers pick changes up on `git pull`.

The split mirrors the journal: dotclaude ships behavior, work-journal holds
what happened.

## Grammar

Obsidian-Tasks-compatible emoji format — a plain-text grammar that also
renders as live tasks if the file is ever opened in Obsidian:

```text
- [ ] <text> [priority] [🔁 <rule>] [🛫 YYYY-MM-DD] [📅 YYYY-MM-DD]
```

One example per shape:

```text
- [ ] Rotate research-box certs ⏫ 🔁 every 3 months 🛫 2026-09-24 📅 2026-10-01
- [ ] Review data-vendor invoices 🔺 🔁 every month on the 1st 📅 2026-08-01
- [ ] Benchmark new fill model #project/fill-model 📅 2026-07-15
- [x] Renew VPN cert 📅 2026-07-01 ✅ 2026-07-01
```

| Status | Meaning |
|---|---|
| `[ ]` | todo |
| `[/]` | in progress |
| `[x]` | done (gets `✅ YYYY-MM-DD`) |
| `[-]` | cancelled (gets `❌ YYYY-MM-DD`) |

| Priority | Word |
|---|---|
| 🔺 | highest |
| ⏫ | high |
| 🔼 | medium |
| 🔽 | low |
| ⏬ | lowest |

Fields: `🔁` recurrence rule (optionally ending `when done`) · `🛫` scheduled
(lead-time — the date the task should start appearing) · `📅` due · `✅`/`❌`
completion stamps (tool-written, don't hand-author). Both bullets `-` and `*`
parse; the tool emits `-`.

Tags: `#project/<slug>` (or any `#tag`) live inside the task text and are
never repositioned — `#project/` is reserved for the future project dashboard.
One caveat: a tag terminates a `🔁` rule, so put tags before the fields, not
between `🔁` and its rule's end.

## Recurrence

| Rule | Example next-from-📅 |
|---|---|
| `every day` / `every N days` | `every 3 days`: 06-09 → 06-12 |
| `every weekday` | Fri → Mon (skips weekends) |
| `every week` / `every N weeks` | `every 2 weeks`: 06-24 → 07-08 |
| `every <weekday>` | `every Friday` from Mon → this Fri; from Fri → next Fri |
| `every N weeks on <weekday>` | +7N days, then forward-snap to the weekday |
| `every month` / `every N months` | keeps the day-of-month, clamps at month end |
| `every month on the Nth` / `on the last` | pins the day |
| `every year` / `every N years` | Feb 29 clamps to Feb 28 off-leap |
| `... when done` (suffix) | base the next occurrence on completion day, not 📅 |

Semantics:

- **Due-based by default.** Completing a task spawns the next instance from
  its 📅 date, not from today — a task done late recurs on schedule (matches
  the personal vault's observed behavior). Add `when done` for
  interval-since-last-time chores.
- **🛫 keeps its offset.** `🔁 every year 🛫 2026-12-01 📅 2026-12-15` spawns
  `🛫 2027-12-01 📅 2027-12-15`.
- **Month-end drift.** Plain `every month` from Jan 31 clamps to Feb 28 and
  *stays* on the 28th thereafter (stateless per-line recurrence). If you mean
  month-end, say `on the last`; if you mean the 31st where possible, say
  `on the 31st` — it un-sticks in longer months.
- **Dateless rules** (`🔁` with no 🛫/📅) spawn from today with a warning —
  the chain survives, but give it a date.
- **Unparseable rules refuse to complete** (exit 1) rather than silently
  killing the chain. `check` finds them proactively.

## Surfacing

A task surfaces when it's open (`[ ]` or `[/]`) and `📅 ≤ today` **or**
`🛫 ≤ today`. 🛫 is lead time: set it days or weeks before 📅 and the task
appears early ("in Nd"). Surfaced tasks show up:

- **At session start** — the `session-start-tasks.sh` hook injects overdue +
  due-today + lead-time tasks into every Claude session on machines that have
  a tasks file (capped at 20; silent when nothing is due).
- **On demand** — `/task` (or `/task list`), and the morning `/briefing`.

## Operations

| You want | Run | Engine call |
|---|---|---|
| see what's due | `/task` or `/task list` | `list` |
| everything | `/task list --all` | `list --all` |
| capture | `/task add rotate certs every 3 months starting Oct 1` | `add "Rotate certs" --every "every 3 months" --due 2026-10-01` |
| complete | `/task done rotate certs` | `done rotate certs` (spawns next instance) |
| push back | `/task defer certs to next Friday` | `defer certs 2026-07-10` (🛫 shifts by the same delta) |
| in progress | `/task start ...` | `start` |
| kill a chain | `/task cancel ...` | `cancel` (never spawns; to skip one occurrence, `done` or `defer` it) |
| recategorize | `/task move certs to Infra` | `move certs --to Infra` (`--create` for a new section) |
| triage Inbox | `/task triage` | Claude proposes a section per Inbox item; each accepted move runs `move` |
| tidy | `/task prune` | `prune --keep-days 30` |
| lint | `/task check` | `check` |

Direct edits are fine for reorganizing sections and rewording — run
`/task check` afterwards. **State changes go through the tool**: `done` is
what makes recurrence math deterministic and stamps consistent. Completed
lines stay in the file (history for `/week`); `prune` moves closed tasks
older than 30 days to the archive — fold it into a Friday review once a
month or so.

## Finished (board section)

Closed/cancelled lines move to a `## Finished` section at the bottom of
tasks.md (added 2026-08-25) so open work reads first. Engine semantics are
unchanged — prune reads stamps, not sections, so Finished drains into
`tasks_archive.md` as lines age past 30 days. `/task done` completes lines
in place; moving them to Finished is periodic hygiene, not required.

## Archive

`prune` doesn't delete — it appends closed tasks verbatim to
`~/work-journal/tasks_archive.md`, grouped under `## YYYY-MM` headings by
their ✅/❌ stamp, with the source section in trailing parentheses:

```text
## 2026-05
- [x] Depth-of-book study #research ✅ 2026-05-20 (Research)
```

Append-only, tool-written, plain markdown. Accomplishment history queries
("what research tasks did I finish in the last two months?") = grep the
archive plus the still-unpruned `[x]` lines in `tasks.md`, filtering by
month heading, section, or `#tag`. `prune --no-archive` exists for a true
delete; don't use it by default.

## Boundaries

| Shape of the thing | Home |
|---|---|
| single dated next-action (< half a day) | `~/work-journal/tasks.md` (here) |
| multi-step design/initiative | `plans/<slug>.md` in the project repo (`plan-driven-workflow.md`) |
| undated someday/maybe idea | `~/work-journal/project-ideas.md` (`/project-sweep`, `/project-clean-up`) |

A plan's action items can live inside the plan; promote one to a task when it
needs a date or a reminder.

## Assumptions and limitations

- `tasks.md` and `command-log.tsv` are **per-server** unless you git-sync
  `~/work-journal` between machines. Completing a task on server A does not
  mark it done on server B. If you work from one primary server, this is
  moot; if not, sync the journal repo or keep server-specific sections.
- **No locking**: concurrent sessions are last-writer-wins. Writes are atomic
  (temp file + rename) so the file can't tear, but two simultaneous `done`
  calls can drop one. Same risk posture as the journal.
- "Today" is the server's local date. `--today YYYY-MM-DD` overrides for
  backfill ("I actually did this yesterday") and tests.
- Don't put task-shaped lines (`- [ ] ...`) in code fences inside the tasks
  file — the parser doesn't track fences and will treat them as real tasks.
