# Generative trigger sentence for the ascii-graph chat card

Date: 2026-08-12
Status: brief (axes walked in-conversation 2026-08-11→12; user ratified option 1, rejected options 2/3)

## Problem

Chat-side visualization has doctrine but no generation trigger: the
shipped trigger card is guard-shaped ("before typing box art → use the
tool"), and the descriptive channel rule (family-relay §(b)) is
behaviorally inert (measured 0/2 on haiku while provably in context).
The proven lever is the imperative action-moment card: the same A/B
flipped behavior 2/2 (docs/loom/memory/imperative-trigger-cards-beat-descriptive-preloads.md).
Job: when an agent is about to EXPLAIN a flow/state/architecture shape
to the user in chat, a diagram should be generated first — proactively,
not only when the agent already decided to draw.

## Users

kouko + any agent session on Claude Code AND Codex — the card ships in
`ascii-graph-toolkit/hooks/trigger-card.md`, emitted by a SessionStart
hook whose JSON shape both hosts consume (verified against Codex
0.139.0: loom-code/skills/using-loom-code/references/codex-tools.md:70-83).
One file edit reaches both hosts.

## Smallest End State

1. ONE generative imperative sentence appended to
   `ascii-graph-toolkit/hooks/trigger-card.md` (pinned verbatim in the
   plan): quantified trigger (≥3 steps/states/components), lead-with-
   diagram instruction, anti-decoration guard ("one short paragraph
   covers it → don't draw"), option-fork table carve-out preserved.
   Existing pinned phrases ("ascii-graph", "CJK", "Trivial all-ASCII
   sketches") and hooks.json wiring stay intact
   (ascii-graph-toolkit/scripts/test_trigger_card.py:60-63).
2. Pin test extended: new test function asserting the generative
   sentence's full load-bearing phrases (grep-pin discipline).
3. Behavioral A/B before ship: headless `--plugin-dir` probes per
   docs/loom/memory/headless-branch-plugin-testing-recipe.md — baseline
   (main's card) vs candidate (branch card), n≥2 per leg, weak tier;
   report → docs/loom/dogfood/. Codex-side injection probe: post-merge
   rider (marketplace tracks GitHub main —
   auto-memory feedback_marketplace_github_source_blocks_premerge_deploy_ab),
   folded into the existing backlog telemetry item.
4. Version bump 0.5.0 → 0.6.0, both manifests via
   `python3 scripts/sync_codex_manifests.py ascii-graph-toolkit`
   (verified script; SSOT `.claude-plugin/plugin.json`). No CHANGELOG:
   this plugin has never carried one (ls verified 2026-08-12) — the
   Keep-a-Changelog convention entry
   (docs/loom/memory/version-bump-packets-must-name-changelog-entry.md)
   applies to plugins that HAVE one; creating one here is out of scope.
   No shipping-version pin test exists in this plugin (task-kind recall
   grep, 2026-08-12).

## Current State Evidence

- **Forward**: card text `ascii-graph-toolkit/hooks/trigger-card.md`
  (7 lines, guard-shaped only); emitted via `hooks/session-start:45`.
- **Reverse**: card is SSOT for its own text; family-relay §(b) stays
  the channel-rule SSOT the card's doctrine complements — NOT edited
  (user rejected option 2: redundant second always-on surface, blast
  radius on freshly-shipped Pin B citations; decision recorded
  2026-08-12 conversation).
- **Error**: over-firing → decoration guard is in-sentence; pin tests
  keep existing exemptions alive.
- **Data**: A/B precedent 2/2 vs 0/2
  (docs/loom/dogfood/2026-07-10-visual-trigger-weak-model-dogfood.md).
- **Boundary**: test_trigger_card.py content pins (three phrases +
  hooks.json wiring + description constraints — description NOT touched
  this arc); suite `python3 -m pytest ascii-graph-toolkit/scripts/ -q`
  runs locally only (no CI workflow covers this plugin's scripts/ —
  pre-existing gap, recorded as debt, not fixed here).

## Decision

Add the generative trigger as ONE pinned sentence on the existing card
(single SSOT, proven carrier, cross-host by construction). NOT building:
family-relay §(b) rewrite (option 2 — rejected), relay-seam diagram
slots (option 3 — over-engineering), SKILL.md description changes
(routing surface, not the behavior gap), a CHANGELOG for this plugin,
CI wiring for its test suite.

## Out of Scope

- family-relay.md, loom-* plugins, visual-companion.md — untouched.
- Codex-side behavioral probe pre-merge (post-merge rider, see above).
- Telemetry re-run (existing backlog item
  2026-07-10-ascii-graph-trigger-fix-post-ship-telemetry-a-b-re-run —
  the new sentence joins that measurement when it fires).

## What Becomes Obsolete

Nothing removed; the card grows one sentence (guard-shaped rules keep
their jobs).

## Open Questions

None — A/B failing (candidate ≤ baseline) routes back to sentence
wording, which is the plan's revision loop, not a user decision.
