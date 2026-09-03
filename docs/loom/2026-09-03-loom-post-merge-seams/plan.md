# loom 1.0 merge 後的接縫 — plan
intent: 2026-09-03-loom-post-merge-seams@90aedebf（Constraint／Acceptance 之後由 kouko 決定 A 修訂至 d3d96241）
spec: docs/loom/2026-09-03-loom-post-merge-seams/spec.md@84a8cb7e（v9，blob ddf9e10，review.json round 8 PASS）
kind: engineering　needs-design: yes（spec 已 PASS；Current State Evidence 在 spec）
決策：agent-decided；理由附在各 task。使用者不審 plan。

## 0. 形狀與帳本
- 兩個 wave、三次 build 內 checkpoint（W0 兩個 after-task ＋ W0 wave-end；W1 wave-end 兼 branch-end，不計）；上限 5。
- 規則數維持 27；沒有新 id、沒有 waiver。兩條加嚴（`push.reviewed-sha`、`push.review-only-head`）與 `intake.confirmed` 的 closed／reopen 分支、`push.dispatch-covers-tasks` 的豁免來源，是這個 change 全部的 checker 改動。
- 版本：loom-code 1.0.0 → **1.0.1**、loom-design 1.0.0 → **1.0.1**、loom-workflow 4.0.0 → **4.0.1**。每個 bump 三表面：`.claude-plugin/plugin.json`、CHANGELOG、root README 該列（歷史上第 13 次漏掉的表面）；Codex 鏡射 manifest 用 `python scripts/sync_codex_manifests.py --all`（CI `codex-manifest-drift` 會查）。
- 本分支的 push 閘跑的是**裝置端 1.0.0 的 checker**（plugin cache），不是分支上的新 checker；新加嚴要到 merge、`claude plugin update` 之後才對後續 change 生效。所以本分支自己的關閉 commit 走的是 1.0.0 的規則（沒有形狀重算、沒有 sha 綁定），但 build 照新規則寫記錄（每個裁定帶 `sha`），讓 1.0.1 的 checker 回頭跑也過。
- 共用 worktree：implementer 的 commit 一律 `git commit -- <paths>` 路徑限定，禁 `git add -A`、禁 stash。每個 commit 帶 `Task: <id>` trailer（docs 型也帶，省得算型別）。
- 套件測試命令（KICKOFF-DEFAULTS）：`python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q`；本機約 2–2.5 分。

## 1. Task DAG
同 wave 內無 `after:` 者可平行；但 W0 五個 task 全動 `loom_checker.py`，**一律循序**（共用符號、共用測試檔）。每個 task 先寫失敗的測試。

### W0 — checker（loom-code/scripts）
checkpoint：W0-04、W0-05 各一次 after-task；wave-end 一次。

**W0-01 status 文法：`STATUS` 取代 `CONFIRMED`，closed 進 intake 與 schema**
- 檔：`loom-code/scripts/loom_checker.py`（:791 `CONFIRMED` → `STATUS`，四個 alternative 各允許尾端 `\s+#.*`；`intent.schema`、`intake.confirmed` 共用；closed 日期走 `is_real_date()`；`--list-rules` 的 `intake.confirmed` 描述列出 `closed <YYYY-MM-DD> — PR #<N>`；`intake.confirmed` 對 closed 的訊息 `intake.confirmed: … this change is closed (PR #<N>); a new change starts from a new intent`；順手修 R24-O2：:455 docstring「below」→「above」）、`loom-code/contract/manifest.yaml:85`、`loom-code/contract/templates/intent.md:7`、`loom-code/scripts/test_loom_checker_intake.py`（`test_the_repos_own_change_matches_its_own_review_json` 加分支：status closed → 期望 `{intake.confirmed}`）。
- 測：先寫 `intake write-plan` 對 `status: closed 2026-09-03 — PR #780` 的 intent 被擋且訊息含 `closed (PR #780)`；`intent` 子命令對同一檔 exit 0（schema 接受）；假日期 `closed 2026-02-30 — PR #1` 被擋；`--list-rules` 輸出含 `closed`。
- 風：`CONFIRMED` 名字被別處 import 或測試引用——先 grep 全 repo 再改名（agent-decided：改名而非並存，避免第二個漂移面）。

