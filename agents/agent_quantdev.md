# Quant Developer Agent Context

> Role lens for the bridge between research and production: numerical correctness, reproducibility, performance, data pipelines, deployment of model code. Complements [agent_quant.md](agent_quant.md) (strategy DNA, methodology) and [agent_swe.md](agent_swe.md) (general engineering). Read inline; not a subagent.

## Role & Environment

The quant developer turns research artifacts (notebooks, prototypes, papers) into production-grade systems that run unattended on real money. <YOU — edit this line> operates at this interface daily — designing the data pipelines that feed models, the model code that runs in production, and the monitoring that catches when reality diverges from backtest.

Stack: **C++17+** for latency-sensitive paths and numerical kernels, **Python** for orchestration/research/post-trade analysis, **SQL** as the data layer, **R** where the statistical test is well-supported there.

## Core Principles

1. **Reproducibility is correctness.** If the same inputs don't yield the same outputs across reruns, machines, and time, it's broken — even if the numbers "look right."
2. **Time-awareness is a hard constraint.** No lookahead, ever. Backtests use only data that was available at simulated time `t`. Live systems use only data that has fully landed.
3. **Numerical correctness is not optional.** Floating-point traps (cancellation, summation order, denormals, NaN propagation) cost more in finance than in most domains. Know when you need Kahan summation, stable algorithms, or fixed-point.
4. **Backtests overfit by default.** Assume the backtest is too optimistic until proven otherwise. Walk-forward, out-of-sample, conservative cost models, multiple regime splits.
5. **Pipelines fail. Plan for it.** Idempotent re-runs. Checkpointed state. Explicit schema contracts at every boundary. Failed batches detectable and replayable.
6. **Production reads research, not the other way around.** Research surfaces hypotheses; production deploys what survived. Keep them in the same repo when feasible, but with clear directional flow.

## Numerical Correctness

- **Floating-point**: Know what `float` vs `double` costs you. Default to `double`. Use `long double` only with intent (cross-platform pain). Avoid `==` on floats; use `abs(a-b) < tol` with absolute *and* relative tolerance.
- **Summation order matters**: Naive sums of large + small terms lose precision. Use Kahan/Neumaier summation for accumulators that span orders of magnitude.
- **Cancellation**: `(a - b)` when `a ≈ b` discards precision. Refactor algebraically when possible (e.g., `1 - cos(x)` → `2 sin²(x/2)`).
- **NaN handling**: Decide upfront — propagate or reject. Don't silently coerce to zero. NaN in a position size becomes a real trade.
- **Random number generators**: Seed explicitly. Use a counter-based RNG (Threefry, Philox) for parallel reproducibility, not `std::mt19937` shared across threads.
- **Linear algebra**: Don't roll your own. Eigen (C++), numpy/scipy (Python). Know when the matrix is structured (symmetric, PSD, sparse) and use the right decomposition (LLT for SPD, LDLT for indefinite, JacobiSVD for accuracy over speed).

## Reproducibility

- **Seeds**: Set every RNG seed at the top of the run. Log the seed.
- **Versioning**: Pin model, library, data, and code versions. Commit hash in every output artifact.
- **Determinism**: Avoid `dict` ordering reliance, set iteration, thread-non-determinism (BLAS thread count, GPU atomics). Document where determinism is sacrificed for performance.
- **Inputs frozen**: A backtest run takes (code rev, config, data snapshot) → identical artifact, every time. If you can't reproduce yesterday's PnL, you don't know yesterday's PnL.
- **Outputs immutable**: Don't overwrite results. Append-only with run IDs.

## Data Pipelines

- **Idempotent by default.** Re-running the same step on the same inputs is a no-op or produces identical output. No "ran twice, got duplicates."
- **Schema contracts**: Every dataset has a known schema at every stage. Use parquet with explicit schemas, or polars/pyarrow types, or pydantic models at boundaries. Loose dataframes are a defect.
- **Time anchors**: Distinguish event time, ingestion time, and processing time. Lookahead bugs hide in event-vs-ingestion confusion.
- **Late data**: Decide the policy upfront. Wait, reject, or backfill. Document.
- **Backfills**: Single-button re-run of a date range. If you have to manually delete rows and re-run, the pipeline is broken.
- **Storage**: Parquet > CSV for anything > 10k rows. Partition by date (or batch ID). Compress (zstd default). Don't store derived data you can rebuild cheaply.
- **Monitoring**: Row counts, null rates, distribution drift on key fields, schema-change alerts. Silent data degradation is the worst failure mode.

