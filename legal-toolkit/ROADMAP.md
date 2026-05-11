# legal-toolkit Roadmap (v0.1.0 → v1.0.0)

> **Status**: design phase complete, scaffold in progress
> **Source of design**: `<obsidian-vault>/research/2026-05-09 法務 Agent Skill (legal-toolkit) 整體架構與執行流程設計.md`（1344 行；38+ 鎖定決定見 §11 ledger）
> **Target**: 台灣 SME → 上市櫃 in-house 法務 in-house toolkit（不是 BigLaw 移植 / 不是 general legal assistant）
> **Distribution**: 免費 open-source 工具，非服務（律師法 §48 對工具不適用）

---

## 結論

完整 11 skill 從 0 → GA 估 **~60-80 工作天**（focused mode）或 **6-8 個月** part-time，分 7 個 phase + 1 個 prerequisite research bracket。Phase 4.5（上市櫃 Compliance research）是 critical path 唯一可平行的長尾項，建議 Phase 2 之後就先開頭做。

---

## Timeline 總覽

```
Phase  v0.x.0  天數    Skill 累計   Critical
─────  ──────  ──────  ─────────   ────────
1      0.1.0   8-12d   3           MVP shell
1.5    0.2.0   5d      3 (補基建)  DSL + ABAC + 8 條 baseline + seed
1.6    0.3.0   3-5d    3 (補 eval) Binary rubric + dogfood baseline
2      0.4.0   10d     5           Template + Runbook cluster
─────────────────────────────────  ─── 至此 = 完整合約 + 合規應變
3      0.5.0   8-12d   7           IRAC cluster (諮詢 + 研究)
4      0.6.0   10d     9           Tracker cluster
4.5    ─       10-15d  9 (no skill) ⚠️ Compliance prerequisite research
5      0.9.0   10-15d  11          Compliance cluster
6      1.0.0   ongoing 11 (治理)   Governance mechanics + GA polish
```

---

## 完整 Skill 全景（11 個）

| # | Skill | Cluster | Abstraction | Phase | Status |
|---|---|---|---|---|---|
| 0a | `using-legal-toolkit` | router | Model System | 1 | MVP |
| 0b | `legal-playbook-author` | utility (cross-cluster) | Workflow | 1 | MVP |
| 1 | `legal-contract-review` | 📋 Playbook | playbook (七層 + TW overlay) | 1 | MVP |
| 2 | `legal-document-draft` | 📝 Template | template + playbook override | 2 | planned |
| 3 | `legal-incident-response` | 🚨 Runbook | NIST IR | 2 | planned |
| 4 | `legal-issue-spot` | 🔍 IRAC | issue 矩陣 + 構成要件涵攝 | 3 | planned |
| 5 | `legal-research` | 🔍 IRAC | IRAC + 請求權基礎 + Agent | 3 | planned |
| 6 | `legal-contract-tracker` | 📅 Tracker | 時序 + threshold alert | 4 | planned |
| 7 | `legal-regulation-watch` | 📅 Tracker | RSS poll + LLM 摘要 + Agent | 4 | planned |
| 8 | `legal-corporate-governance` | 🏛️ Compliance | statutory checklist + filing template + deadline tracker | 5 | ⚠️ BLOCKED on 4.5 research |
| 9 | `legal-dd-quickscan` | 🏛️ Compliance | DD checklist 30-50 項 | 5 | ⚠️ BLOCKED on 4.5 research |

---

## Phase 1 — MVP shell（v0.1.0，8-12 天）

**Scope**：3 skill + cold-start fallback。

**Q-lock**（5+1 鎖定決定）：
- Q-A：plugin 初始 version = **v0.1.0**
- Q-B：雛形成熟度 = **(ii)** SKILL.md + protocols 骨架 + assets stub（不含 baseline 8 條完整內容）
- Q-C：Phase 5 兩個 skill **不建任何空殼**；router 識別表標 Phase 5 + 「pending prerequisite research」
- Q-D：visible 三層擁有權設計（`legal-playbook/` + `legal-outputs/` + `.legal-toolkit/`）；不預留 `clauses/` / `templates/`
- Q-E：disclaimer / escalation override 模板放 **各 skill `assets/{disclaimer-block,escalation-override}.md`**，TECH-SPEC 註明三 skill 內容必須 byte-identical
- Q-F：Cold-start fallback ship **4 條 flat baseline**（confidentiality / governing-law-jurisdiction / auto-renewal / termination-and-survival）+ L7 fallback branch + author bootstrap (a)(b)(c) 三選一 + `escalate_to` 佔位字串 + L7 偵測 warning（β 方案）

