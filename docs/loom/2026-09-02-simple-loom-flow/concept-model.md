# loom 目標概念模型 v10

日期：2026-09-02　狀態：目標文件　對照組：Anthropic「The AI-Native SDLC Playbook」
推理過程與作廢版本見 `evidence/`（現況診斷、v5 裁定、v7 人審版、Codex 兩輪、opus 邏輯審、紅隊、儀式成本量測）。本文只寫目標。

## 0. 目標與威脅模型

**loom 的目標**：假定使用者只具備基本軟體工程知識，盡量自動化判斷並維持高品質的實作，避免讓使用者做過多的決策。

由此推出三件事：

1. 使用者**不能**判斷 spec／plan／diff 的品質，所以人類簽核沒有品質意義；人只回答「這是不是我要的」——在 intent（要什麼）、product 的 spec 可見行為（操作與反應）、驗收（做到了嗎）三處。
2. 品質的唯一來源是**機器**：寫的 agent ≠ 審的 agent（≥2 個 fresh context；第二家 vendor 由使用者選，機制每 change 至多建議一次）、沒寫過它的 agent 盲跑、一個 agent 試著弄壞它、每個事故變永久 eval。
3. 主要威脅是**agent 品質不夠而使用者看不出來**，不是 agent 繞閘（沒有人在審，就沒有冒充人的問題）。決定性層擋的是手滑，不宣稱擋作弊；需要作弊防護的多人 repo 另加 branch protection，不在本文。

## 1. Plugin 與依賴

| plugin | 回答 | 內容 | 安裝 |
|---|---|---|---|
| **loom-design** | 要什麼、為什麼、應該長怎樣 | 站：capture-intent、write-spec；工具：product-principles、design-system | 可選 |
| **loom-code** | 怎麼做 | 站：write-plan、build、review、ship、maintain；checker；host hooks；reference 一份；intent／spec／plan／review 的檔案契約 | 可獨立 |
| **loom-workflow** | 使用者點名的工具 | decision-map、handoff、recap、cot-explain、distill、git-memory、independent-advisor、critique | 可選 |

- 依賴單向：loom-design 與 loom-workflow 依賴 loom-code 的 **versioned contract package**（schema、checker）；兩者各宣告 `requires-contract: >=<major>.<minor>`，站點啟動時對 manifest 版本重算，不符→BLOCK 印「請更新 loom-code」。design 寫檔、code 讀檔；decision-map 寫 intent.md；沒有反向呼叫。
- 契約由消費者定義：schema 與 checker 住在 loom-code；loom-design 的站是「產生這個格式的比較好的方法」。
- 仍需同步的功能副本，明列：checker（Codex scaffold 的 repo 內副本）。除此之外沒有。

## 2. Artifact

### 2a. core per-change 五種 ＋ git

| artifact | 誰寫 | 人類介入 | 位置 |
|---|---|---|---|
| **intent.md** | 人（capture-intent 訪談後寫、手寫、decision-map 開的交付片、maintain 站的 agent——同一 alert 已有 open intent 時只更新 evidence） | **決策點 ①**：使用者確認「這是我要的」 | `docs/loom/intent/<change-id>.md` |
| **spec.md** | Claude，套 standing docs；含 UI flows 段 | **決策點 ②（只在 `kind: product`）**：使用者確認可見行為——Requirements 與 UI flows 用白話呈現，Design decision 以下不呈現；engineering 不問 | `docs/loom/<change-id>/spec.md`（只在 `needs-design: yes`） |
| **plan.md** | Claude | 無；agent-decided | `docs/loom/<change-id>/plan.md` |
| **diff / PR** | Claude | **決策點 ③**：使用者讀盲跑報告後驗收 | git |
| **review.json** | review 站 | 無 | `docs/loom/<change-id>/review.json`（入版控；`.git/loom/ready.json` 為本機鏡像）|

memory（git trailer ＋ `docs/loom/memory/`）與 standing docs（`PRINCIPLES.md`、`DESIGN.md`、`KICKOFF-DEFAULTS.md`）不是 per-change artifact。evidence 是附件（§9）。

### 2b. intent.md schema（loom-code 擁有）

