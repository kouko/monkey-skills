# loom 目標概念模型 v5（一頁紙草稿）

日期：2026-09-02　狀態：草稿，未批准　對照組：Anthropic「The AI-Native SDLC Playbook」
v0 → v1：採「what/why vs how」切線（C）、loom-code 可獨立、intent schema 定案、新增 §7 准入規則。
v1 → v2：review 站改為 checkpoint review（§3i）；三種驗證動作＋按 artifact 型別觸發（§3j）；Q2 裁定（刪 batch）。
v2 → v3：Q3–Q6 裁定（常駐文件三段式、host hooks＋CI、delivery ticket＝intent、design 維持可選）；證據落點規則（§3k）。
v4 → v5：自審 8 項＋opus 對抗邏輯審 10 項（D1 verdict 入版控給 CI、D2 覆寫後重 probe、D3 kind 限定禁令、D4 拒收非擋 commit、D5 after-task wave 必審、D6 dismissed＋waiver 語意、D7 withdrawn 態、D8 18＋計數規則、D9 刪條件 (c)、D10 名詞數退出 CI）。
v3 → v4：Codex gpt-5.6-sol high 獨立審查（`inventory/independent-advisor-codex-run.md`）：修 5 項事實錯誤；採 #2 open_findings、#3 Task trailer＋兩暫態、#5 spec 先審、#6 action 分類；裁 #1 逃生口保留、#4 BLOCK＋probe＋CI digest、#10 准入改 AND。

## 1. 現況（盤點結果）

| | loom-code | loom-design | loom-workflow | 合計 |
|---|---|---|---|---|
| skill | 14 | 10 | 12 | 36 |
| 寫出的 artifact 種類 | 13 | 11–13 | 14 | ~38 |
| 引入的專有名詞 | 44 | 44 | 25（清單實列約 38，待重數） | ≈113 |
| 不產 artifact 的 skill | 4 | 1 | 5 | 10 |
| 產物沒有下游讀者的 skill（含 router／chat-only／自用檔，非 17 種孤兒 artifact） | 6 | 3 | 8 | 17 |

現況鏈（實際接線，不是文件宣稱）：

```
[對話中的 seed] ─┬─ design 側：discovery(無下游) → PRINCIPLES → DESIGN/ui-flows
                 │            → proposal+specs(+critic 就地增補) → change-folder ─┐
                 └─ code 側：brainstorming → brief(Problem…Decision) ───────────┤
                                                                               ▼
        plan.md（一檔六角色：DAG／Status／Decision Log／Review Batches／Stage／kickoff）
                                                                               ▼
        SDD：task → implementer + 2 reviewers（或 batch packet/receipt）→ commit
                                                                               ▼
        review-pass.json + verified.json + waiver.json ──→ git-guard ──→ push/PR
                                                                               ▼
        finishing：memory／backlog／INDEX／archive
```

對照組（Anthropic）：

```
intent.md(人寫) → spec.md(Claude 寫) → plan.md → diff/PR → review findings → incident→intent.md
   PO 批          PO 批               工程師批    code owner 批   release mgr 批(hook)
治理三層：skills=建議性 ／ hooks=決定性(allow/ask/block) ／ git=稽核軌跡
```

## 2. 六個結構性診斷

1. **intent 沒有家**。design 側 seed 只在對話裡；code 側 intent 混在 brief 裡跟 Decision 同居；backlog entry 是第三個半成品。
2. **plan.md 一檔扛六角色**，五個 skill 用不同腳本改同一檔的不同段——名詞爆炸的物理來源。
3. **審查有六種 reviewer、兩套 critic、一套 batch 機制**，對照組只有「每個 PR 一次相同的 agent 審查 + 一個人批」。
4. **三個 gate marker、一個讀者**（git-guard）。
5. **10 個 skill 不產 artifact**——它們是行為規則，不是流程站，卻和站平起平坐佔 skill 名額。
6. **17 個 skill 的產物沒有自動下游**（其中含 router／chat-only／自用檔；真正宣稱「informs 下游」卻無接線的是 discovery 三檔、completeness-critic verdict、HANDOFF、cot-explain）。

根因不在 plugin 切法，在 artifact 切法：brief 同時裝「要什麼」和「決定怎麼做」，誰擁有它都會混。

