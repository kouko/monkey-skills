# UX-Flow Checklist — 7 generation dimensions for `ui-flows.md`

These are **generation prompts**, not post-hoc capture questions. For each
feature/change, actively *produce* the artifact each dimension asks for — do
not merely record what already exists. The output is the **interface surface**
(inventory, navigation, layout, arrival/exit). The **behavioral depth**
(domain state machines, edge cases, acceptance scenarios) belongs to
`spec-toolkit:spec-expansion`, which consumes this file as a rich seed — do not
do its fan-out here.

## Render-variant flag rule (applies to dimension 1)

When you inventory a screen/panel/command, **flag** which render variants it
can present — pick from `empty / loading / error / success` (extend only if a
variant genuinely differs). This is **flag-only**: list the variant names that
exist for that surface; do **not** author the transition logic, guards, or the
full state machine that moves between them. Enumerating *when* and *why* a
surface moves empty → loading → error is the **domain lifecycle**, which is
`spec-toolkit:spec-expansion`'s job. Design stops at "these variants exist";
spec owns "here is how they transition." Doing the fan-out here would duplicate
spec-toolkit.

Per-modality reading of the flag:
- **GUI** — render states of a screen/component (empty list, spinner, error
  banner, populated).
- **TUI** — panel states (blank pane, in-progress indicator, error line,
  filled pane).
- **CLI** — output states of a command (no-results message, progress/streaming,
  non-zero-exit error text, success stdout).

---

## 1. Screen / panel / command inventory (+ render-variant flag)

**Generate** the full list of interface surfaces this feature introduces or
touches, and **flag** the render variants (see flag rule above) each one has.

- **GUI** → enumerate **screens** and major components (e.g. a list screen, a
  detail screen, a create dialog).
- **TUI** → enumerate **panels** / panes (e.g. a tree pane, a content pane, a
  status bar).
- **CLI** → enumerate **commands** and sub-commands (e.g. `widget list`,
  `widget add`, `widget show <id>`).

Example flag: `detail screen — variants: loading, error, success` (variant
names only; no transition rules).

## 2. User flows (mermaid)

**Generate** the user's path through the surfaces as a **mermaid** diagram —
`flowchart` for branching task paths, `stateDiagram` for mode-bound flows,
`journey` for satisfaction-annotated end-to-end journeys. Reuse
`obsidian:obsidian-mermaid-visualizer` for syntax; do not re-author mermaid
rules.

- **GUI** → screen-to-screen **navigation** flow (which screen leads to which).
- **TUI** → panel-focus / keybinding-driven flow (e.g. `Tab` moves focus pane →
  pane).
- **CLI** → **command/output flow** (one command's output feeds the next
  command; piping or copy-an-id chains).

## 3. UI structure (ascii layout)

**Generate** the spatial layout of each key surface as an **ascii layout block**
(mermaid has no native wireframe — issue #1184, so use ascii).

- **GUI** → screen wireframe: header / nav / content region / footer boxes.
- **TUI** → panel layout: pane split ratios, status-bar row, keybinding hint
  row.
- **CLI** → **output format** block: column layout of `list` output, shape of a
  `show` record, help-text layout.

## 4. Transitions (instant / guided / deliberate)

**Generate**, for each move between surfaces, the transition *character* —
choose **instant** (immediate, no friction), **guided** (a wizard / confirm /
intermediate step), or **deliberate** (a heavyweight, explicit, possibly
destructive action gated behind intent). This is the *feel/pacing* of the
move, distinct from the behavioral guard rules spec-expansion owns.

- **GUI** → e.g. instant tab switch vs guided multi-step create vs deliberate
  delete-with-confirm.
- **TUI** → e.g. instant pane focus vs guided modal prompt vs deliberate
  quit-with-unsaved-warning.
- **CLI** → e.g. instant flag default vs guided interactive prompt vs
  deliberate `--force`-required destructive command.

## 5. Entry points (how the user arrives)

**Generate** every way a user can **arrive** at this feature — do not assume a
single front door.

- **GUI** → deep link, nav-menu item, notification tap, search result,
  onboarding step.
- **TUI** → launch flag/sub-command, keybinding from another panel, config
  default view.
- **CLI** → the command itself, an alias, a shell completion, an invocation
  from a script/pipe.

## 6. Exit points (kill dead-ends)

**Generate** the **exit** from every surface — actively hunt for and **kill
dead-ends**: every surface must offer a way forward, back, or out.

- **GUI** → back action, close, cancel, post-success next-step / done screen
  (no screen that traps the user).
- **TUI** → escape-to-previous-pane, quit keybinding, return-to-list after an
  action.
- **CLI** → clean exit code + next-command suggestion in output; an error path
  that tells the user what to run next (not a bare stack trace).

## 7. Information density + mobile flow

**Generate** the density posture of each surface (how much is shown at once;
what is progressively disclosed) **and** the **mobile flow** where the modality
has a small/constrained form factor.

- **GUI** → desktop density vs **mobile flow**: reflow, bottom-sheet, collapsed
  nav, touch-target sizing, single-column stacking.
- **TUI** → density per pane vs **narrow-terminal flow**: behavior at small
  `COLS`/`LINES` (the TUI analogue of mobile — graceful degradation, truncation,
  scroll).
- **CLI** → output density (verbose vs `--quiet`/`--json`) vs **narrow / piped
  flow**: behavior when stdout is not a TTY or width is small (stable
  machine-readable output, no ANSI when piped).

---

## Seam to spec-expansion

This checklist produces the **surface**: inventory, flows, layout, transitions
character, entry/exit, density. The render-variant **flags** name which states
exist. `spec-toolkit:spec-expansion` then does the **behavioral fan-out** —
object state machines, transition rules, edge cases, `#### Scenario:` blocks —
seeded by this file. Keep the boundary: flag here, fan-out there.

## Anti-patterns — NEVER ship these flows

Bad flows share recognizable smells. Name them so the generated `ui-flows.md`
avoids them:

- **NEVER design only the happy path.** The empty / loading / error / success
  variants are where real products live and where users actually get stuck — a
  flow that only shows the success state is half a flow. Flag every variant
  (dimension 1) even when you do not spec its transition.
- **NEVER leave a dead-end surface.** Every surface must offer a way forward,
  back, or out. A screen/panel/command a user can reach but not leave (no nav, no
  back, no exit) is the most common — and most invisible — flow bug.
- **NEVER gate the *primary* task behind a modal or interstitial.** Modals
  interrupt and trap focus; reserve them for destructive confirmation or genuinely
  blocking input. Routing the main job through a modal is friction theater.
- **NEVER add a confirm step to a *reversible* action** (friction with no payoff),
  and **NEVER skip confirmation on an *irreversible* one** (delete, send, pay).
  Match the transition's weight (instant / guided / deliberate) to its
  reversibility, not to habit.
- **NEVER assume a single front door.** Real users arrive via deep links,
  notifications, sub-commands, aliases, pipes, and back-navigation. A flow drawn
  from "user opens the home screen" only is brittle — enumerate the real entry
  points (dimension 5).
- **NEVER bury a primary task more than ~3 steps deep.** Each extra hop sheds
  users; if the core job needs a 5-screen wizard, the information architecture is
  wrong, not the flow.
- **NEVER let a flow drift from PRINCIPLES.md.** A "≤3-step primary task"
  principle and a 6-screen onboarding are in direct conflict — the constitution
  wins; redesign the flow.

The test for each: would a product designer say "yes, learned that the hard way,"
or "that's obvious"? Keep only the former.
