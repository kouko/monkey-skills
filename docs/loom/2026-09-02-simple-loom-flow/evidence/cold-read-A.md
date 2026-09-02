> REQ-9 正式驗收（W4-01，2026-09-03）：fresh sonnet 只讀 write-plan/SKILL.md＋references/，開檔 2，猜測 0（所列 5 項皆為任務未給的環境事實）。前兩輪見 cold-read-A-interim.md。

# Cold Read — REQ-9 Task A（write-plan / Codex CLI）

前提：只裝 loom-code plugin；Host = Codex CLI；尚無 intent 檔；無
`docs/loom/KICKOFF-DEFAULTS.md`。任務："A repo has six scripts that each
re-implement the same git helper; extract one shared helper."

我只讀了 `loom-code/skills/write-plan/SKILL.md` 與其 `references/`
子目錄下唯一一個連結檔 `references/one-way-door.md`（`contract/templates/*`
等路徑雖被 SKILL.md 引用，但不在 `references/` 下，依任務範圍未讀）。

---

## 1. 產生哪些檔（順序、確切路徑、change-id）

change-id 由 SKILL.md 自己給的 worked example 直接算出（第 39-40 行）：
> "for 'six scripts share a git helper' started on 2026-09-02, `2026-09-02-scripts-share-git-helper`"

所以 change-id = `2026-09-02-scripts-share-git-helper`。

依 Step 0b → 0 → 1 → 2 → 3 → 4 → 5 → 6 的順序：

1. `.codex/hooks/loom_checker.py`（及 scaffold 寫入的其他 hook 檔，檔名未列出）
   — Step 0b：`python3 <loom-code>/scripts/codex_scaffold.py --repo .`
   寫入／變更，之後以 `chore(loom): scaffold hooks <version>` commit。
2. `docs/loom/intent/2026-09-02-scripts-share-git-helper.md`
   — Step 1（loom-design 未裝，且使用者願意現在描述）由本站以「restate-and-
   confirm 式訪談」寫出；Step 3「yes」後寫入 `status: confirmed <date>`，
   以 `docs(loom): intent 2026-09-02-scripts-share-git-helper confirmed`
   commit（body 需逐字含 `needs-design:` 行）。
3.（不產生 spec）— Step 4 依 SKILL.md 自己的 worked example（第 321-324
   行）：「nothing the user reads or types into changes, and it is one
   object with no states, so neither (a) nor (b) holds →
   `needs-design: no — internal refactor, no surface the user reads or
   types into`」。所以 Task A 不進 write-spec，也不呼叫 review。
4. `docs/loom/2026-09-02-scripts-share-git-helper/plan.md`
   — Step 5，從 `contract/templates/plan.md`（範本路徑未讀，僅引用）產生；
   Step 6 以 `docs(loom): plan 2026-09-02-scripts-share-git-helper` commit。
5.（條件式）`docs/loom/KICKOFF-DEFAULTS.md` — 只有在 Step 3 第 3 點偵測到
   非本機 vendor 的 CLI 且該檔尚無 `second-vendor:` 行時才會建立/寫入
   (見 §7 猜測清單，本檔存不存在依環境而定，我無法斷言)。

## 2. 誰決定什麼

**決定點 ①（restate-and-confirm，Step 3）**——一則訊息內問完，原句：

> "你要的是 ___，做完後你可以 ___、___、___。對嗎？"
>
> "(You want ___, and when it is done you will be able to ___, ___ and
> ___. Is that right?)"

同一訊息裡還會帶（若有）：目前為止找到的 one-way doors（consequence
form，見 `references/one-way-door.md`）；第二審查工具建議（每個 change
最多問一次，見下）；以及 principles interview（只有 `kind: product` 且無
`PRINCIPLES.md` 才會插入——Task A 是 engineering，這條不觸發）。

第二審查工具建議原句（Step 3 第 3 點）：
> "reviewing with a second vendor costs a few minutes and some quota, and
> when this system's own spec was reviewed, five of the seven serious
> problems were found by only one of the two vendors"

是否真的問到這句，取決於環境是否偵測到「與 host 不同 vendor 的 CLI」（Codex
上看 `codex` 自己不算，要找 `claude` 或 `gemini`）——這是環境事實，我無法
從 SKILL.md 斷言 Codex 這台機器上是否裝了 claude/gemini（見 §7）。