## 3. 目標模型

### 3a. 切線：what/why 對 how

| plugin | 回答 | 站 | 安裝 |
|---|---|---|---|
| **loom-design** | 要什麼、為什麼、應該長怎樣 | capture-intent／write-spec（＋PRINCIPLES／DESIGN 產生器） | 可選 |
| **loom-code** | 怎麼做 | write-plan／build／review／ship／maintain ＋ hooks ＋ 紀律 reference ＋ **intent/spec 檔案契約與 checker** | 可獨立 |
| **loom-workflow** | 使用者點名的工具 | decision-map／handoff／recap／cot-explain／distill／git-memory／independent-advisor／critique | 可選 |

依賴只有一個方向：loom-design 依賴 loom-code 提供的 **versioned contract package**（intent／spec schema、checker、relay 散文）；loom-design 寫檔、loom-code 讀檔，沒有反向呼叫。契約由消費者定義（consumer-driven）：schema 與 checker 住在 loom-code；loom-design 的站是「產生這個格式的比較好的方法」。仍需同步的東西明列：checker（design 側呼叫 code 側的同一支）、family-relay／plain-relay。loom-workflow 的 decision-map 也依賴同一個 contract package（它會寫 intent.md）。

**Codex 的 repo 級接線**（無 init 原則）：adopting repo 的 `.codex/hooks.json` 與 checker 副本由 loom-code 的站在第一次碰到 repo 時 lazy 寫入，帶版本戳；站每次比對版本戳，舊了就覆寫（覆寫＝hook 定義變 → Codex 要求重新 `/hooks`，這是預期行為）。**覆寫後站必須立刻重跑 probe 並停止本次執行**，直到使用者重新 `/hooks`；不得在同一次執行裡繼續（opus D2：否則覆寫到下次 probe 之間整段無閘門）。CI 的 digest 檢查比對的是 adopting repo main 上的副本（完整性），版本戳比對 plugin 版本（漂移只 WARN）。

### 3b. Artifact：core per-change 五種 + git（全家族仍有 memory、standing docs、map、evidence、工具產物；「38 → 5」只指 per-change 核心）

| artifact | 誰寫 | 誰批 | 位置 | 吸收現況的什麼 |
|---|---|---|---|---|
| **intent.md** | 人（capture-intent 站訪談後寫，或手寫；維護迴圈時由 agent 寫；地圖開的 delivery 片） | 使用者 | `docs/loom/intent/<change-id>.md` | brief 的 Problem／Users／Smallest End State／Out of Scope；design 的 seed；backlog entry；decision-map 的 delivery ticket；business-value 的 GO/NO-GO 變成 intent 的一段 |
| **spec.md** | Claude，套 standing docs | 使用者 | `docs/loom/<change-id>/spec.md` | brief 的 Decision／Alternatives／Current State Evidence；spec-expansion 的 proposal+specs；ui-flows 的變更部分 |
| **plan.md** | Claude | 使用者 | `docs/loom/<change-id>/plan.md` | Task DAG（每 task 穩定 ID）／檔案／測試／風險；**`needs-design: no`（無 spec）時，plan 前段必含 brief 的 Current State Evidence（Forward／Reverse／Error／Data／Boundary 五條，各附路徑與錨點）**，否則拆任務沒有事實基礎。Status、Decision Log、Review Batches、Stage 全部**移出**：進度由 commit 的 `Task: <id>` trailer 派生（script 生成 view），決策＝git-memory trailer。保留兩個尚無 commit 的暫態 `claimed(@branch)`／`blocked(<reason>)`，寫在 plan 該 task 行，供平行派工用（Codex 分歧點 #3） |
| **diff / PR** | Claude | 使用者 | git | 不變 |
| **review findings** | review 站（一份契約，三種動作，見 §3i／§3j） | 使用者 | **`docs/loom/<change-id>/review.json`（被 commit；verdict＋reviewed_sha＋open_findings）**；`.git/loom/ready.json` 是它的本機鏡像給 hook 用；PR thread 為副本 | 取代 spec/quality/code/docs 四份 verdict 契約 + batch packet/receipt + 三個 marker |
| **memory** | Claude | — | git trailers + `docs/loom/memory/` | 不變；backlog 併入 intent（一條 backlog＝一個未批的 intent） |

