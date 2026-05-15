# legal-toolkit

> 台灣 SME → 上市櫃 in-house 法務 toolkit — 七層 schema-driven 合約審查、playbook-driven 議價、disclaimer-driven 輸出。

Read this in: [English](README.md) | [日本語](README.ja.md) | **繁體中文**

![version](https://img.shields.io/badge/version-0.5.2-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![phase](https://img.shields.io/badge/phase-3_IRAC_(closed)-orange)

> ⚠️ **本工具不是律師意見。** 本工具為免費 open-source utility，非律師事務所、亦非執業律師。每份輸出皆含 Mandatory Disclaimer；高風險 findings 額外觸發 Escalation Override（「請諮詢執業律師」）。詳見 [§Disclaimer policy](#disclaimer-policy)。

## 做什麼

legal-toolkit 給 in-house 法務（個人 / SME / 上市櫃）一個 **markdown-first / runtime-portable** 的 workflow，處理 in-house 工時 80% 的高頻場景：**合約審查**（主戰場）、**playbook authoring**（自家公司的議價規則）、**文書起草**（隱私權政策 / 服務條款 / DPA / NDA；v0.4.0+）、**個資事故應變**（個資外洩 / 主管機關函覆 / 合約違約；v0.4.2+）、**issue spotting**（IRAC fact-pattern 分析；v0.5.0+）、**法律研究**（iterative-search + 三角驗證 + document-level citation；v0.5.2+），以及 (Phase 4-5 規劃) 合約 lifecycle 追蹤 / 法規追蹤 / 公司治理 / 配合 DD 快速 scan。

跟 BigLaw 移植版工具的三大差異：

1. **Schema-driven，不是 vibe-driven** — 合約審查跑決定性的七層 pipeline（Stark 7 contract concepts / Adams 10 language categories / Burnham 6 functional tiers）+ 台灣 jurisdiction overlay（強行/任意 規定二分 / 定型化契約 §247-1 / 六準則契約解釋）。
2. **Playbook 放在你看得到、改得到的地方** — `legal-playbook/<clause>.md` 放在 working folder visible 處，Markdown / git-trackable。不埋進 SQLite blob、不藏在 dotfile 隱藏資料夾、不放到 vendor cloud。三層擁有權：visible `legal-playbook/`（使用者擁有）+ visible `legal-outputs/`（使用者擁有）+ hidden `.legal-toolkit/`（工具 internals）。
3. **Disclaimer-driven，不硬閹割功能** — 律師法 §48 規律的是「自然人」，不是「工具」；免費 open-source utility ≠ service。把「法律意見產出」硬排除等於否定 Phase 3 計畫的 issue-spot / research 兩個 sub-skill 的存在。每份輸出加 Mandatory Disclaimer，高風險 findings 額外加 Escalation Override 紅字 banner。

## 7 個 active skill（Phase 1 MVP + Phase 2 Template/Runbook + Phase 3 IRAC 完整 ship，v0.5.2）

| Skill | 角色 |
|---|---|
| `using-legal-toolkit` | **Router** — 識別 6 cluster（Playbook / Template / Runbook / IRAC / Tracker / Compliance）的意圖並 dispatch；剩下的 Phase 4-5 sub-skill 標為 not-yet-available 並列出 cluster 選單。 |
| `legal-playbook-author` | **Cross-cluster utility** — bootstrap / extend / revise mode；產 per-clause Markdown entry，frontmatter 為決定性（`gates` / `walk_away_triggers` / `escalate_to` / `risk_default`）+ body 為 LLM-comparison（`preferred` / `fallback N` / `為什麼這條重要`）。偵測 flat clause 是否該升級為 variant-folder（用 deal_size / counterparty_type / jurisdiction 當 gate）。 |
| `legal-contract-review` | **📋 Playbook cluster — 主戰場** — 七層 pipeline + TW overlay；ABAC pre-filter 在 LLM 之前先選出 matched variant（LLM 只看到單一 variant，不讓它選）。三 mode：`review`（完整輸出）/ `redline`（聚焦替代條款文字）/ `nda`（結構簡單，跳過 L2-L3）。輸出：`legal.md` + `business.md` + `findings.json`（v0.3.4+ 整合）。 |
| `legal-document-draft` | **📝 Template cluster（v0.4.0+）** — 4 mode：隱私權政策 / 服務條款 / DPA / NDA。Skeleton-and-LLM-fill template，pin 在現行台灣法（Path A 紀律）。2-file output（`<doc-type>.md` 公開可發佈 + `compliance.md` 法務 review）。Hand-curated per-mode 合規 checklist + 法條引用（個資法 / 民法 / 消保法 / 公平交易法）。 |
| `legal-incident-response` | **🚨 Runbook cluster（v0.4.2+）** — 3-path 分流（個資外洩 / 主管機關函覆 / 合約違約）+ auto-classify + confirm path routing。Audience-shaped 2-file output（`legal.md` + `business.md`）+ optional `handoff-context.json`（合約違約 path 把案件 handoff 給 `legal-contract-review`）。ISO 8601 timeline section（未確定 anchor 用 ⏳ marker）。 |
| `legal-issue-spot` | **🔍 IRAC cluster, sub-skill 1 of 2（v0.5.0+）** — pure-LLM IRAC 議題識別。從 business-language fact pattern（「我們想做 X，能不能做？」）產 issue 矩陣 + per-element 構成要件 涵攝 + 反事實 counterfactual + 🔴/🟡/🟢 風險分級 + escalation 建議。2-file output（`issues.md` 給 法務 / `business.md` 給 業務 + escalation 建議）。無外部 fetch、無 profile.yml 依賴、無 playbook coupling — 跟 `legal-contract-review` 正交。⚠️ 低信心 subsumption 偵測時，soft handoff 到 `/legal-research` 並附具體 query string。 |
| `legal-research` | **🔍 IRAC cluster, sub-skill 2 of 2（v0.5.2+）** — 法源 citation research，採 **Agent 抽象**（plan-adapt-interact 半互動 — plan 先行，使用者 Y/n 確認後才進入 autonomous loop）。**只走 WebFetch**（不用 Python scraper；fallback chain = 一次 source URL → Google cache → archive.org Wayback）。4-protocol pipeline（plan → iterative-search → triangulate → cite）。Loop 上限 ≤ 5 輪 OR ≤ 30 次 fetch；早期收斂條件 ≥ 8 個 source AND ≥ 2 種法源類型；`forced_stop` 會在輸出標 ⚠️ marker。4 檔 output（`plan.md` / `state.json` / `research-memo.md` 給 法務 / `executive-summary.md` 給 業務）+ Harvey 風格 document-level citation manifest（3-line shape：URL + 標題 + 取得日期）。§6.4 Escalation Override 觸發條件擴及 `forced_stop` / 刑事 / 訴訟 / 跨境 / 重大金額。 |

Phase 4-5 再上 4 個 skill — v0.1.0 → v1.0.0 完整 plan / 版本策略 / critical path / risk callouts 見 **[ROADMAP.md](ROADMAP.md)**。

## Cold-start fallback（沒自訂 playbook 也能用）

第一次 install：working folder 還沒有 `legal-playbook/`。工具仍然能跑 — `legal-contract-review` 從 plugin 內讀 **4 條 bundled fallback baseline clause**：

| clause_id | Layout |
|---|---|
| `confidentiality` | flat |
| `governing-law-jurisdiction` | flat |
| `auto-renewal` | flat |
| `termination-and-survival` | flat |

每個由 bundled clause 產生的 finding 帶 banner：`⚠️ 使用 bundled fallback baseline — 建議跑 legal-playbook-author 客製化你公司的紅線`。`escalate_to` 欄位 ship 成佔位字串（`[請編輯為你公司的角色：法務主管 / GC / 部門主管]`）；review 時偵測到佔位符會 emit warning，避免使用者把帶佔位符的輸出當最終決定。

跑 `legal-playbook-author bootstrap` 可從 bundled fallback 遷移到你自家的客製化 playbook。**v0.2.0 (Phase 1.5)** 把 bundled baseline 擴到 8 條 — 加 variant-folder `limitation-of-liability`（small/mid/large-deal）/ `indemnification`（small/mid/large-deal）/ `data-protection-dpa`（tw-only/gdpr-overlay/cross-border）+ flat `ip-assignment-and-license`。跑 `seed_baseline.py` 解壓 8-clause tarball 到 working folder。

## Playbook layout（議價判斷的 Source of Truth）

```
<working folder>/
├── legal-playbook/                    ← visible，使用者擁有
│   ├── README.md                      # auto-seed 寫進去的「怎麼維護你的 playbook」
│   ├── confidentiality.md             # flat clause
│   ├── governing-law-jurisdiction.md
│   ├── limitation-of-liability/       ← variant-folder（deal-size keyed）
│   │   ├── _clause.md
│   │   ├── small-deal.md              # gates: deal_size < 100K USD
│   │   ├── mid-deal.md                # gates: 100K-1M USD
│   │   └── large-deal.md              # gates: >= 1M USD
│   └── data-protection-dpa/           ← variant-folder（jurisdiction keyed）
│       ├── _clause.md
│       ├── tw-only.md
│       ├── gdpr-overlay.md
│       └── cross-border.md
│
├── legal-outputs/                     ← visible，使用者擁有（per-run review 結果）
│   └── 2026-05-11-acme-saas-msa/
│       ├── issues.md
│       ├── redline.md
│       ├── memo-legal.md
│       ├── memo-business.md
│       ├── escalation.md
│       └── self-grade.md
│
└── .legal-toolkit/                    ← hidden，工具擁有
    ├── config.yml                     # profile + global_rules
    ├── schema.json
    └── cache/
```

Discovery 順序：`<cwd>` → 5 層 ancestors → BFS 深度 5 → bundled fallback。`legal-outputs/` 跟 `.legal-toolkit/` 加進 `.gitignore`；`legal-playbook/` 要 track（公司的議價知識財產）。

## 合約審查 pipeline

```
INPUT （合約 path + contract_type + jurisdiction + deal_context）
   ↓
LOAD PLAYBOOK  （scan legal-playbook/ → 建 index；validate schema；last_updated > 180 天 staleness warning）
   ↓
[只在台灣]  L0a 強行/任意 規定二分  →  L0b 定型化契約 §247-1 + 消保法 §11-1
   ↓
L1  Expectations           bundled template ∪ playbook_index keys
L2  Anatomy mapping        preamble / definitions / action / endgame / boilerplate
L3  Categorize             Stark 7 contract concepts + Adams 10 language categories
L4  Functional tier        money / risk / control / standards / endgame
L5  Domain priority        bundled[contract_type] + playbook augment
L6  Cycle / cross-ref      if-breach branch；definitions 重讀；missing-items flag（gaps == 0 AND cycle >= 2 才出 loop）
   ↓
[只在台灣]  L6.5  六準則契約解釋  （當事人目的 → 習慣 → 任意法規 → 誠信原則）
   ↓
L7  Evaluate Against Playbook  （per-clause）
       ├── clause.id 在 user playbook_index？        → user variant 評斷
       ├── clause.id 在 bundled fallback？           → bundled fallback + banner
       └── 都沒有？                                    → advisory mode + 建議跑 playbook-author extend
   ↓
   每條 matched entry：
   ABAC pre-filter（gates vs deal_context）→ 單一 matched variant
   walk_away_trigger LLM judge → 🔴 walk / 🟢 preferred / 🟡 fallback / 🔴 worse
   LLM 不確定？ → 用 frontmatter risk_default
   ↓
SELF-GRADE  （Harvey dual-score：answer_score / source_score — 永不合併；all-pass binary）
   ↓
OUTPUT  6 份檔案 → legal-outputs/<timestamp>-<contract-name>/
   + Mandatory Disclaimer （每份輸出檔尾）
   + Escalation Override （高風險才有，檔頭紅字 banner）
```

## Disclaimer policy

每份輸出檔尾強制加 Mandatory Disclaimer：

- 本工具非律師事務所、亦非執業律師
- 本工具為免費 open-source 工具，**非服務**（無收費 / 無 SLA / 無 advisor-client 關係）
- 輸出僅供使用者**內部決策參考**，不構成法律意見
- 涉及訴訟 / 刑責 / 重大商業決策時，**請諮詢執業律師**
- 引用之法條 / 判例 / 函釋請以**全國法規資料庫 / 司法院判決系統 / 主管機關官網**為準

高風險 findings — `risk_default: red` / `walk_away_triggered: true` / `confidence < 0.7` / 涉及刑責 / `deal_size > escalation_threshold` — 會在受影響的輸出檔頭額外加 **Escalation Override** 紅字 banner，明確標示*「請諮詢執業律師」*。

業界 context：Harvey / Spellbook / LawGeex / Lawsnote / 律果 LegalSign.ai 全部採 disclaimer-driven 設計；**沒有任何一家 vendor 硬排除「法律意見產出」**。律師法 §48 規律的是自然人從事律師業務（訴訟代理 / 以律師名義對外 / 收費撰寫法律文書供對外使用）— 不及於免費 open-source utility，也不及於 in-house 法務的內部 advisory 工作。

## Install

```bash
# 在 Claude Code，已 enable monkey-skills marketplace
/plugin install legal-toolkit@monkey-skills
```

Plugin 是 self-contained — bundled fallback baseline + protocols + schemas 全在 plugin 內。Toolkit 本機 FS-first，完全 offline 可跑，無外部 API 呼叫。在 Claude Code CLI 驗過；Cowork「Work in a Folder」mount 也支援，但 FUSE pre-existing-file 行為可能需要首次 onboarding step（Phase 2 補完整 doc）。

## 使用

```
/using-legal-toolkit
```

常見三種 shape：

| Shape | Trigger | Path |
|---|---|---|
| **Shape A** — 審查一份合約 | 「review 這份 SaaS MSA 看跟 playbook 對不對」/「redline 這份 NDA」 | router → contract-review → 6 份輸出 |
| **Shape B** — 建 / 改 playbook | 「加一條 auto-renewal 的紅線」/「LoL enterprise tier 的 fallback 要改」 | router → playbook-author（extend / revise mode）|
| **Shape C** — 第一次裝 | 「剛裝好，下一步幹嘛？」 | router → playbook-author（bootstrap mode）→ 提供「從 bundled fallback seed」or「從零 interview」二選一 |

意圖明確時也可直接呼叫 skill（例如針對合約 path 跑 `/legal-contract-review`）。

## Language policy（cross-cutting）

**英文骨架 + zh-TW 血肉**（design phase 鎖定，TECH-SPEC 寫進去）：

- **英文**：SKILL.md / protocols / scripts / JSON schema keys — LLM instruction-following 在英文顯著較強；對齊 Anthropic 官方 skill convention；跨 runtime portability 較高。
- **zh-TW（原文保留）**：法條引用（民法 §247-1 / 個資法 §21 / 勞基法 §9-1）/ 台灣判例 / baseline playbook body / user-facing output。
- **Bilingual triggers**：frontmatter `description` 同時列 EN + zh-TW keyword — 命中率上升，false-positive routing 不會增加。
- **不翻譯的東西**：法條原文（民法 §247-1 翻成 "unconscionability" 會讓 LLM 抓錯到美國 doctrine）、Stark / Adams / Burnham terminology（專有名詞，翻了 citation lookup 會壞）。

## Status

- **Version**：0.5.2 (2026-05-15)
- **Stability**：7 個 active skill（Phase 1 MVP + Phase 2 Template/Runbook + Phase 3 IRAC 完整 ship）
- **Phase**：3 SP3-b（legal-research ship）— IRAC cluster 完整 active（issue-spot v0.5.0 + research v0.5.2）；Phase 4 Tracker（v0.6.0）為下一站；v0.1.0 → v1.0.0 plan 見 [ROADMAP.md](ROADMAP.md)
- **Test suite**：259+ tests（schema / discover / validate / detect_conflicts / abac_filter / build_baseline / seed_baseline / self_grade / grade_draft / grade_response / grade_issue_spot / grade_research / canonical drift 4-grader bank）— `uv run --with jsonschema --with pyyaml --with pytest` 全綠
- **License**：MIT (plugin code)

## Reference

- **ROADMAP**：[`ROADMAP.md`](ROADMAP.md) — 7-phase plan、版本策略、risk callouts
- **PRODUCT-SPEC**：(Step B，pending) — 商業 + 設計方向
- **TECH-SPEC**：(Step B，pending) — 模組 + 資料流 + 介面合約
- **Design note (SoT)**：`<obsidian-vault>/research/2026-05-09 法務 Agent Skill (legal-toolkit) 整體架構與執行流程設計.md`（1344 行、38+ locked decision）

## Contributing

PR 歡迎透過 `https://github.com/kouko/monkey-skills`。Conventions：

- **Skill structure** 遵守 monkey-skills convention：flat skill 目錄，`<subfolder>/` 內不能再開 subfolder。詳細 hook enforcement 見 repo `CLAUDE.md`。
- **Commit prefix**：`feat(legal-toolkit)` / `fix(legal-toolkit)` / `docs(legal-toolkit)` / `chore(legal-toolkit)` / `refactor(legal-toolkit)` / `test(legal-toolkit)`。
- **三語 skill README（en/ja/zh-TW）強制要求** — 依 monkey-skills PR #150，per-skill README.md 跟本 plugin-level README 都適用。
- **Disclaimer block** — 每份輸出 footer 的 disclaimer 文字必須在 ship 它的 3 個 skill 之間 byte-identical（Phase 6 補 CI gate）。

## License

MIT — 詳見 repository root 的 [LICENSE](../LICENSE)。
