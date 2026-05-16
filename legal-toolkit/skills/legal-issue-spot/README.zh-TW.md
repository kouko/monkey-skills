# legal-issue-spot

Read this in: [English](README.md) | [日本語](README.ja.md) | **繁體中文**

![version](https://img.shields.io/badge/version-0.1.0-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![phase](https://img.shields.io/badge/phase-3_SP3--a-orange)

> ⚠️ **本工具不是律師意見。** 本工具為免費 open-source utility，非律師事務所、亦非執業律師。輸出為 法律意見，僅供 in-house 法務 內部參考；涉及刑事 exposure / 主管機關 應對 / 重大經營判斷的案件，請務必交由執業律師處理。每份輸出皆會附上 §6.3 Mandatory Disclaimer footer（詳下）。

台灣 in-house 法務 IRAC 議題盤點 (issue-spotting) skill。讀取 business-language 的 fact pattern（例：「我們想做 X，能不能做？」），產出 議題矩陣 (issue 矩陣) + 逐要件 構成要件 涵攝 + 反事實 + 風險分級 (🔴/🟡/🟢) + 律師 escalation 建議。Pure-LLM workflow；不外取資料；不依賴 `legal-playbook/profile.yml`。

## 什麼時候用

- 業務端問「我們想做 X，能不能做？」— product launch / 新功能 / 新 vendor / 新 SOP 上線前的 legal pre-check
- 跨 民法 / 勞基法 / 個資法 的 multi-statute fact pattern — 一個事實同時觸發多個 statutory issue
- 需要逐要件結構化的 構成要件 涵攝 + 風險分級 + 律師 escalation 建議，光是 yes/no 不夠

## 什麼時候不用

- **法條原文 lookup**（「§227 條文是什麼？」）→ 改用 `legal-research`（Phase 3 SP3-b v0.5.2）
- **合約 review**（既有合約檔案或貼上的條文）→ 改用 `legal-contract-review`
- **書面起草**（通知函 / 警示函 / 終止合約信）→ 改用 `legal-document-draft`
- **事後 incident response**（已發生外洩 / 已收到 主管機關 來文 / 對方已違約）→ 改用 `legal-incident-response`

## Input format

- **Required at session**：fact pattern 自由描述（1-3 段 business-language 描述，例：「我們想送一份員工生日禮物給客戶聯絡人，能不能做？」）
- **無結構 schema** — Step 1 由 `protocols/parse-facts.md` 抽出 當事人 / 行為 / 時間 / 金額 / 標的
- **不依賴 `profile.yml`** — 分析是 fact-pattern-driven，不是 company-identity-driven（router Q4-fact 跳過其他 v0.4.x skill 的 profile prerequisite check）

## Output format

每次 session 寫入 `<cwd>/legal-outputs/<YYYY-MM-DD-HHmm>-issue-spot/`：

| File | Audience | Sections |
|---|---|---|
| `issues.md` | 法務 / GC / 內部簽核 | §事實摘要 / §時間軸 / §Issue 矩陣 / §構成要件涵攝 / §反事實 / §風險分級 / §Disclaimer |
| `business.md` | 非法務（CEO / BD / 業務 / PM）| §TL;DR / §可以做的部分 / §不能做的部分 / §注意點 / §風險分級 / §Disclaimer（+ §建議下一步 conditional + §Escalation conditional）|

Schema validation：兩個檔都有 JSON Schema contract（`assets/output-schema-issues.json` + `assets/output-schema-business.json`），由 `scripts/grade_issue_spot.py` 消費。

## Cross-skill handoff

當 subsumption 表中出現 **≥ 1 ⚠️**（任一信心不足的要件），`business.md` 末尾會加上 `§建議下一步` block，列出 `/legal-research` 用的具體 query string：

```markdown
## §建議下一步

⚠️ 以下構成要件信心不足，建議跑 research 釐清：

- §227 不完全給付的 carve-out 認定
  → `/legal-research --query="不完全給付 §227 carve-out 民國 110 年後判決趨勢"`
```

這是 **soft handoff** — user 自己 copy command 去跑 `/legal-research`；不會 auto-dispatch（Q8 lock：user 控管 token budget）。反向（research → issue-spot）刻意不做；router Q4 會接住誤 routing 的 query。

## §6.3 Disclaimer footer

每份輸出檔末尾都必須附上 §6.3 Disclaimer footer（canonical 文字在 `protocols/risk-grade.md`）。內容涵蓋：AI 工具 attribution / 非正式法律意見 / 現行台灣法 scope / 訴訟、簽約、刑責、cross-border、高風險決策請洽 律師。Grader 會 grep canonical sentinel substring；缺 footer → exit 1（FAIL）。本 skill 產出 法律意見 — disclaimer 是 mandatory，不是 optional。

當 風險分級 = 🔴 或 §構成要件涵攝 出現 ≥ 2 ⚠️ 時，`business.md §Escalation` 同樣 hard-wired（§6.4 Escalation Override）— LLM 不能 soften 也不能 skip 律師 建議。

## 參考

- 完整 skill 說明：[`SKILL.md`](SKILL.md)
- Design spec：[`docs/superpowers/specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md`](../../../docs/superpowers/specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md) §5
- Plugin spec：[`legal-toolkit/PRODUCT-SPEC.md`](../../PRODUCT-SPEC.md) + [`legal-toolkit/TECH-SPEC.md`](../../TECH-SPEC.md)
- ROADMAP：[`legal-toolkit/ROADMAP.md`](../../ROADMAP.md)
