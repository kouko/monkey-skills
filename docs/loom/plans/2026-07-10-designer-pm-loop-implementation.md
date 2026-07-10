# Plan: designer/PM loop implementation — construction flow (A) + loom-code hardening (B)

Source brief: docs/loom/specs/2026-07-10-designer-pm-loop-implementation.md
Total tasks: 14
Critical-path depth: 4 (≤5)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-10, 14/14 checks)

Notes:
- Reviewer advisories (non-fatal, acknowledged): (a) Tasks 4∥5 and 11∥12
  are file-disjoint with no edge between them — left unmarked
  `Independent: true` deliberately because each carries a declared
  dependency on an earlier `Independent: true` task; the dispatcher may
  still run them concurrently once their prerequisites are DONE
  (readiness-gated). (b) Task 6's dogfood folder date placeholder
  (2026-07-XX) is resolved by SDD at execution. (c) The "tests retained"
  brief bullet is realized inside Task 5/4 GREENs (traceability note).
- Post-PASS amendment (2026-07-10, re-review skipped — additive and
  schema-safe: no field/DAG/Module change): Task 5 gains the §Headless /
  seeded mode requirement (loom-pipeline Segment 1 drives the skill
  inside a headless Workflow agent — decision points must degrade to
  "delegate to agent" + agent-decided ledger entries); Task 9's cascade
  gains layer (0): explicitly handed path binds immediately, detection
  never runs (the conductor names the change-id). Trigger: user question
  "不需要修改 loom-pipeline 嗎" — answer: no loom-pipeline file changes;
  both fixes land station-side. Conductor compatibility verified:
  adopt-if-valid keys only on North Star + `— check:` (loom-pipeline.js
  isPrinciplesStructurallyValid), which Task 5 retains.
- Two execution clusters per the brief's Decision: Cluster A (Tasks 1-7,
  plugin loom-product-principles) and Cluster B (Tasks 8-14, plugin
  loom-code) run on SEPARATE branches / PRs. Clusters are mutually
  independent (disjoint plugins); cross-cluster ordering is free.
- Task 6 (cold-operator dogfood) is Workstream A's ship gate per the
  brief — it is a process task with a diagnostic-style RED/GREEN, not a
  code test.
- Instrument v0.1 (`docs/loom/dogfood/2026-07-10-designer-pm-loop-paper/
  instrument-v0.1.md`) is the flow spec for Tasks 2, 5; the canon
  research note (`docs/loom/research/2026-07-10-principles-canon-base-lists.md`)
  is the content source for Task 1. Copy facts (question texts, list
  entries), link rationale — per brief.

