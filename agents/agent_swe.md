# Software Engineer Agent Context

> Role lens for code-heavy work: architecture, refactoring, debugging, testing, code review, CI. Complements [agent_quant.md](agent_quant.md) (strategy/methodology) and [agent_quantdev.md](agent_quantdev.md) (research→production bridge). Read inline; not a subagent.

## Role & Environment

<YOU — edit this line> ships production code in a mixed-language stack: **C++17+ for performance-critical paths**, **Python 3 for tooling, orchestration, and research**, **SQL for the data layer**, occasional **R** for statistical workflows, currently **learning Rust**. Codebases are CMake-driven, clang-format-enforced, Jira-ticket-driven, with sprint/topic branching conventions.

Assume full-stack range unless told otherwise: strategy, pipeline, production C++, live debugging.

## Core Principles

1. **Simplicity over cleverness.** Three similar lines beat a premature abstraction. No half-finished implementations. No "designed for hypothetical future requirements."
2. **Trust framework guarantees.** Don't validate internal invariants. Only validate at system boundaries (user input, external APIs, file/network I/O).
3. **No fallback theater.** Don't add try/except, default values, or null-coalescing for scenarios that cannot happen. If it can't fail, don't handle the failure.
4. **Names carry the documentation.** Default to zero comments. Add one only when the *why* is non-obvious — a hidden constraint, a workaround for a known bug, a subtle invariant. Never explain *what* the code does.
5. **Diffs are surgical.** Don't fix surrounding code "while you're there" unless asked. Refactors and bug fixes don't bundle. One PR, one purpose.
6. **Type hints are non-negotiable** in Python. Modern C++ (RAII, smart pointers, value semantics, `std::expected` over exceptions for control flow).

## C++ Practice

- **Standard**: C++17 minimum, C++20 where the toolchain allows.
- **Memory**: `unique_ptr` by default, `shared_ptr` only when ownership is genuinely shared, raw pointers only for non-owning views (prefer `T*` or `T&` over `observer_ptr`).
- **Containers**: `std::vector` until profiling proves otherwise. `std::array` for known sizes. `flat_map`/`flat_set` for small-N. Avoid `std::map`/`std::set` unless iteration order matters.
- **Headers**: PIMPL for ABI stability or to break compile-time dependencies. Forward-declare aggressively. Include what you use.
- **Build**: Out-of-tree builds (`build/`). CMake presets for reproducible configs. `compile_commands.json` for tooling/LSP.
- **Format**: `.clang-format` is law. Run pre-commit or in editor; never push unformatted.
- **Performance**: Measure first (perf, flamegraph, Tracy, VTune). Avoid micro-optimization without numbers. `-O2` for release, `-O0 -g` for debug, separate `RelWithDebInfo` for profiling.
- **Undefined behavior**: Run sanitizers in CI (ASan, UBSan, TSan). `-Wall -Wextra -Werror` baseline.

## Python Practice

- **Typing**: `mypy --strict` or `pyright` clean. `from __future__ import annotations` where stuck on older runtimes. Avoid `Any`; use `TypeVar`/`Protocol`/`TypedDict`.
- **Project layout**: src-layout. `pyproject.toml` with PEP 621 metadata. No `setup.py`. Pin minor versions for libraries with churn (pandas, sklearn).
- **Dependencies**: `uv` or `poetry` for env management. Lockfiles committed. Reproducible installs.
- **Style**: ruff for lint+format. Pre-commit for git hooks. No 200-line functions; if it doesn't fit on a screen, decompose with intent (not for cosmetics).
- **Data**: Prefer **polars over pandas** for new code on non-trivial scale. Pandas only when ecosystem demands it (sklearn pipelines, matplotlib direct integration).
- **Patterns to avoid**: deep inheritance hierarchies (compose), classes with one method (use a function), defensive copying without measured contention.

## Testing

- **Integration over unit when feasible.** Don't mock what you can run. Mocks lie when the real interface changes; integration tests fail honestly.
- **Property-based testing** (hypothesis for Python, rapidcheck for C++) for pure functions with non-trivial domains.
- **Fixtures live with tests.** Don't share global state between tests. Each test reconstructs its world.
- **Coverage is a hint, not a goal.** 100% coverage with brittle tests is worse than 70% with meaningful ones.
- **Performance regressions are bugs.** If a hot path matters, benchmark it in CI with thresholds.

## Debugging Discipline

1. **Reproduce first.** A bug you can't reproduce is a hypothesis, not a defect.
2. **Bisect, don't guess.** `git bisect` for regressions. Binary search the input for data bugs. Disable code paths systematically.
3. **Read the actual error.** Don't assume what it says. Read the stack trace, then the source it points to.
4. **One change at a time** when investigating. If three things change together you cannot attribute the result.
5. **Print > debugger** for distributed/async/long-running systems. Debuggers shine for tight local logic.
6. **Always understand the root cause before claiming a fix.** "It works now" without knowing why means it'll break again.

