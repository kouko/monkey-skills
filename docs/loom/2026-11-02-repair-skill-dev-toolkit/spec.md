# Repair skill-dev-toolkit — spec
intent: 2026-11-02-repair-skill-dev-toolkit@3b1b225d
pre-build-review: required — Blind comparisons and preference exports affect evidence integrity; conflicting execution policies require an independent scope check.

## Requirements
REQ-1 — Restore advertised creator commands
  WHEN an advertised creator command receives valid inputs, the toolkit shall execute its declared packaging, benchmark aggregation, or bounded description-optimization responsibility rather than fail to parse → Acceptance #1
REQ-2 — Ordered structural comparison
  WHEN tool traces are supplied, the structural comparator shall reject reordered calls while accepting the documented limited count tolerance without introducing new tool vocabulary → Acceptance #2
REQ-3 — Blind full-output inspection
  WHEN a blind comparison is truncated, the harness shall provide full-output inspection without identity-bearing metadata and preserve the same label assignment through selection → Acceptance #3
REQ-4 — Complete usable preference export
  WHEN a valid explicit single preference is recorded, the exporter shall preserve its selected-over-other comparisons, including an explicit baseline choice, and report readiness using one consistent usable-record definition → Acceptance #4
REQ-5 — Consistent skill execution rules
  The toolkit shall supply consistent instructions for description authoring/judging, metadata location, split votes, reference extraction, ablation judges, human agreement, multi-pick handling, and blind-auditor evidence → Acceptance #5
REQ-6 — Accurate size qualification
  WHEN a planned group exceeds the declared nominal reporting bound, the report shall display a qualified size notice independently of grouping while preserving existing grouping decisions → Acceptance #6
REQ-7 — Executable regression coverage
  The verification suite shall detect the retained defects through executable or realistic behavioral cases, check current resolved instruction authorities, satisfy existing repository structural limits, and run in the relevant plugin verification path → Acceptance #7

## Design decision
- REQ-1 agent-decided — Initial recovery selectively restored `aggregate_benchmark.py`, `package_skill.py`, and `run_loop.py` from `cb8d7e4aa317af4707373636f494ebd2a45a1f4d`. Subsequent review requires bounded corrections in their consumed helpers. Preserve command invocation shapes and reference extraction; qualify missing evidence instead of preserving fabricated numeric values. Offline backends test orchestration without paid calls or browser launches.
- REQ-2 agent-decided — Same-length traces must be identical. A length difference of at most one may remove one call from the longer trace to obtain the shorter trace, with identical tool vocabulary. This preserves the existing count tolerance while enforcing relative order. No-trace skip behavior remains; this change does not claim semantic equivalence without Layer 2.
- REQ-3 agent-decided — Store complete outputs as ordinary A.md/B.md files under a fresh neutral temporary directory for the current run. Render only blind paths; never expose original filenames or use symlinks. Keep one random mapping until choice lock-in and preserve existing session decoding. Leave generated viewing files available for the current workflow; do not mutate source outputs.
- REQ-4 agent-decided — Accept ADOPT single picks and DROP with explicit baseline identity when the selected and alternative records contain usable distinct hashes. None/multiple/refine do not invent a winner. Count readiness as 1000 usable explicit single-pick records, each yielding at least one pair; report pair count separately. Align exporter, inactive training stub, schema and pipeline outline. Existing JSONL is read only; no migration or training activation.
- REQ-5 agent-decided — Description design reference is the operative authority: positive triggers first; limited 2–3 exclusions for adjacent-skill disambiguation; optional short multilingual belt only under its documented mixed-language condition. Align creator and judge, retain current reference routing, and update Principle 5 pointers to Principle 4. Do not claim new empirical triggering validation.
- REQ-5 agent-decided — Eval metadata belongs to the case directory and its explicit path goes to the grader; grading outputs remain per run. Fixed effectiveness comparison and previous-iteration regression detection remain distinct and unchanged.
- REQ-5 agent-decided — Preserve the existing vote reducer: 2 equivalent plus 1 uncertain passes moderately; 2 equivalent plus 1 non-equivalent escalates; concrete dissent retains its existing override. Entry prose follows the reducer/detailed references; no new voting engine.
- REQ-5 agent-decided — Permit a new bundled reference required for equivalent extraction while protecting existing dependencies. Resource changes follow package mode, Q1/Q3 and whole-package Q2; moving words alone earns no saving. Keep historical examples recognizable and correct their current-policy interpretation.
- REQ-5 agent-decided — Current ablation uses the Q1 three-judge ensemble. Align cost and vote mapping; preserve the dated two-judge prototype as historical. Ablation remains candidate discovery, not deletion authorization.
- REQ-5 agent-decided — Multi-human agreement uses the existing entrypoint's 70% bound: 2/3 escalates and 3/4 can form a majority. Multi-pick always defers; only a locked single non-baseline ADOPT permits an edit. None and Refine never adopt.
- REQ-5 agent-decided — Blind auditors receive an explicit output rubric plus artifact, excluding author reasoning and execution trajectory. The existing informed/orchestrator pass compares transcript steps against the declared procedure. Correct taxonomy role wording without adding a model role or inferring criteria from the flawed output.
- REQ-6 agent-decided — Keep split threshold 30000 and grouping target 25000. Treat 25000 as a conservative nominal notice bound, not a proven accuracy cliff. Any actual group over it warns, even when unsplit. The existing 25135-token corpus retains its experimental provenance and is described as approximately 25k.
- REQ-7 agent-decided — Repair scoped assertions on actual reference authorities, not legacy inline phrase placement. Replace only the obsolete root AGENTS CLI advertisement assertion with coverage of the bundled protocol. Trim judge repetition below 4500 whole-file words without changing its rubric. Add a path-filtered toolkit CI job using existing workflow conventions and direct tests for real command outputs.
- REQ-7 agent-decided — Test first, repair in sequential coherent batches, and retain independent final review and adversarial probes. Local stubs and text checks never imply real host/provider validation. No user data is rewritten or transmitted for tests; source publication is separately authorized by confirmed intent.
- REQ-1 agent-decided — Backend errors, incomplete output and timeouts before a conclusive trigger decision are evaluation failures, never successful non-triggers. Abort with non-success rather than scoring a failed negative query as correct; legitimate conclusive non-trigger decisions remain False. Exercise the actual command entry and evaluator, replacing only the offline backend/transport seam.
- REQ-1 agent-decided — Missing token capture is unknown, distinct from a captured zero. Keep existing fields, represent unavailable token values/statistics/deltas as null, and qualify Markdown and observation counts. Partial token statistics use captured observations only; a numeric token delta requires complete capture in both compared configurations. Retain known numeric results and duration precedence; never substitute characters or empty samples for measurements.
- REQ-3 agent-decided — Interactive invalid/clarification inputs continue within the current invocation using one display and map until a valid pick or EOF. Noninteractive invalid picks remain non-success. EOF aborts; another invocation is a new displayed round, not an implicit resume. Persist no pre-lock identity map and add no side-file state.
- REQ-5 agent-decided — Optimizer generation follows the bundled description authority rather than the legacy imperative/word-count prompt. Enforce deterministic description limits before returning an eligible best candidate; review contextual justification, third-person voice and trigger coverage before applying frontmatter. Do not introduce another model judge or change the established normal/router exception policy.
- REQ-4/5 agent-decided — Synchronize all tuning README/NOTICE readiness statements with usable explicit single-pick records, including valid baseline DROP choices. Golden-anchor checks may optionally supplement PASS_MODERATE but cannot clear FLAG_TIER_2 or replace its human review. Preserve the legacy comparison-result enum as a comparison-only result and retain cumulative-drift safeguards.