### 交付物

| 模組 | 檔案 |
|---|---|
| Plugin root | `legal-toolkit/.claude-plugin/plugin.json`（v0.1.0）/ 加入 `.claude-plugin/marketplace.json` / `README.{md,ja.md,zh-TW.md}` |
| Spec | `PRODUCT-SPEC.md`（商業 + 設計，從 design note §1+§2 抽）/ `TECH-SPEC.md`（含 Cold-Start Fallback 章節） |
| router | `skills/using-legal-toolkit/{SKILL.md, README×3}` — 6 cluster 識別表（Phase 2-5 標 not-yet-available） |
| author | `skills/legal-playbook-author/{SKILL.md, protocols/{bootstrap,extend,revise}-mode.md, assets/{stub.flat.md, stub.variant.md, stub._clause.md, disclaimer-block.md, escalation-override.md}, README×3}` |
| review | `skills/legal-contract-review/{SKILL.md, protocols/{L0a,L0b,L1,L2,L3,L4,L5,L6,L6_5,L7}.md, assets/{output-schema-×6, baseline-fallback-×4, disclaimer-block.md, escalation-override.md}, checklists/{answer,source}-criteria.md, README×3}` |

### Quality gate

5 份真合約跑 contract-review（NDA / SaaS MSA / 採購 / 勞動 / DPA），手動評：
- 6 份輸出檔案完整度（issues / redline / memo-legal / memo-business / escalation / self-grade 全有）
- Disclaimer block 100% 出現於檔尾
- Escalation Override 在高風險場景觸發正確（risk_default red / walk_away_triggered / confidence < 0.7）
- Cold-start 4 條 fallback 命中率 ≥ 50%
- 沒有 LLM pipeline 跳步

---

## Phase 1.5 — DSL 基建（v0.2.0） ✅ **DONE 2026-05-12**

**Scope**：補基礎設施，**不新增 skill**。

**完成狀態**（commits 6748333 → 9892690 on `feat/legal-toolkit-v0.1.0`）：
- ✅ JSON Schema 2020-12 for flat / variant-file / _clause shapes
- ✅ discover_playbook.py + validate_schema.py + detect_conflicts.py
- ✅ abac_filter.py + build_baseline.py + seed_baseline.py
- ✅ 8-clause baseline tarball (4 flat + 4 with variant-folders) +
  deterministic build + sha256-pinned manifest
- ✅ bootstrap-mode / extend-mode / revise-mode / L7-evaluate wired
  to invoke the scripts
- ✅ 80+ tests across all components

### 交付物

| 模組 | 檔案 |
|---|---|
| Schema | `skills/legal-playbook-author/assets/schema.json`（flat / `_clause` / variant 三套 JSON schema） |
| Scripts | `legal-playbook-author/scripts/{discover_playbook.py, validate_schema.py, detect_conflicts.py}` — cwd → ancestors → BFS 深度 5 → bundle fallback |
| Scripts | `legal-contract-review/scripts/{abac_filter.py, seed_baseline.py}` — rule-based gate matching + 解壓 baseline archive |
| Baseline | `legal-contract-review/assets/baseline-playbooks.tar.gz` — 8 條完整（含 LoL / Indemnification / DPA 三 variant-folder）+ `seed-manifest.yml` |
| Author 升級 | bootstrap mode 加 (a) 新增「seed 8 條 baseline」選項；偵測「需要 variants」trigger（user 答 walk_away 提到 deal_size / counterparty_type）|

### Quality gate

- ✅ Validator 跑 24 個 hand-crafted broken playbook 抓出 **24/24**（要求 ≥ 22）
- ✅ ABAC filter 對 12 個 deal_context 變項配對 **12/12 正確**（要求 ≥ 11）
- ✅ baseline seed 後立即跑 contract-review 0 error（seed_baseline.py 後所有
  17 檔 schema 驗證 PASS / detect_conflicts.py 0 conflict）

---

## Phase 1.6 — Eval 基建（v0.3.0，3-5 天）

**Scope**：定量驗證機制，**不新增 skill**。

### 交付物

