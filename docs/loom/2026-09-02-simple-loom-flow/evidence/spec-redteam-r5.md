# spec 對抗（red-team）— round 5 — 2026-09-02

派工：opus，fresh context，verdict-only；read 四輪（r1–r4）之後、W0 build 期間補跑（checker 的 `intake.spec-pass` 要求 spec 有「讀＋對抗」兩種 probe，發現本 change 只有讀）。攻擊面：A–H 八個情境（平庸誠實 implementer／同 vendor 盲點／單向門誤判／決策點②隱藏設計／checkpoint 門檻／standing docs／硬切換／不可證偽 REQ）。

## verdict: NEEDS_REVISION

| id | 嚴重度 | 一句話 | 處置（commit 見 review.json SR5-xx） |
|---|---|---|---|
| H-1 | 🔴 | `probes[]` 的 package 測試結果由 agent 自填，REQ-6「不讀宣稱」自我否定 | 採納：checker 在乾淨工作樹自行執行 `command`，agent 的 `result` 只作記錄（§7；checker 追加） |
| C/D | 🔴 | 決策點過後浮現的單向門 agent 可自選承諾型預設（付費 API、帳號） | 採納：(b)(c)(e) 三類決策點後只能選零義務可逆預設（§4） |
| C-2 | 🔴 | 四類單向門全是「選型」，漏掉對既有資料的不可逆動作；盲跑在乾淨環境結構上碰不到 | 採納：類別 (e)，無岔路也必問；盲跑報告固定行「對你既有的資料做了什麼」（§4、§6、UI flow 3/4） |
| A-1 | 🔴 | repo 未宣告 mutation 工具時「對抗」等於零 | 採納：對抗 agent 自寫 ≥3 個可執行 abuse 案例進 `probes[]`（§6） |
| A-2/B-1 | 🔴 | `dismissed` 可由 implementer 自己下，且不進決策點③ | 採納：dismissed 只能由 dispatch 中的審查角色下（checker 重算）；important 以上進「我替你決定了」段（§5、§7） |
| H-2 | 🔴 | REQ-1 只限停點數，40 個問題也合規 | 採納：每個問題須可歸入三型或後果形，違者 user-judgment-leak 判 NEEDS_REVISION（§4、REQ-1） |
| B-2 | 🟡 | 5/7 致命只有一家 vendor 找到，建議句該用數字 | 採納：寫進 Design decision 與決策點①建議句（§5） |
| E-1 | 🟡 | checkpoint ≤5 觸頂無出口；after-task ≤2 硬帽 | 採納：修正輪不計；after-task 改預算＋理由行（§5） |
| E-2 | 🟢 | 大小當風險代理 | 接受風險；replay 時量「首輪 vs 後續輪 finding 比例」（plan W4-03） |
| F | 🟡 | ratified 但空洞的 PRINCIPLES 讓拒收閘與 conformance 變噪音 | 採納：ratified＝有行且 Non-negotiables ≥3；conformance 可回 N/A＋理由（§8） |
| G | 🟡 | 切換日：Codex 重授信、plugin 版本傾斜、舊 branch 首推被擋、DA 指向失效 | 採納：`requires-contract` 重算 BLOCK；REQ-2 明示重授信；舊 branch 出口；DA retired（§1、§10、REQ-2、plan W2-01/W3-01） |
| H-3 | 🟡 | `fresh-context` 不可重算 | 採納：降為 dispatch 記錄欄位（§7） |
| H-4 | 🟢 | REQ-10 的 #772 基線太鬆 | 接受風險；replay 三個分開呈現（plan W4-03） |
| H-5 | 🟢 | 「猜測」由受測者自評 | 採納：定義猜測＋派測者判（§12） |

原文（verbatim）：

> 三個攻擊在現行文字下擊穿 §0 目標敘述（品質不夠而使用者看不出來），且找不到任何既有機制接住：`probes[]` 是唯一擋在 push 前的品質證據卻是 agent 自填（H-1）、決策點後浮現的單向門被降級成 agent 預設（C/D 共根）、程式的「對抗」在沒有宣告工具的 repo 等於零（A-1）。三者的修法都很小（各一到兩句），不動架構。

（各攻擊故事全文保留在 session transcript；本檔只留裁定表與結論句，避免與 concept-model 重複。）

what_i_did_not_read（reviewer 自述）：evidence/ 全部、review.json 的 findings 內文、現行 loom 程式碼。
