# tmux organization

How to lay out tmux across servers, projects, and mixed-size clients.
Written from an audit of a heavily-used dev box (9 sessions, 26 windows,
86 panes); intended as a fresh-setup spec — apply it clean rather than
migrating an old layout.

## The problem this solves

Three client machines (Windows laptop + Windows work computer running
alacritty, Linux desktop) with different monitor geometries, attaching
to multiple servers, across many concurrent projects. The failure modes
observed on the old box:

- **Junk-drawer session** (`MAIN`): six unrelated windows (a data
  pipeline, a mislabeled vendor job, editor configs, this repo, a
  half-started project, cloud console) that never got sorted into homes.
- **One project scattered across three sessions** — switching context
  within one project meant switching sessions.
- **Screen-size session forks**: sessions created so a laptop attach
  wouldn't squish big-monitor layouts. They work, but they fork project
  state — a second checkout with its own claude, divergent from the
  primary session.
- **Dashboard/dev fusion** (11 panes in one window — 4 ssh monitors +
  editors + config diffs). Monitoring walls and dev environments have
  different layout-stability needs.
- **Zombie preservation**: resurrect+continuum keep everything alive
  forever — stale panes (one parked in a jedi typeshed dir), mislabeled
  windows, untouched sessions since July.

The reference-quality counterexample was one session for one
program of work, one window per repo, consistent pane grammar
(nvim / shell / claude-or-runner). That pattern, generalized, is this
doc.

## Design

```
clients (thin)                 servers (one tmux each)        sessions
──────────────                 ───────────────────────        ────────
pinned shortcut per server ──► ssh -t "tmux new -A -s …" ──►  OPS  (pinned dashboards)
per-machine font config only                                  WORK (fluid, per program)
```

The client knows nothing except its font size. The server owns
everything. A project's session exists only on the server where its
data/compute lives; a project session never sits behind an ssh hop.

### Two session classes

**OPS** — live-trading monitors, ssh walls, prod dashboards.
- Pinned geometry: `window-size manual` + session `default-size` set
  once, to the screen the dashboard is actually read on all day.
  Immune to whatever client attaches.
- Stable layout, essentially never re-arranged. No claude panes.
- Small-screen glance goes through a zoomed viewport (see `tv` below),
  never by resizing the session.

**WORK** — everything else. One session per program of work.
- Fluid geometry: global `window-size latest` — windows size to the
  client that most recently touched them and snap back when the big
  monitor returns.
- Window = one repo, named after it. Pane grammar: nvim / shell /
  claude-or-runner.

The boundary between a project's OPS and WORK sessions is
*operational mode*, not screen size (e.g. `PROJ-TRADE` vs
`PROJ-RESEARCH`). Forking a session by screen size is the anti-pattern;
splitting live-ops from research/dev is correct — different uptime
expectations, different risk if a pane gets squished mid-day.

### The five rules

1. **A session is a program of work or a dashboard.** Never a screen
   size, never a single Claude conversation.
2. **A window is a repo**, named after its basename. A new Claude
   conversation gets a pane/window in the owning session — never a new
   session.
3. **OPS windows are pinned; WORK windows float.** Simultaneous
   two-device work on one session goes through a `tv` viewport.
4. **Session names match the project slugs** used in plans/journal, so
   `/week`, `/briefing`, and tmux describe the same world.
5. **Prune monthly** alongside `/task prune`: continuum means nothing
   dies on its own — kill stale panes, fix drifted window names,
   retire finished-project sessions.

## Fresh-setup checklist

### tmux.conf deltas

```tmux
set -g window-size latest      # windows size to the most recent active client
set -g history-limit 50000     # 5000 is too low for long python/claude output
```

Everything else in the existing conf carries over as-is (vi mode,
vim-tmux-navigator, current-path splits, resurrect+continuum, your
theme, tmux-sysstat).

### OPS session pinning (per ops session, once, after creating it)

