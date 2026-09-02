# loom 重設計 — spec
intent: 2026-09-02-simple-loom-flow@be19b961
confirmed-behavior: 2026-09-02   # 重確認 2026-09-02：對抗 r5 後三處可見行為（不可逆動作必問、盲跑報告兩固定段、問題三型判準）kouko 逐項確認

## Requirements                                    【使用者可讀】
REQ-1 — 決策點數固定
  engineering 兩處（intent 確認、驗收）、product 三處（加可見行為確認）；單向門與判斷型岔路一律併進既有決策點，不新增停點；決策點後才浮現的岔路由 agent 選預設、標 agent-decided、在盲跑報告揭露。每個決策點內問題數不限，但每個問題必須可歸入三型之一（要什麼／可見行為／做到了嗎）或單向門的後果形；歸不進去的由 review 的 user-judgment-leak 維度判 NEEDS_REVISION（判準對象＝站在決策點記進 review.json `questions[]` 的問題）。決策點過後才浮現的單向門若屬金錢／綁定／動既有資料三類，agent 只能選零義務、可逆、不動既有資料的預設。→ Acceptance #1, #3
REQ-2 — 兩個 host 一致
  Claude Code 與 Codex CLI 走出相同的檔案、決策點、閘門；Codex 只多一次每 repo 的 `/hooks` 授信，成立條件是 `.codex/hooks.json` 的 command 字串固定（相對路徑、不含版本），升級只換 checker 副本內容；切換日既有 Codex repo 因定義改變需重授信一次（一次性，spec 明示）。→ Acceptance #2
REQ-3 — 機器審查為唯一品質來源
  每個判斷型 checkpoint ≥ 2 個 fresh-context reviewer；跨 vendor 為使用者常設選擇（KICKOFF-DEFAULTS `second-vendor:`），機制在同一個 change 裡至多建議一次，答案記住後不再問；盲跑 agent ≠ implementer；finding 的 dismissed 只能由非 implementer 的 reviewer 下；repo 未宣告 mutation／fuzz 工具時，對抗 agent 自寫 ≥3 個可執行 abuse 案例。→ Acceptance #1
  （對抗動作按 artifact 型別觸發屬 Design decision，不對應 Acceptance。）
REQ-4 — 盲跑報告是驗收介面
  對 intent 的每條 Acceptance（product 時加 spec 的 UI flows）寫「怎麼試、結果、證據」；固定一行「對你既有的資料做了什麼」；「我替你決定了」段列 agent-decided 岔路與 important 以上的 dismissal。→ Acceptance #1
REQ-5 — 五種 per-change artifact
  intent.md、spec.md、plan.md、diff/PR、review.json；memory 與 standing docs 不算 per-change。→ Acceptance #5
REQ-6 — 決定性層靠重算
  checker 對 needs-design 重算介面表面、對 package 測試在乾淨工作樹自行重跑（agent 填的結果只作記錄）、對 reviewer ≠ implementer 與 dismissed 者身分機械檢查、對收件與 push 條件重算、對 standing docs 的勸導／拒收／靜音三段重算（完整規則集見 concept-model §7 與 §8）；不讀 agent 的宣稱。→ Acceptance #1（品質由機器保證）
REQ-7 — 准入規則可機械驗
  機制母體＝`docs/loom/evidence/mechanisms.yaml`，五類各有可重算面（skill 目錄、checker `--list-rules` 輸出、hooks.json 條目、`loom-code/contract/manifest.yaml` 宣告、SKILL.md 內 `<!-- gate: id -->` 標記）；checker 必須提供 `--list-rules`；CI 重算五類與 yaml 比對：漏登→紅、yaml 有而清單無→紅、淨數增且 CHANGELOG 無 `budget-exception: <id> — <reason>`→紅、無 eval→紅。→ Acceptance #7
REQ-8 — 瘦身目標
  skill ≤ 18（站＋計數工具；reference 與 standalone 工具不計；plan 目標 17）；每 change 文件形狀 ≤ 5；session-start 注入字數 ≤ 基線之半（基線＝本 change 合併前 main 的固定 SHA，落地時記進 KICKOFF-DEFAULTS `session-start-baseline: <sha> <words>`；命令 `bash loom-code/hooks/session-start </dev/null | wc -w`，cwd 為空 git repo）。→ Acceptance #5
  （名詞 ≤ 40 屬 intent Open question：計數規則與基線定案前只記錄，不入本 REQ。）
REQ-9 — 冷讀可執行
  一個沒看過 loom 的 agent，只拿該站的 SKILL.md，對指定任務（測例固定：Task A「六支腳本抽共用 git helper，只裝 loom-code，Codex」與 Task B「CLI todo 加到期日，兩 plugin，Claude Code」）在 15 分鐘內零猜測說出：會產生哪些檔、誰決定什麼、哪個 checker 在何時擋、審查何時跑；零猜測優先於 15 分鐘。受測站＝該任務的入口站（Task A：write-plan；Task B：capture-intent）；入口站文件必含一張「本 change 的完整站序（含上游已完成者）、各站產生的檔與決策者、checker 時機、checkpoint 時機」摘要表，冷讀者只靠它回答。concept-model.md 只記錄（v10：25 分鐘、零猜測），不作驗收。→ Acceptance #6
