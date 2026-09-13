#!/usr/bin/env bash
# Symlink dotclaude config into ~/.claude/
# Idempotent: safe to re-run.

set -euo pipefail

DOTCLAUDE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_DIR="${HOME}/.claude"

mkdir -p "${CLAUDE_DIR}"

backup_or_clear() {
  local target="$1"
  if [[ -L "$target" ]]; then
    rm "$target"
    echo "Removed existing symlink: $target"
  elif [[ -e "$target" ]]; then
    local bak="${target}.bak.$(date +%Y%m%d-%H%M%S)"
    mv "$target" "$bak"
    echo "Backed up: $target -> $bak"
  fi
}

link() {
  local source="$1"
  local target="$2"
  backup_or_clear "$target"
  ln -s "$source" "$target"
  echo "Linked: $target -> $source"
}

link "${DOTCLAUDE_DIR}/CLAUDE.md"                        "${CLAUDE_DIR}/CLAUDE.md"
link "${DOTCLAUDE_DIR}/.claude/settings.json"            "${CLAUDE_DIR}/settings.json"
link "${DOTCLAUDE_DIR}/.claude/statusline-command.sh"    "${CLAUDE_DIR}/statusline-command.sh"
link "${DOTCLAUDE_DIR}/.claude/agents"                   "${CLAUDE_DIR}/agents"
link "${DOTCLAUDE_DIR}/.claude/commands"                 "${CLAUDE_DIR}/commands"
link "${DOTCLAUDE_DIR}/.claude/hooks"                    "${CLAUDE_DIR}/hooks"
link "${DOTCLAUDE_DIR}/.claude/themes"                   "${CLAUDE_DIR}/themes"

echo ""
echo "Setup complete. Start a new Claude session to load the config."
echo "To update later: cd ${DOTCLAUDE_DIR} && git pull"
