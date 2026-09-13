---
description: Promote (or demote) a plan to a new status — validate, move, commit
argument-hint: <slug> <speculative|actionable|in-flight|complete|archived>
---

Move a plan to a new status, validate required sections, and commit. Arguments: `$ARGUMENTS` (`<slug> <target-status>`).

## Steps

1. **Parse `$ARGUMENTS`.** First token = `<slug>`. Second token = `<target-status>` ∈ {`speculative`, `actionable`, `in-flight`, `complete`, `archived`}. If either is missing or `<target-status>` is invalid, abort with usage hint.

2. **Locate the file.** Search in this order:
   - `plans/<slug>.md`
   - `plans/speculative/<slug>.md`
   - `plans/complete/<slug>.md`
   - `plans/archived/<slug>.md`

   If multiple matches, abort with the list. If none, abort with "not found."

3. **Read the current `Status:` line** from the header. That's `<from>`.

4. **Validate the target.** Per `~/dotclaude/practices/plan-driven-workflow.md`'s required-sections matrix:

   **For `actionable` or `in-flight`**, these sections must contain non-placeholder content:
   - `## Scope in v1 / out-of-scope` — `In v1:` has at least one real bullet
   - `## Stakeholders & buy-in` — at least one recorded line
   - `## Preconditions` — at least one item marked met/pending
   - `## Implementation sequence` — numbered steps with real content, not `...`
   - `## Verification criteria` — specific bullets

   **For `complete`**, additionally:
   - `## Closeout / as-built` — non-placeholder content (not just italic guidance text)

   If validation fails, list the missing or empty sections and abort. The user fills them in and re-invokes.

5. **Compute target path:**

   | Status | Path |
   |---|---|
   | `speculative` | `plans/speculative/<slug>.md` |
   | `actionable` | `plans/<slug>.md` |
   | `in-flight` | `plans/<slug>.md` |
   | `complete` | `plans/complete/<slug>.md` |
   | `archived` | `plans/archived/<slug>.md` |

6. **Move with `git mv`** to preserve history. If the file is already at the target path (status change that doesn't move it, e.g. `actionable → in-flight`), skip the move.

7. **Update the `Status:` line** in the moved file to `<target-status>`.

8. **Stage and commit:**

   ```bash
   git add -A plans/
   git commit -m "plans: promote <slug> <from> → <to>"
   ```

   Use a single arrow `→`. Don't push — the user pushes when ready.

## Notes

- "Demotion" (e.g. `actionable → speculative`) is supported; the commit message reads the same way but the meaning is "scope unravelled, sent back to think more."
- `complete → archived` is also legal (rare — happens if a delivered plan is later superseded by a different approach).
- Validation is intentionally strict at `actionable` to enforce the promotion-rules discipline. Override by editing the file to satisfy the sections, not by skipping validation.