Standing docs（不是 per-change artifact，等同 CLAUDE.md 地位）：`PRINCIPLES.md`、`DESIGN.md`、`KICKOFF-DEFAULTS.md`。

**Q2 已裁**（見 §5）：刪 Review Batch 與常態 per-task 審查，採 §3i checkpoint review（含 `review: after-task` 逃生口）。

### 3c. intent.md schema（loom-code 擁有）

```
# <title>
originator: <who>            # 人名或 "maintenance-loop"
kind: product | engineering  # product：Problem 段禁程式識別字；engineering：Problem 段允許路徑與識別字（工程問題本來就長那樣）
needs-design: yes | no — <reason>
map: <map-id>               # 可選；有則此 intent 是該地圖的一片交付（Q5）
evidence: [<paths>]          # 可選；引用 docs/loom/<change-id>/evidence/ 或常駐證據，write-spec／review 必須真的讀

## Problem        ← 只寫問題與誰受影響。`kind: product` 時禁：檔案路徑、函式／類別識別字、腳本檔名（regex 可抓；checker 擋）；`kind: engineering` 不禁。口語機制名（「git helper」）兩者皆不禁
## Proposed outcome  ← 允許方向與解法形狀（「helper 只有一份」「add 指令接受 --due」）；engineering 可含檔名
## Constraints
## Value case      ← 可選；吸收 business-value 的 GO/NO-GO 與理由（product 才需要）
## Out of scope
## Open questions
```

- `needs-design: yes` 當任一成立：(a) 動到使用者看得到的介面且無 DESIGN.md／ui-flows 覆蓋；(b) 多狀態或多物件行為且無 spec。否則 `no`。（原 (c)「product-shaped 且無 PRINCIPLES.md」刪除：Q3 的拒收已覆蓋，且 product 缺憲法根本到不了 spec 站，條件不可達——opus D9。）所有 `kind` 套同一判定；bug fix／refactor 通常落在 `no`，但碰到 (a)–(c) 任一仍是 `yes`。
- (a) 可機械查（檔案存不存在），(b) 是判斷。防 agent 代決的保險是機械的：checker 要求 `needs-design` 行必須帶 `— <reason>`，且 intent 的 commit message 必須含同一行（進 git 稽核）；缺任一就擋 commit。**未簽核的 intent 可以 commit**（那就是 backlog 的一條）；`Approved-by:` 不是 commit 的條件，而是 **write-spec／write-plan 拒收沒有它的 intent**。「使用者真的讀了」無法機械化，這裡不假裝可以——跟今天一樣靠簽核習慣。
- 工程意圖通常三到五行，手寫比訪談快；這是正常路徑，不是降級。

### 3d. Skill 三分類

| 類 | 定義 | 目標數 | 現況對應 |
|---|---|---|---|
| **站 (station)** | 產出 3b 某一個 artifact | 7：capture-intent／write-spec（design，spec 含 UI flows 段）；write-plan／build／review／ship／maintain（code） | brainstorming＋discovery＋spec-expansion＋writing-plans＋SDD/TDD＋4 reviewer＋finishing |
| **紀律 (discipline)** | 建議性規則，無 artifact | 1 份 reference（不是 skill）：engineering-baseline＝**tdd-iron-law 與 systematic-debugging** 的純規則 | 只有這兩個是純散文 |
| **站內動作 (action)** | 站呼叫的可執行步驟，有輸入輸出與失敗語意，不是 skill | verification-before-completion → review 站的「盲跑」；ui-verification → 同上（GUI）；dispatching-parallel-agents、using-git-worktrees → build 站的派工 helper | 這四個會改 plan／git 狀態或產 marker，不能降為散文 |
| **工具 (tool)** | 使用者點名才跑，或被站以機械條件叫起 | ~10 | loom-workflow 現有大多數；product-principles、design-system（常駐文件產生器） |

36 → **18**（站 7、工具 10、reference 1；action 不計）。名詞目標 **≤ 35，計數規則**：只數 artifact 名、站／工具／action 名、schema 頂層欄位名、狀態物件名（ready.json／review.json／waiver／open_findings 等）；**不數**欄位子值（waiver 的五個欄位）、型別列舉值（code／ui／spec…）、既有 git 詞（trailer、HEAD）。本頁自數約 33。

