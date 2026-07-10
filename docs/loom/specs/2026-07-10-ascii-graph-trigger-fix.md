# Brief: ascii-graph trigger-rate fix (PR1) + loom visual-contract preload (PR2)

Date: 2026-07-10 · Branch: more-visualization · Author: brainstorming session
(decision pre-made by user via dev-workflow:brief-before-asking; this brief
formalizes scope for writing-plans — it does not reopen the option fork)

## Problem

When the model is mid-response and about to draw a diagram, nothing in the
loaded context reminds it that a width-safe generator exists — drawing is a
reflexive act (like emitting a bullet list), so it never passes through skill
routing. Measured over 1,042 local sessions (2026-07-10):

- 29 `ascii-graph-toolkit:ascii-graph` invocations total; 28 in its own
  dogfood sandboxes; **1 organic firing in real work** — and that one was
  triggered by the user's global CLAUDE.md width rule, not by the skill
  description or any loom mechanism.
- **56 sessions hand-drew box-drawing diagrams containing CJK labels** (the
  exact case the tool exists for), tool globally enabled and description
  fully present in the listing (379 chars, under the ~1536 budget).
- The loom family's visual rules live in pull-based references that are
  never pulled: `family-relay.md` actually Read in **1/216** loom sessions;
  `visual-companion.md` Read in **0/56** brainstorming sessions.

Job to be done: put the trigger rule where the drawing moment actually
happens — the always-loaded session context — and make the loom family's
visual-communication contract load-bearing instead of aspirational.

## Users

- kouko (zh-TW / ja / en), reading in narrow IDE panes and terminals where
  eyeballed CJK padding visibly breaks; sessions span all projects, not just
  monkey-skills (dotfiles, obsidian vault, Xcode projects all hand-drew).
- Weak-model subagents inside loom workflows (relay discipline consumers).

## Design-side on-ramp

Negative guard applies (infrastructure increment to existing plugins, not
product-shaped new work) — Axis 0 skipped silently.

## Smallest End State

**PR1 — ascii-graph-toolkit 0.4.0 → 0.5.0** (always-loaded trigger card +
action-moment description):

1. New `hooks/hooks.json` + `hooks/session-start` emitting a **≤5-line
   trigger card** via `hookSpecificOutput.additionalContext` (3-key
   defensive shape, mirroring `loom-pipeline/hooks/session-start`; fail-open
   on missing file). Card rule: *before typing any box-drawing / ASCII
   diagram in chat or a text artifact — CJK labels or ≥3 boxes → invoke the
   `ascii-graph` skill first; trivial all-ASCII sketches exempt.*