```
# <title>
originator: <who>            # 人名、"maintenance-loop"、或 map:<id>
kind: product | engineering
needs-design: yes | no — <reason>
map: <map-id>                # 可選
evidence: [<paths>]          # 可選；write-spec／review 必讀
status: open | confirmed <date> | withdrawn — <reason>   # 缺＝open

## Problem            ← 問題與誰受影響，白話。product：禁檔案路徑、函式／類別識別字、腳本檔名（checker 擋）；engineering 不禁
## Proposed outcome   ← 方向與解法形狀
## Acceptance         ← 使用者看得懂的驗收條件：「做完後我可以…」，每條可被盲跑證明
## Constraints
## Value case         ← 可選；product 的 GO/NO-GO 與理由
## Out of scope
## Open questions
```

- `needs-design: yes` 當任一成立：(a) 動到使用者看得到的介面——任何使用者讀或輸入的表面（GUI、TUI、CLI 參數與輸出、對外 API）——且無 DESIGN.md／ui-flows 覆蓋；(b) 多狀態或多物件行為且無 spec。否則 `no`。所有 kind 同一判定。(a) 由 checker 對 repo 宣告的介面表面 glob **重算**，agent 標 `no` 而 diff 碰到就擋。
- **決策點 ①**：用白話覆述 Problem／Acceptance 給使用者，使用者說「對」→ agent 寫 `status: confirmed <date>`。這個「覆述並確認」是 contract package 裡的 **action**，不屬於任何一站：有 loom-design 時由 capture-intent 做；只裝 loom-code 時由 write-plan 在收到未確認的 intent 時做（先確認再拆任務）。這是記錄，不是防偽。未確認的 intent 可以 commit（backlog）；write-spec／write-plan 只收 confirmed 的。
- `needs-design` 行必須帶理由，且 intent 的 commit message 含同一行。
- 狀態：open → confirmed → closed（PR merged）；withdrawn＝closed。
- 工程意圖通常三到五行，手寫比訪談快。

### 2c. spec.md schema

```
# <title>
intent: <change-id>@<sha>
## Requirements        ← REQ-<n> — <name>，每條可驗，並對回 intent 的 Acceptance      【使用者可讀；product 時呈現給使用者確認】
## Design decision     ← 做什麼、不做什麼、為什麼；agent-decided 的岔路各附一句理由   【混合；不呈現】
## Alternatives considered                                                          【工程；不呈現】
## Current state evidence   ← Forward／Reverse／Error／Data／Boundary 五條，各附路徑與錨點 【工程；不呈現】
## UI flows            ← 有介面必填：每個操作與系統的反應（指令／畫面 → 輸出／狀態）；無介面 N/A 【使用者可讀；product 時呈現給使用者確認】
```

- **決策點 ②（product 限定）**：write-spec 完成後、spec 審查前，agent 把 Requirements 與 UI flows 用白話呈現（「你下 X 會看到 Y」），使用者說「對」或改；改了重寫再呈現。這是「行為是不是我要的」的確認，不是品質審查；Design decision 以下永不呈現。agent 寫 `confirmed-behavior: <date>` 進 spec frontmatter；write-plan 對 product 只收有此行的 spec。engineering 的 spec 不問，agent-decided。

### 2d. plan.md

Task DAG（每 task 穩定 ID）／檔案／測試／風險。`needs-design: no` 時 plan 前段必含 Current State Evidence。進度由 commit 的 `Task: <id>` trailer 派生；決策走 git-memory trailer。暫態只有 `claimed(@branch)`、`blocked(<reason>)`。task 可標 `review: after-task`。沒有 Status 帳、Decision Log、Review Batches、Stage。

### 2e. review.json ＝ ready.json

```
reviewed_sha         # 初值 branch base；只有 PASS／PASS_WITH_NOTES 推進
scope                # 這一輪審的是什麼（spec | code | …）
verdicts[]           # 每個 reviewer 一份：{reviewer, vendor, model, lens, verdict, dimension_scores, findings}
vendors[]            # 本次 checkpoint 用到的 vendor 清單（記錄，不是條件）
probes[]             # 實際跑過的 probe／測試／盲跑：{kind, command, sha, result, artifact}；sha == reviewed_sha
open_findings[]      # {id, anchor, origin_sha, raised_by, resolved: <evidence> | dismissed: <reason> by <who>}
questions[]          # 每個決策點問過的問題：{decision_point, text, type: what|behaviour|done|consequence}；§4 三型判準與 §11 提問數量測讀這裡
dispatch[]           # build／review 站每次派工一筆：{task, role: implementer|reviewer|blind-runner|adversary, agent_id, model, started, fresh_context}；push 規則 reviewer≠implementer 與 dismissed 身分讀這裡
```

