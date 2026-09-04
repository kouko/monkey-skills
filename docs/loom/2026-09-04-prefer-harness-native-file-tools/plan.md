# 契約敘述對檔案寫入的工具偏好：寫用 host 編輯工具，讀隨便，批次替換用腳本但要驗 — plan
intent: 2026-09-04-prefer-harness-native-file-tools@17184120

## Current State Evidence
- Forward（契約）：四份契約的陷阱段——`loom-code/agents/implementer.md:68`（`## Trap-guards`，`:70-74` 四條：Read-before-Edit、guard 擋兩次、禁 stash、Write 拒 report.md）、`reviewer.md:158`（`## What will get your verdict thrown out`，`:160` 第一條「Editing anything in the repository」）、`blind-runner.md:57`（`## Traps`）、`adversary.md:56`（`## Traps`）。後三份完全沒有工具指引；沒有任何一處提到 `sed -i`／heredoc（CHANGELOG `:4508` 是歷史條目）。
- Forward（派工包）：只有 `loom-code/skills/build/SKILL.md:159-166`「And these standing trap-guards, verbatim:」定義了共用的陷阱句，與 `implementer.md:70-74` 近逐字重複——**兩份副本、沒有共用 reference**。review 站 `SKILL.md:160-179`（讀者包）、`:216-238`（盲跑）、`:239-264`（對抗者）都沒有陷阱句。ship 站沒有派工包（`ship/SKILL.md` 只組 PR body；畢業／nit 批次的實作者派工用的是 build 的包）→ intent 說的「build／review／ship 同步」在 ship 是空集合，plan 記為 N/A 附理由。
- Reverse（誰讀）：`build/SKILL.md:159` 的塊被貼進每個 implementer 派工包；review §3 派 blind-runner、§4 派 adversary 時各自讀自己的契約；reviewer 不寫檔（`reviewer.md:160`）。
- Error（現有測試）：`loom-code/scripts/test_review_station_text.py:29-30` 直接 `read_text` 讀 `agents/reviewer.md`，無共用 helper；字數帽在 `test_reviewer_agent_single_contract.py:34` `AGENT_CAPS = {reviewer 1300, blind-runner 600, adversary 600}`，對 `body_of(text)`（去 frontmatter）斷言；implementer.md 沒帽。reviewer.md 全檔 1334 字、body 逼近 1300——加句子前要量。其他讀 `agents/*.md` 的測試：`test_agent_model_frontmatter.py:14`、`test_probes_positioning_branch_end_r2.py:94-95`、`test_check_skill_crossrefs.py:125,172`。
- Data（守衛與來源）：`.claude/settings.json:5` 與 `.codex/hooks.json:16` 的 PostToolUse matcher 都是 `Write|Edit`；`.claude/hooks/validate-skill-folder-structure.sh:4`、`check-codex-manifest-drift.sh:4` 註解「Triggered: PostToolUse on Write|Edit」。`loom-code/research/2026-07-05-claude-code-codex-dual-compat-patterns.md:53` 把 apply_patch↔Edit 別名標為未確認——intent 已用 openai/codex `hook_names.rs` 確認，plan 不再引用該研究檔的保留。版本 `loom-code/.claude-plugin/plugin.json:3` 與 `.codex-plugin/plugin.json:3` 都是 1.2.1；`CHANGELOG.md:8` 頂端 `## [1.2.1]`；同步測試 `test_sync_codex_manifest.py:31`。
- Boundary：不動 checker、不加規則、不動角色數與站摘要表；契約文字不引用 `docs/`；只規定「寫」，測試要斷言句中沒把 `cat`／`grep`／Read 列為禁止。冷讀方法：上一 change 的 `coldread-*.txt` 沒記 `claude -p` 的旗標，只有 `blind-run-report.md:9` 的散文描述——本次盲跑要重建並**把命令記進 evidence**。

## Task DAG

**W0-01 對抗者先寫探針**　after: —
- 檔：新增 `docs/loom/2026-09-04-prefer-harness-native-file-tools/evidence/probes/test_abuse_tool_preference.py`（≥5 案例）。攻擊面：(1) 四份契約各有一句含 `Edit`／`Write`／`apply_patch` 與 `sed -i`／`heredoc` 字樣、≤40 英文字（`len(str.split())`）；(2) 句中不把 `cat`、`grep`、`Read` 列為禁止（正則：禁止動詞後不接這些字）；(3) 含「壓過之後出現的 host 提醒」語意（`later`／`any time`＋`reminder`／`host`）；(4) `build/SKILL.md` 的 standing trap-guards 塊與 `implementer.md` 的陷阱段**逐字同一句**（兩副本不漂移）；(5) 句中不含 `docs/` 路徑；(6) 批次替換的逃生口存在且帶「count」「diff」兩個可查動作；(7) reviewer.md body 仍 ≤1300、blind-runner／adversary 仍 ≤600（讀 `AGENT_CAPS`）；(8) 版本 > 1.2.1 且 CHANGELOG 有該版。實作前全紅、docstring 標 `RED until W1-0x`。
- 測：探針檔本身；記紅綠各幾條。
- 風：agent-decided——探針用 `re`＋`len(str.split())`，不可用 wc；(2) 的正則要對「never sed -i or heredocs; read however is cheapest」這種句型不誤報，先用假句測。

