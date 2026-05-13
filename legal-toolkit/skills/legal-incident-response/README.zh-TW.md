# legal-incident-response

Read this in: [English](README.md) | [日本語](README.ja.md) | **繁體中文**

![version](https://img.shields.io/badge/version-0.4.2-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![phase](https://img.shields.io/badge/phase-2_收尾-orange)

> ⚠️ **本工具不是律師意見。** 本工具為免費 open-source utility，非律師事務所、亦非執業律師。輸出僅供 in-house 法務 內部參考；涉及刑事 exposure / 主管機關 應對 / 重大經營判斷的案件，請務必交由執業律師處理。

台灣 in-house 法務 **事後 incident response** skill — 3-path classifier（個資外洩 / 主管機關函覆 / 合約違約）+ auto-classification + per-path sub-protocol + audience-shaped 2-file 輸出。釘在台灣現行法（Path A，SP2 verify run 確定）；台灣 個資法 採「即時」reporting + 委託/受託 model — grader 拒收的禁止 phrase canonical list 詳見 `scripts/grade_response.py PATH_A_ANTIPATTERNS`。

## 做什麼

讀取 incident 自由描述，dispatch 到 3 路之一：

1. **個資外洩 (pii-breach)** — skeleton + LLM-fill templates → 起草 PDPC 通報文 + 當事人通知文 + 內部記錄（以 個資法 §12 + 施行細則 §22 + 相關 主管機關函釋 為 anchor）
2. **主管機關函覆 (authority-letter)** — pure-LLM protocol → 讀取來文（PDPC / 金管會 / 公平會 / 勞動部 / etc.）→ 起草 公文格式 函覆（canonical-§-gated 引用 + ISO 8601 deadline tracker）
3. **合約違約 (contract-breach)** — thin classifier + handoff JSON → soft delegate 給 `legal-contract-review`（user 手動 接力）

auto-classification（決定性 keyword scan + LLM confidence judgement）先跑；user 確認 path 後再 dispatch sub-protocol。

## 什麼時候用

- 收到 個資外洩 alert（內部回報 / 資安事件 / vendor leak）→ 起草 PDPC 通報 / 當事人通知 之前先跑
- 主管機關（PDPC / 金管會 / 公平會 / 勞動部 / etc.）來文要求 函覆 → 用法源 anchor + deadline tracker 起草
- 對方違約（交期延誤 / 付款違約 / SLA 未達）→ triage + emit `legal-contract-review` 接力用的 handoff bundle
- 需要把 內部 事件記錄 + 對外溝通 拆成 audience-shaped 兩份（法務看完整時間軸 + 法條引用；非法務看 Top 3 即時動作 + deadline 警示）

## 什麼時候不用

- **事前 policy / template 起草** → 改用 `legal-document-draft`（隱私權政策 / 服務條款 / DPA / NDA）
- **既有合約的深度 clause 分析** → 改用 `legal-contract-review`（七層 pipeline + TW overlay）
- **一般法律研究 / 法律諮詢** → Phase 3 planned `legal-research` + `legal-issue-spot`（IRAC cluster）
- **事前 playbook authoring** → 改用 `legal-playbook-author`
- **訴訟策略** — PRODUCT-SPEC §9 明確排除
- **非台灣 jurisdiction** — Path A 只處理台灣現行法；GDPR-style 功能刻意不納入

## 怎麼用

1. 透過 router 啟動：
   ```
   /using-legal-toolkit
   ```
   router 問到 Q3（個資外洩 / 違約 / 主管機關來文）時答 yes。

2. 在 repo 內準備 `legal-playbook/profile.yml` v2（schema 見 `assets/profile-schema.yml`）。必填：公司 identity + 主管機關 + optional `external_counsel` + `regulatory_authorities`（v2 新增；v1 profile auto-upgrade）。

3. 提供 incident 自由描述。skill 會 auto-classify 並請你確認 path。

各 path 一句話範例：

- **PII breach** — 「我們昨天發現某資料庫有外部存取紀錄，可能影響 5000 個客戶的姓名 + 電話」→ 產 `legal.md` + `business.md`（PDPC 通報草稿 + 當事人通知 + 內部記錄）
- **Authority letter** — 把來文內容 + 來文機關 + 來文日期貼上 → 產 函覆草稿（§-anchor 引用 + ISO 8601 deadline tracker）
- **Contract breach** — 「對方 §3 應於 2026-05-01 交付，至今未交」→ 產 handoff-context.json（給 `legal-contract-review` 接力）+ business-side 即時動作 summary

## Inputs

- **Required**：`legal-playbook/profile.yml`（v2 schema；session 開始前由 `scripts/load_profile.py` validate）
- **Required at session**：incident 自由描述（或 explicit `--type pii-breach|authority-letter|contract-breach` override）
- **Optional from profile**：`external_counsel` + `regulatory_authorities`（v2 新增；backward-compat v1 profile）

完整 schema 見 SKILL.md §Inputs + spec §4。

## Outputs

每次 session 寫入 `legal-outputs/<timestamp>-incident-<path-type>/`：

- `legal.md` — 法務 audience：事件記錄 + ISO 8601 時間軸 + path 專屬內容 + compliance checklist + TBD migration tracker
- `business.md` — 非法務 audience：1 句 summary + Top 3 即時動作 + deadline 警示 + 對外溝通要點
- `handoff-context.json` — **僅** contract-breach path 會產生（schema_version 1；10 個必填 key；soft delegation 給 `legal-contract-review`）

完整 schema 見 SKILL.md §Outputs + spec §5。

## Quality gates

- `scripts/load_profile.py`（`legal-toolkit/scripts/canonical/` 的 functional copy）依 `assets/profile-schema.yml` v2 校驗 `legal-playbook/profile.yml`；必填欄缺漏 halt session start
- `scripts/grade_response.py` per-path 跑決定性 structural check（2 個檔在 / ISO timeline / canonical TBD id / PII section 完整 / authority-letter 函覆 + ISO deadline / contract-breach handoff JSON schema）。Path A anti-pattern bank 與 SP3a v0.4.1 byte-identical — grader 在 `<doc-type>.md` output 內拒收的禁止 phrase canonical list 詳見 `scripts/grade_response.py PATH_A_ANTIPATTERNS`
- 手工 curated 的 path 別 compliance checklist（`checklists/compliance-pii-breach.md` / `compliance-authority-letter.md` / `compliance-contract-breach.md`）+ 法條引用 + `**{{verdict}}**` template

## 限制

- Path A scope：只追台灣現行法；台灣 個資法 採「即時」reporting + 委託/受託 model — grader 拒收的禁止 phrase canonical list 詳見 `scripts/grade_response.py PATH_A_ANTIPATTERNS`
- 違約 path 是 thin delegator；深度 clause 分析交給 `legal-contract-review`（soft delegation；user 手動透過 handoff-context.json 接力）
- 只輸出 zh-TW；多語言支援走 `translation-toolkit` plugin（另案）
- 本 skill **不會** auto-invoke `legal-contract-review`；`--seed` flag consumption 延到 v0.4.3+
- v0.4.2 沒有 `legal-playbook/` IR 專屬 clauses — 延到 v0.4.3+ 由 dogfood 驅動設計

## 相關 skill

- `legal-document-draft` — **事前** 起草（隱私權政策 / 服務條款 / DPA / NDA）。事件發生 *前* 用；`legal-incident-response` 是發生 *後* 用
- `legal-contract-review` — 深度 clause 分析（七層 pipeline + TW overlay）；接收本 skill contract-breach path 產生的 `handoff-context.json`
- `legal-playbook-author` — 撰寫 `legal-contract-review` 引用的議價立場
- `using-legal-toolkit` — entry-point router（Q3 dispatch 到本 skill）
- Phase 3+ planned：`legal-issue-spot` + `legal-research`（IRAC cluster）；`legal-regulation-watch`（PDPC 子法 RSS poll）

## 參考

- Spec：`docs/superpowers/specs/2026-05-13-legal-toolkit-sp3b-incident-response-design.md`
- SP2 ground truth（Path A 五大支柱）：`legal-toolkit/research/2026-05-12-pdpa-2025-11-verify.md`
- ROADMAP：`legal-toolkit/ROADMAP.md`（§Phase 2 v0.4.2）
- Plugin spec：`legal-toolkit/PRODUCT-SPEC.md` + `legal-toolkit/TECH-SPEC.md`
