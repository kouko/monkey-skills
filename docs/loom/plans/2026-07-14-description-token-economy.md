# Plan: Description token-economy — Pocock rules port + standard reconciliation + loom-* sweep

Source brief: docs/loom/specs/2026-07-14-description-token-economy.md
Total tasks: 14
Critical-path depth: 4 (≤5)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-14, round 2 — round-1 NEEDS_REVISION on Check 13 codex-manifest oracle + Check 14 Task-9 report-only, both fixed and verified)

## Notes

- **Change-folder binding: N/A, loudly.** One non-archived change-folder exists
  (`docs/loom/2026-07-12-us-sec-primary-source-layer/`) but it belongs to the
  investing-toolkit memo-wiring arc; this plan's input is the explicitly-handed
  brainstorming brief (Layer 0 explicit handoff wins — detection never ran).
- **Kickoff decision: two-tier numbers** → normal skills target ≤150 chars with
  250 as SOFT lint line (not hard cap); router/CONDITIONAL skills exception band
  ≤500 REQUIRING a firing-evidence note. User-approved (option b), calibrated by
  2026-07-14 industry measurement (medians 106/156/304/339, n=88; CC 250 cap
  rescinded v2.1.105). Tasks transcribe these numbers VERBATIM from this pin.
- **Kickoff decision: A/B method** → `loom-code/scripts/loom_firing_harness.py`
  headless: `validate_corpus` on corpus edits; `run` mode with ≥4 turns floor on
  the direct-ask subset covering swept skills; `filter_contaminated` before
  grading; `grade` mode EXACT/FAMILY. Acceptance bar: no swept skill's
  EXACT+FAMILY combined rate drops below its baseline. Regression → revert that
  one description, record in results, ship the rest.
- **Kickoff decision: version bumps** → skill-dev-toolkit 0.2.1→0.3.0 (new
  method content); domain-teams 5.7.1→5.8.0 (gate semantics change); swept loom
  plugins PATCH bump each (description-only content, precedent PR #506 =
  research-toolkit 0.3.1). Implementers verify current versions before bumping.
- **Gotcha (standing)**: Write tool refuses basenames `report.md` — dogfood
  artifacts use another basename then `mv`. Codex-eligible plugins: after any
  plugin.json bump run `python3 scripts/sync_codex_manifests.py <plugin>`.
- Dogfood artifact directory for this arc:
  `docs/skill-dogfood/2026-07-14-description-token-economy/`.
- Amendment (2026-07-14, post-T1 review): Task 3 gains the drift-guard test
  file in Files touched + guard-update obligations (T1 quality-review 🟡:
  substring-only assertions are vacuous for two-tier semantics; and the
  literal '250'/'150' assertions conflict with T3's number removal by
  design). Additive and schema-safe (fields/DAG unchanged; T3 stays
  Independent: true — no other task touches that test file) — re-review
  skipped per writing-plans amendment rule.
- Amendment (2026-07-14, T5 implementer): Task 5 RED overclaimed — direct-ask
  line 7 pre-existed expecting loom-pipeline:using-loom-pipeline (untouched);
  GREEN criteria unaffected, both reviewers confirmed.
- Amendment (2026-07-14, T8 execution-surface discovery): Task 8 becomes a
  POST-MERGE gate. The harness probes bare `claude -p` sessions, whose skill
  descriptions come from the installed plugin cache; the monkey-skills
  marketplace source is github:kouko/monkey-skills (NOT the local path), so
  `plugin update` cannot deploy a feature branch — pre-merge B-leg would
  re-probe the old cache (false no-regression). Execution: after merge +
  device `plugin update`, run the identical pinned method (18-record
  subset, ≥4 turns, filter_contaminated, grade) and compare vs the
  committed baseline; bar unchanged (zero MISS/OVER); a regression reverts
  that one description via follow-up PR. Static guard already applied
  pre-merge: per-record corpus-intent preservation verified by both
  reviewers for every swept skill. Plan-authoring error acknowledged: the
  original T8 assumed working-tree visibility.
