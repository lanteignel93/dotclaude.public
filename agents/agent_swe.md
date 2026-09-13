# Software Engineer Agent Context — SKELETON, fill me in

> Role lens for code-heavy work: architecture, refactoring, debugging,
> testing, code review, CI. Read inline; not a subagent. Every section
> below is a prompt — replace the guidance with YOUR answers. A section
> you can't fill yet is a section you haven't decided yet; leave the
> header and come back.

## Role & Environment
*Who you are as an engineer, your languages in order of fluency, the build
systems and conventions your codebases enforce. One paragraph.*
Example line: "Ships production code in a mixed stack: C++17+ for
performance-critical paths, Python 3 for tooling and research."

## Core principles
*The 5-10 rules you actually hold code to. Not aspirations — the things
you reject PRs over.*
Example: "Three similar lines beat a premature abstraction."

## Testing doctrine
*What must be tested, at what level, against what (mocks vs real
systems), and what "done" means.*

## Debugging approach
*Your order of operations when something breaks; the tools you reach for;
what evidence a root-cause claim requires.*

## Code review standards
*What you look for first; what's a blocker vs a nit; how findings should
be reported (severity, file:line, failure scenario).*

## Anti-patterns to avoid
*The specific habits that annoy you in generated code. Be blunt — this
section saves the most time.*
Example: "Backwards-compatibility shims for code with a single consumer."

## Communication when coding
*How results should be reported. Example: "State results, not process.
Cite file:line. Surface uncertainty explicitly. No preambles."*

## When working in a shared production repo
*Your team repo's branching model, commit-message convention, PR
etiquette, and the reference docs a session should load (style guide,
build doc, module references). Name real paths.*

## Scope
See `~/dotclaude/CLAUDE.md` — work content belongs here; personal context
lives in your separate personal repo.
