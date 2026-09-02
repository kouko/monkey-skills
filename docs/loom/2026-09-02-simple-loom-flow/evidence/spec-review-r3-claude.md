# spec review round 3 — Claude leg (opus) — verbatim

讀完指派路徑與 delta，核對 evidence 逐 change 基線後：

**findings_status**
- N1（跨 vendor 與 intent 牴觸，🔴）— resolved：intent §Proposed outcome 已改「用不用第二家模型由使用者選，至多建議一次」，status 重確認；spec REQ-3 與 §5 逐字對齊。
- N2（非決策型類別無判準）— resolved：§4 立入場判準「不做就無法繼續的授權或缺件」＋「不得新增成員，新增＝走 §11」；spec UI flows 同步為「一種非決策型」。
- N3（code-only 格漏 product 限定）— resolved：§4 表格改「`kind: product` 時做決策點②，engineering 不問」。
- N4（散文閘無可重算面）— resolved：`<!-- gate: <id> -->` 為母體＋未標記不得當閘；REQ-7 寫明 checker 必須提供 `--list-rules`。
- N5（REQ-10 引用合計而非逐 change）— resolved：改引逐 change 31/22/2、67/58/2、28/14/2，並釘「一律以 engineering 路徑計」；三組數字與 evidence §(i)(ii)(iii) 逐項核對相符。
- N6（checker 副本可被改寫的已知限制）— resolved：§7a 補一行，並指向 §0 與 CI digest 比對。
- SR1-04 — resolved（同 N4；殘留見 F7）。
- SR1-08 — **still-open**：修正只落在 concept-model §11（釘 SHA＋計數命令），spec REQ-8 仍寫「基線＝main **當前** 渲染輸出字數」，合併後自我覆蓋、`≤ 基線之半` 仍恆真；review.json 的 resolved 宣稱因此不完全屬實。
- Codex flow-6 🔴（「不需要產品原則」可繞過拒收且是額外停點）— resolved：flow 6 改為併進決策點①直接進訪談、無「不需要」選項；§8 靜音改為「只靜音 WARN，永不豁免 product 拒收」。

**new_findings**
- 🟡 `spec.md:REQ-8` — 與 `concept-model.md:§11` 對同一基線定義不一致（「main 當前」vs 釘 SHA），契約層仍是恆真需求。fix：REQ-8 改為「基線＝本 change 合併前 main 的固定 SHA，命令 `bash loom-code/hooks/session-start </dev/null | wc -w`」。
- 🟡 `spec.md:REQ-10` — 新綁定的 `evidence/ceremony-cost-old-vs-new.md` 其 New model 欄自算人類決策點 3／4／3（§Totals「Where the new model is HEAVIER」6→10），逐 change 皆 > 今天的 2，等於自證 REQ-10 不可能通過；該欄仍含 v10 已刪的 plan approval 停點，未重算。fix：以 v10 決策點定義重算三列 new-model c 值，或於 REQ-10 註明 new-model 欄過時、以 replay 實測為準。
- 🟡 `spec.md:REQ-9` — 測例已固定，但未指明 Task A／B 各交付**哪一站**的 SKILL.md；Task A（code-only、Codex）橫跨 write-plan／build／review／ship，「審查何時跑」是否須由單一站文件自答不明，量測無法重現。fix：每個測例標註受測站（或明訂「該任務入口站」）。
- 🟡 `concept-model.md:§8` × `§4` — 訪談併進決策點①後，未裝 loom-design 的 `kind: product` 路徑缺執行者：§8 仍留「沒裝 loom-design 可照 loom-code 附的模板手寫」，與 §4「使用者永遠不手寫」及 Acceptance #1 的三種問題衝突。fix：明訂 code-only 時由 write-plan 以 contract package 模板做訪談並代寫 PRINCIPLES.md。
- 🟢 `concept-model.md:§12` 表 v7→v10 列仍寫「獨立審查升為必要（≥2 reviewer、**跨 vendor**）」，與 §5 選配矛盾且無「歷史記錄」標註。
- 🟢 重複性範圍措辭不一：intent／§5「同一個 change 至多一次」vs `spec.md:UI flows` 括號「該 repo 第一次決策點①」。
- 🟢 `concept-model.md:§11` CI 比對只定義「清單有而 yaml 無→紅」，未定義 yaml 有而清單無（殘留條目可墊高基線讓淨數不增）。

**spec_vs_intent**：consistent —Acceptance #1/#3/#4/#5/#6/#7 各有對應 REQ，跨 vendor 選配與 Acceptance #6 改站文件兩處已與重確認後的 intent 逐字對齊；唯一落差是 REQ-8 基線措辭（內部不一致，非與 intent 牴觸）。

**verdict**：PASS_WITH_NOTES — 無 fatal still-open、無新 🔴；SR1-08 屬 important 仍開，另四條 🟡 建議合併一輪修正（REQ-8 與 REQ-9 兩處是落地時會直接卡住量測的）。

**what_i_did_not_read**：只開指派的六個路徑，加上為核對數字而讀的 `evidence/ceremony-cost-old-vs-new.md`（§(i)(ii)(iii)、§Totals、§Where the new model is HEAVIER）。未開 r1 findings 檔、`q2`／`q4`／`current-state-diagnosis` 等其餘 evidence、任何 loom plugin 原始碼；未重審 delta 未觸及的段落（§1–§3、§6、§9、§10）。未派任何 subagent，未修改任何檔案。