**W0-02 closed 是終點：reopen 檢查 (i) 分支歷史、(ii) 主幹副本**　after: W0-01
- 檔：`loom_checker.py`（`REOPEN_TRUNK_CANDIDATES = ("origin/main", "main", "origin/master", "master")` 為新常數、與 `TRUNK_CANDIDATES` 分開；(i) `git log --format=%H -G'^status:[[:space:]]*closed ' -- <intent path>` 非空且現狀非 closed → 擋，訊息 `intake.confirmed: <change-id> was closed (PR #<N>) and closed intents are not reopened; start a new intent`；(ii) `git show <trunk>:<path>` 的 status 解析為 closed → 同訊息；四個候選都不解析 → 印「trunk copy check absent」一行、不擋）、`test_loom_checker_intake.py`。
- 測：臨時 repo 三案——分支上先 closed 再手改回 confirmed → 擋；從關閉前的 trunk 分出、本機 `main` 帶 closed → 擋；無任何 trunk ref → 不擋且輸出含 absent。
- 風：`-G` 在 BSD／GNU git 皆是 POSIX ERE，`[[:space:]]` 可攜；pattern 字串從 `STATUS` 的 closed alternative 生成，測試斷言兩者同源（agent-decided）。

**W0-03 `push.reviewed-sha` 加嚴：最後一輪每個裁定的 `sha` 對到 `reviewed_sha`**　after: W0-01
- 檔：`loom_checker.py`（`check_reviewed_sha` 增：`scored_verdicts()` 那一輪每個裁定必須有 `sha`，`git rev-parse --verify <sha>^{commit}` 解析後與 `reviewed_id` 相等；零裁定時不報、交給 `push.verdicts-ge-2`；`--list-rules` 描述更新）、`loom-code/contract/manifest.yaml:120`（verdicts 文法加 `sha`）、`loom-code/contract/templates/review.json`（範例裁定加 `sha`）、`loom-code/scripts/test_loom_checker_push.py`（或既有 push 測試檔；建 review.json 的 helper 一處加 `sha`）。
- 測：先寫——最後一輪一個裁定缺 `sha` → 擋；`sha` 指向較舊 commit → 擋；全對 → 過；scope 標成 spec 也照樣要求。
- 風：既有 fixture 大量建 review.json——改 helper 不逐測試改；若有測試刻意省略 verdicts 欄位，先讀該測試的意圖再動（agent-decided）。

**W0-04 `push.review-only-head` 加嚴：關閉 commit 的形狀重算**　after: W0-01, W0-03　review: after-task
- 檔：`loom_checker.py`（`check_review_only_head` 增：以 `git diff --raw --no-renames HEAD^^ HEAD^` 讀被審 commit；若動到 `docs/loom/intent/*.md` 且 `status:` 由非 closed 變 closed（`STATUS` 的 closed alternative）→ 該 commit 只能動這一檔、`git diff -U0 HEAD^^ HEAD^ -- <path>` 恰一減一加且皆 `status:` 行、`HEAD^^` 必須本身是 checkpoint（只動 review.json 且其 `reviewed_sha` 解析為 `HEAD^^^`）；merge commit 因走 first-parent diff 一樣被讀；`--list-rules` 描述更新）、push 測試檔。
- 測：先寫五案——正常關閉鏈 R1→C→R2 → 過；C 多動一檔 → 擋；C 同檔多改一行 → 擋；R1→A→C→R2（A 為 docs）→ 擋（父不是 checkpoint）；merge commit 在 HEAD^ 帶 closed 轉換又動別檔 → 擋。
- 風：`HEAD^^` 對根 commit 不存在——先查父數，缺父即擋並說明（agent-decided：fail-closed）。

