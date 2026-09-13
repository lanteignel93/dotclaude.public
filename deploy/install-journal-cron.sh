#!/usr/bin/env bash
# Idempotently install the journal-cron crontab entry for the current user.
# Schedule: daily 22:00 local time (override tz with JOURNAL_CRON_TZ).
# Run on each server where you want auto-journaling.
#
# FALLBACK PATH: prefer deploy/install-systemd-timers.sh (systemd user
# timers with catch-up + failure emails); it retires these cron entries.
# Use this installer only on boxes without a systemd user manager.

set -euo pipefail

DOTCLAUDE_DIR="${DOTCLAUDE_DIR:-$HOME/dotclaude}"
SCRIPT="$DOTCLAUDE_DIR/.claude/bin/journal-cron.sh"
LOG_DIR="$HOME/.claude/logs"
LOG="$LOG_DIR/journal-cron.log"

if [ ! -x "$SCRIPT" ]; then
  echo "ERROR: $SCRIPT not found or not executable" >&2
  echo "Make sure dotclaude is checked out at $DOTCLAUDE_DIR (or set DOTCLAUDE_DIR=...)" >&2
  exit 1
fi

mkdir -p "$LOG_DIR"

# Build the desired crontab lines.
TZ_LINE=${JOURNAL_CRON_TZ:+CRON_TZ=$JOURNAL_CRON_TZ}
CRON_LINE="0 22 * * * $SCRIPT >> $LOG 2>&1"
MARKER='# journal-cron (managed by dotclaude/deploy/install-journal-cron.sh)'

# Snapshot current crontab (or empty if none).
CURRENT=$(crontab -l 2>/dev/null || true)

# Strip any existing managed block so we can re-install cleanly.
NEW=$(printf '%s\n' "$CURRENT" | awk -v m="$MARKER" '
  $0 == m { skip = 3; next }   # skip the marker + next 2 lines (CRON_TZ + schedule)
  skip > 0 { skip--; next }
  { print }
')

# Append the managed block.
NEW=$(printf '%s\n%s\n%s\n%s\n' "$NEW" "$MARKER" "$TZ_LINE" "$CRON_LINE")

# Install.
printf '%s\n' "$NEW" | crontab -

echo "Installed:"
echo "  $TZ_LINE"
echo "  $CRON_LINE"
echo ""
echo "Verify with: crontab -l"
echo "Logs at:     $LOG"
echo "Test now:    $SCRIPT --dry-run"
