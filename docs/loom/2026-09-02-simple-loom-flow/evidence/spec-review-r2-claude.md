# spec review round 2 — Claude leg (opus) — verbatim

## 前提更正
指定的 delta 終點 `24528776` **不是 HEAD**：其後還有 `fc5693e2`（docs(loom): cross-vendor review is a user standing choice）。我審的是 `12027c40..HEAD`（＝現行文字），下列 N1／N2 由這個追加 commit 引入。

## findings_status
- **SR1-01 resolved** — 新增 `REQ-10 — 不比今天重`，指名 PR #771／#772／#775、三項計數、基線 evidence §Totals，write-plan 可據此排 replay 任務。殘留見 N5。
- **SR1-02 resolved** — REQ-1「單向門與判斷型岔路一律併進既有決策點，不新增停點；決策點後才浮現的岔路由 agent 選預設、標 agent-decided、在盲跑報告揭露」；§4 同步改為「附在既有決策點內」，engineering 在 write-plan 前問的句子已刪。但 N2 從另一側重開缺口。
- **SR1-03 resolved** — §4 表格改為「write-plan 用 contract package 的 §2c 模板**自動產生最小 spec.md**……使用者永遠不手寫 spec」。殘留見 N3。
- **SR1-04 still-open（🟡，自 fatal 降級）** — §11 新增「機制母體＝`docs/loom/evidence/mechanisms.yaml`」＋CI 重算＋兩條紅燈，母體與判定方式已存在；但重算來源不涵蓋母體自列的「散文閘」，見 N4。
- **SR1-05 resolved（🟢 殘留）** — UI flows 補了非決策型 5（Codex `/hooks`）與 6（缺 PRINCIPLES 拒收）。§8 的 standing docs「固定三行 WARN」仍未出現在 UI flows。
- **SR1-06 resolved** — REQ-3 的對抗動作、REQ-8 的名詞 ≤40 各自降為括號註記並註明「不對應 Acceptance／屬 intent Open question」；REQ-6 箭頭改指 Acceptance #1。
- **SR1-07 resolved** — REQ-2 補「command 字串固定（相對路徑、不含版本），升級只換 checker 副本內容」，§7a 同步改寫並刪去「版本舊就覆寫」。已對 `q4-codex-hooks-live-test.md` §Addendum run E 核對：definition 未變、script 內容改動仍以 trusted 身分執行 — 引用屬實。
- **SR1-08 still-open（🟡）** — `skill ≤ 18`、名詞 113 已加「基線待重數」對沖，這兩點 resolved；但 session-start 基線寫成「main **當前** 渲染輸出字數」，未釘 SHA：本 change 合併進 main 後基線即被自己覆蓋，`≤ 基線之半`變成恆真。
- **SR1-09 resolved（🟢 殘留）** — REQ-9 已逐字採 Acceptance #6 四項輸出，並帶入現況 25 分鐘與「各站 SKILL.md 只載自己那段」的達標路徑。Codex 要求的「指定一個 given task 作為冷讀測例」仍未指定。
- **SR1-10 resolved** — 掃讀改為「whole-branch 首輪 under-reach（q2 §C.5：round 3 三條、round 4 再兩條）」；UI flows 第 4 項的觸發規則已移入 Design decision；REQ-6 補「完整規則集見 concept-model §7」、REQ-7 的「三項觀察指標」措辭已刪。

## new_findings
- **N1 🔴 spec-conformance** — `spec.md:REQ-3`／`concept-model.md:§5`（commit fc5693e2）。跨 vendor 由「必用／預設」改成「使用者常設選擇，選了就用，沒選就不用，兩者都不 WARN、不擋」，且 §7 push 閘改為「vendor 數不是條件」、schema 刪 `degraded`。但 ground truth `intent §Proposed outcome` 仍寫「品質來自機器：寫的 agent 和審的 agent 分開、**至少一個不同 vendor**」；Open question 只把**成本**列為待量，不是把它降為偏好。spec 現在與未修改的 intent 直接牴觸。
  fix：二擇一——(a) 回復「預設開啟，成本量完前缺第二 vendor 只 WARN」；或 (b) 先修 intent 該句並記錄使用者裁定，spec 再跟改。
