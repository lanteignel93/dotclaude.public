#!/usr/bin/env bash
# Scheduled journal-writer. Runs headless `claude` at 22:00 CT (cron-installed)
# to consolidate a day's session transcripts into ~/work-journal/daily_logs/<date>.md.
#
# Usage:
#   journal-cron.sh                 # journal today
#   journal-cron.sh --date 2026-05-27   # backfill a specific day
#   journal-cron.sh --dry-run       # gate-check + print prompt, don't invoke claude
#   (flags combine: --dry-run --date 2026-05-27)

set -euo pipefail

DRY_RUN=0
DATE=$(date +%F)
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --date)    DATE="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

# Cron has a minimal PATH; ~/.local/bin holds the claude binary.
export PATH="$HOME/.local/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROMPT_FILE="$SCRIPT_DIR/journal-cron-prompt.md"
LOCK=/tmp/claude-journal-cron.lock

HOST=$(hostname -s)
JOURNAL="$HOME/work-journal/daily_logs/$DATE.md"
NEXT=$(date -d "$DATE + 1 day" +%F)
mkdir -p "$(dirname "$JOURNAL")"

log() { printf '%s %s\n' "$(date -Is)" "$*"; }

# Lock — don't overlap with a still-running prior fire.
exec 200>"$LOCK"
if ! flock -n 200; then
  log "lock held by another run; exiting"
  exit 0
fi

# Gate 1: any session transcripts modified ON or AFTER $DATE? No upper bound:
# a transcript resumed after the target day still contains that day's content
# (upper-bounding to the single day made backfills report "no activity" for
# days whose sessions were later resumed). Content-date filtering is the
# prompt's job — it greps message timestamps before reading anything.
if ! find "$HOME/.claude/projects" -name '*.jsonl' \
       -newermt "$DATE 00:00" 2>/dev/null | grep -q .; then
  log "no session activity on $DATE for $HOST; exiting"
  exit 0
fi

# Gate 2: was the journal already written/modified in the last hour?
# Cheap dedup if you ran /journal manually at 21:55 and cron fires at 22:00.
# Skipped for backfills (an old journal won't be recently modified anyway).
if [ -f "$JOURNAL" ] && [ "$(find "$JOURNAL" -mmin -60 2>/dev/null | wc -l)" -gt 0 ]; then
  log "$JOURNAL modified in last hour; exiting (assume manual /journal already ran)"
  exit 0
fi

# Substitute {{DATE}}, {{HOST}}, {{NEXT}} into the prompt template.
PROMPT=$(sed -e "s|{{DATE}}|$DATE|g" -e "s|{{HOST}}|$HOST|g" -e "s|{{NEXT}}|$NEXT|g" "$PROMPT_FILE")

if [ "$DRY_RUN" -eq 1 ]; then
  log "DRY RUN: gates passed; would invoke claude with the following prompt:"
  printf -- '----- PROMPT -----\n%s\n----- END -----\n' "$PROMPT"
  exit 0
fi

log "invoking headless claude for $HOST/$DATE"

# Start from a deterministic cwd so workspace scoping doesn't depend on caller.
cd "$HOME"

# Prompt is piped via stdin — NOT passed as a positional arg. A positional prompt
# placed after variadic --add-dir gets swallowed by the flag (the original bug).
# stdin sidesteps that entirely, so --add-dir is now safe to use.
# --print: non-interactive | acceptEdits: auto-approve writes within allowed dirs
# --model sonnet: cheaper than opus, sufficient | --no-session-persistence: don't
# pollute the session picker | --max-budget-usd: hard cost ceiling per fire
# ($2 blew three nights running 08-22..24 on large-transcript days; $5 blew
# 08-26 at $5.07 re-reading transcripts of already-manually-journaled sessions.
# The prompt now forbids full reads of covered/oversized transcripts; $8 is
# headroom on top of that, failure emails via OnFailure)
# --add-dir: grant read of transcripts + write of the journal regardless of cwd.
set +e
printf '%s' "$PROMPT" | claude \
  --print \
  --permission-mode acceptEdits \
  --model sonnet \
  --no-session-persistence \
  --max-budget-usd 8.00 \
  --add-dir "$HOME/.claude/projects" "$HOME/work-journal"
rc=$?
set -e

if [ "$rc" -ne 0 ]; then
  log "claude exited non-zero: $rc"
  exit "$rc"
fi
log "done"