## Alternatives considered
- Revert all of #851 — rejected because it would discard unrelated reference extraction and consistency work.
- Rewrite the three command implementations — rejected because local Git retains compatible implementations and packaging smoke evidence.
- Compare unordered tool multisets — rejected because they still accept harmful reordering.
- Print original full-output paths or blind symlinks — rejected because identity remains discoverable in harness metadata.
- Remove truncation or ask users to choose without viewing full text — rejected because it drops an existing workflow capability.
- Treat None as an explicit baseline preference — rejected because it fabricates a selected output absent from the record.
- Replace all voting rules with two-thirds — rejected because it collapses uncertain versus non-equivalent and changes the repeated human 70% policy.
- Change splitting to 25000 — rejected because the confirmed outcome preserves 30000 grouping and only reconciles reporting.
- Redesign the judge rubric based on its self-score — rejected because subjective calibration does not prove a runtime defect.

## Current state evidence
- Forward: `skill-dev-toolkit/skills/skill-creator-advance/SKILL.md`, Packaging, still advertises the broken command.
- Reverse: `skill-dev-toolkit/skills/skill-refactor/references/equivalence-check-protocol.md`, Layer 1, requires ordered tool traces.
- Error: `skill-dev-toolkit/skills/skill-creator-advance/scripts/package_skill.py:3` is unquoted prose; #851 replaced executable modules.
- Data: `skill-dev-toolkit/skills/skill-tuning/references/preference-log-schema.md`, Per-pick entry schema, preserves explicit baseline versus None identities.
- Boundary: `skill-dev-toolkit/skills/skill-consistency-check/scripts/test_plan_groups.py`, test_T_validated_package_reads_whole, fixes grouping behavior for the approximate 25k corpus.

## UI flows
These are engineering CLI repairs; existing invocation shapes remain except for added blind viewing paths and clarified export accounting.

| Case | What the user does | What they see |
|---|---|---|
| Packaging success | Package a valid skill | A readable .skill archive and successful command completion. |
| Packaging error | Supply an invalid/missing skill | Existing validation error, nonzero completion, and no success archive; fix the input and retry. |
| Aggregation success | Aggregate valid repeated evaluations | Benchmark JSON/Markdown with recomputed statistics; unavailable token capture is explicitly unknown, with no fabricated saving. |
| Aggregation empty/error | Supply missing or malformed evaluation inputs | Existing explicit error or existing empty-data representation, never fabricated successful evaluation results; correct inputs and retry. |
| Optimization progress | Run a bounded optimization with valid backend | Existing iteration/results output, preserving evaluated candidate identity; no additional paid service is introduced. |
| Optimization failure | Backend/input fails or no compliant candidate can be evaluated | Error/non-success, never a successful negative trigger or fabricated best description; correct the cause before retrying. |
| Blind inspection | View truncated candidates and open the printed full-output files | Neutral letter-only paths and complete content, with the same letter retained when choosing. |
| Blind input error | Enter an invalid letter or request multiple-pick clarification | Interactive input is requested again against the same displayed labels; one-shot invalid picks and EOF return non-success without identity disclosure. |
| Explicit preference | Export a valid candidate or baseline choice | Selected-over-other comparison data and usable-record/pair counts. |
| No usable preference | Export None/multiple/refine or unusable records | No fabricated preference pairs; clear skipped/readiness accounting. |
| Size notice | Check a group over nominal 25k | Caution explaining approximate validation scope; grouping remains governed by 30k. |

All local fixture operations are immediate except explicitly bounded optimization iteration. Existing log data is not rewritten; generated blind copies and reports are new artifacts. These changes do not introduce a GUI or require an external model call in CI.
