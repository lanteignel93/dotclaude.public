# Quant Developer Agent Context — SKELETON, fill me in

> Role lens for the research→production bridge: numerical correctness,
> reproducibility, performance, data pipelines, deployment of model code.
> Read inline; not a subagent. Replace each section's guidance with YOUR
> answers.

## Role & Environment
*What "research to production" means on your team; where you sit in it;
the stack per layer (latency-sensitive vs orchestration vs data).*

## Numerical correctness
*Your rules for float discipline, determinism/reproducibility, seeds,
tolerances, golden files, and cross-implementation checks (research
prototype vs production port must agree to what precision, on what data).*

## Time and data discipline
*Event time vs ingestion time vs processing time — where lookahead hides
in YOUR pipelines. Revision semantics of your data sources. Timezone
traps. Name the actual stores and their gotchas.*

## Performance
*When optimization is allowed (measured hot paths only), what gets
benchmarked, what regression gates exist.*

## Pipelines & deployment
*How model code ships: packaging, config, rollback, monitoring. What a
production incident owes the postmortem.*

## Reporting standards
*Example: "Cite numbers — runtime delta, memory delta, accuracy delta —
not adjectives. A backtest result always includes the validation method."*

## Scope
See `~/dotclaude/CLAUDE.md` — work content belongs here; personal context
lives in your separate personal repo.
