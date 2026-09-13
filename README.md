# dotclaude — a Claude Code operating system for engineering work

A batteries-included workflow kit for running your engineering life
through Claude Code: a deterministic task board, an automatic engineering
journal, a morning briefing, per-project continuity injection, research
notes with rot detection, and the scheduled automation that keeps it all
running while you sleep.

Built and hardened in daily production use by a quant researcher/engineer
running ~10 concurrent Claude sessions across projects. Genericized for
sharing — every path, name, and example is yours to fill in.

**Companion repo**: `work-journal` (the data half — a private scaffold
this machinery reads and writes). Install both.

## What you get

| Feature | What it does |
|---|---|
| **Task board** (`/task` + `tasks.py`) | Dated + recurring tasks in a plain-markdown board; deterministic engine owns completion stamps and recurrence math; monthly prune to an archive |
| **Engineering journal** (hooks + `/journal`) | Every session leaves a structural stub automatically; `/journal` writes the rich entry (done/decisions/blocked/next); optional nightly AI writer consolidates what you forgot |
| **Morning briefing** (`/briefing` + collector) | One command: overdue/due tasks, journal carryovers, PR queue, overnight-job health (config-driven, false-positive-hardened), rhythm alerts |
| **Project continuity** (`projects.md` + SessionStart hook) | One block per active project; every session you open in a repo starts already knowing that project's thread, next action, and blockers |
| **Research notes** (`/note` + pulse) | Per-topic append-only notes with lifecycle frontmatter; drift detection flags active notes gone silent; snapshot-on-cite keeps citations from rotting |
| **Weekly rhythm** (`/week`, `/project-sweep`, `/project-clean-up`, `/memory-clean`) | Cross-project weekly summary; idea capture from journal days; idea triage; monthly memory hygiene |
| **Plans practice** (`/plan`, `/promote-plan`, `/sweep`) | Speculative→actionable→in-flight→complete lifecycle, living in each project's own repo |
| **Automation** (systemd user timers) | Journal cross-box sync, nightly journal writer, morning collector, config pull — with failure alerts and missed-run catch-up |

## The philosophy, in ten lines

1. Claude sessions are ephemeral; your work isn't. Everything durable
   lands in files (journal, board, notes) that the next session reads.
2. Deterministic things (dates, recurrence, stamps) belong to code;
   judgment (summaries, triage, briefings) belongs to the model.
3. Capture is ambient. Hooks record what happened; you only write when
   you have something to say (`/journal`, `/note`).
4. The morning briefing is the contract: if the system knows it, you
   hear about it before it bites.
5. Boards hold dated actions; plans hold designs; ideas hold maybes.
   Don't mix them.
6. Negative results are first-class research output.
7. Automation must fail loudly (alerts) and recover honestly (no
   false-positive alarm fatigue).
8. Every convention lives in a file Claude can read — the system explains
   itself to every new session.
9. Personal life stays out of work repos, by construction.
10. Start small: board + journal first; add timers when the habit sticks.

## Start here

1. **[INSTALL.md](INSTALL.md)** — clone, symlink, personalize (20 min).
2. **[WORKFLOW.md](WORKFLOW.md)** — the day and the week, as actually run.
3. **[docs/guide.md](docs/guide.md)** — the full operator's manual.
4. **[docs/DESIGN.md](docs/DESIGN.md)** — why it's built this way.

## Layout

```
.claude/commands/   13 slash commands (the verbs)
.claude/hooks/      6 hooks (the ambient capture)
.claude/bin/        engines: tasks.py, research_pulse.py, sync + cron scripts
.claude/settings.json  hook wiring + a starter permission allowlist
deploy/             setup script, systemd units + installer, example configs
templates/          plan / sprint / tasks / research-note stubs
practices/          the conventions (task grammar, plan lifecycle, tmux, commands)
agents/             role-lens context files + how to write your own
docs/               guide, workflow patterns, troubleshooting, design rationale
tests/              engine test suites
CLAUDE.md           the standing contract — symlinked to ~/.claude/CLAUDE.md
```