## Task 1 — canon base list reference files ×4
- Description: Create the four agent-facing canon base lists as flat
  reference files, content from the research note (name + fits-when +
  stability/version + source URL per entry; "including but not limited
  to" header; popularity-head note per list; no doctrine bodies).
- Module: loom-product-principles/skills/product-principles/references/
- Files touched: loom-product-principles/skills/product-principles/references/canon-product.md, loom-product-principles/skills/product-principles/references/canon-design-interaction.md, loom-product-principles/skills/product-principles/references/canon-design-visual.md, loom-product-principles/skills/product-principles/references/canon-engineering.md, loom-product-principles/scripts/test_canon_references.py
- Context paths:
  - docs/loom/research/2026-07-10-principles-canon-base-lists.md
  - docs/loom/design/2026-07-10-designer-pm-loop-architecture.md (§4 constraints)
- Acceptance:
  - RED: pytest loom-product-principles/scripts/test_canon_references.py fails (files absent)
  - GREEN: same passes — 4 files exist, each has the "including but not limited to" header, a popularity-head section, and ≥14 entries each carrying a URL
- Dependencies: none
- Independent: true
- Brief item covered: "`references/` (flat): 4 canon base lists … name + fits-when + stability + source only, agent-facing"

## Task 2 — question-sets reference file
- Description: Create the question-sets reference (Product Q1-Q8 incl. Q4
  "replaces X" capability-enumeration annotation and Q8 lifecycle/scale;
  Engineering 5 stance mini-briefing templates with stakes lines +
  tech-stack declaration slot with derivation-for-confirmation pattern;
  Design expert-lane instructions), content graduated from instrument
  v0.1 (facts verbatim, structure adapted to a reference file).
- Module: loom-product-principles/skills/product-principles/references/
- Files touched: loom-product-principles/skills/product-principles/references/question-sets.md, loom-product-principles/scripts/test_question_sets.py
- Context paths:
  - docs/loom/dogfood/2026-07-10-designer-pm-loop-paper/instrument-v0.1.md
- Acceptance:
  - RED: pytest loom-product-principles/scripts/test_question_sets.py fails (file absent)
  - GREEN: same passes — Q8 lifecycle/scale present, Q4 carries the "replaces X" annotation, 5 engineering stance questions with stakes, tech-stack slot names derivation-for-confirmation
- Dependencies: none
- Independent: true
- Brief item covered: "the question sets" in references/ + "Product question set Q1-Q8 … Engineering 5 stance mini-briefings + tech-stack declaration slot"

## Task 3 — principles-rules.md: Anchors + Deviation Ledger format rules
- Description: Add format rules for the two new PRINCIPLES.md sections to
  the rules SSOT: `## Anchors` (table; each row = canon name + pinned
  version/edition) and `## Deviation Ledger` (each entry = deviation +
  reason bound to a named principle). Include ✅/❌ examples per the
  file's existing style; update its Validator contract summary.
- Module: loom-product-principles/skills/product-principles/references/principles-rules.md
- Files touched: loom-product-principles/skills/product-principles/references/principles-rules.md, loom-product-principles/scripts/test_principles_rules_sections.py
- Context paths:
  - loom-product-principles/skills/product-principles/references/principles-rules.md
  - docs/loom/design/2026-07-10-designer-pm-loop-architecture.md (§3 guardrails)
- Acceptance:
  - RED: pytest loom-product-principles/scripts/test_principles_rules_sections.py fails (sections absent from rules file)
  - GREEN: same passes — rules file defines both section formats + validator-contract rows for them
- Dependencies: none
- Independent: true
- Brief item covered: "New PRINCIPLES.md sections: `## Anchors` (version-pinned canon table) and `## Deviation Ledger`"

## Task 4 — validator: enforce-when-present for Anchors + Deviation Ledger
- Description: Extend validate_principles_output.py with
  enforce-when-present checks (fire only if the heading exists; required
  set unchanged): `## Anchors` rows must carry a version/edition token;
  `## Deviation Ledger` entries must reference a principle. Existing
  PRINCIPLES.md files without the sections stay exit-0.
- Module: loom-product-principles/scripts/
- Files touched: loom-product-principles/scripts/validate_principles_output.py, loom-product-principles/scripts/test_validate_principles_output.py
- Context paths:
  - loom-product-principles/scripts/validate_principles_output.py
  - loom-product-principles/skills/product-principles/references/principles-rules.md (post-Task-3)
- Acceptance:
  - RED: new rows in test_validate_principles_output.py fail (validator ignores the sections)
  - GREEN: full test_validate_principles_output.py passes incl. matrix rows: absent sections → valid; malformed Anchors row (no version) → invalid; ledger entry without principle ref → invalid
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: "validator: enforce-when-present for the two new sections … existing PRINCIPLES.md files stay valid"

## Task 5 — product-principles SKILL.md: construction-flow rewrite
- Description: Replace the elicitation core (Steps 2-5) with the
  construction flow per instrument v0.1: user-states-first → probe via
  question-sets reference (propose-then-react on stalls; cross-section
  answer propagation) → 2-3 canon candidates with fit/tension notes
  (consult canon lists as completeness audit; ≥2 traditions; 1-2
  considered-but-rejected; user never sees raw lists) → user decides
  (mix / bespoke escape hatch) → write Anchors (version-pinned) +
  Deviation Ledger + falsifiable principles → per-section + final total
  read-back. MUST include a §Headless / seeded mode: when driven with no
  user available (loom-pipeline Segment 1 Workflow agent, batch context),
  every decision point degrades to its "delegate to agent" answer —
  agent picks canon/stances itself from the seed, records each choice in
  the Deviation Ledger / decision entries as agent-decided, and marks
  read-back as deferred-to-human; a run-input seed may pre-supply
  answers. Retain: output contract (North Star, 3-7 `— check:`
  principles, optional sections — conductor's adopt-if-valid check keys
  on these), all test-pinned tokens, ≤6k-token body (point to
  references, don't inline lists).
- Module: loom-product-principles/skills/product-principles/SKILL.md
- Files touched: loom-product-principles/skills/product-principles/SKILL.md, loom-product-principles/scripts/test_product_principles_skill.py
- Context paths:
  - loom-product-principles/skills/product-principles/SKILL.md
  - docs/loom/dogfood/2026-07-10-designer-pm-loop-paper/instrument-v0.1.md
  - docs/loom/design/2026-07-10-designer-pm-loop-architecture.md (§3-§4)
  - loom-product-principles/scripts/test_product_principles_skill.py
- Acceptance:
  - RED: new grep assertions in test_product_principles_skill.py fail on the current SKILL.md (no construction-flow elements)
  - GREEN: full test_product_principles_skill.py passes — existing token pins (L113-205 set) retained AND new pins present (propose-then-react, canon candidates double guard, deviation ledger, version pins, read-back, cross-section propagation, headless/seeded degradation mode, references/question-sets.md + 4 canon list paths)
- Dependencies: Tasks 1, 2, 3 complete first
- Independent: false
- Brief item covered: "SKILL.md: elicitation core (Steps 2-5) REPLACED by the construction flow per instrument v0.1"

## Task 6 — cold-operator dogfood (ship gate for Cluster A)
- Description: Dispatch a fresh-context operator (NOT the instrument/skill
  author; weaker model tier preferred) to run the SHIPPED skill
  (post-Task-5 SKILL.md + references) on one real product idea supplied
  by the user, end-to-end; grade against the five success criteria of the
  paper-dogfood instrument; write the run report. Any criterion failing →
  fix tasks spawn before Task 7.
- Module: docs/loom/dogfood/
- Files touched: docs/loom/dogfood/2026-07-XX-principles-flow-cold-operator/report.md
- Context paths:
  - loom-product-principles/skills/product-principles/SKILL.md (post-Task-5)
  - docs/loom/dogfood/2026-07-10-designer-pm-loop-paper/instrument-v0.1.md (success criteria table)
- Acceptance:
  - RED: report file absent
  - GREEN: report exists with all five criteria graded and an explicit ship / fix-first verdict
- Dependencies: Tasks 4, 5 complete first
- Independent: false
- Brief item covered: "Ship gate for A: cold-operator dogfood (operator ≠ instrument author — fresh context, ideally weaker model)"

## Task 7 — Cluster A version bump + CHANGELOG
- Description: Bump loom-product-principles version (minor — new flow +
  validator surface), add CHANGELOG entry, keep marketplace description
  in sync (only if description changed).
- Module: loom-product-principles/
- Files touched: loom-product-principles/.claude-plugin/plugin.json, loom-product-principles/.codex-plugin/plugin.json, loom-product-principles/CHANGELOG.md
- Context paths:
  - loom-product-principles/CHANGELOG.md
- Acceptance:
  - RED: pytest loom-product-principles/scripts/test_plugin_manifest.py after edit would fail on malformed semver / mismatched manifests (diagnostic: run before+after)
  - GREEN: manifest tests + `python scripts/check-marketplace-description-sync.py` exit 0 with new version
- Dependencies: Task 6 completes first
- Independent: false
- Brief item covered: "Version bumps + CHANGELOG entries per plugin" (Open Question 3, mechanical)

## Task 8 — archive_change_folder script
- Description: Create the deterministic archive script: moves
  `docs/loom/<change-id>/` → `docs/loom/archive/<date>-<change-id>/`,
  stamps a status field in the folder's proposal.md frontmatter, refuses
  to archive a folder that doesn't exist or is already archived, and is
  path-safe (OpenSpec #412 bug class = the test focus). Verify
  living-spec-index interaction: with an archived folder present,
  check-living-spec-index.py still exits 0 (archive/ excluded or
  tolerated — pick whichever the current scanner needs and pin it in a
  test).
- Module: loom-code/scripts/
- Files touched: loom-code/scripts/archive_change_folder.py, loom-code/scripts/test_archive_change_folder.py
- Context paths:
  - loom-code/scripts/check-living-spec-index.py
  - loom-spec/scripts/validate_spec_output.py (change-folder shape)
- Acceptance:
  - RED: pytest loom-code/scripts/test_archive_change_folder.py fails (script absent)
  - GREEN: same passes — happy-path move, refusal cases, path-safety cases, and the living-spec-index-still-green case
- Dependencies: none
- Independent: true
- Brief item covered: "a deterministic SCRIPT … moves the folder to `docs/loom/archive/<date>-<change-id>/` … lightweight status field"

## Task 9 — writing-plans: layered detection cascade
- Description: Rewrite writing-plans SKILL.md §Consuming a loom-spec
  change-folder: replace the "second input contract / instead of a brief"
  optional framing with detection + mandatory-when-bound — (0) an
  explicitly handed change-folder path (conductor / caller names it)
  binds immediately, detection never runs; (i) exact
  branch-slug match, opportunistic only (miss → silent fall-through;
  binding surfaced when it decides; ambiguity → ask layer); (ii)
  non-archived folder count 0 → N/A-loud, 1 → auto-bind + state it,
  >1 → ask once sorted by recency with recommended default; never
  content-similarity. Include the wrong-bind reversal trigger note.
- Module: loom-code/skills/writing-plans/SKILL.md
- Files touched: loom-code/skills/writing-plans/SKILL.md, loom-code/scripts/test_writing_plans_change_binding.py
- Context paths:
  - loom-code/skills/writing-plans/SKILL.md
  - docs/loom/research/2026-07-10-change-binding-and-lifecycle-research.md
  - docs/loom/specs/2026-07-10-designer-pm-loop-implementation.md (Workstream B item 1)
- Acceptance:
  - RED: pytest loom-code/scripts/test_writing_plans_change_binding.py fails (cascade absent; old "instead of a brief" framing present)
  - GREEN: same passes — cascade steps, N/A-loud line, mandatory-when-bound, no-content-similarity pin all grep-present; optional framing gone
- Dependencies: none
- Independent: true
- Brief item covered: "writing-plans must-consume with layered detection (replaces the 'optional alternate input' framing)"

## Task 10 — check_scenario_coverage script
- Description: Create the coverage script: given a change-folder path and
  a plan path, compare the folder's `#### Scenario:` set (per
  validate_spec_output.py's heading grammar) against the plan's join keys
  (`<change-id> / Requirement: <name> / Scenario: <name>`); exit 0 on
  full coverage, exit 1 naming every dropped scenario.
- Module: loom-code/scripts/
- Files touched: loom-code/scripts/check_scenario_coverage.py, loom-code/scripts/test_check_scenario_coverage.py
- Context paths:
  - loom-spec/scripts/validate_spec_output.py (Scenario regex, L249-252)
  - loom-code/skills/writing-plans/references/plan-format.md (join-key field)
- Acceptance:
  - RED: pytest loom-code/scripts/test_check_scenario_coverage.py fails (script absent)
  - GREEN: same passes — full-coverage exit 0, dropped-scenario exit 1 with the scenario named, malformed-plan handling
- Dependencies: none
- Independent: true
- Brief item covered: "Coverage script … compare the bound change-folder's `#### Scenario:` set against the plan's join keys; name every dropped scenario"

## Task 11 — finishing-a-development-branch: archive-on-close step
- Description: Add the archive-on-close step to
  finishing-a-development-branch SKILL.md: when the branch consumed a
  change-folder and its scenarios shipped, run archive_change_folder.py
  (script path + when-it-fires + N/A when no folder was bound); stage the
  move in the close-out commit.
- Module: loom-code/skills/finishing-a-development-branch/SKILL.md
- Files touched: loom-code/skills/finishing-a-development-branch/SKILL.md, loom-code/scripts/test_finishing_archive_step.py, AGENTS.md (declare archive_change_folder.py in the managed command-surface block — runnable-capability accretion the plan originally missed; amendment 2026-07-10)
- Context paths:
  - loom-code/skills/finishing-a-development-branch/SKILL.md
  - loom-code/scripts/archive_change_folder.py (post-Task-8)
- Acceptance:
  - RED: pytest loom-code/scripts/test_finishing_archive_step.py fails (no archive step in SKILL.md)
  - GREEN: same passes — step present, names the script, has the N/A-when-unbound line
- Dependencies: Task 8 completes first
- Independent: false
- Brief item covered: "Archive-on-close: finishing-a-development-branch gains a step — a deterministic SCRIPT moves the folder"

## Task 12 — writing-plans: coverage-script wiring
- Description: Add the coverage self-check to writing-plans SKILL.md
  (change-folder input path only): after producing the plan, run
  check_scenario_coverage.py; exit 1 blocks the plan from PASS until
  every scenario maps or the drop is user-approved in the plan Notes.
- Module: loom-code/skills/writing-plans/SKILL.md
- Files touched: loom-code/skills/writing-plans/SKILL.md, loom-code/scripts/test_writing_plans_change_binding.py, AGENTS.md (declare check_scenario_coverage.py in the managed command-surface block — runnable-capability accretion; amendment 2026-07-10)
- Context paths:
  - loom-code/skills/writing-plans/SKILL.md (post-Task-9)
  - loom-code/scripts/check_scenario_coverage.py (post-Task-10)
- Acceptance:
  - RED: new grep assertions in test_writing_plans_change_binding.py fail (no coverage-check wiring)
  - GREEN: full file passes — wiring present, names the script, block-on-exit-1 semantics stated
- Dependencies: Tasks 9, 10 complete first
- Independent: false
- Brief item covered: "Wired as a writing-plans self-check + pytest suite"

## Task 13 — code-reviewer: principles-existence derivation
- Description: Change code-reviewer.md's principles-conformance dimension
  activation: the reviewer derives existence by checking the target repo
  for docs/loom/PRINCIPLES.md itself; an orchestrator-passed path becomes
  an override (e.g. non-standard location), not the activation condition.
  N/A stays honest when the file is absent.
- Module: loom-code/agents/code-reviewer.md
- Files touched: loom-code/agents/code-reviewer.md, loom-code/scripts/test_code_reviewer_principles_derivation.py, loom-code/skills/requesting-code-review/SKILL.md (round-2 review-driven addition: D8's pointer target still described the old orchestrator-gated model — orchestrator-authorized cross-file coherence fix)
- Context paths:
  - loom-code/agents/code-reviewer.md (activation block ~L403-417)
- Acceptance:
  - RED: pytest loom-code/scripts/test_code_reviewer_principles_derivation.py fails (orchestrator-gated wording present, derivation absent)
  - GREEN: same passes — derivation instruction present, override semantics stated, N/A-honesty retained
- Dependencies: none
- Independent: true
- Brief item covered: "code-reviewer principles-existence derivation: the reviewer checks the target repo … itself (filesystem derivation)"

## Task 14 — Cluster B version bump + CHANGELOG + next-arc BACKLOG entry
- Description: Bump loom-code version (minor — two scripts + three skill
  behavior changes), add CHANGELOG entry; run codex-manifest drift check.
  Also append the next-arc BACKLOG entry (escalation interface /
  decision-log / acceptance-surface behavioral contracts — the
  architecture doc §1-§2 KEEPs beyond this arc) to docs/loom/BACKLOG.md
  per its entry format, and delete the consumed COMMITTED-NEXT entry.
- Module: loom-code/
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md, docs/loom/BACKLOG.md
- Context paths:
  - loom-code/CHANGELOG.md
  - docs/loom/BACKLOG.md
  - docs/loom/design/2026-07-10-designer-pm-loop-architecture.md (§1-§2)
- Acceptance:
  - RED: (diagnostic) manifest/drift checks against unbumped state; BACKLOG lacks the next-arc entry
  - GREEN: loom-code manifest tests + `python3 scripts/sync_codex_manifests.py --check --all` exit 0 with new version; BACKLOG carries the next-arc entry with Status/Start/Origin/What and the consumed entry is gone
- Dependencies: Tasks 11, 12, 13 complete first
- Independent: false
- Brief item covered: "Version bumps + CHANGELOG entries per plugin" + "the escalation interface / decision-log / acceptance-surface behavioral contracts … go to BACKLOG at this arc's close" (Decision)
