# loom 目標概念模型 v7

日期：2026-09-02　狀態：目標文件（裁定已併入，無未決項）　對照組：Anthropic「The AI-Native SDLC Playbook」
現況診斷與六題裁定的推理過程見 `evidence/current-state-diagnosis.md`、`evidence/concept-model-v5-pre-fold.md`；本文只寫目標。

## 0. 一段話

三個 plugin 沿「要什麼／為什麼」對「怎麼做」切線。每個 change 從一份人寫的 intent.md 開始，視需要經 spec.md，再到 plan.md、diff／PR、review.json；進度與決策走 git，不另立帳本。審查是同一份契約在里程碑重複跑的 checkpoint review。治理三層：建議性（散文）、決定性（兩支 checker ＋ host hooks）、稽核（git ＋ CI）。人最多簽四次。新機制要同時有回歸 eval 且淨數不增。

## 1. Plugin 與依賴

| plugin | 回答 | 內容 | 安裝 |
|---|---|---|---|
| **loom-design** | 要什麼、為什麼、應該長怎樣 | 站：capture-intent、write-spec；工具：product-principles、design-system | 可選 |
| **loom-code** | 怎麼做 | 站：write-plan、build、review、ship、maintain；checker 兩支；host hooks；reference 一份；intent／spec／plan／review 的檔案契約 | 可獨立 |
| **loom-workflow** | 使用者點名的工具 | decision-map、handoff、recap、cot-explain、distill、git-memory、independent-advisor、critique | 可選 |

- 依賴單向：loom-design 與 loom-workflow 依賴 loom-code 提供的 **versioned contract package**（schema、checker、relay 散文）。design 寫檔、code 讀檔；decision-map 寫 intent.md；沒有反向呼叫。
- 契約由消費者定義：schema 與 checker 住在 loom-code；loom-design 的站是「產生這個格式的比較好的方法」，不是必要條件。
- 仍需同步的功能副本，明列：checker（design 側呼叫 code 側同一支）、family-relay／plain-relay（跨 plugin 的「怎麼跟使用者說話」散文）。除此之外沒有。

## 2. Artifact

### 2a. core per-change 五種 ＋ git

| artifact | 誰寫 | 誰批 | 位置 |
|---|---|---|---|
| **intent.md** | 人（capture-intent 訪談後寫、手寫、decision-map 開的交付片、maintain 站的 agent——**同一 alert identity 已有 open intent 時只更新其 evidence，不新建**） | 使用者 | `docs/loom/intent/<change-id>.md` |
| **spec.md** | Claude，套 standing docs；含 UI flows 段 | 使用者 | `docs/loom/<change-id>/spec.md`（只在 `needs-design: yes`） |
| **plan.md** | Claude | 使用者 | `docs/loom/<change-id>/plan.md` |
| **diff / PR** | Claude | 使用者 | git |
| **review.json** | review 站 | 無獨立簽核；findings 在下一個既有簽核點（plan 或 PR）處置，最終由 PR approval 承接 | `docs/loom/<change-id>/review.json`（入版控）；`.git/loom/ready.json` 是給 hook 用的本機鏡像；PR thread 為副本 |

memory（git trailer ＋ `docs/loom/memory/`）與 standing docs（`PRINCIPLES.md`、`DESIGN.md`、`KICKOFF-DEFAULTS.md`，等同 CLAUDE.md 地位）不是 per-change artifact。evidence 是附件，見 §9。

### 2b. intent.md schema（loom-code 擁有）

```
# <title>
originator: <who>            # 人名、"maintenance-loop"、或 map:<id>
kind: product | engineering  # 見下
needs-design: yes | no — <reason>
map: <map-id>                # 可選；此 intent 是該地圖的一片交付
evidence: [<paths>]          # 可選；write-spec／review 必須真的讀
status: open | withdrawn — <reason>   # 可選；缺＝open

## Problem            ← 問題與誰受影響。product：禁檔案路徑、函式／類別識別字、腳本檔名（regex 可抓，checker 擋）；engineering：不禁。口語機制名皆不禁
## Proposed outcome   ← 方向與解法形狀，可含檔名
## Constraints
## Value case         ← 可選；product 的 GO/NO-GO 與理由
## Out of scope
## Open questions
```

