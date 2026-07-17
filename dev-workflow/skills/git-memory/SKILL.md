---
name: git-memory
description: |
  Mandatory gate before every git commit / gh pr create / gh pr merge — the skill decides whether memory trailers (Decision/Learning/Gotcha) apply; don't pre-judge a commit 'routine'. Also recalls past decisions: 'why did we…', '為什麼', an old branch.
---

# Git Memory

Durable lessons live in the repo's committed memory store
(`docs/loom/memory/` here) — the authoritative carrier. Commit trailers are
commit-bound capture: best-effort, secondary, and never the retrieval path
a durable lesson depends on. This skill mechanizes that commit-bound
capture — portable, tool-agnostic decision context riding in git commit
messages and PR bodies.

## Invocation policy

> **The skill is an invocation gate, not a trailer gate.**

Two distinct decisions must not be conflated:

| Decision | Who decides | When |
|----------|-------------|------|
| **Should this skill be invoked?** | The caller | Before `git commit` / `gh pr create` / `gh pr merge` — answer is **always yes** in a Claude session |
| **Should this commit carry memory trailers?** | The skill | Inside the skill — routine commits exit cleanly with no trailers |

`gh pr merge` (esp. `--squash`) is the **last checkpoint before the
branch closes** and the capture can end up empty. A squash *relocates*
each commit's trailers into the squash commit's mid-body — still
retrievable via `git log --grep`, though no longer footer-parseable
(`%(trailers)`) — so on a squash `main` there are **two** commit-bound
capture locations (best-effort, not the durable carrier — see the
hierarchy above): the grep-able mid-body trailers and the PR `## Memory`
section (which additionally survives and renders on GitHub). Fire the
gate here too — the *always yes* rule holds, only the trailer outcome
varies.

Pre-deciding "this commit is routine, I'll skip the skill" is the bug.
The skill's classification logic (routine vs non-routine, see *When not to
use* below) belongs **inside** the skill, not in the caller's head. Skipping
the skill loses the audit trail of "we considered memory and decided no",
and biases toward under-recording over time.

**Concretely**: even when the skill outputs *"no trailers needed for this
commit"*, the invocation itself ensures consistent decision-making and
catches the cases where the caller would have wrongly classified a
non-trivial commit as routine.

## Core thesis

Write the **why** of a decision into commit messages and PR bodies —
best-effort, commit-bound capture that any future session (Claude Code,
Cursor, Codex, aider, or a human reader) can reconstruct from `git log`.
No database, embedding index, or vendor-specific memory file is needed
for this capture step; where the repo has a committed memory store, that
store — not `git log` — is the durable carrier (see the hierarchy above).

## Three pillars

### Pillar 1 — Carrier: git artifacts as commit-bound capture

Decision context rides in commit messages and PR descriptions as
best-effort capture — not the durable carrier (that's the repo's
committed memory store, per the hierarchy above, where one exists).
Consequences for this capture layer:

- Any tool that can read git can read the memory (Claude / Cursor /
  Codex / aider / `cat` / a human).
- `git clone` brings the memory with it. Switching machines requires
  no sync step.
- Zero infrastructure dependency. No server, no embedding store, no
  vendor lock-in.
- The memory is versioned automatically by git history. `git blame`
  and `git log` are the audit trail.

### Pillar 2 — Structure: commit trailers

Structured facts ride in **git trailers** — the same mechanism as
`Co-Authored-By:` and `Signed-off-by:` (see `git-interpret-trailers(1)`).

- Machine-readable: `git log --grep='^Decision:'` (reliable everywhere)
  and `git log --pretty='%(trailers)'` (feature branch / merge-commit
  repos — see squash caveat below) make retrieval trivial.
- Coexists with prose: the commit body reads naturally for humans;
  trailers carry the structured signal for machines.
- Git-native: trailer format is part of core git, not a Claude Code
  convention. Every git hosting platform preserves trailers as raw
  text — true for rendering and non-squash merges; a squash merge
  relocates them mid-body (see caveat below).
- Minimum viable schema — three trailers cover ~80% of value:
  - `Decision:` — why this approach was chosen
  - `Learning:` — what was discovered during the work
  - `Gotcha:` — a trap for future self or other readers

