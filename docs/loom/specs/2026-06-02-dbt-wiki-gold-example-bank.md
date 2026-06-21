# Brief — dbt-wiki `examples/` gold question→SQL bank（Gap B, v2.x fast-follow）

- **Date**: 2026-06-02
- **Topic**: 在 dbt-wiki 知識層之上，加一個 gold 「問題→SQL」範例庫，供 text-to-SQL skill 做 few-shot
- **Status**: brainstorming brief（探索 + 研究 + dogfood 驗證完成）→ 待簽核 → writing-plans（時機由 user 定）
- **北極星**: dbt-wiki 知識庫服務「對商業邏輯問題有效的 text-to-SQL skill」；in-domain gold 範例是研究驗證的最大缺口槓桿。

## 分層定位（2026-06-02 LOCKED）

本 brief 是**增強層 L1**，不是最小狀態。三層：

| 層 | 內容 | 狀態 |
|---|---|---|
| **最小（核心）** | v2.0 知識層 + 關係圖 + **metric 欄位卡** | 前二已 ship；**metric 欄位卡 = 最小狀態唯一未完成的一塊**（artifact-only、零 warehouse/log）|
| **增強 L1（無 log）** | 合成 + 人工 gold 範例（本 brief 的 `examples/` bank）| 設計中 |
| **增強 L2（需 log）** | log-mined 範例（Redshift 加速器）| 已驗證、可選 |

→ 完成最小狀態只剩 **metric 欄位卡**（另立 brief）。examples 整個（含合成 producer）都是增強層、可延後。

---

## Problem（Axis 1 — JTBD）