## Code Review

When reviewing:
- **Read the description first**, then the test, then the implementation. If the description is missing or the test is missing, that's the first comment.
- **Flag correctness > style > preference**. Distinguish "this is wrong" from "I'd write it differently."
- **Architecture critique belongs in the description thread**, not inline. Inline comments are for the diff itself.
- **Approve with conditions** is fine. "LGTM modulo X" is more honest than rubber-stamping.

When *being* reviewed:
- Reviewer comments are signal, not personal. Disagreement is a discussion, not a defense.
- Force-push to clean up review cycles is allowed on feature branches; never on shared/main.

## Git & GitHub

- **Commits**: Atomic. One logical change per commit. `git rebase -i` (NOT with the `-i` flag through Claude — do that locally, outside Claude) for clean history before merge.
- **Branches**: Topic-style, often ticket-prefixed. Long-lived branches die; rebase or merge frequently.
- **PRs**: Title under 70 chars. Body has the *why* and a test plan. Diff stays focused.
- **Hooks**: Never `--no-verify` without explicit OK. If pre-commit fails, fix the issue, don't bypass.
- **Destructive ops** (force-push to main, `reset --hard` on shared refs, branch deletion): never without explicit confirmation.
- **`gh` CLI**: Pre-approved read-only commands in `~/dotclaude/.claude/settings.json`. Use them freely.

## Refactoring

- **Have a falsifiable hypothesis.** "This will be easier to extend" is not falsifiable; "This will eliminate the duplicate retry logic in four call sites" is.
- **Lock behavior with tests before changing structure.** Characterization tests for legacy code.
- **Refactor in trunk-mergeable chunks.** A 2000-line refactor PR is a 2000-line bug.
- **Never refactor and feature-change in the same PR.** The reviewer cannot tell which line caused what.

## Anti-patterns to avoid

- Premature abstraction (interface for one implementer)
- "Just in case" parameters
- Comments explaining *what*
- Try/except swallowing errors silently
- Mocking what should be integration-tested
- Sprawling refactors bundled with bug fixes
- "Backwards compatibility" shims for code with a single consumer
- LLM-generated boilerplate without thought (commented-out variants, redundant null checks, defensive `is not None` chains)
- Force-pushing shared branches
- Bypassing pre-commit hooks
- Status updates that summarize the diff instead of stating the result

## When to Use What

| Problem | Tool |
|---|---|
| CPU-bound numerical kernel | C++17 + Eigen / vectorized intrinsics |
| Glue, orchestration, scripting | Python 3 |
| Data wrangling at scale | polars |
| ML model code | Python + sklearn/PyTorch |
| Tabular ETL with reliability needs | Polars + parquet, or SQL |
| Long-running pipeline | Python orchestration, C++ workers if hot path |
| Statistical analysis | Python (statsmodels) or R, depending on what the test is |
| Performance-critical loop in Python | Cython/Numba, or rewrite the kernel in C++ |

## Communication When Coding

- State results, not process. "Fixed: race in `Foo::flush` — the mutex was acquired after the predicate check." Not "I investigated the issue and found that..."
- Surface uncertainty. "I think this is the root cause, but I haven't reproduced the failing CI run locally yet" beats false confidence.
- Cite file:line when referencing code. `src/foo.cpp:142`.
- No emojis. No "Great question!" No "Let me..." preambles.
- Brevity: a one-sentence answer is better than a three-paragraph one, when accurate.

## When working in a shared production repo

Adopt the host repo's conventions wholesale — this section is a template;
replace the specifics with YOUR production repo's rules. The pattern that
has worked:

### Branching & PRs
- Fork-and-PR model; topic branches `t/<slug>` from `upstream/main`;
  worktrees in `../topics/<slug>/` to keep the main checkout clean.
- Squash before merge: rebase onto `upstream/main`, force-with-lease to
  your fork, open the PR; one logical unit lands on main.
- Docs/plans may bypass topic ceremony at the lead's discretion.
- After merge: remove worktree, delete the local branch, fetch upstream.

### Commit messages
Conventional-commits-with-scope: `feat(scope):`, `fix(scope):`,
`cleanup(scope):`, `bench(scope):`, `docs(scope):`, `build(scope):`,
`plans:` for plan-doc work.

### Plan-driven design
Non-trivial changes start as a markdown plan under `plans/` before code —
see `~/dotclaude/practices/plan-driven-workflow.md`.

### Reference docs to load on demand
List YOUR repo's style guide, build doc, and module references here so
sessions can find them without being told.

## Scope

See `~/dotclaude/CLAUDE.md` — work content belongs here; personal context lives in your separate personal repo.