寫 review.json 的 commit（review-only）只動這一個檔。push 時 HEAD 是 review-only commit 且 `reviewed_sha == HEAD^`。amend 或新增 code commit 後重跑 checkpoint。

### 2f. 命名

`<slug>`＝標題 kebab-case；`<change-id>`＝`<date>-<slug>`；intent 檔名與 `docs/loom/<change-id>/` 同名。intent／spec／plan／review.json 都是被 commit 的檔案。

## 3. Skill 四分類

| 類 | 定義 | 數 | 成員 |
|---|---|---|---|
| **站** | 產出 §2a 某一 artifact | 7 | capture-intent、write-spec（design）；write-plan、build、review、ship、maintain（code） |
| **工具** | 使用者點名，或被站以機械條件叫起 | 10 | loom-workflow 八個；product-principles、design-system |
| **reference** | 建議性規則，不是 skill | 1 | engineering-baseline＝tdd-iron-law ＋ systematic-debugging |
| **action** | 站內可執行步驟，不是 skill，不計 | — | package 測試、UI 盲跑、平行派工、worktree |

skill 36 → 17（7 站＋10 計數工具；另 1 個 reference 不是 skill，2 個 standalone 工具——goal-create、dbt-model-style——不計）。名詞 ≤ 40（計數規則：artifact 名、站／工具／action 名、frontmatter 與 JSON 頂層欄位名、狀態物件名；standalone 工具不計；不數段落標題、欄位子值、型別列舉值、git 詞、alias）。

## 4. 入口、路由、人類決策點

| | 有裝 loom-design | 只裝 loom-code |
|---|---|---|
| 入口 | capture-intent 站 | write-plan 站：讀 intent.md，沒有就停下來要（給模板） |
| `needs-design: yes` | write-spec 站 | write-plan 用 contract package 的 §2c 模板**自動產生最小 spec.md**（Requirements 從 Acceptance 派生、UI flows 從 intent 推），走同一個 spec 審查閘，`kind: product` 時使用者做決策點②，engineering 不問；印一行建議「裝 loom-design 可得到更完整的 spec」。使用者永遠不手寫 spec |
| `needs-design: no` | 交 loom-code | 直接 write-plan |
| checker | 兩邊都跑（同一支） | loom-code 跑 |

