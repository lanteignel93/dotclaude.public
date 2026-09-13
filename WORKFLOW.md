# The workflow — a day and a week

How the pieces compose in practice. Reference detail lives in
[docs/guide.md](docs/guide.md); this is the rhythm.

## A day

**Morning — `/briefing`.** The 15-minute exec-assistant chat, compressed:
overdue and due-today tasks, unresolved Next/blocked from recent journal
entries, PRs needing you, overnight-job health from the collector cache,
cadence alerts ("no /week in 9 days"). Read-only; it never writes.

**Session start — automatic.** Opening Claude in any repo injects: due
tasks, that repo's `projects.md` block (thread / next / blocked), and the
last journal entry's open items. You start already knowing where you left
off — across ten concurrent projects.

**During work — ambient capture.**
- Something dated or recurring comes up → `/task add rotate certs every 3
  months starting Oct 1`. Done something → `/task done <substring>`.
  Slipping → `/task defer`.
- A durable finding (result, parameter, failed experiment) → `/note` (or
  Claude offers it per the CLAUDE.md standing rule). Negative results are
  first-class.
- Someone gives you useful feedback in a paste or review → it lands in
  `feedback.md` on sight (standing rule), one line of mention.
- Every slash command is logged (hook) — that powers the rhythm alerts.

**Session end.** The SessionEnd hook stubs the structural facts
automatically. For anything that mattered, `/journal` before you stop:
what was done, decisions, open/blocked, next — it also bumps the
project's dashboard block and commits/pushes the journal repo. The
optional nightly journal-cron sweeps transcripts you forgot to journal.

## A week

| When | Command | What it earns you |
|---|---|---|
| Weekly (pick your day) | `/week` | Cross-project summary: highlights, decisions, open threads, dashboard staleness, research drift |
| Weekly-ish | `/project-sweep` | Journal days → project-shaped ideas into the inbox (append-only) |
| When the inbox itches | `/project-clean-up` | Categorize, rank, archive ideas; graduate mature ones via `/plan` |
| Monthly | `/task prune` | Closed tasks older than 30d → archive |
| Monthly | `/memory-clean` | Validate Claude's auto-memory against the journal record — keep/update/delete on evidence |
| On demand, per project | `/sweep` | Plans-directory drift report |

## The three tiers (don't mix them)

| Thing | Home | Verb |
|---|---|---|
| Dated/recurring next-action (< half a day) | `~/work-journal/tasks.md` | `/task` |
| Multi-step initiative with a design | `<project>/plans/<slug>.md` | `/plan`, `/promote-plan` |
| Undated someday/maybe idea | `~/work-journal/project-ideas.md` | `/project-sweep`, `/project-clean-up` |

Plus the knowledge stores: per-topic research notes
(`research/{trading,dev}/`, lifecycle frontmatter, drift-tracked by the
pulse), immutable cited-artifact snapshots (`research/sources/`,
snapshot-on-cite), and the feedback log.

## Research-note conventions (the part that compounds)

- One note per topic, append-only dated sections, every section ends with
  a `_source:` line.
- Frontmatter: `status: active|dormant|closed|reference` (note freshness)
  and, for strategy-shaped threads, `stage: hypothesis→…→deployed|killed`
  (lifecycle). The pulse flags active notes silent >21 days — either the
  thread stalled or findings are leaking into the journal instead.
- **Snapshot on cite**: any cited artifact on a temp or regenerable path
  gets copied into `research/sources/` as `YYYY-MM-DD-<slug>.<ext>`,
  immutable, and cited by its repo-relative path. Citations survive
  machine moves; a vanished reference is citation rot the pulse reports.
- Re-read the topic note before resuming a thread. That's what it's for.

## Working with Claude on top of this

The CLAUDE.md contract makes sessions autonomous but accountable: work to
an organic stopping point, arrive with tests ready, checkpoint with
status + evidence + 2-3 next directions. The journal/board/notes give
every future session the memory this session earned.