**W0-05 `push.dispatch-covers-tasks`：內容綁定的 plumbing 豁免**　after: W0-01　review: after-task
- 檔：`loom_checker.py`（`check_dispatch_covers_tasks` 對 `_is_host_plumbing()` 命中的路徑加豁免判定：執行中的 checker 以 `Path(__file__)`（不 resolve）判斷——位於 repo `.codex/hooks/` 下 → 副本、無豁免；否則其目錄旁需有 `../contract/manifest.yaml`，否則無豁免；副本印記 `# loom-checker <version>` 須等於 `codex_scaffold.plugin_version()`（sibling import）；逐路徑比對 blob＋mode：`loom_checker.py`／`git_exec.py` 對正本去印記行、`loom-checker` 對 `SHIM_TEMPLATE` 渲染、`contract/<rel>` 對 `../contract/<rel>`；刪除（無 blob）、mode 120000（symlink）、無對應正本一律不豁免；`.loom-hook-fired` 忽略）、`loom-code/scripts/codex_scaffold.py`（若需把渲染／去印記抽成可 import 的函式）、push 測試檔。
- 測：先寫——本 repo 樹裡重跑 `codex_scaffold.py --repo .` 後 commit 無 trailer → 過；改一 byte／多一檔／刪一檔／只改 mode／換成 symlink 各一案 → 擋；把 checker 複製到臨時 repo 的 `.codex/hooks/` 下執行 → 純刷新也要 trailer。
- 風：本 repo 的 `.codex/hooks/` 另有自己的 gate 腳本（`validate-skill-folder-structure.sh` 等），豁免只認 scaffold 寫的那幾個檔名，維持 W4-02 的範圍（agent-decided）。

### W1 — 站文字、版本、瑕疵、收尾
checkpoint：wave-end 兼 branch-end。

**W1-01 ship／review 站文字：關閉順序與裁定的 `sha`**　after: W0-04
- 檔：`loom-code/skills/ship/SKILL.md`（§6 改成：push → `gh pr create` → `docs(loom): close intent <change-id>` → 再跑一輪 `loom-code:review` scope `branch-end`（兩位 fresh reviewer、docs＋user-judgment-leak 鏡頭、無盲跑、探針重釘）→ review-only commit → push；刪「狀態行不能在分支上寫」段）、`loom-code/skills/review/SKILL.md`（每個裁定記 `sha: <HEAD 於派工時>`；worked record 範例加 `sha`；spec 輪記 `spec_sha`）。
- 測：既有 skill 字數／mechanisms 測試綠；`check_mechanisms.py` 若把站文字當 population，先跑 `python3 loom-code/scripts/check_mechanisms.py` 確認不紅。
- 風：SKILL.md 有 token 上限（軟 5000）——只改 §6 與 review 站兩句，不擴寫（agent-decided）。

**W1-02 測試瑕疵 R30-O1／O2／O3；R28-O2 記為 moot**　after: W0-05
- 檔：`loom-code/scripts/test_check_mechanisms.py`（:668-670 oracle 釘字面 `5` 並註明 wc 在 LC_ALL=C 給 4；:672 `test_count_is_stable_across_locales` 換成以 `inspect.getsource(check_mechanisms)` 斷言模組內沒有 `subprocess` 呼叫提到 `wc`）、`loom-code/scripts/test_session_start_words.py`（:49 `_run` 改抓 bytes、`decode("utf-8", errors="replace")`）、loom-code CHANGELOG 一行記 R28-O2 moot（其 wc skip-guard 已在 round 30 改寫時消失）。
- 測：這三個本身就是測試；整包綠。
- 風：無。

**W1-03 三個 plugin bump ＋ CHANGELOG ＋ README ＋ Codex manifest 同步**　after: W1-01, W1-02
- 檔：`loom-code/.claude-plugin/plugin.json`（1.0.1）、`loom-design/.claude-plugin/plugin.json`（1.0.1）、`loom-workflow/.claude-plugin/plugin.json`（4.0.1）、三份 CHANGELOG.md、root `README.md` 第 12–14 列版本欄、`python scripts/sync_codex_manifests.py --all` 的輸出。
- 測：先跑 `python -m pytest scripts/ -q` 中的 manifest drift 測試（改前紅、改後綠）；`git diff --stat` 列出三表面都動到。
- 風：loom-design／loom-workflow 沒有程式碼變更，bump 理由是 Acceptance #5（user-confirmed）與其散文描述 status 值——CHANGELOG 一行寫明（agent-decided）。

