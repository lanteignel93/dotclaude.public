You are running NON-INTERACTIVELY as a scheduled cron job at 22:00 local time on host `{{HOST}}`. Date is `{{DATE}}`. There is no human watching — do the work and exit.

# Your task

Produce a consolidated engineering-journal entry for today's work on this host and append it to `~/work-journal/daily_logs/{{DATE}}.md`.

# Steps

1. **Target file.** `~/work-journal/daily_logs/{{DATE}}.md`. If it doesn't already exist, write the header line `# {{DATE}}` AND your full entry in a SINGLE Write call (don't create an empty file then Edit it — write it all at once). If it already exists, Read it FIRST and note which projects are already covered by manual `/journal` entries today — those projects are ALREADY JOURNALED and their transcripts must not be read beyond the verification tail described below.

2. **Find that day's session transcripts.** Glob `~/.claude/projects/*/*.jsonl`, filtered to files modified on `{{DATE}}` — i.e. at or after `{{DATE}} 00:00` AND strictly before `{{NEXT}} 00:00` local time. Each file is one Claude session's full conversation log. The parent dir's name is a sanitized form of the project's cwd (slashes become dashes — e.g. `-home-you-yourproject` → `/home/you/yourproject`). **File mtime lies for resumed sessions**: a session touched today may contain zero content from today. Before reading any transcript, verify it has message timestamps dated {{DATE}} cheaply (grep for `"{{DATE}}T` in the file, or read only its tail); exclude files that don't.

3. **Group by project.** For each transcript, the parent dir tells you the project cwd. Group transcripts by project. A single project may have multiple sessions today.

4. **Filter to projects with real activity — under a strict reading budget.**
   - Projects already covered by a manual entry (step 1): read ONLY the transcript tail (last ~200 lines) to check for post-entry work; if the tail shows nothing after the manual entry's timeframe, skip the project with a one-line note. Never read such a transcript in full.
   - Transcripts larger than ~2 MB: never read in full, covered or not. Use the tail plus targeted greps (Edit/Write calls, `git commit`, decision language) to synthesize.
   - If the work is large, prioritize completeness for UNCOVERED projects over perfection: a finished entry for the unjournaled work beats an exhaustive read that exhausts the budget mid-run.

   Skip projects that were purely exploratory (only Reads, no Edits/Writes/Bash mutations, no decisions). Keep projects where:
   - Files were modified (Edit/Write tool calls)
   - Git activity happened (commits, PRs, pushes)
   - Substantive decisions or design discussions occurred
   - Bugs were investigated and resolved (or punted with reasoning)

5. **For each kept project, synthesize a terse entry.** Match the existing `/journal` style:
   - **What was done** — past-tense bullets, concrete files/decisions. Cite `path:line` when useful.
   - **Decisions** — only if there were meaningful tradeoffs.
   - **Open / blocked** — only if applicable.
   - **Next** — explicit next action if obvious from the session ending.

   Drop any section that would be empty. Don't pad with "n/a".

6. **Append ONE consolidated section** to `~/work-journal/daily_logs/{{DATE}}.md`:

   ```
   
   ## 22:00 — {{HOST}} (auto via cron)
   
   ### <project-name-1>
   
   **What was done**
   - …
   
   **Decisions**
   - …
   
   **Next**
   - …
   
   ### <project-name-2>
   …
   ```

   Use `basename` of the project cwd as `<project-name>` (e.g. `dotclaude`, not `-home-you-yourproject`).

# Hard constraints

- **Do NOT commit.** The journal is a git repo but the user reviews and commits manually.
- **Do NOT touch files outside `~/work-journal/`.** Read transcripts, write the one journal file. Nothing else.
- **Do NOT create new files except the journal file itself.**
- **Terse.** No fluff, no emojis, no "Great work today!" No paragraphs where bullets work.
- **If there's nothing meaningful to journal** (e.g. all of today's sessions were trivial reads or aborted), exit without writing anything. Print a one-line explanation to stdout.
