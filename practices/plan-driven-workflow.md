# Plan-driven workflow

Adapted from a colleague's production-repo convention; generalized for any project. Apply when a project warrants a `plans/` directory — non-trivial design work, multi-step initiatives, anything where "let me write down the approach first" pays for itself.

Mirrors the lifecycle pattern that `docs/incidents/` uses in larger codebases. Same DNA, different domain.

---

## Why

Plans-as-markdown serve three needs at once:

1. **Pre-implementation thinking surface.** Cheaper to throw away a 1k-word plan than a 10k-line refactor.
2. **Stakeholder alignment.** A plan you can link to is easier to review than a meeting transcript.
3. **Institutional memory.** Six months later, "why did we do it this way" is answered by `plans/complete/<name>.md`, not by archaeology on the diff.

If a change is small enough that the diff explains itself, skip the plan. If you find yourself rewriting the approach mid-way, you needed a plan.

---

## Directory layout

```
plans/
    README.md              ← project-specific notes (optional)
    speculative/           ← floated ideas; not committed
    <plan>.md              ← actionable or in-flight (at root)
    complete/              ← delivered; historical record
    archived/              ← abandoned or superseded
```

At-a-glance rule: **what's at the root is real work** — committed-to or actively landing. Subdirectories signal "not at the root for a reason." Movement between directories is a deliberate, reviewable event with a clear commit message.

---

## Status header (required on every plan)

```markdown
# <title>

**Status:** <status>
**Prepared:** <YYYY-MM-DD>
**Owner:** <named person or "unassigned">
**Buy-in:** <stakeholder(s), date>     # optional, required at actionable
```

`Status:` is authoritative. If it disagrees with the directory location, the header wins and the file moves to match.

### Status vocabulary

| Status        | Meaning                                                                       | Lives in           |
|---------------|-------------------------------------------------------------------------------|--------------------|
| `speculative` | Floated during triage, brainstorm, or thinking out loud. Not committed. Value is capturing the thinking while fresh; may never mature. | `plans/speculative/` |
| `actionable`  | Scope agreed, owner named, ready to start.                                    | `plans/` (root)    |
| `in-flight`   | Work happening — PR open, branch active, or partial landing.                  | `plans/` (root)    |
| `complete`    | Delivered. Plan stays as the historical record of what was built and why.     | `plans/complete/`  |
| `archived`    | Abandoned or superseded. Retained for institutional memory.                   | `plans/archived/`  |

### Lifecycle

```
speculative → actionable → in-flight → complete
                         ↓
                      archived   (if abandoned or superseded)
```

Reverse transitions are legal (`actionable → speculative` if scope unravels under review) but explicit: update the header, move the file, commit with a message that explains why.

---

## Promotion rules

A plan graduates from `speculative` to `actionable` when **all** are true:

1. **Scope cut.** What's in v1 and what's deferred is explicit. A plan that "does everything the title suggests" is speculative by default.
2. **Stakeholder buy-in, named.** Whose sign-off was needed; got it. Record as a Buy-in line with date. Specialize per-project (e.g. `Trader (confirmed 2026-04-24); Platform lead (PR #143 review)`).
3. **Named owner.** Someone accountable for landing it. No "unassigned actionable."
4. **Preconditions resolved.** Dependencies on other plans, PRs, or decisions are met and noted in the plan's own Preconditions section.

`actionable → in-flight` when the work has actually started — PR opened, branch created, design walkthrough being followed. No separate approval; update the header and commit.

`in-flight → complete` when the last promised v1 deliverable is in production (or the explicit "done bar" stated in the plan). Update header, move to `complete/`, commit with a close-out line referencing merged PRs.

---

## Required sections, by status

