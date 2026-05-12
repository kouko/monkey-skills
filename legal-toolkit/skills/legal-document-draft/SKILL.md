---
name: legal-document-draft
description: Draft new Taiwan-law legal documents (privacy policy / ToS / DPA / NDA) from company profile + negotiation playbook + per-session inputs. Skeleton-and-LLM-fill templates pinned to current in-force 個資法 + 民法 + 消保法 + 公平交易法; hand-curated per-mode compliance checklists with statute citations; deterministic structural grading; safe defaults for items deferred to PDPC 子法 (Phase 2.5 patch path documented in compliance.md TBD migration section). Outputs 2 files per session — <doc-type>.md (publish-ready) + compliance.md (法務 internal review) — into legal-outputs/<timestamp>-<mode>/. Cross-references legal-playbook/ for variable defaults; uses legal-playbook/profile.yml as the single source of company identity shared across legal-toolkit skills.
---

# legal-document-draft

In-house legal toolkit drafting skill for Taiwan SME → 上市櫃 法務. Generates **new** legal documents (the company's own privacy policy / ToS / DPA / NDA) from a 4-mode template library, with current-Taiwan-law statute citations and deterministic structural verification.

## Modes

- **privacy** — 隱私權政策 / 個資告知事項 (個資法 §8 + §9 + §21 + 施行細則 §22)
- **tos** — Terms of Service / 服務條款 (民法 + 消保法 §11-1 / §17 + 公平交易法)
- **dpa** — Data Processing Agreement / 委託處理協議 (個資法 §4 + §8 + 施行細則 §12)
- **nda** — Non-Disclosure Agreement / 保密協議 (民法 + 商業慣例)

## Pipeline

`protocols/draft.md` orchestrates: LOAD_PROFILE → SELECT_TEMPLATE → SCAN_PLAYBOOK → ASK_GAPS → MERGE → COMPLY_CHECK → SELF_GRADE → OUTPUT.

## Inputs

- **Required**: `legal-playbook/profile.yml` (validated against `assets/profile-schema.yml`)
- **Required at session**: mode flag + per-mode session variables (collected via ASK_GAPS)
- **Optional**: `legal-playbook/<clause>.md` (playbook supplies stance defaults for variables; session can override)

## Outputs

Per session, writes 2 files to `legal-outputs/<timestamp>-<mode>/`:
- `<doc-type>.md` — publish-ready Markdown document; safe defaults inline for items deferred to PDPC 子法 (e.g., breach notification timeframe = "即時")
- `compliance.md` — 法務 internal review: hand-curated checklist with PASS / FAIL / TBD_<reason> verdicts + TBD migration tracking (instructions for upgrading when PDPC sub-regulations land)

## Quality gates

- `scripts/load_profile.py` validates `legal-playbook/profile.yml` against `assets/profile-schema.yml` before draft starts; missing required fields halt with explicit message
- `scripts/grade_draft.py` runs deterministic structural checks on the output directory: no orphan `{{variable}}`, all checklist items have verdicts, no fabricated TBDs (must match canonical OPEN list from `references/pdpa-current-state.md`), document.md exceeds minimum byte count
- Hand-curated compliance checklists (per mode) ground the COMPLY_CHECK step in primary-source statute references

## Limitations (current scope per spec §13)

- Path A: tracks current in-force Taiwan law only; GDPR-style features (controller/processor split, 72hr breach window) are NOT included
- 2025/11 PDPA amendments are tracked as TBD in compliance.md migration sections; templates use current施行細則 §22 "即時" language until PDPC 子法 publishes specific timeframes
- Minor protection: cites 民法 §12-13 (not invented PDPA-specific age threshold)
- 5th mode (員工合約 / 服務契約 / 採購合約 / SLA): YAGNI per spec §13; add when user demand emerges

## Cross-skill

- Shares `legal-playbook/confidentiality.md` stance with `legal-contract-review nda` mode (draft generates new; review redlines existing)
- Reads `legal-playbook/profile.yml` (created and maintained by user; skill does NOT auto-modify)
- References `legal-toolkit/skills/legal-contract-review/assets/legal-sources.json` URL templates **at template authoring time** (templates hardcode URLs); NOT a runtime dependency

## References

- Spec: `docs/superpowers/specs/2026-05-13-legal-toolkit-sp3a-document-draft-design.md`
- SP2 ground truth: `legal-toolkit/research/2026-05-12-pdpa-2025-11-verify.md`
- TBD migration guide: `references/tbd-migration-template.md`
- Statute URL index: `references/statute-citations.md`
- Plugin spec: `legal-toolkit/PRODUCT-SPEC.md` + `legal-toolkit/TECH-SPEC.md`
- Roadmap: `legal-toolkit/ROADMAP.md`