- Amendment (2026-07-14, T8 EXECUTED post-merge): B-leg ran at main
  47bc1316 against the deployed 0.1.1/0.7.1/0.30.2/0.9.1 cache — 11
  EXACT / 5 FAMILY / 2 MISS / 0 OVER. Bar verdict FAIL on ONE skill:
  user-insights 100%→33% via sibling attraction (loom-memory's
  before-clause). Remedy (b) targeted 217-char restore cache-experimented
  and FAILED (1/3, ja record newly flipped) → pin-literal full revert
  (899 chars, byte-identical to pre-sweep) shipped via follow-up PR;
  loom-memory guard held 4/4 throughout. Five other swept skills: 100%
  combined preserved, ship as-is. Evidence: ab-results.md
  §remedy-experiment; durable lesson recorded in docs/loom/memory/
  sibling-attractor-makes-lexical-tuning-unstable.md.
- Amendment (2026-07-14, T4 quality-review 🔴): Task 4 Files touched gains
  domain-teams/skills/skill-team/standards/skill-md-structure.md — the
  checklist's grounding standard still stated the flat ≤250 rule (:34, :73)
  and the two files cross-reference each other; no plan task owned the
  standard (plan gap, not implementer error). Additive, schema-safe.
- Amendment (2026-07-14, post-T3 implementer CONCERN): NEW Task 11 added —
  skill-judge/SKILL.md:302-303 carries a third contradictory number copy
  ("Penalize >250; flag >150") + test_judge_has_length_cap pins those
  literals; exactly the drift class this arc eliminates. Task 11 dep = Task 3
  (same test file). Critical-path depth recomputed: 1→3→11 chains with
  3→10 unchanged; longest path now T1→T2→T7x→T8 (4) and T1→T3→T11 (3),
  header updated 13→14 tasks; depth stays ≤5. Additive, schema-safe —
  re-review skipped per writing-plans amendment rule.

## Decision Log

1. chose the strict reading for evidence-less new routers (stay in the
   normal band until a corpus/live run supplies firing evidence, then the
   ≤500 band opens) because it is the literal consequence of the pinned
   "no evidence, no exception" — cost-of-change: the day a brand-new
   router genuinely cannot fit its CONDITIONAL announcement in 250 chars,
   this choice costs one extra corpus run before shipping the longer
   description. (Source: T9 cold-reader MISREAD-1 ambiguity; grader
   expectation, not rule text, was the looser side.)

2. chose YAML-comment placement for the router firing-evidence note (a
   `# firing-evidence: <date> <result> (<baseline path>)` line above
   `description:` in frontmatter) because it is greppable, colocated, and
   costs zero listing chars — cost-of-change: the day tooling wants to
   parse the note mechanically, this choice costs moving it to a real
   frontmatter field. (Principle 5 codification of placement = next-touch.)

## Task 1 — description-design.md: two-tier number reconciliation + provenance

- Description: Rewrite Principle 5 of description-design.md into the single
  number authority per the Notes pin (two-tier), add the harness facts (spec
  max 1,024; CC listing truncation 1,536 combined description+when_to_use;
  250-cap rescission provenance v2.1.86→v2.1.105), and add a dated
  supersession note to the old rationale doc pointing at the new SSOT.
- Module: skill-dev-toolkit/skills/skill-creator-advance/references/
- Files touched: skill-dev-toolkit/skills/skill-creator-advance/references/description-design.md, docs/skill-mining/2026-06-19-skill-description-standard.md
- Context paths:
  - docs/loom/specs/2026-07-14-description-token-economy.md (§Decision, §Industry grounding)
- Acceptance:
  - RED: `grep -n "ceiling at ~500\|aim for 100–250" description-design.md` hits (old contradictory wording present); `grep -c "v2.1.105" description-design.md` = 0
  - GREEN: Principle 5 states the two-tier standard verbatim from the Notes pin; rescission provenance present; rationale doc carries dated supersession note; old wording gone
- Dependencies: none
- Independent: true
- Brief item covered: "Reconcile the standard into ONE SSOT — description-design.md Principle 5 becomes the number authority" (Decision 1)

## Task 2 — description-design.md: Pocock quality rules + two-currencies framing

- Description: Add a new section porting Pocock's three quality rules (one
  trigger per branch / synonyms = duplication / cut identity already stated in
  the body) and the context-load vs cognitive-load framing, with the explicit
  carve-out that Principle 6's multilingual keyword belt (中/日 triggers) is
  NOT synonym-duplication. Cite mattpocock/skills (MIT) as source, mirroring
  writing-lean.md's attribution style.
