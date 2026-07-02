# Plan: loom-pipeline conductor plugin

Source brief: docs/loom/specs/2026-07-03-loom-pipeline-conductor.md
Total tasks: 17
Critical-path depth: 4 (T8→{T9|T10|T11|T12}→T13→T14)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (round 3, 2026-07-03; 13/13 applicable checks; advisories: T4/T6 parallel-marking optional — kept false for review-order preference; T8 density accepted per module-boundary architecture; T6's AGENTS.md edit is a companion-file edit, not a second module)

Shared context paths (referenced by multiple tasks; implementers Read on demand):
- docs/loom/specs/2026-07-03-loom-pipeline-conductor.md (brief; G/F IDs resolve via its Evidence section)
- docs/loom/research/2026-07-03-pipeline-driver-industry-research.md (G1–G7)
- docs/loom/research/2026-07-03-lessons-from-agentic-engineering-patterns.md (recovery ladder, stable-prefix, prohibitions)
- docs/loom/dogfood/2026-07-03-pipeline-driver-dogfood.md (F1–F5, station table)
- /Users/kouko/.claude/projects/-Users-kouko-GitHub-monkey-skills/3f8c7086-8891-4198-b828-06b0c7c82b02/workflows/scripts/loom-pipeline-dogfood-wf_9e99b055-eb8.js (previous driver — derivation source)
- /Users/kouko/.claude/projects/-Users-kouko-GitHub-monkey-skills/ff13f714-94eb-43a6-825f-66df5598420c/workflows/scripts/f5-dispatch-spike-wf_667ec006-ec2.js (F5 spike — agentType dispatch proof)
- CLAUDE.md §Cross-Plugin Delegation Contract, §Skill Structure
- loom-code/agents/{implementer,spec-reviewer,code-quality-reviewer,code-reviewer}.md (agentType contracts the driver dispatches)
- loom-code/scripts/distribute.py + verify-drift.py (house SSOT-assembly precedent for the build/drift mechanism)

Driver assembly architecture (brief §Smallest End State item 2, user-approved
2026-07-03): the driver ships as flat per-concern source modules
`loom-pipeline/scripts/driver_NN_<concern>.js` (NN = concat order),
concatenated by `loom-pipeline/scripts/build_driver.py` into the
self-contained asset `loom-pipeline/skills/using-loom-pipeline/assets/loom-pipeline.js`
(generated-and-committed; Workflow scripts cannot import). **The committed
asset is owned by exactly ONE task (T14 assemble)** — module tasks touch only
their own source + test, so source-module tasks are genuinely disjoint.
Module boundaries = task boundaries. Module tasks have no build dependency:
each module test `node --check`s its own source; whole-asset checks live in
T14.

Notes:
- Same-basename pytest collision (loom-siblings-ci.yml header): all test files here use the `test_pipeline_*` prefix — unique across the repo.
- T9/T10/T11/T12 call helpers T8 defines (semantic interface dependency, declared); their Files touched are mutually disjoint source files → true parallel wave.
- T17 has no execution dependency; PR-atomic rationale: the doc pointer and the plugin land in the same PR.
- Round-2 fixes applied: former Task 5 (build script + header module + AGENTS.md, two languages) split by module boundary into T5 (header module) and T6 (build script + AGENTS.md verb declaration, dep T5 so the build has a real module to concatenate); module tasks' build dependency dropped (tests are source-only), which also cuts critical-path depth 5→4. Reviewer advisory adopted: the entry skill's run-input contract (T3) gains an optional `resumeRunId` input mapping to Workflow's native `resumeFromRunId` (the mechanism behind G6/F3 journal resume — the driver documents it; the harness implements it).
- Review-round transparency: this document's rounds 1–2 both returned NEEDS_REVISION (structural task-splitting each time, plan-side only — the brief was never implicated); the 2-round-cap escalation was surfaced to the user 2026-07-03 and round 3 authorized on the judgment that the residual fix was mechanical.

## Task 1 — plugin manifests (claude + codex)
- Description: Create `loom-pipeline/.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` (version 0.1.0, description per brief one-liner, keywords incl. `loom-pipeline`, author/homepage/license mirroring loom-product-principles' manifest shape). Write the failing test first.
- Module: loom-pipeline/.claude-plugin/
- Files touched: loom-pipeline/.claude-plugin/plugin.json, loom-pipeline/.codex-plugin/plugin.json, loom-pipeline/scripts/test_pipeline_manifests.py
- Context paths:
  - loom-product-principles/.claude-plugin/plugin.json (shape template)
- Acceptance:
  - RED: loom-pipeline/scripts/test_pipeline_manifests.py::test_manifests_exist_and_sync fails (files absent)
  - GREEN: both manifests parse, `name == "loom-pipeline"`, versions identical, keywords contain "loom-pipeline"
- External surfaces: Claude Code plugin manifest schema — grounding: existing sibling manifests in-repo (source 4d)
- Dependencies: none
- Independent: true
- Brief item covered: "A 5th thin plugin" (Smallest End State)

## Task 2 — marketplace entry
- Description: Add the `loom-pipeline` entry to `.claude-plugin/marketplace.json` (name / description matching plugin.json verbatim / source `./loom-pipeline/`). Test asserts entry present and description string-equal to plugin.json (marketplace-sync CI gate).
- Module: .claude-plugin/marketplace.json
- Files touched: .claude-plugin/marketplace.json, loom-pipeline/scripts/test_pipeline_marketplace_entry.py
- Context paths:
  - .claude-plugin/marketplace.json:92-96 (loom-code entry shape)
- Acceptance:
  - RED: test_pipeline_marketplace_entry.py::test_entry_present_and_synced fails (no entry)
  - GREEN: entry exists; description == plugin.json description
- External surfaces: none (repo-internal JSON)
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "A 5th thin plugin" (Smallest End State; marketplace = install surface)

## Task 3 — entry skill: fire conditions, run inputs, Workflow invocation
- Description: Create `loom-pipeline/skills/using-loom-pipeline/SKILL.md` with frontmatter (name/description/version 0.1.0; description states triggers + Codex N/A) and sections: when-it-fires (Workflow tool available AND 4 station plugins installed, else N/A-loud), run-input contract (change-id, target project path, per-station + run token budgets with defaults, model policy, optional `resumeRunId` mapping to Workflow's native `resumeFromRunId` for journal resume), and the invocation mechanism — resolve the driver asset's absolute path from this skill's base path and invoke `Workflow({scriptPath: <resolved>, args: {...}})`, one invocation per segment. SUBAGENT-STOP block included.
- Module: loom-pipeline/skills/using-loom-pipeline/
- Files touched: loom-pipeline/skills/using-loom-pipeline/SKILL.md, loom-pipeline/scripts/test_pipeline_skill_contract.py
- Context paths:
  - loom-code/skills/ui-verification/SKILL.md (conditional-gate + N/A-loud prose pattern)
  - CLAUDE.md §Skill Structure (flat-folder rule, ~6k token body cap)
- Acceptance:
  - RED: test_pipeline_skill_contract.py::test_fire_inputs_and_invocation fails (file absent)
  - GREEN: SKILL.md carries both fire conditions, the N/A-loud clause, all 5 run-input fields (incl. resumeRunId), AND the base-path-resolution + `Workflow({scriptPath` invocation snippet
- External surfaces: Workflow tool scriptPath + resumeFromRunId parameters — grounding: F5 spike + this session's live Workflow runs (source 4a)
- Dependencies: none
- Independent: true
- Brief item covered: "One entry skill … resolves the driver script's absolute path from the skill's base path, and invokes Workflow({scriptPath})" + "G6 … journal resume"

## Task 4 — entry skill: segments, human gates, prohibitions
- Description: Extend SKILL.md with: 3-segment execution map ([principles+design+critic] / [spec+critic] / [SDD+review+ui-verify]), the between-segment human gates (change-id minting, product forks → brief-per-#475, cost policy, final merge), verbatim driver prohibitions ("never edits station artifacts, never produces verdicts, never merges"), and the stable-prefix dispatch convention note.
- Module: loom-pipeline/skills/using-loom-pipeline/
- Files touched: loom-pipeline/skills/using-loom-pipeline/SKILL.md, loom-pipeline/scripts/test_pipeline_skill_gates.py
- Context paths:
  - docs/loom/research/2026-07-03-lessons-from-agentic-engineering-patterns.md §Borrowed (prohibitions + stable-prefix wording)
- Acceptance:
  - RED: test_pipeline_skill_gates.py::test_segments_gates_prohibitions fails (sections absent)
  - GREEN: all 3 segments named; 4 human gates listed; all 3 prohibitions present verbatim
- External surfaces: none
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: "one workflow invocation per pipeline segment, with human gates between segments" + "driver-side behavioral prohibitions stated verbatim"

## Task 5 — header module
- Description: Create `loom-pipeline/scripts/driver_00_header.js`: pure-literal `meta` (name/description/phases for all 3 segments) and args intake comment block documenting the concat contract (modules appended in filename order).
- Module: loom-pipeline/scripts/driver_00_header.js
- Files touched: loom-pipeline/scripts/driver_00_header.js, loom-pipeline/scripts/test_pipeline_driver_header.py
- Context paths:
  - previous driver script (shared context paths above — meta shape prior art)
- Acceptance:
  - RED: test_pipeline_driver_header.py::test_meta_literal fails (module absent)
  - GREEN: `node --check` passes on the source; meta is a pure literal; no `Date.now`/`Math.random`/argless `new Date` in the source
- External surfaces: Workflow script meta contract — grounding: Workflow tool docs + this session's live runs (source 4a)
- Dependencies: none
- Independent: true
- Brief item covered: "One driver script asset" (Smallest End State — the asset's head module)

## Task 6 — build script + command-surface declaration
- Description: Create `loom-pipeline/scripts/build_driver.py`: concatenate `driver_NN_*.js` in filename order → the asset path, prepend a generated-file banner, support `--out <path>` for test builds. Test builds to a TEMP path (does NOT touch the committed asset) and `node --check`s it. Declare the build verb in AGENTS.md commands section and verify it runs (runnable-capability rule).
- Module: loom-pipeline/scripts/build_driver.py
- Files touched: loom-pipeline/scripts/build_driver.py, loom-pipeline/scripts/test_pipeline_driver_build.py, AGENTS.md
- Context paths:
  - loom-code/scripts/distribute.py (assembly precedent)
- Acceptance:
  - RED: test_pipeline_driver_build.py::test_build_to_temp_and_lint fails (build script absent)
  - GREEN: temp build succeeds from the modules present; node --check passes on it; banner present; AGENTS.md declares the build verb
- External surfaces: none (repo-internal tooling)
- Dependencies: Task 5 completes first
- Independent: false
- Brief item covered: "concatenated by scripts/build_driver.py"

## Task 7 — guard module (F4)
- Description: Create `driver_10_guard.js`: args contract {segment, changeId, projectPath, budgets, models, resumeRunId?} with fail-loud validation — any missing required field or the literal string "undefined" → throw with a named-input error; no filesystem hunting, no substitute seeds.
- Module: loom-pipeline/scripts/driver_10_guard.js
- Files touched: loom-pipeline/scripts/driver_10_guard.js, loom-pipeline/scripts/test_pipeline_driver_guard.py
- Context paths:
  - docs/loom/dogfood/2026-07-03-pipeline-driver-dogfood.md (F4 incident — what improvisation looked like)
- Acceptance:
  - RED: test_pipeline_driver_guard.py::test_fail_loud_guard fails (module absent)
  - GREEN: source grep-asserts throw-on-missing + throw-on-"undefined" + all 5 required arg names; `node --check` passes on the module source
- External surfaces: none
- Dependencies: none
- Independent: true
- Brief item covered: "F4 … input-contract guard: missing inputs → FAIL, never improvise"

## Task 8 — runStation module (G1 + F1/F2 + watchdog + stable prefix)
- Description: Create `driver_20_runstation.js`: STATION result schema {verdict, artifacts, validator_exit, interventions[], summary}; `runStation` wrapper with per-station token budget check (budget.spent() delta vs cap → fail-loud), run-level budget guard, per-station wall-clock watchdog (`Promise.race` of the station promise vs a `setTimeout`-based timeout constant — a timed-out station throws, never hangs the run; setTimeout is not on the workflow banned list — if the sandbox rejects it, surface as discovery at T14, do not fake), 4-step recovery ladder (retry-same → re-ground-with-error-context → fresh-context re-dispatch → throw-to-human), rally-cap constant (≤2) exported for critic loops, stable-prefix dispatch helper (stable station preamble + appended per-change payload) whose appended contract pins "your FINAL action must be the StructuredOutput call" (F1).
- Module: loom-pipeline/scripts/driver_20_runstation.js
- Files touched: loom-pipeline/scripts/driver_20_runstation.js, loom-pipeline/scripts/test_pipeline_driver_runstation.py
- Context paths:
  - previous driver script (shared context paths above — retry wrapper prior art)
  - docs/loom/research/2026-07-03-lessons-from-agentic-engineering-patterns.md (ladder stages wording)
- Acceptance:
  - RED: test_pipeline_driver_runstation.py::test_ladder_budgets_watchdog_prefix fails (module absent)
  - GREEN: grep-asserts: 4 ladder stages named in order, per-station + run budget checks, `Promise.race` + timeout constant present, rally-cap constant = 2, StructuredOutput-pinning line, STATION schema fields; `node --check` passes on the module source
- External surfaces: Workflow `budget` primitive — grounding: Workflow tool docs (budget.spent/remaining) + dogfood run (source 4a)
- Dependencies: none
- Independent: true
- Brief item covered: "G1 (run-level token budget … per-station token budgets, over-budget = fail-loud + wall-clock watchdog per station + rally cap ≤2 … recovery ladder)" + "stable-prefix dispatch" + F1/F2

## Task 9 — segment-1 module: principles + design + critic panel
- Description: Create `driver_30_seg1.js`: idempotent adopt-if-valid on existing PRINCIPLES.md; design station (station agents load design-system + interaction-flows via Skill tool); design-critic as script-layer fresh-context panel (≥2 distinct lenses as separate `agent()` calls), rally cap via T8's constant, per-judge verdicts pushed to the ledger array (G5), G3 Decisions-section presence check on emitted artifacts.
- Module: loom-pipeline/scripts/driver_30_seg1.js
- Files touched: loom-pipeline/scripts/driver_30_seg1.js, loom-pipeline/scripts/test_pipeline_driver_seg1.py
- Context paths:
  - loom-interface-design/skills/design-critic/SKILL.md (panel + two-valued verdict contract)
  - docs/loom/dogfood/2026-07-03-pipeline-driver-dogfood.md (seg-1 station prompts prior art)
- Acceptance:
  - RED: test_pipeline_driver_seg1.py::test_seg1_panel_caps_ledger fails (module absent)
  - GREEN: grep-asserts: adopt-if-valid branch, ≥2 critic-lens dispatches, rally-cap usage, per-judge ledger push, Decisions-section check; `node --check` passes on the module source
- External surfaces: station skills via Skill tool inside agents; verdict enum PASS_WITH_NOTES/NEEDS_REVISION — grounding: design-critic SKILL.md (in-repo)
- Dependencies: Task 8 completes first
- Independent: true
- Brief item covered: "segments … [principles+design+critic]" + "G5 per-judge verdicts in ledger" + "G3 validator-checked Decisions section"

## Task 10 — segment-2 module: spec + critic + validator gate
- Description: Create `driver_40_seg2.js`: spec-expansion station seeded from segment-1 artifact paths (paths not content); completeness-critic script-layer panel (same rally/ledger contract); hard gate on `validate_spec_output.py` exit 0 via Bash inside a station agent, exit code recorded as STATION.validator_exit; G3 check on the change-folder proposal.
- Module: loom-pipeline/scripts/driver_40_seg2.js
- Files touched: loom-pipeline/scripts/driver_40_seg2.js, loom-pipeline/scripts/test_pipeline_driver_seg2.py
- Context paths:
  - loom-spec/skills/completeness-critic/SKILL.md (panel contract)
  - loom-spec/scripts/ (validator entry point name)
- Acceptance:
  - RED: test_pipeline_driver_seg2.py::test_seg2_validator_gate fails (module absent)
  - GREEN: grep-asserts: validate_spec_output invocation, validator_exit recorded, panel + rally cap reused, seed passed as paths; `node --check` passes on the module source
- External surfaces: loom-spec validator CLI — grounding: loom-spec/scripts in-repo + dogfood run (executed live)
- Dependencies: Task 8 completes first
- Independent: true
- Brief item covered: "segments … [spec+critic]" + "machine-readable gates" (validator exit-0)

## Task 11 — segment-3 module: SDD triad, review, ui-verify
- Description: Create `driver_50_seg3.js`: consume the plan path from args; per-task triad at script layer — implementer via `agentType: "loom-code:implementer"`, then spec-reviewer + code-quality-reviewer in parallel (writer≠judge structural); whole-branch review via `agentType: "loom-code:code-reviewer"` with the "You ARE the reviewer" anchor as the dispatch prompt's first line; conditional ui-verification station (fires only when ui-flows.md exists AND branch touched UI, else records N/A-loud).
- Module: loom-pipeline/scripts/driver_50_seg3.js
- Files touched: loom-pipeline/scripts/driver_50_seg3.js, loom-pipeline/scripts/test_pipeline_driver_seg3.py
- Context paths:
  - loom-code/agents/code-reviewer.md §Input contract (anchor line, verbatim)
  - loom-code/skills/ui-verification/SKILL.md (conditional-gate conditions)
- Acceptance:
  - RED: test_pipeline_driver_seg3.py::test_seg3_triad_review_uiverify fails (module absent)
  - GREEN: grep-asserts: 3 agentType dispatches per task (implementer + 2 parallel reviewers), "You ARE the reviewer" as dispatch opener, ui-verification conditional with N/A branch; `node --check` passes on the module source
- External surfaces: loom-code plugin agentTypes via workflow opts.agentType — grounding: F5 spike variant C (live, source 4a); code-reviewer.md input contract (in-repo)
- Dependencies: Task 8 completes first
- Independent: true
- Brief item covered: "segments … [SDD+review+ui-verify]" + "panels/triads at the script layer" (F5)

## Task 12 — ledger module
- Description: Create `driver_60_ledger.js`: aggregate STATION results → `docs/loom/<change-id>/pipeline-ledger.md` in the target project — per-station verdicts, per-judge panel verdicts (G5), interventions[], budget spent vs caps (run + per-station), critic-found rows count + later-rejected placeholder (G2 false-positive metric), closing line "checkpointed run — resume via journal + resumeFromRunId" (G6 naming).
- Module: loom-pipeline/scripts/driver_60_ledger.js
- Files touched: loom-pipeline/scripts/driver_60_ledger.js, loom-pipeline/scripts/test_pipeline_driver_ledger.py
- Context paths:
  - docs/loom/dogfood/2026-07-03-pipeline-driver-dogfood.md (intervention-ledger 3-bucket shape)
- Acceptance:
  - RED: test_pipeline_driver_ledger.py::test_ledger_fields fails (module absent)
  - GREEN: grep-asserts: ledger path under docs/loom/, G2 + G5 + budget fields, "checkpointed" wording; `node --check` passes on the module source
- External surfaces: none (file write inside target project via station agent)
- Dependencies: Task 8 completes first
- Independent: true
- Brief item covered: "G2 critic false-positive rate as ledger metric; G5 per-judge verdicts in ledger; G6 honest 'checkpointed, not durable' naming"

## Task 13 — main dispatch module
- Description: Create `driver_90_main.js`: segment dispatcher — route `args.segment` (1/2/3) to the segment function, render the ledger via T12's helper, return a machine-readable run summary {segment, stations[], verdicts, budget} for the entry skill to relay.
- Module: loom-pipeline/scripts/driver_90_main.js
- Files touched: loom-pipeline/scripts/driver_90_main.js, loom-pipeline/scripts/test_pipeline_driver_main.py
- Context paths:
  - loom-pipeline/scripts/driver_30_seg1.js, driver_40_seg2.js, driver_50_seg3.js, driver_60_ledger.js (function names it routes to — read after those tasks land)
- Acceptance:
  - RED: test_pipeline_driver_main.py::test_segment_routing fails (module absent)
  - GREEN: grep-asserts: routing covers segments 1/2/3, ledger render call, run summary returned; `node --check` passes on the module source
- External surfaces: none
- Dependencies: Tasks 9, 10, 11, 12 complete first
- Independent: false
- Brief item covered: "one workflow invocation per pipeline segment" (the `args.segment` interface v1.1 batch mode builds on — brief §Committed next enabling-interface sentence)

## Task 14 — assemble the committed asset (sole owner)
- Description: Run `build_driver.py` to produce and commit `skills/using-loom-pipeline/assets/loom-pipeline.js` from all landed modules; add the drift test (rebuild == committed asset, byte-identical) and whole-asset checks. This is the ONLY task that writes the committed asset.
- Module: loom-pipeline/skills/using-loom-pipeline/assets/
- Files touched: loom-pipeline/skills/using-loom-pipeline/assets/loom-pipeline.js, loom-pipeline/scripts/test_pipeline_driver_drift.py
- Context paths:
  - loom-code/scripts/verify-drift.py (drift-check precedent)
- Acceptance:
  - RED: test_pipeline_driver_drift.py::test_asset_matches_rebuild fails (asset absent)
  - GREEN: committed asset exists; rebuild diff is empty; `node --check` passes on the asset; all module markers (header/guard/runstation/seg1/seg2/seg3/ledger/main) present in the asset
- External surfaces: none
- Dependencies: Tasks 6, 7, 13 complete first
- Independent: false
- Brief item covered: "with a rebuild-and-diff drift test — the same SSOT-and-functional-copy mechanism as loom-code's distribute.py; the built asset is generated-and-committed"

## Task 15 — README + CHANGELOG
- Description: Create `loom-pipeline/README.md` (single language, per loom-sibling convention): what it is (3-layer hybrid diagram), install, run inputs, human gates, Codex N/A-loud note, G4 section — the verdict-distribution comparison protocol for the Sonnet-vs-Fable gate A/B (same branch reviewed by both tiers; compare verdict tokens + finding severity distributions against human review), committed-next v1.1 batch implementation mode (queue of frozen change-folders → batch segment-3 runs → PR-not-merge), and parked items with re-triggers (full autopilot; Codex shell driver; dispatch lock; CHECK/ACT monitor; G7 mutation testing). Create `CHANGELOG.md` with [0.1.0] entry.
- Module: loom-pipeline/README.md
- Files touched: loom-pipeline/README.md, loom-pipeline/CHANGELOG.md, loom-pipeline/scripts/test_pipeline_readme.py
- Context paths:
  - loom-spec/README.md (sibling single-README shape)
  - docs/loom/specs/2026-07-03-loom-pipeline-conductor.md §Committed next + §Out of Scope (planned + parked list source)
- Acceptance:
  - RED: test_pipeline_readme.py::test_readme_parks_and_codex_note fails (files absent)
  - GREEN: README carries Codex N/A note + G4 comparison-protocol section + v1.1 batch-mode section + all 5 parked items with re-triggers; CHANGELOG has [0.1.0]
- External surfaces: none
- Dependencies: Task 4 completes first
- Independent: true
- Brief item covered: "G4 (verdict-distribution comparison protocol documented for the Sonnet-vs-Fable A/B)" + "Out of Scope … parked re-trigger" + "Committed next (v1.1)" surfaced in the shipped doc

## Task 16 — CI workflow
- Description: Add `.github/workflows/loom-pipeline-ci.yml`: single job running `python3 -m pytest loom-pipeline/scripts/ -q` (which includes the build-drift test) on PRs/pushes touching `loom-pipeline/**`, `.claude-plugin/marketplace.json`, or the workflow file (fail-open guard per loom-siblings header). Separate invocation (same-basename collision rule). Test asserts the YAML parses and the three path triggers exist.
- Module: .github/workflows/loom-pipeline-ci.yml
- Files touched: .github/workflows/loom-pipeline-ci.yml, loom-pipeline/scripts/test_pipeline_ci_workflow.py
- Context paths:
  - .github/workflows/loom-siblings-ci.yml (shape + path-trigger rationale)
- Acceptance:
  - RED: test_pipeline_ci_workflow.py::test_workflow_paths fails (workflow absent)
  - GREEN: YAML loads; paths include loom-pipeline/**, marketplace.json, self; pytest command targets loom-pipeline/scripts/
- External surfaces: GitHub Actions workflow syntax — grounding: sibling workflows in-repo (source 4d)
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "Structural tests for the script + skill prose (repo CI)"

## Task 17 — dogfood report pointer (obsolescence note)
- Description: Edit the header note of `docs/loom/dogfood/2026-07-03-pipeline-driver-dogfood.md`: the "driver-layer requirements learned" framing gains one line — F1–F5 are now implemented by `loom-pipeline` v0.1.0 (this doc stays the evidence record; the plugin is the living implementation).
- Module: docs/loom/dogfood/
- Files touched: docs/loom/dogfood/2026-07-03-pipeline-driver-dogfood.md
- Context paths:
  - docs/loom/specs/2026-07-03-loom-pipeline-conductor.md §What Becomes Obsolete
- Acceptance:
  - RED: `grep -q "implemented by .loom-pipeline" docs/loom/dogfood/2026-07-03-pipeline-driver-dogfood.md` exits 1
  - GREEN: same grep exits 0; no other content changed
- External surfaces: none
- Dependencies: none
- Independent: true
- Brief item covered: "The dogfood report's 'driver requirements F1–F5' section flips from wishlist to implemented-reference (update its header note in the same change)"
