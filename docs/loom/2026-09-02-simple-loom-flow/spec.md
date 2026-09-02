# loom 重設計 — spec
intent: 2026-09-02-simple-loom-flow@be19b961
confirmed-behavior: 2026-09-02

## Requirements                                    【使用者可讀】
REQ-1 — 決策點數固定
  engineering 兩處（intent 確認、驗收）、product 三處（加可見行為確認）；單向門與判斷型岔路一律併進既有決策點，不新增停點；決策點後才浮現的岔路由 agent 選預設、標 agent-decided、在盲跑報告揭露。每個決策點內問題數不限。→ Acceptance #1, #3
REQ-2 — 兩個 host 一致
  Claude Code 與 Codex CLI 走出相同的檔案、決策點、閘門；Codex 只多一次每 repo 的 `/hooks` 授信，成立條件是 `.codex/hooks.json` 的 command 字串固定（相對路徑、不含版本），升級只換 checker 副本內容。→ Acceptance #2
REQ-3 — 機器審查為唯一品質來源
  每個判斷型 checkpoint ≥ 2 個 fresh-context reviewer；跨 vendor 為使用者常設選擇（KICKOFF-DEFAULTS `second-vendor:`），機制只在首次偵測到第二家 CLI 時建議一次；盲跑 agent ≠ implementer。→ Acceptance #1
  （對抗動作按 artifact 型別觸發屬 Design decision，不對應 Acceptance。）
REQ-4 — 盲跑報告是驗收介面
  對 intent 的每條 Acceptance（product 時加 spec 的 UI flows）寫「怎麼試、結果、證據」。→ Acceptance #1
REQ-5 — 五種 per-change artifact
  intent.md、spec.md、plan.md、diff/PR、review.json；memory 與 standing docs 不算 per-change。→ Acceptance #5
REQ-6 — 決定性層靠重算
  checker 對 needs-design 重算介面表面、對測試與 probe 要求實跑記錄、對 reviewer ≠ implementer 機械檢查、對收件與 push 條件重算（完整規則集見 concept-model §7）；不讀 agent 的宣稱。→ Acceptance #1（品質由機器保證）
REQ-7 — 准入規則可機械驗
  機制母體＝`docs/loom/evidence/mechanisms.yaml`（skill、checker 規則、hook、action、schema 欄位、散文閘，各帶 eval 連結）；CI 對 PR 重算母體：淨數增且無 budget-exception 行→紅、有機制無 eval→紅。→ Acceptance #7
REQ-8 — 瘦身目標
  skill ≤ 18；每 change 文件形狀 ≤ 5；session-start 注入字數 ≤ 基線之半（基線＝main 當前 `hooks/session-start` 渲染輸出字數，CI 命令固定）。→ Acceptance #5
  （名詞 ≤ 40 屬 intent Open question：計數規則與基線定案前只記錄，不入本 REQ。）
REQ-9 — 冷讀可執行
  一個沒看過 loom 的 agent，只拿站文件，對一個指定任務在 15 分鐘內零猜測說出：會產生哪些檔、誰決定什麼、哪個 checker 何時擋、審查何時跑。現況 concept-model.md 整份為 25 分鐘（§12）；達標路徑＝落地後各站 SKILL.md 只載自己那段，量測對象為站文件。→ Acceptance #6
REQ-10 — 不比今天重
  以 PR #771（refactor）、#772（feature）、#775（docs）三個已合併 change replay 新流程；commit 數、審查派工數、人類決策點三項逐 change 皆 ≤ 今天實測（基線見 evidence/ceremony-cost-old-vs-new.md §Totals：126／94／6）。→ Acceptance #4

## Design decision                                 【混合；不呈現給使用者】
全文見同資料夾 `concept-model.md`（v10）。摘要：三 plugin 沿「要什麼／為什麼」對「怎麼做」切線，loom-design 與 loom-workflow 依賴 loom-code 的 versioned contract package；七站、十工具、一 reference、四 action；checkpoint review（wave 結束按門檻、branch 結束必跑、after-task 逃生口 ≤ 2）；review.json 入版控且 push 時 HEAD 為 review-only commit；standing docs 三段式（勸導／拒收／靜音）；decision-map 的 delivery ticket 由 intent 取代；evidence 跟著 artifact 住；准入規則 AND 形式。
單向門規則（自 UI flows 移入）：類別 (a)–(d) 與四道閘（先查、先量、門檻、合併）見 concept-model §4；決策點後才浮現的岔路 agent 選預設、標 `agent-decided`、盲跑報告設「我替你決定了」段。
agent-decided 的岔路與理由：
- 不做 git hook（`--no-verify` 六種繞法、worktree 下 `core.hooksPath` 失效——industry research）。
- Codex 未授信時 BLOCK 而非 WARN（實測未授信為靜默 fail-open）。
- 刪 waiver、approval-only commit、身分錨（紅隊：11/13 閘可偽造；目標敘述下人不審品質，無冒充問題）。
- 不 default-install loom-design（安裝不改變觸發條件）。
- delivery ticket ＝ intent（雙向綁定與 phase 帳本是「用狀態機記 git 已知的事」）。

