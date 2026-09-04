# loom 契約敘述對檔案寫入的工具偏好：寫用 host 編輯工具，讀與搜尋隨便，批次替換用腳本但要驗
originator: kouko
kind: engineering
needs-design: no — 只改 agent 契約與站 SKILL.md 的派工包文字；沒有使用者讀或輸入的介面
evidence: [docs/loom/2026-09-04-reviewer-and-adversary-positioning/review.json]
status: confirmed 2026-09-04

## Problem
loom 的契約對「怎麼讀寫檔案」沒有立場：派工包只說「Read a file before you Edit it」，其餘交給 host 預設。2026-09-04 實測（Claude Code 2.1.260，`settings.json` 的 `defaultMode: bypassPermissions`）：harness 在**bypass permissions 模式**下會附一條 reminder——原文「While bypass permissions mode is active: Do your work through the Bash tool wherever it can accomplish the job: read files with cat, head, or sed -n … make file changes with sed, heredocs, or short scripts, rather than using the dedicated Read, Edit, or Write tools」——orchestrator 於是改用 `sed -i`／heredoc 改檔。三個查證過的事實決定契約要怎麼寫：(1) 這條提醒**沒有任何官方文件**——哪一版加的、理由、能不能關都沒寫（GitHub anthropics/claude-code #50331 回報 auto mode 也注入未公開的行為提醒，提議做成可設定，未實作）；(2) 它與系統提示自己的預設**相反**（#39979：系統提示寫「有 Read／Edit／Glob／Grep 時不用 Bash」），所以契約明寫「派工包的句子壓過 host 提醒」不是跟 host 唱反調，是把 host 自己前後不一的地方釘住；(3) **subagent 也收得到**，但不是在啟動時——探針 agent 實測：啟動 context 裡沒有這句，第一次工具呼叫的結果旁才出現，所以 agent 第一次讀檔會自然選 Read，之後才被推向 Bash。契約那句話因此必須寫成「之後任何時候出現的相反提醒都不算數」，不能只寫「優先用 Read／Edit」。這條偏好不在 repo 任何檔案裡，只在 harness 側，卻直接改變 loom 流程裡的操作方式；kouko 看到後要求改回內建工具。再查兩層之後的來源：(4) 那句話編在 Claude Code 2.1.260 執行檔裡，內部旗標 `tengu_thrifty_sonic`、變數 `bashFirst`／`bashFirstSessionAssignment`——是**按 session 抽籤分組的省 token 實驗**（forced／cohort／none），有嚴格與寬鬆兩種文案，寬鬆版自己寫「精確或多行替換、GNU/BSD sed 旗標差異這類脆弱改動，優先用 Edit/Write」；bypass 與 auto 兩種模式都會注入，只是標題不同。實驗會換組、會改文案、會消失，契約不該跟著它漂。(5) **兩個 host 的品質守衛都掛在 `Write|Edit`**：本 repo `.claude/settings.json` 與 `.codex/hooks.json` 的 PostToolUse（skill 資料夾結構、memory store 完整性、codex manifest 漂移）都只在 Write／Edit 之後跑；Codex 明寫 `Write`／`Edit` 是 `apply_patch` 的 matcher 別名（openai/codex `codex-rs/core/src/tools/hook_names.rs`），所以在兩個 host 用 shell 改檔＝**繞過 repo 自己設的守衛**。(6) Codex 自己的系統提示（`gpt_5_codex_prompt.md`）已是「單檔編輯用 apply_patch；自動產生的檔案或跨 codebase 搜尋替換這種用腳本更有效率的不用」——跟本 intent 的分法同向；Claude Code 的 bypass 實驗是唯一反向的來源。代價是可觀察的：`sed -i` 沒命中會靜默成功（macOS BSD sed 少一個 `''` 就 no-op）；heredoc 含敏感字樣（如刪遠端分支的指令字串）會被 bash-guard 擋下；Edit 工具逼先讀、精確比對、沒命中就報錯，Write 對長檔更可靠；apply_patch 對不上 context 也報錯。研究面（SWE-agent 2024：同模型下專用編輯介面比純 shell 相對高 64%；Anthropic 自己的 SWE-bench agent 只給 Bash＋str_replace_editor；OpenAI 為此自創 V4A 格式）支持「寫」用專用工具，沒有來源反對用 shell「讀」。

## Proposed outcome
1. `loom-code/agents/*.md` 的 Traps／standing trap-guards 與各站 SKILL.md 的派工包標準句，加一句工具偏好，**只管寫**：改檔用 host 的編輯工具（Claude Code：Edit／Write；Codex：apply_patch），不用 `sed -i`／heredoc；讀與搜尋用哪個都行（Bash 讀還便宜）；批次機械替換可用腳本，但要 grep 前後計數並貼出 diff。理由一句（靜默沒命中 vs 報錯；repo 的守衛掛在 Write|Edit）。這跟 Codex 自己的提示同向，跟 Claude Code 寬鬆版文案不衝突——弱模型讀到的是一條不打架的規則。
2. 明寫這條「壓過 host 的相反 reminder」：host 在 bypass permissions 之類模式下附的工具偏好是預設值——**包括任務進行中才出現在工具結果旁的那種**——loom 派工包裡的句子是契約，契約優先。
3. 不加規則、不動 checker——工具選擇無法從 git 紀錄重算，只能是散文；措辭要指向可查動作（「用 Edit，不用 sed -i」）不要判斷（「視情況」）。

## Acceptance
1. 四份 agent 契約（implementer／reviewer／blind-runner／adversary）的 trap 段各有那一句；build／review／ship 站的派工包標準句同步；一個文字測試斷言存在且字數帽內；那一句只規定寫、不禁讀（測試斷言句中沒有把 `cat`／`grep`／Read 列為禁止）。
2. 冷讀盲跑：給一個 agent 派工包，在它第一次工具呼叫**之後**才注入一條相反的 host reminder（「優先用 Bash」，模擬實測的出現時機），它後續改檔仍用 Edit 不用 `sed -i`，並能說出依據是派工包哪一句。
3. `--list-rules` 規則數不變；loom-code 版本 bump（patch）。

## Constraints
- 純散文，≤40 英文字每處；不重述各 host 的工具清單，只點名讀寫用的那幾個。
- 不引用本 repo `docs/` 下的紀錄（可攜性規則）。

## Out of scope
- 其他 host 行為的對抗（如 auto mode 本身要不要開）；orchestrator 自身（非 subagent）的工具選擇由 CLAUDE.md／使用者當場決定，不進契約。

## Open questions
- Codex 側本 repo 的 `.codex/hooks.json` 在新 worktree 沒有 trust 紀錄時，PostToolUse 守衛靜默不跑（2026-09-04 在 simple-loom-flow worktree 實測：`config.toml` `hooks.state` 只有全域 dcg 與 code-toolkit SessionStart）。要不要讓 codex scaffold 在寫入後驗 trust 狀態並提示 `/hooks`？屬 codex scaffold 的事，可能另開 intent；plan 站決定。
