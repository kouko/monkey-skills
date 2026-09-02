# spec review round 4 — Claude leg (opus) — verbatim

**findings_status**（我方 🟡 + 對方）

| 條目 | 狀態 |
|---|---|
| 🟡 REQ-8 baseline（SR1-08） | resolved — REQ-8 已改「本 change 合併前 main 的固定 SHA＋`session-start-baseline: <sha> <words>`＋固定計數命令」，與 §11 逐字一致，恆真需求消失 |
| 🟡 REQ-10 evidence caveat | resolved — 加註「New model 欄依 v7 算、已過時；以 replay 實測為準」；自證不可能通過的矛盾解除 |
| 🟡 REQ-9 受測站 | resolved（見 new_findings NF-2 殘餘）— 已釘入口站（A：write-plan／B：capture-intent）＋要求入口站含摘要表 |
| 🟡 §8 code-only PRINCIPLES | resolved — 改為 write-plan 用 contract package 模板代做訪談並代寫，「使用者永遠不手寫」全文一致 |
| 🟡 §12 措辭 | resolved — v7→v10 列改為「跨 vendor 當時寫必用，spec 審查後改為使用者選配」，標明是歷史記錄 |
| 🟢 yaml-extra | resolved（concept-model 側）— §11 加「yaml 有而清單無→紅（殘留條目墊高基線）」；spec 側未同步，見 NF-1 |
| 🟢 重複性措辭不一 | resolved — spec UI flows 括號改為「同一個 change 至多一次」，與 intent／§5 對齊 |
| Codex N1 §0 跨 vendor（🔴 fatal） | resolved — §0 改「≥2 個 fresh context；第二家 vendor 由使用者選，機制每 change 至多建議一次」；與 intent／REQ-3／§5 四處一致 |
| Codex SR1-04 manifest 路徑 | resolved — §11 與 REQ-7 皆釘 `loom-code/contract/manifest.yaml`（列 actions／schema 欄位／station 名，機器可讀，版本戳在檔內），五類母體全部可重算 |
| Codex SR1-05 WARN flow | resolved — spec UI flows 新增第 7 條，逐字給出固定三行提示與靜音出口 |

**new_findings**（僅本 delta 引入）
- 🟡 `spec.md:REQ-7` × `concept-model.md:§11` — §11 新增的第四條紅線「yaml 有而清單無→紅」未同步進 REQ-7；REQ-7 仍只列三條紅線，契約層漏一條可重算規則。fix：REQ-7 補上該行。
- 🟡 `spec.md:UI flows` — 新增的第 7 條放進「非決策型」清單，但該清單上一輪剛立的入場判準是「不做就無法繼續的授權或缺件，不得新增成員」；第 7 條不需回答、也永不阻擋，兩者不合，且抬頭仍寫「四種決策型、**一種**非決策型」而實際已有三條（5／6／7）。fix：把 WARN 提示改列為獨立的「非互動提示」類，或放寬判準並改正計數。
- 🟢 `spec.md:REQ-9` — 入口站已釘，但 Task A 的入口站是 write-plan，而決策點①（intent 確認）發生在其**上游**；摘要表只要求「接下來會經過的站」，冷讀者恐無法從 write-plan 單站答出「誰決定什麼」全貌。fix：摘要表改為涵蓋本 change 的完整站序（含上游已完成者）。

**spec_vs_intent**：consistent — 跨 vendor 選配、至多一次、Acceptance #6 以各站 SKILL.md 為對象三處皆與重確認後的 intent 逐字對齊；Acceptance #1/#3/#4/#5/#6/#7 各有對應 REQ。

**verdict**：PASS_WITH_NOTES — 對方的 🔴 fatal 已死、雙方 r3 所有 still-open 全關；三條新發現皆為契約層同步／分類瑕疵，不阻擋落地，建議與落地首個 commit 合併修。

**what_i_did_not_read**：只開指派的六個路徑與指定的 `74229611..0f907d37` diff（另跑 `git log --oneline -3` 核對兩個 fix commit）。未再開 `evidence/ceremony-cost-old-vs-new.md`（本輪只驗 caveat 措辭，未重算 New model 欄）、未開 r1／r2 findings 檔與其餘 evidence、未開任何 loom plugin 原始碼；未重審 delta 未觸及的 §1–§3、§6、§7、§9、§10。未派 subagent，未修改任何檔案。
