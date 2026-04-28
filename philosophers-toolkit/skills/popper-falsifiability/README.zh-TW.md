# Popper's Falsifiability Skill

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

將模糊主張轉成可測試的 hypothesis，
並設計能證明它們為錯的 test。

## 五個步驟

| Step | 提問 | 目的 |
|------|------|------|
| State the Claim | hypothesis 究竟是什麼？ | 在改寫前先捕捉主張本身 |
| Operationalize | 你會如何衡量它？ | 將模糊主張變得具體且可測試 |
| Design Falsification Test | 什麼證據能推翻它？ | 在 test 前定義 pass/fail 標準 |
| Evaluate Evidence | 既有資料是支持還是 falsify？ | 將 test 套用至既有證據 |
| Verdict | Falsified、survived，或 unfalsifiable？ | 得出結論並提出建議的下一步 |

## Method Type

Process-driven（逐步的 hypothesis 測試流程）。
與 First Principles（拆解到真理）或 Dialectics（檢視取捨）不同。

## 三種裁決

| Verdict | 含義 | 下一步行動 |
|---------|------|-----------|
| Falsified | 證據與 hypothesis 矛盾 | 修改或放棄 |
| Survived | 未被推翻（也未被證實） | 謹慎前行；設計更嚴的 test |
| Unfalsifiable | 沒有任何證據能推翻它 | 改寫，或承認其為信念 / 價值 |

## 不可證偽的紅旗

| 訊號 | 範例 |
|--------|------|
| 對證據免疫 | 「沒有資料能改變我的看法」 |
| 無限延後 | 「我們只是還需要更多資料」 |
| 例外免疫 | 「任何反例都是特例」 |
| 無法量測 | 「它以我們無法觀測的方式運作」 |

## SKILL.md 中的範例

| 範例 | Domain | 主張 | 裁決 |
|------|--------|------|------|
| Performance Claim | Caching | 「Redis 讓我們更快」 | Survived（p95 從 350ms 降到 180ms） |
| Architecture Assumption | Microservices | 「Microservices 讓我們出貨更快」 | Unfalsifiable（混淆變數） |

## 互補的 Skills

- **Assumption Mapping**（planning-team）：AM 識別假設，Popper 對其進行 test
- **First Principles**：拆解到 ground truths；Popper 測試特定主張
- **Socratic Method**：透過 dialogue 挑戰思考；Popper 結構化 test

## 靈感來源

五步驟證偽流程基於 Karl Popper《The Logic of Scientific Discovery》（1934）
與《Conjectures and Refutations》（1963）。依 philosophers-toolkit 標準
改寫為 guided dialogue 風格。
