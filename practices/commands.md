# Custom slash commands

Operational layer on top of the plan-driven workflow in `~/dotclaude/practices/plan-driven-workflow.md`. Each command is a markdown prompt template in `~/dotclaude/.claude/commands/`, available globally as a `/<name>` slash command in any Claude session.

Source of truth is the files in `.claude/commands/` themselves. This doc explains *when* to invoke each and how they fit together; each command file spells out the *how* (the procedure Claude follows when invoked).

## The commands

| Command | Signature | One-line |
|---|---|---|
| `/briefing` | — | Morning briefing: due tasks, in-flight work, PRs, rhythm alerts |
| `/task` | `[list\|add\|done\|start\|cancel\|defer\|move\|triage\|prune\|check] [args]` | Manage dated/recurring tasks in `~/work-journal/tasks.md` |
| `/plan` | `<slug> [--actionable]` | Bootstrap a new plan from the template |
| `/promote-plan` | `<slug> <status>` | Move a plan to a new status, with validation |
| `/journal` | — | Append a rich session summary to today's `~/work-journal/daily_logs/` file |
| `/sweep` | — | Weekly plans drift report + journal-line draft |
| `/week` | — | Cross-project summary of the last 7 days from `~/work-journal/daily_logs/` |
| `/project-sweep` | — | Sweep un-swept journal days + meeting notes for project ideas → inbox |
| `/project-clean-up` | — | Interactively categorize, rank, and archive ideas |
| `/note` | `[topic] [finding]` | Append a research finding to `~/work-journal/research/{trading,dev}/` |
| `/feedback` | `[material]` | Distill received feedback into `~/work-journal/feedback.md` |
| `/projects` | `[update\|add\|retire <project>]` | Cross-project dashboard blocks in `~/work-journal/projects.md` |
| `/memory-clean` | — | Monthly: validate auto-memory against the journal record (evidence-based) |

Plus the passive hooks:

| Hook | Trigger | What it does |
|---|---|---|
| `session-start-tasks.sh` | SessionStart (startup/resume/clear) | Injects overdue + due-today + lead-time tasks from `~/work-journal/tasks.md` into context. Silent when the file is absent or nothing is due — non-work machines are unaffected. |
| `session-end-journal.sh` | SessionEnd (Claude session terminates) | Appends a structural stub (cwd, branch, today's commits, dirty state) to today's `~/work-journal/daily_logs/` file if the cwd is a git repo with activity. No summary — just artifacts. |
| `log-command.sh` | UserPromptSubmit (every prompt) | Appends slash-command invocations to `~/work-journal/command-log.tsv` (timestamp, host, cwd, command). `/briefing` reads it for cadence alerts. Silent no-op where `~/work-journal` doesn't exist. |

## Weekly rhythm

### Start of day → `/briefing`

```
/briefing
```

The exec-assistant pass: overdue and due-today tasks, unresolved Next/blocked
items from recent journal days, PRs needing review or fixing, in-flight plans
in the current repo, and cadence alerts from the command log (`/sweep` overdue,
journal silent, etc.). Read-only. The SessionStart hook already injects due
tasks into every session; `/briefing` is the fuller synthesis for deciding
what the day is for.

### Dated work → `/task`

```
/task                                              # what's due (also injected at session start)
/task add rotate certs every 3 months starting Oct 1
/task done rotate certs                            # stamps ✅, spawns the next occurrence
/task defer invoices to next friday                # 🛫 shifts by the same delta
```

Anything with a date or a recurrence goes to `~/work-journal/tasks.md` through
the engine at `~/dotclaude/.claude/bin/tasks.py` — date and recurrence math
stays deterministic, never model arithmetic. Grammar, recurrence table, and
boundaries: `~/dotclaude/practices/tasks.md`. The boundary in one line: single
dated action → `/task`; multi-step initiative → `/plan`; undated someday idea
→ `project-ideas.md`. Defer instead of letting overdue rot; `/task prune`
monthly to clear old completed lines.

### Starting new work → `/plan`

When a non-trivial change comes to mind — design rework, multi-step initiative, anything where writing the approach first beats just starting code:

```
/plan slot-arena-v2
```

Creates `plans/speculative/slot-arena-v2.md`, fills the status header (today, owner = you from `git config user.name`), leaves placeholders for Problem, Approach, Open questions. Status defaults to `speculative` because most plans should — you're capturing thinking, not committing to land.

If you already have buy-in and a scope cut, skip speculative:

```
/plan slot-arena-v2 --actionable
```

Then fill in the required sections (Scope, Stakeholders, Preconditions, Implementation sequence, Verification) before promoting further.

The command never commits. Edit the plan, then `git commit -m "plans: introduce slot-arena-v2"`.

### Moving a plan forward → `/promote-plan`

When a plan matures (got buy-in, found an owner, started landing, or finished):

```
/promote-plan slot-arena-v2 actionable
/promote-plan slot-arena-v2 in-flight
/promote-plan slot-arena-v2 complete
```

- Validates the plan has the sections required for the target status (per the matrix in `plan-driven-workflow.md`).
- `git mv`s the file to the right directory (preserves history).
- Updates the `Status:` line in the moved file.
- Commits with `plans: promote slot-arena-v2 speculative → actionable`.

Will refuse with a list of missing or placeholder sections if you try to promote past `speculative` without filling things in. That refusal is the whole point — it enforces discipline at the promotion boundary.

Demotion (`actionable → speculative` when scope unravels) uses the same command; the message and direction make the reason visible in `git log`.

### End of each session → SessionEnd hook + `/journal`

Two paths capture what happened in a session:

- **SessionEnd hook** (passive) — fires automatically when a Claude session terminates if the cwd is a git repo with activity. Appends a structural stub to `~/work-journal/daily_logs/<today>.md`: cwd, branch, today's commits in this repo, uncommitted state. No synthesis; just artifacts. Lives at `~/dotclaude/.claude/hooks/session-end-journal.sh`.
- **`/journal`** (active) — invoke during or at the end of a session for a richer entry. Adds a synthesized summary: what was done, decisions, blockers, next. Built from the actual conversation, not the artifacts alone.

Both write to `~/work-journal/daily_logs/<YYYY-MM-DD>.md` (curated docs like `project-proposals.md` live at the journal root, not in `daily_logs/`). Multiple sessions in a day → multiple sections, ordered by time. The hook never commits; `/journal` commits and pushes the journal repo after appending (`git add -A`, so pending task/idea/command-log changes ride along). If the push needs a pull first, it merges with `--no-rebase` and resolves any conflict by keeping both sides — safe because journal files are append-only — then pushes.

Scope: **work artifacts only.** Code, design, decisions, blockers, next. Personal context (life, philosophy, hobbies) belongs in your separate personal repo, not here. The boundary stays clean only if you keep entries scoped.

### Friday review → `/sweep` + `/week`

Once a week (Friday close, Monday morning — whatever fits):

```
/sweep      # walks plans/, surfaces drift candidates, drafts journal line
/week       # walks ~/work-journal/daily_logs/, summarizes the last 7 days cross-project
```

**`/sweep`** walks every `.md` under `plans/`, `plans/speculative/`, `plans/complete/`. Classifies drift:

| Category | Trigger |
|---|---|
| demote-or-assign | `actionable` + unowned + Prepared > 3 weeks ago |
| blocked-or-stopped | `in-flight` + no commit touching the file in 7 days |
| archive-candidate | `speculative` + Prepared > 4 months ago |
| back-annotate | `complete` + missing or placeholder Closeout |

Output: summary table + drafted journal entry like:

```
plans sweep 2026-W19: 2 speculative → archived, 1 actionable → in-flight, 3 complete back-annotated
```

Never moves files. You decide what to actually move (via `/promote-plan` per item) or fix manually.

**`/week`** reads the last 7 days of `~/work-journal/daily_logs/<date>.md` files and synthesizes a cross-project summary: projects touched, highlights (shipped, merged, promoted), decisions of the week, open/blocked carrying forward, tasks (completed this week + overdue carrying forward, via `tasks.py`), and any plans-sweep journal lines from the period. Read-only; outputs to stdout. While you're in the Friday pass, `/task prune` about monthly clears completed task lines older than 30 days.

Together: `/sweep` keeps the plans directory honest; `/week` answers "what did I actually do." Skip either for three weeks and you lose the longitudinal signal the system is supposed to provide. The drafted journal line from `/sweep` is the weekly receipt that the discipline still held.

### Idea capture → `/project-sweep` + `/project-clean-up`

A pre-plan layer: ideas that aren't yet worth a `plans/<slug>.md` but shouldn't evaporate into the journal. Lives in `~/work-journal/project-ideas.md`.

```
/project-sweep       # scan un-swept journal days, append project-shaped ideas to the inbox
/project-clean-up    # interactively categorize, rank, and archive stale ideas
```


**`/project-clean-up`** is the deliberate, *conversational* counterpart — the `/promote-plan` to `/project-sweep`'s `/sweep`. It walks the file with you: proposes a domain category and an impact×effort tag per inbox idea and asks you to confirm, surfaces ideas untouched > 8 weeks and asks which to archive, and flags mature ideas to promote. It rewrites the file only after you've weighed in, preserves every entry (archive, never delete), and never commits.

Mature idea → `/plan <slug>` graduates it into the plans lifecycle. That's the boundary: `project-ideas.md` holds one-liners; a plan is structured thinking.

### Knowledge capture → `/note` + `/feedback` (2026-07-31)

Two stores for what the other tiers don't hold: cumulative research knowledge and received feedback.

```
/note <topic> [finding]   # append a dated finding to research/{trading,dev}/<topic>.md
/feedback [paste]         # distill received feedback into feedback.md
```

**`research/trading/` + `research/dev/`** hold per-topic accumulating notes (template `templates/research-note.md`: frontmatter status/sources/updated + dated finding sections with provenance). Domain = directory. Negative results and rejected experiments are first-class. Active projects with a living in-repo research log get a pointer note (in-repo log canonical while active; full distillation at thread freeze). Re-read the topic note before resuming a thread — that's what it's for.

**`feedback.md`** is ONE newest-first log of feedback you receive (chat advice, PR-review nuggets, guidance handed to you in person). Person/role are entry metadata, never the organizing key.

Both commands are the *explicit* triggers; the default is ambient capture per the CLAUDE.md standing rules — Claude extracts feedback on sight from shared material, and offers/appends research findings when a session produces them (`/journal` reinforces this at synthesis time). Neither store is swept by `/project-sweep` (v1). Neither command commits.

## How they compose

A typical plan lifecycle, with journaling overlaid:

```
Mon:     /plan slot-arena-v2                       # → speculative, draft
Mon EOD: /journal                                  # richer entry for the day
Wed:     (edit plan; get the lead's buy-in via PR comment)
Wed:     /promote-plan slot-arena-v2 actionable    # validation passes
Thu:     git worktree add ../topics/slot-arena-v2 t/slot-arena-v2
Thu:     /promote-plan slot-arena-v2 in-flight     # work started
Thu–Mon: (commit incrementally; SessionEnd hook stubs entries at each session close)
Tue:     (squash + rebase + open the PR per your repo's flow)
Tue:     (PR review, merge)
Wed:     (write Closeout / as-built section in the plan)
Wed:     /promote-plan slot-arena-v2 complete      # validation requires closeout
Fri:     /sweep                                    # journal line: W19 movements
Fri:     /week                                     # cross-project summary
```

Not every plan visits every step. Some die in `speculative/`. Some get demoted. Some are small enough that the diff explains itself — no plan needed at all. The four commands are *operations*; a plan's life is whatever sequence of them it actually takes.

## What's deliberately not a command

- **`/incident`** — some production repos keep `docs/incidents/`. Whether to wire this depends on whether you author incident docs in your day-to-day. Not added yet.
- **Quant methodology check** — already prose in `agents/agent_ds.md`. Claude applies it inline. A command would add ceremony without adding enforcement.
- **`/format`, `/build`, `/test`** — single-shell wrappers belong in `~/.zshrc` aliases.

If a recurring pattern justifies a new command, add it.

## Adding a new command

1. Write `~/dotclaude/.claude/commands/<name>.md`:
   ```yaml
   ---
   description: <one-line, shown in /help>
   argument-hint: <arg pattern, optional>
   ---
   ```
2. Body = prompt template. Use `$ARGUMENTS` where the user's input goes.
3. Spell out the procedure as concrete steps with explicit preflight and what *not* to do (e.g. "do not commit").
4. Commit + push from dotclaude. New sessions pick it up; existing sessions may need a restart.

The symlink `~/.claude/commands → ~/dotclaude/.claude/commands` is set up by `deploy/setup-server.sh`, so a new command is available everywhere as soon as it's in the directory.
