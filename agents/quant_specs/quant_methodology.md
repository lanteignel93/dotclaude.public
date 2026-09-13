# Quant Methodology
*A living standards document — edit thresholds and examples to your desk.*

> Define what "good research" means - analytical standards, statistical rigor, backtesting protocols, and documentation requirements. The benchmark for all quantitative work.

---

## Statistical Rigor

### Hypothesis Testing

#### When to Use
- Before committing capital to any new strategy
- When claiming an effect exists (alpha, predictive power)
- When comparing strategies or parameters
- When validating model assumptions

#### Which Tests
- **t-tests**: Mean comparison (returns vs. zero, strategy vs. benchmark)
- **Paired tests**: When comparing same-sample results (before/after, strategy A vs B)
- **Non-parametric**: When normality assumptions violated (Wilcoxon, Mann-Whitney)
- **Chi-squared**: For categorical outcomes
- **Regression**: For relationship quantification with controls

### Significance Levels

#### Standard α Levels
- **α = 0.05**: Minimum for claims of significance
- **α = 0.01**: Preferred for trading decisions
- **α = 0.001**: For strong claims with high stakes

#### Multiple Testing Corrections
- **Bonferroni**: Conservative; divide α by number of tests
- **Benjamini-Hochberg (FDR)**: Less conservative; controls false discovery rate
- **Apply when**: Testing multiple strategies, parameters, features simultaneously

#### When to Be More Stringent
- High-stakes decisions
- Many comparisons made
- Data has been "looked at" multiple times
- Claims that would change behavior significantly

### Effect Sizes

#### Minimum Thresholds
Not just "statistically significant" but "large enough to matter":
- **Sharpe ratio**: > 0.5 after costs (> 1.0 excellent)
- **Information ratio**: > 0.3
- **Alpha**: Must exceed transaction costs meaningfully
- **Win rate**: Context-dependent; consider payoff ratio

#### Report Effect Sizes, Not Just P-Values
- Cohen's d for mean comparisons
- R² for regressions
- Confidence intervals always

### Time Series Analysis

#### Stationarity
- **Test for it**: ADF test, KPSS test
- **Handle non-stationarity**: Differencing, detrending, returns instead of prices
- **Be suspicious**: Of relationships that assume stationarity when data isn't

#### Autocorrelation
- **Check**: ACF/PACF plots, Ljung-Box test
- **Implications**: Standard errors may be wrong; need robust methods
- **Common in**: Returns (weak), volatility (strong)

#### Regime Change
- **Acknowledge**: Relationships change over time
- **Test for**: Structural breaks (Chow test, CUSUM)
- **Handle via**: Rolling windows, regime-switching models, sub-sample analysis

### Causality vs. Correlation

#### Be Humble
- Correlation does not imply causation
- Spurious correlations are everywhere in finance
- Economic theory should precede statistical testing

#### When Claiming Causality
- Have economic reasoning for why X causes Y
- Rule out reverse causation
- Control for confounders
- Consider natural experiments if available
- Be skeptical even then

---

## Monte Carlo Validation

### When to Use MC
- Assessing strategy robustness
- Estimating parameter uncertainty
- Stress testing extreme scenarios
- When analytical solutions unavailable
- Evaluating path-dependent strategies

### Standard Parameters
- **Number of simulations**: Minimum 1,000; prefer 10,000+
- **Confidence level**: 95% standard; 99% for risk metrics
- **Seed setting**: For reproducibility
- **Convergence check**: Verify results stable with more simulations

### What to Stress-Test

#### Market Conditions
- Volatility regimes (low, medium, high, extreme)
- Trend directions (bull, bear, sideways)
- Correlation breakdowns
- Liquidity crises
- Skew regimes 
- Volatility of Volatility Regimes 
- Term-Structure of Volatility 
- First and Second derivative of VIX (how quickly market vol has moved.)

#### Strategy Parameters
- Entry/exit thresholds
- Position sizes
- Holding periods
- Filter parameters