### 3e. 治理三層（照對照組）

- **建議性**：skill 散文＋standing docs。不再用散文當閘。
- **決定性**：hooks（契約與腳本歸 loom-code；Codex 側為 repo 內副本）。兩支 checker：**intent checker**（product 的 Problem 段禁程式識別字；`needs-design` 行帶理由且進 commit message；product 且無 ratified PRINCIPLES.md → **下游站拒收**，不擋 commit；`Approved-by` 缺 → 下游站拒收）與 **git-guard**（只認一個 marker `<git-dir>/loom/ready.json`：verdict 覆蓋 HEAD、`open_findings` 為空、waiver 若有則 head 未變；三合一）。
- **稽核**：git。plan 進度、決策走 commit/trailer。**waiver** 是 review.json／ready.json 內的 head-bound 物件：`{approver, reason, gates ⊂ {verdict-coverage, open-findings}, expected_head, expiry: <date>, consumed: bool}`；命中的 gate 該次豁免，`consumed` 在一次成功 push 後置 true；checkpoint 覆寫不動 waiver；HEAD ≠ expected_head 即刪除（Codex finding #3、opus D6）。

### 3f. 人類簽核點：常駐文件批准後，每個 change 最多四個、最少三個

intent → (spec) → plan → PR。spec 站只在 `needs-design: yes` 時存在。首次建立 PRINCIPLES.md／DESIGN.md 的 ratify 是 repo 級 bootstrap，另計。**批准不是 commit**：每次批准要有 `Approved-by: <name> <date>` trailer（intent／spec／plan 的 commit）或 PR 的 approval 事件；checker 認 trailer，不認「有 commit 就算批」。其他所有「問使用者」（on-ramp 選擇、kickoff briefing、batch checkpoint、waiver）要嘛併進這幾點，要嘛變 standing default。

### 3g. 入口與兩種安裝模式

| | 有裝 loom-design | 只裝 loom-code |
|---|---|---|
| 入口 | capture-intent 站 | write-plan 站：讀 `docs/loom/intent/<change-id>.md`，沒有就停下來要（給模板） |
| `needs-design: yes` | 走 spec 站 | 大聲 N/A：「這份 intent 要設計，請裝 loom-design 或手寫 spec.md」 |
| `needs-design: no` | 交 loom-code | 直接 plan |
| intent checker | 兩邊都跑 | loom-code 跑 |

沒有獨立 router，沒有先於 intent 的 reception。現況 on-ramp 表 1–3 列＋negative guard 收進 `needs-design` 規則；4–6 列降為 standing default 或工具建議。

### 3h. 命名與落地慣例

- `<slug>`＝標題 kebab-case；`<change-id>`＝`<date>-<slug>`；intent 檔名與 `docs/loom/<change-id>/` 同名，一眼對得回。
- intent.md／spec.md／plan.md 都是**被 commit 的檔案**；稽核軌跡＝該 commit 的 `Approved-by:` trailer，不是 commit 本身。
- `<git-dir>/loom/ready.json` 在 `.git/` 內，不入版控；它鏡像 `docs/loom/<change-id>/review.json`（入版控）。**寫 review.json 的 commit 只准動這一個檔**，CI 檢查：`review.json.reviewed_sha == HEAD^`（或 == HEAD 當 HEAD 沒有 review commit）且 `open_findings` 為空——這就是 review 閘門的 CI 兜底（opus D1：否則 CI 只能驗 checker digest，review 閘門在未授信 Codex 上會靜默失守）。

### 3i. review 站＝checkpoint review（不是單次，也不是 per-task）

