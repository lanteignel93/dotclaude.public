#!/usr/bin/env bash
# PostToolUse on Read — record which files have been read this session.
# Read by read-before-edit.sh to decide whether to allow an Edit.
set -u
input=$(cat)
sid=$(jq -r '.session_id // "default"' <<<"$input")
f=$(jq -r '.tool_input.file_path // empty' <<<"$input")
if [ -n "$f" ]; then
  echo "$f" >>"/tmp/claude-reads-${sid}.txt"
fi
exit 0
