# legal-contract-review

> legal-toolkit 的主戰場。七層 schema-driven 合約審查（Stark + Adams + Burnham + 台灣 overlay）、playbook-driven L7 評斷、disclaimer-driven 輸出。

Read this in: [English](README.md) | [日本語](README.ja.md) | **繁體中文**

## 這個 skill 做什麼

對合約跑決定性的七層 pipeline，產出**結構化 Markdown 6 份檔案**：

| 檔案 | 內容 |
|---|---|
| `issues.md` | Findings 矩陣 + business-issue 標籤 + playbook trace |
| `redline.md` | 替代條款文字（從 playbook body 來 或 LLM 生成）|
| `memo-legal.md` | 完整 CRAC memo + 法條 / 判例 citation |
| `memo-business.md` | 非法務人員看的 Why/What/What-if 三句 |
| `escalation.md` | 誰簽核什麼 + trigger 條件 |
| `self-grade.md` | Harvey dual-score（answer + source）+ failed criteria |

每份輸出檔尾含 Mandatory Disclaimer；高風險 findings 在檔頭額外加 Escalation Override 紅字 banner。

## Pipeline

```
INPUT （合約 + type + jurisdiction + deal_context + mode + stance）
   ↓
LOAD PLAYBOOK （user legal-playbook/ 或 bundled fallback）
   ↓
[只在台灣] L0a 強行/任意 → L0b 定型化契約 §247-1
   ↓
L1 Expectations → L2 Anatomy → L3 Categorize → L4 Functional tier → L5 Domain priority → L6 Cycle
   ↓
[只在台灣] L6.5 六準則契約解釋
   ↓
L7 Evaluate against playbook （ABAC pre-filter + LLM compare）
   ↓
SELF-GRADE （Harvey dual-score：answer / source，永不合併）
   ↓
WRITE 6 outputs → legal-outputs/<timestamp>-<contract-name>/
```

每層 protocol 檔在 [`protocols/`](protocols/) 內，各自獨立 instruction。

## 三 mode

| Mode | 跑的層 | 主推輸出 |
|---|---|---|
| `review`（預設）| L0a → L7 + L6.5（完整）| 6 份完整輸出 |
| `redline` | L1-L7 + L6.5 | 替代條款文字強化 |
| `nda` | bundled NDA template + L4-L7 | issues + redline + memo-legal（3 份）|

## Cold-start fallback

使用者沒有 `legal-playbook/` 時 skill 不會 abort。L7 從 plugin 內的 4 條 bundled fallback baseline 讀 ([`assets/`](assets/))：

- `baseline-fallback-confidentiality.md`
- `baseline-fallback-governing-law-jurisdiction.md`
- `baseline-fallback-auto-renewal.md`
- `baseline-fallback-termination-and-survival.md`

從 bundled fallback 產生的 finding 帶 banner（提示客製化）。`escalate_to` 欄位 ship 成佔位字串（`[請編輯為你公司的角色：...]`）；L7 偵測到會在 escalation.md 加 warning callout。

非這 4 條的 clause 在 L7 落到 **advisory mode**：標 `source_type: advisory`，建議跑 `legal-playbook-author extend <clause-id>` 客製化。

Phase 1.5 會把 bundled fallback 擴到 8 條（加上 LoL / Indemnification / DPA / IP-Assignment 的 variant-folder 版）。

## Inputs

| 欄位 | 必填 | 預設 |
|---|---|---|
| `contract_path` | 是 | — |
| `contract_type` | 否 | 自動偵測 |
| `jurisdiction` | 否 | `TW` |
| `deal_context` | 否 | 最大努力 extract |
| `mode` | 否 | `review` |
| `stance` | 否 | `ours` |

## 何時用

- 合約 sign / 反提案 前的 review
- 來回 redline 議價
- Portfolio consistency 對齊（每份合約都對自己 playbook）
- 給律師討論用的初稿 memo

## 何時不用

- 想**建立** playbook 條目 → `/legal-playbook-author`
- 想**從零起草** privacy policy / ToS → （Phase 2）`legal-document-draft`
- Fact-pattern 諮詢（「能不能做 X？」）→ （Phase 3）`legal-issue-spot`
- 訴訟策略 / 複雜談判 tactics — **設計上 out of scope**

## 輸出結構

```
<cwd>/legal-outputs/<YYYY-MM-DD>-<contract-name-slugified>/
├── issues.md              # findings 矩陣
├── redline.md             # 替代條款
├── memo-legal.md          # CRAC + citation
├── memo-business.md       # Why/What/What-if
├── escalation.md          # 誰簽核
└── self-grade.md          # answer + source dual-score
```

每份檔尾：Mandatory Disclaimer（從 `assets/disclaimer-block.md`）
高風險檔頭：Escalation Override 紅字 banner（從 `assets/escalation-override.md`）

## External-share mode

`--external-share` flag 從 `issues.md` / `memo-legal.md` / `escalation.md` strip 掉 playbook ID（替換為「依本公司紅線政策」）。Override 紅字 banner **絕對不 strip**。

## Reference

- SKILL.md（instruction）：[`SKILL.md`](SKILL.md)
- 各層 protocol：[`protocols/`](protocols/)
- Output schema：[`assets/output-schema-*.json`](assets/)
- Bundled fallback：[`assets/baseline-fallback-*.md`](assets/)
- Self-grade rubric：[`checklists/answer-criteria.md`](checklists/answer-criteria.md) + [`source-criteria.md`](checklists/source-criteria.md)
- Domain reference：[`references/`](references/)（Stark 7 concepts / Adams 10 categories / 各 contract type priority）
- Plugin spec：[`PRODUCT-SPEC.md`](../../PRODUCT-SPEC.md) / [`TECH-SPEC.md`](../../TECH-SPEC.md)
- Roadmap：[`ROADMAP.md`](../../ROADMAP.md)

## License

MIT — 詳見 monorepo root 的 [LICENSE](../../../LICENSE)。
