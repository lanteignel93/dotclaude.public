---
description: Monthly memory hygiene — validate auto-memory against the work-journal record, propose deletions/updates conversationally
---

Validate this session's auto-memory against `~/work-journal` (the
verifiable record) and clean it up **with the user**. Conversational like
`/project-clean-up`: classify, propose, ask, apply. Never silently delete.

The premise: memories are point-in-time observations; the journal is
git-committed, dated, and records outcomes. When they disagree, the
journal is evidence — but journal entries record *claims*, so prefer
git-verifiable facts (commits, closed tasks, files on disk) over narration
when those conflict too.

## Steps

1. **Locate and read.** The session's memory directory (the one whose
   `MEMORY.md` is loaded at session start). Read `MEMORY.md` and every
   memory file it indexes.

2. **Gather evidence per memory.** Grep `~/work-journal` for each memory's
   subjects, names, and dates: `daily_logs/`, `tasks.md` +
   `tasks_archive.md`, `research/`, `feedback.md`,
   `project-ideas.md`. Verify any file paths, flags, or commands the
   memory references still exist.

3. **Classify** each memory:
   - **LIVE** — guidance still applies; no contradicting evidence.
   - **RESOLVED** — the journal shows the tracked thing completed or
     closed; the memory is now history, not guidance.
   - **SUPERSEDED** — the journal shows the fact changed after the memory
     was written (or a referenced path/flag no longer exists).
   - **UNVERIFIABLE** — nothing in the journal confirms or denies; note
     it, default keep.

4. **Present the full table in one shot** — memory name, classification,
   one-line evidence citation (`daily_logs/<date>.md` or task stamp) — and
   a proposed action per memory: keep / delete / update. Batch approval,
   not per-item questions.

5. **Apply agreed actions:**
   - Delete: remove the file and its `MEMORY.md` line.
   - Update: edit in place; keep one dated history line per change
     (`Superseded YYYY-MM-DD: <what changed>`) per the supersession
     convention in CLAUDE.md; refresh the `description:` if stale.
   - Keep: untouched.

6. **Consistency check:** every `MEMORY.md` line points at an existing
   file; every memory file has an index line; report any orphans fixed.

7. **Report:** N kept / N updated / N deleted, with one line each for the
   deletions (what knowledge left the system and why that's safe).

## Guardrails

- Memories carrying confidentiality constraints (held-close agreements,
  never-surface rules) are **never deleted or rewritten** without the user
  explicitly naming them in this conversation — resolution of a
  confidence is the user's call, not an inference from journal silence.
- This pass never *creates* memories — capture happens elsewhere.
- Nothing here is committed: the memory dir is not a repo, and
  `~/work-journal` is read-only for this command.

## Cadence

Monthly, surfaced by `/briefing`'s Rhythm section (same rhythm slot as
`/task prune`).
