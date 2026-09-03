# 既有對抗探針畢業成永久測試 — plan
intent: 2026-09-03-probes-graduate-to-permanent-tests@20d79ac3

## Current State Evidence
- Forward：整包命令 `docs/loom/KICKOFF-DEFAULTS.md` 的 `package-tests:` 行只收集 `loom-code/scripts/ scripts/ .claude/hooks/`；`docs/loom/**/evidence/probes/*.py` 不在路徑內，merge 後無人跑。
- Reverse：先例 `loom-code/scripts/test_loom_checker_push_probes.py:1-19`——2026-09-03-loom-post-merge-seams 的 W1-04 已把 12 個不重疊案例搬進來，檔頭 docstring 記畢業／重疊處置，`sys.path.insert(0, str(Path(__file__).parent))` 後直接 import 同目錄的 `loom_checker` 與姊妹測試的 fixture。
- Error：兩個待畢業探針檔用 `REPO_ROOT = Path(__file__).resolve().parents[N]` 反推 repo 根，再 `sys.path.insert(0, REPO_ROOT/"loom-code"/"scripts")`；搬到 `loom-code/scripts/` 後 `parents[N]` 的層數不同，不改會指到錯的目錄（`docs/loom/2026-09-03-package-tests-run-in-parallel/evidence/probes/test_abuse_package_tests_command.py:36-40`、`docs/loom/2026-09-03-small-change-lane/evidence/probes/test_abuse_change_lane.py:43-49`）。
- Data：33 個案例（7＋26）；函式名與既有 `loom-code/scripts/test_*.py` 的 `def test_` 零同名（2026-09-04 以 `comm -12` 比對；12 個同名全是 post-merge-seams 已畢業的那批）。change_lane 探針每案例開臨時 git repo，單跑約 25 秒；整包 `-n auto` 本機 34 秒。
- Boundary：不動 evidence 原檔、不動 checker／skill／KICKOFF；本 change 自己的對抗探針不畢業。

## Task DAG

**W0-01 兩個探針檔複製成永久測試**　after: —
- 檔：新增 `loom-code/scripts/test_probes_package_tests_command.py`（來源 `docs/loom/2026-09-03-package-tests-run-in-parallel/evidence/probes/test_abuse_package_tests_command.py`）與 `loom-code/scripts/test_probes_change_lane.py`（來源 `docs/loom/2026-09-03-small-change-lane/evidence/probes/test_abuse_change_lane.py`）。內容逐字複製，只改三處：檔頭 docstring 第一段加一句出處與畢業日；`REPO_ROOT` 改為 `Path(__file__).resolve().parents[2]`；`sys.path.insert` 改為 `Path(__file__).parent`（照 `test_loom_checker_push_probes.py` 先例）。不改任何斷言、fixture、案例名。
- 測：deliverable 本身就是測試——RED 的定義是搬家前整包命令收集不到這 33 個名字（`python3 -m pytest loom-code/scripts/ --collect-only -q | grep -c 'test_probes_'` 得 0），GREEN 是搬家後得 33 且整包全綠。實作者另量三個數字寫進回報：兩個探針檔單獨跑（`-n auto`）的秒數、整包搬家前、整包搬家後。
- 風：agent-decided——檔名用 `test_probes_<topic>.py` 而非沿用 `test_abuse_`，與先例 `test_loom_checker_push_probes.py` 的「probes」字眼一致，讓 `grep test_probes_` 一次找到所有畢業檔；agent-decided——不做斷言層去重（intent Acceptance #2 只以函式名判），重疊的行為由既有測試與探針各測一次，代價是整包多幾秒。

## Questions asked
1 — what — 甲／乙二選一：甲＝這次只做把主幹上既有探針中不重疊的搬進永久測試（小車道），ship 站那句話併進 C 組；乙＝照 intent 原文只加 ship 站那句話。重述甲：既有測試沒蓋到的攻擊案例變成永久測試，整包命令會跑到、evidence 原檔不動、整包時間不比探針本身多。對嗎？（答：甲）
1 — what — 追問「整包時間不比探針本身跑的時間多」是什麼意思（答覆：搬＝複製，不重寫成更慢的 fixture）。

## Risks
1. 小車道首測（Acceptance #4）：本 change 只碰 `loom-code/scripts/test_*.py`（tests-only）與 `docs/loom/<id>/**` 紀錄——checker 應判 small；若判 full，原因寫進 blind-run 報告的「我替你決定」段，不硬改。
2. change_lane 探針的臨時 repo 與 `test_loom_checker_push.py` 的 fixture 在 `-n auto` 下各自用 `tmp_path`，不共用狀態；實作者跑整包兩次確認無互踩。
3. 一個 wave、一個 task、無 after-task；只有 branch-end 一個 checkpoint。KICKOFF `second-vendor: codex` 在小車道仍適用（只有 `ask` 依車道免問），唯一的讀者跑 codex 腿；codex 不可用則照站規則記 fallback。