- **一份契約**：verdict schema、`reviewed_sha`、輪次規則只有一套。鏡頭可以多個（code 11 維、docs 5 維，按檔案型別選；spec-conformance 併為一維；correctness 必跑 probe），結果彙整進同一份 verdict。
- **何時跑（機械）**：每個 wave 結束時算 `git diff <reviewed_sha>..HEAD --stat`；未審 delta **任一**超過門檻（8 檔 **或** 400 行——**實驗預設**，無量測依據；落地後用歷史分支 replay 量 defect catch／review 次數／重工後再固定，數字在 KICKOFF-DEFAULTS）才跑，否則累積（不限一跳，直到跑過 checkpoint 才歸零）；branch 結束必跑。`reviewed_sha` 初值＝branch base。plan 深度 ≤ 5（writing-plans 既有規則，非本次證據）⇒ checkpoint ≤ 5 次，小工程自然只有 1 次。wave＝plan DAG 同一層可平行的 task 集合（writing-plans 既有定義）。
- **spec 先審再批**（Codex 分歧點 #5）：`needs-design: yes` 時，spec.md 首次簽核前必跑一次 spec 型別的「讀＋對抗」（同一契約），PASS 後 write-plan 才開始；build checkpoint 之後只審 spec 的 delta。這保住現況 design-critic 在 spec 前、completeness-critic 在 plan 前的時序。
- **提前觸發（逃生口）**：plan 的 task 可標 `review: after-task`；build 站在該 task commit 後立刻跑一次**同一套** checkpoint（同契約、同 reviewer、同 `reviewed_sha` 規則），不是另一種 review。一個 plan 最多標 2 個，超過要在 plan 裡寫理由（checker 數）。**含 after-task 的 wave，wave 結束一律跑 checkpoint（不論門檻）**，因為提前審查推進了 `reviewed_sha`，剩餘 delta 可能低於門檻而漏掉跨任務一致性（opus D5）。落地後用歷史分支 replay 量 checkpoint 版本的漏失率，數字進 evidence。
- **第 N 次審什麼**：`reviewed_sha` 之後的 delta ＋ 跨任務一致性 ＋ 回歸 probe。修 findings 的 commit 就是下一個 delta。
- **狀態**：`reviewed_sha` ＋ 最小 `open_findings`（每條：穩定 id、anchor、來源 SHA、解決證據）。**只有 PASS／PASS_WITH_NOTES 才推進 `reviewed_sha`**；NEEDS_REVISION 不推進，下一輪必須逐條關閉 `open_findings` 才能推進（Codex 分歧點 #2）。關閉有兩種：`resolved: <evidence>`（reviewer 確認修了）或 `dismissed: <reason>`（reviewer 或使用者判定無效／範圍外／程式已刪；記進 verdict 供稽核）。ready.json 每次 checkpoint 覆寫其餘欄位；git-guard 問「verdict 覆蓋到 HEAD 且 open_findings 為空嗎」。沒有 packet／receipt／apply-result／ledger。
- **邊界**：task 3 的錯要到該 wave 結束才抓到，重工可能波及同 wave 後面的 task；wave 大小就是旋鈕。

### 3j. 三種驗證動作＋按 artifact 型別觸發

| 動作 | 做什麼 | 程式專案 | 設計專案 | skill／規則 |
|---|---|---|---|---|
| **讀** | reviewer 對 delta 跑維度 | code 11 維 | docs 5 維 | docs 5 維 |
| **盲跑** | 沒寫它的 agent 只拿 artifact 執行，對照 acceptance criteria，不修只報 | 乾淨環境 build／跑／點 UI／截圖 | 冷讀者拿 spec／ui-flows 走一個情境 | 冷讀 agent 照 SKILL.md 做一個真實任務 |
| **對抗** | 主動弄壞、繞過、誤用；成功的攻擊進目錄 | mutation／fuzz／abuse case／安全 | red-team spec：未定義狀態、衝突需求、惡意路徑 | gate 繞過（ATTACK-CATALOGUE） |

