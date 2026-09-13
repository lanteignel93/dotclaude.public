# Troubleshooting

Symptom → diagnosis → fix, for the machinery on any server. Most failures are
one of: a broken symlink, a missing opt-in (`~/work-journal/`), or a missing
binary (`python3`, `gh`, `jq`).

## Symlinks / setup

- **Config changes don't show up on a server.** `cd ~/dotclaude && git pull`.
  Config is read per session — no Claude restart, but a *new* session.
- **Symlinks point at the wrong path.** Re-run
  `bash ~/dotclaude/deploy/setup-server.sh` — idempotent, backs up and
  relinks. Verify: `ls -la ~/.claude/{CLAUDE.md,settings.json,agents,commands,hooks}`
  should all resolve under `~/dotclaude/`.
- **Permission denied on `~/.claude/`.** Check ownership: `ls -ld ~/.claude/`.
- **Repo not at `~/dotclaude`.** The hooks and cron reference
  `$HOME/dotclaude/...` absolutely. Clone to `~/dotclaude` (or symlink it);
  anything else fails silently by design.

## Permissions

- **gh prompts despite the allowlist.** Check both
  `~/dotclaude/.claude/settings.json` and `~/.claude/settings.local.json` for
  the command (the latter shadows/extends the former).
- **gh not installed.** The allowlist assumes it: `sudo dnf install gh` /
  `sudo apt install gh`, then `gh auth login`.

## Tasks not surfacing at session start

The gate chain — each link fails silent, so walk it in order:

1. `~/work-journal/tasks.md` exists? (Opt-in:
   `mkdir -p ~/work-journal && cp ~/dotclaude/templates/tasks.md ~/work-journal/tasks.md`)
2. `~/dotclaude/.claude/bin/tasks.py` exists? (repo cloned at `~/dotclaude`)
3. `command -v python3` — present and ≥ 3.8?
4. Is anything actually due? An empty surfaced set injects nothing:
   `python3 ~/dotclaude/.claude/bin/tasks.py list`
5. Test the hook end-to-end:
   `echo '{}' | bash ~/.claude/hooks/session-start-tasks.sh` — should print a
   JSON object when tasks are due, nothing otherwise.
6. Hook wired? `~/.claude/settings.json` → `hooks.SessionStart` with matcher
   `startup|resume|clear`. The hooks *directory* is symlinked, but
   settings.json must be the symlinked one too.

## /task or /briefing misbehaving

- **`done` refuses with "unparseable recurrence rule".** Deliberate — a bad
  rule would silently kill the chain. Fix the rule against the table in
  `~/dotclaude/practices/tasks.md`, or drop the 🔁 field.
- **`done` exits 2 with candidates.** Ambiguous substring; re-run with
  `--line N`.
- **Emoji look corrupted in the file.** The engine always reads/writes UTF-8.
  If a hand edit corrupted encoding, fix the editor (must save UTF-8) and run
  `python3 ~/dotclaude/.claude/bin/tasks.py check`.
- **`check` reports "malformed checkbox".** A checkbox-shaped line the parser
  can't read (e.g. `-[ ]` missing the space). Fix the line; the listed line
  numbers are exact.
- **Rhythm alerts missing or stale.** `/briefing` reads
  `~/work-journal/command-log.tsv`. No file → commands were never logged on
  this machine (see next section). Log is per-server.

## Command log empty

`log-command.sh` (UserPromptSubmit) appends only when **all** hold:
`~/work-journal/` exists, `python3` is on PATH, and the prompt's first line
starts with `/<command>`. Test:
`echo '{"prompt":"/sweep"}' | bash ~/.claude/hooks/log-command.sh` then check
`tail ~/work-journal/command-log.tsv`. The hook always exits 0 — it will never
block a prompt, which also means it never complains.

## Journal

- **SessionEnd stub missing.** The hook gates on: cwd inside a git repo AND
  activity today (commits since midnight or a dirty tree). Both false → no
  entry, by design.
- **Nightly journal produced nothing.** Check `~/.claude/logs/journal-cron.log`
  and `journalctl --user -u journal-cron.service -n 50`. Common causes: the
  timer isn't installed (`systemctl --user list-timers` should show
  `journal-cron.timer`; install via `bash ~/dotclaude/deploy/install-systemd-timers.sh`),
  `claude` exceeded the `--max-budget-usd` ceiling in `journal-cron.sh`
  (large-transcript days; the log says `Exceeded USD budget`), no session
  transcripts today (it gates on `~/.claude/projects/*/*.jsonl` modified
  today), or the journal was touched within the last hour (dedup vs a manual
  `/journal`). A unit failure emails the address in `~/.config/dotclaude/alert.conf` via
  `failure-alert@` — no email and no entry usually means a gate, not a crash.
- **Timers not firing after reboot/logout.** `loginctl show-user $USER -p Linger`
  must be `yes` (the installer enables it). Also check
  `systemctl --user --failed`.
- **/briefing says the collector cache is stale.** Run
  `systemctl --user start briefing-collect.service` and check
  `journalctl --user -u briefing-collect.service`. The cache lives at
  `~/.claude/logs/briefing-cache.md`.

## Edits being denied

`read-before-edit.sh` (PreToolUse) denies Edit calls on files not Read earlier
in the session — that's the point. Read the file first. The per-session read
log lives at `/tmp/claude-reads-<session_id>.txt`.

## Python

- **No `python3` on the server.** Tasks machinery gates off silently; install
  ≥ 3.8 to enable it. Everything else (journal, plans, commands) works
  without it.
- **Engine test suite:** `python3 ~/dotclaude/tests/test_tasks.py` — 43
  passing tests is the healthy baseline.
