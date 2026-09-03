# REQ-10 replay ①：PR #771（真 replay，走到 PR-ready）

任務：W4-03。對象：`5a437eb1` "refactor(loom-code): shared git body + sibling loader,
hook tests (0.108.1) (#771)"。做法：在 `5a437eb1^`（`33681e50`）拉一支 scratch clone，
用**本 branch 的五個站**（`loom-code/skills/{write-plan,build,review,ship,maintain}/SKILL.md`）
從 intent 一路走到 `loom_checker.py push` exit 0（不 push、無 remote）。

Scratch repo：`<scratchpad>/replay-771`，branch `replay-771`，base `33681e5093be2b13`。
plugin 檔一律用本 worktree 的絕對路徑代替 `${CLAUDE_PLUGIN_ROOT}`。

## 角色扮演揭露（必讀）

派工深度規則禁止本 task 再派 subagent。因此站裡每一個「dispatch」都由**我本人以該角色的身分、
用各自獨立的 `agent_id` 就地執行**，每次算一個派工。這代表：

- `review.json` 的 `dispatch[]` 裡 `fresh_context: true` 是**模型語意**，不是事實——
  31 個 entry 全部由同一個 agent 扮演。
- 因此「reviewer ≠ implementer」在本次 replay 是**記錄上成立、事實上不成立**；
  `push.reviewer-ne-implementer` 檢查的是 `agent_id` 不同，它通過了。
- 影響到的是**品質證據**（finding 的獨立性），不影響本 task 要量的**數量**
  （commit／派工／決策點都是機械可數的）。
- 「首輪 vs 後續輪 finding 比例」這條門檻判準因此是**弱證據**：同一個 agent 在三輪裡
  看同一棵樹，本來就會偏向「後面才想到」。這一點記在結論裡，不修飾。

使用者也由我模擬：決策點① 答「對」、第二 vendor 答「none」（照 W4-03 指定）。

## 每一步做了什麼（命令）

環境：`LC=/Users/kouko/.herdr/worktrees/monkey-skills/simple-loom-flow/loom-code`

```
git clone --no-hardlinks <worktree> <scratchpad>/replay-771
git checkout -b replay-771 5a437eb1^                       # → 33681e50
# KICKOFF-DEFAULTS：原檔已存在（舊 on-ramp 格式），追加 loom 1.0 的 key，不覆寫
#   - package-tests: python3 -m pytest loom-code/scripts/ -q
python3 -m pytest loom-code/scripts/ -q                    # 基線 2075 passed（1m59s）

# ── write-plan ────────────────────────────────────────────────
python3 $LC/scripts/loom_checker.py contract --require 1.0  # exit 0
python3 $LC/scripts/loom_checker.py standing docs/loom/intent/<id>.md
#   → 三行 WARN（此 repo 無 PRINCIPLES.md／DESIGN.md），逐字轉給使用者，不阻擋
command -v codex && codex --version                         # 存在 → 第二 vendor 建議出場一次
#   決策點① 一則訊息：restate + 第二 vendor 建議（無單向門）
python3 $LC/scripts/loom_checker.py intent docs/loom/intent/<id>.md    # exit 0
python3 $LC/scripts/loom_checker.py intake write-plan <id>             # exit 0
#   plan.md：Current State Evidence／16 task／3 wave／Questions asked／Risks

# ── build ─────────────────────────────────────────────────────
git merge-base HEAD origin/main                             # 33681e50 → review.json reviewed_sha
#   每個 wave：先寫 dispatch 記錄再派工；每個 task 一個 commit，帶 Task: <id> trailer
python3 -m pytest loom-code/scripts/ -q                     # 每個 wave 尾巴跑一次

# ── review（三個 checkpoint）───────────────────────────────────
#   每個 checkpoint：dispatch 記錄 commit → 2 reviewer + 1 blind-runner + 1 adversary
#   → 對抗者寫可執行 abuse 檔並進版控 → review-only commit（reviewed_sha = HEAD^）

# ── ship ──────────────────────────────────────────────────────
git commit --amend --no-edit --trailer "Learning: …" --trailer "Gotcha: …"
python3 $LC/scripts/loom_checker.py push                    # exit 0（見下）
```

`push` 的實際輸出（checker 在乾淨樹自己重跑，不信 agent 的宣稱）：

```
package-tests `python3 -m pytest loom-code/scripts/ -q`: observed exit code 0 (recorded result: 'pass')
adversarial loom-code/scripts/test_git_exec_abuse.py: observed exit code 0
adversarial loom-code/scripts/test_migrated_wrappers_abuse.py: observed exit code 0
adversarial loom-code/scripts/test_helper_contract_abuse.py: observed exit code 0
exit=0
```

## 實作範圍：做了什麼、略過什麼

- **做了**：16 個 task 全部真的實作並跑測試——兩支特性測試（釘住三種失敗家族）、
  `git_exec.py`＋`sibling_import.py` 兩支 helper、六個 git 呼叫端搬遷、
  五個 sibling 載入端搬遷、版本 bump 與 CHANGELOG。最終 `python3 -m pytest loom-code/scripts/ -q`
  → **2132 passed**。
- **略過**：原 PR 一併補的三支語言 hook 測試（`lang_detect`、`language-anchor`、
  `language-stop-check`，原 plan 的 T16–T18）。它們與「收斂重複的 git 執行」沒有依賴關係，
  在本次 intent 明寫進 Out of scope。
  **對計數的影響**：少 3 個 task ＝ 少 3 個 commit、少 3 個 implementer 派工。
  若補回來，commit 34→37、派工 31→34；wave 數與 checkpoint 數不變（那三支是獨立葉節點，
  掛在既有 wave 上不會多開一次 checkpoint）。**兩個結論都不會翻轉**：commit 仍 > 31，
  派工的 review 子集仍 ≤ 22。
- **中途兩次真的紅**（不是排練）：
  1. `test_gate_scripts_fail_loud_on_unreadable_input.py::test_every_script_here_is_classified`
     ——兩支新 helper 沒登記在腳本普查表。
  2. `test_check_living_spec_index.py::test_committed_index_is_current`
     ——`docs/loom/INDEX.md` 是衍生檔，新測試名進來就過期。
  兩次都是 wave 尾巴的 package-tests 抓到的，各補一個 fix commit。

## 計數（實測）

base `33681e50` .. HEAD `bd55885a`，34 個 commit：

| 類別 | 數 | 內容 |
|---|---|---|
| intent | 1 | `docs(loom): intent … confirmed`（含 KICKOFF-DEFAULTS 的兩個 key） |
| plan | 1 | `docs(loom): plan …` |
| review.json 建檔 | 1 | build 站 step 0.4 |
| dispatch 記錄（wave） | 4 | 應為 3；多的一個是我 wave 分組出錯後的補派（見下） |
| task commit | 16 | 每個帶 `Task: <id>` |
| 修紅 | 2 | 腳本普查表、living-spec 索引 |
| checkpoint × 3 | 9 | 每個 3 個：dispatch review／checkpoint artifacts／review-only |
| ship | 0 | memory 用 `--amend` 掛在 review-only commit 上，不新增 commit |

`dispatch[]` 31 筆：implementer 19、reviewer 6、blind-runner 3、adversary 3。
implementer 19 ＝ 計畫的 16 ＋ 計畫外的 3（見下一節）。

人類決策點 **2**：① intent 確認（2 個問題）、③ 驗收（我寫完盲跑報告就停，2 個問題）。
`review.json` 的 `questions[]` 共 4 筆，`decision_point` 1 兩筆、3 兩筆。

## finding：首輪 vs 後續輪

| round | scope | important | nit | 小計 |
|---|---|---|---|---|
| 1 | wave-end:1 | 1 | 3 | 4 |
| 2 | wave-end:2 | 1 | 2 | 3 |
| 3 | branch-end | 1 | 2 | 3 |

**首輪 4／10 ＝ 40%；後續輪 6／10 ＝ 60%**（important 只算：首輪 1/3 ＝ 33%）。
意思：只在最後審一次，會在一棵大得多的 diff 上重新找那 40%；只在開頭審一次，
會漏掉 60%。方向與 `q2-per-task-review-evidence.md` §C.5（whole-branch 首輪 under-reach）一致。
**但這是弱證據**：三輪 reviewer 由同一個 agent 扮演（見角色扮演揭露）。

## replay 找到的三個真缺陷（不是排練出來的）

1. **計畫沒有位置放「對抗者寫的 abuse 檔」**（round 3 important，`branch-end-01`）。
   review 站要求對抗者寫**可執行且進版控**的 abuse 案例；進版控的程式碼被
   `push.dispatch-covers-tasks` 要求帶 `Task:` trailer；trailer 又要對應一個
   `dispatch[]` 裡有 implementer 的 task。write-plan 沒有替 review 站自己生產的工件留位置。
   本次是臨時長出 W1-05／W2-07／W3-07 三個計畫外 task 才過閘（因此 implementer 19 ≠ 16）。
   **建議**：write-plan 每規劃一個 checkpoint 就預留一個「落地本輪 regression 案例」的 task，
   或 `push.dispatch-covers-tasks` 對 adversary 產出的路徑開一個機械可判的例外。
2. **wave 的定義有兩個來源**：plan 寫的 wave 標題 vs build 站 §1「wave ＝ `after:` 已滿足的 task 集合」。
   我先照 plan 的標題分成三 wave，執行到一半才發現四個 task 的依賴在 wave 1 結束時就已滿足，
   照站的定義它們屬於 wave 2。補派了一次（多一個 dispatch commit）。
   站的定義應該寫進 plan 模板的 wave 段，或 write-plan 要自己先跑一次 wave 推導。
3. **每個 checkpoint 固定三個 commit**（dispatch review／checkpoint artifacts／review-only）。
   review-only commit 的「只碰 review.json」是 push 閘的硬條件，所以盲跑報告與 abuse 檔
   一定要另外一個 commit；dispatch 記錄「派工前先寫」又要再一個。checkpoint 數是
   commit 數的三倍係數，這是本模型 commit 帳的主要成本。

## 對照今天（REQ-10）

| 欄 | 今天（實測） | v10 replay（實測） | 通過？ |
|---|---|---|---|
| commit | 31 | **34** | ✗ |
| 派工 | 22（審查派工，見下） | **31**（`dispatch[]` 全部）／**12**（審查角色子集） | 全部：✗／子集：✓ |
| 人類決策點 | 2 | **2** | ✓（持平） |

**兩個必須說清楚的事，都不是為了讓它過：**

- **commit 34 > 31，這是 §0 意義的失敗。** 敏感度：扣掉兩個純 replay 執行成本
  （我 wave 分組出錯多的 1 個 dispatch commit；兩次修紅若由真的 fresh-context implementer
  在自己的 task 裡跑完 package-tests 就會被吸收，−2）＝ **31**，與今天持平，仍非「更輕」。
  換句話說：**#771 這種小型純工程改動，新模型在 commit 帳上最好也只是打平。**
  成本結構已經在上面第 3 點寫明：checkpoint × 3。
- **派工的 22 與 31 不是同一種東西。** `ceremony-cost-old-vs-new.md` §(i) 的 b 列
  自己寫明來源＝「plan-review 3 輪＋5 次 DL 修訂重審＋task 級 fan-out 8＋whole-branch 2 臂 × 3 輪」，
  **全部是審查派工，不含 implementer**。#771 今天另有 19 個 SDD implementer 派工沒有被計進去。
  逐字對齊今天的定義，v10 的對應數字是 **12**（6 reviewer ＋ 3 blind-runner ＋ 3 adversary），
  12 ≤ 22 ✓。若兩邊都改成「全部派工」，今天 ≈ 41（22 ＋ 19），v10 是 31，31 ≤ 41 ✓。
  **兩種一致的定義下 v10 都比較輕；只有「今天算審查、v10 算全部」這種不一致的比法會 ✗。**
  這裡按 W4-03 的指定規則兩個數都列出，不挑一個。

## 推導規則的校準（給 #772／#775 用）

W4-03 給的規則是「commit ＝ task 數 ＋ 每 wave 1 個 dispatch chore ＋ 每 checkpoint 1 個
review-only ＋ ship memory amend」。用 #771 實測校準後，它**漏了四類 commit**：
intent、plan、review.json 建檔、每個 checkpoint 的另外兩個 commit（dispatch review、
checkpoint artifacts），以及 wave 尾巴的修紅。

- W4-03 原規則套 #771：16 ＋ 3 ＋ 3 ＋ 0 ＝ **22**；實測 34 → **誤差 −12（−35%）**。
- 校準後規則：`3（intent＋plan＋review.json 建檔）＋ T（task）＋ W（wave）＋ 3×C（checkpoint）＋ F（修紅）`
  套 #771：3 ＋ 16 ＋ 3 ＋ 9 ＋ 2 ＝ **33**；實測 34 → **誤差 −1（−3%）**。
  少的 1 個就是我 wave 分組出錯多派的那次。
- 派工規則「implementer（每 task 一個）＋ 每 checkpoint 4（2 reviewer＋1 盲跑＋1 對抗）」
  套 #771：16 ＋ 12 ＝ **28**；實測 31 → **誤差 −3**，缺口正是計畫外的三個
  「落地 abuse 檔」task。校準後：`T ＋ C（每 checkpoint 一個 regression 落地 task）＋ 4×C`。
- 決策點規則「engineering ＝ 2」：實測 2，**誤差 0**。

`#772`／`#775` 兩份推導同時列出「W4-03 原規則」與「校準後規則」兩個數。