2. `skills/ascii-graph/SKILL.md` description rewritten as an action-moment
   sentence ("Use BEFORE typing the first `┌` of any ASCII/box-drawing
   diagram…"), keeping **at most one** representative CJK trigger phrase
   (CJK keyword stuffing is A/B-refuted — see
   `docs/loom/memory/skill-triggering-diagnose-listing-before-text.md`).
3. `.claude-plugin/marketplace.json` description synced; `plugin.json`
   version bump.
4. Tests first (TDD): new pytest pinning (a) hooks.json wiring shape,
   (b) card content strings, (c) description contains the action-moment
   phrase — repo precedent: `loom-pipeline/scripts/test_family_relay.py`.

**PR2 — loom-pipeline 0.6.1 → next + loom-code 0.28.0 → next** (preload the
visual contract):

1. `loom-pipeline/hooks/session-start` additionally extracts
   `family-relay.md §(b) Visual defaults` **at runtime** and appends it to
   the injected reception card. Pointer-not-copy is preserved: the SSOT
   stays `family-relay.md`, extraction is mechanical, no duplicated text in
   the repo (the family anti-copy convention is test-pinned).
2. `loom-code/skills/brainstorming/SKILL.md` §Visual companion gains the
   operative one-liner: flow/state diagrams in briefs and summaries are
   generated via `ascii-graph-toolkit`, not hand-drawn (word headroom OK:
   3,562 / 4,500 CHK-SKL-010).
3. Tests first: extend `test_family_relay.py` — reception output includes
   the Visual-defaults section; brainstorming SKILL.md carries the operative
   line.

## Current State Evidence

- **Forward** (who consumes the touched artifacts): Claude Code SessionStart
  consumes `hooks/hooks.json` (wiring pattern at
  `loom-pipeline/hooks/hooks.json:3-13`); the host skill listing consumes
  `ascii-graph-toolkit/skills/ascii-graph/SKILL.md:3` (description live,
  not evicted — verified in this session's listing).
- **Reverse** (SSOT / sync direction): `family-relay.md` is SSOT for relay
  discipline, test-pinned at `loom-pipeline/scripts/test_family_relay.py:78-79`
  (`"ascii-graph-toolkit"`, `"markdown comparison table"` must remain);
  plugin description has a marketplace copy at
  `.claude-plugin/marketplace.json:128-130` (sync required); loom-code
  knowledge-layer `distribute.py` is NOT involved.
- **Error**: `loom-pipeline/hooks/session-start:24+` fails open (empty
  context, exit 0) when its markdown source is missing — PR1's hook mirrors
  this; a crashing SessionStart hook would break every session start.
- **Data**: injection card costs ~100-150 tokens per session across ALL
  projects (accepted by user in the option decision); baseline telemetry
  for post-ship comparison: 1/1042 organic firing, 56 CJK hand-drawn
  sessions, 1/216 relay reads, 0/56 companion reads (measurement scripts
  preserved in session scratchpad).
- **Boundary**: Codex host — the plugin ships `.codex-plugin/plugin.json`,
  but Codex hook support is upstream-pending (see
  `docs/loom/memory/` store, loom-memory-store entry); PR1's hook is
  Claude-Code-effective only; the description rewrite benefits both hosts.
  `ascii-graph-toolkit` has no existing `hooks/` dir (greenfield inside the
  plugin).

## Decision

Build PR1 (injection card + action-moment description) as the primary
mechanism — always-loaded context is the only empirically working trigger
path (the single organic firing came from a standing CLAUDE.md rule). Build
PR2 to make the loom family's visual contract load-bearing by mechanical
preload instead of model-initiated pull.

Will NOT build: user-CLAUDE.md edits (propose-only jurisdiction; deferred —
option C); hook interception of chat text (infeasible — hooks fire on tool
calls, and 7/7 sampled hand-drawn diagrams were chat text, not file writes);
any new measurement harness (reuse `loom_firing_harness.py` and this
session's scripts for post-ship re-measurement).

## Alternatives Considered

Four options (A description rewrite / B plugin injection card / C CLAUDE.md
rule sharpening / D loom contract relocation) were compared on local
telemetry via `dev-workflow:brief-before-asking`; user chose **B+A in PR1,
D as PR2**; C deferred (user-diff-gated jurisdiction + redundant with B).
Industry web-search waived: the mechanism (Claude Code plugin SessionStart
injection) is host-specific with a proven in-house precedent (loom family
reception card), and the option evidence is measured local behavior, which
dominates imagined external comparisons here.

## What Becomes Obsolete

- The noun-phrase description at `skills/ascii-graph/SKILL.md:3` (replaced
  in the same PR).
- The assumption that `family-relay.md §(b)` reaches sessions via
  model-initiated pull (superseded by mechanical extraction; the file itself
  stays — SSOT, test-pinned, no deletion).
- `visual-companion.md` stops being the sole carrier of brainstorming's
  visual rule (file stays; strings test-pinned by
  `test_brainstorming_visuals`).

## Out of Scope

- User-level CLAUDE.md / dotfiles edits (option C).
- Any change to ascii-graph generators/verify-loop themselves (the tool
  works; the problem is triggering).
- Codex-side hook support (upstream-pending).
- New skills, new measurement infrastructure, MEMORY.md graduation.
- Retro-fixing the 56 historical hand-drawn diagrams.

## Open Questions

- PR1 card final wording — drafted at plan stage, validated by cold-reader
  dogfood (fresh-context agent + realistic "draw me a diagram" prompt per
  `docs/loom/memory/process-mechanism-dogfood-via-coldreader-real-commits.md`
  analog); full two-run corpus A/B on the firing harness is deferred to
  post-ship telemetry re-run (trigger moment is mid-response, which the
  prompt-routing corpus only partially exercises).
- Whether PR2's runtime extraction should include §(c) Turn-ordering too —
  default NO (scope: visual defaults only; turn-ordering is
  brief-before-asking's jurisdiction).