- `needs-design: yes` 當任一成立：(a) 動到使用者看得到的介面——任何使用者讀或輸入的表面：GUI、TUI、CLI 參數與輸出、對外 API——且無 DESIGN.md／ui-flows 覆蓋（機械可查）；(b) 多狀態或多物件行為且無 spec（判斷）。否則 `no`。所有 kind 同一判定；bug fix／refactor 通常 `no`，碰到 (a)(b) 仍 `yes`。
- `needs-design` 行必須帶理由，且 intent 的 commit message 含同一行；缺任一擋 commit。「使用者真的讀了」無法機械化，不假裝。
- **未簽核的 intent 可以 commit**——那就是 backlog 的一條。批准是**之後的 approval-only commit**：只動該 artifact 檔（可為空改動或加一行 `approved: <sha>`），commit message 帶 `Approved-by: <name> <date>` 與 `Approves: <artifact path>@<sha>`；checker 以「引用的 sha 與檔案當前內容一致」認定批准，不重寫原 commit。批准後再改 artifact 內容＝批准失效，需重批。這是下游站收件的條件，不是 commit 的條件。
- intent 狀態派生：無 Approved-by＝open；有＝claimed；PR merged＝closed；檔案刪除或 `status: withdrawn`＝closed。
- 工程意圖通常三到五行，手寫比訪談快；這是正常路徑。

### 2c. spec.md schema（loom-code 擁有；手寫時照此模板即可過 checker）

```
# <title>
intent: <change-id>@<sha>     # 對應的已批准 intent
## Requirements        ← REQ-<n> — <name>，每條可驗
## Design decision     ← 一段：做什麼、不做什麼、為什麼（吸收 brief 的 Decision）
## Alternatives considered
## Current state evidence   ← Forward／Reverse／Error／Data／Boundary 五條，各附路徑與錨點（動既有碼時必填）
## UI flows            ← 有介面時必填：screens／navigation／states；無介面寫 N/A
## Acceptance criteria
```

### 2d. plan.md

Task DAG（每 task 穩定 ID）／檔案／測試／風險。`needs-design: no` 時（無 spec）plan 前段必含 Current State Evidence（同 spec 的五條格式）；`yes` 時引用 spec 的即可。進度由 commit 的 `Task: <id>` trailer 派生，script 生成 view；決策走 git-memory trailer。plan 只保留兩個尚無 commit 的暫態：`claimed(@branch)`、`blocked(<reason>)`，寫在該 task 行，供平行派工。task 可標 `review: after-task`（見 §5）。沒有 Status 帳、Decision Log、Review Batches、Stage。

### 2e. review.json ＝ ready.json

```
reviewed_sha         # 初值 branch base；只有 PASS／PASS_WITH_NOTES 推進
verdict              # findings 依嚴重度排序；dimension_scores
open_findings[]      # {id, anchor, origin_sha, resolved: <evidence> | dismissed: <reason>}
waiver?              # {approver, reason, gates ⊂ {open-findings}, expected_head, expiry: <date>, consumed: bool}
                     # 有效 ⇔ gate ∈ gates ∧ HEAD^ == expected_head ∧ today ≤ expiry ∧ consumed == false
                     # git-guard 放行前先把鏡像與 review.json 的 consumed 置 true（一次 push attempt 語意；失敗要重核發）
                     # CI 用同一條有效性規則驗 review.json 裡的 waiver；verdict-coverage 不可 waive
```

寫 review.json 的 commit（review-only commit）只准動這一個檔。**拓樸固定**：push 時 HEAD 必須是 review-only commit，`reviewed_sha == HEAD^`；git-guard 與 CI 用同一條規則。amend 或新增 code commit 後，舊 review-only commit 作廢（reset 掉或再疊一個新的），重跑 checkpoint 產生新的 review-only HEAD。checkpoint 覆寫 verdict 與 reviewed_sha，不動 waiver。