REQ-10 — 不比今天重
  以 PR #771、#772、#775 三個已合併 change replay 新流程，一律以 engineering 路徑計（三者今天皆為工程改動）；三項逐 change 皆 ≤ 今天實測——#771：31 commit／22 派工／2 決策點；#772：67／58／2；#775：28／14／2（evidence/ceremony-cost-old-vs-new.md §(i)(ii)(iii)）。該 evidence 的「New model」欄是依 v7（含 approval-only commit）算的，已過時；以 replay 實測為準。→ Acceptance #4

## Design decision                                 【混合；不呈現給使用者】
全文見同資料夾 `concept-model.md`（v10）。摘要：三 plugin 沿「要什麼／為什麼」對「怎麼做」切線，loom-design 與 loom-workflow 依賴 loom-code 的 versioned contract package；七站、十工具、一 reference、四 action；checkpoint review（wave 結束按門檻、branch 結束必跑、after-task 逃生口 ≤ 2）；review.json 入版控且 push 時 HEAD 為 review-only commit；standing docs 三段式（勸導／拒收／靜音）；decision-map 的 delivery ticket 由 intent 取代；evidence 跟著 artifact 住；准入規則 AND 形式。
單向門規則（自 UI flows 移入）：類別 (a)–(e)（(e)＝對既有資料的不可逆動作，無岔路也必問）與四道閘（先查、先量、門檻、合併）見 concept-model §4；決策點後才浮現的岔路 agent 選預設、標 `agent-decided`、盲跑報告設「我替你決定了」段；(b)(c)(e) 三類只能選零義務可逆的預設。
跨 vendor 已揭露成本：本 spec 自身四輪審查的 7 個致命 finding 有 5 個只有一家 vendor 找到（review.json）；單 vendor 是使用者裁定的預設，這個數字寫進決策點①的一次性建議句。
硬切換日的三件契約事實（concept-model §1／§10）：plugin 版本傾斜由 `requires-contract` 重算並 BLOCK；進行中舊 branch 首次 push 被擋，出口＝補 intent＋一次 checkpoint；綁舊 brief 的 DA 改指 retired。
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
使用者看到的對話有三類：四種決策型；兩種非決策型（入場判準：不做就無法繼續的授權或缺件，不得新增）；一種非互動提示（只顯示、不需回答、永不阻擋）：
1. intent 確認：「你要的是 ___，做完後你可以 ___、___、___。對嗎？」→ 對／改。
2. spec 可見行為確認（product）：「你下 ___ 會看到 ___；___ 的情況會 ___。對嗎？」→ 對／改。
3. 驗收：「照你說的第 1 條，我在乾淨環境這樣試：___，結果 ___（截圖）。第 2 條 ___。對你既有的資料：___。我替你決定了：___。有一個地方我不確定你要什麼：___。」→ OK／不 OK／回答問題。
4. 單向門（併在 1 或 2 裡問，不另外停）：「A 用你的三段錄音測，準確率 91%、每小時 0.9 美元、錄音送雲端；B 本機跑，78%、免費、不外傳。我建議 A，除非你在意隱私。」→ 選一個／問更多。無岔路的不可逆動作同樣在這裡問：「這會把你現在的 todos.json 改成新格式，舊版程式讀不了；我會先留一份備份在 ___。可以嗎？」→ 可以／不要。
非決策型（不計入決策點）：
5. Codex 第一次用此 repo：「我已幫這個 repo 裝好 loom 的檢查；請在 Codex 裡輸入 /hooks 按一次授權，我才會繼續。」→ 使用者授權 → 下次指令自動繼續。
6. product 但 repo 還沒有產品原則（**併在決策點①的同一段對話**，不另停）：「做產品功能前這個 repo 要先有一份產品原則，我接著問你幾個問題來產生（約十分鐘），最後跟 intent 一起確認。」→ 直接進訪談。
非互動提示：
7. 缺 DESIGN.md（或 engineering 缺 PRINCIPLES.md）時，每份 intent 開頭固定三行提示，不需回答：「這個 repo 還沒有 ___。沒有它，___ 無法檢查一致性。想要的話說一聲我來做；不想再看到這行，我可以在設定裡記住。」
（要不要用第二家模型當 reviewer，在決策點①裡順帶問，同一個 change 至多一次，答案記進 KICKOFF-DEFAULTS 後不再問。）
單向門的觸發規則（哪些算、先量再問、已釘住不問、合成一次）見 Design decision。