- 沒有獨立 router，沒有先於 intent 的 reception。
- **人類決策點**：engineering 兩個（① intent 確認、③ 驗收）；product 三個（加 ② spec 的可見行為確認）。plan 永遠由 agent 決定並記理由。
- **非決策型互動**只有一類、有入場判準：**不做就無法繼續的授權或缺件**（Codex 的一次性 `/hooks` 授信；缺 PRINCIPLES 的訪談——後者併進決策點①）。偏好類問題（例如要不要用第二家模型當 reviewer）不是非決策型：它在第一次碰到時併進決策點①一起問，答案記進 KICKOFF-DEFAULTS。這個類別不得新增成員，新增＝新機制，走 §11。
- **問使用者的規則**：決策點的**數量**是結構（engineering 2、product 3），每個決策點**內**問幾個問題不限——訪談問到清楚為止、可見行為逐個操作對、驗收報告列所有不確定。限制是「不問使用者看不懂的問題」（spec 品質、plan 拆法、審查裁定），不是少問。可驗判準：決策點內的每個問題必須可歸入三型之一（要什麼／可見行為／做到了嗎）或單向門的後果形；歸不進去的問題由 review 的 `user-judgment-leak` 維度判 NEEDS_REVISION。**岔路不新增停點**：所有岔路問題都併進既有決策點——engineering 併進決策點①（intent 確認時一起問；若岔路在 plan 階段才浮現，agent 選預設並標 `agent-decided`，寫進盲跑報告的「我替你決定了」段讓決策點③看到）；product 併進決策點②。決策點之外 agent 不停。其他決定 agent 做，標 `agent-decided` 記理由；使用者隨時可翻。岔路有兩類：
  - **判斷型**：≥3 個 trade-off 且不同選擇會改變交付物（brief-before-asking 既有定義）。
  - **單向門（必問，不靠判斷）**：任一成立——(a) 之後難以更換：框架、語言、資料庫、認證方式、託管平台、套件管理器；(b) 產生金錢或持續義務：付費服務、需帳號的第三方 API、要維護的基礎設施；(c) 限制使用者未來能做的事：資料格式、匯出能力、平台綁定；(d) **決定輸出品質上限的選型**：辨識／生成模型、演算法、資料來源等，且候選在使用者感受得到的軸（準確率、速度、每次費用、語言／格式覆蓋、隱私）上差異顯著——任一軸差 ≥ 20%，或金錢／隱私／覆蓋的有無；純內部差異（記憶體、行數、可維護性）不算；(e) **對使用者既有狀態的不可逆動作**：就地改寫或刪除使用者資料、改變既有檔案格式而無備份、把使用者資料送出本機——即使只有一種做法、沒有岔路也必問（盲跑在乾淨環境做，結構上碰不到既有資料，所以這類傷害只有問才擋得住）。四道閘依序：**先查**（intent 的 Acceptance／Constraints 或 PRINCIPLES.md 已釘住該軸→不問，選符合的）→ **先量**（能用使用者真實樣本快速比較的，量了再問，問結果不問假設）→ **門檻**（上述顯著性）→ **合併**（一個 change 的所有單向門合成一次問，附在既有決策點內；決策點過後才浮現的，agent 選預設、標 `agent-decided`、在盲跑報告揭露；**但 (b)(c)(e) 三類在決策點過後浮現時，agent 只能選零義務、可逆、不動既有資料的那個**，記 `agent-decided — 未經授權，取保守選項`，不得自選承諾型預設；「可逆」＝不觸發 (e) 的三個標記（就地改寫／刪除／送出本機）；若不存在零義務可逆選項，該項工作就此停住不做，在盲跑報告「我替你決定了」段列為未完成並說明原因，交決策點③）。問法固定為**後果形**：「選 A：以後只能在 ___ 跑、每月 ___、換掉要重寫 ___。選 B：___。我建議 A，因為 ___。」不出現機制名詞。答案寫進 spec 的 Design decision 並標 `user-decided`。
- 所有「問使用者」的舊時機（on-ramp、kickoff briefing、batch checkpoint、waiver）全部取消；on-ramp 1–3 列由 `needs-design` 重算，4–6 列變 standing default。

## 5. review 站＝checkpoint review（機器是唯一的審查者）

- **一份契約**：verdict schema、`reviewed_sha`、輪次規則一套。鏡頭多個（code 11 維、docs 5 維；spec-conformance、design-conformance、principles-conformance、user-judgment-leak 各一維；correctness 必跑 probe）。
- **獨立性是必要條件**：每個判斷型 checkpoint ≥ 2 個 fresh-context reviewer（同 host 的兩個 fresh session 即可）。**跨 vendor 是選配，由使用者選**：KICKOFF-DEFAULTS 記 `second-vendor: <cli> | none — <reason> (<date>)`（vendor＝不同模型供應商的可非互動 CLI，例如 Codex CLI、Gemini CLI）。未記錄且站偵測到第二家 CLI 時，在決策點①裡順帶建議（一段白話，用數字當理由：本設計自己的 spec 審查七個致命問題有五個只有一家找到；每次約幾分鐘與額度），**同一個 change 至多一次**，並把選擇記進 KICKOFF-DEFAULTS；記了就不再提。選了就用，沒選就不用，兩者都不 WARN、不擋。review.json 只記 `vendors: [...]`。reviewer 分歧記進 verdicts，不平均。
- **何時跑**：wave 結束算未審 delta，任一超過門檻（8 檔或 400 行，實驗預設，replay 後固定）才跑；branch 結束必跑；含 after-task 的 wave 結束一律跑。`needs-design: yes` 時 spec 進 plan 前必跑 spec 型別的「讀＋對抗」且 PASS。build 階段 checkpoint ≤ 5（plan 深度上限；NEEDS_REVISION 後的修正輪不計入）。
- **after-task**：plan 標記的 task commit 後立刻跑同一套；每 plan 預算 2，超過的每個要在 plan 的該 task 記一行理由（預算不是硬帽）。它是獨立的一次 checkpoint；該 wave 結束時的 checkpoint 是**另一次**（只審 after-task 之後的 delta ＋ 跨任務一致性；delta 為零時只跑一致性，很便宜）。
- **第 N 次審什麼**：`reviewed_sha` 後的 delta ＋ 跨任務一致性 ＋ 回歸 probe。
- **狀態機**：NEEDS_REVISION 不推進；下一輪逐條關閉 `open_findings`（resolved 或 dismissed，記誰）才推進。`dismissed` 只能由非 implementer 的 reviewer 下（checker 對 dispatch 記錄重算）；severity 為 important 以上的 dismissal 必須出現在盲跑報告的「我替你決定了」段。findings 只在 checkpoint 內改變。
- **邊界**：wave 內走歪要到 wave 結束才抓到；wave 大小是旋鈕。