**Codex 授權停點（Step 0b，非決定點）**——原句：

> "我已幫這個 repo 裝好 loom 的檢查；請在 Codex 裡輸入 `/hooks` 按一次授
> 權，我才會繼續。"

SKILL.md 明講：「This is an authorisation, not a decision about the
work — it is not a decision point」。

**Agent-decided 的點**（不問使用者，原句依據）：

- 整份 plan 怎麼拆：「how the work is split is your decision, and you
  write down why」（第 16-17 行）。
- Step 5「Nothing about the plan itself」清單第 5 點：「the task split,
  the wave sizes and the review timing are mine to decide; each
  judgement call gets a written reason」（第 72-74 行）。
- `needs-design: no` 這個判定本身是 agent 依 (a)(b) 兩條判準自己算的
  （Step 4），checker 只在偏離介面 glob 時才回頭擋（`intent.needs-design-
  recompute`）。
- Step 3 表格中列的三個「不該問使用者」的例子（parser 設計、模組放哪、
  測試風格）——原句：「if the user would have to read code to answer it,
  it is not a decision-point question — decide it yourself and mark it
  `agent-decided`」。Task A（git helper 放哪個模組、簽名長什麼樣）屬於此類。
- Step 3 gate marker 之後、post-decision 才冒出的 one-way door，一律
  `agent-decided`，且 class (b)(c)(e) 沒有免費預設，必須取保守選項並記
  `agent-decided — not authorised, took the conservative option`
  （`write-plan.post-decision-conservative-default`）。

## 3. 哪個 checker 在何時擋（Codex 形式）

順序（Codex：先 0b 再 0）：

1. Step 0b 探針（先於 0）：
   `python3 <loom-code>/scripts/codex_scaffold.py --probe`
   — 沒被擋＝未受信任的 hook 被靜默跳過，SKILL.md 說「stop」，印
   BLOCK 訊息（無獨立 rule id，屬 scaffold 腳本自身輸出）。
2. Step 0 契約版本：
   `python3 .codex/hooks/loom_checker.py contract --require 1.0`
   — rule `contract.requires`；非 0 則印訊息、要求升級 loom-code、stop。
3. Step 2 standing（決定點 ① 之前，每個 change 都跑）：
   `python3 .codex/hooks/loom_checker.py standing docs/loom/intent/2026-09-02-scripts-share-git-helper.md`
   — rules `standing.warn`、`standing.silence`（notice-only，不擋）、
   `standing.product-principles-reject`（會擋，但只在 `kind: product`
   且無已批准 `PRINCIPLES.md` 時才觸發——Task A 是 engineering，不觸發）。
4. Step 3「no plan without confirmed intent」（gate marker
   `write-plan.no-plan-without-confirmed-intent`，散文閘非指令）＋
   Step 3 驗證指令：
   `python3 .codex/hooks/loom_checker.py intent docs/loom/intent/2026-09-02-scripts-share-git-helper.md`
   — 涵蓋 `intent.schema` 家族（含 `intent.product-no-identifiers`、
   `intent.needs-design-reason`、`intent.needs-design-recompute`）；不過
   即使 Step 3 沒擋，checker 在 Step 4 仍會用 `intake.confirmed` 再擋一次
   （"the checker enforces the same rule at step 4"）。
5. Step 4 intake 檢查（both branches, every time）：
   `python3 .codex/hooks/loom_checker.py intake write-plan 2026-09-02-scripts-share-git-helper`
   — rules `intake.confirmed`、`intake.spec-pass`、
   `intake.confirmed-behavior`、`intake.after-task-budget`。SKILL.md 明講
   「When `needs-design: no` there is no spec, and the spec rules have
   nothing to check and pass; only `intake.confirmed` and the budget
   rule can block」——Task A 屬此情形。

## 4. 審查何時跑、review.json 誰建

write-plan **不會**在 Task A 這個 case 呼叫 review：站表原句
（write-plan 那列）：「none of its own; when `needs-design: yes` it
calls the review station once with scope `spec` (that checkpoint
belongs to review)」——Task A 是 `needs-design: no`，所以這一呼叫不觸發。

