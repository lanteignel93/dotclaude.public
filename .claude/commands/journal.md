---
description: Append a rich summary of this session to today's work journal
---

Append a richer entry to today's `~/work-journal/daily_logs/<YYYY-MM-DD>.md`. Use this when you want decisions, blockers, and next steps captured — beyond the structural stub the SessionEnd hook produces.

## Steps

1. **Resolve target file:**
   - Date: today (`date +%Y-%m-%d`)
   - Path: `~/work-journal/daily_logs/<date>.md`
   - If the file doesn't exist, create it with `# <date>` as the first line (creating the `daily_logs/` dir if missing).

2. **Gather session context:**
   - cwd
   - Git repo root and project name (basename of `git rev-parse --show-toplevel`)
   - Branch (`git symbolic-ref --short HEAD`)
   - Today's commits in this repo: `git log --since=midnight --oneline --no-decorate`
   - Current uncommitted state: `git status --porcelain`
   - Any PRs opened during this session (review prior tool use in the conversation if available)

3. **Synthesize a session summary.** Pull from the actual conversation in this session, not from imagination. Cover:
   - **What was done** — concrete actions: files touched, decisions made, code shipped. Past tense, bulleted.
   - **Decisions & tradeoffs** — meaningful choices (e.g. "went with X over Y because Z"). Only if there were any.
   - **Open / blocked** — what's still in-flight, what's waiting on someone. Only if applicable.
   - **Next** — explicit next action(s). The thing you'd do if you opened a fresh session tomorrow.

   If the session produced durable research findings (results, parameters,
   failed experiments, methodology), also append them to the matching topic
   note under `~/work-journal/research/{trading,dev}/` per the CLAUDE.md
   standing rule (`/note` semantics) and reference the note in the entry.

   If `~/work-journal/projects.md` has a block for this project (slug or
   `**aka:**` match on the repo basename), refresh its **thread** /
   **next** / **blocked** lines from this entry and bump `_updated_` —
   one line of mention, no permission ask. Don't create a block for
   one-off work; `/projects` handles deliberate additions.

4. **Append the entry** in this format:

   ```markdown
   
   ## <HH:MM> — <project> (manual /journal)
   
   **cwd:** `<short cwd, with ~ for $HOME>`  
   **branch:** `<branch>`
   
   ### What was done
   - ...
   
   ### Decisions
   - ...
   
   ### Open / blocked
   - ...
   
   ### Next
   - ...
   ```

   Drop any section that's genuinely empty — don't pad with "n/a."

5. **Style:**
   - Terse bullets, not paragraphs.
   - Past tense for "What was done."
   - Cite code as `file:line` where relevant.
   - No fluff, no emojis, no "Great progress today!"
   - Match the no-personal-content scope: work artifacts only. If today included non-engineering activity, omit it.

6. **Commit and push.** After appending the entry:
   - `cd ~/work-journal && git add -A && git commit -m "journal: <date> <short slug>"` — `add -A` on purpose: pending tasks/ideas/command-log changes ride along with the entry.
   - `git push`. If the push is rejected because the remote moved: `git pull --no-rebase`. If the merge conflicts, keep **both** sides of every conflicted hunk (ours then theirs, conflict markers removed — nothing from either side is dropped), then `git add -A && git commit --no-edit && git push`.
   - Never rebase, never force-push, never resolve a conflict by discarding a side.

## Notes

- This is additive — `/journal` can be invoked multiple times per session. Each adds a new dated section. The SessionEnd hook also adds a stub when the session terminates, so today's file may end up with N+1 entries.
- The SessionEnd hook and the task/ideas tooling still never commit — their uncommitted changes are picked up by the next `/journal` commit.
- If you're not in a git repo, still write the entry, but note `**cwd:**` as the bare path and skip the branch/commits sections.