## Alternatives considered                         【工程；不呈現】
- 兩個 plugin 合併 design 進 code：否決，違背 what/why vs how 切線且失去 code-only 安裝。
- 只保留最後一次大審：否決，大 diff 下 whole-branch 首輪 under-reach（q2 evidence §C.5：round 3 再找 3 條、round 4 再找 2 條）；改 checkpoint。
- 保留 Review Batch：否決，11k LOC、8 天 5 修正版、真實採用 6/268、無淨節省證據。
- CI ＋ branch protection 作為唯一閘（v8）：否決，把主要防護搬到 adopting repo 的外部設定，違背「loom 自身做主要防護」。
- 簽名式人在場閘（v9）：否決，每 change 三到四次確認框，且目標敘述下不需要防冒充。

## Current state evidence                          【工程；不呈現】
- Forward：使用者請求 → family-reception on-ramp 表 → using-loom-design 或 using-loom-code → brainstorming → brief → writing-plans → SDD（per-task 三臂或 batch）→ requesting-code-review → finishing → push。見 `evidence/current-state-diagnosis.md`、`evidence/loom-code.md`。
- Reverse：git-guard 讀 `.git/loom/{verified,review-pass,waiver}.json`；marker 由 orchestrator 以 `loom_gate_markers.py` 鑄造。見 `evidence/loom-code.md` §Totals。
- Error：Codex shim 對未知 payload fail-open；未授信 hook 靜默跳過；trust hash 不綁 script 內容。見 `evidence/q4-codex-hooks-live-test.md`。
- Data：36 skill／~38 artifact／名詞約 113（loom-workflow 清單自不一致，基線待重數）；三個真實 change 合計 126 commit、94 審查派工、6 人類決策點、40 artifact。見 `evidence/ceremony-cost-old-vs-new.md`。
- Boundary：plugin 間靠 family-reception／relay／plain-relay 功能副本同步；decision-map 靠 `start_delivery` 雙向綁定 brief。見 `evidence/loom-workflow.md`。

## UI flows                                        【使用者可讀】
使用者看到的對話有四種決策型、兩種非決策型：
1. intent 確認：「你要的是 ___，做完後你可以 ___、___、___。對嗎？」→ 對／改。
2. spec 可見行為確認（product）：「你下 ___ 會看到 ___；___ 的情況會 ___。對嗎？」→ 對／改。
3. 驗收：「照你說的第 1 條，我在乾淨環境這樣試：___，結果 ___（截圖）。第 2 條 ___。有一個地方我不確定你要什麼：___。」→ OK／不 OK／回答問題。
4. 單向門（併在 1 或 2 裡問，不另外停）：「A 用你的三段錄音測，準確率 91%、每小時 0.9 美元、錄音送雲端；B 本機跑，78%、免費、不外傳。我建議 A，除非你在意隱私。」→ 選一個／問更多。
非決策型（不計入決策點）：
5. Codex 第一次用此 repo：「我已幫這個 repo 裝好 loom 的檢查；請在 Codex 裡輸入 /hooks 按一次授權，我才會繼續。」→ 使用者授權 → 下次指令自動繼續。
6a. 第一次偵測到第二家模型 CLI：「我看到這台機器也有 ___。要不要讓它當第二個審查者？好處是能抓到同一家模型一起漏掉的問題；代價是每次審查多幾分鐘和它的額度。你選了我就記住，不再問。」→ 要／不要。
6. product 但 repo 還沒有產品原則：「這個 repo 還沒有產品原則檔，做產品功能前要先有。我可以訪談你產生一份（約十分鐘），或你告訴我這個 repo 不需要，我就不再提。」→ 產生／不需要。
單向門的觸發規則（哪些算、先量再問、已釘住不問、合成一次）見 Design decision。
