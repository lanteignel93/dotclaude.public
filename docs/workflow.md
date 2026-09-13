# Project workflow

Using Claude in a project directory on the server.

## Starting a session

```bash
cd /path/to/project
claude
```

Auto-loaded:
- `~/.claude/CLAUDE.md` (→ `~/dotclaude/CLAUDE.md`) — global config
- `<project>/CLAUDE.md` if present — project context

## Per-project CLAUDE.md

Two patterns depending on whether you're the only contributor or others contribute too.

### Pattern A — solo project (you're the only contributor)

Track the project CLAUDE.md in dotclaude so it syncs across your machines.

1. In the project: `claude`, run `/init` to draft from the codebase
2. Move into dotclaude:
   ```bash
   mkdir -p ~/dotclaude/projects/<name>
   mv <project>/CLAUDE.md ~/dotclaude/projects/<name>/claude.md
   ```
3. Symlink back:
   ```bash
   ln -s ~/dotclaude/projects/<name>/claude.md <project>/CLAUDE.md
   ```
4. Commit + push:
   ```bash
   cd ~/dotclaude && git add projects/<name> && git commit -m "Add <name> CLAUDE.md" && git push
   ```

Now the project's CLAUDE.md is version-controlled with dotclaude, edited in one place, available wherever dotclaude is cloned.

### Pattern B — team-owned project (others contribute, or could)

CLAUDE.md belongs in the project's own git, not in dotclaude. Other engineers benefit from it without needing your personal config repo, and the file evolves with the team rather than your private fork of the conventions.

A shared production repo fits this pattern: its CLAUDE.md lives in the project tree alongside the whole team's work.

1. In the project: `claude`, run `/init` to draft from the codebase
2. Edit `<project>/CLAUDE.md` directly. Typical content:
   - Build/test commands
   - Top-level layout, namespace tree, key modules and entry points
   - Conventions specific to this project
   - Pointers to in-repo reference docs (`docs/contributing.md`, `plans/README.md`, etc.) so Claude finds them
3. Commit it with the project, not with dotclaude.

If a solo project gains team contributors, promote A → B: remove the dotclaude-side symlink, move the file back into the project tree, commit it there.

## Editing context

Edit `~/dotclaude/CLAUDE.md` (global) or `~/dotclaude/projects/<name>/claude.md` (Pattern A projects) in VS Code/neovim. Commit + push. Next Claude session reflects the change — symlinks resolve on read, no restart needed.

For Pattern B projects, just edit `<project>/CLAUDE.md` directly. No commit/push needed; it's local.

## GitHub work

Pre-approved commands (from `dotclaude/.claude/settings.json`) — run without permission prompts:

```
gh pr {view, list, checks, diff, status}
gh issue {view, list}
gh repo view
gh api repos/*
gh search
gh auth status
git {log, diff, status, branch, remote -v}
```

Built-in skills for PR work:
- `/review` — structured PR review
- `/security-review` — audit pending changes for security issues

To extend the allowlist: edit `~/dotclaude/.claude/settings.json` and push.

## Plan-driven workflow

Non-trivial design work starts as a markdown plan under `plans/`, not as code. Adapted from a colleague's production-repo convention. See `~/dotclaude/practices/plan-driven-workflow.md` for the full convention.

- **Lifecycle**: `speculative → actionable → in-flight → complete` (or `archived`). Status header on every plan.
- **Directory layout**: `plans/` root for actionable/in-flight, `plans/speculative/`, `plans/complete/`, `plans/archived/`.
- **Weekly sweep**: keeps the directory honest. One log line per week.
- **Templates**: `~/dotclaude/templates/plan.md` and `~/dotclaude/templates/sprint.md`. Copy into a project's `plans/` or `sprints/` and edit.

Bootstrap a project for plans:

```bash
mkdir -p plans/{speculative,complete,archived} sprints
cp ~/dotclaude/templates/plan.md plans/<initial-plan>.md
```

## Reference docs (read on demand)

Not auto-loaded. Mention inline when relevant, or reference from a project's `claude.md`:

- `~/dotclaude/agents/` — your domain agent files (see agents/README.md for how to write one)
- `~/dotclaude/agents/quant_specs/quant_methodology.md` — statistical rigor standards
- `~/dotclaude/practices/` — engineering practice docs: `plan-driven-workflow.md`, `commands.md`, `tasks.md`

## Where content lives

| Content | Location | Loaded |
|---|---|---|
| Global preferences, style, conventions | `~/dotclaude/CLAUDE.md` | Always |
| Solo-project per-project context | `~/dotclaude/projects/<name>/claude.md` (symlinked) | When in project |
| Team-owned per-project context | `<project>/CLAUDE.md` (in the project's git) | When in project |
| gh/git allowlist + model/effort defaults | `~/dotclaude/.claude/settings.json` | Always |
| Statusline script | `~/dotclaude/.claude/statusline-command.sh` (symlinked) | On status refresh |
| Engineering practices | `~/dotclaude/practices/<topic>.md` | On demand |
| Plan / sprint / tasks templates | `~/dotclaude/templates/<type>.md` | On demand |
| Journal, tasks, ideas, command log (state) | `~/work-journal/` (per server, not synced by dotclaude) | Hooks + commands |
| Domain reference | `~/dotclaude/agents/quant_specs/` | On demand |
| Role-specific agent context | `~/dotclaude/agents/agent_{swe,quantdev,ds}.md` | On demand |
| Personal context (philosophy, journal, life) | your own personal-notes repo | Never on work servers |
| Machine-specific overrides | `~/.claude/settings.local.json` (not synced) | Always |

## Subagents and slash commands

Both are first-class Claude Code primitives:
- **Subagent**: `~/dotclaude/.claude/agents/<name>.md` with frontmatter (`name:`, `description:`, optional `tools:`). Isolated context, invoked via the `Agent` tool when Claude decides to delegate or when you explicitly request it.
- **Slash command**: `~/dotclaude/.claude/commands/<name>.md`. A prompt template invoked as `/<name>`.

Slash commands are populated (see `~/dotclaude/practices/commands.md` for the full set and when to use each); subagents are not. Add either only when a recurring pattern justifies the abstraction — not pre-emptively. Domain agent files are intentionally reference docs, not subagents.

## Cross-machine sync

dotclaude is a regular git repo on your fork's remote. Edit on any machine, commit, push, pull on another. Standard git conflict handling if two machines edit the same file simultaneously.

Keep a separate personal repo for non-work content; by design it never clones to work servers.
