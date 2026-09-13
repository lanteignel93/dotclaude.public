#!/usr/bin/env bash
# UserPromptSubmit hook: append slash-command invocations to
# ~/work-journal/command-log.tsv (timestamp, host, cwd, command).
# /briefing reads this to alert on overdue cadenced commands.
# Must never block a prompt — every path exits 0.

LOG_FILE="$HOME/work-journal/command-log.tsv"

if [ ! -d "$HOME/work-journal" ] || ! command -v python3 >/dev/null 2>&1; then
  cat >/dev/null 2>&1 || true
  exit 0
fi

# Program via -c: stdin stays reserved for the hook payload JSON.
python3 -c '
import json
import os
import re
import socket
import sys
from datetime import datetime

try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)
prompt = str(payload.get("prompt", ""))
first = " ".join(prompt.strip().split("\n", 1)[0].split())
if not re.match(r"^/[a-z][a-z-]*(\s|$)", first):
    sys.exit(0)
line = "\t".join([
    datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    socket.gethostname(),
    str(payload.get("cwd", os.getcwd())),
    first,
])
with open(sys.argv[1], "a", encoding="utf-8") as f:
    f.write(line + "\n")
' "$LOG_FILE" || true

exit 0
