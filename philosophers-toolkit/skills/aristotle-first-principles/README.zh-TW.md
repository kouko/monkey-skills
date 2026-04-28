# Aristotle's First Principles Skill

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

將問題拆解到根本真理，再從零重建，拒絕類比與慣例。

## 五階段流程

| Phase | 提問 | 目的 |
|-------|------|------|
| Problem Essence | 你真正想達成的是什麼？ | 將結果與假設的解法分開 |
| Challenge Assumptions | 你正在假設什麼？驗證過嗎？ | 對每個假設以證據進行 test |
| Establish Ground Truths | 不論如何都仍為真的是什麼？ | 找出 3-5 個無法再化約的事實 |
| Reason Upward | 僅從這些真理出發，最簡單的解是什麼？ | 構築由真理所支撐的最小化解法 |
| Validate Reasoning | 每個決策都能回溯到一個 ground truth 嗎？ | 對類比 / 複雜化 / 包袱陷阱進行壓力測試 |

## Method Type

Process-driven（逐步拆解與重建）。
與 Four Causes（分析既有事物）或 Dialectics（比較立場）不同。

## 須避免的關鍵陷阱

| Trap | 描述 | 範例 |
|------|------|------|
| Complexity | 不必要的元件偷偷溜回來 | 「為了以防萬一」加上 cache |
| Analogy | 在無意間複製既有解法 | 「像是 X 版本的 Uber」 |
| Legacy | 維持已過時的相容性 | 支援沒人使用的格式 |

## SKILL.md 中的範例

| 範例 | Domain | 慣例做法 | First-Principles 結果 |
|------|--------|----------|----------------------|
| Authentication | 內部工具 | 加上 OAuth2 | 直接使用既有的 corporate SSO |
| Data Storage | 事件記錄 | PostgreSQL vs MongoDB | append-only log 檔案 + 批次查詢 |

## 靈感來源

五階段流程結構靈感來自
[awesome-skills/first-principles-skill](https://github.com/awesome-skills/first-principles-skill)（MIT License）。
依 philosophers-toolkit 標準改寫為 guided dialogue 風格。