| 模組 | 檔案 |
|---|---|
| Rubric | `legal-contract-review/checklists/answer-criteria.md`（10-15 條 binary） |
| Rubric | `legal-contract-review/checklists/source-criteria.md`（4-6 條 binary） |
| Rubric | `legal-playbook-author/checklists/playbook-quality.md`（給 author 產出評估） |
| Eval harness | `legal-contract-review/scripts/self_grade.py` — LLM 自評 + 結果寫進 `self-grade.md` |
| Dogfood corpus | `docs/dogfood-corpus/`（5-10 份合約 + 對應 hand-graded reference） |

### Quality gate

LLM self-grade 跟 hand-graded reference 在同份 dogfood 上：
- **answer_score** Pearson corr ≥ 0.6
- **source_score** Pearson corr ≥ 0.7（source_score 較好驗，binary citation valid/invalid）

---

## Phase 2 — Template + Runbook（v0.4.0，10 天）

**Scope**：+2 skill → 累計 **5**。

### 交付物

| Skill | 主要模組 |
|---|---|
| `legal-document-draft` | SKILL.md / 4 mode protocols（privacy / tos / dpa / nda）/ `assets/template-{privacy,tos,dpa,nda}.md`（含 GDPR + 個資法 2025/11 hardcode）/ `checklists/compliance-{pdpc,gdpr}.md` / 跟 `.legal-toolkit/config.yml` profile 整合（公司資訊不重問）|
| `legal-incident-response` | SKILL.md / protocols/{detect,analyze,contain,recover}.md（NIST SP 800-61 r3）/ `assets/template-{pdpc-notification,authority-reply,breach-remedy}.md` / 72hr timer 機制（Claude Code mode 顯示倒數；Cowork mode 用 deadline marker）|
| Router 更新 | `using-legal-toolkit` 識別表 active 標記 + Q2/Q3 dispatch path |

### Quality gate

- draft privacy policy 跑 PDPC 2025/11 checklist ≥ 90% pass
- IR 個資外洩演練從 trigger 到輸出 PDPC 通報文 < 30 秒
- 兩個 skill 都正確讀 `.legal-toolkit/config.yml` profile 不重問

---

## Phase 3 — IRAC cluster（v0.5.0，8-12 天）

**Scope**：+2 skill → 累計 **7**。

### 交付物

| Skill | 主要模組 |
|---|---|
| `legal-issue-spot` | SKILL.md / protocols/{parse-facts,timeline,spot-issues,subsumption,counterfactual,risk-grade}.md / `references/{請求權基礎-民法.md, 構成要件-勞動.md, 構成要件-個資.md}` / `assets/output-schema-issue-matrix.json` |
| `legal-research` | SKILL.md / protocols/{plan,iterative-search,triangulate,cite}.md / Agent 能力（plan-adapt-interact）/ `scripts/fetch_{moj,judicial,authority}.py`（全國法規 / 司法院 / 主管機關 RSS）/ document-level citation 強制 |
| Router 更新 | Q4 dispatch path（fact-driven → issue-spot / 查法源 → research） |

### Quality gate

- issue-spot 拿 5 個已知 case fact pattern 跑出 issue 矩陣 + 構成要件涵攝結論跟資深法務 hand-graded 70% 對齊
- research 對 5 個法律問題跑 iterative search 三角驗證後，引用 ≥ 8 個有效 source 且 source 跟 conclusion 有 supporting relationship

---

## Phase 4 — Tracker cluster（v0.6.0，10 天）

**Scope**：+2 skill → 累計 **9**。

### 交付物

| Skill | 主要模組 |
|---|---|
| `legal-contract-tracker` | SKILL.md / `scripts/{extract_metadata.py, build_db.py, schedule_alerts.py}` / SQLite or YAML 本機 DB / `assets/output-schema-{upcoming-deadlines,obligations-status}.json` / 自動續約日 / 終止 notice / obligations due / 價格調整觸發點 alert |
| `legal-regulation-watch` | SKILL.md / Agent 能力 / `scripts/{rss_poll.py, summarize.py, impact_assess.py}` / 監看 PDPC / 勞動部 / 立院 / 金管會 / 證交所 / cross-ref playbook 變動建議（呼叫 author revise）|
| Router 更新 | Q5 dispatch path |

### Quality gate

- contract-tracker 對 10 份歷史合約 metadata 抽取 accuracy ≥ 85%
- regulation-watch 跑 30 天 RSS poll，false-positive alert（無關變動）< 20%

---

## Phase 4.5 — 上市櫃 Compliance Prerequisite Research（10-15 天，可從 Phase 2 後 parallel）

> ⚠️ **Phase 5 BLOCKER** — design note §9 + research outline `<obsidian-vault>/research/2026-05-09 上市櫃 in-house Compliance 工作流深度研究——大綱與議題清單.md` 已寫成，70-100 工時。

