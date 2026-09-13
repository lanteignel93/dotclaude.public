# Data Scientist Agent Context — SKELETON, fill me in

> Role lens for empirical work: experimental design, statistical
> inference, model validation, feature engineering, visualization. Read
> inline; not a subagent. Replace each section's guidance with YOUR
> answers.

## Role & Environment
*Your data domain and its statistical character (signal-to-noise,
stationarity, sample sizes), and your analysis stack.*
Example line: "Time-series financial data: non-stationary, low SNR,
regime changes, fat tails — every 'discovery' is a candidate for noise
plus optimism."

## Experimental design
*How a study starts: hypothesis first? pre-registration? holdout
discipline? what a valid comparison requires (baselines, controls,
multiple-testing policy).*

## Inference standards
*Your significance and effect-size bars, when to correct for multiple
tests, non-parametric fallbacks, how uncertainty is reported (intervals,
not points).*

## Validation
*Cross-validation shapes that respect your data's structure (temporal
blocks? group splits?), leakage checks, negative controls.*

## Feature engineering
*Conventions: transformations, normalization policy (e.g. within-date
ranks), missing-data handling, persistence/stability checks before a
feature is trusted.*

## Visualization
*What every plot owes the reader; your defaults; what you consider
chartjunk. When a notebook is the deliverable vs the scratchpad.*

## Scope
See `~/dotclaude/CLAUDE.md` — work content belongs here; personal context
lives in your separate personal repo.
