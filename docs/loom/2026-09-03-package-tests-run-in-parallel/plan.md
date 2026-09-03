# 整包測試平行跑 — plan
intent: 2026-09-03-package-tests-run-in-parallel@11aca3a8

## Current State Evidence
- Forward：命令的活體載體只有兩處——`docs/loom/KICKOFF-DEFAULTS.md:8`（`package-tests: python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q`）與 `.github/workflows/loom-code-ci.yml:114`（同路徑，`-v`）。其餘出現處全是 `docs/loom/plans/`、`docs/loom/specs/`、`docs/loom/memory/` 的歷史紀錄，不動。
- Reverse：`loom-code/scripts/loom_checker.py:2294`（`declared_test_command` 讀 KICKOFF 那行）→ `push.probes-package-tests` 逐字比對 review.json 的 `package-tests` 探針命令並自己重跑；review 站的 reviewer／blind-runner 也照這行跑。
- Error：本機（16 核、macOS）串行 200 秒；CI（ubuntu，4 核）89 秒。subagent 因此撞 Bash 120 秒預設逾時五次（`docs/loom/2026-09-03-loom-post-merge-seams/evidence/checkpoint-cost-orchestrator-notes.md`）。量測（2026-09-03，`uv run --with pytest --with pytest-xdist --with pyyaml --with markdown-it-py … -n auto`）：**1061 passed in 34.34s**，零失敗。
- Data：測試相依沒有宣告檔——CI 的 `Install test deps` 步驟寫死 `pip install pytest pyyaml`（`loom-code-ci.yml:108`），本機靠使用者環境（`python3` = conda `dbt-redshift`，有 pytest 9.0.3、pyyaml，無 xdist）；`markdown-it-py` 也是隱性依賴（adjudication_render 測試）。repo 根沒有 pyproject／requirements；README `## Contributing` 沒有「怎麼跑測試」。
- Boundary：不改任何測試本身；不改探針重跑（另一 intent）；不動 loom-design／loom-workflow 各自的 CI 測試命令（它們跑別的 suite）；`loom_checker.py:1648` 的 `os.chdir` 只在 hook 子程序模式，與平行無關。

## Task DAG

**W0-01 開發依賴有一個宣告處，CI 與 README 都從它裝**　after: —
- 檔：新增 `requirements-dev.txt`（repo 根：pytest、pytest-xdist、pyyaml、markdown-it-py，不釘死版本）；`.github/workflows/loom-code-ci.yml` 的 `Install test deps` 改為 `python3 -m pip install --quiet -r requirements-dev.txt`（保留原註解說明各依賴為何存在）；`README.md` `## Contributing` 加三行「跑測試：`python3 -m pip install -r requirements-dev.txt`，再跑 KICKOFF-DEFAULTS 的 `package-tests:` 那行」。
- 測：新檔 `loom-code/scripts/test_package_tests_command.py`：`test_dev_requirements_declare_xdist_and_ci_installs_from_them` —— 讀 `requirements-dev.txt` 斷言含 `pytest-xdist`、讀 workflow YAML 斷言 install 步驟含 `-r requirements-dev.txt`（今天兩者皆不存在 → RED）。
- 風：agent-decided——放 repo 根而非 `loom-code/`，因為這條 suite 橫跨 `loom-code/scripts/`、`scripts/`、`.claude/hooks/` 三處，是 repo 級的；不用 pyproject，因為 plugin 目錄不可有 build-system（既有慣例）。

**W0-02 命令三處同步改成 `-n auto`**　after: W0-01
- 檔：`docs/loom/KICKOFF-DEFAULTS.md:8`（`package-tests: python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q -n auto — …`，註解記平行度決定：`-n auto` 取 runner 核心數，本機 16 核 34 秒、CI 4 核預期 ~40 秒；固定數字會在其中一邊過載或閒置）；`.github/workflows/loom-code-ci.yml:114` 同樣加 `-n auto`；`loom-code/scripts/test_package_tests_command.py` 加第二個測試。
- 測：`test_kickoff_and_ci_run_the_same_parallel_command` —— KICKOFF 的 `package-tests:` 值（去掉 `— …` 註解）與 CI run 行，路徑相同且都含 `-n auto`（`-q`／`-v` 的差異保留，因為 CI 要逐條輸出）；今天兩者皆無 `-n auto` → RED。
- 風：本機 push 閘用使用者當下的 `python3` 跑這行；該環境沒有 xdist 就會 `unrecognized arguments: -n`。agent-decided——實作者在改 KICKOFF 前先 `python3 -m pip install -r requirements-dev.txt` 到當下環境（同一個已裝 pytest／pyyaml 給本 repo 用的環境；可逆、不花錢、不動資料），並在回報寫明裝到哪個環境。

## Questions asked
1 — what — 你要的是整包測試從 200 秒壓到 60 秒以內（分到多核心跑）；做完後：乾淨環境照 README 裝依賴、跑 KICKOFF 那行 1061 全過且低於原本三分之一；CI 同一行綠、push 閘逐字比對照常；連跑三次一致。不動測試寫法、不動探針去重；平行度由我量了決定。沒有一次性難回頭的選擇。對嗎？（答：對）

## Risks
1. 平行後測試互踩：量測一次零失敗；再連跑兩次（plan 撰寫時已排程）；盲跑照 Acceptance #3 連跑三次。若出現非決定性失敗，不在本 change 修測試（intent Constraints）——記成 finding、該測試暫以 `-p no:randomly`／`--dist loadfile` 之類**命令層**手段處理，仍是同一行命令的一部分。
2. 歷史 review.json 的 `package-tests` 探針記的是舊命令：checker 只比對**本 change** 的 review.json，舊紀錄是歷史，不動。
3. 五處版本／命令散落的老坑：這次命令只有兩個活體載體＋checker 從 KICKOFF 讀，W0-02 的測試把兩處綁在一起，之後漂移會紅。
4. 一個 wave、兩個 task、無 after-task；只有 branch-end 一個 checkpoint（build 期間 0／5）。
