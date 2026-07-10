# Brief: designer/PM loop implementation — PRINCIPLES construction flow + loom-code hardening

Date: 2026-07-10
Stage: brainstorming output → writing-plans input
Design-side on-ramp: offered — direct per repo precedent (monkey-skills deliberately has no `docs/loom/PRINCIPLES.md`; all prior loom stations were built via brainstorming → brief).
Source architecture: `docs/loom/design/2026-07-10-designer-pm-loop-architecture.md` (merged, PR #525)
Dogfood evidence: `docs/loom/dogfood/2026-07-10-designer-pm-loop-paper/` (instrument v0.1 is the flow spec)

## Problem

Two jobs, one boundary (the architecture doc's division of labor):

1. **Construction job**: when a designer/PM brings a product idea to the
   loom PRINCIPLES station, the station must run the dogfood-validated
   construction flow — user states → agent probes (question sets,
   propose-then-react) → 2-3 canon candidates with fit notes (double guard
   vs popularity bias) → user decides → write anchors (version-pinned) +
   deviation ledger + falsifiable principles → per-section and total
   read-back. Today's `product-principles` runs a linear single-ask
   elicitation (SKILL.md L62-67) with none of this.
2. **Consumption job**: when upstream artifacts exist, loom-code must not
   be able to skip them silently. Today writing-plans consumes a
   change-folder only if handed a path (L192-208, no detection at all),
   spec-reviewer sees only the plan (transitive hole), and code-reviewer's
   principles dimension activates only if the orchestrator remembers to
   pass a path (registration-shaped, PR#524-vulnerable).

## Users

- The designer/PM persona (architecture doc §0) authoring a constitution
  in conversation — non-engineer, canon-literate in design, needs
  product-stakes language for engineering choices.
- Downstream agents: writing-plans, spec-reviewer, code-reviewer,
  ui-verification — consuming PRINCIPLES.md and change-folders.
- kouko as plugin owner (ships to marketplace; Codex-compat constraints
  apply to loom-code changes).

## Smallest End State

**Workstream A — loom-product-principles (the construction flow):**

- `product-principles/SKILL.md`: elicitation core (Steps 2-5) REPLACED by
  the construction flow per instrument v0.1 (`docs/loom/dogfood/
  2026-07-10-designer-pm-loop-paper/instrument-v0.1.md`): Product
  question set Q1-Q8 (incl. Q4 "replaces X" capability enumeration, Q8
  lifecycle/scale), Design expert lane (two lenses: interaction +
  visual), Engineering 5 stance mini-briefings + tech-stack
  declaration slot (derivation-for-confirmation pattern), cross-section
  answer propagation, propose-then-react on stalls, per-section + final
  total read-back. Output contract retained: North Star + 3-7 falsifiable
  `— check:` principles + optional Design/Engineering sections.
- New PRINCIPLES.md sections: `## Anchors` (version-pinned canon table)
  and `## Deviation Ledger` (base-canon deviations, each bound to a
  principle). Same record shape as engineering decision log (one format,
  two views — architecture doc §5 merge 2).
- `references/` (flat): 4 canon base lists (content from
  `docs/loom/research/2026-07-10-principles-canon-base-lists.md` —
  name + fits-when + stability + source only, agent-facing, "including
  but not limited to" header, popularity-head note per list) + the
  question sets. SKILL.md body stays ≤6k tokens by pointing.
- `validate_principles_output.py`: enforce-when-present for the two new
  sections (structure checks fire only if the heading exists; required
  set unchanged — existing PRINCIPLES.md files stay valid).
- Tests: retain the pinned tokens (test_product_principles_skill.py
  L113-205); add pins for the new flow elements + validator matrix rows.

**Workstream B — loom-code (hardening):**

1. **writing-plans must-consume with layered detection** (replaces the
   "optional alternate input" framing at L192-208): (i) branch-slug match
   against `docs/loom/<change-id>/` — OPPORTUNISTIC only: exact slug
   match, no fuzzy inference; miss → silent fall-through; when this layer
   decides, the binding is stated explicitly ("bound to `<change-id>` via
   branch name"); any ambiguity → the ask layer, never a silent pick
   (spec-kit's sole-truth binding is the documented anti-pattern; Jira /
   GitHub / GitLab's opportunistic binding is the at-scale precedent).
   (ii) count non-archived change-folders — 0 → N/A-loud ("no
   change-folder; proceeding on brief"), 1 → auto-bind + state it,
   >1 → ask once, sorted by recency, most-recent flagged recommended.
   NEVER select by content similarity. Consumption becomes
   mandatory-when-bound. Reversal trigger: one real wrong-bind incident →
   downgrade layer (i) to confirm-before-use.
2. **Archive-on-close**: finishing-a-development-branch gains a step —
   when the branch consumed a change-folder and its scenarios shipped, a
   deterministic SCRIPT (not a manual `mv`; OpenSpec's archive-path bug
   #412 is the move approach's known risk class, so the script gets
   tests) moves the folder to `docs/loom/archive/<date>-<change-id>/`.
   Pool-shrinking is the industry-uniform stale-guard; in-place metadata
   alone rots without a purpose-built reader contract (Rust RFC
   postmortem), and our consumer is a naive glob. A lightweight status
   field rides in the change-folder for the pre-archive window +
   in-archive provenance — the glob never depends on it. Tombstone stub
   at the old path only if real references break (conditional, not
   built now).
3. **Coverage script**: `loom-code/scripts/check_scenario_coverage.py` —
   compare the bound change-folder's `#### Scenario:` set against the
   plan's join keys (`<change-id> / Requirement / Scenario`); name every
   dropped scenario; exit 0/1. Wired as a writing-plans self-check +
   pytest suite. (Mechanical substitute for the code review this persona
   never does.)
4. **code-reviewer principles-existence derivation**: the reviewer checks
   the target repo for `docs/loom/PRINCIPLES.md` itself (filesystem
   derivation); orchestrator-passed path becomes an override, not the
   activation condition.

**Ship gate for A**: cold-operator dogfood (operator ≠ instrument author —
fresh context, ideally weaker model) runs the shipped skill on one real
product idea before version release. B has no such gate (mechanical,
test-covered).

## Current State Evidence

- **Forward**: user idea → single-ask elicit
  (`loom-product-principles/skills/product-principles/SKILL.md:62-67`) →
  author sections (`:69-146`) → emit `docs/loom/PRINCIPLES.md` (`:148-153`)
  → validator gate (`:156-165`).
- **Reverse (SSOT)**: `references/principles-rules.md:47-255` owns the
  format rules incl. the load-bearing `— check:` falsifiability rule
  (`:97-125`) and the validator-contract summary (`:212-255`) mirrored by
  `validate_principles_output.py:191-197`; on-ramp criteria table SSOT is
  `loom-pipeline/hooks/family-reception.md` (pointed, never copied).
- **Error**: `validate_principles_output.py` exits 1 with agent-actionable
  stderr (checks at `:99-188`); `validate_spec_output.py` CLI = dir arg,
  exit 0/1 (docstring L25-28); writing-plans trusts only exit-0 folders
  (`loom-code/skills/writing-plans/SKILL.md:194-196`). No detection
  failure mode exists today because no detection exists.
- **Data**: PRINCIPLES.md = North Star + Product Principles (required) +
  Design/Engineering (optional); unknown `##` sections pass the validator
  unvalidated today (allow-list architecture, `:191-197`) — new sections
  are additive-safe but unenforced. Change-folder =
  `docs/loom/<change-id>/proposal.md + specs/<capability>/spec.md`;
  `#### Scenario:` regex at `validate_spec_output.py:249-252`.
- **Boundary**: tests pin SKILL.md tokens
  (`test_product_principles_skill.py:113-205` — `— check:`, "3"/"7",
  jurisdiction headings, `docs/loom/PRINCIPLES.md`, key-free/headless
  claims); `test_validate_principles_output.py:122-420` pins the validator
  matrix; entry-skill contract test forbids `north star`/`產品原則`/`憲章`
  in the router description (`test_principles_entry_skill.py:104-109`);
  code-reviewer principles dimension currently orchestrator-gated
  (`loom-code/agents/code-reviewer.md:403-417`); writing-plans consumes by
  handed path only (`SKILL.md:192-208, 214`).

Evidence paths: loom-product-principles/skills/product-principles/SKILL.md ·
loom-product-principles/skills/product-principles/references/principles-rules.md ·
loom-product-principles/scripts/{validate_principles_output.py, test_*.py} ·
loom-code/skills/writing-plans/SKILL.md · loom-code/agents/code-reviewer.md ·
loom-spec/scripts/validate_spec_output.py ·
loom-code/skills/finishing-a-development-branch/SKILL.md

## Alternatives Considered (Axis 4 — WebSearch EN+JA, agreement across languages)

Detection design (fragile point #1 of the architecture doc):

1. **Branch↔folder binding** (GitHub spec-kit; EN quickstart + JA
   azukiazusa.dev) — zero-memory, zero false-fire; breaks when one branch
   spans several changes. Adopted as cascade step (i), demoted to
   confirmable.
2. **Named-arg + list-non-archived + ask-on-tie** (OpenSpec CLI docs; JA
   NEXTSCAPE, SIOS) — never guesses on ambiguity; depends on archive
   discipline. Adopted as cascade steps (ii)-(iii) + archive-on-close.
3. **User-picks-per-turn** (AWS Kiro `#spec`; JA note.com) — zero misfire
   but exactly the "user must remember" burden we're removing. Rejected
   as the primary path; survives as the >1 ask.
4. **Embedded file backlinks** (Tessl) — answers "which spec produced this
   file", not "which change governs this task". Rejected (wrong
   cardinality).

Rejected for Workstream A: shipping a NEW skill alongside the old flow
(two flows = drift; rewrite in place), and doctrine-carrying canon lists
(canon-copy liability — name+hint only, per architecture doc §4).
Validator enforcement: tolerate (drift risk) vs require (breaks existing
files) vs **enforce-when-present (chosen)**.

Two follow-up research rounds (branch↔work-item binding at scale;
lifecycle marking in PEP/Rust-RFC/KEP/ADR/TC39/Ember vs OpenSpec) are
synthesized in
`docs/loom/research/2026-07-10-change-binding-and-lifecycle-research.md`
— their conclusions are baked into Workstream B items 1-2 above.

## What Becomes Obsolete (removed in the same change)

- product-principles Step 2 single-ask elicitation prose (SKILL.md:62-67)
  — replaced by the construction flow, not appended to.
- writing-plans "second input contract / instead of a brief" optional
  framing (SKILL.md:192-208) — replaced by detection + mandatory-when-bound.
- The BACKLOG COMMITTED-NEXT entry — deleted at ship (BACKLOG convention:
  completed items are deleted, git history is the archive).
- NOT obsolete: `instrument-v0.1.md` in the dogfood folder stays as the
  run record; the shipped skill becomes the living home of the flow.

## Decision

Build Workstreams A and B as **two independent branches/PRs** (different
plugins, different CI lanes; B's four items are mechanical and
parallelizable with A). A ships only after the cold-operator dogfood gate
passes. Explicitly NOT building (DEFER ledger with re-triggers lives in
architecture doc §5): 4-type question-set split, escalation-appetite
presets, reversibility-bias principle, canon version-watch, per-stack
convention library. Also not in this arc: the escalation interface /
decision-log / acceptance-surface behavioral contracts (architecture doc
§1-§2 KEEPs beyond the hardening trio) — they need loom-code behavioral
design of their own and go to BACKLOG at this arc's close.

## Out of Scope

- loom-pipeline conductor changes (segment sequence unchanged; verified
  2026-07-10 — its principles station is adopt-if-valid keyed only on
  North Star + `— check:`, unaffected by the new sections. The two
  pipeline-compat obligations land STATION-side, in scope: the
  construction flow's headless/seeded degradation mode — Segment 1
  drives the skill inside a headless Workflow agent — and the detection
  cascade's layer 0, explicit-handoff-wins)
- loom-spec / loom-interface-design / loom-discovery station changes
- Kickoff-briefing + decision-log implementation (next arc; BACKLOG entry
  to be written at close)
- Any DEFER-list item (see Decision)
- Codex-port of new loom-code behaviors beyond existing manifest-sync
  obligations

## Open Questions

1. ~~Branch-slug layer~~ RESOLVED 2026-07-10 (second research round):
   keep, opportunistic-only — exact match, silent fall-through, surfaced
   binding, ambiguity→ask. Evidence:
   `docs/loom/research/2026-07-10-change-binding-and-lifecycle-research.md`.
2. ~~Archive mechanism~~ RESOLVED 2026-07-10 (same round): folder-move by
   deterministic script + lightweight in-place status (hybrid); evidence
   ibid. REMAINING plan-time check: interaction with
   `check-living-spec-index.py` (INDEX regen must tolerate/reflect
   `docs/loom/archive/`) before the script's format freezes.
3. Version bumps + CHANGELOG entries per plugin (mechanical, decide at
   plan time).
