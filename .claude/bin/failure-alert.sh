#!/usr/bin/env bash
# failure-alert.sh — email an alert when a systemd user unit fails.
# Wired via OnFailure=failure-alert@%n.service in the dotclaude units.
# Usage: failure-alert.sh <unit-name>
#
# Primary channel: email to ALERT_EMAIL through your internal
# SMTP relay (an unauthenticated internal relay, port 25).
# Fallback: ntfy push if the email fails and ~/.config/ntfy/topic exists.
# Overrides via ~/.config/dotclaude/alert.conf (shell syntax):
#   ALERT_EMAIL=... SMTP_RELAY=...
set -u
unit="${1:-unknown-unit}"

ALERT_EMAIL=""   # set in ~/.config/dotclaude/alert.conf
SMTP_RELAY=""    # set in ~/.config/dotclaude/alert.conf
conf="$HOME/.config/dotclaude/alert.conf"
[ -r "$conf" ] && . "$conf"

host=$(hostname -s)
ALERT_TAIL=$(journalctl --user -u "$unit" -n 30 --no-pager 2>/dev/null || echo "journalctl unavailable")
export ALERT_TAIL

if [ -z "$ALERT_EMAIL" ] || [ -z "$SMTP_RELAY" ]; then
    # not configured -> silently no-op (alerts are opt-in)
    exit 0
fi

if python3 - "$unit" "$host" "$ALERT_EMAIL" "$SMTP_RELAY" <<'PYEOF' >/dev/null 2>&1
import smtplib, sys, os
from email.mime.text import MIMEText

unit, host, to_addr, relay = sys.argv[1:5]
body = (
    f"systemd user unit failed: {unit}\n"
    f"host: {host}\n\n"
    f"Last 30 journal lines:\n"
    + os.environ.get("ALERT_TAIL", "(none)")
    + f"\n\nInspect: journalctl --user -u {unit} -n 50\n"
)
msg = MIMEText(body)
msg["Subject"] = f"[claude-workflow] {host}: {unit} failed"
msg["From"] = to_addr
msg["To"] = to_addr
with smtplib.SMTP(relay, timeout=15) as s:
    s.send_message(msg)
PYEOF
then
    exit 0
fi

# Email failed (relay unreachable from this box?) — best-effort ntfy push.
topic_file="$HOME/.config/ntfy/topic"
if [ -r "$topic_file" ]; then
    topic=$(head -n1 "$topic_file" | tr -d '[:space:]')
    [ -n "$topic" ] && curl -fsS -m 10 \
        -H "Title: $host: $unit failed (email alert also failed)" \
        -H "Priority: high" \
        -d "Inspect with: journalctl --user -u $unit -n 50" \
        "https://ntfy.sh/$topic" >/dev/null
fi
exit 0
