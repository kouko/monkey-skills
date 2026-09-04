# checker 四條接縫一次修 — plan
intent: 2026-09-04-checker-seams@5e5a21ab

## Current State Evidence
- Forward（templates glob）：`loom-code/scripts/loom_checker.py:365-388` `interface_surfaces()` 讀 manifest 預設（`loom-code/contract/manifest.yaml:145`，含 `**/templates/**`）並只允許 KICKOFF 加 glob；`:781-793` `touched_interface_surfaces()` 把 `changed_paths()` 逐一比對 glob，`intent.kind-recompute`（`:809`）與 `intent.needs-design-recompute`（`:796`）都讀它。`artifact_types()` 對 `loom-code/contract/templates/intent.md` 回 `docs`（manifest `:162` `**/*.md`），對 `src/cli/x.py` 回 `code`；`.codex/hooks/**` 早已被 `_is_host_plumbing` 排除（`:499-505`）。
- Forward（squash）：`:731-780` `check_needs_design_reason()` 無 `--commit-msg` 時讀 `deciding_commit()`（`:672-685`：最新一個改到 frontmatter `status:`／`needs-design:` 的 commit）的訊息；主幹上該 commit 是 squash（例如 `4e25360c`，subject 尾 `(#780)`），訊息無該行。真正的 merge commit（兩個 parent）今天就已經過：`git show` 對 merge 不印 diff，`_decides_in_frontmatter()` 回 False，`deciding_commit()` 落到分支上帶那行的原 commit（W0-01 對抗者實測）。分支上的 commit 由 push 閘與 CI 的 `intent` 子命令已逐字驗過。
- Forward（探針去重）：`:2616-2733` `check_probes_adversarial()` 對每筆 `kind: adversarial` 紀錄執行 `artifact_argv(repo, artifact)`（整檔，非紀錄命令），`usable` 逐筆累計，`ADVERSARIAL_FLOOR = 3`（`:2421`）以紀錄計；`--list-rules` 文字在 `:170-176` 附近的 RULES 表。2026-09-03-loom-post-merge-seams 的 review.json 有 126 筆 `kind: adversarial` 紀錄指向 13 個不同 artifact（其中 3 個 code／docs 檔各被 60／55／1 筆引用；W0-01 對抗者實數，plan 初稿寫的 23／2 是錯的）。
- Reverse：`AGENTS.md:37` 仍把 `check_open_questions.py` 列為命令面；`loom-code/scripts/test_check_open_questions.py:21` 是它唯一的測試；沒有 SKILL、hook、CI、`loom_checker.py` 引用它（`grep -rn check_open_questions` 其餘全在 `docs/loom/` 歷史與 CHANGELOG）。
- Error：`.codex/hooks/loom_checker.py` 與 `loom-code/scripts/loom_checker.py` `cmp` 第 2 行即不同（版本戳），內容落後 #784 的 W0-02 修正；`loom-code/scripts/codex_scaffold.py --repo .` 是唯一合法寫入方式（檔頭「do not edit by hand」）。CI job `pytest + knowledge-drift + codex-manifest-drift`（`.github/workflows/loom-code-ci.yml:86`）只比 manifest，不比 checker 本體。
- Data：`docs/loom/KICKOFF-DEFAULTS.md` `second-vendor: codex — …flip to ask…`；review.json 的 `second_vendor` 頂層鍵由 `_resolve_second_vendor_ask()`（`:3176-3230`）讀，小車道免、完整車道必填。ship SKILL.md 3242 字（帽 4500，軟 3750）；站摘要表由 `loom-code/scripts/test_station_summary_table.py` 對九處同步。規則數 27。
- Boundary：不動規則清單（27）、不加 waiver、不動 `intent.schema`、不動模板文法；不動 loom-design／loom-workflow 檔案（若 W1-03 的站摘要同步碰到，跑該 plugin 的 suite）。

## Task DAG