**Scope**：寫獨立 research note（**不**寫 skill 程式），動工後才能 unblock Phase 5。

### 交付物

| 模組 | 內容 |
|---|---|
| Primary interview | 3-5 位上市櫃 in-house GC 訪談（議題：股東會 vs 董事會差別 / 重大訊息揭露決策樹 / 配合 DD 三類場景）|
| Research note | `2026-05-XX 上市櫃 in-house Compliance 工作流深度研究.md`（1500-2000 行，10 個必答核心問題）|
| Sub-research | 重大訊息揭露三層 decision tree + 案例集 / 個資法 2025/11 對 governance template 影響 |

### Quality gate

10 個核心問題每個都有 ≥ 2 個 primary source（GC 訪談 or 公開揭露案例 or 主管機關函釋）+ confidence MEDIUM 以上。

---

## Phase 5 — Compliance cluster（v0.9.0，10-15 天）

**Scope**：+2 skill → 累計 **11**（complete）。

**前置條件**：Phase 4.5 research note 完成。

### 交付物

| Skill | 主要模組 |
|---|---|
| `legal-corporate-governance` | SKILL.md / 3 mode protocols（股東會 / 董事會 / 重大訊息）/ `assets/checklist-{shareholders-meeting,board-meeting,material-disclosure}.md` / `assets/template-{議事手冊,議案模板,揭露文模板}.md` / 公司法 §172 / §192 / 證交法 §36 / TWSE 處理程序 hardcode / 跟 regulation-watch hook（規範變動 → 自動 flag template 更新）|
| `legal-dd-quickscan` | SKILL.md / 3 scenario（IPO / 配合併購 / 配合投資 DD）/ 30-50 項 checklist / 6 大領域 scan（公司結構 / 合約 portfolio / 勞動 / IP / 訴訟 / 稅務內控）/ `assets/output-schema-dd-findings.json` |
| Router 更新 | Q6 dispatch path active |

### Quality gate

- corporate-governance 跑一場真實股東會議事手冊 → 公司法 §172 checklist 100% pass
- dd-quickscan 對 1 家上市櫃公司資訊跑 IPO 場景 → 跟外部律師 DD report 30 項對照 ≥ 25 項一致

---

## Phase 6 — 治理機制（v1.0.0 GA，持續）

**Scope**：不新增 skill，補長期維運機制。

### 交付物

| 模組 | 內容 |
|---|---|
| Drift detection | `scripts/drift_check.py` — 對歷史合約 retro 跑當前 playbook，計算 deviation 數變化趨勢；季度自動跑 |
| Annual reminder | playbook entry `last_updated` > 180 天時 contract-review session start 強制 warn |
| Cross-playbook benchmark | `scripts/benchmark.py` — 個人 playbook vs WorldCC 2024 industry baseline + SpotDraft + ContractKen 對照 |
| Multi-playbook inheritance（v2 schema 預留實作）| 個人 + 公司 + 客戶律所三層 inheritance；schema 已預留 |
| CI gate | drift between bundled fallback / disclaimer / escalation override 三 skill 內容 byte-identical check |
| Docs polish | 完整 3-lang README rewrite / case study × 5 / migration guide / FAQ |

### GA criteria

- 11 skill 全 dogfood pass rate ≥ 80%
- drift detection 抓出 ≥ 1 個真實 stale entry
- marketplace metadata 完整（plugin.json + marketplace.json + 3 lang README）
- 至少 3 個外部 user 跑過完整 flow 回饋

---

## Critical Path & Dependencies

```
                                       ┌──────────────────────┐
                                       │ Phase 4.5 Research   │  parallel
                                       │ (上市櫃 GC interview)│  可從 P2 後起跑
                                       └─────────┬────────────┘
                                                 ↓
P1 (MVP) ─→ P1.5 (DSL) ─→ P1.6 (Eval) ─→ P2 ─→ P3 ─→ P4 ─→ P5 ─→ P6 (GA)
   3 skill    +baseline    +rubric      +2     +2     +2     +2    polish
   8-12d      5d           3-5d         10d    8-12d  10d    10-15d ongoing
```

### 關鍵依賴

- **P1.5 必 after P1**：DSL refactor 需要 working shell
- **P1.6 必 after P1.5**：rubric 需要穩定 schema 才能評
- **P2-P4 之間**理論可平行但建議接力（context switching 成本）
- **P5 必 after P4.5 Research**：design note §9 BLOCKER
- **P6 必 after P5**：drift detection 對 sparse playbook 沒意義