## 6. 三種驗證動作＝品質的全部來源

| 動作 | 程式 | 設計（spec） | skill／gate |
|---|---|---|---|
| **讀** | ≥2 reviewer，code 11 維 | ≥2 reviewer，docs 5 維 | 同左 |
| **盲跑** | 乾淨環境 build／跑／照 intent 的 Acceptance 逐條驗／截圖 | 冷讀者拿 spec 走 Acceptance 的情境 | 冷讀 agent 照 SKILL.md 做真實任務 |
| **對抗** | mutation／fuzz（repo 宣告工具時）；**repo 未宣告工具時對抗 agent 自寫 ≥3 個可執行的 abuse／邊界案例並記進 `probes[]`** | red-team spec | gate 攻擊目錄 |

- **盲跑報告是驗收介面**：用使用者的語言，對 intent 的每條 Acceptance（product 時再加 spec 的 UI flows 每條）寫「我怎麼試、結果、證據（截圖／輸出）」，不確定的地方列成問題；固定一行「對你既有的資料做了什麼」（沒有就寫沒有）；「我替你決定了」段列 agent-decided 的岔路與 important 以上的 dismissal。決策點 ③ 讀的就是這份，不是 diff。
- 三者共用 verdict schema，結果進 review.json。寫的人不能自己驗：盲跑與對抗的 agent 不得是 implementer，checker 對 `reviewer ≠ implementer` 機械檢查（dispatch 記錄）。
- **型別對映**（KICKOFF-DEFAULTS 可覆寫）：`docs/loom/intent/**`＝intent、`docs/loom/<id>/spec.md`＝spec、`docs/loom/<id>/plan.md`＝plan、`PRINCIPLES.md`／`DESIGN.md`／`KICKOFF-DEFAULTS.md`＝standing、`docs/loom/memory/**`＝memory、`**/evidence/**`＝evidence（被引用時必讀）、`**/SKILL.md` 與 `agents/*.md`＝skill、`hooks/**` 與 `scripts/check_*`＝gate、`docs/loom/maps/**`＝map、其餘 `*.md`＝docs、其餘＝code。
- 目錄累積＝continuous evals：每個事故變永久案例，是 §11 的供給。

## 7. 決定性層（擋手滑，靠重算不靠宣稱）

- **建議性**：skill 散文、standing docs、reference。不用散文當閘。
- **決定性**：一支 **loom checker**，host hook 呼叫，規則全部是「重算」：
  - intent：schema；product 的 Problem 禁識別字；`needs-design` 行帶理由且進 commit message；`no` 但 diff 碰介面表面 glob → 擋。
  - 站點啟動：`contract.requires`——loom-design／loom-workflow 的站對 manifest 版本重算，不符→擋。
  - 收件：write-spec／write-plan 只收 `status: confirmed` 的 intent；write-plan 在 `needs-design: yes` 時只收有 spec PASS 的，且 `kind: product` 時另要求 spec 有 `confirmed-behavior:` 行。
  - push：HEAD 是 review-only commit、`reviewed_sha == HEAD^`、`open_findings` 全關、`probes[]` 裡有 package 測試記錄，且 artifact 型別要求對抗時有 ≥3 筆 `kind: adversarial` 記錄；**這兩類的每一筆 checker 都在乾淨工作樹（== reviewed_sha）自行執行其 `command`，以自己觀察到的 exit code 為準**（adversarial 的 command 預期 exit 0＝案例被擋住／通過），agent 填的 `result` 只作記錄——信任邊界：被 checkout 的分支其 review.json 的 `command` 會在 push 前被 checker 執行，這在 §0 的單人／自家 agent 威脅模型下可接受，多人 repo 要另加 branch protection、`verdicts[]` ≥ 2（vendor 數不是條件；`fresh-context` 是 dispatch 記錄欄位，不是可重算條件）、reviewer ≠ implementer、`dismissed` 者屬 dispatch 的審查角色。
  - 明說：這層擋的是漏步驟，不擋有目標的 agent；多人 repo 要作弊防護時加 branch protection。
