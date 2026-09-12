# Risk-based reviewer floor — plan
intent: 2026-09-12-risk-based-reviewer-floor@8b0d9a318
charter: 1.0

## Current State Evidence
- Forward: `loom-code/skills/review/SKILL.md` at “Every change” always dispatches two reviewers.
- Reverse: `loom-code/scripts/loom_checker.py` at `validate_attestation` rejects every attestation with fewer than two reviewer identities.
- Error: `loom-code/scripts/loom_checker.py` at `cmd_finalize_review` rejects review input before executing verification when only one reviewer is present.
- Data: `loom-code/contract/manifest.yaml` at action `read` declares a fixed reviewer floor of two.
- Boundary: `loom-code/scripts/test_loom_attestation.py` pins both finalization and publication validation to the same fixed floor.

## Task DAG

### Wave 1 — executable policy

**W1-01 Add a fail-closed reviewer-floor computation**  after: none  acceptance: 1,2,3
- Files: loom-code/scripts/loom_checker.py, loom-code/scripts/test_loom_attestation.py, docs/loom/evidence/risk-based-reviewer-floor.py
- Test: A1 positive: allowed-low-risk-delta; boundary: mixed-or-unknown-delta. A2 positive: protected-path-two; boundary: malformed-base-two. A3 positive: finalize-one-when-eligible; negative: validate-under-floor.
- Risk: agent-decided — reuse branch-base and changed-path primitives in the checker; default to two on every classification or Git error instead of adding lane state.

### Wave 2 — one policy, consistent guidance

**W2-01 Make Closing Review consume the executable floor**  after: W1-01  acceptance: 3,4,5
- Files: loom-code/skills/review/SKILL.md, loom-code/skills/write-plan/SKILL.md, loom-code/contract/manifest.yaml, loom-code/scripts/test_simplified_station_text.py, loom-code/scripts/test_write_plan_station_text.py
- Test: A3 positive: review-invokes-policy; negative: prose-declared-count. A4 positive: safeguards-retained; boundary: no-new-state. A5 positive: contract-pins-SSOT; negative: fixed-floor-text.
- Risk: agent-decided — keep operational instructions in Review and replace other reviewer counts with references; do not duplicate the allowlist outside checker tests.

**W2-02 Remove contradictory reviewer counts from design stations**  after: W1-01  acceptance: 4,5
- Files: PRINCIPLES.md, loom-design/skills/capture-intent/SKILL.md, loom-design/skills/write-spec/SKILL.md, loom-design/skills/product-principles/SKILL.md, loom-design/skills/design-system/SKILL.md, loom-code/scripts/test_simplified_station_text.py
- Test: A4 positive: station-flow-unchanged; boundary: no-new-user-stop. A5 positive: all-summaries-policy-neutral; negative: stale-small-full-counts.
- Risk: agent-decided — align the ratified quality floor and make station summaries policy-neutral; the user's intent confirmation authorizes replacing the obsolete lane exception.

### Wave 3 — package truth and integration

**W3-01 Publish coherent plugin metadata and run integration gates**  after: W2-01,W2-02  acceptance: 1,2,3,4,5
- Files: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md, loom-design/.claude-plugin/plugin.json, loom-design/.codex-plugin/plugin.json, loom-design/CHANGELOG.md
- Test: A1 positive: clean-checkout-policy; boundary: install-layout. A2 positive: protected-fixtures; negative: unknown-fixture. A3 positive: finalize-roundtrip; negative: stale-attestation. A4 positive: package-suite; boundary: mechanism-count. A5 positive: manifest-sync; negative: crossref-drift.
- Risk: agent-decided — use patch releases unless executable contract compatibility requires a minor bump; keep manifests synchronized from Claude SSOT.

## Questions asked
1 — what — 只有當整個變更可由機械規則證明為明確、低風險範圍時，Closing Review 才降為 1 位 reviewer；其他情況維持 2 位，且既有驗證與發布安全不變。若回答「是」，也授權 Review 通過後非強制 push 並建立 Ready PR，但 merge 另行決定。這是你要的嗎？

## Risks
1. A broad allowlist could hide risky documentation or configuration changes; eligibility therefore uses narrow positive evidence and makes mixed or unrecognized paths require two reviewers.
2. Finalization and publication could disagree if they compute from different inputs; both must call one function over the same repository and selected commit.
3. Historical lane prose may imply obsolete behavior; operative station text will become policy-neutral while historical records remain untouched.
4. Scope correction — `PRINCIPLES.md` is an operative standing contract whose zero-reviewer gate-only clause contradicts Acceptance #2; W2-02 must align it with the confirmed intent.