---

## 版本策略

| 版本 | 觸發點 | 對使用者意義 |
|---|---|---|
| v0.1.0 | Phase 1 ship | 「能用，但 playbook 你要自己寫」cold-start fallback 4 條當 demo |
| v0.2.0 | Phase 1.5 ship | 「有 8 條 baseline + ABAC + validator」 |
| v0.3.0 | Phase 1.6 ship | 「我可以自評跟你 hand-grade 對齊」 |
| v0.4.0 | Phase 2 ship | 「合約 + 起草 + 應變」 |
| v0.5.0 | Phase 3 ship | 「+ 諮詢 + 研究」 |
| v0.6.0 | Phase 4 ship | 「+ lifecycle + 法規追蹤」 |
| v0.9.0 | Phase 5 ship | 「+ 公司治理 + DD」(complete features) |
| v1.0.0 | Phase 6 GA | 「全 11 skill + 治理機制 + 3-user 真實驗證」 |

**Semver semantics**：Phase 1.X 內微調 = patch；新 skill = minor bump；schema breaking 在升 v1.0.0 前不算 breaking（pre-GA）。

---

## Risk Callouts

| Risk | 影響 | Mitigation |
|---|---|---|
| Phase 4.5 上市櫃 GC primary interview 約不到人 | Phase 5 永遠 blocked | 用次佳 source（公開揭露案例 + 法律期刊 + GC 公開演講 transcript）退而求其次；接受 confidence LOW 動工 + 後續補訪談 |
| Phase 1.6 rubric Pearson corr 跑不到 0.6 | 無法定量驗 contract-review 品質 → Phase 2-5 都是「感覺對」| 先 ship MVP；rubric 跟 dogfood corpus 邊用邊加，3-5 輪迭代後通常會 converge |
| 個資法 2025/11 新制條文細節未 lock | draft / IR / DPA playbook 都受影響 | Phase 2 動工前再 verify 一次主管機關函釋；draft template 設成可配置欄位 |
| LLM 對中文 instruction following 在 long pipeline 跳步 | contract-review 七層 L1-L7 跑不完整 | 英文骨架 + Q-B 雛形 (ii) 動工後 5 份合約 dogfood A/B 驗證；跳步 > 20% 就回頭把 SKILL.md 寫更英文化 |
| Phase 4 regulation-watch RSS 來源不穩 | false-positive alert 過多 | v1 用 pull-based polling + LLM 去重，避免 push subscription 依賴；v2 才考慮 connector |
| `escalate_to` bundled fallback 佔位符使用者懶得改 | escalation.md 永遠含「[請編輯]」字串 → disclaimer 失效 | Phase 1.6 rubric 加 binary check「escalate_to 是否含 [請編輯]」，failed_criteria 列出來壓 user |

---

## 估時 summary

| 模式 | 估時 |
|---|---|
| Focused mode（每天 6-8 小時專注） | **~60-80 工作天 = 3-4 個月** |
| Part-time（每週 10-15 小時） | **~6-8 個月** |
| Phase 4.5 平行 | 可省 10-15 天 → 約 1.5-2 週 |

---

## 明確排除（不會做的，design note §9）

- ❌ 訴訟策略 / 複雜談判
- ❌ General legal assistant
- ❌ Word add-in
- ❌ 證交所 / 金管會系統整合 / e-mail 打通
- ❌ 收費 / SLA 化變成 service（保持「免費工具」定位 → 不踩律師法 §48）

---

## 相關文件

- **Design note (SoT)**：`<obsidian-vault>/research/2026-05-09 法務 Agent Skill (legal-toolkit) 整體架構與執行流程設計.md`（1344 行）
- **Source research**：
  - `2026-05-07 法務工作流與思考方法論——Agent Skill 設計研究.md`（1570 行）
  - `2026-05-07 Harvey.ai 法務 AI 產品方法論深度研究.md`（586 行）
  - `2026-05-09 法務 Contract Playbook 深度研究——從 BigLaw 到 Agent Skill 的設計原語.md`（1605 行）
- **Phase 5 prerequisite research outline**：`<obsidian-vault>/research/2026-05-09 上市櫃 in-house Compliance 工作流深度研究——大綱與議題清單.md`
- **Repo convention**：`monkey-skills/CLAUDE.md`（skill folder structure / two-layer spec / quality gates）
