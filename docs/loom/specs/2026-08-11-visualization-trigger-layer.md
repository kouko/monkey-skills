# Visualization trigger layer for the loom family

Date: 2026-08-11
Status: brief (brainstorming output → writing-plans input)

## Problem

The loom family has visualization *doctrine* but no visualization *behavior*.
Every existing rule is guard-shaped — it regulates HOW to draw once drawing
has been decided (channel rule, tool choice, anti-patterns) — while the only
generation trigger (content-shape → diagram-type mapping) lives in one
pull-loaded reference of one skill (`loom-code/skills/brainstorming/references/visual-companion.md`).
Measured outcome in this repo: 1 of 29 plans/briefs contains a Mermaid block,
9 of 29 contain (mostly hand-drawn) box art, 0 files under `docs/loom/` +
`loom-code/docs/` contain Mermaid. The job to be done: flow-, state-, and
architecture-shaped content in loom artifacts and loom chat should actually
get drawn, in the form each channel renders.

Key causal finding: `handoff-brief-format.md:100` ALREADY has a `## Diagrams`
section, and briefs still ship without diagrams — an optional slot with no
fill-or-declare obligation and no reviewer check does not change behavior.
Preloaded prose defaults don't either (family-relay §(b) is preloaded every
session; behavior unchanged). Judgment-shaped prose drifts; verifiable
actions survive (established repo doctrine).

## Users

- kouko (primary): reads loom-produced briefs/plans/specs/PR bodies in
  GitHub + IDE, and chat in a terminal that does NOT render Mermaid.
- Downstream loom agents (reviewers, implementers) consuming those artifacts.
- External repos installing loom plugins (kumiko et al.): may NOT have
  `ascii-graph-toolkit` or `obsidian` plugins installed — any dependence on
  them must be availability-guarded, not assumed (environmental absence, a
  legitimate fallback class per
  `docs/loom/memory/a-documented-fallback-can-legitimize-a-delivery-gap.md`).
- Hosts: Claude Code today, Codex port pending — everything must stay
  host-neutral (no Claude-only preview paths in doctrine).

## Channel rule (settled with user, 2026-08-11)

- **Committed `.md` artifacts** → Mermaid is the default diagram form
  (zero-dependency text syntax; GitHub/Obsidian render it).
- **Chat** → option forks render as markdown tables; flow/state/architecture
  shapes render via `ascii-graph-toolkit` WHEN the skill is available,
  degrade to a markdown table when absent; hand-drawn CJK box art stays
  forbidden. SSOT for this rule remains
  `loom-pipeline/hooks/family-relay.md §(b)` — new text points at it, never
  copies it (anti-copy convention, test-pinned).

## Smallest End State

Four changes, shape-triggered (never count-triggered):

1. **ascii-ui-patterns ↔ toolkit contradiction fix** (loom-interface-design):
   `skills/interaction-flows/references/ascii-ui-patterns.md` currently
   instructs hand-drawing box characters and never mentions
   `ascii-graph-toolkit` — the exact failure mode the toolkit prevents (its
   own Pattern 1 example at `:39-51` is width-inconsistent). Add an
   availability-guarded generation instruction: toolkit listed → generate/
   verify layouts with it; absent → hand-draw is permitted for pure-ASCII
   labels only, CJK labels degrade to a labeled prose/table description.
2. **Structural diagram slots in the three writer templates** (primary
   change): each template gains a diagram section whose contract is
   *fill-or-declare* — the writer either embeds the diagram or writes the
   pinned N/A line (`N/A — no flow/state/architecture-shaped content: <one
   line why>`). A bare absent section becomes a reviewable omission; a false
   N/A becomes a reviewable claim. Slots:
   - `loom-code/skills/brainstorming/references/handoff-brief-format.md` —
     upgrade the existing `## Diagrams` section from optional to
     fill-or-declare.
   - `loom-code/skills/writing-plans/references/plan-format.md` — add one
     plan-level slot (task dependency/flow shape), NOT per-task.
   - `loom-spec/skills/spec-expansion/SKILL.md` (+ its artifact schema
     sections) — state-machine content → Mermaid `stateDiagram-v2`; OOUX
     object model relations → Mermaid `erDiagram`.
3. **Reviewer feedback loop** (loom-code): add missing-diagram-slot /
   unjustified-N/A to `agents/docs-reviewer.md`'s omission dimension
   prompt (a check on artifacts that carry a slot contract, not a new
   dimension, not a convergence-loop change). Static verification only this
   session — an in-session dispatched reviewer runs the cached plugin
   contract, not the branch edit
   (`docs/loom/memory/agent-contract-edits-do-not-reach-this-sessions-subagents.md`).
4. **Rider pointers** (demoted, cheap only): where a touched file already
   discusses visuals, add a one-line pointer to visual-companion / §(b).
   No standalone pointer-wiring task — pointer-only wiring is empirically
   ineffective (see Problem).