> **Squash-merge caveat — `%(trailers)` is unreliable on the default branch.**
> A squash merge concatenates every per-commit message into one squash
> commit, so the original trailers land in the **mid-body**, not the
> footer. `git log --pretty='%(trailers)'` and `git interpret-trailers
> --parse` read **only the footer**, so on a squash-merge `main` they
> miss the buried trailers. `git log --grep='^Decision:'` is a **text**
> match that still finds them on `main` — useful for spot-checking, but
> this is commit-bound capture, never the durable retrieval path (that's
> the repo's committed memory store, per the hierarchy above). Ending
> the PR body with the raw trailer footer required by the O2 mandate
> below (see `protocols/compose-pr.md`) is a **best-effort** measure,
> not a guarantee: GitHub's own squash-merge UI can append a
> `---------` divider + `Co-authored-by:` block AFTER the body and
> hard-wrap long trailer lines (both live-observed on PR #576), which
> breaks `%(trailers)` for the body's own keys even when the PR body
> itself ends with the footer correctly. The reliable paths stay
> `git log --grep` + the PR `## Memory` section + the repo's committed
> memory store; the footer's guaranteed floor is that its keys stay at
> line starts for grep — not a `%(trailers)`-parses guarantee.

Best-effort capture location by repo style (not a durable-retrieval
ranking — see the hierarchy above):

| Repo merge style | Where the capture survives |
|---|---|
| **Squash merge** (default branch) | `git log --grep` + the PR `## Memory` section (always survive); `%(trailers)` is best-effort only — GitHub's squash-merge UI can append a `Co-authored-by:` block/divider after the body even when it ends with the mandated raw trailer footer (see caveat above) |
| **Feature branch** (pre-squash) | `%(trailers)` structured parse |
| **Merge-commit / rebase-merge** | `%(trailers)` structured parse |

**Verification is required before a memory-worthy PR closes.** The
confirmed failure mode is authoring-time under-recording — a
memory-worthy PR closing with an empty capture, *not* a squash-loss
problem. So before merge, **verify the commit-bound capture actually
landed** (this verifies capture, not durable filing — see the hierarchy
above):

- Run `scripts/memory-grep.sh --verify <ref>` against the commit
  carrier. It exits `0` when a `Decision:`/`Learning:`/`Gotcha:`
  trailer is retrievable from the ref's message body (text match, so it
  works mid-body on a squash `main`), and `4` when the capture is
  empty.
- Confirm the PR `## Memory` section is present (per
  `protocols/compose-pr.md`).
- `--verify-merged <ref>` — the post-merge CI predicate: exits `0` when
  the ref's body has no `## Memory` heading (nothing to check) or the
  heading plus a memory key both survive; `4` on the #574 silent-drop
  case (heading present, no key).
- `--verify-strict <ref>` — a diagnostic, not the durable-lesson path:
  requires the memory key to survive `git interpret-trailers --parse
  --unfold` (a true trailing footer), catching the #575 case where a
  non-trailer line after the trailer block empties the structured parse
  even though plain `--verify` still passes on the text match.

An empty result is a flag to fix **before** merge, not to ignore.
This verification is **enforced as an executable gate by
`loom-code:finishing-a-development-branch`** at branch close-out — it
runs `memory-grep.sh --verify HEAD` and STOPs when a memory-worthy
branch's commit carrier is empty (exit `4`).

Structured `%(trailers)` footer-parse on `main` is not an opt-in escape
hatch — it is the **mechanized mandate** in `protocols/compose-pr.md`
(Step 4): a memory-worthy PR body MUST end with a raw trailer block
(`Decision:` / `Learning:` / `Gotcha:`, unbolded) as the absolute last
block, placed after even the `🤖 Generated with` footer. This repo's
squash mode is `squash_merge_commit_message = PR_BODY`, so the PR body
becomes the squash commit's message verbatim — only a trailer block
that is that message's true last block parses via `%(trailers)`. See
`protocols/compose-pr.md` for the exact placement rule, the
anti-pattern that empties `%(trailers)`, and a worked before/after
example. A **merge-commit** (not squash) for memory-worthy PRs remains
a valid alternative, preserving each commit's footer natively.

See `standards/memory-conventions.md` for the full schema, line-length
rules, and examples.

### Pillar 3 — Content: decision context, not code

The git diff already shows **what** changed. Memory records the **why**.

- Record: the reason behind a non-obvious choice, alternatives
  considered and rejected, surprising behavior discovered,
  gotchas to avoid.
- Don't record: what the diff already makes obvious ("added function
  foo"), implementation details, routine fixes, typo corrections.
- Aim for entries that stay valuable six months later when the
  original context is gone — not entries that are redundant with
  the code itself.

## When to use

- Recording a non-trivial design decision (why this approach, not
  the alternatives)
- Capturing a gotcha or surprising constraint discovered mid-implementation
- Surfacing relevant past decisions when starting new work in a repo
- Making project knowledge survive a machine change or a tool switch
- Complementing Claude Code's native `~/.claude/.../MEMORY.md`
  (user-level preferences) with repo-level project knowledge

## When not to use

> The lines below describe when the skill **outputs no trailers**, not
> when to skip invoking the skill. See *Invocation policy* above — the
> skill is always invoked; only the trailer outcome varies.

- **Routine commits → skill exits with no trailers.** Typo fixes, version
  bumps, formatting changes — memory trailers would be pure noise. The
  skill itself recognises these and outputs an empty trailer set.
- **User-level preferences not tied to a repo** (e.g. "user prefers
  concise responses") — those belong in Claude Code's native memory,
  not in git. The skill does not write these as git-memory trailers.
- **Secrets or sensitive context** — git is public-by-default; use
  `.gitignore`d notes or secret managers instead. The skill refuses
  to embed secrets in commit trailers.
- **Replacing Claude Code's memory wholesale** — git-memory complements
  it, does not substitute for it. Both layers coexist; see the
  *Relationship to Claude Code native memory* table below.

## Relationship to Claude Code native memory

| Layer | Substrate | Scope | Owner |
|---|---|---|---|
| Claude Code native | `~/.claude/projects/{slug}/memory/MEMORY.md` | User-level preferences, cross-project | The individual user |
| git-memory | commit messages + PR bodies in-repo | Project decisions, shared knowledge | The repo (team or solo) |

The two are complementary. A user preference ("kouko prefers
terse replies") stays in Claude native memory. A project decision
("we adopted two-layer i18n because API surface is English but
user-facing design needs trilingual") belongs in git-memory.

The two are recalled differently: Claude Code native memory is
**pushed** (auto-loaded every session), while git-memory is **pulled**
on demand — you retrieve the few project decisions relevant to the task
at hand rather than preloading them (see `protocols/recall.md`).
Distilling git-memory into an always-loaded `MEMORY.md` is deliberately
**not** the design: auto-generated, always-loaded context files tend to
degrade agent performance (see `standards/memory-conventions.md`
§Pull retrieval for the evidence), so retrieval stays on-demand.

## Phased rollout

- **Phase 1 (MVP, this version)** — conventions + a retrieval
  primitive. Claude helps compose commit trailers and the PR
  `## Memory` section when prompted.
- **Phase 2** — install script for `attribution.commit` integration,
  optional pre-commit validate hook. (A static PR template under
  `.github/` is deferred until humans-opening-PRs-via-GitHub-UI
  becomes a real use case in this repo — Claude-authored PRs
  bypass the template entirely via `gh pr create --body`.)
- **Phase 3** — pull retrieval surface: on-demand topic/area recall over
  the substrate (`memory-grep.sh --match` / `--path` / `--top`, driven by
  `protocols/recall.md`), so past decisions surface when the task needs
  them. This deliberately replaces the earlier "distill into an
  always-loaded `MEMORY.md`" idea — preloaded auto-generated context
  tends to hurt agents (evidence in `standards/memory-conventions.md`
  §Pull retrieval); on-demand pull does not. A future step could expose the
  same retrieval as an MCP tool for cross-agent ambient querying, but
  that trades away the zero-infra property and is deferred until a
  multi-agent / larger-team need is real.

## Resources

- `standards/memory-conventions.md` — trailer schema, PR body section
  layout, diagram venue rules
- `protocols/compose-commit.md` — guidance for writing commit messages
  with memory trailers
- `protocols/compose-pr.md` — guidance for writing PR bodies with a
  `## Memory` section
- `protocols/recall.md` — when and how to **pull** past decisions
  (topic/area triggers, liveness defaults, surfacing to the user)
- `scripts/memory-grep.sh` — retrieval primitive; dumps memory trailers
  + PR `## Memory` sections, with `--match`/`--path`/`--top` for scoped
  recall, `--history` to include superseded decisions, and `--verify`

## Prior art

The approach is closest to **Lore** (Stetsenko, arXiv:2603.15566,
2026) — a git-trailer-based decision protocol with an associated CLI.
`git-memory` deliberately uses a leaner **three-key schema**
(`Decision:` / `Learning:` / `Gotcha:`, plus the `Related:` /
`Supersedes:` link trailers) rather than Lore's 12-trailer schema, to
keep the per-commit cognitive load low. Note this is a *different*
schema, not a subset — only `Related:` overlaps by name.

Two deliberate divergences worth recording:

- **On supersession**, Lore's paper leaves conflict-resolution
  undefined; `git-memory` computes liveness from a backward-pointing
  `Supersedes:` (see `standards/memory-conventions.md`).
- **On substrate**, Lore's *shipped* product (`rac`, github.com/
  itsthelore/rac-core, 2026) moved off commit trailers to typed Markdown
  files served read-only over MCP with CI-enforced status — a divergence
  from the paper's trailer-based protocol. That is the right lane at
  team/org scale;
  `git-memory` keeps the zero-infra commit-trailer substrate for the
  solo / small-team case, and treats "graduate to a Markdown + MCP
  store" as an explicit signal for when the repo outgrows it.

Related prior art:

- **Letta Context Repositories** (2026-01) — git-backed agent memory
  with markdown files committed to the repo; auto-commit on memory
  change
- **Git Context Controller** (arXiv:2508.00031, 2025-08) — COMMIT /
  BRANCH / MERGE as agent-memory primitives

## License

MIT — see repository root `LICENSE`.