### 2f. 命名

`<slug>`＝標題 kebab-case；`<change-id>`＝`<date>-<slug>`；intent 檔名與 `docs/loom/<change-id>/` 同名。intent／spec／plan／review.json 都是被 commit 的檔案。

## 3. Skill 四分類

| 類 | 定義 | 數 | 成員 |
|---|---|---|---|
| **站** | 產出 §2a 某一 artifact | 7 | capture-intent、write-spec（design）；write-plan、build、review、ship、maintain（code） |
| **工具** | 使用者點名，或被站以機械條件叫起 | 10 | loom-workflow 八個；product-principles、design-system |
| **reference** | 建議性規則，無 artifact，不是 skill | 1 | engineering-baseline＝tdd-iron-law ＋ systematic-debugging 的純規則 |
| **action** | 站內可執行步驟，有輸入輸出與失敗語意，不是 skill，不計 | — | package 測試（原 verification-before-completion）、UI 盲跑（原 ui-verification）、平行派工、worktree（原 dispatching-parallel-agents、using-git-worktrees） |

36 → 18。名詞 ≤ 40，計數規則：數 artifact 名、站／工具／action 名、schema 的 frontmatter 欄位名、狀態物件名；**不數** Markdown 段落標題、欄位子值、型別列舉值、既有 git 詞、alias（review.json＝ready.json 算一）。依此規則 Codex 第二輪數得 36，本頁以 36 為基線。

## 4. 入口、路由、簽核

| | 有裝 loom-design | 只裝 loom-code |
|---|---|---|
| 入口 | capture-intent 站 | write-plan 站：讀 intent.md，沒有就停下來要（給模板） |
| `needs-design: yes` | write-spec 站 | 大聲 N/A：裝 loom-design 或手寫 spec.md |
| `needs-design: no` | 交 loom-code | 直接 write-plan |
| intake checker | 兩邊都跑（同一支） | loom-code 跑 |

- 沒有獨立 router，沒有先於 intent 的 reception。舊 on-ramp 表 1–3 列收進 `needs-design`，4–6 列變 standing default 或工具建議。
- **簽核點**：intent → (spec) → plan → PR，每 change 最多四、最少三。批准＝§2b 定義的 approval-only commit（`Approved-by:` ＋ `Approves: <path>@<sha>`）或 PR approval 事件；checker 認引用的 sha，不認「有 commit」。首次 ratify PRINCIPLES.md／DESIGN.md 是 repo 級 bootstrap，另計。
- 其他所有「問使用者」（舊 on-ramp 選擇、kickoff briefing、batch checkpoint、waiver）併進這幾點，或變 standing default。

## 5. review 站＝checkpoint review

- **一份契約**：verdict schema、`reviewed_sha`、輪次規則只有一套。鏡頭多個（code 11 維、docs 5 維，按型別選；spec-conformance 併為一維；design-conformance 對 DESIGN.md；correctness 必跑 probe），彙整進同一份 verdict。
- **何時跑**：每個 wave 結束算 `git diff <reviewed_sha>..HEAD --stat`；未審 delta 任一超過門檻（8 檔或 400 行，實驗預設，落地後 replay 量測再固定，數字在 KICKOFF-DEFAULTS）才跑，否則累積；branch 結束必跑；含 `review: after-task` 的 wave 結束一律跑（剩餘 delta 為零時只跑跨任務一致性，很便宜）。wave＝plan DAG 同一層可平行 task 集合。plan 深度 ≤ 5 ⇒ build 階段 checkpoint ≤ 5；spec 審查與 after-task 不計入此上限。
- **spec 先審再批**：`needs-design: yes` 時 spec.md 首次簽核前必跑 spec 型別的「讀＋對抗」；write-plan 由 intake checker 機械拒收沒有 PASS 或 approval 早於 PASS 的 spec（§7）；之後只審 spec delta。
- **after-task**：plan 標 `review: after-task` 的 task，commit 後立刻跑同一套 checkpoint。每 plan ≤ 2，超過寫理由。落地後用歷史分支 replay 量 checkpoint（含 after-task）的漏失率、review 次數、重工，數字進 evidence 再固定門檻。
- **第 N 次審什麼**：`reviewed_sha` 之後的 delta ＋ 跨任務一致性 ＋ 回歸 probe。修 findings 的 commit 就是下一個 delta。
- **狀態機**：NEEDS_REVISION 不推進 `reviewed_sha`；下一輪逐條關閉 `open_findings`（resolved 或 dismissed）才推進。**findings 只在 checkpoint 內改變**：使用者要 dismiss 是給下一個 checkpoint 的輸入（寫在 plan 該 finding 旁或對話中），由 reviewer 在該輪的 review-only commit 裡記 `dismissed: <reason>` 與提出者；沒有獨立的 dismiss commit。沒有 packet／receipt／apply-result／ledger。
- **邊界**：wave 內某 task 走歪要到 wave 結束才抓到；wave 大小是旋鈕。