#### Assumptions
- Transaction costs (2x, 3x baseline)
- Slippage scenarios
- Fill rate assumptions
- Data timing assumptions

### Reporting Requirements
- **Confidence intervals**: Not just point estimates
- **Distribution**: Show histogram of outcomes
- **Worst-case**: Report 5th percentile and worst observation
- **Sensitivity**: How results change with parameters
- **Assumptions**: Explicitly state what's assumed

---

## Backtesting Standards

### Walk-Forward Protocol

#### Structure
1. **In-sample (training)**: Fit model, optimize parameters
2. **Out-of-sample (testing)**: Evaluate on unseen data
3. **Walk forward**: Roll window, repeat

#### Window Types
- **Expanding**: Training grows over time (more data, potential regime mixing)
- **Rolling**: Fixed training window (adapts to regime, less data)
- **Recommendation**: Test both; prefer expanding unless strong regime-change evidence

### Training/Testing Splits
- **Minimum OOS**: 20% of data
- **For time series**: Respect temporal ordering (no future leakage)
- **Multiple folds**: Cross-validation with temporal blocks

### Out-of-Sample Requirements
- **True hold-out**: Data never seen during development
- **Sufficient length**: Multiple market cycles if possible
- **No peeking**: Once used for evaluation, cannot optimize on it
- **Report honestly**: OOS results are the results

### Parameter Optimization Approach

#### Dangers
- Overfitting to historical data
- Data mining bias
- Degrees of freedom exhaustion

#### Best Practices
- Minimize free parameters
- Use reasonable ranges based on theory
- Grid search with coarse granularity first
- Avoid fine-tuning to historical quirks
- Prefer robust parameters over optimal parameters

### Overfitting Prevention

#### Red Flags
- Strategy works perfectly in sample, fails out of sample
- Many parameters relative to data points
- Complex rules with no theoretical basis
- Performance depends on specific parameter values
- Strategy "discovered" through data mining

#### Prevention Techniques
- Start with economic theory
- Keep strategies simple
- Use regularization
- Cross-validate properly
- Reserve true hold-out data
- Report both IS and OOS results

---

## Transaction Costs

### Bid-Ask Spread Modeling
- **Minimum**: Use actual spreads, not mid-prices
- **Conservative**: Assume crossing spread on entry and exit
- **Variable**: Spreads widen in stress; model this

### Slippage Assumptions
- **For liquid instruments**: 0.5-1 tick typical
- **For less liquid**: Market impact models needed
- **Stress scenario**: 2-3x normal slippage

### Market Impact
- **Linear model**: Impact = coefficient × (size / ADV)
- **Square-root model**: Impact = coefficient × √(size / ADV)
- **Be conservative**: Overestimate rather than underestimate

### Fees
- **Commission**: Include all broker fees
- **Exchange fees**: Especially for options
- **Financing**: Margin costs if applicable
- **Taxes**: Consider if material

### Rebalancing Costs
- **Frequency matters**: More rebalancing = more costs
- **Threshold-based**: Rebalance bands reduce unnecessary trading
- **Include in backtest**: Don't ignore these costs

---

## Performance Metrics

### Primary Metrics

#### Return Metrics
- **CAGR**: Compound annual growth rate
- **Total return**: Over full period
- **Monthly/annual returns**: Distribution

#### Risk-Adjusted Metrics
- **Sharpe ratio**: (Return - Rf) / Volatility
- **Sortino ratio**: (Return - Rf) / Downside deviation (penalizes downside only)
- **Calmar ratio**: CAGR / Max drawdown

#### Risk Metrics
- **Volatility**: Annualized standard deviation
- **Max drawdown**: Worst peak-to-trough decline
- **Drawdown duration**: Time to recover
- **VaR**: Value at Risk (95%, 99%)
- **CVaR/ES**: Expected Shortfall (average of worst cases)

#### Trade Metrics
- **Win rate**: % of profitable trades
- **Profit factor**: Gross profit / Gross loss
- **Average win / Average loss**: Payoff ratio
- **Number of trades**: Statistical significance check