- 三者共用 verdict schema，結果都進 ready.json。寫的人不能自己驗（separation of duties）。
- **觸發（機械）**：repo 在 KICKOFF-DEFAULTS 宣告路徑 → artifact 型別（code／ui／spec／skill／gate）；**未宣告時預設（依優先序）：`docs/loom/intent/**`＝intent、`docs/loom/<change-id>/spec.md`＝spec、`docs/loom/<change-id>/plan.md`＝plan、`docs/loom/PRINCIPLES.md`／`DESIGN.md`／`KICKOFF-DEFAULTS.md`＝standing、`docs/loom/memory/**`＝memory、`**/evidence/**`＝evidence（不審）、`**/SKILL.md` 與 `agents/*.md`＝skill、`hooks/**` 與 `scripts/check_*`＝gate、`docs/loom/maps/**`＝map（docs 維度）、其餘 `*.md`＝docs、其餘＝code**。intent／spec／plan／standing／skill／map／docs 用 docs 維度；code／gate 用 code 維度。checkpoint 時 checker 看 delta 碰到哪種型別決定跑哪幾個動作；code 型別的「盲跑」＝**package 級測試必跑**（現況 verification-before-completion），app 級盲跑（build／跑／點 UI）需 repo 宣告可執行入口。「對抗」按型別：spec → red-team、gate → 攻擊目錄、code → 只在 repo 宣告 mutation／fuzz 工具時跑；沒碰 gate 的 branch 不跑 gate 攻擊目錄。
- **目錄累積**＝Anthropic 的 continuous evals：每個事故變永久案例（eval suite／情境庫／ATTACK-CATALOGUE）。這是 §7 第三條的主要供給。
- 現況零件的歸宿：ui-verification、verification-before-completion → 盲跑；design-critic、completeness-critic → 設計的讀＋對抗；dogfood-skill-testing → 盲跑；adversarial-audit-station（finishing Step 3.5）→ 對抗，改為型別觸發而非每支 branch 固定一步。

### 3k. 證據落點

證據不是第六種 artifact（無 schema、無簽核、無消費者），是附件。規則一條：**跟著它支撐的 artifact 住**——某個 change 的證據放 `docs/loom/<change-id>/evidence/`；repo 級常駐證據（ATTACK-CATALOGUE、eval 目錄、harness 審計）放 `docs/loom/evidence/`。現況 discovery／research／audits／dogfood／harness-audit／task-batch-review／firing-corpus 七個目錄收成這兩處；user-insights 的研究導向某份 intent 就進那個 change，否則是常駐證據。本 change 的 `inventory/` 將搬到 `docs/loom/<change-id>/evidence/`。

## 4. 明確刪除

- Review Batch／packet／receipt／apply-result 整套（≈4.2k 腳本 LOC＋6.9k 測試 LOC＋23 名詞；由 §3i 取代）
- verified.json／review-pass.json／waiver.json → ready.json
- plan 的 Status／Decision Log／Review Batches／Stage 段
- brief（拆成 intent + spec）、seed、backlog（併入 intent）
- family-reception 契約（router 只剩 capture-intent 與 write-plan 的檔案檢查，不需要共用散文）；family-relay／plain-relay（跨 plugin 共用的「怎麼跟使用者說話」散文：白話優先、名詞翻譯表）保留，仍需同步
- completeness-critic 與 design-critic 合併為 review 站對 spec 型別的「讀＋對抗」動作
- docs-reviewer 的 delta 封包確認協定（第 N 輪只審 delta 已是 §3i 通則）
- adversarial-audit-station 作為 finishing 固定步驟（改為 §3j 型別觸發）
- tdd-iron-law、systematic-debugging 降為 reference；verification／ui-verification／parallel-agents／worktrees 改為站內 action（不佔 skill 名額）

## 5. 未決（需使用者裁定）

