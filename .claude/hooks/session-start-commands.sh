#!/usr/bin/env bash
# SessionStart hook: show the custom slash commands and their one-line
# purposes (from each command file's frontmatter description). Gates
# silently when the commands dir or jq is absent.

set -euo pipefail

CMD_DIR="$HOME/.claude/commands"

# Discard any stdin payload from the harness without blocking.
cat >/dev/null 2>&1 || true

[ -d "$CMD_DIR" ] || exit 0
command -v jq >/dev/null 2>&1 || exit 0

msg="Custom commands:"
found=0
for f in "$CMD_DIR"/*.md; do
  [ -e "$f" ] || continue
  name="/$(basename "$f" .md)"
  desc=$(awk '/^description:/ {sub(/^description:[ \t]*/,""); print; exit}' "$f")
  msg+=$'\n'"  $(printf '%-18s' "$name") ${desc:-—}"
  found=1
done

[ "$found" -eq 1 ] || exit 0

jq -cn --arg m "$msg" '{systemMessage: $m, suppressOutput: true}'
