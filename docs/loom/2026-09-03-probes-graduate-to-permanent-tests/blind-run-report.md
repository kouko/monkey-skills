# 既有對抗探針畢業成永久測試 — what I tried and what happened

Tried on 2026-09-04, in the working tree of the change branch at 4483d347 (small lane: no separate clean-copy blind run is owed — every Acceptance line is settled by running a command and comparing a number; the numbers below were produced by the implementer, the adversary and the push gate, and re-run by the orchestrator at 4483d347).

## What you asked for, one line at a time

### 1. 主幹上尚未畢業的 2 個探針檔（package-tests、change_lane）的案例出現在 `loom-code/scripts/` 的測試檔裡，整包命令（KICKOFF 的 package-tests 行）收集並跑過它們，全綠；4 個 evidence 探針原檔的內容與 main 上一字不差。
- **How I tried it**: ran `python3 -m pytest loom-code/scripts/ --collect-only -q | grep -c test_probes_` before and after the copy; ran the KICKOFF package command three times after; ran `git diff --stat origin/main -- docs/loom/*/evidence/probes/`.
- **What happened**: collected count 0 → 38 (33 test functions, two of them parametrized); package command 1096 → 1134 passed, three runs green; the evidence diff is empty.
- **Evidence**: commit b8932c23 (the two new files); probe `test_evidence_probe_originals_are_byte_identical_to_origin_main` and `test_graduated_copy_diverges_from_source_only_by_the_three_permitted_edits` in `evidence/probes/test_abuse_probe_graduation.py`, both green; the push gate's own re-run of the package command at 4483d347 exited 0.
- **Verdict**: works.

### 2. 搬進來的測試函式名沒有一個與既有 `loom-code/scripts/test_*.py` 裡的函式同名；被略過的案例在 plan 或 commit 訊息裡逐一點名，附一句「既有哪個測試已蓋到」。
- **How I tried it**: `comm -12` on every `def test_` name of the two copies against every other `loom-code/scripts/test_*.py` (orchestrator, before the plan; implementer, after the copy; adversary probe `test_graduated_test_and_class_names_do_not_collide_with_any_other_test_file`, which also checks class names).
- **What happened**: zero collisions; nothing was skipped, so there is no skipped-case list — all 33 functions were copied.
- **Evidence**: commit b8932c23 body; the adversary probe above, green.
- **Verdict**: works.

### 3. 整包命令的 wall-clock 時間增加不超過這 2 個探針檔單獨跑的 wall-clock 時間總和（兩邊都用同一台機器、同一個 `-n auto` 量）。
- **How I tried it**: the implementer timed the two evidence files alone with `-n auto`, then the package command before the copy and twice after; the orchestrator timed the package command twice more at the reviewed commit.
- **What happened**: probe files alone 3.85 s; package before 35.92 s; after 41.07 s / 39.42 s (implementer), 38.29 s / 38.46 s (orchestrator). Increases 5.15 s / 3.50 s / 2.37 s / 2.54 s against the 3.85 s bar: three of four runs inside it, one outside by 1.30 s.
- **Evidence**: commit b8932c23 body; `evidence/cost.md`.
- **Verdict**: partly — met in 3 of 4 runs; the one miss (1.30 s over) is within this machine's run-to-run spread under `-n auto` (38.29 vs 41.07 s on identical trees), and the copies are byte-identical apart from three path lines (probe 1), so the cost is the probes' own, not a slower rewrite. Whether one miss in four counts as "不超過" is yours to call; the "share fixtures / fewer subprocesses" intent the Constraints defer to is the fix if you want it met every run.

### 4. 這個 change 從 intent 確認到 push 閘乾跑通過，不超過 20 分鐘（小車道首測；時間以 commit 時間戳為準）。
- **How I tried it**: read the commit timestamps on the branch.
- **What happened**: intent confirmed 07:29:11 → review-only commit 07:45:59 (both commit timestamps). The push gate ran right after that commit in the orchestrator's shell; its output is not timestamped, so its time is bounded, not recorded: after 07:45:59 and before 07:49 (the shell's next `date` print, after the round-3 review). That bounds the span at 17–20 minutes. The checker recomputed the lane as `small` at every step (one reviewer, no blind run).
- **Evidence**: `git log --format='%ci %s' 2df247b1..f5824656`; `evidence/cost.md`.
- **Verdict**: partly — 17 minutes by the recorded commits, ≤20 by the bound; the gate's own minute is not on record. From the next change the gate output is saved with a timestamp. This report and the cost table are committed after the gate passed, which owed the read rounds recorded in review.json.

## 對你既有的資料做了什麼 (what this did to data you already had)

Nothing — it only added two test files under `loom-code/scripts/` and this change's own records under `docs/loom/`. The four evidence probe files on `main` were read, not written.

## I decided for you

- **File names `test_probes_<topic>.py`** — I picked them over keeping `test_abuse_` so `grep test_probes_` finds every graduated file, matching the earlier `test_loom_checker_push_probes.py`. Changing it later is a rename.
- **No dedup by assertion target, only by function name** — the intent's Acceptance #2 says name; behaviour overlap between `test_probes_change_lane.py` and `test_loom_checker_push.py` therefore runs twice, costing a few seconds per package run.
- **The reviewer's one important finding was fixed, not dismissed** — Codex found the plan said 33 cases where pytest collects 38 items; the plan now says both numbers. No finding was dismissed.

## Things I am not sure you want

- The repo's Codex mirror `.codex/hooks/loom_checker.py` has drifted from `loom-code/scripts/loom_checker.py` (the adversary found it still admits `standing` to the small lane and lacks the adversary-coverage rule). Not this change's — the package command never collects it — but a Codex-hosted session would run the stale copy. Worth folding into the next full-lane change.