- **N2 🟡 ambiguity／spec-conformance** — `spec.md:§UI flows` 非決策型清單。新增的「非決策型（不計入決策點）」是一個**無上限、無判準**的類別：5 與 6 是解除阻擋的動作，但新增的 6a（要不要用第二家 CLI 當 reviewer）是純偏好詢問，性質上就是停下來要使用者做工程取捨，卻被排除在 Acceptance #3 的計數之外。這條路徑可以無限增生而不違反 REQ-1。
  fix：定義「非決策型」的入場判準（只限：不做就無法繼續的授權／缺件），並明訂總數上限；6a 若保留，改為併進決策點①。
- **N3 🟡 inconsistency** — `concept-model.md:§4` 表格「只裝 loom-code／needs-design: yes」格：「使用者只做決策點②」未帶 `kind: product` 條件，與 §2 表 spec.md 列的「決策點②（**只在 kind: product**）……engineering 不問」矛盾；照字面 engineering 的 code-only change 會多一個停點，破 Acceptance #3 的 ≤2。
  fix：改為「`kind: product` 時使用者做決策點②；engineering 不問」。
- **N4 🟡 missing-population** — `concept-model.md:§11`。母體列舉含「散文閘」，但 CI 重算來源只給 skill＝`skills/*/SKILL.md`、checker rule 表、hooks.json 條目、contract package 宣告——散文閘沒有可重算面，而在既有 SKILL.md 內新增一條散文規則不改變任何一項計數。這正是 intent §Problem 描述的歷史增生形態，Acceptance #7 對它仍不生效。另：「checker 的 rule 表」預設 checker 會匯出機器可讀規則表，該義務未寫進任何 REQ。
  fix：散文閘改以可重算的標記為母體（例如 SKILL.md 內 `gate:` 區塊或 rule id 註記），並在 REQ-7 寫明 checker 必須輸出 rule 清單供 CI 重算。
- **N5 🟡 ambiguity** — `spec.md:REQ-10`。(a) 引用 §Totals 的**合計** 126／94／6，卻要求「逐 change 皆 ≤」；逐 change 基線（31/67/28、22/58/14、2/2/2）在同檔 §(i)(ii)(iii)，應直接引用。(b) 未標三個 replay 對象的 `kind`：今天每 change 的人類決策點都是 2，而 REQ-1 把 product 固定為 3——若三者中任一被判為 product，REQ-10 依設計即不可能通過。
  fix：引用逐 change 基線列，並標注三個 change 的 kind（或明訂 replay 一律以 engineering 路徑計）。
- **N6 🟢 omission** — `concept-model.md:§7a`（delta 觸及範圍內）。新寫法把升級路徑定為「只換 repo 內 checker 副本內容」，而 run E 結論是 `trusted_hash` 不綁 script 內容、工作分支上的 agent 可改寫該副本；intent Constraint「決定性層擋的是漏步驟，不宣稱擋有目標的 agent」已豁免此威脅，但 §7a 未寫明這個已知限制。
  fix：§7a 加一行註明「repo 內 checker 副本可被工作分支改寫；此層不防有目標的 agent，需防時靠 CI 比對 main 的 digest」。

## verdict
**NEEDS_REVISION** — N1 為 🔴（spec 與未修改的 intent 直接牴觸）。10 條 round-1 findings 中 8 條 resolved、SR1-04／SR1-08 為 🟡 still-open，皆非致命；擋住的是 delta 之後那個追加 commit。

## what_i_did_not_read
只開了指派的六個路徑，加上為核對事實而讀的 `evidence/ceremony-cost-old-vs-new.md`（§Totals 與三個 change 的計數列）與 `evidence/q4-codex-hooks-live-test.md`（§Implications ＋ run E addendum）。未開 `q2-per-task-review-evidence.md`（SR1-10 的 §C.5 引用未逐字核對）、`current-state-diagnosis.md`、三份 plugin inventory、其餘 evidence 檔，以及任何 loom plugin 原始碼。未重審 delta 未觸及的段落。