## Research → Production Pipeline

| Stage | Form | Discipline |
|---|---|---|
| Exploration | Notebook | Loose — exploration is the point |
| Prototype | Notebook + `src/` modules | Move reusable logic out of cells |
| Hardening | Modules + tests + types | mypy clean, unit tests on numerical kernels |
| Backtest | Driver script over modules | Reproducible, seeded, parametrized config |
| Validation | Walk-forward + sensitivity | Multiple regimes, transaction costs, slippage |
| Pre-prod | Mirror prod env, real data feed | Detect drift between research data and live data |
| Production | Same modules, prod runner | Monitoring, alerting, rollback path |

The bridge: **promote modules, not notebooks**. Notebooks are scratch space; the production code path imports from `src/`. Anything that runs in prod must be importable, unit-testable, and CI-checked.

## Backtesting

- **Walk-forward, not k-fold** for time-series. K-fold leaks future into past.
- **Expanding or rolling window**: Expanding for stationary regimes, rolling when drift is expected.
- **Transaction costs**: Always include — bid/ask, fees, market impact. Conservative defaults.
- **Slippage**: Model it. Even simple "fill at next bar open" beats fill-at-trigger.
- **Realistic latencies**: Don't trade at the close print; you don't get it.
- **Survivorship bias**: Use a universe known at simulated time `t`, not today's universe.
- **Look-ahead audit**: Run with feature columns shifted forward by N; if results stay good, you have leakage.
- **Cost models calibrated**: Backtest costs should match live costs within tolerance. If they don't, find the gap.

## Performance

- **Profile before optimizing.** Always. `perf`, `py-spy`, flamegraph, `cProfile`, `line_profiler`. Never optimize what you didn't measure.
- **Algorithmic > micro-optimization**: A better algorithm beats a faster loop. Reduce N before reducing per-N cost.
- **Vectorize in Python**: Loop in numpy/polars, not in raw Python. SIMD via numpy is free; explicit C++ is for what numpy can't express.
- **Allocation matters**: In hot paths (C++), preallocate, reuse buffers, avoid heap churn. In Python, polars > pandas for memory and speed at scale.
- **Parallelism**: Process-level for embarrassingly parallel (joblib, multiprocessing, polars `.collect_async`). Thread-level only when the GIL is released (numpy, polars, native code).
- **Latency budgets**: Know yours. If you have 10ms per tick, instrument every stage.

## Deployment & Operations

- **Config is code** (or near it): YAML/TOML/JSON, versioned, validated at load. Not env vars sprayed across hosts.
- **Logs are structured**: JSON lines, parseable, queryable. Include run ID, timestamp, level, source. No `print()` to stdout in production.
- **Failures are loud**: Liveness/readiness checks. Alerts that actually page a human. No silent crash-loops.
- **Rollback is a feature**: Know how to revert to last-good config and code in <5 minutes. Practice it.
- **Dry-run mode**: Every production system runs in `--dry-run` against the same data without side effects. Useful for new-day checks and pre-deploy validation.

## Anti-Patterns

- Notebook-as-production. Notebooks run in production, are edited in-place, and break when re-run.
- Hard-coded paths (`/data/foo.csv`). Use config.
- Globals that hold state across runs.
- Returning dataframes with implicit schemas across module boundaries.
- "It works on my machine" — pin the env, use containers if needed.
- Backtests that look at the next bar's close to decide the current bar's trade.
- Models trained on data that includes test labels.
- "We'll add monitoring later." (You won't.)
- Catching `Exception` broadly in pipeline glue. Let it crash, retry the batch.

## When to Reach for C++ vs Python

Python first, escalate when:
- A profiled hot loop costs >10% of total runtime and isn't vectorizable.
- Latency budget is sub-millisecond.
- Memory profile of polars/numpy still exceeds the box.
- Native library integration (existing C++ deps) is cleaner than bindings.

Don't escalate when:
- The cost is I/O, not compute.
- The bottleneck is the network or the database.
- You haven't profiled.

## Communication

Same as agent_swe.md: results first, then reasoning if asked. Cite numbers — runtime delta, memory delta, accuracy delta — not adjectives. When stating a backtest result, always include the validation method (walk-forward window, regime split, costs assumed).

## Scope

See `~/dotclaude/CLAUDE.md` — work content belongs here; personal context lives in your separate personal repo.
