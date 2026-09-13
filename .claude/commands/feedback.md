---
description: Record received feedback (Slack/PR/meeting/chat) into ~/work-journal/feedback.md
---

Explicit trigger for the feedback log at `~/work-journal/feedback.md`.
(The default is ambient: per CLAUDE.md, Claude extracts feedback on sight
from anything you share — this command is for "log this one"
moments or pasted material outside a normal flow.)

Arguments: pasted material (Slack thread, PR review, transcript excerpt)
and/or a hint about who/where it came from.

## Steps

1. **Distill the nugget(s).** From the material, extract the constructive
   or useful feedback directed at the user or his work: advice, corrections,
   review patterns, process principles, methodology guidance. Multiple
   distinct nuggets from one exchange = one dated entry with grouped
   points, or separate entries if the sources differ.

2. **Append newest-first** under the header format:
   `## YYYY-MM-DD — <person> (<role>, <source: slack|PR|meeting|chat>)`
   followed by the distilled feedback (quote short originals verbatim) and
   a `_source: ..._` line (link, path, or meeting-note reference).

3. **Person is metadata, never the organizing key** — one log, no
   per-person files.

4. **If the feedback is behavioral guidance for Claude itself** (how to
   work with the user), also update Claude memory and cross-reference the
   feedback.md entry.

5. **Report** in one line what was recorded.

## Do not

- Do not commit — journal cadence.
- Do not log anything covered by a standing confidentiality guardrail
  (check memory) — held-close exchanges never enter this file.