### Benchmarks
- **For equity strategies**: SPY, relevant index
- **For vol strategies**: VIX, volatility indices
- **For absolute return**: Risk-free rate + target premium

### Minimum Thresholds
Before considering a strategy viable:
- Sharpe > 0.5 after costs (prefer > 1.0)
- Max drawdown < 20% (prefer < 10%)
- Win rate + payoff ratio combination that makes sense
- Sufficient number of trades for statistical significance (n > 30 minimum)
- Positive expectancy per trade after all costs

---

## Robustness Checks

### Standard Checks (Always Perform)
1. **Out-of-sample validation**: Mandatory
2. **Parameter sensitivity**: Performance vs. parameter changes
3. **Sub-period analysis**: Different time windows
4. **Market regime analysis**: Bull/bear/sideways performance
5. **Transaction cost sensitivity**: 1x, 2x, 3x costs

### Parameter Sensitivity
- Vary each parameter ±20%, ±50%
- Strategy should degrade gracefully, not collapse
- Cliff edges indicate overfitting
- Document parameter dependence

### Regime Analysis
Define and test across:
- **Low vol**: VIX < 15
- **Medium vol**: VIX 15-25
- **High vol**: VIX 25-35
- **Extreme vol**: VIX > 35

Report performance in each regime separately.

### Subsampling
- **Random subsamples**: Bootstrap confidence intervals
- **Time-based subsamples**: Different years, market cycles
- **Event exclusion**: What if we exclude 2008? 2020?

### Red Flags That Invalidate Strategy
- Works only in specific parameter range
- Works only in specific time period
- Fails completely out of sample
- Returns dominated by few observations
- No economic rationale for why it should work
- Transaction costs eliminate edge

---

## Documentation Standards

### Jupyter Notebook Structure
```
1. Summary / Abstract
2. Hypothesis and Economic Rationale
3. Data Description
   - Sources
   - Time period
   - Cleaning steps
4. Methodology
   - Strategy logic
   - Parameters
   - Backtesting approach
5. Results
   - In-sample
   - Out-of-sample
   - Robustness checks
6. Discussion
   - What worked
   - What didn't
   - Caveats
7. Conclusion and Next Steps
8. Appendix
   - Additional charts
   - Code details
```

### Code Quality in Notebooks
- Clear markdown explanations between code cells
- Functions for reusable logic
- Meaningful variable names
- Comments for non-obvious code
- Version control the notebooks

### Markdown Report Format
For sharing/archiving findings:
```markdown
# Strategy Name

## Executive Summary
[2-3 sentences on what, why, results]

## Hypothesis
[What we're testing and why we think it might work]

## Data
[Sources, period, quality notes]

## Methodology
[How we tested it]

## Results
[Key metrics, charts]

## Robustness
[Sensitivity analysis, regime analysis]

## Conclusion
[Does it work? What's next?]
```

### Math Notation (LaTeX)
- Use LaTeX for all equations
- Define all variables
- Show derivations when non-obvious
- Example:
```latex
$$
\text{Sharpe} = \frac{\mathbb{E}[R_p - R_f]}{\sigma_p}
$$
```

---

## Literature Review Standards

### When to Search
- Before starting any new strategy research
- When encountering unexpected results
- When extending existing work
- Quarterly for field updates

### Preferred Sources
1. **Academic journals**: Journal of Finance, JFE, RFS, Journal of Empirical Finance
2. **Working papers**: SSRN, NBER
3. **Practitioner research**: AQR, Man Institute, Bridgewater
4. **Quality blogs**: MoonTower, Sharpe Two, Euan Sinclair

### Citation Format
For vault notes:
```markdown
**Title**: [Paper title]
**Authors**: [Names]
**Year**: [Year]
**Source**: [Journal/SSRN/etc.]
**Key findings**: [Bullet points]
**Relevance**: [Why it matters for our work]
**Critique**: [Limitations, concerns]
```