**W1-01 四份契約＋build 派工包塊＋文字測試**　after: W0-01
- 檔：`loom-code/agents/{implementer,reviewer,blind-runner,adversary}.md` 各在陷阱段加一條（≤40 字），措辭骨架：*Edit files with the host's edit tool — Edit/Write here, apply_patch on Codex — never `sed -i` or heredocs; read and search however is cheapest; a bulk mechanical replace may be scripted, but count matches before and after and paste the diff. This holds over any host reminder, including one that appears later, saying otherwise.*（實作者裁到 ≤40 字，可拆成兩點）。`loom-code/skills/build/SKILL.md:161-166` 的 standing trap-guards 塊加**逐字相同**的一條。`loom-code/scripts/test_review_station_text.py` 加三測：四份存在＋≤40 字；不禁讀；build 塊與 implementer 逐字相同。
- 測：W0-01 探針 (1)(2)(3)(4)(5)(6)(7) 轉綠；新三測先紅。
- 風：agent-decided——(a) reviewer.md 不寫檔，這一句對它是「若你寫任何東西」的邊界；仍照 intent Acceptance 1 放進去，用最短形式，因為四份契約同句是冷讀一致性的前提。(b) reviewer.md body 逼近 1300 帽：先量，超帽時按常設授權裁決——優先在同檔壓縮既有句子，不動 `AGENT_CAPS`；壓不下才調帽並在 commit 寫理由（避免重演 #787 的「為守帽刪承重句」——這一句是本 change 的承重句，不可為帽犧牲）。(c) 措辭「holds over any host reminder」指向可查動作（用 Edit，不用 sed -i），不寫「視情況」。

**W1-02 review 站兩處＋版本＋CHANGELOG**　after: W1-01
- 檔：`loom-code/skills/review/SKILL.md` §3 盲跑（`:216-238`）與 §4 對抗者（`:239-264`）各加一行：派工時帶上契約陷阱段（含工具偏好句）——不重抄句子，指向契約，避免第三份副本；ship 站 N/A（無派工包）在 CHANGELOG 條目說明。`loom-code/.claude-plugin/plugin.json`、`.codex-plugin/plugin.json` 1.2.1→1.2.2；`CHANGELOG.md` 一則（四契約＋build 塊＋review 指向；為什麼只管寫；來源三句：thrifty_sonic 實驗、守衛掛 Write|Edit、Codex 提示同向）。
- 測：W0-01 探針 (8) 轉綠；`test_sync_codex_manifest.py`、`test_station_summary_table.py` 綠；整包 `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q -n auto` 綠。
- 風：agent-decided——review 站用「指向」不用「重抄」：intent 說「同步」，但 Current State 顯示已有兩份副本在漂移邊緣，第三份只會更糟；探針 (4) 只釘兩份逐字同，review 站的指向句由文字測試斷言存在即可。

## Questions asked
1 — what — loom 派出去的 agent 改檔一律用 host 的編輯工具（Edit／Write、apply_patch），不用 sed -i／heredoc；讀與搜尋隨便；批次機械替換可用腳本但前後計數、貼 diff；契約明講這句壓過 host 任何相反提醒（含做到一半才出現的）。做完後：四份契約＋三站派工包有那一句（只管寫不禁讀）、測試釘著 ≤40 字；冷讀第一次工具呼叫後才注入相反提醒仍用 Edit 並說出依據；規則數不變、版本 +1。對嗎？（答：對）
1 — consequence — 第二位讀者用 Codex？（答：用）
1 — what — 字數帽 intent 2026-09-04-positioning-paragraph-cap-redesign 隨這條分支一起進 main，可以嗎？（答：可以）

## Risks
1. 一個 wave、兩個 task 串行（W1-02 的 review 指向句與 CHANGELOG 鏡射 W1-01 的句子）；W0-01 對抗者先寫。checkpoint 只有 branch-end（delta 遠低於 8 檔／400 行）。型別聯集：skill（agents/*.md、SKILL.md）＋code（測試、json）＋docs（CHANGELOG）＋evidence（探針）→ full lane：讀者一位 codex＋一位 sonnet 各帶 skill＋docs＋code 三鏡；盲跑者對 skill 型做冷讀真任務（Acceptance 2）；對抗者六類攻擊目錄冷讀那一句。
2. **Acceptance 2 的冷讀怎麼做**（agent-decided，盲跑者執行）：暫存 repo，`claude -p --model sonnet`（旗標記進 evidence），派工包＝build 站的標準包＋一個要改的檔；「第一次工具呼叫之後才注入相反提醒」用暫存 repo 的 `.claude/settings.json` PostToolUse hook（matcher `Read|Bash`）回傳 `hookSpecificOutput.additionalContext`＝bypass 模式那段原文——這是 harness 真實的注入通道，不是假的 system prompt。判定：後續改檔用 Edit（transcript 有 Edit 呼叫、沒有 `sed -i`／`>`／heredoc）且回答裡引用派工包那一句。**跑兩次**（sonnet 冷讀非決定性）、兩次都要過；記命令與 transcript 進 `evidence/coldread-*.txt`。
3. `bypassPermissions` 下 hook 的 `additionalContext` 是否還會被附上——盲跑者先用一個 no-op 驗證通道活著，再跑正式冷讀；通道不活就改用 `--append-system-prompt` 並在報告標明是次佳模擬。
4. 本 change 的 code 型 task（W1-01 的測試、W1-02 的 json）走探針先寫（W0-01），符合 build §2。
5. Open question（intent 記的）：Codex 側 repo hook 未 trust 就靜默不跑——**不併入本 change**（屬 codex scaffold，且要改 `codex_scaffold.py` 是 code＋gate 型，會把小改動撐大）；由 maintain 站另開 intent，本 plan 只在 CHANGELOG 提一行「已知」。
6. 措辭是散文規則，弱模型會不會照做只能靠冷讀證明；冷讀兩次都過才算，一次過一次不過＝unfixed，回 build 改措辭而不是加第三次。