`review.json` 第一次出現，依 station 表：「created here, at the first
checkpoint (the spec review, or the first wave end); never written by
write-plan」。對 Task A 而言沒有 spec review，所以 `review.json` 會在
**build 站第一個 wave-end checkpoint**（或某任務標了
`review: after-task`）時才第一次建立，建立者是「Agent — two or more
fresh reviewers; their disagreement is recorded, not averaged」。這已經
是 build/review 站的行為，write-plan 本身不落地任何 review 產物。

## 5. Codex 與 Claude Code 的差異（含 repo 內第一個動作）

| 項目 | Claude Code | Codex CLI |
|---|---|---|
| checker 指令前綴 | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/loom_checker.py` | `python3 .codex/hooks/loom_checker.py`（由 scaffold 寫入 repo） |
| repo 內第一個動作 | 直接跑 Step 0 契約檢查 | 先跑 Step 0b：`python3 <loom-code>/scripts/codex_scaffold.py --repo .`（首次接觸此 repo才需要），寫入/變更檔案才 commit，再跑 `--probe` 驗證 hook 真的生效，最後才進 Step 0 |
| 額外停點 | 無 | 一次性授權停點（`/hooks`），SKILL.md 明講「it is not a decision point... it happens once per repo, not once per change」 |
| 順序備註 | Step 0 照寫的順序 | 原句：「On Codex do step 0b first and then this step; on Claude Code the order is as written」 |

## 6. 工作在哪個分支

Step 6：若目前在 trunk（`git branch --show-current` 印出 trunk 名），先
`git switch -c 2026-09-02-scripts-share-git-helper`；intent 可以留在
trunk 上不用搬，但 plan 與之後所有東西都要在這條分支上——原句：「It is
the plan and everything after it that belongs on the branch」。所以：
intent commit 可能落在 trunk，plan commit 與後續建置一律在分支
`2026-09-02-scripts-share-git-helper` 上。

## 7. 猜測清單（無法逐字引用原句的斷言）

1. **是否真的建立 `docs/loom/KICKOFF-DEFAULTS.md`**——取決於這台 Codex
   環境是否裝了 `claude` 或 `gemini` 且 `<cli> --version` exit 0，這是
   環境事實，SKILL.md 未給答案，我無法斷言。
2. **`codex_scaffold.py --probe` 第一次是否成功**（是否需要使用者按
   `/hooks`）——同樣是環境事實，SKILL.md 只給兩種分支的處理方式，不預測
   哪一支會發生。
3. **Step 0b commit message 裡的 `<version>`**——SKILL.md 說「using the
   version the script printed」，我沒有跑腳本，無法填實際版本號。
4. **使用者在 Step 1 是否選擇「現在描述變更」**——SKILL.md 給了兩個分支
   （停下拿模板 vs. 現在做訪談），我假設走「現在描述」分支以便任務往下
   走完；若使用者不描述，流程在 Step 1 就停在模板交付，後面全部不發生。
5. **Task A 是否真的沒有任何 one-way door**——SKILL.md 沒有針對 git
   helper 抽取這個具體情境給出結論；我依 `one-way-door.md` 五類定義判斷
   「不涉及 framework/金錢/使用者資料/品質軸差異」，這是我的推論套用
   規則，不是原文對這個具體任務下的斷言。

（共 5 條；目標零，未達成，皆屬環境事實或使用者選擇，非 SKILL.md 文字
本身模糊。）

## 8. 開檔數與耗時

- 開檔數：**2**（`SKILL.md`、`references/one-way-door.md`）——這是
  `references/` 目錄下唯一被連結的檔案，且是本任務允許讀取的全部範圍。
- 耗時：工具結果中只有最後一次 `date` 指令帶時間戳
  （`2026-09-02T13:09:36Z`，UTC），前面的 Read/Bash 呼叫結果未附時間戳，
  所以無法從工具輸出精確算出起始時間——誠實記錄：**無法量測**（本節
  依規則要求「用工具結果裡的時間戳」，但前段工具結果未提供，屬工具限制
  而非我省略）。若以回合數估算（4 次工具呼叫：Read SKILL.md、find、Read
  one-way-door.md、date），整個冷讀應在數分鐘內完成。