Industry grounding (Axis 4, EN+JA agree): arc42 gives each architecture
information type a fixed *place* (typed sections), not a diagram quota
([arc42 overview](https://arc42.org/overview/),
[arc42 template repo](https://github.com/arc42/arc42-template)); JA practice
maps content shape → diagram type (flow→flowchart, 状態→stateDiagram,
順序→sequence, 構造→class/ER) and votes Mermaid-in-git for diffable review
([Zenn 基本設計 Mermaid サンプル集](https://zenn.dev/maman/articles/59a3f6f2723001),
[一創 Mermaid ガイド](https://www.issoh.co.jp/tech/details/3374/)).
Neither language's practice mandates minimum diagram counts — quota designs
rejected.

## Current State Evidence

- **Forward** (where the new obligations land): brief template
  `loom-code/skills/brainstorming/references/handoff-brief-format.md:100`
  (`## Diagrams` exists, optional today); plan schema
  `loom-code/skills/writing-plans/references/plan-format.md:24`; spec
  artifact sections `loom-spec/skills/spec-expansion/SKILL.md:197,220`;
  reviewer omission dimension `loom-code/agents/docs-reviewer.md:485-490`.
- **Reverse** (SSOT direction): channel rule SSOT =
  `loom-pipeline/hooks/family-relay.md:90-98` §(b); when-to-draw SSOT =
  `visual-companion.md` (incl. `:16` "paragraph suffices → don't draw",
  `:111-114` anti-patterns). New text POINTS at both; the family anti-copy
  convention is test-pinned (`loom-pipeline/scripts/test_family_relay.py:92,193,270,374`).
  loom-code knowledge layer syncs to domain-teams via `scripts/distribute.py`
  — none of the touched files are in that sync set (verified by the
  inventory pass; re-verify at plan time).
- **Error** (failure modes designed against): false `N/A` → reviewable
  claim under docs-reviewer omission prompt; decorative diagrams →
  visual-companion anti-pattern 1 stays the counterweight, slots fire on
  shape only; toolkit absent in external repo → guarded degrade path with
  the absence-class stated (environmental, not undelivered).
- **Data** (baseline for post-ship comparison): 1/29 plans-briefs with
  Mermaid, 9/29 with box-drawing chars, 0 Mermaid under `docs/loom/` +
  `loom-code/docs/` (grep, 2026-08-11).
- **Boundary** (blast surfaces): family-relay pointer tests (above);
  description/content pins in each plugin's `scripts/` guard tests — every
  task packet carries the owning plugin's package suite
  (`docs/loom/memory/description-sweeps-must-run-owning-plugin-suite.md`);
  three plugins bump versions (loom-code, loom-spec, loom-interface-design)
  each with `.codex-plugin` manifest mirror + marketplace sync; skill-folder
  flatness hook (`.claude/hooks/validate-skill-folder-structure.sh`);
  SKILL.md ~6k-token body cap.

## Decision

Build the trigger layer as *structural slots + reviewer loop*, not as more
prose defaults: upgrade/insert fill-or-declare diagram slots in brief, plan,
and spec templates (Mermaid forms named per content shape); wire
missing-slot/false-N/A into docs-reviewer's omission prompt; fix the
ascii-ui-patterns hand-drawing contradiction with an availability-guarded
toolkit instruction. The shared N/A line and slot wording are PINNED in the
plan's ## Notes and transcribed verbatim into every template
(`docs/loom/memory/pin-shared-wording-in-plan-copies-transcribe-from-pin.md`);
any new grep pins assert the full phrase the failure message names
(`docs/loom/memory/substring-assertions-must-pin-the-phrase-their-message-names.md`).
We will NOT build: diagram quotas, a new reviewer dimension, a chat-side
hook, any Mermaid-preview mechanism (host-specific), pointer-only wiring as
a standalone change, and no changes to loom-discovery / loom-product-principles
(text-argument artifacts; forcing diagrams there hits visual-companion
anti-pattern 1).

## Out of Scope

- loom-discovery / loom-product-principles templates — unchanged.
- family-relay.md §(b) content changes — it stays SSOT as-is.
- The SessionStart diagram trigger card (ascii-graph-toolkit's own) — owned
  outside the loom family; unchanged.
- Chat-side enforcement hooks (no mechanical gate on conversation turns).
- Regenerating every existing shipped doc — old artifacts stay as-is;
  slots apply to newly written artifacts.
- Host-specific preview affordances (SendUserFile/Artifact render paths).
- Backlog telemetry item `2026-07-10-ascii-graph-trigger-fix-post-ship-telemetry-a-b-re-run`
  — separate re-run, unaffected.

## What Becomes Obsolete

- `ascii-ui-patterns.md`'s hand-drawn-box instructions (and its
  width-inconsistent example rows) as the *primary* path — replaced by the
  guarded toolkit instruction; the patterns' semantic content (region tags,
  coarse-skeleton conventions) survives.
- The `## Diagrams` section's optional status in handoff-brief-format.md —
  superseded by fill-or-declare.
- Nothing else deleted; this is a tightening, and the additive surface is
  bounded to three template slots + one reviewer prompt line.

## Open Questions

1. Regenerate ascii-ui-patterns' misaligned example rows via the toolkit in
   this arc, or record as debt? (Cheap if the toolkit run is one command;
   decide at plan time.)
2. Backlog riders whose start-triggers this arc fires:
   `2026-07-06-anti-copy-acceptance-greps-pass-paraphrase-copies` (fires on
   next writing-plans touch) and
   `2026-07-10-grounding-notes-for-sibling-stations-claude-code-tools-md`
   (fires on next loom-spec / loom-interface-design references touch).
   Adopt as in-arc riders or explicitly re-park? (User call at plan
   checkpoint.)

## Design-side on-ramp

Increment to existing loom-family plugins (not product-shaped new work) —
Axis 0 upstream walk skipped per negative guard; backlog ready check run
(`## Now` empty; two related OPEN items surfaced above). loom-init N/A
(queue layer already adopted).
