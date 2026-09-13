#!/usr/bin/env bash
# briefing-collect.sh — pre-briefing collector. Gathers overnight-job
# health, repo state, and GitHub PR state into a cache that /briefing
# reads instead of gathering live. Runs from briefing-collect.timer
# (weekday mornings) but is safe to run by hand any time.
# Output: ~/.claude/logs/briefing-cache.md (overwritten).
#
# Job table: ~/.config/dotclaude/briefing-jobs.tsv — tab-separated:
#   name <TAB> log_path <TAB> max_age_hours <TAB> error_regex [<TAB> success_regex]
# Lines starting with # are comments. No file -> section reports that and
# moves on. An error line is suppressed as "recovered" when a line
# matching success_regex appears LATER in the tail window (a retried job
# that ultimately succeeded is not a morning alarm).
#
# Repo table: ~/.config/dotclaude/config-repos (shared with config-pull),
# plus ~/work-journal and ~/dotclaude always.
set -u
OUT="$HOME/.claude/logs/briefing-cache.md"
mkdir -p "$(dirname "$OUT")"
: > "$OUT"
say() { printf '%s\n' "$*" >> "$OUT"; }

say "# Briefing cache — generated $(date '+%Y-%m-%d %H:%M %Z') on $(hostname -s)"
say ""

# ---- systemd user units -------------------------------------------------
say "## Failed units / timers"
failed=$(systemctl --user --failed --no-legend 2>/dev/null | sed 's/●//g')
if [ -n "$failed" ]; then
    say '```'; say "$failed"; say '```'
else
    say "- no failed user units"
fi
say ""

# ---- overnight job health ------------------------------------------------
# check_log <name> <path> <max_age_hours> <error_rx> [<success_rx>]
check_log() {
    local name="$1" path="$2" max_h="$3" rx="$4" ok_rx="${5:-}"
    path="${path/#\~/$HOME}"
    if [ ! -f "$path" ]; then
        say "- $name: no log at $path"
        return
    fi
    local age_h=$(( ( $(date +%s) - $(stat -c %Y "$path") ) / 3600 ))
    local flag=""
    [ "$age_h" -gt "$max_h" ] && flag=" [STALE: last write ${age_h}h ago]"
    local win errs
    win=$(tail -n 60 "$path")
    # recovered? a success marker after the LAST error line clears the alarm
    if [ -n "$ok_rx" ]; then
        local last_err last_ok
        last_err=$(printf '%s\n' "$win" | grep -inE "$rx" | tail -1 | cut -d: -f1)
        last_ok=$(printf '%s\n' "$win" | grep -inE "$ok_rx" | tail -1 | cut -d: -f1)
        if [ -n "$last_err" ] && [ -n "$last_ok" ] && [ "$last_ok" -gt "$last_err" ]; then
            say "- $name: ok (errors present but recovered)$flag"
            return
        fi
    fi
    local d0 d1 d2
    d0=$(date +%F); d1=$(date -d yesterday +%F); d2=$(date -d '2 days ago' +%F)
    errs=$(printf '%s\n' "$win" | grep -iE "$rx" \
        | awk -v a="$d0" -v b="$d1" -v c="$d2" \
            'match($0, /20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]/) { if (index($0,a) || index($0,b) || index($0,c)) print; next } { print }' \
        | tail -n 3)
    if [ -n "$errs" ]; then
        say "- $name: RECENT ERRORS$flag"
        say '```'; say "$errs"; say '```'
    else
        say "- $name: ok (last write ${age_h}h ago)$flag"
    fi
}

say "## Overnight job health"
JOBS="$HOME/.config/dotclaude/briefing-jobs.tsv"
if [ -f "$JOBS" ]; then
    while IFS=$'\t' read -r name path max_h rx ok_rx; do
        case "$name" in ''|\#*) continue ;; esac
        check_log "$name" "$path" "${max_h:-30}" "${rx:-error|fail|traceback}" "${ok_rx:-}"
    done < "$JOBS"
else
    say "- no job table at $JOBS (see deploy/examples/briefing-jobs.tsv)"
fi
# the kit's own timers, always checked when their logs exist
[ -f "$HOME/.claude/logs/journal-cron.log" ] && \
    check_log "journal-cron (nightly)" "$HOME/.claude/logs/journal-cron.log" 30 \
        "error|fail|exceeded" "^Appended|done$"
[ -f "$HOME/.local/state/journal-sync.log" ] && \
    check_log "journal-sync" "$HOME/.local/state/journal-sync.log" 70 \
        "FAILED|CONFLICT|diverged" "synced OK"
[ -f "$HOME/.local/state/config-pull.log" ] && \
    check_log "config-pull" "$HOME/.local/state/config-pull.log" 30 \
        "DIVERGED|FAILED" "pulled:"
say ""

# ---- repo state ------------------------------------------------------------
say "## Repos"
repo_state() {
    local repo="$1"; [ -d "$repo/.git" ] || return 0
    local name dirty ahead behind
    name=$(basename "$repo")
    dirty=$(git -C "$repo" status --porcelain 2>/dev/null | wc -l)
    ahead=$(git -C "$repo" rev-list --count @{u}..HEAD 2>/dev/null || echo "?")
    behind=$(git -C "$repo" rev-list --count HEAD..@{u} 2>/dev/null || echo "?")
    say "- $name ($(git -C "$repo" branch --show-current 2>/dev/null)): $dirty dirty, $ahead ahead, $behind behind upstream"
}
repo_state "$HOME/work-journal"
repo_state "$HOME/dotclaude"
LIST="$HOME/.config/dotclaude/config-repos"
if [ -f "$LIST" ]; then
    while IFS= read -r line; do
        line="${line%%#*}"; line="$(echo "$line" | xargs)"; [ -n "$line" ] || continue
        line="${line/#\~/$HOME}"
        case "$line" in "$HOME/work-journal"|"$HOME/dotclaude") continue ;; esac
        repo_state "$line"
    done < "$LIST"
fi
say ""

# ---- GitHub PRs -------------------------------------------------------------
say "## GitHub PRs"
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    me=$(gh api user -q .login 2>/dev/null)
    say "(account: ${me:-unknown})"
    say "### Awaiting my review"
    gh search prs --review-requested="$me" --state=open \
        --json repository,number,title,updatedAt \
        -q '.[] | "- \(.repository.nameWithOwner)#\(.number): \(.title)"' \
        2>/dev/null | head -15 >> "$OUT" || say "- (query failed)"
    say "### My open PRs"
    gh search prs --author="$me" --state=open \
        --json repository,number,title,updatedAt \
        -q '.[] | "- \(.repository.nameWithOwner)#\(.number): \(.title)"' \
        2>/dev/null | head -20 >> "$OUT" || say "- (query failed)"
else
    say "- gh not available/authenticated; PR section skipped"
fi

echo "wrote $OUT"
