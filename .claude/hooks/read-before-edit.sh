#!/usr/bin/env bash
# PreToolUse on Edit — deny if the target file_path has not been Read this session.
# Pairs with read-track.sh which records reads to /tmp/claude-reads-<session_id>.txt.
set -u
input=$(cat)
sid=$(jq -r '.session_id // "default"' <<<"$input")
f=$(jq -r '.tool_input.file_path // empty' <<<"$input")
[ -z "$f" ] && exit 0
log="/tmp/claude-reads-${sid}.txt"
if [ -f "$log" ] && grep -qxF -- "$f" "$log"; then
  exit 0
fi
jq -n --arg p "$f" '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    permissionDecision: "deny",
    permissionDecisionReason: ("Read " + $p + " with the Read tool before editing it.")
  }
}'
exit 0