**W0-01 對抗者先寫三條規則的探針**　after: —
- 檔：新增 `docs/loom/2026-09-04-checker-seams/evidence/probes/test_abuse_templates_glob.py`、`test_abuse_squash_needs_design.py`、`test_abuse_probe_rerun_dedup.py`（每檔 ≥4 案例：今天就該擋的要綠、實作目標刻意紅並在 docstring 標 `RED until W0-0x`）。攻擊面：(1) `templates/` 下的 `.py`／`.html`／`.tsx` 仍要被抓、只有 docs／skill 型別放行、KICKOFF 仍不能減 glob；(2) 分支上漏行照擋、squash 判定不能被普通 commit 冒充（subject 手寫 `(#1)` 而非 merge）、merge commit 兩個 parent；(3) 同檔 N 筆只跑一次、失敗檔所有紀錄不可用且訊息一次、不同檔各跑一次、既有 loom-post-merge-seams 紀錄形狀（2 檔 23 筆）門檻結果不變。
- 測：探針檔本身；跑 `python3 -m pytest <三檔> -q` 記紅綠各幾條。
- 風：agent-decided——探針用 `subprocess` 跑 `loom_checker.py` 真命令（不 mock），沿用 `test_loom_checker_push.py` 的臨時 repo fixture。

**W0-02 只有 `code` 型路徑算介面**　after: W0-01
- 檔：`loom-code/scripts/loom_checker.py` `touched_interface_surfaces()`：比對 glob 後再以 `artifact_types()` 過濾，只留型別為 `code` 的路徑（docs／skill／intent／plan／memory／evidence／standing／map 一律不是使用者介面）；印出的 `interface-surfaces (…)` 行加一句「non-code paths excluded」。docstring 寫明為何不違反「只能加不能減」：KICKOFF 的 `artifact-types` 是 reserved、checker 不讀，agent 無法藉此把介面排除掉。`test_loom_checker_intent.py` 加兩測（templates/*.md 放行、templates/*.tsx 與 `src/cli/x.py` 仍擋）。
- 測：W0-01 的 `test_abuse_templates_glob.py` 全綠；新增兩測先紅。
- 風：`**/templates/**` 下的 `.html`／`.jinja` 型別是 `code`，照樣被抓——這是要的。

**W0-03 squash 之後的 needs-design 行**　after: W0-02
- 檔：`loom_checker.py` `check_needs_design_reason()`：deciding commit 訊息無該行時，若該 commit 是 GitHub squash（單 parent、subject 以 ` (#<n>)` 結尾、且在主幹第一父系鏈上：`git merge-base --is-ancestor <sha> <trunk>`），則視為「決定在被閘過的分支上做過」，pass 並印一行 note 說明來源；否則照擋。`test_loom_checker_intent.py` 加測：squash 形狀 pass、分支上普通 commit 手寫 `(#1)` 但不在主幹上仍擋、無該行普通 commit 仍擋；真正 merge commit 今天已過，只需守住（W0-01 探針 `test_real_merge_commit_on_main_already_passes_today`）。
- 測：`test_abuse_squash_needs_design.py` 全綠；Acceptance #3 兩半。
- 風：agent-decided——不改 PR body 模板（那是 ship 站文字，另一個 task 面），主幹判定以 git 拓撲為準而非訊息文字，冒充 `(#n)` 的分支 commit 不在主幹第一父系鏈上所以不會過。

**W0-04 探針按檔案去重執行**　after: W0-03
- 檔：`loom_checker.py` `check_probes_adversarial()`：先把通過格式檢查的紀錄按 `artifact` 分組，每個檔案只 `subprocess.run` 一次，結果套回該檔所有紀錄；失敗訊息每檔一則（列出引用它的紀錄數）；`out` 的 observed 行每檔一行加「referenced by N records」。`--list-rules` 文字改為「…records at least three adversarial probe records against the reviewed commit; a file referenced by several records is executed once, and every record of a failing file is unusable」。計數單位維持**紀錄**（agent-decided：改成檔案會讓 #785 這種一檔六筆的既有紀錄失格，intent Acceptance #4 要求既有紀錄結果不變）。去重後要不要平行：實作者量一次（同檔 N 筆去重前後的 `push` 秒數）寫進回報再決定，預設不平行。既有紀錄的「結果不變」以單元測試的紀錄形狀（多筆同檔、floor 以紀錄計）證明——歷史 review.json 的 sha 在乾淨樹本來就重跑不了。`test_loom_checker_push_probes.py` 或 `test_loom_checker_push.py` 加測。
- 測：`test_abuse_probe_rerun_dedup.py` 全綠；記錄執行次數的測試先紅。
- 風：紀錄的 `sha`／artifact 存在等逐筆檢查仍逐筆做（只有執行去重），失格紀錄不影響同檔其他紀錄的可用性判定順序。

**W1-01 刪舊腳本**　after: W0-04
- 檔：刪 `loom-code/scripts/check_open_questions.py`、`loom-code/scripts/test_check_open_questions.py`；`AGENTS.md:37` 那條命令面項目刪除。
- 測：新測 `loom-code/scripts/test_no_stale_open_questions_script.py`：兩檔不存在、`grep -rn check_open_questions` 排除 `docs/loom/` 與 CHANGELOG 後為空、`--list-rules` 仍 27 條（先紅）。
- 風：`docs/loom/memory/` 兩則提到它的舊 memory 是歷史，不動。

**W1-02 ship 站畢業那一句**　after: W0-04
- 檔：`loom-code/skills/ship/SKILL.md` §3 Memory 加一段（≤60 字）：本 change `evidence/probes/` 裡的 pytest 探針，與既有測試不重疊者（以函式名判）複製進永久測試目錄、帶 `Task:` trailer、原檔不刪；docs／skill 型的冷讀報告不畢業。九處站摘要表若需同步照 `test_station_summary_table.py`。
- 測：`loom-code/scripts/test_ship_station_text.py`（新或既有）斷言那段存在且字數帽內（先紅）。
- 風：ship 站是 `skill` 型，會把 checkpoint 拉成 skill lens＋冷讀；接受。

**W1-03 KICKOFF ask、codex 鏡射、版本**　after: W1-01, W1-02
- 檔：`docs/loom/KICKOFF-DEFAULTS.md` `second-vendor: ask — kouko decides per change (2026-09-04)`；`python3 loom-code/scripts/codex_scaffold.py --repo .` 重寫 `.codex/hooks/`；`loom-code/.claude-plugin/plugin.json` 1.1.0→1.2.0、`loom-code/CHANGELOG.md`、marketplace／README 版本同步（照 `test_sync_codex_manifest.py`、`plugin version bump` CI）。
- 測：`test_codex_scaffold.py` 既有；新測 `test_codex_mirror_matches_checker`：`.codex/hooks/loom_checker.py` 與 `loom-code/scripts/loom_checker.py` 逐位元相同（先紅）。
- 風：scaffold 重寫後 `.codex/hooks/` 是 host plumbing，不進 changed_paths；版本 bump 是 `code`（json）→ 完整車道本來就是。

## Questions asked
1 — what — 你要的是 checker 四條小接縫加三件殘務在一個分支一次修完；做完後（七條可見結果逐條）；規則數不變、不加 waiver、每條 checker 改動對抗者先寫探針；四條原 intent 併入後標 withdrawn。對嗎？（答：對）
1 — what — 前置討論：探針先寫要不要擴到所有 code task（答：先記下來、之後再討論；本 change 不含）

## Risks
1. 三個 W0 task 都改 `loom_checker.py` 同一檔：序列執行、同一工作樹，不開 worktree。W1-01／W1-02 檔案互斥可平行（各自 worktree，`--no-ff` 合回）。
2. checkpoint：W0 wave 結束（delta 必超 400 行）一次 wave-end；W1 結束 branch-end。build 期 1／5。
3. W0-03 的「squash 判定」是這個 change 最容易被冒充的點；W0-01 探針已寫「分支 commit 手寫 `(#1)`」的攻擊。
4. W1-03 改 KICKOFF 為 `ask` 後，本 change 的 branch-end 讀者就要 review.json 的 `second_vendor` 答案：在 wave-end 前問 kouko 一次並記下。