```sh
# size to the screen the dashboard lives on, e.g. 240x60:
tmux set-option  -t OPS-DASH default-size 240x60
tmux set-option -w -t OPS-DASH:1 window-size manual   # repeat per window
```

### Viewport function (`~/.zshrc`)

Temporary independent view into an existing session — grouped session
sharing the same windows (same shells, same claude conversations,
nothing forked) but with its own current-window and zoom state.
Self-destructs on detach, so continuum never accumulates them.

```zsh
# tv <session> — temporary viewport; detach (or switch away) destroys it
tv() {
  local base=${1:?usage: tv <session>}
  local view="${base}-v$$"
  tmux new-session -d -t "$base" -s "$view" || return
  tmux set-option -t "$view" destroy-unattached on
  if [ -n "$TMUX" ]; then
    tmux switch-client -t "$view"
  else
    tmux attach-session -t "$view"
  fi
}
```

Note: `destroy-unattached` means switching away from the viewport
inside tmux also destroys it — it cannot be parked. That is the
intended behavior (use from a laptop: `tv WORK`, work, detach,
gone).

### Optional: layout toggle for laptop work (sketch — test before trusting)

Zoom (`prefix+m`) is the primary small-screen habit. If a window
genuinely needs a laptop layout, toggle instead of hand-resizing:

```zsh
# tmux-fit — toggle main-horizontal "laptop layout"; second call restores
tmux-fit() {
  local saved
  saved=$(tmux show-options -wv @fit-saved 2>/dev/null)
  if [ -n "$saved" ]; then
    tmux select-layout "$saved"
    tmux set-option -wu @fit-saved
  else
    tmux set-option -w @fit-saved "$(tmux display -p '#{window_layout}')"
    tmux select-layout main-horizontal
  fi
}
```

### Windows clients (alacritty)

- One pinned shortcut per server (or per daily-driver session):

  ```
  alacritty --title "WORK @ <server>" -e ssh <server> -t "tmux new -A -s WORK"
  ```

  `new -A` = attach-or-create, survives server reboots. Alacritty has
  no tabs by design — one OS window per server/monitor, alt-tab
  between them; tmux is the only mux.
- Per-machine geometry via alacritty.toml `import`: shared base +
  tiny per-device file (font size, padding). Nothing else is
  device-specific.
- **Terminfo gotcha**: alacritty sets `TERM=alacritty`, which older
  server terminfo lacks (borked colors / "unknown terminal" outside
  tmux). Fix once per server (install alacritty terminfo) or in the
  Windows-side `~/.ssh/config`:

  ```
  Host *
      SetEnv TERM=xterm-256color
  ```

  Inside tmux the conf's `default-terminal screen-256color` insulates
  regardless.

## Example session blueprint

Adapt to whatever actually lives on your server; the shape is the point.

| Class | Session | Contents |
|---|---|---|
| OPS | `TRADE-MONITOR` | live checkouts of the trading stack, hedger/fleet monitoring |
| OPS | `SERVERS` | hop/monitor windows, each named after its host |
| WORK | `CORE` | your main program of work: one window per repo it touches |
| WORK | `RESEARCH` | the current research program's repos and notebooks |
| WORK | `META` | dotclaude, work-journal, editor configs, infra odds and ends |
| WORK | `PERSONAL` | exercises, side learning (keep it out of the work sessions) |

Do not fold two programs of work into one session — merging programs is
how the junk drawer happens.

## Known caveats

- **Simultaneous same-window, two geometries**: `window-size latest`
  means last keystroke wins — the window flip-flops. Viewports fix
  current-window contention, not same-window geometry. No clean tmux
  answer; don't co-view one window from two screen sizes.
- **resurrect + grouped sessions**: a viewport alive at save time can
  resurrect as an ordinary zombie session. `destroy-unattached` makes
  this rare; the monthly prune catches stragglers.
- **`window-size manual` scope**: the pinned size comes from the
  *session's* `default-size`, so an OPS session has one pinned
  geometry for all its manual windows — another reason OPS sessions
  stay single-purpose.