- **稽核**：git（trailer、review.json）。

### 7a. host hooks

- Claude Code：plugin hooks，零動作。
- Codex：adopting repo 內 `.codex/hooks.json` ＋ checker 副本，站第一次碰到 repo 時寫入並以 `chore(loom): scaffold hooks <version>` commit。**hooks.json 的 command 字串固定為相對路徑且不含版本**（`.codex/hooks/loom-checker`），升級只換 checker 副本內容、版本戳寫在副本檔內——因為 Codex 的 trust 綁 hook 定義，定義不變就不重授信（實測 run E）；這是「每 repo 一次授信」成立的條件。已知限制：repo 內 checker 副本可被工作分支上的 agent 改寫而 trust 不撤（run E）；本層不防有目標的 agent（§0），需要時靠 CI 比對 main 的 digest。順序：寫入 → 若有寫入立刻 probe（派一個必被擋的假指令）→ 沒被擋＝安全帶不存在 → BLOCK，指名「請在 Codex 跑 /hooks」→ 使用者授信 → 下次 probe 通過才繼續。fail-closed：shim 或 checker 執行錯誤一律擋。
- 不做 git hook。
- CI 是**可選的第二層**：有 CI 的 repo 用同一支 checker 重跑相同規則；沒有的 repo 不假裝有。

## 8. Standing docs

- product-principles／design-system 是工具，產 `PRINCIPLES.md`／`DESIGN.md`；文件要有 `ratified-by: <name> <date>`（使用者確認後 agent 寫）。沒裝 loom-design 時，write-plan 用 contract package 的模板**代做訪談並代寫** PRINCIPLES.md，使用者只確認；使用者永遠不手寫。
- **勸導（每份 intent）**：repo 缺任一份 → checker 印固定三行 WARN；站原樣呈現。
- **拒收（只有一種）**：`kind: product` 且無 ratified PRINCIPLES.md（ratified ＝ 有 `ratified-by:` 行且 Non-negotiables 段 ≥ 3 條）→ write-spec／write-plan 拒收。conformance 維度對照不到條文時回 N/A＋理由進 review.json，不硬給分。DESIGN.md 永不拒。engineering 永不因此被拒。**不另開停點**：capture-intent（或 code-only 的 write-plan）在決策點①的同一段對話裡發現缺件時，直接接著做產品原則訪談，訪談結束一起確認；使用者不會被單獨問「要不要」。
- **靜音**：KICKOFF-DEFAULTS 記 `standing-docs: waived — <reason> (<date>)`，只靜音 WARN（DESIGN.md、與 engineering 的 PRINCIPLES 提醒）；**永不豁免 product 的 PRINCIPLES 拒收**。
- 消費：write-spec 載入；review 站 `principles-conformance`、`design-conformance`。

## 9. decision-map 與 evidence

- delivery ticket 不存在：地圖要交付一片就寫 intent.md 帶 `map:`；MAP.md 列 change-id；狀態由 §2b 派生。grilling／research／prototype 留在地圖。地圖對 intent 唯讀；open intent 阻擋對應 DA；withdrawn 記 retired，DA 要關需替代 intent 或 DA 證據。
- evidence 是附件：change 的放 `docs/loom/<change-id>/evidence/`；repo 級放 `docs/loom/evidence/`。舊七個目錄收成這兩處。

## 10. 明確刪除

- Review Batch／packet／receipt／apply-result；per-task 三臂審查作為常態層
- verified.json／review-pass.json／waiver.json → review.json；waiver 概念整個刪除
- approval-only commit、`Approved-by` 作為閘門、spec／plan 的人類簽核
- plan 的 Status／Decision Log／Review Batches／Stage
- brief（→ intent ＋ spec）、seed、backlog（→ intent）
- family-reception 契約、兩個 router、loom-init、on-ramp 問答、kickoff briefing
- 四份 verdict 契約 → 一份；docs-reviewer delta 封包協定
- completeness-critic／design-critic 作為獨立 skill；adversarial-audit-station 作為固定步
- decision-map delivery ticket 與綁定機制
- tdd-iron-law／systematic-debugging → reference；verification／ui-verification／parallel-agents／worktrees → action
- 舊 plan／spec／brief 一律原地封存不轉換（硬切換）；切換日事實：既有 Codex repo 因 hooks.json 定義改變需重授信一次；進行中的舊 branch 第一次 push 會被新 checker 擋，出口＝補 intent＋跑一次 checkpoint；活著的 decision-map 中綁舊 brief 的 DA 改指 `retired — 硬切換`