| Section                       | speculative | actionable | in-flight | complete |
|-------------------------------|:-----------:|:----------:|:---------:|:--------:|
| Problem / motivation          | ✓ required  | ✓ required | ✓         | ✓         |
| Proposed approach             | ✓ required  | ✓ required | ✓         | ✓         |
| Scope in v1 / out-of-scope    | optional    | ✓ required | ✓         | ✓         |
| Stakeholders & buy-in         | optional    | ✓ required | ✓         | ✓         |
| Preconditions                 | optional    | ✓ required | ✓         | n/a      |
| Implementation sequence       | optional    | ✓ required | ✓         | ✓         |
| Verification criteria         | optional    | ✓ required | ✓         | ✓         |
| Open questions                | ✓ encouraged| optional   | optional  | n/a      |
| Related plans / docs / PRs    | ✓ required  | ✓ required | ✓         | ✓         |
| Closeout / as-built           | n/a         | n/a        | n/a       | ✓ required |

Speculative plans are deliberately light on scope/verification — requiring those would block the "capture thinking while fresh" value. Promotion to actionable is the moment those fields must be filled in.

Template: `~/dotclaude/templates/plan.md` has the section skeleton matching the `actionable` requirements.

---

## Weekly sweep

Plans rot without a deliberate touch. Without a sweep, `actionable` quietly becomes speculative-in-actionable-clothing, `in-flight` plans drift into zombie state, and `speculative` accumulates forever. Pairs naturally with a personal GTD weekly review.

Once a week (Friday close, Monday morning — whatever fits):

1. **Walk `plans/` (root).** For each file:
   - Status still accurate? An `actionable` plan that's been actionable for three weeks with no owner is drifting — demote to `speculative` or find an owner.
   - `in-flight` with no visible movement this week? Either record the blocker, move to `archived/`, or back to `actionable`.
2. **Walk `plans/speculative/`.** Someday/maybe sweep:
   - Still interesting? If not → `archived/`.
   - Preconditions newly met? Candidate for promotion — check scope cut, buy-in, owner.
   - Anything learned elsewhere (incident, new data, external change) that should update the open-questions section?
3. **Walk `plans/complete/`.** Anything recently landed without a closeout note? One line — `delivered via PR #NN, MM/DD/YY` — keeps the archive queryable.
4. **Log the sweep.** One line in your week journal: `plans sweep 2026-W19: 2 speculative → archived, 1 actionable → in-flight, 3 complete back-annotated`. Provides a longitudinal record of where energy is going.

---

## Mapping to GTD / PARA

PARA applied to engineering planning, with GTD's weekly review on top. If unfamiliar, the [PARA primer](https://fortelabs.com/blog/para/) and a Wikipedia skim of [GTD](https://en.wikipedia.org/wiki/Getting_Things_Done) give the vocabulary.

| GTD / PARA              | Where it lives                                                |
|-------------------------|---------------------------------------------------------------|
| Capture                 | Plans-in-draft, incident docs, session dialog                 |
| Projects (active work)  | `plans/` root — `actionable` + `in-flight`                    |
| Areas (ongoing)         | `docs/` (durable reference), `CLAUDE.md`, this doc            |
| Resources               | `docs/`, external refs (GitHub, wiki, books)                  |
| Archive                 | `plans/complete/`, `plans/archived/`                          |
| Someday/Maybe           | `plans/speculative/`                                          |
| Weekly review           | The sweep above                                               |
| Next actions            | Action items inside plans; standalone dated ones in `~/work-journal/tasks.md` (see `~/dotclaude/practices/tasks.md`) |

If something doesn't fit a bucket, that's a signal — either the taxonomy needs a new slot, or the thing doesn't belong here at all.

---

## Housekeeping

- Move plans between directories with a clear commit: `plans: promote <name> speculative → actionable`. Git renames preserve history.
- Don't silently delete plans. Archive them to `archived/` with a one-line closeout at the top so future searches find the decision trail.
- A bottom-of-README index isn't worth maintaining until the directory grows large. `ls plans/` + `ls plans/*/` is usually the index.

---

## Reference

- Plan template: `~/dotclaude/templates/plan.md`
- Sprint template: `~/dotclaude/templates/sprint.md`
