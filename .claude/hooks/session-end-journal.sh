#!/usr/bin/env bash
# SessionEnd hook for Claude Code.
# Appends a structured entry to ~/work-journal/daily_logs/<YYYY-MM-DD>.md.
# Gates on cwd being inside a git repo with activity today.

set -euo pipefail

JOURNAL_DIR="$HOME/work-journal/daily_logs"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
JOURNAL_FILE="$JOURNAL_DIR/$DATE.md"

CWD=$(pwd)

# Discard any stdin payload from the harness without blocking.
cat >/dev/null 2>&1 || true

# Gate 1: cwd must be inside a git repo. Non-repo sessions are presumed
# exploratory and not journal-worthy.
if ! git -C "$CWD" rev-parse --is-inside-work-tree --no-optional-locks >/dev/null 2>&1; then
  exit 0
fi

GIT_ROOT=$(git -C "$CWD" rev-parse --show-toplevel)
PROJECT=$(basename "$GIT_ROOT")
BRANCH=$(git -C "$CWD" symbolic-ref --short HEAD 2>/dev/null \
         || git -C "$CWD" rev-parse --short HEAD 2>/dev/null \
         || echo "unknown")

COMMITS=$(git -C "$CWD" log --since=midnight --oneline --no-decorate 2>/dev/null | head -10 || true)
DIRTY=$(git -C "$CWD" status --porcelain --no-optional-locks 2>/dev/null | head -10 || true)

# Gate 2: skip if there's no activity to record.
if [ -z "$COMMITS" ] && [ -z "$DIRTY" ]; then
  exit 0
fi

mkdir -p "$JOURNAL_DIR"
if [ ! -f "$JOURNAL_FILE" ]; then
  printf '# %s\n' "$DATE" > "$JOURNAL_FILE"
fi

SHORT_CWD="${CWD/#$HOME/\~}"

{
  printf '\n'
  printf '## %s — %s\n' "$TIME" "$PROJECT"
  printf '\n'
  printf '**cwd:** `%s`  \n' "$SHORT_CWD"
  printf '**branch:** `%s`\n' "$BRANCH"

  if [ -n "$COMMITS" ]; then
    printf '\n**Commits today (this repo):**\n\n'
    printf '```\n%s\n```\n' "$COMMITS"
  fi

  if [ -n "$DIRTY" ]; then
    printf '\n**Uncommitted at session end:**\n\n'
    printf '```\n%s\n```\n' "$DIRTY"
  fi

  printf '\n_(Run `/journal` for a richer summary — decisions, blockers, next.)_\n'
} >> "$JOURNAL_FILE"

exit 0
