---
description: Cross-project dashboard — show, update, or retire blocks in ~/work-journal/projects.md
---

Manage `~/work-journal/projects.md` — one block per active project, the
state that spans sessions. The SessionStart hook injects the block whose
slug (or `**aka:**` alias) matches the repo a session opens in, so every
instance boots knowing its project's thread, next action, and blockers.

## Block format

```markdown
## <repo-basename> — <active|paused>
- **aka:** other-checkout-name        (optional; matcher honors it)
- **thread:** the current line of work, one sentence
- **next:** the concrete next action(s)
- **blocked:** what it's waiting on   (omit if nothing)
- **links:** research notes · PRs · plans
- _updated YYYY-MM-DD_
```

The slug must be a repo checkout basename or the block never injects.
Retired blocks move under `## Archive` (keep the text, add `archived
YYYY-MM-DD`); never delete.

## Behavior

- **No arguments** → show the dashboard: one line per block (slug, status,
  thread, days since updated), flag blocks not updated in >14d, and any
  block whose slug matches no repo seen in recent journal entries.
- **"update <project> ..."** → rewrite the named block's fields from the
  user's words (or from session context if invoked mid-work), bump
  `_updated_`.
- **"add <project>"** → new block; ask only for what can't be inferred
  (thread/next). Confirm the slug matches the checkout basename.
- **"retire/archive <project>"** → move the block to `## Archive` with an
  archived date.
- Conversational like `/project-clean-up`: propose, confirm, apply.

## Boundaries

- projects.md holds cross-session STATE, not tasks (tasks.md), not
  research findings (research/), not idea one-liners (project-ideas.md).
  A block line should point at those, not duplicate them.
- Never commit — the journal repo is committed at the user's cadence
  (the next /journal commit or journal-sync picks it up).
- `/journal` bumps the matching block ambiently after each entry;
  `/week` reviews staleness weekly. This command is for deliberate edits.