### Critical Reading Checklist
- [ ] What's the hypothesis?
- [ ] Is the data appropriate?
- [ ] Is the methodology sound?
- [ ] Are there data mining concerns?
- [ ] Do results generalize?
- [ ] What's the economic mechanism?
- [ ] What assumptions are made?
- [ ] What are the limitations?
- [ ] Can we replicate key findings?

---

## Peer Review / Self-Review

### Before Considering Analysis "Done"

#### Self-Review Checklist
- [ ] Hypothesis clearly stated?
- [ ] Economic rationale provided?
- [ ] Data described and appropriate?
- [ ] Methodology documented?
- [ ] Out-of-sample results reported?
- [ ] Transaction costs included?
- [ ] Robustness checks performed?
- [ ] Results interpretable?
- [ ] Limitations acknowledged?
- [ ] Code clean and reproducible?

#### Common Mistakes to Check
- Look-ahead bias (using future information)
- Survivorship bias (only current securities)
- Selection bias (cherry-picked samples)
- P-hacking (running tests until significant)
- Overfitting (too many parameters)
- Ignoring transaction costs
- Wrong benchmark
- Insufficient data
- Assuming stationarity inappropriately

### When to Ask for Critique
- Before allocating real capital
- When results seem too good
- When uncertain about methodology
- After significant time investment
- Before presenting to others

### How to Critique Own Work
Ask yourself:
1. Why might this be wrong?
2. What's the most likely source of error?
3. What would a skeptic say?
4. Can I replicate the results with different code?
5. What am I missing?

---

## Process Complements
*Added 2026-08-28, extended 2026-08-30 (template v2). Chosen for gaps, not strengths: the standards above are strong at the back end (sealed holdouts, labelled spends, pre-registered variants, kill criteria on pilots). Each item below attacks a failure mode they do not reach. Adoption notes belong in your own research notes.*

### 1. Kill-first, before any real work
State the idea in one sentence naming three things: **under [circumstance], this is too cheap/rich, because [group] is forced, greedy, or stupid.** If circumstance, counterparty, and their reason cannot all be named, it probably is not an edge. Then plot the predictor against subsequent returns before anything else — raw points, no binning, no smoothing, no deciles. A formless scatter ends it in five minutes; deciles, t-tests and PCA all still produce numbers on a round cloud. Falsification checks on the picture itself: is the relationship carried by fewer than 5 points (then it is those points, not a signal); is it one regime, one year, or one event (colour by date and re-look); does it survive removing the largest |x| decile; is it monotone, or is the sign coming from the tails only. Record the scatter whether or not it supports the hypothesis — a plot kept only when it agrees is not evidence. Surviving earns further work, it is not validation. At fill horizons the raw scatter is always formless; the test is the binned conditional mean, subjected to the same checks.

### 2. Benchmark against market-implied, not against zero
Score your forecast and the market's over the same events with log-likelihood (mean log p assigned to what happened) and Brier (mean sum of (predicted - actual)^2). If the market scores better it holds information you lack, and the gap sizes the deficit. This asks *is the edge mine, or already priced*, which no backtest against a zero/random benchmark answers. Operational form: state a probability per observation, not a direction; score
    edge_nats  = mean(y*log(p_model)  + (1-y)*log(1-p_model))
               - mean(y*log(p_market) + (1-y)*log(1-p_market))
    brier_gain = mean((p_market-y)^2) - mean((p_model-y)^2)
and require edge_nats > 0 with positive brier_gain as part of the signal decision gate — significance against a 50% null is not an edge against a priced market; a model with a good Brier score that loses to the implied benchmark has rediscovered the surface. Plot a reliability curve (predicted vs realised frequency by bucket): systematic over-confidence is the common failure and is invisible in a hit rate. Caveat: naive odds-to-probability normalisation understates longshots and overstates favourites because margin concentrates in the tails; the same distortion applies to wing pricing. For a market-making TV defined as a correction to mid/microprice this comparison is the edge measurement itself; it is genuinely new for forecast-shaped work (vol forecast vs implied).

