# Installation

~20 minutes. Two repos: this one (machinery) and `work-journal` (your
private data scaffold).

## 0. Prerequisites

- `git`, `python3` ≥ 3.8, `jq`
- [Claude Code CLI](https://claude.com/claude-code) installed and logged in
- `gh` (GitHub CLI) — optional, powers the PR sections of `/briefing`
- `uv` — optional, only for running the test suite
- Linux with a systemd user manager for the timers (macOS/no-systemd:
  use the cron fallback)

## 1. Clone

```bash
git clone <this-repo-url> ~/dotclaude
git clone <work-journal-template-url> ~/work-journal
```

Make your `~/work-journal` clone PRIVATE (it will fill with your
employer's context): point it at a fresh private remote of your own —

```bash
cd ~/work-journal && git remote set-url origin <your-private-remote>
git push -u origin master
```

## 2. Wire into Claude Code

```bash
bash ~/dotclaude/deploy/setup-server.sh
```

Symlinks `~/.claude/{CLAUDE.md,commands,hooks,statusline-command.sh}` and
merges `settings.json`. Idempotent — rerun after pulling updates.

## 3. Personalize (do not skip)

1. `~/dotclaude/CLAUDE.md` — fill every `EDIT ME` section: who you are,
   code-style stack, value hierarchy.
2. `~/dotclaude/.claude/settings.json` — review the permission allowlist.
   The `~/`-based Read/Edit rules require a recent Claude Code; if rules
   don't take effect, replace `~` with your absolute home path.
3. `agents/` — read `agents/README.md`; fill the `<YOU — edit this line>`
   markers in the three role files; write your domain file from the
   template when ready.

## 4. Smoke test

```bash
python3 ~/dotclaude/.claude/bin/tasks.py check      # "ok — N task(s)"
python3 ~/dotclaude/.claude/bin/tasks.py add "try the board" --due $(date +%F)
claude   # open a session anywhere: the greeting lists commands,
         # and the due task is injected at session start
```

Then `/task done try the board` inside the session.

## 5. Scheduled automation (optional, recommended once the habit sticks)

```bash
bash ~/dotclaude/deploy/install-systemd-timers.sh
systemctl --user list-timers   # journal-sync, journal-cron, briefing-collect, config-pull
```

- Installs four user timers + failure alerting, enables linger (timers
  survive logout).
- Configure the pieces (all optional, all no-op silently when absent):
  - `~/.config/dotclaude/briefing-jobs.tsv` — overnight jobs the morning
    collector should health-check (`deploy/examples/briefing-jobs.tsv`)
  - `~/.config/dotclaude/config-repos` — repos config-pull ff-pulls
  - `~/.config/dotclaude/alert.conf` — email relay for failure alerts
- No systemd user manager? `bash deploy/install-journal-cron.sh` installs
  the nightly journal via cron instead (set `JOURNAL_CRON_TZ` if your
  server TZ differs from your working TZ).

### ⚠ journal-cron costs API money

The nightly journal writer runs headless `claude` over the day's session
transcripts. It carries `--max-budget-usd` (default in the script) — keep
a ceiling you're comfortable paying nightly, watch
`~/.claude/logs/journal-cron.log` for the first week, and know that
`Exceeded USD budget` in that log means the ceiling stopped a run, not a
crash. Skip this timer entirely if you don't want nightly spend; the
SessionEnd hook + `/journal` cover the essentials for free.

## 6. First real day

Read [WORKFLOW.md](WORKFLOW.md), then just work: `/briefing` in the
morning, `/task` as things come up, `/journal` before you stop. The rest
accretes.

## Troubleshooting

[docs/troubleshooting.md](docs/troubleshooting.md) — hooks silent, timers
not firing, command log empty, edits denied, etc.
