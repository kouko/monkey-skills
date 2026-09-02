# loom-design artifact-chain inventory

Repo root: /Users/kouko/.herdr/worktrees/monkey-skills/simple-loom-flow
Plugin: loom-design (skills/*/SKILL.md)
All line numbers are 1-indexed from `cat -n` on the file at the time of this
inventory (2026-09-02, HEAD = 923fb84a).

---

## using-loom-design
- Purpose (plain words, 1 line): family-entry router — decides which loom-design station (discovery / product-principles / interface-design / spec) an ask belongs to, then hands off; writes nothing itself.
- Entered via: user phrase "不確定從哪開始" / any design-shaped ask when unsure which skill — loom-design/skills/using-loom-design/SKILL.md:4-7 (frontmatter description)
- INPUTS (artifacts it READS):
  - `references/family-reception.md` (on-ramp table, SSOT) — loom-design/skills/using-loom-design/SKILL.md:23-25
  - `docs/loom/PRINCIPLES.md` (governs interface-design routing) — loom-design/skills/using-loom-design/SKILL.md:112-114
  - chat context only (the user's ask) — loom-design/skills/using-loom-design/SKILL.md:35-45 (routing table keyed off "the ask")
- OUTPUTS (artifacts it WRITES): none — loom-design/skills/using-loom-design/SKILL.md:222-232 ("What this router does NOT do" — never produces artifacts itself)
- CONSUMERS: N/A (router only, no artifact output)
- TERMS INTRODUCED:
  - `station — discovery / product-principles / interface-design / spec / code, the five loom-design/loom-code stopping points a request routes to` — loom-design/skills/using-loom-design/SKILL.md:35-45
  - `on-ramp — the upstream-check table deciding whether a request should be redirected to an earlier station before proceeding` — loom-design/skills/using-loom-design/SKILL.md:23-25
- MECHANISMS INVOKED: none (pure routing; delegates to member skills)
- GATES:
  - Step 1 "前站檢查" — recommends an upstream stop once, then proceeds either way (advisory, not a hard block) — loom-design/skills/using-loom-design/SKILL.md:23-33
  - Step 3 — runs `loom-workflow:brief-before-asking` before a non-trivial fork — loom-design/skills/using-loom-design/SKILL.md:50-52
  - Interface-design Stage 3 — `design-critic` gate before handing `ui-flows.md` to spec-expansion; NEEDS_REVISION repairs, no bare PASS — loom-design/skills/using-loom-design/SKILL.md:161-168

## business-value
- Purpose (plain words, 1 line): adversarial "is this worth my time" checkpoint that produces a GO/NO-GO/NEEDS-MORE-RESEARCH verdict before betting real effort.
- Entered via: `using-loom-design` §Discovery station, "worth doing?" row — loom-design/skills/using-loom-design/SKILL.md:65-67; also direct trigger phrases in its own frontmatter — loom-design/skills/business-value/SKILL.md:3
- INPUTS (artifacts it READS):
  - `assets/business-value-template.md` (shape + verdict enum) — loom-design/skills/business-value/SKILL.md:28, :111
  - `references/business-complexity-lens.md` — loom-design/skills/business-value/SKILL.md:113
  - `docs/loom/discovery/<date>-<slug>/user-insights.md`, when present, as optional evidence — loom-design/skills/business-value/SKILL.md:118-119
  - chat context only (the "seed" of the idea, elicited via interrogation) — loom-design/skills/business-value/SKILL.md:59-75
- OUTPUTS (artifacts it WRITES):
  - `docs/loom/discovery/<date>-<slug>/business-value.md` — loom-design/skills/business-value/SKILL.md:125-128
- CONSUMERS:
  - `using-loom-design` §Discovery station reads the GO/NO-GO verdict to decide whether to proceed — loom-design/skills/using-loom-design/SKILL.md:76-80 (references `business-value.md` emission but does not cite a re-read; no explicit downstream reader found beyond the human) — mark as "no automated consumer found"
- TERMS INTRODUCED:
  - `business-value.md — a short, git-diffable worth-it one-pager whose reasoning remains useful later` — loom-design/skills/business-value/SKILL.md:9-11
  - `GO / NO-GO / NEEDS-MORE-RESEARCH — the three-valued verdict enum this skill emits` — loom-design/skills/business-value/SKILL.md:94-105
- MECHANISMS INVOKED:
  - `scripts/discovery/validate_discovery_artifacts.py` — loom-design/skills/business-value/SKILL.md:129-139
- GATES:
  - Validator run, fix, retry bounded at 2 attempts; stop and surface to user after 2nd failure — loom-design/skills/business-value/SKILL.md:129-139
  - "Two or more weak axes require NEEDS-MORE-RESEARCH, never hopeful GO" — loom-design/skills/business-value/SKILL.md:104-105

## user-insights
- Purpose (plain words, 1 line): problem-space research verb — maps evidence-linked user needs (Mode 1) and, on ratification, records which needs to serve (Mode 2).
- Entered via: `using-loom-design` §Discovery station, "what do users need?" row — loom-design/skills/using-loom-design/SKILL.md:68-70
- INPUTS (artifacts it READS):
  - chat context only (the "seed" problem statement) — loom-design/skills/user-insights/SKILL.md:107-108 (Frame step)
  - Web/repo research results (via inline search or delegated `research-toolkit:deep-deep-research`) — loom-design/skills/user-insights/SKILL.md:64-71
  - `assets/user-insights-template.md`, `assets/evidence-template.md` — loom-design/skills/user-insights/SKILL.md:83-85, :134-135
- OUTPUTS (artifacts it WRITES):
  - `docs/loom/discovery/<date>-<slug>/user-insights.md` — loom-design/skills/user-insights/SKILL.md:83
  - `docs/loom/discovery/<date>-<slug>/evidence.md` — loom-design/skills/user-insights/SKILL.md:85
  - `docs/loom/discovery/<date>-<slug>/research/` (one report per research question) — loom-design/skills/user-insights/SKILL.md:84
- CONSUMERS:
  - `business-value` reads `user-insights.md` as optional evidence — loom-design/skills/business-value/SKILL.md:118-119
  - Downstream `PRINCIPLES.md` checks, interaction-flow seeding, and acceptance-criteria seeding are stated as informing later work in problem-space terms, but no specific skill is cited as reading these files directly — loom-design/skills/user-insights/SKILL.md:95-97 ("no consumer found" beyond the stated intent)
- TERMS INTRODUCED:
  - `Opportunity-space mapping (Mode 1) — knowledge-work mode; ground truth is in the world, never interrogate the user for researchable facts` — loom-design/skills/user-insights/SKILL.md:31-36
  - `Value commitment (Mode 2) — value-judgment mode; ground truth is with the user, agent recommends but writes only what the user ratifies` — loom-design/skills/user-insights/SKILL.md:47-52
  - `job story — "When …, I want …, so I can …" evidence-linked need format` — loom-design/skills/user-insights/SKILL.md:39
  - `evidence.md — claims-to-evidence registry` — loom-design/skills/user-insights/SKILL.md:85
- MECHANISMS INVOKED:
  - `scripts/discovery/validate_discovery_artifacts.py` — loom-design/skills/user-insights/SKILL.md:122-124
- GATES:
  - Validator run, fix-and-rerun bounded at 2 attempts, then stop and surface — loom-design/skills/user-insights/SKILL.md:126-130
  - §Ratify — commitment written only after "explicit affirmative user reply" — loom-design/skills/user-insights/SKILL.md:55-58

## product-principles
- Purpose (plain words, 1 line): turns a sparse product idea into a falsifiable `PRINCIPLES.md` constitution that governs every downstream design/spec/code decision.
- Entered via: `using-loom-design` §Product-principles station — loom-design/skills/using-loom-design/SKILL.md:95-103; also direct frontmatter triggers — loom-design/skills/product-principles/SKILL.md:5-9
- INPUTS (artifacts it READS):
  - `docs/loom/PURPOSE.md`, when present (read, not authored) — loom-design/skills/product-principles/SKILL.md:29-30
  - `references/principles-rules.md`, `references/question-sets.md`, `references/canon-product.md`, `references/canon-design-interaction.md`, `references/canon-design-visual.md`, `references/canon-engineering.md`, `references/knowledge-triage.md` — loom-design/skills/product-principles/SKILL.md:53, :60-63, :96-99, :157-158
  - chat context only (the "seed" idea, user-stated first) — loom-design/skills/product-principles/SKILL.md:38-43, :57-59
- OUTPUTS (artifacts it WRITES):
  - `docs/loom/PRINCIPLES.md` (project-level, one per product) — loom-design/skills/product-principles/SKILL.md:187-188
  - `seed-inventory.md` (headless/seeded mode only, write-only companion artifact) — loom-design/skills/product-principles/SKILL.md:225-230
- CONSUMERS:
  - `design-system` reads `PRINCIPLES.md` as governing constraint (§Anchors tone & manner) — loom-design/skills/design-system/SKILL.md:50-66
  - `interaction-flows` reads `PRINCIPLES.md` as governing constraint — loom-design/skills/interaction-flows/SKILL.md:20-28
  - `spec-expansion` reads `PRINCIPLES.md` as governing constraint — loom-design/skills/spec-expansion/SKILL.md:34-43
  - `design-critic` conditional PRINCIPLES lens, `completeness-critic` lens 6 — loom-design/skills/product-principles/SKILL.md:280-283
  - `loom-code:code-reviewer` scores a `principles-conformance` dimension (D8) — loom-design/skills/product-principles/SKILL.md:284-286
  - `scripts/principles/check_seed_traceability.py` reads `seed-inventory.md` + the principles file together — loom-design/skills/product-principles/SKILL.md:204-207
- TERMS INTRODUCED:
  - `PRINCIPLES.md — the supreme, always-on, key-free, git-diffable constitution governing every downstream station` — loom-design/skills/product-principles/SKILL.md:275-279
  - `Anchors — chosen base canons, version-pinned, incl. the 3-5 tone & manner adjectives` — loom-design/skills/product-principles/SKILL.md:147-148, :101-104
  - `Deviation Ledger — every canon break, with `— reason:` + `— principle:` markers` — loom-design/skills/product-principles/SKILL.md:149-151
  - `— check: marker — same-line literal marker making a principle falsifiable/artifact-bound` — loom-design/skills/product-principles/SKILL.md:54-55, :141
  - `seed-inventory.md — headless-mode write-only record of every seed-named canon/stance for traceability` — loom-design/skills/product-principles/SKILL.md:225-230
  - `(agent-decided) — literal marker tagging a choice made without a human, for later human veto` — loom-design/skills/product-principles/SKILL.md:264-268
- MECHANISMS INVOKED:
  - `scripts/principles/validate_principles_output.py` — loom-design/skills/product-principles/SKILL.md:190-198
  - `scripts/principles/check_seed_traceability.py` — loom-design/skills/product-principles/SKILL.md:204-207
- GATES:
  - "Push until falsifiable" — a statement without an artifact-falsifiable check is rejected — loom-design/skills/product-principles/SKILL.md:153-155
  - Step 6 read-back (per-section + final total) must be confirmed before proceeding — loom-design/skills/product-principles/SKILL.md:179-183
  - Step 8: both structural validator (exit 0) and seed-traceability checker (exit 0) required — loom-design/skills/product-principles/SKILL.md:190-213
  - Tripwire — thin seed in headless mode → structured BLOCKED refusal, routes to user-insights — loom-design/skills/product-principles/SKILL.md:221-224

## design-system
- Purpose (plain words, 1 line): generates the product's visual design system (colors, type, spacing, component tokens) governed by `PRINCIPLES.md`, emitting `DESIGN.md` for GUI.
- Entered via: `using-loom-design` §Interface-design station, Skill priority table stage 1 — loom-design/skills/using-loom-design/SKILL.md:151-159
- INPUTS (artifacts it READS):
  - `references/design-md-schema.md`, `references/visual-complexity-lens.md`, `references/knowledge-triage.md`, `references/canon-design-surface.md` — loom-design/skills/design-system/SKILL.md:40-48, :74-77, :132-134
  - `docs/loom/PRINCIPLES.md` (governing constraint, incl. `## Anchors` tone & manner) — loom-design/skills/design-system/SKILL.md:52-66
  - `docs/loom/PURPOSE.md` (fallback mood source when Anchors absent) — loom-design/skills/design-system/SKILL.md:59-61
  - chat context / seed for modality detection — loom-design/skills/design-system/SKILL.md:67-69
- OUTPUTS (artifacts it WRITES):
  - `docs/loom/DESIGN.md` (GUI, product-level, one per product) — loom-design/skills/design-system/SKILL.md:22-24, :172-174
  - TUI/CLI conventions stub (phase-2, same location, lightweight) — loom-design/skills/design-system/SKILL.md:156-169
- CONSUMERS:
  - `interaction-flows` / `design-critic` validator resolves `DESIGN.md` most-specific-first (change folder, then parent) when validating the change-folder — loom-design/skills/design-system/SKILL.md:186-191; loom-design/skills/interaction-flows/SKILL.md:132-139
  - `design-critic` critiques `DESIGN.md` + `ui-flows.md` together — loom-design/skills/design-critic/SKILL.md:16-18
  - "Frontend styling consumes the tokens" (human/code seam, not a loom skill) — loom-design/skills/design-system/SKILL.md:198-203
- TERMS INTRODUCED:
  - `DESIGN.md — the visual system only (brand/color/type/spacing/elevation/shape/component tokens); NOT flows/screens/navigation` — loom-design/skills/design-system/SKILL.md:20-25
  - `modality — GUI / TUI / CLI, detected/asked before generation` — loom-design/skills/design-system/SKILL.md:67-72
  - `surface treatment — the chosen depth/corner/border convention, a candidate-round decision distinct from tone & manner` — loom-design/skills/design-system/SKILL.md:125-146
- MECHANISMS INVOKED:
  - `scripts/interface/validate_design_output.py` — loom-design/skills/design-system/SKILL.md:179-185
  - `npx @google/design.md` (external lint, where available) — loom-design/skills/design-system/SKILL.md:100-101
- GATES:
  - "Ending gate" — must confirm artifact exists on disk + validator ran before ending any run — loom-design/skills/design-system/SKILL.md:18
  - WCAG-AA contrast failure is a blocker — loom-design/skills/design-system/SKILL.md:98-99, :145-146
  - If `PRINCIPLES.md` absent, proceed only on user's say-so, never invent a constitution — loom-design/skills/design-system/SKILL.md:63-65

## interaction-flows
- Purpose (plain words, 1 line): generates the per-change `ui-flows.md` interface-surface artifact (inventory, flows, layout, transitions, entry/exit, density) that seeds spec-expansion.
- Entered via: `using-loom-design` §Interface-design station, Skill priority table stage 2 — loom-design/skills/using-loom-design/SKILL.md:151-159
- INPUTS (artifacts it READS):
  - `references/ux-flow-checklist.md`, `references/ascii-ui-patterns.md`, `references/knowledge-triage.md`, `references/interaction-complexity-lens.md` — loom-design/skills/interaction-flows/SKILL.md:36-39, :81-84, :78-79
  - `docs/loom/PRINCIPLES.md` (governing constraint) — loom-design/skills/interaction-flows/SKILL.md:20-28, :41-44
  - chat context / seed (feature description) — loom-design/skills/interaction-flows/SKILL.md:53-54
- OUTPUTS (artifacts it WRITES):
  - `docs/loom/<change-id>/ui-flows.md` (per feature/change) — loom-design/skills/interaction-flows/SKILL.md:93-103
- CONSUMERS:
  - `design-critic` critiques it together with `DESIGN.md` — loom-design/skills/design-critic/SKILL.md:16-18
  - `spec-expansion` consumes it as its "rich seed" (§Consuming a `ui-flows.md` seed), mapping its sections to Phase ①/②/③ inputs — loom-design/skills/spec-expansion/SKILL.md:45-59; loom-design/skills/interaction-flows/SKILL.md:108-121
  - `scripts/interface/validate_design_output.py` reads it as part of change-folder validation — loom-design/skills/interaction-flows/SKILL.md:123-139
- TERMS INTRODUCED:
  - `ui-flows.md — modality-aware interface surface: inventory, navigation, flows, layout, transitions, entry/exit, density` — loom-design/skills/interaction-flows/SKILL.md:10-12
  - `change-id — kebab-case per-feature identifier shared between ui-flows.md's folder and spec-expansion's change folder` — loom-design/skills/interaction-flows/SKILL.md:96-99
  - `flag-only rule — name a surface's empty/loading/error/success variants without authoring the transition logic` — loom-design/skills/interaction-flows/SKILL.md:86-91
  - `Complexity handoff — optional upstream-evidence section for spec-expansion, never a behavioral gate` — loom-design/skills/interaction-flows/SKILL.md:77-79
- MECHANISMS INVOKED:
  - `scripts/interface/validate_design_output.py` — loom-design/skills/interaction-flows/SKILL.md:125-130
  - `obsidian:obsidian-mermaid-visualizer` (cross-plugin) — loom-design/skills/interaction-flows/SKILL.md:63-65
- GATES:
  - "Ending gate" — confirm `ui-flows.md` exists on disk and §7 validator ran before ending any run — loom-design/skills/interaction-flows/SKILL.md:18
  - If `PRINCIPLES.md` absent, ask user to run product-principles or proceed only with explicit approval — loom-design/skills/interaction-flows/SKILL.md:26-28

## design-critic
- Purpose (plain words, 1 line): writer≠judge adversarial panel that hunts surface omissions (missing states, dead-ends, a11y gaps) in `DESIGN.md` + `ui-flows.md` before spec-expansion.
- Entered via: `using-loom-design` §Interface-design station, Skill priority table stage 3 — loom-design/skills/using-loom-design/SKILL.md:151-159, :161-168
- INPUTS (artifacts it READS):
  - `docs/loom/DESIGN.md` (product-level) — loom-design/skills/design-critic/SKILL.md:16-17
  - `docs/loom/<change-id>/ui-flows.md` (per-change) — loom-design/skills/design-critic/SKILL.md:16-17
  - `references/design-heuristics.md` (Nielsen grounding, read by each lens-critic) — loom-design/skills/design-critic/SKILL.md:64-67
  - `docs/loom/PRINCIPLES.md` (conditional 6th lens) — loom-design/skills/design-critic/SKILL.md:119-123
- OUTPUTS (artifacts it WRITES):
  - Augmented `DESIGN.md` / `ui-flows.md` in place, tagged `critic-found` — loom-design/skills/design-critic/SKILL.md:160-166
  - `## Blind spots — needs human/field input` section (non-empty, appended) — loom-design/skills/design-critic/SKILL.md:167, :182-185
  - Minted verdict file (via mint script) — loom-design/skills/design-critic/SKILL.md:213-216
- CONSUMERS:
  - `spec-expansion` requires this verdict be minted and matching before consuming `ui-flows.md` (validate step, exit codes 2/3/4) — loom-design/skills/spec-expansion/SKILL.md:61-79
  - `using-loom-design` routes NEEDS_REVISION back to design-system/interaction-flows, PASS_WITH_NOTES onward to spec-expansion — loom-design/skills/using-loom-design/SKILL.md:166-168
- TERMS INTRODUCED:
  - `writer≠judge panel — one fresh-context general reasoning agent per lens, blind to each other, decorrelating failures` — loom-design/skills/design-critic/SKILL.md:28-33, :58-62
  - `critic-found — provenance tag for panel-added states/exits/error-screen stubs` — loom-design/skills/design-critic/SKILL.md:165
  - `loop-until-dry / K=2 — stop condition: 2 consecutive rounds with no new gap` — loom-design/skills/design-critic/SKILL.md:80-99
  - `Fixed Nielsen lenses (5, +1 conditional) — render-state, dead-end/exit, navigation reachability, error prevention/recovery, modality fit; + principles` — loom-design/skills/design-critic/SKILL.md:101-123
  - `NEEDS_REVISION / PASS_WITH_NOTES — two-valued verdict enum, no bare PASS` — loom-design/skills/design-critic/SKILL.md:201-216
- MECHANISMS INVOKED:
  - `scripts/interface/validate_design_output.py` — loom-design/skills/design-critic/SKILL.md:168-169
  - `scripts/interface/mint_critic_verdict.py` — loom-design/skills/design-critic/SKILL.md:213-216
- GATES:
  - Mechanical pre-check for schema violations (out-of-enum `evidence_needed`, tier discipline) — loom-design/skills/design-critic/SKILL.md:35-56
  - Writer↔critic cycle capped at 2; 2nd consecutive NEEDS_REVISION stops and hands back to user — loom-design/skills/design-critic/SKILL.md:203-208
  - No bare PASS; Blind spots section mandatory non-empty — loom-design/skills/design-critic/SKILL.md:182-185, :213-214

## spec-expansion
- Purpose (plain words, 1 line): GENERATE-layer skill turning a sparse seed (or `ui-flows.md`) into a high-recall OpenSpec-shape spec draft (objects/states/paths/edge cases → acceptance criteria).
- Entered via: `using-loom-design` §Spec station, "draft/expand a spec from a seed" row — loom-design/skills/using-loom-design/SKILL.md:185-187
- INPUTS (artifacts it READS):
  - chat context only / a sparse seed (a few lines of feature intent) — loom-design/skills/spec-expansion/SKILL.md:10-11
  - `docs/loom/<change-id>/ui-flows.md`, when the seed is a design output — loom-design/skills/spec-expansion/SKILL.md:45-51
  - `docs/loom/PRINCIPLES.md` (governing constraint) — loom-design/skills/spec-expansion/SKILL.md:34-43
  - `docs/loom/spec/MODEL.md` + `docs/loom/spec/<capability>/README.md` (persisted intent layer, when present) — loom-design/skills/spec-expansion/SKILL.md:80-86, :390-394
  - design-critic verdict file, validated via `mint_critic_verdict.py validate` — loom-design/skills/spec-expansion/SKILL.md:61-79
  - `references/execution-details.md`, `references/domain-tag-triage.md`, `references/behavioral-complexity-lens.md`, `references/design-panel-dispatch.md`, `references/requirement-identifiers.md`, `references/intent-layer.md`, `references/adjudication-view.md` — cited throughout, e.g. loom-design/skills/spec-expansion/SKILL.md:50-51, :153, :172-174, :227, :302, :394
- OUTPUTS (artifacts it WRITES):
  - `docs/loom/<change-id>/proposal.md` (7 sections: USM backbone, OOUX object model, Path×edge matrix, Cross-object combinations, Journey navigation, Provenance, Blind spots) — loom-design/skills/spec-expansion/SKILL.md:274-278, :315-352
  - `docs/loom/<change-id>/specs/<capability>/spec.md` (OpenSpec-pure delta, `### Requirement: REQ-<n>` / `#### Scenario:`) — loom-design/skills/spec-expansion/SKILL.md:277-296
  - `docs/loom/spec/MODEL.md` + `docs/loom/spec/<capability>/README.md` (persistent intent layer, when authoring/extending) — loom-design/skills/spec-expansion/SKILL.md:388-394
- CONSUMERS:
  - `completeness-critic` reads the whole `proposal.md` + `specs/` directory as its critique target — loom-design/skills/completeness-critic/SKILL.md:10-12
  - `loom-code:writing-plans` reads emitted `#### Scenario:` criteria and turns each into a RED/GREEN task — loom-design/skills/spec-expansion/SKILL.md:304-306, :438-441
  - `scripts/spec/validate_spec_output.py` reads the output directory — loom-design/skills/spec-expansion/SKILL.md:367-369
- TERMS INTRODUCED:
  - `GENERATE / DECLARE / VERIFY — the three-stage pipeline this skill sits in (GENERATE layer)` — loom-design/skills/spec-expansion/SKILL.md:15-17
  - `proposal.md — additive richness / narrative layer of the hybrid output` — loom-design/skills/spec-expansion/SKILL.md:274-278, :315-317
  - `specs/<capability>/spec.md — OpenSpec-pure delta, load-bearing contract joint to VERIFY` — loom-design/skills/spec-expansion/SKILL.md:280-284
  - `REQ-<n> — <name> — optional requirement identifier, id-mode once one id is used` — loom-design/skills/spec-expansion/SKILL.md:289-302
  - `provenance tags: seeded / inferred / critic-found` — loom-design/skills/spec-expansion/SKILL.md:249-261
  - `USM backbone / OOUX object model / Path×edge matrix / Cross-object combinations / Journey navigation — the five per-phase proposal.md artifacts` — loom-design/skills/spec-expansion/SKILL.md:102-246, :323-346
  - `requirement status [active|deferred] — intent-status suffix on a Requirement heading` — loom-design/skills/spec-expansion/SKILL.md:403-421
  - `persistent intent layer — durable spec root outliving one change (TOP MODEL.md + MID README.md)` — loom-design/skills/spec-expansion/SKILL.md:390-394
  - `change-id — kebab-case id shared with interaction-flows' change folder` — loom-design/skills/spec-expansion/SKILL.md:265-272
- MECHANISMS INVOKED:
  - `scripts/spec/mint_critic_verdict.py` (validate + mint) — loom-design/skills/spec-expansion/SKILL.md:61-69
  - `scripts/spec/pairwise.py` — loom-design/skills/spec-expansion/SKILL.md:227
  - `scripts/spec/validate_spec_output.py` — loom-design/skills/spec-expansion/SKILL.md:367-369
  - `scripts/validate_intent_layer.py` (referenced via `_TOP_SECTIONS`) — loom-design/skills/spec-expansion/SKILL.md:396-398
- GATES:
  - Seed-adequacy pre-flight (Phase ① gate) — stop before fan-out if too few actors/objects or lifecycle unstated — loom-design/skills/spec-expansion/SKILL.md:106-118
  - design-critic verdict validation exit codes 2/3/4 gate consuming a `ui-flows.md` seed — loom-design/skills/spec-expansion/SKILL.md:61-79
  - "Ban the word complete" — never claim complete/comprehensive/exhaustive coverage — loom-design/skills/spec-expansion/SKILL.md:31-32
  - Gate rule before VERIFY-ready: unresolved SHAPING-class `evidence_needed: domain-convention` tags block unless `deferred:` — loom-design/skills/spec-expansion/SKILL.md:354-358
  - Validator must pass before handoff — loom-design/skills/spec-expansion/SKILL.md:367-369

## completeness-critic
- Purpose (plain words, 1 line): writer≠judge multi-lens panel that adversarially hunts OMISSIONS (missing objects/actors/states/NFRs) in a spec-expansion draft before VERIFY.
- Entered via: `using-loom-design` §Spec station, "critique/audit an EXISTING draft for omissions" row — loom-design/skills/using-loom-design/SKILL.md:188-190
- INPUTS (artifacts it READS):
  - `docs/loom/<change-id>/proposal.md` + `specs/<capability>/spec.md` (the spec-expansion output) — loom-design/skills/completeness-critic/SKILL.md:10-12
  - `docs/loom/PRINCIPLES.md` + `docs/loom/PURPOSE.md` (conditional lens 6 input) — loom-design/skills/completeness-critic/SKILL.md:188-190
  - `references/consistency-lens.md` (cross-layer consistency check) — loom-design/skills/completeness-critic/SKILL.md:267-269
- OUTPUTS (artifacts it WRITES):
  - Augmented `proposal.md` / `specs/` in place: extended `## Blind spots`, `## Provenance` (`critic-found` tags), candidate `#### Scenario:` items — loom-design/skills/completeness-critic/SKILL.md:311-330
  - Minted verdict file (via mint script) — loom-design/skills/completeness-critic/SKILL.md:371
- CONSUMERS:
  - "Resolution: hand to human review → loom-code VERIFY" — loom-design/skills/completeness-critic/SKILL.md:369 (no specific skill named as automated reader beyond loom-code's VERIFY layer / `writing-plans`, which reads the underlying `#### Scenario:` items it augmented)
- TERMS INTRODUCED:
  - `writer≠judge — the critic is a fresh-context evaluator, never the draft's own author` — loom-design/skills/completeness-critic/SKILL.md:18-22
  - `loop-until-dry / K=2 (same term as design-critic, redefined locally for spec omissions)` — loom-design/skills/completeness-critic/SKILL.md:41-76
  - `six lenses: NFR/security, policy/legal/permissions, missing object/actor, state completeness, cross-object & system-layer failures, principles-entailed omission (conditional)` — loom-design/skills/completeness-critic/SKILL.md:150-210
  - `overlap-rate diagnostic — qualitative panel-diversity judgment (high >70% = redundant, low 20-40% = diverse)` — loom-design/skills/completeness-critic/SKILL.md:118-138
  - `NEEDS_REVISION / PASS_WITH_NOTES — two-valued verdict enum, no bare PASS (shared vocabulary with design-critic)` — loom-design/skills/completeness-critic/SKILL.md:352-381
- MECHANISMS INVOKED:
  - `scripts/spec/validate_spec_output.py` — loom-design/skills/completeness-critic/SKILL.md:360
  - `scripts/spec/mint_critic_verdict.py` (mint + validate) — loom-design/skills/completeness-critic/SKILL.md:371, :377-379
- GATES:
  - Ban claiming "complete" and ban completeness percentage / capture-recapture estimate — loom-design/skills/completeness-critic/SKILL.md:230-256
  - Blind spots section mandatory non-empty (Rule 12 "Fail loud") — loom-design/skills/completeness-critic/SKILL.md:212-224
  - Writer↔critic revision cycle capped at 2; 2nd consecutive NEEDS_REVISION stops, hands back to user — loom-design/skills/completeness-critic/SKILL.md:358-366
  - No bare PASS in the verdict enum — loom-design/skills/completeness-critic/SKILL.md:381-384

## using-loom-pipeline
- Purpose (plain words, 1 line): thin conductor that drives the principles→design→spec→code pipeline end-to-end via Claude Code Workflow segments; never authors artifacts or verdicts itself.
- Entered via: user phrase "run the loom pipeline" / "全管線" — loom-design/skills/using-loom-pipeline/SKILL.md:4-11 (CONDITIONAL on Workflow tool + both station plugins installed)
- INPUTS (artifacts it READS):
  - `docs/loom/QUEUE.toml` (batch mode, human-authored intent) — loom-design/skills/using-loom-pipeline/SKILL.md:130-141
  - `docs/loom/queue-state.json` (batch mode, machine state, via `batch_queue.py`) — loom-design/skills/using-loom-pipeline/SKILL.md:144-146
  - `docs/loom/<change-id>/` change folder + loom-design validator (freeze predicate check) — loom-design/skills/using-loom-pipeline/SKILL.md:150-153
  - `docs/loom/plans/<date>-<slug>.md` (Brief+plan freeze form, checks for "Plan-document-reviewer verdict: PASS") — loom-design/skills/using-loom-pipeline/SKILL.md:153, :137
  - `../using-loom-design/references/family-reception.md` (on-ramp check) — loom-design/skills/using-loom-pipeline/SKILL.md:28
  - `assets/loom-pipeline.js` (the Workflow driver script itself) — loom-design/skills/using-loom-pipeline/SKILL.md:58-72
- OUTPUTS (artifacts it WRITES):
  - `docs/loom/<changeId>/pipeline-ledger.md` (one per completed batch change) — loom-design/skills/using-loom-pipeline/SKILL.md:245-247
  - `loom/<id>` PR-ready branches — loom-design/skills/using-loom-pipeline/SKILL.md:245-247
  - Delegates writing of all station artifacts (PRINCIPLES.md, DESIGN.md, ui-flows.md, proposal.md, specs/) to the driven station skills; the driver itself "never edits station artifacts" — loom-design/skills/using-loom-pipeline/SKILL.md:113-119
- CONSUMERS:
  - `docs/loom/<changeId>/pipeline-ledger.md` — read by a fresh session's `batch_queue.py status` report and by the human at merge time — loom-design/skills/using-loom-pipeline/SKILL.md:244-251
- TERMS INTRODUCED:
  - `segment — one of 3 Workflow calls (Principles+Design / Spec / Code)` — loom-design/skills/using-loom-pipeline/SKILL.md:75-93
  - `human gate — one of 4 stop-and-wait points (change-id minting, product forks, cost policy, final merge)` — loom-design/skills/using-loom-pipeline/SKILL.md:95-111
  - `batch mode — frozen-decision unattended sequential queue over Segment 3` — loom-design/skills/using-loom-pipeline/SKILL.md:123-127
  - `freeze predicate — change-folder form or brief+plan form, the two ways a queued change becomes eligible to run` — loom-design/skills/using-loom-pipeline/SKILL.md:148-163
  - `circuit-breaker HALT — next exits 3 after 2 consecutive FAILED entries` — loom-design/skills/using-loom-pipeline/SKILL.md:240
  - `SUSPECT / SUSPECT-COMPLETE / AUTO-FAILED — reconcile's informational/mutating flags for stale RUNNING entries` — loom-design/skills/using-loom-pipeline/SKILL.md:220-225
- MECHANISMS INVOKED:
  - `assets/loom-pipeline.js` (Workflow driver script) — loom-design/skills/using-loom-pipeline/SKILL.md:58-72
  - `scripts/pipeline/batch_queue.py` (next / mark-running / mark / reconcile / reset / force-fail / status) — loom-design/skills/using-loom-pipeline/SKILL.md:188-244
  - `scripts/pipeline/argv_exec.py` (base64-JSON argv bridge for Bash-string-only hosts) — loom-design/skills/using-loom-pipeline/SKILL.md:176
- GATES:
  - §When it fires — BOTH Workflow-available AND both plugins-installed, else `loom-design: N/A` and stop — loom-design/skills/using-loom-pipeline/SKILL.md:32-41
  - 4 human gates (change-id minting, product forks, cost policy, final merge) — loom-design/skills/using-loom-pipeline/SKILL.md:95-111
  - Freeze predicate hard-reject (no fallback) — loom-design/skills/using-loom-pipeline/SKILL.md:150-163
  - circuit-breaker HALT after 2 consecutive FAILED entries, requires `--override-halt` + human review — loom-design/skills/using-loom-pipeline/SKILL.md:240

---

## Totals

**Distinct artifact types written by this plugin** (canonical path pattern):
1. `docs/loom/discovery/<date>-<slug>/business-value.md` — business-value
2. `docs/loom/discovery/<date>-<slug>/user-insights.md` — user-insights
3. `docs/loom/discovery/<date>-<slug>/evidence.md` — user-insights
4. `docs/loom/discovery/<date>-<slug>/research/*` — user-insights
5. `docs/loom/PRINCIPLES.md` — product-principles
6. `seed-inventory.md` (headless mode only) — product-principles
7. `docs/loom/DESIGN.md` — design-system
8. `docs/loom/<change-id>/ui-flows.md` — interaction-flows
9. `docs/loom/DESIGN.md` / `ui-flows.md` augmented (`critic-found` additions + `## Blind spots`) — design-critic (same files as #7/#8, in-place edit, not a new type)
10. `docs/loom/<change-id>/proposal.md` — spec-expansion
11. `docs/loom/<change-id>/specs/<capability>/spec.md` — spec-expansion
12. `docs/loom/spec/MODEL.md` + `docs/loom/spec/<capability>/README.md` (persistent intent layer) — spec-expansion
13. `proposal.md` / `specs/*.md` augmented (`critic-found` Provenance + Blind spots + candidate Scenarios) — completeness-critic (same files as #10/#11, in-place edit)
14. `docs/loom/<changeId>/pipeline-ledger.md` — using-loom-pipeline
15. `docs/loom/QUEUE.toml` (human-authored, not agent-written) / `docs/loom/queue-state.json` (machine-owned by `batch_queue.py`) — using-loom-pipeline batch mode

Net distinct **new** file-shapes (excluding in-place augmentation of an
existing type and the human-authored QUEUE.toml): **11**
(business-value.md, user-insights.md, evidence.md, research/*, PRINCIPLES.md,
seed-inventory.md, DESIGN.md, ui-flows.md, proposal.md, spec.md,
MODEL.md/README.md intent-layer pair, pipeline-ledger.md, queue-state.json
— 13 counting the intent-layer pair and queue-state.json separately).

**Distinct terms introduced** (deduplicated):
station, on-ramp, business-value.md, GO/NO-GO/NEEDS-MORE-RESEARCH,
Opportunity-space mapping (Mode 1), Value commitment (Mode 2), job story,
evidence.md, PRINCIPLES.md, Anchors, Deviation Ledger, `— check:` marker,
seed-inventory.md, `(agent-decided)`, DESIGN.md, modality, surface treatment,
ui-flows.md, change-id, flag-only rule, Complexity handoff, writer≠judge
panel, critic-found, loop-until-dry/K=2, Fixed Nielsen lenses,
NEEDS_REVISION/PASS_WITH_NOTES, GENERATE/DECLARE/VERIFY, proposal.md,
specs/<capability>/spec.md, REQ-<n>, provenance tags (seeded/inferred/
critic-found), USM backbone, OOUX object model, Path×edge matrix,
Cross-object combinations, Journey navigation, requirement status
[active|deferred], persistent intent layer, six lenses (completeness-critic),
overlap-rate diagnostic, segment, human gate, batch mode, freeze predicate,
circuit-breaker HALT, SUSPECT/SUSPECT-COMPLETE/AUTO-FAILED.
**Count: 44 distinct named terms.**

**Skills whose output has no consumer found:**
- `business-value` — `business-value.md` is read only as *optional evidence* by
  nothing found reading it automatically downstream except the human/next
  `using-loom-design` session (loom-design/skills/business-value/SKILL.md:125-128 write;
  no automated read-back site found in this plugin).
- `user-insights` — `user-insights.md` / `evidence.md` / `research/*` are
  consumed only as optional evidence by `business-value`
  (loom-design/skills/business-value/SKILL.md:118-119); the stated downstream
  informing of `PRINCIPLES.md`, interaction-flows seeding, and acceptance
  criteria (loom-design/skills/user-insights/SKILL.md:95-97) names no skill
  that actually re-reads these files.
- `completeness-critic` — its write-back augments spec-expansion's own files
  (`proposal.md`/`specs/`), and its verdict's stated consumer is "human
  review → loom-code VERIFY" (loom-design/skills/completeness-critic/SKILL.md:369)
  with no specific skill file named as an automated reader of the verdict
  (unlike spec-expansion, which explicitly validates design-critic's verdict
  file before consuming `ui-flows.md`).
</content>
