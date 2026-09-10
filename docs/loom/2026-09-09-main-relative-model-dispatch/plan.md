# Main-relative subagent model dispatch — plan
intent: 2026-09-09-main-relative-model-dispatch@be39c611d5fb8bfc85ed35b888e420e515ff1e11
spec: docs/loom/2026-09-09-main-relative-model-dispatch/spec.md@6a29d5bb979daa017b2063ef6d38f62202f7526f
charter: 1.0

## Task DAG

### Wave 1 — portable policy contract

**W1-01 Define and prove the shared dispatch profile**  after: none  acceptance: 1, 2, 3, 4
- Files: loom-code/references/dispatch-profile.md, loom-code/scripts/test_dispatch_profile_contract.py
- Test: A1 positive: class-relative-route; boundary: insufficient-evidence. A2 positive: five-tier-map; negative: native-generation. A3 positive: atomic-fallback; negative: partial-profile. A4 positive: sequential-high-xhigh; boundary: max-inherited-only.
- Risk: REQ-1–4; agent-decided — one executable prose contract replaces role profiles, with model-specific support verified before atomic overrides.

### Wave 2 — station integration

**W2-01 Wire every loom-code dispatch and release the contract**  after: W1-01  acceptance: 5
- Files: loom-code/skills/build/SKILL.md, loom-code/skills/review/SKILL.md, loom-code/scripts/test_agent_model_frontmatter.py, loom-code/scripts/test_dispatch_profile_contract.py, loom-code/CHANGELOG.md, loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json
- Test: A5 positive: stations-resolve-profile-and-package-pass; negative: static-pin-or-missing-adapter; boundary: isolated-install-resolves-reference.
- Risk: REQ-5; agent-decided — keep routing session-local and extend existing package gates rather than adding a resolver service or ledger.

### Wave 3 — closing-review functional fixes

**W3-01 Add the executable routing oracle and station invocation**  after: W2-01  acceptance: 1, 2, 3, 4
- Files: loom-code/scripts/dispatch_profile.py, loom-code/scripts/test_dispatch_profile_resolver.py, loom-code/references/dispatch-profile.md, loom-code/skills/build/SKILL.md, loom-code/skills/review/SKILL.md
- Test: A1 positive: computed-class-route; boundary: insufficient-evidence. A2 positive: five-tier-capabilities; negative: native-generation. A3 positive: atomic-fallback; negative: host-rejection. A4 positive: sequential-escalation; boundary: terminal-success.
- Risk: REQ-1–4; agent-decided — use one pure standard-library state machine and JSON CLI, not a resident resolver service.

**W3-02 Register and reconcile the routing mechanism**  after: W3-01  acceptance: 5
- Files: docs/loom/evidence/mechanisms.yaml, loom-code/CHANGELOG.md, loom-code/scripts/test_agent_model_frontmatter.py, docs/skill-dogfood/2026-09-09-model-effort-cost-pilot/report.md, loom-code/scripts/test_dispatch_profile_contract.py
- Test: A5 positive: resolver-matrix-and-mechanism-pass; negative: stale-ledger-or-unregistered-gate; boundary: historical-calibration-not-routing.
- Risk: REQ-5; agent-decided — register one shared gate and correct stale records instead of adding per-station mechanisms or persistent state.

## Questions asked

1 — what — 可以照此提交並繼續撰寫 spec 嗎？（答：繼續吧）

## Risks

1. Host model names and supported effort values drift; adapters must inspect current capabilities and treat unknown mappings as unsupported rather than freezing a universal product table.
2. Claude Code is currently logged out, so its required live adapter probe cannot run until authentication returns; deterministic contract work remains executable.
3. Existing cost results cover one Claude review corpus and do not authorize repository-wide savings claims or additional high-effort benchmark cells.
4. Closing Review found prose-only verification insufficient; Wave 3 replaces lexical routing claims with executable state transitions while preserving the no-service boundary.
