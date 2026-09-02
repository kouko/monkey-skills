# loom 重設計 — spec
intent: 2026-09-02-simple-loom-flow@be19b961

## Requirements                                    【使用者可讀】
REQ-1 — 三處決策點
  使用者只在 intent 確認、product 的 spec 可見行為確認、盲跑報告驗收三處被問；其餘決定 agent 做並記理由。→ Acceptance #1, #3
REQ-2 — 兩個 host 一致
  Claude Code 與 Codex CLI 走出相同的檔案、決策點、閘門；Codex 只多一次每 repo 的 `/hooks` 授信。→ Acceptance #2
REQ-3 — 機器審查為唯一品質來源
  每個判斷型 checkpoint ≥ 2 個 fresh-context reviewer，host 有第二 vendor 時必用；盲跑 agent ≠ implementer；對抗動作按 artifact 型別觸發。→ Acceptance #1
REQ-4 — 盲跑報告是驗收介面
  對 intent 的每條 Acceptance（product 時加 spec 的 UI flows）寫「怎麼試、結果、證據」。→ Acceptance #1
REQ-5 — 五種 per-change artifact
  intent.md、spec.md、plan.md、diff/PR、review.json；memory 與 standing docs 不算 per-change。→ Acceptance #5
REQ-6 — 決定性層靠重算
  checker 對 needs-design 重算介面表面、對測試與 probe 要求實跑記錄、對 reviewer ≠ implementer 機械檢查；不讀 agent 的宣稱。→ Acceptance #7
REQ-7 — 准入規則
  新機制必須同時有回歸 eval 且淨數不增（或明示 budget 例外）；CI 算三項紅燈指標、記三項觀察指標。→ Acceptance #7
REQ-8 — 瘦身目標
  skill 36 → 18；名詞 ≤ 40（計數規則見 concept-model §3）；session-start 注入減半。→ Acceptance #5
REQ-9 — 冷讀可執行
  只拿 concept-model.md 的 agent 15 分鐘內零猜測走完一個任務。→ Acceptance #6

## Design decision                                 【混合；不呈現給使用者】
全文見同資料夾 `concept-model.md`（v10）。摘要：三 plugin 沿「要什麼／為什麼」對「怎麼做」切線，loom-design 與 loom-workflow 依賴 loom-code 的 versioned contract package；七站、十工具、一 reference、四 action；checkpoint review（wave 結束按門檻、branch 結束必跑、after-task 逃生口 ≤ 2）；review.json 入版控且 push 時 HEAD 為 review-only commit；standing docs 三段式（勸導／拒收／靜音）；decision-map 的 delivery ticket 由 intent 取代；evidence 跟著 artifact 住；准入規則 AND 形式。
agent-decided 的岔路與理由：
- 不做 git hook（`--no-verify` 六種繞法、worktree 下 `core.hooksPath` 失效——industry research）。
- Codex 未授信時 BLOCK 而非 WARN（實測未授信為靜默 fail-open）。
- 刪 waiver、approval-only commit、身分錨（紅隊：11/13 閘可偽造；目標敘述下人不審品質，無冒充問題）。
- 不 default-install loom-design（安裝不改變觸發條件）。
- delivery ticket ＝ intent（雙向綁定與 phase 帳本是「用狀態機記 git 已知的事」）。

## Alternatives considered                         【工程；不呈現】
- 兩個 plugin 合併 design 進 code：否決，違背 what/why vs how 切線且失去 code-only 安裝。
- 只保留最後一次大審：否決，大 diff 下 reviewer 掃讀；改 checkpoint。
- 保留 Review Batch：否決，11k LOC、8 天 5 修正版、真實採用 6/268、無淨節省證據。
- CI ＋ branch protection 作為唯一閘（v8）：否決，把主要防護搬到 adopting repo 的外部設定，違背「loom 自身做主要防護」。
- 簽名式人在場閘（v9）：否決，每 change 三到四次確認框，且目標敘述下不需要防冒充。

## Current state evidence                          【工程；不呈現】
- Forward：使用者請求 → family-reception on-ramp 表 → using-loom-design 或 using-loom-code → brainstorming → brief → writing-plans → SDD（per-task 三臂或 batch）→ requesting-code-review → finishing → push。見 `evidence/current-state-diagnosis.md`、`evidence/loom-code.md`。
- Reverse：git-guard 讀 `.git/loom/{verified,review-pass,waiver}.json`；marker 由 orchestrator 以 `loom_gate_markers.py` 鑄造。見 `evidence/loom-code.md` §Totals。
- Error：Codex shim 對未知 payload fail-open；未授信 hook 靜默跳過；trust hash 不綁 script 內容。見 `evidence/q4-codex-hooks-live-test.md`。
- Data：36 skill／~38 artifact／113 名詞；三個真實 change 合計 126 commit、94 審查派工、6 人類決策點、40 artifact。見 `evidence/ceremony-cost-old-vs-new.md`。
- Boundary：plugin 間靠 family-reception／relay／plain-relay 功能副本同步；decision-map 靠 `start_delivery` 雙向綁定 brief。見 `evidence/loom-workflow.md`。

## UI flows                                        【使用者可讀】
使用者看到的只有三種對話：
1. intent 確認：「你要的是 ___，做完後你可以 ___、___、___。對嗎？」→ 對／改。
2. spec 可見行為確認（product）：「你下 ___ 會看到 ___；___ 的情況會 ___。對嗎？」→ 對／改。
3. 驗收：「照你說的第 1 條，我在乾淨環境這樣試：___，結果 ___（截圖）。第 2 條 ___。有一個地方我不確定你要什麼：___。」→ OK／不 OK／回答問題。
4. 單向門（架構／框架／元件選擇）：「選 A：以後只能在 ___ 跑、每月 ___、換掉要重寫 ___。選 B：___。我建議 A，因為 ___。」→ 選一個／問更多。框架、語言、資料庫、認證、託管、付費服務、資料格式都算；PRINCIPLES.md 已有立場的不問。
其餘時間 agent 只在判斷型岔路（≥3 個 trade-off 且改變交付物）停下來，用白話列選項並給預設。
