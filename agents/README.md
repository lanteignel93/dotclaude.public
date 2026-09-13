# agents/ — role-lens context files

Reference docs Claude reads on demand (mention them inline, or link them
from a project's CLAUDE.md). They are NOT subagents — no frontmatter, no
tool grants; just dense context that makes a session competent in a lens.

Shipped as SKELETONS — headers plus prompts, deliberately unfilled. The
value of an agent file is that it's written in your voice about your
standards; a pre-filled one teaches you nothing and misleads Claude about
what you actually hold code to. Fill them over your first weeks — every
time you correct Claude twice for the same thing, that correction belongs
in one of these files.

- `agent_swe.md` — engineering: principles, testing, review, repo rules.
- `agent_quantdev.md` — the research→production bridge.
- `agent_ds.md` — empirical work: design, inference, validation.
- `quant_specs/quant_methodology.md` — what "good research" means:
  hypothesis testing, effect sizes, backtesting standards, process gates.
- `quant_specs/microstructure_mm.md` — microstructure/market-making
  theory canon (five-paper arc, key equations, empirical priors).

## Write your own domain file

The highest-value agent file is the one describing YOUR domain — your
firm's systems, universe, vocabulary, priorities, colleagues' areas. That
file cannot ship in a public kit; write it from
`agent_domain.template.md` and keep it in your PRIVATE fork/overlay.
Rules of thumb:

- Stable background only — live thread state belongs in
  `~/work-journal/projects.md`, which is injected per-session anyway.
  Write the file so it's still true in three months.
- Name things precisely (systems, data stores, conventions) — vocabulary
  is half the value.
- Dated snapshot sections ("priorities as of <date>") beat silent staleness.
- Regenerate/refresh when your role or the desk shifts materially.