- ~~Q1 plugin 數~~ → **已裁：維持三個，切線＝what/why vs how（§3a）**。family-relocation 地圖目的地不變。
- ~~Q2 per-task 審查~~ → **已裁：刪 Review Batch 與 per-task 作為常態層，採 §3i checkpoint review；保留 `review: after-task` 逃生口（同契約提前觸發，每 plan ≤ 2）**（Codex 獨立審查分歧點 #1 後修訂）。證據：`inventory/q2-per-task-review-evidence.md`（14 plan：per-task 可歸類案例 4 例＝2 例 NEEDS_REVISION ＋ 2 例 PASS_WITH_NOTES 的 probe 發現，後兩例靠 reviewer 主動 probe 抓到——屬 reviewer 行為非層的性質；反向 memory 5 條、正向 0 條）；`inventory/batch-review-mechanism.md`（batch：11k LOC、23 名詞、8 天 5 個修正版、真實採用 6/268、無任何 harness 觀測的淨節省，招牌數字 10→2 被自己的 backlog 註明不可引用）。
- ~~Q3~~ → **已裁**：product-principles／design-system 是**工具**（常駐文件不在五種 artifact 內，產生它們的不是站）；interaction-flows 併入 write-spec 的 UI 段（ui-flows 與 spec 同生命週期），design-critic 的 Nielsen lens 搬進 review 站對 spec 型別的維度。存在與批准由 intent checker 管，三段式：
  - **勸導（每份 intent）**：repo 缺 PRINCIPLES.md 或 DESIGN.md → checker 印固定三行 WARN（exit 0），列缺哪份、為什麼、該跑哪個工具；capture-intent／write-plan 必須原樣呈現。
  - **擋（只有一種情況）**：`kind: product` 且 repo 無 ratified 的 PRINCIPLES.md → write-spec／write-plan **拒收**這份 intent（憲法必須先於 spec）；intent 本身仍可 commit 進 backlog，也可先簽 Approved-by，只是走不下去。沒裝 loom-design 時，PRINCIPLES.md 可照 loom-code 附的模板手寫，只要有 `ratified-by` 行；不是死路。**DESIGN.md 永不擋**：條件 (a) 因為缺 DESIGN.md 而讓 `needs-design: yes`，write-spec 的 UI 段就是這次 change 的設計覆蓋，DESIGN.md 只由 WARN 建議。engineering intent 永不因此被擋。
  - **靜音（一次性）**：KICKOFF-DEFAULTS 記 `standing-docs: waived — <reason> (<date>)`（純 CLI／個人腳本），WARN 不再印。
  - 文件必須有 `ratified-by: <name> <date>` 行才算存在（工具產草稿時留空，使用者填了才過）。消費端：write-spec 載入為 standing docs；review 站 `principles-conformance` 已有，加對稱的 `design-conformance`。取代 on-ramp 表第 1、2 列。
- ~~Q4~~ → **已裁：host hooks 為主、CI + branch protection 兜底、不做 git hook**。證據：`inventory/q4-industry-gate-research.md`（Codex hooks 已官方化、與 Claude Code 同形狀；git hook 有 `--no-verify` 六種繞法與 worktree `core.hooksPath` 失效兩個實據硬傷）、`inventory/q4-codex-hooks-live-test.md`（codex-cli 0.151.0 五次實跑：授信後擋得住、worktree 正常、payload 同形；**未授信時靜默跳過**；**授信後改 script 內容仍照跑**）。
  - Claude Code：plugin hooks，零動作。Codex：repo 內 `.codex/hooks.json` 呼叫同一支 checker，shim 依實測 payload 重寫、fail-closed。
  - Codex 授信：每 repo 每 hook 版本使用者跑一次 `/hooks`（Codex 安全設計，loom 不能代做）。**偵測用真實 probe、結果是 BLOCK**（Codex 獨立審查分歧點 #4 後修訂）：站第一步派一個必被擋的假指令（例如含固定標記的 no-op），沒被擋就代表閘門無效 → 站拒絕往下走，訊息指名「請在 Codex 跑 /hooks 授信」。不讀 `hooks.state`，因為條目只證明定義受信。
  - **checker 完整性**（run E 實測：授信後只改 script 內容照跑不重審）：checker 留在 repo，**CI 驗 checker 檔的 digest 對 main 版本**；工作分支改了 checker，PR 即紅。這是既有 CI 層的一條規則，不是新機制。
  - 未驗證：使用者自寫 `~/.codex/requirements.toml` 是否被認為 managed（免授信）。動全機設定，需使用者同意後測。
  - 對 family-relocation 的影響：F-7（sibling-root 探索）對 hook 不再重要，因為 repo 級 hooks.json 用相對路徑；「hooks 先搬 loom-workflow」那一刀的必要性要重估。
