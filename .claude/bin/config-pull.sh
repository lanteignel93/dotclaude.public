#!/usr/bin/env bash
# config-pull.sh — nightly ff-only pull of your config-layer repos.
# Repo list: ~/.config/dotclaude/config-repos (one absolute or ~-path per
# line, # comments allowed). Missing list -> pulls ~/dotclaude only.
# Optional hooks: executables in ~/.config/dotclaude/post-pull.d/ run after
# a successful pull pass (drift checks, installs — your call).
# ff-only on purpose: a config repo with local commits should surface as a
# "diverged" log line for a human, never auto-merge.
# Log: ~/.local/state/config-pull.log
set -u
LOG="$HOME/.local/state/config-pull.log"
mkdir -p "$(dirname "$LOG")"
log() { printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$LOG"; }

LIST="$HOME/.config/dotclaude/config-repos"
repos=()
if [ -f "$LIST" ]; then
  while IFS= read -r line; do
    line="${line%%#*}"; line="$(echo "$line" | xargs)"
    [ -n "$line" ] && repos+=("${line/#\~/$HOME}")
  done < "$LIST"
else
  repos=("$HOME/dotclaude")
fi

rc=0
for repo in "${repos[@]}"; do
  if [ ! -d "$repo/.git" ]; then log "skip (not a repo): $repo"; continue; fi
  if out=$(git -C "$repo" pull --ff-only 2>&1); then
    log "pulled: $repo — $(echo "$out" | tail -1)"
  else
    log "DIVERGED or failed: $repo — $(echo "$out" | tail -1)"; rc=1
  fi
done

HOOKS="$HOME/.config/dotclaude/post-pull.d"
if [ -d "$HOOKS" ]; then
  for h in "$HOOKS"/*; do
    [ -x "$h" ] || continue
    if "$h" >> "$LOG" 2>&1; then log "hook ok: $(basename "$h")"
    else log "hook FAILED: $(basename "$h")"; rc=1; fi
  done
fi
exit $rc