- Module: skill-dev-toolkit/skills/skill-creator-advance/references/
- Files touched: skill-dev-toolkit/skills/skill-creator-advance/references/description-design.md
- Context paths:
  - skill-dev-toolkit/skills/skill-creator-advance/references/writing-lean.md (attribution style)
  - docs/loom/specs/2026-07-14-description-token-economy.md (§Decision 2)
- Acceptance:
  - RED: `grep -in "one trigger per branch\|synonym" description-design.md` = 0 hits
  - GREEN: new section present with all three rules + framing + multilingual carve-out + attribution
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "Port Pocock's quality rules … into description-design.md" (Decision 2)

## Task 3 — SCA SKILL.md body: defer numbers to SSOT (net ≤0 words)

- Description: Edit §House description standard in skill-creator-advance
  SKILL.md so the body carries NO standalone numeric caps that can drift —
  it defers to description-design.md as number authority (keep the two-tier
  shape nameable in ≤1 line). Net word delta must be ≤0 (file at 4,497/4,500).
  SAME TASK must update the drift guard
  `skill-dev-toolkit/.claude-plugin/test_skill_description_standard.py`:
  (a) its `test_creator_has_length_cap` substring assertions on literal
  '250'/'150' in SCA SKILL.md break by design when the numbers move to the
  SSOT — repoint them at the deferral line; (b) T1-review 🟡: extend the
  guard to pin the two-tier SEMANTICS in description-design.md (assert
  'soft lint line' + 'not a hard cap' + '≤150' + '≤500' + 'firing-evidence'
  co-occur) so the guard encodes the property it claims.
- Module: skill-dev-toolkit/skills/skill-creator-advance/
- Files touched: skill-dev-toolkit/skills/skill-creator-advance/SKILL.md, skill-dev-toolkit/.claude-plugin/test_skill_description_standard.py
- Context paths:
  - skill-dev-toolkit/skills/skill-creator-advance/references/description-design.md (post-Task-1 state)
- Acceptance:
  - RED: `grep -n "hard cap 250" SKILL.md` hits (body contradicts new SSOT)
  - GREEN: body defers to the SSOT with no contradicting standalone numbers; `wc -w` ≤ 4,500
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "SCA SKILL.md body + CHK-SKL-001 point at the SSOT; body edit net ≤0 words" (Decision 1)

## Task 4 — CHK-SKL-001 two-tier alignment + domain-teams bump

- Description: Update CHK-SKL-001 in the skill-completeness checklist to the
  two-tier standard (transcribe numbers verbatim from the Notes pin; keep the
  30-word floor and existing "Use when"/redirect requirements), pointing at
  description-design.md as authority. Bump domain-teams 5.7.1→5.8.0 with
  CHANGELOG entry; run `python3 scripts/sync_codex_manifests.py domain-teams`
  after the bump and stage the regenerated .codex-plugin/plugin.json.
- Module: domain-teams/
- Files touched: domain-teams/skills/skill-team/checklists/skill-completeness-checklist.md, domain-teams/skills/skill-team/standards/skill-md-structure.md, domain-teams/.claude-plugin/plugin.json, domain-teams/.codex-plugin/plugin.json, domain-teams/CHANGELOG.md
- Context paths:
  - skill-dev-toolkit/skills/skill-creator-advance/references/description-design.md (post-Task-1 state)
- Acceptance:
  - RED: checklist line 16 states flat "≤250 chars" (single-tier, conflicts with new SSOT)
  - GREEN: CHK-SKL-001 states the two-tier rule + SSOT pointer; plugin.json 5.8.0; CHANGELOG entry present
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "SCA SKILL.md body + CHK-SKL-001 point at the SSOT" (Decision 1)

## Task 5 — firing-corpus extension for uncovered stations