- ~~Q5~~ → **已裁（B）：delivery ticket 消失，由 intent.md 接手；grilling／research／prototype 三型留在地圖（它們是問題，不是改動）**。
  - 地圖要交付一片 → 直接寫 `docs/loom/intent/<change-id>.md`，帶 `map: <map-id>` 欄位；MAP.md 列 change-id。沒有 `map:` 的 intent 是普通改動，地圖不管。
  - 狀態派生、不另立帳：未簽核＝open、簽核＝claimed、PR merged＝closed、**檔案刪除或標 `status: withdrawn — <reason>`＝closed**（opus D7：否則永不簽核的 intent 無出口）；phase 由 `docs/loom/<change-id>/` 下 spec／plan 存在與否及 PR 狀態算出。`blocked` 等細態降為 intent 欄位或 Open questions。
  - 刪：`start_delivery` 雙向綁定、`DeliveryClosureInputs`、delivery phase 帳本；地圖對 intent 唯讀（開檔後所有權歸 loom-code）。地圖名詞約 10 → 5。順帶解 backlog「Map claims collide at merge not runtime」（intent 一 change 一檔，不撞）。
  - 損失：地圖狀態機對 delivery 的細粒度拒絕（claim blocked、close da-gap）要重寫成 checker 對 intent 欄位＋git 狀態的查詢。
- ~~Q6~~ → **已裁（A）：loom-design 維持可選**。理由：預設安裝不改變觸發條件（只在 product intent 且 `needs-design: yes` 時被用），解不了「用得少」；「太輕」是相對於治理膨脹的 loom-code，砍完比例回正。量測：CHANGELOG 加記「本版期間 `needs-design: yes` 的 intent 數」，連續為零時該問的是留不留，不是預設裝不裝。設計側若缺具體能力，另立 intent 逐項列，不在本題。

## 6. 驗收方式

冷讀者（fresh sonnet）只拿這頁，能在 10 分鐘內對一個給定任務說出：會產生哪些檔、誰批、哪個 hook 擋什麼。答不出的地方＝這頁的缺陷。v0 實測 12–15 分鐘，四個缺陷已修。v1 實測約 12 分鐘：兩條路徑皆正確；三缺陷已修。v3 實測約 15 分鐘：兩條路徑、checkpoint 算術（3+10=13>8 → wave 2 後一次；branch 尾一次）、Codex fresh clone 無閘門皆答對；抓到 DESIGN.md 擋／不擋循環、門檻 OR/AND 與累積跳數未定、`reviewed_sha` 初值、ready.json 覆寫、型別預設對映未定——全部已修。仍未達 10 分鐘；主因是 §5 的裁定散文與 §3 規則交叉引用，落地時應把 §5 併回 §3 成純目標文件。

## 7. 准入規則（防止長回去）

heavy 的成因是「事故 → 新機制」這條生成規則，不是任何一個機制。砍完不立這條，半年回原點。

**新增任何機制（skill、reference、checker、gate、hook、schema 欄位、名詞）必須同時滿足兩者**（Codex 獨立審查分歧點 #10 後由三選一改為兩者皆須）：

1. **有 regression eval**：附一個回歸案例（程式＝測試，跑 CI；閘門＝攻擊案例，跑 CI；散文規則＝§3j 的冷讀 dogfood 案例，需模型執行，跑排程 eval suite 而非每 PR）。
2. **淨數不增**：同一個 PR 刪掉或合併至少一個既有機制；做不到時寫 **明示 budget 例外**（一行理由，進 CHANGELOG），例外本身可被看見與統計。

決定性（hook／checker）不再是獨立的准入理由，只是機制的形式要求：新閘門仍必須是決定性的，但「決定性」不能換到免刪舊機制。

**不再新增散文閘。** 事故的預設處置是：寫進 memory（一次）→ 變 eval（兩次）→ 才考慮 hook（需判斷的性質永遠不上散文，見 memory「需判斷的散文死、指向可查動作的散文活」）。

**量測面**（每次 bump 時記在 CHANGELOG）：skill 數、artifact 種類數、session-start 注入字數、`needs-design: yes` 的 intent 數、**未簽核 intent 數**（opus D7）——這五項 CI 可算；名詞數依 §3d 計數規則**手數**，只進 CHANGELOG 不進 CI（opus D10：腳本算不出「名詞」）。任何一項上升需在 PR 註明取代了什麼。

這條規則本身是散文，所以它的執行靠機械層：**CI 腳本計算五項可算指標**（skill 數、artifact 種類數、session-start 注入字數、`needs-design: yes` intent 數、未簽核 intent 數），任一項超過 main 基線且 PR 沒有 budget 例外行就紅；PR 模板一行「本 PR 新增機制取代了：___」只是給人看的，不是執行層。
