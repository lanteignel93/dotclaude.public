---
description: Bootstrap a new plan from the template
argument-hint: <slug> [--actionable]
---

Create a new plan document from `~/dotclaude/templates/plan.md`. Arguments: `$ARGUMENTS`

## Steps

1. **Parse `$ARGUMENTS`.**
   - First token = `<slug>` (kebab-case, required)
   - Optional `--actionable` → drop the plan in `plans/` root (rare; most plans start speculative)
   - Default (no flag) → `--speculative` → plan goes in `plans/speculative/`
   - If `<slug>` is missing, abort with usage hint.

2. **Verify the cwd is a project that has or wants a `plans/` directory.** If it doesn't exist, ask the user before creating it. On confirm:

   ```bash
   mkdir -p plans/{speculative,complete,archived}
   ```

3. **Copy the template:**

   - speculative: `cp ~/dotclaude/templates/plan.md plans/speculative/<slug>.md`
   - actionable:  `cp ~/dotclaude/templates/plan.md plans/<slug>.md`

   If the target already exists, abort — don't clobber.

4. **Substitute placeholders in the new file:**

   | Placeholder | Replacement |
   |---|---|
   | `# <title>` | `# <humanized slug>` (e.g. `slot-arena-v2` → `Slot Arena v2`) |
   | `**Status:** speculative` | adjust to `actionable` if the flag was passed |
   | `**Prepared:** YYYY-MM-DD` | today: `$(date +%Y-%m-%d)` |
   | `**Owner:** unassigned` | output of `git config user.name`; if empty, keep `unassigned` |

5. **Report** the new file path and remind the user to fill in Problem and Approach before committing. Do not commit — the user does that with a message like:

   ```
   plans: introduce <slug>
   ```

## Notes

- The full convention is in `~/dotclaude/practices/plan-driven-workflow.md`.
- Required-sections matrix kicks in at promotion to `actionable`. Speculative plans can be sparse.

## Length

Plans err expansive — when filling one in (here or later), write the full
reasoning, not a summary. ~75% longer than what feels condensed is the target;
tasks and ideas stay terse because the detail lives in the plan.