- Description: Add 3–5 direct-ask entries each for loom-discovery
  (using-loom-discovery, user-insights, business-value) and loom-pipeline
  (using-loom-pipeline, loom-memory) to direct-ask.jsonl, following the
  existing record schema and description-derived intent phrasing (harness
  trap #5: not transcript-mined). Validate with the harness `validate_corpus`
  mode (warnings reviewed, no failures).
- Module: docs/loom/firing-corpus/
- Files touched: docs/loom/firing-corpus/direct-ask.jsonl
- Context paths:
  - loom-code/scripts/loom_firing_harness.py (module docstring + validate_corpus)
  - docs/loom/firing-corpus/direct-ask.jsonl (existing schema examples)
- Acceptance:
  - RED: `python3 -c` scan shows zero direct-ask records expecting loom-discovery:* or loom-pipeline:* skills
  - GREEN: ≥15 new records covering the 5 skills; `validate_corpus` passes
- Dependencies: none
- Independent: true
- Brief item covered: "Uncovered top offenders … EXTEND direct-ask.jsonl with 3–5 entries each FIRST" (Decision 3)

## Task 6 — baseline firing run (pre-sweep)

- Description: Run the harness A/B method (Notes pin) over the direct-ask
  subset covering every skill Task 7a–7d will sweep, against CURRENT
  descriptions. Persist per-skill EXACT/FAMILY rates + discard counts to
  `docs/skill-dogfood/2026-07-14-description-token-economy/baseline.md`
  (write via alias basename then mv if needed).
- Module: docs/skill-dogfood/
- Files touched: docs/skill-dogfood/2026-07-14-description-token-economy/baseline.md
- Context paths:
  - loom-code/scripts/loom_firing_harness.py
  - docs/loom/firing-corpus/direct-ask.jsonl (post-Task-5 state)
- Acceptance:
  - RED: baseline.md does not exist
  - GREEN: baseline.md exists with per-skill EXACT/FAMILY table for all sweep-target skills, discard count surfaced
- Dependencies: Task 5 completes first
- Independent: false
- Brief item covered: "Corpus-covered skills: baseline run → rewrite → re-run" (Decision 3)

## Task 7a — loom-discovery description sweep + bump

- Description: Rewrite the three loom-discovery descriptions under the new
  standard (Notes pin numbers): using-loom-discovery (1,081) as router →
  exception band ≤500 with firing-evidence note; user-insights (927) and
  business-value (632) as normal skills → target ≤150, apply Pocock quality
  rules, keep load-bearing trigger words incl. multilingual belt. PATCH bump
  loom-discovery + CHANGELOG; run `python3 scripts/sync_codex_manifests.py
  loom-discovery` after the bump.
- Module: loom-discovery/
- Files touched: loom-discovery/skills/using-loom-discovery/SKILL.md, loom-discovery/skills/user-insights/SKILL.md, loom-discovery/skills/business-value/SKILL.md, loom-discovery/.claude-plugin/plugin.json, loom-discovery/.codex-plugin/plugin.json, loom-discovery/CHANGELOG.md
- Context paths:
  - skill-dev-toolkit/skills/skill-creator-advance/references/description-design.md (post-Task-2 state)
  - docs/skill-dogfood/2026-07-14-description-token-economy/baseline.md
- Acceptance:
  - RED: `awk` frontmatter-description char counts are 1,081/927/632 (over band)
  - GREEN: all three in-band per the pin; router carries evidence note; plugin bumped + CHANGELOG entry
- Dependencies: Tasks 2, 6 complete first
- Independent: true
- Brief item covered: "Sweep loom-* over-cap descriptions under the new standard" (Decision 3)

## Task 7b — loom-pipeline description sweep + bump

- Description: Rewrite using-loom-pipeline (1,049) and loom-memory (1,005) —
  both CONDITIONAL skills → exception band ≤500 with firing-evidence notes,
  preserving the CONDITIONAL/N/A-loud announcement semantics and multilingual
  triggers. PATCH bump loom-pipeline + CHANGELOG; run
  `python3 scripts/sync_codex_manifests.py loom-pipeline` after the bump.
- Module: loom-pipeline/
- Files touched: loom-pipeline/skills/using-loom-pipeline/SKILL.md, loom-pipeline/skills/loom-memory/SKILL.md, loom-pipeline/.claude-plugin/plugin.json, loom-pipeline/.codex-plugin/plugin.json, loom-pipeline/CHANGELOG.md
- Context paths:
  - skill-dev-toolkit/skills/skill-creator-advance/references/description-design.md (post-Task-2 state)
  - docs/skill-dogfood/2026-07-14-description-token-economy/baseline.md
- Acceptance:
  - RED: frontmatter-description char counts are 1,049/1,005 (over band)
  - GREEN: both ≤500 with evidence notes + CONDITIONAL semantics intact; plugin bumped + CHANGELOG entry
- Dependencies: Tasks 2, 6 complete first
- Independent: true
- Brief item covered: "Sweep loom-* over-cap descriptions under the new standard" (Decision 3)

## Task 7c — loom-code description band sweep + bump

- Description: ui-verification (582) → in-band per pin; quality-pass (Pocock
  rules only, no forced shortening) over the 250–310 band: SDD (308),
  brainstorming (305), requesting-code-review (265), dispatching-parallel-agents
  (264), verification-before-completion (263). PATCH bump loom-code
  0.30.1→0.30.2 + CHANGELOG + codex manifest sync.
- Module: loom-code/
- Files touched: loom-code/skills/ui-verification/SKILL.md, loom-code/skills/subagent-driven-development/SKILL.md, loom-code/skills/brainstorming/SKILL.md, loom-code/skills/requesting-code-review/SKILL.md, loom-code/skills/dispatching-parallel-agents/SKILL.md, loom-code/skills/verification-before-completion/SKILL.md, loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md
- Context paths:
  - skill-dev-toolkit/skills/skill-creator-advance/references/description-design.md (post-Task-2 state)
  - docs/skill-dogfood/2026-07-14-description-token-economy/baseline.md
- Acceptance:
  - RED: ui-verification description = 582 chars (over normal band, not a router)
  - GREEN: ui-verification in-band; band-skills pass quality rules with no trigger-word loss; frontmatter edits only (bodies untouched); plugin bumped + CHANGELOG entry
- Dependencies: Tasks 2, 6 complete first
- Independent: true
- Brief item covered: "Sweep loom-* over-cap descriptions under the new standard" (Decision 3)

## Task 7d — loom-product-principles description sweep + bump

- Description: product-principles (585) → normal-band rewrite per pin (this
  description carries a long trigger list incl. 中/日 — keep distinct triggers,
  cut synonyms/identity per quality rules). PATCH bump + CHANGELOG; run
  `python3 scripts/sync_codex_manifests.py loom-product-principles` after
  the bump.
- Module: loom-product-principles/
- Files touched: loom-product-principles/skills/product-principles/SKILL.md, loom-product-principles/.claude-plugin/plugin.json, loom-product-principles/.codex-plugin/plugin.json, loom-product-principles/CHANGELOG.md
- Context paths:
  - skill-dev-toolkit/skills/skill-creator-advance/references/description-design.md (post-Task-2 state)
  - docs/skill-dogfood/2026-07-14-description-token-economy/baseline.md
- Acceptance:
  - RED: product-principles description = 585 chars (over normal band)
  - GREEN: in-band per pin with multilingual triggers preserved; plugin bumped + CHANGELOG entry
- Dependencies: Tasks 2, 6 complete first
- Independent: true
- Brief item covered: "Sweep loom-* over-cap descriptions under the new standard" (Decision 3)

## Task 8 — post-sweep A/B re-run + comparison

- Description: Re-run the identical harness method (Notes pin) over the same
  direct-ask subset against the swept descriptions; write per-skill
  EXACT/FAMILY comparison vs baseline to
  `docs/skill-dogfood/2026-07-14-description-token-economy/ab-results.md`.
  Any skill whose combined EXACT+FAMILY rate drops below baseline → revert
  that one description (keep the rest), record the revert + evidence.
- Module: docs/skill-dogfood/
- Files touched: docs/skill-dogfood/2026-07-14-description-token-economy/ab-results.md, plus CONDITIONAL revert writes to any regressed skill's SKILL.md among the Task 7a–7d sweep set (frontmatter description only; fires only on a measured regression)
- Context paths:
  - docs/skill-dogfood/2026-07-14-description-token-economy/baseline.md
  - loom-code/scripts/loom_firing_harness.py
- Acceptance:
  - RED: ab-results.md does not exist
  - GREEN: comparison table exists for every swept skill; acceptance bar evaluated per skill; any revert executed + recorded
- Dependencies: Tasks 7a, 7b, 7c, 7d complete first
- Independent: false
- Brief item covered: "guarded by firing-corpus A/B … no regression" (Decision 3)

## Task 9 — cold-reader dogfood of the new rule text

- Description: Dispatch a fresh-context agent given ONLY the post-Task-2
  description-design.md and a synthetic skill spec (one normal skill + one
  router/CONDITIONAL skill); it authors both descriptions blind. Verify both
  land in-band with the quality rules applied (no synonyms, no identity
  restatement, triggers front-loaded; router carries evidence-note
  placeholder). REPORT-ONLY task: this task writes ONLY coldreader.md —
  any misread becomes a recorded finding routed back as a Task-2 revision
  dispatch (SDD NEEDS_REVISION loop), never an inline edit to
  description-design.md from this task.
- Module: docs/skill-dogfood/
- Files touched: docs/skill-dogfood/2026-07-14-description-token-economy/coldreader.md
- Context paths:
  - skill-dev-toolkit/skills/skill-creator-advance/references/description-design.md (post-Task-2 state)
- Acceptance:
  - RED: coldreader.md does not exist
  - GREEN: coldreader.md records both authored descriptions + in-band/rules verdicts; misreads (if any) recorded as findings with a routed Task-2 revision note — no writes outside coldreader.md
- Dependencies: Tasks 2, 3 complete first
- Independent: true
- Brief item covered: "Cold-reader dogfood the new rule text (quality floor)" (Decision 4)

## Task 11 — skill-judge number-copy SSOT alignment

- Description: Align skill-judge's description-length wording with the
  two-tier SSOT: skill-judge/SKILL.md ~:302-303 currently states
  "Length ≤250 chars (target ≤150…) … Penalize >250; flag >150" — rewrite to
  score against the two-tier standard (normal ≤150 target / 250 soft lint;
  router-CONDITIONAL ≤500 with firing-evidence note) with the SSOT pointer,
  keeping the judging-rubric voice. SAME TASK: repoint
  `test_judge_has_length_cap` in test_skill_description_standard.py from
  literal '250'/'150' substrings to assertions that encode the new property
  (deferral/two-tier present; no flat penalize-over-250 claim). TDD order:
  test first (RED against current skill-judge body), then edit to GREEN.
- Module: skill-dev-toolkit/skills/skill-judge/
- Files touched: skill-dev-toolkit/skills/skill-judge/SKILL.md, skill-dev-toolkit/.claude-plugin/test_skill_description_standard.py
- Context paths:
  - skill-dev-toolkit/skills/skill-creator-advance/references/description-design.md §Principle 5 (number authority)
  - docs/loom/plans/2026-07-14-description-token-economy.md (## Notes two-tier pin)
- Acceptance:
  - RED: `grep -n "Penalize >250" skill-dev-toolkit/skills/skill-judge/SKILL.md` hits; repointed test fails pre-edit
  - GREEN: skill-judge scores against the two-tier rule + SSOT pointer; guard suite passes; skill-judge SKILL.md stays within CHK-SKL-010 word cap
- Dependencies: Task 3 completes first
- Independent: true
- Brief item covered: "Reconcile the standard into ONE SSOT" (Decision 1 — third contradictory copy discovered during execution)

## Task 10 — skill-dev-toolkit bump + CHANGELOG

- Description: Bump skill-dev-toolkit 0.2.1→0.3.0; CHANGELOG entry covering
  Tasks 1–3 (two-tier standard, Pocock description rules, body deferral) with
  the industry-measurement provenance one-liner. Run
  `python3 scripts/sync_codex_manifests.py skill-dev-toolkit` after the bump
  (manifest verified present on disk).
- Module: skill-dev-toolkit/
- Files touched: skill-dev-toolkit/.claude-plugin/plugin.json, skill-dev-toolkit/.codex-plugin/plugin.json, skill-dev-toolkit/CHANGELOG.md
- Context paths:
  - skill-dev-toolkit/CHANGELOG.md (entry style)
- Acceptance:
  - RED: plugin.json = 0.2.1, no 0.3.0 CHANGELOG entry
  - GREEN: 0.3.0 in plugin.json + CHANGELOG entry present
- Dependencies: Tasks 3, 9 complete first
- Independent: false
- Brief item covered: "description-design.md = single number authority, Pocock rules folded in" (Smallest End State)
