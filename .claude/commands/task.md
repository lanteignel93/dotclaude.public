---
description: Manage dated/recurring work tasks in ~/work-journal/tasks.md
argument-hint: "[list|add|done|start|cancel|defer|move|triage|prune|check] [args]"
---

Manage the work tasks file through the deterministic engine at
`~/dotclaude/.claude/bin/tasks.py` (invoke as `python3 ~/dotclaude/.claude/bin/tasks.py`;
if `python3` is absent — e.g. on Windows — use `python`). Grammar and
semantics: `~/dotclaude/practices/tasks.md`.

Arguments: $ARGUMENTS

## Procedure

1. **Preflight.** If `~/work-journal/tasks.md` does not exist: for a read
   request, report that and stop; for anything else, offer to bootstrap
   (`mkdir -p ~/work-journal && cp ~/dotclaude/templates/tasks.md
   ~/work-journal/tasks.md`) and proceed only after the user confirms.

2. **Route.** No arguments → run `list` and show its output verbatim.
   Otherwise the first token is the subcommand; pass the rest through.
   `list --all`, `--section <S>`, `--json`, `prune [--dry-run]`, and `check`
   map directly.

3. **Natural-language add.** Translate phrasing into engine flags — the
   engine takes ISO dates only:
   - "remind me to rotate certs every 2 months starting Aug 1" →
     `add "Rotate certs" --every "every 2 months" --due 2026-08-01`
   - Resolve every relative date ("next Friday", "in two weeks") to
     `YYYY-MM-DD` from today's date.
   - Only use recurrence rules from the supported table in
     `practices/tasks.md`; if the request doesn't fit one, say so instead of
     approximating.
   - Lead time ("surface it a week early") → `--sched` before `--due`.
   - Pick `--section` only when the user names one; default is Inbox. Tags
     (`#project/<slug>`) go inside the text argument.
   - Echo the exact command you ran and the engine's output.

4. **Done / start / cancel.** Run `done "<substring>"` (or `start`/`cancel`).
   On exit 2 the engine prints numbered candidates: if the user's wording
   already singles one out, re-run with `--line N`; otherwise show the
   candidates and ask. Exit 1 with "unparseable recurrence" → show the line,
   propose a corrected rule, and fix it only with the user's OK.

5. **Defer.** Resolve the target date to ISO, then
   `defer <match...> <YYYY-MM-DD>`. The engine shifts 🛫 by the same delta.

6. **Move.** "move X to <section>" → `move <match> --to <Section>`. Unknown
   section → the engine lists the available ones; add `--create` only when
   the user asked for a new category by name.

7. **Triage.** `triage` walks the Inbox: run `list --all --section Inbox`,
   take the *open* items, and for each propose a target section — judge by
   existing section names, `#tags`, and task text; propose at most one or
   two new sections if a real cluster has no home. Present the full mapping
   for approval in one shot (per-item questions are tedious), apply the
   agreed moves via `move ... --to ... [--create]`, then run `check`. Items
   with no clear home stay in Inbox — say so rather than inventing a
   category.

8. **Accomplishment queries.** "what did I get done ...?" → search the `[x]`
   lines in `tasks.md` *and* `~/work-journal/tasks_archive.md` (where `prune`
   moves closed tasks, grouped by `## YYYY-MM` stamp month, source section in
   trailing parentheses). Filter by month, section, or `#tag`; answer with
   the matching lines, not a paraphrase.

9. **Direct edits.** Editing the file by hand (or via Edit) is allowed for
   reorganizing sections and rewording only. Always run `check` afterwards
   and fix what it reports.

## Do not

- Mark tasks done/cancelled by editing the file — completion stamps and
  recurrence spawns must come from the engine.
- Invent recurrence rules outside the supported grammar.
- Commit anything in `~/work-journal` — the journal repo is committed
  manually, never by tooling.

## Brevity

Keep task text short (aim under ~135 characters of text). A task line is a
handle, not a document — put the detail in the matching research note or
projects.md block and reference it as `(detail: <path>)`. Long lines make
the board unreadable and bloat every session-start injection.