## 11. 准入規則

新增任何機制必須**同時**：(1) 有 regression eval（程式＝測試；閘門＝攻擊案例；散文規則＝冷讀 dogfood，排程 eval suite）；(2) 淨數不增，做不到寫明示 budget 例外進 CHANGELOG。決定性只是形式要求。不再新增散文閘：事故 → memory → eval → 才考慮 hook。

**機制母體**：`docs/loom/evidence/mechanisms.yaml`（repo 級常駐證據）列出每個機制，各帶 `eval:` 指向其回歸案例。每類都有可重算面：skill＝`skills/*/SKILL.md` 目錄；checker 規則＝checker 以 `--list-rules` 輸出的 rule id 表（checker 必須提供此輸出）；hook＝hooks.json 條目；action／schema 欄位＝contract package 的宣告檔 `loom-code/contract/manifest.yaml`（列 actions、artifact schema **逐欄位**（`artifact:<name>.<field>`）、station 名，機器可讀，版本戳在檔內）；**散文閘＝SKILL.md／reference 內以 `<!-- gate: <id> -->` 標記的段落**——沒有標記的散文不算閘，也就不得當閘用（審查維度 user-judgment-leak／omission 抓未標記的閘）。CI 重算五類清單與 mechanisms.yaml 比對：清單有而 yaml 無→紅（漏登）；**yaml 有而清單無→紅（殘留條目墊高基線）**；淨數增加且 CHANGELOG 該版條目無 `budget-exception: <mechanism-id> — <reason>` 行→紅；有機制無 `eval:`→紅。

**量測**（CI 或排程算）：機制淨數（上述）、skill 數、artifact 種類數、session-start 注入字數（超 main 基線且無例外→紅；session-start 基線＝本 change 合併前 main 的固定 SHA（落地時寫進 KICKOFF-DEFAULTS `session-start-baseline: <sha> <words>`），計數命令 `bash loom-code/hooks/session-start </dev/null | wc -w`，cwd 為空 git repo）；`needs-design: yes` intent 數、逾期未確認 intent 數、**每 change 的決策點數與岔路提問數**（只記錄，不是配額；連續上升＝違背 §0）。名詞數手數。

## 12. 驗收與審查紀錄

驗收對象是落地後各站的 SKILL.md（intent Acceptance #6）：冷讀者只拿該站文件，15 分鐘內零猜測說出指定任務的檔、決策點、checker、checkpoint；零猜測優先於時間。「猜測」＝冷讀者為回答四項而讀了入口站文件以外的任何檔案，或回答中出現無文件依據的斷言；由派測者判。本頁的冷讀結果只作記錄。

| 版本 | 檢查 | 結果 |
|---|---|---|
| v0–v3 | 冷讀者三輪 | 13 缺陷修 |
| v4 | Codex 獨立審 | 14 項處置 |
| v5 | 自審＋opus 邏輯審 | 18 缺陷修 |
| v6–v7 | Codex 情境審＋冷讀者 | 12＋5 修；拓樸全對，14 分鐘 |
| v7→v10 | 紅隊（11/13 閘可偽造）＋儀式成本量測（人類決策點 6→10 變重）＋目標敘述重定 | 威脅模型改為「品質不夠而人看不出」；人類決策點 4→2；刪 waiver／approval commit／身分錨；獨立審查升為必要（≥2 fresh reviewer；跨 vendor 當時寫必用，spec 審查後改為使用者選配）；盲跑報告＝驗收介面 |
| v10 | 冷讀者；決策點 ② 新增（product 的 spec 可見行為確認） | 兩條路徑、決策點、單 vendor 降級全對；每個問使用者的時刻皆判定基本知識可答；抓到「決策點①機制只在 capture-intent」與「after-task／wave-end 是一次還是兩次」——已修。25 分鐘（未達 15；文件密度是主因，落地後 SKILL.md 各站只載自己那段） |
