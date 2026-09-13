# Shrink three Loom skill entrypoints — plan
intent: 2026-09-13-shrink-three-loom-skill-entrypoints@cb3252941d4866d5370b829c5293b4008ce1bf18
charter: 1.0

## Current State Evidence

- Forward: `loom-code/skills/write-plan/SKILL.md` is 4,498 words against the repository-wide 4,500-word hard cap.
- Reverse: `loom-code/skills/write-plan/references/` already owns detailed one-way-door and second-vendor procedures that the entrypoint can load on demand.
- Error: `loom-design/scripts/spec/test_capture_intent_contract.py::test_body_within_word_cap` leaves `capture-intent` only five body words below its 3,500-word cap.
- Data: `loom-workflow/skills/independent-advisor/references/` already separates executor detection, dispatch, and reporting, while its entrypoint remains 4,035 words.
- Boundary: `scripts/test_loom_plugin_install_layout.py` verifies each Loom plugin without mandatory sibling dependencies.

## Task DAG

Wave 0

**W0-01 Freeze behavioral baselines and package invariants**  after: none  acceptance: 2, 3
- Files: loom-code/skills/write-plan/test-prompts.json, loom-design/skills/capture-intent/test-prompts.json, loom-workflow/skills/independent-advisor/test-prompts.json, docs/loom/2026-09-13-shrink-three-loom-skill-entrypoints/evidence/baseline.md
- Test: A2 positive: representative-current-use-cases; negative: omitted-failure-boundary. A3 positive: immutable-package-export; negative: relocation-only-accounting.
- Risk: Prompts could encode the desired rewrite instead of current behavior; anchor each case to documented behavior before any candidate edit — agent-decided.

Wave 1

**W1-01 Refactor write-plan as one isolated package round**  after: W0-01  acceptance: 1, 2, 3
- Files: loom-code/skills/write-plan/SKILL.md, loom-code/skills/write-plan/references/, docs/loom/2026-09-13-shrink-three-loom-skill-entrypoints/evidence/write-plan-refactor.md
- Test: A1 positive: entrypoint-below-cap; boundary: two-word-headroom. A2 positive: planning-output-equivalent; negative: decision-duty-moved-out. A3 positive: package-reduction-ten-percent; negative: prose-relocated-only.
- Risk: Prior memory says detail may move but duties may not; keep every decision, refusal, and hand-off obligation in the entrypoint — agent-decided.

**W1-02 Refactor capture-intent as one isolated package round**  after: W0-01  acceptance: 1, 2, 3
- Files: loom-design/skills/capture-intent/SKILL.md, loom-design/skills/capture-intent/references/, docs/loom/2026-09-13-shrink-three-loom-skill-entrypoints/evidence/capture-intent-refactor.md
- Test: A1 positive: body-below-specific-cap; boundary: five-word-headroom. A2 positive: capture-output-equivalent; negative: confirmation-gate-weakened. A3 positive: package-reduction-ten-percent; negative: cross-plugin-private-reference.
- Risk: The duplicated one-way-door detail exists for standalone installation; retain a plugin-local carrier and forbid references into loom-code private files — agent-decided.

**W1-03 Refactor independent-advisor as one isolated package round**  after: W0-01  acceptance: 1, 2, 3
- Files: loom-workflow/skills/independent-advisor/SKILL.md, loom-workflow/skills/independent-advisor/references/, docs/loom/2026-09-13-shrink-three-loom-skill-entrypoints/evidence/independent-advisor-refactor.md
- Test: A1 positive: entrypoint-materially-smaller; boundary: repository-cap. A2 positive: advisor-output-equivalent; negative: egress-duty-hidden. A3 positive: package-reduction-ten-percent; negative: reference-duplication-retained.
- Risk: Existing references already own mechanics, but privacy, approval, failure, and blindness obligations must remain visible at the entrypoint — agent-decided.

Wave 2

**W2-01 Publish the loom-code package revision**  after: W1-01  acceptance: 4
- Files: loom-code/CHANGELOG.md, loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json
- Test: A4 positive: isolated-loom-code-install; negative: codex-manifest-drift.
- Risk: Use a patch release because behavior is preserved; regenerate the Codex manifest from the Claude source of truth — agent-decided.

**W2-02 Publish the loom-design package revision**  after: W1-02  acceptance: 4
- Files: loom-design/CHANGELOG.md, loom-design/.claude-plugin/plugin.json, loom-design/.codex-plugin/plugin.json, loom-design/scripts/spec/test_capture_intent_contract.py
- Test: A4 positive: isolated-loom-design-install; negative: cross-plugin-boundary.
- Risk: Use a patch release because behavior is preserved; do not turn the local one-way-door carrier into a mandatory sibling dependency — agent-decided.

**W2-03 Publish the loom-workflow package revision**  after: W1-03  acceptance: 4
- Files: README.md, loom-workflow/CHANGELOG.md, loom-workflow/.claude-plugin/plugin.json, loom-workflow/.codex-plugin/plugin.json
- Test: A4 positive: isolated-loom-workflow-install; negative: codex-manifest-drift.
- Risk: Use a patch release because behavior is preserved; keep translated README claims aligned without counting translation edits as skill reduction — agent-decided.

Wave 3

**W3-01 Integrate measurements, marketplace metadata, and package gates**  after: W2-01, W2-02, W2-03  acceptance: 1, 2, 3, 4
- Files: loom-code/scripts/test_write_plan_station_text.py, docs/loom/2026-09-13-shrink-three-loom-skill-entrypoints/plan.md, docs/loom/2026-09-13-shrink-three-loom-skill-entrypoints/evidence/integration.md
- Test: A1 positive: counts-below-caps; boundary: exact-cap. A2 positive: equivalence-ensemble; negative: load-bearing-deletion. A3 positive: package-reduction; negative: relocation-only. A4 positive: isolated-installs; negative: cross-plugin-link.
- Risk: A green package suite cannot prove semantic equivalence; require each skill's frozen baseline, invariant snapshot, and layered refactor verdict — agent-decided.

## Questions asked

① — what — 你要的是：重構 `write-plan`、`capture-intent`、`independent-advisor`，讓三個 `SKILL.md` 明顯縮短、每個 package 都真正減少至少既定門檻的文字量，同時維持原有行為、契約及獨立安裝能力。三個 skill 將分別建立基準、驗證等價性，不能互相抵銷失敗。對嗎？

## Risks

1. Moving prose lowers entrypoint size but not package size; every skill must pass whole-package accounting independently.
2. Shorter instructions can weaken behavior even when static pins pass; equivalence needs representative positive, refusal, and boundary cases.
3. Existing exact-phrase tests can make harmless rewording fail; replace brittle pins only when behavior-level assertions preserve the same duty.
4. The three plugin packages share repository-level release metadata; integrate only after all isolated package rounds have passed.