## 6. 三種驗證動作，按型別觸發

| 動作 | 程式 | 設計（spec） | skill／gate |
|---|---|---|---|
| **讀** | code 11 維 | docs 5 維 | docs 5 維 |
| **盲跑**（沒寫的人只拿 artifact 執行，不修只報） | package 測試必跑；app 級（build／跑／點 UI）需 repo 宣告入口 | 冷讀者走一個情境 | 冷讀 agent 照 SKILL.md 做真實任務 |
| **對抗**（弄壞它，成功的進目錄） | 只在 repo 宣告 mutation／fuzz 工具時 | red-team spec | gate 攻擊目錄（ATTACK-CATALOGUE） |

- 三者共用 verdict schema，結果進 review.json。寫的人不能自己驗。
- **型別對映**（KICKOFF-DEFAULTS 可覆寫；預設依優先序）：`docs/loom/intent/**`＝intent、`docs/loom/<id>/spec.md`＝spec、`docs/loom/<id>/plan.md`＝plan、`PRINCIPLES.md`／`DESIGN.md`／`KICKOFF-DEFAULTS.md`＝standing、`docs/loom/memory/**`＝memory、`**/evidence/**`＝evidence（不跑維度，但被引用時 reviewer 必讀）、`**/SKILL.md` 與 `agents/*.md`＝skill、`hooks/**` 與 `scripts/check_*`＝gate、`docs/loom/maps/**`＝map、其餘 `*.md`＝docs、其餘＝code。docs 維度給 intent／spec／plan／standing／skill／map／docs；code 維度給 code／gate。
- checkpoint 時 checker 看 delta 碰到哪些型別決定跑哪些動作。目錄累積＝continuous evals，是 §11 第一條的供給。

## 7. 治理三層與決定性層

- **建議性**：skill 散文、standing docs、reference。不再用散文當閘。
- **決定性**：兩支 checker。
  - **intake checker**（intent 與 spec 共用）：product 的 Problem 段禁程式識別字；`needs-design` 行帶理由且進 commit message（缺則擋 commit）；`kind: product` 且無 ratified PRINCIPLES.md → 拒收；缺有效 approval-only commit → 拒收；**`needs-design: yes` 時 write-plan 另要求：review.json 有覆蓋 spec 當前 sha 的 PASS、`open_findings` 全關、且 approval 在該 PASS 之後**——否則拒收（spec「先審再批」的決定性形式）。
  - **git-guard**：只認 `ready.json`，規則與 CI 相同：HEAD 是 review-only commit 且 `reviewed_sha == HEAD^`、`open_findings` 全關（或被有效 waiver 豁免）；三合一取代舊三個 marker。
- **稽核**：git（trailer、review.json）＋ CI。

### 7a. host hooks 與 Codex

