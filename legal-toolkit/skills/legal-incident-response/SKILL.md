---
name: legal-incident-response
description: Taiwan in-house 法務 incident response skill — 3-path classifier (個資外洩 PII-breach / 主管機關函覆 authority-letter / 合約違約 contract-breach). Auto-classifies free-text incident descriptions, dispatches per-path sub-protocols, emits 2-file audience-shaped output (legal.md / business.md) with ISO 8601 timeline + TBD migration tracker. PII-breach uses skeleton+LLM-fill templates pinned to current Taiwan law (Path A from SP2 verify run); authority-letter uses pure-LLM protocol; contract-breach delegates to legal-contract-review via handoff-context.json. Cross-references legal-playbook/profile.yml (shared with legal-document-draft) for company identity + regulatory_authorities + external_counsel.
---

# legal-incident-response

In-house legal toolkit incident-response skill for Taiwan SME → 上市櫃 法務. Handles **post-event response** to PII breaches / 主管機關 letters / 合約違約 via a 3-path auto-classifier + per-path sub-protocol + audience-shaped 2-file output. Path A discipline (current Taiwan in-force law; aligned with SP2 verify run).

## Paths

3-path classifier dispatches based on incident description:

- **個資外洩 (pii-breach)** — skeleton + LLM fill; emits PDPC 通報文 + 當事人通知文 + 內部記錄 (per 個資法 §12 + 施行細則 §22)
- **主管機關函覆 (authority-letter)** — pure-LLM protocol; reads incoming letter + drafts 公文格式 函覆 with canonical-§-gated 法源引用
- **合約違約 (contract-breach)** — thin classifier + handoff JSON to `legal-contract-review` (soft delegation; user manually invokes)

Auto-classification via `protocols/classify-path.md` (deterministic keyword scan + LLM confidence judgement); user confirms before path dispatch.

## Pipeline

`using-legal-toolkit` router (Q3) → `protocols/classify-path.md` (Step 0: auto-classify + confirm) → per-path sub-protocol → `scripts/grade_response.py` (deterministic structural + Path A anti-pattern checks) → 2-file output (`legal.md` + `business.md`).

## Inputs

- **Required**: `legal-playbook/profile.yml` (v2 schema; validated by `scripts/load_profile.py`)
- **Required at session**: incident free-text description (or explicit `--type` override)
- **Optional from profile**: `external_counsel` + `regulatory_authorities` (v2-added fields; backward-compat v1 profiles)

## Outputs

Per session, writes to `legal-outputs/<timestamp>-incident-<path-type>/`:
- `legal.md` — 法務 audience (event record + 時間軸 ISO 8601 + path-specific content + compliance checklist + TBD migration tracker)
- `business.md` — 非法務 audience (1-句 summary + Top 3 即時動作 + deadline 警示 + 對外溝通要點)
- `handoff-context.json` — ONLY for contract-breach path (schema_version 1; 10 required keys; soft delegation to `legal-contract-review`)

## Quality gates

- `scripts/load_profile.py` (functional copy from canonical/) validates `legal-playbook/profile.yml` against `assets/profile-schema.yml` v2 before session starts; missing required fields halt
- `scripts/grade_response.py` runs deterministic structural checks (2 files present / ISO timeline section / canonical TBD ids / Path A anti-pattern bank / per-path branches: PII section completeness / authority-letter 函覆 + ISO deadline / contract-breach handoff JSON schema)
- Hand-curated per-path compliance checklists (PII / authority / contract) with statute citations + `**{{verdict}}**` template

## Limitations (current scope per spec §9)

- Path A: tracks current in-force Taiwan law only; GDPR-style features (fixed-hour breach notification timer / EU-style 控管者-處理者 二分 split) NOT included — Taiwan 個資法 uses 「即時」 reporting language + 委託/受託 model
- 違約 path = thin delegator; `legal-contract-review` owns deep clause analysis (Q8 Soft delegation)
- zh-TW only; multi-language via `translation-toolkit` plugin (separate concern)
- No auto-invocation of contract-review from SP3b — user manually 接力 with handoff-context.json
- No `legal-playbook/` clauses for IR in v0.4.2 — deferred to v0.4.3 dogfood-driven design

## Cross-skill

- Shares `legal-playbook/profile.yml` with `legal-document-draft` (canonical/ SSOT; same schema v2)
- Hands off contract-breach to `legal-contract-review` via `handoff-context.json` (soft delegation; v0.4.3+ may add `--seed` consumption + `breach-remedy` mode)
- References `legal-toolkit/scripts/canonical/legal-sources.json` for statute URL templates (consistent with SP1 SSOT)
- `references/pdpa-current-state.md` + `references/tbd-migration-template.md` shared with SP3a via canonical/ + distribute.py

## References

- Spec: `docs/superpowers/specs/2026-05-13-legal-toolkit-sp3b-incident-response-design.md`
- SP2 ground truth: `legal-toolkit/research/2026-05-12-pdpa-2025-11-verify.md` (Path A discipline pillars)
- Classifier protocol: `protocols/classify-path.md`
- Per-path protocols: `protocols/pii-breach.md` / `protocols/authority-letter.md` / `protocols/contract-breach-delegate.md`
- Per-path checklists: `checklists/compliance-pii-breach.md` / `compliance-authority-letter.md` / `compliance-contract-breach.md`
- Templates (PII-breach): `assets/template-pii-breach-pdpc-notification.md` / `template-pii-breach-data-subject.md` / `template-pii-breach-incident-record.md`
- Handoff template (contract-breach): `assets/template-contract-breach-handoff.json`
- Grader: `scripts/grade_response.py`
- Flow narrative: `references/ir-pii-breach-flow.md` / `references/statute-citations.md`
- Plugin spec: `legal-toolkit/PRODUCT-SPEC.md` + `legal-toolkit/TECH-SPEC.md`
- ROADMAP: `legal-toolkit/ROADMAP.md`
