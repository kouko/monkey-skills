# Main-relative subagent model dispatch — plan
intent: 2026-09-09-main-relative-model-dispatch@be39c611d5fb8bfc85ed35b888e420e515ff1e11
spec: docs/loom/2026-09-09-main-relative-model-dispatch/spec.md@9730418c9367c328a3123e7b1c6ffefb58acb60a
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

## Questions asked

1 — what — 可以照此提交並繼續撰寫 spec 嗎？（答：繼續吧）

## Risks

1. Host model names and supported effort values drift; adapters must inspect current capabilities and treat unknown mappings as unsupported rather than freezing a universal product table.
2. Claude Code is currently logged out, so its required live adapter probe cannot run until authentication returns; deterministic contract work remains executable.
3. Existing cost results cover one Claude review corpus and do not authorize repository-wide savings claims or additional high-effort benchmark cells.
