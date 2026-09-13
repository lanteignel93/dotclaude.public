#!/usr/bin/env bash
# install-systemd-timers.sh — install/refresh the dotclaude systemd user
# timers: journal-sync (18:30/22:30 M-F), journal-cron (22:00 daily),
# briefing-collect (07:15 M-F), plus the ntfy-alert@ OnFailure hook.
# Replaces the cron entries previously installed by install-journal-cron.sh
# (those lines are retired from crontab; a backup is kept). Idempotent:
# re-run after editing any unit under deploy/systemd/.
#
# Why systemd over cron: Persistent=true catches up runs missed while a
# box was down (cron silently skips them, which loses cross-box sync
# days), journald captures output without per-line redirects, and
# OnFailure= turns silent breakage into a phone alert (ntfy topic in
# ~/.config/ntfy/topic; no topic file -> alerts are a no-op).
#
# Boxes without a systemd user manager keep cron: install-journal-cron.sh.
set -euo pipefail

UNIT_SRC="$(cd "$(dirname "$0")/systemd" && pwd)"
UNIT_DST="$HOME/.config/systemd/user"

if ! systemctl --user show-environment >/dev/null 2>&1; then
    echo "No systemd user manager on this box; keep cron (install-journal-cron.sh)." >&2
    exit 1
fi

# symlink dangles and mkdir -p on it fails. Create the target first.
if [ -L "$UNIT_DST" ] && [ ! -e "$UNIT_DST" ]; then
    mkdir -p "$(readlink "$UNIT_DST")"
fi
mkdir -p "$UNIT_DST"
for u in "$UNIT_SRC"/*.service "$UNIT_SRC"/*.timer; do
    install -m 644 "$u" "$UNIT_DST/$(basename "$u")"
done
systemctl --user daemon-reload

for t in journal-sync.timer journal-cron.timer briefing-collect.timer config-pull.timer; do
    systemctl --user enable --now "$t"
done

# Timers must survive logout/reboot without an active session.
if [ "$(loginctl show-user "$USER" -p Linger --value 2>/dev/null)" != "yes" ]; then
    loginctl enable-linger "$USER" 2>/dev/null \
        || echo "NOTE: enable-linger failed; timers only fire while a session exists." >&2
fi

# Retire the cron entries these timers replace (backup kept; other cron
# jobs untouched).
if crontab -l >/dev/null 2>&1; then
    if crontab -l | grep -qE "dotclaude/.claude/bin/(journal-cron|journal-sync)\.sh"; then
        backup="$HOME/.claude/logs/crontab.backup.$(date +%Y%m%d%H%M%S)"
        mkdir -p "$(dirname "$backup")"
        crontab -l > "$backup"
        crontab -l \
            | grep -v "journal-cron (managed by dotclaude" \
            | grep -v "dotclaude/.claude/bin/journal-cron.sh" \
            | grep -v "dotclaude/.claude/bin/journal-sync.sh" \
            | crontab -
        echo "Retired dotclaude cron entries (backup: $backup)."
    fi
fi

echo "Installed. Verify: systemctl --user list-timers"
