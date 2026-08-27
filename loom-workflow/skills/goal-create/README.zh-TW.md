# Goal Create

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 起草一個目標條件。兩種命名模式：**SESSION** 寫出長時間運行 agent
> 的 run 用來比對的四欄目標；**ARC** 起草儲存庫 purpose 產物的草案，
> 交由使用者確認落地。

---

## 概要 — 這個 skill 是什麼

這個 skill 依使用者要的是什麼起草其中一種——絕不由 agent 從情境推測。

- **SESSION 模式** 產出長時間運行 agent 的 run 拿來比對的四欄目標條件
  ——`Outcome`、`Constraints`、`Verification`、`Stop-when`（例如給
  Claude Code 的 `/goal` 指令用）。欄位順序與各欄位定義的權威內容在
  `references/goal-shape.md`；草案建立所依據的兩個輸入槽、其中一槽為空時
  的拒絕規則、以及每個欄位必須帶的 provenance 標籤在
  `references/input-floor.md`。呈現草案前，會先跑過機械式下限檢查
  `scripts/goal_lint.py`——只檢查結構，從不判斷文字是否真的可判定。

- **ARC 模式** 產出儲存庫 purpose 產物 `docs/loom/PURPOSE.md` 的
  `Why` 與 `Done when` 草案。這個 skill 本身絕不會寫入該檔案——草案只能
  由使用者自己確認後落地。當儲存庫既沒有 purpose 產物、也沒有任何
  `docs/loom/` store 時，ARC 會回報自己不適用，且不搭建任何東西。

這份 README 是給人看的概要。這個資料夾裡的 `SKILL.md` 才是執行契約——
兩種模式與兩份參考檔都從那裡讀出；這份檔案不重複它。

---

## 呼叫

這個 skill 不會自己觸發。它在兩個目標需求已經浮現的地方被點名為可用
選項：`loom-workflow:handoff` 的 Prepare 模式,以及 `loom-code` 的
purpose-link 檢查印出的未回答 purpose 訊息。在那裡被點名不等於被呼叫。

---

## Files

```
goal-create/
├── README.md              <- English README
├── README.ja.md           <- 日本語 README
├── README.zh-TW.md        <- 本檔（繁體中文）
├── SKILL.md               <- 執行檔（給 Claude）
├── references/
│   ├── goal-shape.md       <- 四欄目標形態，SESSION 的 SSOT
│   └── input-floor.md      <- 輸入槽、拒絕規則、判準、provenance 標籤
└── scripts/
    └── goal_lint.py        <- SESSION 的機械式下限檢查
```
