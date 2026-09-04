# checker 四條接縫一次修：templates glob、舊腳本、squash 後的 needs-design、探針去重
originator: kouko
kind: engineering
needs-design: no — 改 checker 規則的重算方式、manifest 預設 glob、刪一支舊腳本、ship 站一句話、KICKOFF 一行；沒有使用者讀或輸入的介面，也沒有多狀態行為
evidence: [docs/loom/2026-09-03-loom-post-merge-seams/evidence/, docs/loom/2026-09-03-probes-graduate-to-permanent-tests/evidence/]
status: closed 2026-09-04 — PR #786

## Problem
四條 open intent 各自都是 checker／contract 的小修，各開一個 change 要付四次完整車道的固定成本（兩讀者＋盲跑＋對抗）；它們同屬 loom-code、同是 gate 型 task，合成一個 change 只付一次。四條原文（併入後改 `withdrawn — superseded by 2026-09-04-checker-seams`）：
1. `**/templates/**` 預設被當成使用者介面，逼只改 agent 樣板的 engineering change 改成 product（2026-09-03-templates-glob-is-not-a-user-surface）。
2. 舊腳本 `check_open_questions.py` 的文法與 1.0 intent 模板的 `- none` 打架，沒有站呼叫它，但 `AGENTS.md` 命令面仍列它，reviewer 拿它當閘（2026-09-03-stale-open-questions-script-contradicts-template）。
3. squash merge 後主幹上「最後改到 needs-design 行的 commit」是 squash commit，訊息沒那一行，主幹上每個已合併 intent 跑 `intent` 子命令都紅（2026-09-03-squash-merge-drops-the-needs-design-line）。
4. `push.probes-adversarial` 對每筆紀錄整檔重跑探針；紀錄按案例一筆，同一檔被跑十幾次，門檻「3 支」的計數單位曖昧（2026-09-03-push-gate-reruns-probes-per-artifact）。

順手三件，都是這幾個 change 留下的、不值得各開 intent：
5. `docs/loom/KICKOFF-DEFAULTS.md` 的 `second-vendor` 從 `codex` 改成 `ask`（1.1.0 已裝，#784 留的）。
6. `.codex/hooks/loom_checker.py` 鏡射已落後主 checker（仍讓 standing 進小車道、缺 adversary 覆蓋規則；#785 對抗者發現）。
7. ship 站 memory 步驟加一句：本 change 探針裡與既有測試不重疊的案例畢業成永久測試（從 2026-09-03-probes-graduate-to-permanent-tests 移出）。
8. 「探針先寫」從 gate 型 task 擴到**完整車道的所有 code／gate 型 task**；小車道不變（kouko 2026-09-04 併入，依據：獨立對抗測試的實測收益（SWE-ABS 19.7% 假通過被抓）＋有成本數據的先例全按風險分級，車道即風險線）。

## Proposed outcome
上述七件在一個分支上做完；每條 checker 改動都由對抗者先寫探針、實作者再做（現行 gate 型規則）。`--list-rules` 規則數不變；不加 waiver。

## Acceptance
1. 乾淨 clone 裡改 `loom-code/contract/templates/intent.md` 一行、intent 寫 `kind: engineering`：`loom_checker.py intent` 與 `intake write-plan` 都 exit 0；改 `src/cli/x.py` 一行照樣被 `intent.kind-recompute` 擋。
2. `loom-code/scripts/check_open_questions.py` 與它的測試檔不存在；`grep -rn check_open_questions` 只剩 CHANGELOG 與 `docs/loom/` 歷史紀錄。
3. 乾淨 clone 的 main 上對 `docs/loom/intent/2026-09-02-simple-loom-flow.md` 跑 `loom_checker.py intent`：exit 0；分支上把 needs-design 改掉而 commit 訊息沒帶那行：照樣被擋。
4. review.json 同一探針檔被引用 N 筆時 `push` 只執行它一次（以執行次數證明）；`--list-rules` 對 `push.probes-adversarial` 的說明一句講清計數單位；探針檔失敗時所有引用它的紀錄都不可用、錯誤訊息只出現一次；既有 2026-09-03-loom-post-merge-seams 的紀錄在新規則下結果與現在一致。
5. `docs/loom/KICKOFF-DEFAULTS.md` 的 `second-vendor` 行是 `ask`；本 change 自己的 review.json 記了 `second_vendor` 的答案並過 `push.second-vendor-honoured`。
6. `.codex/hooks/loom_checker.py` 與 `loom-code/scripts/loom_checker.py` 除了 scaffold 寫入的那一行版本戳之外逐位元相同，且版本戳等於 loom-code 的 plugin 版本（user-decided 2026-09-04 決策點③選 (a)：留版本戳、改本條文字；原文「逐位元相同」）。
7. ship 站 SKILL.md memory 步驟有那一句，字數帽內；站摘要表同步測試綠。
8. `loom_checker.py --list-rules` 規則數與 main 相同（27）；整包測試綠。
9. build 站 SKILL.md 的派工順序段說：完整車道中 檔 路徑型別為 `code` 或 `gate` 的 task 先派對抗者；小車道不先派；字數帽內；站摘要表同步測試綠。

## Constraints
- 不加規則、不加 waiver；規則數不增不減。
- 第 1 條的解法要說明為何不違反 KICKOFF「只能加不能減」的原意（建議：artifact_types 的 `docs`／`skill` 型別先於 interface glob 判定）。
- 第 3 條：分支上仍讀 commit；只在找不到帶那行的 commit 且該 commit 是 merge／squash 時退而讀分支歷史或 squash body。
- 第 4 條：探針仍在 reviewed_sha 的乾淨樹重跑，不信紀錄；去重後要不要平行跑由 agent 量過後決定。
- loom-code bump minor 版本；動到 loom-design／loom-workflow 的檔就跑它們的 suite。

## Out of scope
- 其他預設 glob 的重新檢討；其他 pre-1.0 殘留腳本盤點。
- artifact-language-policy（獨立 change，走 spec 站）。

## Open questions
- none