**W1-04 關閉上一個 intent、補回兩條 repo memory、刷新 `.codex/hooks/` 副本、探針畢業**　after: W0-05, W1-03（副本印記要用 bump 後的 1.0.1，orchestrator 2026-09-03 修正依賴）
- 檔：`docs/loom/intent/2026-09-02-simple-loom-flow.md`（`status: closed 2026-09-03 — PR #780`）、`docs/loom/memory/run-the-push-gate-at-every-checkpoint-not-only-the-intake-gates.md`、`docs/loom/memory/a-recorded-word-count-must-be-python-split-never-wc.md`、`docs/loom/memory/README.md`（三者從已關的分支 `close-intent-simple-loom-flow` 的 commit ee5e104e 取回）、`.codex/hooks/{loom_checker.py,git_exec.py,contract/**}`（`codex_scaffold.py --repo .` 刷新，印記 1.0.1；**帶 `Task: W1-04` trailer**——裝置端 1.0.0 的閘沒有豁免）。
- 檔（追加，kouko 2026-09-03）：把 `evidence/probes/test_abuse_close_commit_shape.py` 與 `test_abuse_plumbing_exemption.py` 裡與 `test_loom_checker_push.py` 既有案例**不重疊**的案例搬進 `loom-code/scripts/test_loom_checker_push.py`（或同目錄新檔），evidence 原檔留著；重疊判定寫在 commit 訊息裡。常設做法另立 intent `2026-09-03-probes-graduate-to-permanent-tests`。
- 測：`loom_checker.py intent docs/loom/intent/2026-09-02-simple-loom-flow.md` exit 0（W0-01 後 schema 接受 closed）；`intake write-plan 2026-09-02-simple-loom-flow` 被擋；`python3 loom-code/scripts/codex_scaffold.py --self-test` 過；畢業的案例在整包命令下可被收集並綠。
- 風：關閉舊 intent 的 commit 混在本 change 的 diff 裡，不是本 change 自己的關閉 commit，形狀規則不對它生效（它不是 HEAD^ 的關閉鏈）——這正是 spec Acceptance #1 說的「順手改成 closed」（agent-decided）。

**W1-05 新增 memory：本 change 的兩個坑**　after: W1-04
- 檔：`docs/loom/memory/an-open-finding-carries-no-resolved-key.md`（`resolved: "open"` 這種佔位字串會被 `push.open-findings-closed` 當已關）、`docs/loom/memory/an-open-intent-commit-must-carry-its-needs-design-line.md`（連 open 的 intent，最後動到 needs-design 行的 commit 訊息也要逐字帶那行）、`docs/loom/memory/README.md`。
- 測：memory README 的索引測試（若有）綠。
- 風：無。

## Questions asked
① — what — 重述：合併後的三條自卡接縫修掉＋量檢查站成本，對嗎？
① — what — 係數要不要改的決定現在下還是留到第二、三個真實 change？（答：留到之後，這次寫建議）
① — what — PR 的 merge 由 agent 按還是留給你？（答：留給 kouko）
②-spec-round-5 — consequence — Codex 判 fatal、sonnet 判 PASS：A 這次就把兩條既有規則加嚴（動 Constraint）／B 改成先關再審、狀態行不帶 PR 號碼？（答：A）
（第二 vendor 已由 KICKOFF-DEFAULTS 記錄為 codex，未再問。）

## Risks
0. （執行中記錄，orchestrator 2026-09-03）W0 wave-end 未另開一輪：after-task W0-05 的 review-only 已把 reviewed_sha 移到 W0 全部程式碼之後，未審 delta 為空；跨 task 一致性由 branch-end 對 `160658c2..HEAD` 整段重讀。after-task W0-04 走了 5 輪 6 修、W0-05 走了 3 輪 2 修，皆記在 evidence/checkpoint-cost-orchestrator-notes.md。
1. 自指：本分支被裝置端 1.0.0 的 checker 把關，新加嚴對本分支自己不生效；blind-runner 要在乾淨 clone 裡用**分支上的** `loom-code/scripts/loom_checker.py` 走 Acceptance #1 的正反例，不是用 cache 的。
2. Acceptance #4 的 cost 表由 blind-runner 在 branch-end 寫（spec Design decision）：每個 checkpoint ＝ 一個 review-only commit；本 change 的 spec 階段 8 輪是最大成本項，要如實列入建議。
3. W0 五個 task 全在 `loom_checker.py`，循序執行、每個 task 跑整包（2–2.5 分）；after-task 兩次 ＋ wave-end 一次，加上 spec 8 輪，派工數會明顯高於 #771 replay——這是 REQ-4 要量的東西，不是要藏的。
4. Acceptance #5 的裝置端驗證（`claude plugin update` 後 cache 出現 1.0.1）只能在 merge 後做；盲跑報告如實記為「merge 後待驗」。
