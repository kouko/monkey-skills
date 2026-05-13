# PDPA Current State (SP2 ground truth summary)

> **Source**: `legal-toolkit/research/2026-05-12-pdpa-2025-11-verify.md` (SP2 PR #273)
> **Verified**: 2026-05-12 against 全國法規資料庫 + PDPC + 法務部 (Tier-A primary sources)
> **Scope**: Items used by `legal-document-draft` templates + checklists. Full per-item analysis in SP2 research note.

## Currently in force (HIGH confidence)

- 個資法 §3 — 當事人權利 (查詢 / 更正 / 刪除 / 停止處理 / 異議)
- §4 — 委託處理 + 委託者全責
- §5 — 利用範圍
- §6 — 特種個資限制
- §7-9 — 蒐集 / 處理 / 利用 + 第三人提供告知
- §8 第一項 一至六款 — 個資告知事項 (mandatory disclosure items in privacy policy)
- §11 — 個資保管期間 / 正確性
- §21 — 跨境傳輸 (主管機關公告限制)
- §22 — 主管機關職權 (DPO 推定承辦人)
- §27 — 安全維護措施 (現行)
- §47-48 — 行政罰 (pre-2025 amendment tier; new tier in 2025/11 not yet effective)
- 施行細則 §22 — 個資外洩通報「即時」(safe default for breach notification timeframe; NOT 72hr GDPR)
- 民法 §12-13 — 行為能力 (used for minor protection; NOT a PDPA-specific provision)
- 民法 §227 / §247-1 / §250 — 違約 / 定型化檢視 / 違約金
- 消保法 §11-1 — 等候期 / §17 — 定型化契約
- 公平交易法 — 不公平競爭

## Promulgated 2025-11-11 but NOT yet effective (TBD pending Executive Yuan announcement of 施行日期)

The following exist in the official law text but Art. 1-2 / 20-1 / 21-1~5 / 12 / 47-48 (new tier) are 施行日期未定. Templates use safe defaults; compliance.md tracks via TBD entries.

## Canonical TBD OPEN list

Templates and checklists may emit only the following TBD identifiers in `compliance.md`. `grade_draft.py` rejects any TBD id not in this list as "fabricated":

- **TBD_PDPC_pending** — PDPC 籌備處 → 正式委員會 transition; notification mechanism unverified
- **TBD_PDPC_threshold** — 通報範圍 (numeric / categorical trigger; Art. 12 §2 一定通報範圍授權子法)
- **TBD_PDPC_timeframe** — 通報時限具體小時數 (Art. 12 §4 sub-regulations)
- **TBD_PDPC_notification_url** — 正式通報入口 URL (form / email / paper); pdpc.gov.tw 籌備處 site JS-rendered, body unverified
- **TBD_PDPA_effective_date** — Executive Yuan announcement of 2025/11 batch 施行日期
- **TBD_PDPA_audit_framework** — Art. 20-1 audit framework (promulgated, 施行日期未定)
- **TBD_GOV_CLOUD_restrictions** — 政府機關雲端服務 mainland-China-restriction specifics (likely 政府採購法 / 資通安全管理法, not PDPA-specific; needs Tier-A primary source verification before locking)

## Out of scope for this skill (Path A boundary)

- GDPR 72hr / controller-processor / minor age threshold — NOT in current Taiwan PDPA
- HKSAR / Singapore / EU privacy laws — international expansion is a future Phase
- 2025/11 amendments-as-effective — assume promulgated-but-not-yet-effective until行政院 announcement

## Update path

When PDPC sub-regulations publish, follow `tbd-migration-template.md` to patch templates + checklists. Each TBD id has an associated migration entry.
