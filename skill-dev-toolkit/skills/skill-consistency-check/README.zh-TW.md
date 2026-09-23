# Skill Consistency Check

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 找出 skill 套件內互相矛盾的規則 —— 一個檔案要求的事另一個檔案禁止、
> 兩個上限值對不上，或是遵守某條規則就必然踩到另一條規則禁止的步驟。

使用者主動呼叫的 **檢查型 skill**：指定一個 skill 資料夾，它會回傳
矛盾清單和整體判定。每一項都寫出兩邊的 file:line、引用的原文、信心等級
（high／medium／low）和一句說明。

這份 README 給在 GitHub 上閱讀 skill 的人看。agent 實際載入的操作檔是
[`SKILL.md`](SKILL.md)。

---

## 為什麼需要這個 skill？

指示互相矛盾時，照著每一行做事的 agent 在某些情況下怎麼做都會違規。
作者很難自己發現：兩邊常常在不同檔案、用詞不同，或只在某個條件下才
衝突。

先前的版本把規則轉成邏輯式再交給 SMT solver。盲測中 27 個埋入的矛盾
只抓到 7 個，精確率約 18%，漏掉的幾乎都出在轉換那一步。之後 10 輪
盲測顯示，由 LLM 直接閱讀原文效果好得多，也定下了這裡使用的方法。

---

## 怎麼運作？

```
skill folder ──► plan_groups.py ──► one group, or several groups
                                          │
             ┌────────────────────────────┴───────────────┐
             ▼                                            ▼
   read-through detectors                   walk-through detectors
   (read and report conflicts)              (act as the agent through
                                             3–5 situations)
             └────────────────────┬───────────────────────┘
                                  ▼
                           merge_report.py ──► verdict + report
```

- **兩種偵測器**，各自是獨立的 subagent：通讀（read-through）與模擬
  執行（walk-through）。規格在 [`references/`](references/)。
- **分組**：估計 30,000 tokens 以內的套件整包一次讀完；超過就分組，
  每組以 25,000 tokens 為目標。每組都放 SKILL.md、agents/ 檔和 SKILL.md
  直接引用的檔案，其餘檔案在兩種方法間用不同方式分配。從沒被放在同一
  組讀過的檔案組合會列在報告裡；若仍有某組超過 25,000 tokens（核心檔
  太大，或單一檔案很大），報告會發出警告。
- **判定**：只要有一個 high 的發現就是「需要修改」；medium 和 low
  只是提示。
- **副作用**：沒有。不安裝任何東西，也不在被檢查的資料夾裡寫任何檔案；
  報告寫到另外的執行目錄。不會自動修改發現的問題。
- **主機**：fan-out 用「派出 N 個 subagent」的抽象寫法，所以同一份
  SKILL.md 在 Claude Code 和 Codex 都能跑。不寫死模型名稱；請用中階
  以上的模型（實驗中最小一級的模型抓到 1–3 個就停了）。
- **徹底模式**（需明確要求才啟用）：每種方法各跑兩次。

---

## 限制

- 驗證時用的是 Claude Sonnet（200k context），套件約 25,000 tokens。
  其他模型未經驗證，報告會註明。
- 有條件才成立的矛盾（只在共同條件下衝突）和需要推好幾步才看得出的
  矛盾可能被漏掉。
- 附標準答案的回歸測試資料在 plugin 的
  `tests/consistency-check-corpus/` 資料夾；要依賴其他模型前，先用它
  驗證。

---

## 什麼時候用

- 發佈新的 skill、或大幅修改過的 skill 之前
- 照著 skill 做事的 agent 行為不一致，懷疑指示之間互相衝突時

## 什麼時候不用

- **設計品質評分** —— 用 [`skill-judge`](../skill-judge/)
- **用真實 prompt 做行為測試** ——
  用 [`dogfood-skill-testing`](../dogfood-skill-testing/)
- **資料夾結構或字數規則** —— 由 repo 的結構檢查器負責
