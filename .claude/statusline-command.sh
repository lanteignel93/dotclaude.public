#!/usr/bin/env bash
# Claude Code statusLine — mirrors p10k darkvoid theme
# Colors: lime #bdfe58, sea-green #5EEEAF, lavender #E5CCFF, fg #c0c0c0

input=$(cat)

# --- Data extraction ---
host=$(hostname -s)
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd')
model=$(echo "$input" | jq -r '.model.display_name')
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
session_used=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
week_used=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')

# Shorten cwd: replace $HOME with ~
short_cwd="${cwd/#$HOME/\~}"

# Git branch + dirty state (skip optional locks)
git_branch=""
git_dirty=""
if git -C "$cwd" rev-parse --is-inside-work-tree --no-optional-locks 2>/dev/null | grep -q true; then
  git_branch=$(git -C "$cwd" symbolic-ref --short HEAD 2>/dev/null || git -C "$cwd" rev-parse --short HEAD 2>/dev/null)
  git_status=$(git -C "$cwd" status --porcelain --no-optional-locks 2>/dev/null)
  if [ -n "$git_status" ]; then
    git_dirty="*"
  fi
fi

# ANSI 24-bit color helpers
lime='\033[38;2;189;254;88m'
sea='\033[38;2;94;238;175m'
lavender='\033[38;2;229;204;255m'
fg='\033[38;2;192;192;192m'
reset='\033[0m'

# --- Build the line ---
# Format: $(whoami)  host  ~/path   branch*   model  ctx%  HH:MM

parts=""

# Identity / host (lavender)
parts="${parts}$(printf "${lavender}$(whoami) %s${reset}" "$host")"

# Directory (lime)
parts="${parts}  $(printf "${lime}%s${reset}" "$short_cwd")"

# Git (sea-green)
if [ -n "$git_branch" ]; then
  parts="${parts}  $(printf "${sea} %s%s${reset}" "$git_branch" "$git_dirty")"
fi

# Virtualenv (lime, best-effort from env)
active_venv="${VIRTUAL_ENV##*/}"
if [ -n "$active_venv" ]; then
  parts="${parts}  $(printf "${lime}(%s)${reset}" "$active_venv")"
fi

# Model (fg)
parts="${parts}  $(printf "${fg}%s${reset}" "$model")"

# Context usage — lime if < 80%, lavender if >= 80%
if [ -n "$used_pct" ]; then
  int_pct=$(printf '%.0f' "$used_pct")
  if [ "$int_pct" -ge 80 ]; then
    ctx_color="$lavender"
  else
    ctx_color="$lime"
  fi
  parts="${parts}  $(printf "${ctx_color}ctx:%d%%${reset}" "$int_pct")"
fi

# Usage limits remaining (Pro/Max rate limits) — lime if >20% left, lavender otherwise
usage_seg=""
if [ -n "$session_used" ]; then
  session_left=$(printf '%.0f' "$(echo "100 - $session_used" | bc -l)")
  [ "$session_left" -le 20 ] && u_color="$lavender" || u_color="$lime"
  usage_seg="$(printf "${u_color}5h:%d%%${reset}" "$session_left")"
fi
if [ -n "$week_used" ]; then
  week_left=$(printf '%.0f' "$(echo "100 - $week_used" | bc -l)")
  [ "$week_left" -le 20 ] && u_color="$lavender" || u_color="$lime"
  [ -n "$usage_seg" ] && usage_seg="${usage_seg} "
  usage_seg="${usage_seg}$(printf "${u_color}wk:%d%%${reset}" "$week_left")"
fi
if [ -n "$usage_seg" ]; then
  parts="${parts}  ${usage_seg}"
fi

# Time (lime)
parts="${parts}  $(printf "${lime}%s${reset}" "$(date +%H:%M)")"

printf "%b\n" "$parts"