### 3. Persistence audit on inputs
Before trusting a feature as predictive, measure its own persistence across the relevant unit. Reference result, Russell 1000 since 1999: volatility persists strongly, returns do not, the Hurst exponent has essentially zero year-to-year correlation. Most backward-looking screening silently assumes a persistence only volatility has. Existing gates are output-side; this is the input-side equivalent and cheap enough to run on every feature. Intraday-futures analogue: feature-beta stability across session windows plus within-session autocorrelation of the feature.

### 4. Classify each book by edge type, then write its death criteria
Three kinds of systematic edge: **risk-premium harvesting** (paid to hold a risk others avoid), **slow-converging inefficiency** (behavioural/structural, resolves over time), **fast-converging supply/demand dislocation** (relative value against a fair-value model with fast feedback on the model). The type determines what evidence should convince you the edge is dead. For the slow-converging kind a metric that dies faster than P&L is required, because P&L confirms death long after the fact. Every live book carries standing death criteria, not only pilots. This is the same classification act as the strategy-class table in the research template (factor / VRP / event / short-DTE chooses the phases); produce both at Phase 0.

### 5. Two-window percentiles for distribution shift
Rank a metric against a recent window and a long window simultaneously and read the gap. Worked case: VVIX at 100 sat at the 40th percentile since Aug-2024 but the 78th since 2007; same number, opposite meaning, and the gap is the evidence the distribution moved. Related: test implied against the realised distribution ("3M IV implies more vol than any realised 3M window in three years") rather than a standard-deviation count.

### 6. Mine your own fills for cause and effect
Nobody knows precisely why they make money, so anomalies in executed trades are the cheapest source of genuinely novel hypotheses; inconsistencies with the existing model of the market are where new ideas live. Standing form: markouts on the exchange clock, avoided-fill counterfactuals, queue position at accept and fill, per-level EV.

### Phase 0 additions (template v2, 2026-08-30)
Two gates that run before any code, alongside the kill-first sentence:

**Why is this trade available to *me*?** Distinct from "who is on the other side". If the edge is real and visible, why has a better-capitalised desk with better fills not already taken it? Acceptable answers are structural: too small to matter to them, capacity-constrained, requires holding a risk they are mandated not to hold, or sits in an operational niche they will not staff. "Nobody has noticed" is not an answer — it is the null hypothesis you have failed to reject.

**Cost screen before any modelling.** Convert the quoted spread and fees into the same unit as the hypothesised edge (vol points per year for options: half-spread per leg = (ask_vol - bid_vol)/2; fees = fee_per_contract/(vega x 100); total = n_legs x (spread + fees) x annual turnover) and compare directly. Kill if cost exceeds roughly 50% of the hypothesised edge — no Phase 3 significance rescues that, and the Phase 7 cost model will only say the same thing later and dearer. Worked reference (Moontower Primer #11): a 3-cent spread against $0.03 vega is one full vol point; half-cent fees add another 0.16. Costs belong inside the edge, not as a late haircut on an edge already believed. The 1x/2x/3x sensitivity model stays in Phase 7; this is the cheap gate, not its replacement.

### Lifecycle stage and the killed-strategy form
Every strategy-shaped research thread declares a lifecycle stage and keeps it current: **Hypothesis** (rationale only) -> **Exploratory** (data loaded, factor analysis) -> **In Progress** (walk-forward signal validated, structures tested) -> **Complete** (OOS done, decision made) -> **Deployed** or **Killed**. Stage is distinct from note freshness (active/dormant/closed/reference). A Killed thread documents four things: final performance with all conditioning applied; which threshold(s) failed; what was learned; transferable artifacts (regime features, code patterns, data pipelines). Killed strategies are valuable; one killed strategy's regime-conditioning features were adopted by a sibling strategy and added +0.37 Sharpe.

### Additional invalidating red flag
Extreme kurtosis without corresponding risk management (the VIX-futures case: kurtosis 52.5) invalidates a strategy as surely as a failed OOS window.

---

## Metadata
- Origin: distilled from several completed strategy research arcs; genericized for sharing.
- Update cadence: after each completed major research arc; review annually.