- Claude Code：plugin hooks，裝好即生效，零動作。
- Codex：adopting repo 內 `.codex/hooks.json` ＋ checker 副本（**被 commit 的 scaffold 檔**，由站以一個不需簽核的 `chore(loom): scaffold hooks <version>` commit 落地，CI digest 才有對象）。站的**固定順序**：① 比對版本戳，缺或舊就寫入／覆寫並 commit → ② 若 ① 有寫入，立刻 probe、BLOCK、停止，訊息指名「請在 Codex 跑 /hooks」 → ③ 使用者 `/hooks` → ④ 下次執行先 probe，版本已新且 probe 通過才繼續。舊版更新只需一次重新授信，不成迴圈。
- Codex 授信：每 repo 每 hook 版本使用者跑一次 `/hooks`，loom 不能代做。probe＝派一個必被擋的假指令；沒被擋＝閘門無效 → **BLOCK**。不讀 `hooks.state`。**fail-closed**：shim 或 checker 本身執行錯誤（payload 不合、python 不在）一律 exit 2 擋，不放行。
- 不做 git hook（`--no-verify` 六種繞法；`core.hooksPath` 在 worktree 失效）。

### 7b. CI ＋ branch protection（不可繞）

- checker 副本 digest 對 adopting repo main（完整性；trust 不綁 script 內容是實測事實）；版本戳對 plugin 版本只 WARN。
- intent／spec／plan schema；intent commit message 含 `needs-design` 行；`Approved-by` trailer 存在。
- **review 閘門的 CI 兜底**：PR head 是 review-only commit、`review.json.reviewed_sha == HEAD^`、`open_findings` 全關（或被 CI 驗過的有效 waiver 豁免）、review commit 只動 review.json。
- branch protection：非作者批准。
- 未驗證：使用者自寫 `~/.codex/requirements.toml` 能否讓 hook 免授信；動全機設定，經同意後測。

## 8. Standing docs

- product-principles／design-system 是工具，產 `PRINCIPLES.md`／`DESIGN.md`；文件必須有 `ratified-by: <name> <date>` 行才算存在（工具產草稿留空，使用者填）。沒裝 loom-design 可照 loom-code 附的模板手寫。
- **勸導（每份 intent）**：repo 缺任一份 → checker 印固定三行 WARN（exit 0）：缺哪份、為什麼、該跑哪個工具；站原樣呈現。
- **拒收（只有一種）**：`kind: product` 且無 ratified PRINCIPLES.md → write-spec／write-plan 拒收。DESIGN.md 永不拒：條件 (a) 因缺它而 `yes`，write-spec 的 UI 段就是這次的設計覆蓋。engineering 永不因此被拒。
- **靜音**：KICKOFF-DEFAULTS 記 `standing-docs: waived — <reason> (<date>)`，WARN 不再印。
- 消費：write-spec 載入；review 站 `principles-conformance`、`design-conformance`。

## 9. decision-map 與 evidence

- 地圖四型 ticket 中，**delivery ticket 不存在**：地圖要交付一片就寫 `docs/loom/intent/<change-id>.md` 帶 `map:`；MAP.md 列 change-id；狀態由 §2b 派生，phase 由 `docs/loom/<change-id>/` 下 spec／plan／review.json 存在與 PR 狀態算出；舊狀態機的 `claim blocked`／`close da-gap` 拒絕改為 checker 對 intent 欄位＋git 狀態的查詢。grilling／research／prototype 留在地圖（是問題，不是改動）。地圖對 intent 唯讀，但有**收斂規則**：open 的 intent 阻擋它所服務的 DA；intent 變 withdrawn 時地圖把它記為 retired，DA 要關必須連結替代 intent 或另附 DA 證據。刪 `start_delivery` 綁定、`DeliveryClosureInputs`、delivery phase 帳本。
- **evidence 是附件**（無獨立 schema、無簽核；消費者是 write-spec 與 review——intent／spec 用 `evidence:` 引用的路徑，checker 驗存在，review contract 要求記錄已讀）：change 的證據放 `docs/loom/<change-id>/evidence/`；repo 級常駐證據（ATTACK-CATALOGUE、eval 目錄、harness 審計）放 `docs/loom/evidence/`。舊 discovery／research／audits／dogfood／harness-audit／task-batch-review／firing-corpus 七目錄收成這兩處。

