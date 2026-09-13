# Microstructure & Market-Making Theory

*Distilled from the five foundational microstructure/market-making papers plus practitioner notes. Deeper derivations live in the cited papers; workstream statuses are examples — replace with your desk's.*

## The canonical arc (five papers)

| Paper | Question | Answer |
|---|---|---|
| Avellaneda-Stoikov (2008) | How to quote under inventory + transaction risk? | Reservation price `r = s - q·γ·σ²(T-t)`; closed-form optimal spread |
| Cont-Stoikov-Talreja (2010) | How does the book behave? | Continuous-time Markov queueing system with endogenous price formation |
| Gueant-Lehalle-Fernandez-Tapia (2011) | Quoting under hard inventory caps `q ∈ [-Q,Q]`? | HJB → linear ODE system; the rigorous solution AS approximated |
| Stoikov (2018) | The "true" price given book state? | Micro-price: martingale estimator from L1 imbalance, beats mid and weighted-mid |
| Huang-Lehalle-Rosenbaum (2014) | Realistic LOB simulation for pre-trade analysis? | Queue-reactive intensities (state-dependent) + stochastic reference price |

Key equations:
- Arrival intensity `λ(δ) = A·e^(-κδ)` — κ (flow elasticity) is the parameter
  everything is sensitive to; estimable via the CST model.
- Optimal half-spread `δ* = (1/γ)·ln(1 + γ/κ) + ½γσ²(T-t)`.
- Micro-price `μ = M + G(I, S)`, imbalance `I = V_b/(V_b+V_a)`; equals the
  AS reservation price in the γ→0 limit — "quote around the micro-price" is
  the zero-risk-aversion special case of the whole framework.
- Cartea-Jaimungal drift extension: `r = S + μ_t·τ - q·γ·σ²·τ` — a drift
  forecast (a TV) slots directly in; holding time emerges from (μ, σ, γ, κ),
  and γ becomes the single dial trading edge capture vs inventory risk,
  subsuming a separate risk layer. Portfolio form replaces `γσ²q` with
  `γ·qᵀΣq` (for ~0.9-correlated ES/NQ/RTY, single-asset framing understates
  risk by ~√3).

## Empirical priors worth trusting (queue-reactive calibration)

- Cancellation intensity at Q±1 is **concave increasing** in queue size
  (queue priority has value, so front-of-queue orders don't cancel);
  insertion at Q±2 is **decreasing** (priority harvesting).
- Constant-rate Poisson execution probabilities **systematically
  overestimate fill rates** — any fill model assuming memoryless flow is
  optimistic by construction.
- Mechanical (book-endogenous) volatility ≈ 5 bps vs ~14 bps empirical:
  the book explains a real but minority share of short-term variance; the
  rest is information. Grounds both why micro-price works and why it can't
  explain everything.
- Framework validity: large-tick instruments (avg spread ≤ ~2.5 ticks).
- Shared limitations of the whole family: memoryless flow (real flow is
  Hawkes-clustered), single-asset (no cross-book effects), no adverse
  selection (all flow treated uninformed), static parameters (no regimes).
  Every one of these limitations is a live desk concern.

## Order-flow toxicity (volume clock / VPIN)

Sample in event/volume time, not clock time — microstructure features
behave under a volume clock. VPIN: buy-sell imbalance over equal-volume
buckets as a real-time toxicity gauge; high VPIN → informed one-sided flow
→ widen or withdraw. Reframes adverse selection as a *measurable,
volume-time quantity* rather than a narrative.

## The three-workstream agenda (vault, written pre-PTA) and where it stands

- **A — reference price & feature/horizon pressure-test** (micro-price vs
  your in-house fair value vs weighted-mid; OFI, cross-product lead-lag at 100ms-5s, L2 depth,
  trade-sign imbalance; forecast quality at 100ms/1s/10s/30s): **open**.
  Cheapest offline; the horizon question (is 30s right for a quoting
  decision?) is unanswered.
- **B — adverse selection measurement** (post-fill drift conditional on
  signal strength and queue state; decompose fill P&L into edge capture /
  inventory skew / adverse-selection tax): the highest-leverage workstream if your desk lacks post-trade analytics —
  match-clock markouts, avoided-fill counterfactuals, queue position,
  per-level EV tables. The agenda called this the silent gap no paper covers;
- **C — rigorous quoting layer (Cartea-Jaimungal)**: **pairs naturally with a
  replay/simulation rig** — a rig's quadratic inventory penalty is the
  same object with the coefficient inverted from logs rather than chosen;
  the netting extension is the `γ·qᵀΣq` portfolio form. Calibrate γ from
  max-inventory-tolerance-given-signal-strength, not utility theory.

## Vol forecasting (input side of the risk rewrite)

The vault carries a curated intraday/next-day vol-forecasting reading list
(`Trading/Research Notes/Volatility Forecasting/Papers Guidelines.md`:
realized-measure econometrics, short-dated IV/VIX-family predictors,
dealer-flow/gamma mechanics, classical ML, deep learning) and an
estimation-error primer (`Estimation Error vs Sample Size.md`: relative SE
of σ̂ vs N; sample sizes for target precision). Both feed the
dynamic-volatility input of any risk-model redesign. Sinclair's standing
warnings apply: vol forecasting is no longer edge on its own (use it for
sizing/risk, a composite input, not out-forecasting the market); time-series
moments and implied moments are not comparable quantities — never trade
their difference as if they were.

## References

Avellaneda & Stoikov (2008) QF 8(3) · Cont, Stoikov & Talreja (2010) Op Res
58(3) · Gueant, Lehalle & Fernandez-Tapia (2011) arXiv:1105.3115 · Stoikov
(2018) QF 18(12) · Huang, Lehalle & Rosenbaum (2014) arXiv:1312.0563 ·
Cartea & Jaimungal (2015) *Algorithmic and High-Frequency Trading* ·
Easley, Lopez de Prado & O'Hara, "The Volume Clock" · Glosten & Milgrom
(1985) JFE 14(1). Vault notes: `Trading/Research Notes/` (per-paper
distillations + five-paper synthesis + HFT MM research agenda).
