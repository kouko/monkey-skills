# Kaizen Skill

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

透過結構化的 6 步驟循環，
在既有流程中識別並實施小而持續的改善。

## 六個步驟

| Step | 日文 | 含義 | 關鍵動作 |
|------|------|------|---------|
| 1 | 現状把握 | 掌握現狀 | 不帶評斷地觀察 |
| 2 | 問題発見 | 發現問題 | 找出摩擦與浪費 |
| 3 | 根本原因 | 根本原因 | 不斷追問「為什麼？」直到核心 |
| 4 | 改善案 | 改善提案 | 提出最小幅度的變動 |
| 5 | 実行と検証 | 執行與驗證 | 試做並衡量結果 |
| 6 | 標準化 | 標準化 | 將其變成新的預設 |

## Method Type

Process-driven（不像 Socratic method 是 dialogue-driven）。
agent 依序帶領使用者走過每個步驟，
確保改善維持在小、可逆、可衡量的範圍。

關鍵原則：Kaizen 是持續性的小改善，
不是一次性的大轉型。如果改善案感覺像革命，那就太大了。

## 七種浪費（Muda）

改編自 Toyota Production System，套用於知識工作：

| 浪費類型 | 日文 | 知識工作範例 |
|----------|------|----------------------|
| Overproduction | 作りすぎ | 做出沒人要求的 feature |
| Waiting | 待ち | 卡在 code review、審核排隊 |
| Transportation | 運搬 | 在工具間搬資料、手動轉移 |
| Over-processing | 加工 | 不必要的步驟、gold-plating |
| Inventory | 在庫 | 未處理的 backlog、未讀通知 |
| Motion | 動作 | context switching、工具切換 |
| Defects | 不良 | bug、返工、溝通失誤 |

## SKILL.md 中的範例

| 範例 | Domain | 關鍵洞見 |
|------|--------|----------|
| PR review 瓶頸 | 開發流程 | 根本原因是 PR 大小的文化，而非 reviewer 數量 |
| 冗長的週會 | 會議效率 | 進度報告改為非同步，會議時間減半 |

## 額外案例

更多範例見 `references/kaizen-cases.md`：
deployment pipeline 最佳化、文件流程、onboarding 改善。

## 改善原則

| 原則 | 描述 | 反 pattern |
|------|------|-------------|
| 最小幅度 | 一次只變動一件事 | 「我們重寫整個 pipeline」 |
| 可逆 | 不行就能還原 | 不可逆的基礎設施變更 |
| 可衡量 | 能量化前後差異 | 「感覺變好了」卻沒有資料 |
| 立即 | 本週就開始，而不是「總有一天」 | 「我們 Q3 再做」 |
| 循環 | 一個改善導向下一個 | 「我們已經改善完了」 |

## 文化起源

Kaizen 起源於戰後日本製造業，最具代表性的是
由大野耐一發展的 Toyota Production System。
其哲學強調從 CEO 到生產線員工，每位員工都應
持續尋找改善工作的方法。W. Edwards Deming 的
品質管理原則對 Kaizen 方法論的發展影響深遠。
