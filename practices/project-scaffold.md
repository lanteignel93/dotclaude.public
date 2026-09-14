# Project scaffold — standard directories and build discipline

Standing convention (2026-09-14) for any non-trivial project Claude builds
or co-builds. The goal: every important piece of logic is independently
verifiable by a human stepping through it, tests grow WITH the code, and
the project explains itself.

## The four standard directories

```
<project>/
├── debug_walkthroughs/   # debugger-ready verification scripts
├── tests/                # incremental test suite (grows with the build)
├── docs/                 # what it is, how to read it, decisions
└── notebooks/            # research exploration (research projects)
```

Create them as the work warrants — a 50-line script needs none of this; a
multi-module build needs all of it. When in doubt, the walkthroughs and
tests come first.

## debug_walkthroughs/ — verify the logic, don't trust the claim

One script per important logic unit, named `wt_<topic>.py`, runnable two
ways:

```
python debug_walkthroughs/wt_signal_join.py          # asserted run
python debug_walkthroughs/wt_signal_join.py --pdb    # step-through
```

Each script:
- builds a SMALL, seeded, fully-inspectable input (a handful of rows you
  can hold in your head — not a production data pull);
- calls the real implementation (imports the actual module — never a
  copy of the logic);
- prints/asserts the expected intermediate values at each step, with a
  comment saying WHY that value is expected;
- under `--pdb`, drops into the debugger at the first interesting frame
  with a header comment listing: breakpoint locations worth setting,
  variables worth poking, and what each should contain.

Purpose: verification of a Claude implementation is a JOINT step, not a
claim. The walkthrough is the standing recipe for that joint step — write
it when the logic lands, keep it working (walkthroughs run in CI or the
test suite as their asserted variant), and re-run it whenever the logic
changes.

## tests/ — incremental, not retrospective

- Every build increment lands WITH its narrow test — the test is part of
  the increment, not a later phase. "Done" for a step means its test runs.
- Prefer integration tests against real systems where feasible; don't
  mock what you can run (CLAUDE.md code-style rule).
- The walkthroughs' asserted mode doubles as coarse integration tests;
  the tests/ suite holds the fine-grained cases and the regressions.
- A bug fixed without a test that would have caught it is half-fixed.

## docs/ — the project explains itself

- `docs/` holds: what this is (one page), how to read the outputs
  (units, conventions, how-to-read notes on every report/notebook), and
  dated decision entries for choices that will be questioned later.
- Write the how-to-read notes as sections ship — the reader who needs
  them most is you in six weeks.

## notebooks/ — research work shows its evidence

- Research projects keep exploration in `notebooks/`, executed and
  committed (or exported alongside) so results are inspectable without
  rerunning.
- Notebooks follow the validation-notebook rule from CLAUDE.md: visualize
  inputs, outputs, and edge behavior of whatever was built. Visual
  evidence beats prose.
- Library code graduates OUT of notebooks into modules (with tests); a
  notebook that has become load-bearing is a bug.

## How this composes with the rest of the system

- CLAUDE.md's working protocol ("arrive with tests ready", checkpoint
  with a debugger recipe) is the BEHAVIOR; this scaffold is where the
  artifacts live so the behavior survives the session.
- Plans (plans/) reference the walkthroughs in their Verification
  criteria: "wt_x.py steps clean" is a falsifiable gate.
- Reference implementation of the pattern: a research repo with
  `debug_walkthroughs/wt_*.py --pdb`, per-notebook how-to-read sections,
  and an audit doc in docs/ — the shape this convention generalizes.
