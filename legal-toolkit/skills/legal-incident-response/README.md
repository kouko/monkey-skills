# legal-incident-response

Read this in: **English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

![version](https://img.shields.io/badge/version-0.4.2-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![phase](https://img.shields.io/badge/phase-2_Closeout-orange)

> ⚠️ **Not legal advice.** Free open-source utility, not a law firm. Outputs are for in-house 法務 internal reference only — escalate to a licensed lawyer for any matter with criminal exposure, regulator-facing risk, or material business impact.

Taiwan in-house 法務 **post-event incident response** skill — 3-path classifier (PII breach / authority letter / contract breach) with auto-classification, per-path sub-protocols, and audience-shaped 2-file output. Pinned to current in-force Taiwan law (Path A from the SP2 verify run); Taiwan 個資法 uses 「即時」 reporting language + 委託/受託 model — see `scripts/grade_response.py PATH_A_ANTIPATTERNS` for the canonical list of phrases the grader rejects.

## What it does

Reads a free-text incident description and dispatches to one of 3 paths:

1. **個資外洩 (pii-breach)** — skeleton + LLM-fill templates → drafts PDPC 通報文 + 當事人通知文 + 內部記錄 grounded in 個資法 §12 + 施行細則 §22 + relevant 主管機關函釋.
2. **主管機關函覆 (authority-letter)** — pure-LLM protocol → reads incoming letter (PDPC / 金管會 / 公平會 / etc.) and drafts 公文格式 函覆 with canonical-§-gated citations and ISO 8601 deadline tracking.
3. **合約違約 (contract-breach)** — thin classifier + handoff JSON → soft delegates to `legal-contract-review` for deep clause analysis; user manually 接力.

Auto-classification runs first (deterministic keyword scan + LLM confidence judgement). User confirms the path before sub-protocol dispatch.

## When to use

- Just received a 個資外洩 alert (internal report, security incident, vendor leak) → run before drafting PDPC 通報 or 當事人通知.
- 主管機關 (PDPC / 金管會 / 公平會 / 勞動部 / etc.) sent a 來文 demanding 函覆 → run to draft response with statute anchors + deadline tracker.
- Counterparty is in breach (delivery delay / payment default / SLA miss) → run to triage + emit handoff bundle for `legal-contract-review`.
- Need internal 事件記錄 + business-side 對外溝通 split in audience-shaped form (法務 sees full timeline + statute cites; non-lawyers see Top 3 actions + deadline alerts).

## When NOT to use

- **Pre-event policy / template authoring** → use `legal-document-draft` (隱私權政策 / ToS / DPA / NDA drafting).
- **Deep contract clause analysis** for an existing contract → use `legal-contract-review` (7-layer pipeline with TW overlay).
- **General legal research / 諮詢** → planned Phase 3 `legal-research` + `legal-issue-spot` (IRAC cluster).
- **Pre-event playbook authoring** → use `legal-playbook-author`.
- **Litigation strategy** — out of scope per design (PRODUCT-SPEC §9).
- **Non-Taiwan jurisdictions** — Path A is Taiwan-current-law only; GDPR-style features intentionally excluded.

## How to use

1. Invoke via the router:
   ```
   /using-legal-toolkit
   ```
   When the router asks Q3 (個資外洩 / 違約 / 主管機關來文), answer yes.

2. Ensure `legal-playbook/profile.yml` v2 exists in your repo (see `assets/profile-schema.yml`). Required fields: company identity + statutory authority + optional `external_counsel` + `regulatory_authorities` (v2 additions; v1 profiles auto-upgrade).

3. Provide the incident free-text description. The skill auto-classifies + asks you to confirm.

Per-path one-liners:

- **PII breach** — "我們昨天發現某資料庫有外部存取紀錄，可能影響 5000 個客戶的姓名 + 電話" → emits `legal.md` + `business.md` with PDPC 通報草稿 + 當事人通知 + 內部記錄.
- **Authority letter** — paste 來文內容 + 來文機關 + 來文日期 → emits 函覆草稿 with §-anchored citations + ISO 8601 deadline tracker.
- **Contract breach** — "對方 §3 應於 2026-05-01 交付，至今未交" → emits handoff-context.json for `legal-contract-review` + business-side 即時動作 summary.

## Inputs

- **Required**: `legal-playbook/profile.yml` (schema v2; validated by `scripts/load_profile.py` before session starts; see `references/profile-schema-v2-migration.md` for v1→v2 delta)
- **Required at session**: incident free-text description (or explicit `--type pii-breach|authority-letter|contract-breach` override)
- **Optional from profile**: `external_counsel` + `regulatory_authorities` + `dpo.phone` (all optional in schema v2)

See SKILL.md §Inputs + spec §4 for full schema.

## Outputs

Per session, writes to `legal-outputs/<timestamp>-incident-<path-type>/`:

- `legal.md` — 法務 audience: event record + 時間軸 ISO 8601 + path-specific content + compliance checklist + TBD migration tracker
- `business.md` — 非法務 audience: 1-句 summary + Top 3 即時動作 + deadline 警示 + 對外溝通要點
- `handoff-context.json` — ONLY for contract-breach path (schema_version 1; 10 required keys; soft delegation to `legal-contract-review`)

See SKILL.md §Outputs + spec §5 for full schema.

## Quality gates

- `scripts/load_profile.py` (functional copy from `legal-toolkit/scripts/canonical/`) validates `legal-playbook/profile.yml` against `assets/profile-schema.yml` v2; missing required fields halt session start.
- `scripts/grade_response.py` runs deterministic structural checks per path (2-file presence / ISO timeline / canonical TBD ids / PII section completeness / authority-letter 函覆 + ISO deadline / contract-breach handoff JSON schema). Path A anti-pattern bank is byte-identical to SP3a v0.4.1 — see `scripts/grade_response.py PATH_A_ANTIPATTERNS` for the canonical list of phrases the grader rejects in `<doc-type>.md` output.
- Hand-curated per-path compliance checklists (`checklists/compliance-pii-breach.md` / `compliance-authority-letter.md` / `compliance-contract-breach.md`) with statute citations + `**{{verdict}}**` template.

## Limitations

- Path A scope: tracks current in-force Taiwan law only; Taiwan 個資法 uses 「即時」 reporting language + 委託/受託 model — see `scripts/grade_response.py PATH_A_ANTIPATTERNS` for the canonical list of phrases the grader rejects.
- 違約 path = thin delegator; `legal-contract-review` owns deep clause analysis (soft delegation; user manually 接力 via handoff-context.json).
- zh-TW output only; multi-language via the separate `translation-toolkit` plugin.
- No auto-invocation of `legal-contract-review` from this skill; `--seed` flag consumption deferred to v0.4.3+.
- No `legal-playbook/` IR-specific clauses in v0.4.2 — deferred to v0.4.3+ dogfood-driven design.

## Related skills

- `legal-document-draft` — **pre-event** drafting (隱私權政策 / ToS / DPA / NDA). Use BEFORE an incident happens; `legal-incident-response` is for AFTER.
- `legal-contract-review` — deep clause analysis (7-layer pipeline + TW overlay); receives `handoff-context.json` from this skill's contract-breach path.
- `legal-playbook-author` — author the negotiation stances that `legal-contract-review` consumes.
- `using-legal-toolkit` — entry-point router (Q3 dispatches here).
- Phase 3+ planned: `legal-issue-spot` + `legal-research` (IRAC cluster); `legal-regulation-watch` (PDPC 子法 RSS poll).

## References

- Spec: `docs/superpowers/specs/2026-05-13-legal-toolkit-sp3b-incident-response-design.md`
- SP2 ground truth (Path A pillars): `legal-toolkit/research/2026-05-12-pdpa-2025-11-verify.md`
- ROADMAP: `legal-toolkit/ROADMAP.md` (§Phase 2 v0.4.2)
- Plugin spec: `legal-toolkit/PRODUCT-SPEC.md` + `legal-toolkit/TECH-SPEC.md`