## 10. 明確刪除

- Review Batch／packet／receipt／apply-result（≈4.2k 腳本 LOC ＋ 6.9k 測試 LOC ＋ 23 名詞）
- verified.json／review-pass.json／waiver.json → ready.json
- plan 的 Status／Decision Log／Review Batches／Stage 段
- brief（拆成 intent ＋ spec；Current State Evidence 進 plan）、seed、backlog（併入 intent）
- family-reception 契約與兩個 router；loom-init
- spec-reviewer／code-quality-reviewer／code-reviewer／docs-reviewer 四份 verdict 契約 → 一份；docs-reviewer 的 delta 封包協定
- completeness-critic／design-critic 作為獨立 skill → review 站對 spec 的「讀＋對抗」；adversarial-audit-station 作為 finishing 固定步 → 型別觸發
- decision-map 的 delivery ticket 與其綁定機制
- tdd-iron-law／systematic-debugging → reference；verification／ui-verification／parallel-agents／worktrees → action

## 11. 准入規則

新增任何機制（skill、reference、checker、gate、hook、schema 欄位、名詞）必須**同時**滿足：

1. **有 regression eval**：程式＝測試（CI）；閘門＝攻擊案例（CI）；散文規則＝§6 冷讀 dogfood 案例（排程 eval suite，非每 PR）。
2. **淨數不增**：同 PR 刪或併至少一個既有機制；做不到寫**明示 budget 例外**（一行理由進 CHANGELOG，可統計）。

決定性只是新閘門的形式要求，不換免刪。不再新增散文閘：事故 → memory（一次）→ eval（兩次）→ 才考慮 hook。

**量測**：CI 算五項——skill 數、artifact 種類數、session-start 注入字數、`needs-design: yes` intent 數（連續三版為零 → 開一份 intent 議「loom-design 留不留」）、**逾期未 triage 的 open intent 數**（open 超過 KICKOFF-DEFAULTS 的天數）；前三項超 main 基線且無 budget 例外行就紅，後兩項只記錄不紅（它們量的是使用，不是機制）。名詞數依 §3 規則手數，只進 CHANGELOG。

## 12. 驗收與審查紀錄

冷讀者（fresh sonnet）只拿本頁，10 分鐘內對指定任務說出：產生哪些檔、誰批、哪個 checker 擋什麼、checkpoint 何時跑。答不出＝本頁缺陷。

| 版本 | 檢查 | 結果 |
|---|---|---|
| v0–v3 | 冷讀者三輪 | 路徑皆正確；12–15 分鐘；13 缺陷已修 |
| v4 | Codex gpt-5.6-sol high 獨立審查（`evidence/independent-advisor-codex-run.md`） | 10 分歧 ＋ 4 發現，全部處置 |
| v5 | 自審 8 ＋ opus 情境式邏輯審 10 | 18 缺陷已修，零重疊 |
| v6 | 併裁定成純目標文件；Codex 第二輪情境審（`evidence/independent-advisor-codex-run-2.md`） | `not-ready`：12 缺陷（批准 commit 拓樸、git-guard 對 CI 拓樸、waiver 語意與 CI 死路、map 收斂、maintain 累積 vs 指標、安裝／probe 次序、spec schema 缺、spec 審查僅散文、review.json 第五簽核、evidence 消費者矛盾、名詞 42、fold 漏三項）——全部修入 v7 |
| v7 | 冷讀者 | 兩條路徑含完整 git 拓樸（approval-only／review-only／code commit 順序）皆正確；Codex fresh clone 第一個 commit 前的握手正確；4 個 checkpoint 與 NEEDS_REVISION 痕跡正確；~14 分鐘。抓到 dismiss 落點、after-task 與 wave-end 連跑、spec 審查是否計入上限、hook 檔是否 commit、CLI 算不算介面——五項已補 |