> 當 text-to-SQL skill 收到一個**商業邏輯問題**（churn / OMO 滲透率 / 合約空窗…），它需要**本專案特定的「問題→SQL」示範**做 few-shot——因為 in-domain 範例是準確度最大的可控槓桿（驗證：30 條 in-domain → +44.9pp，KaggleDBQA 26.8→71.7，[EMNLP'23 findings 944](https://aclanthology.org/2023.findings-emnlp.944.pdf)）。沒有範例庫，冷啟動的 text-to-SQL 在硬商業子集上準確度低。

## Users（Axis 2）

- **主要消費者**：（未來的）text-to-SQL skill——讀 dbt-wiki + 檢索範例做 few-shot。
- **生產者/策展者**：資料團隊（人工種子/修正）；長期靠使用累積。
- **通用性前提（關鍵）**：dbt-wiki 是給**任何** dbt 使用者的公開 plugin，**多數人沒有可查的 query log（或無權限）**→ 機制不能綁在 log 上。

## Smallest End State（Axis 3）

**設計第一前提：零 log、零 warehouse 也能運作。**

1. **`examples/` store 格式**（dbt-wiki 端，warehouse-agnostic）：每筆 = 自然語言問題 + skeleton SQL（字面值參數化）+ 用到的表/entities/metrics（連知識圖）+ verification 方式/信心 + provenance。**producer-agnostic**。
2. **Baseline producer（主路徑，零 log）**：
   - **合成 bootstrap**：LLM 從知識層（entities/metrics/concepts + 物化 metric 欄位卡 + 關係圖）生 Q→SQL。dbt-wiki 知識層豐富 → 比通用合成好。
   - **人工種子**：團隊手寫/修正少量 gold（~30 條就有大效益）。
3. **驗證（必須零 warehouse 可跑）**：sqlglot 解析有效 + **比對當前 manifest schema 有效** + **SQL2NL round-trip 等價**（NL→SQL 反譯比對，[2509.04657](https://arxiv.org/pdf/2509.04657)）。執行驗證（warehouse）為可選更強閘。
4. **檢索**：留給消費端 text-to-SQL skill（top-k 相似度，question + SQL skeleton 結構，[2410.14049](https://arxiv.org/pdf/2410.14049)）。**不在本 MVP**。

**可選加速器（非核心、機制不依賴）**：log-mining（Redshift STL，已 dogfood 驗證可行）、BI 工具定義（Looker/Tableau）、使用累積 flywheel（消費端上線後存回，長期最佳）。

## Current State Evidence

- **Forward**：dbt-wiki 4 skill（init/refresh/ingest/query）；新 `examples/` 需要一個 producer 入口（合成在 init Phase B 之後可接；人工/flywheel 是外部）。
- **Reverse/SSOT**：`skills/init/assets/SCHEMA.md` 擁有頁面格式（要加 `examples/` 頁型）；`synthesis_template.md` + SCHEMA 的 `syntheses/` 是**相關但不同**的既存 store（lineage 答案，非 gold Q→SQL）；manifest = schema-validity 真值來源；無 distribute.py（dbt-wiki 自包含）。
- **Error/edge**：SQL2NL 誤讀 → 配對毒化（靠 round-trip 閘）；LISTAGG 截斷的 log SQL（log 加速器路徑才有）；合成 SQL schema 失效（靠 manifest 比對）；迭代草稿/瑣碎 peek（靠分析形狀過濾 + canonical 選取，log 路徑才有）。
- **Data**：知識層頁（合成輸入）→ Q→SQL → 參數化 → example 頁；frontmatter 記 used-tables/metrics/verification/provenance。
- **Boundary**：**public plugin repo = 只放格式/程式碼、零資料**；`examples/`（含真實 SQL）一律落**使用者私有專案 repo** 的 `.dbt-wiki/examples/`，與 `_evidence/` 同；log-mining 是**外部 producer**、非 wiki 機制、Redshift 專屬。

## Decision

建一個 **producer-agnostic 的 `examples/` gold 範例庫**，**以「無 log」為第一前提**：dbt-wiki 端只擁有 store 格式 + 驗證契約 + 合成 producer（讀知識層，零 warehouse）；人工種子與使用累積 flywheel 補強；**log-mining / BI 定義是可選加速器，機制不依賴**。驗證走「sqlglot + manifest schema 有效 + SQL2NL round-trip」三閘（執行驗證可選）。檢索留給消費端 skill。

**不建**：把 log-mining 烤進 dbt-wiki 核心（破 warehouse-agnostic）；檢索/embedding 索引（消費端的事）；把真實 SQL 放進 public repo。

### 品質閘（correct / meaningful / faithful 三層，dogfood 推出）
- **正確**：（合成）sqlglot 有效 + manifest schema 有效；（log）跑過=免費下限 + 截斷偵測。
- **有意義**：分析形狀（JOIN/GROUP BY/CTE/業務謂詞）；去瑣碎 peek；（log）skeleton 去重取 canonical + 頻率信任分。
- **配對忠實**：SQL2NL round-trip 等價 + 分析師別名加持（dogfood：你們 SQL 內含中文業務別名 = 半 ground-truth）。
- 只有全過 → 入庫，記 verification 方式與信心。

## Alternatives Considered（Axis 4 — 已研究）

Sourcing 的四條路（產業 Example Bank + 相似度 + 強制驗證為定型，[SQLGenie ACL'25](https://aclanthology.org/2025.acl-industry.71.pdf)、[Expandable Aux KB 2411.13244](https://arxiv.org/html/2411.13244v1)）：
1. **合成 from 知識層** — 零 log/warehouse、冷啟動即用；合成<真實，需驗證。**← baseline 主路徑**
2. **人工種子** — 最高品質、零依賴；需人工。**← baseline 補強**
3. **使用累積 flywheel** — 長期最佳；冷啟動雞生蛋。**← 長期主路徑**
4. **log-mining（Redshift）** — 真實+驗證免費；Redshift 專屬+需 SYSLOG 提權+retention 短。**← 可選加速器（已 dogfood 驗證）**

**My take**：以 1+2 為「永遠能用」的 baseline、3 為長期升級、4（與 BI 定義）為可選加速器。Conditional reversal：若鎖定單一有 log 的環境（如本案 Redshift 環境）且要快速大量 bootstrap，可把 4 當主力——但**預設架構不假設 log 存在**。

## What Becomes Obsolete（Axis 5）

- 大致純加法（新 store）。需釐清 `examples/` 與既存 `syntheses/` 的關係：syntheses = 人讀的 lineage 答案；examples = 給 skill 的 few-shot Q→SQL。**建議保持分離**（不同消費者）；若日後 query skill 也存「問題→SQL」可考慮收斂。

## Out of Scope

- 檢索/embedding 索引（消費端 text-to-SQL skill）。
- log-mining 作為核心機制（僅可選外部 producer）。
- 真實 SQL 進 public repo。
- 消費端 text-to-SQL skill 本身（schema linking / 生成 / 驗證迴圈）——**另一個元件，scope 待 user 定**。

## Open Questions

1. **消費端 scope**：text-to-SQL skill 本身算這個專案嗎？（決定路線圖長度）
2. **合成品質**：知識層合成的 gold 到底夠不夠好？→ **下一個 dogfood**（用本專案知識層合成幾條，比對 log-mined 的真實版）。
3. `examples/` vs `syntheses/` 是否收斂。
4. 物化 metric 欄位卡（前置依賴）要先做，合成才能引用正確欄位。
