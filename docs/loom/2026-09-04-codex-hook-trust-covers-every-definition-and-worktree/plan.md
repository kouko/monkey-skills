# Codex hook 信任逐條、逐 worktree 驗證 — plan
intent: 2026-09-04-codex-hook-trust-covers-every-definition-and-worktree@34683950

## Current State Evidence
- Forward（探針只驗一條）：`loom-code/scripts/codex_scaffold.py:93` `MARKER = .codex/hooks/.loom-hook-fired`（零位元組檔）；`:116-132` `SHIM_TEMPLATE` 只有 loom-checker 這條 shim 會 `: > .loom-hook-fired`（`LOOM_SELF_TEST` 設定時不寫）；`:300-311` `trusted()` 只看檔案存不存在，印一句總的 trusted／`NOT_TRUSTED_MESSAGE`（`:75-78`，不列定義、不印資料夾路徑）；`:106-113` `HOOKS_JSON` 只知道 PreToolUse Bash 這一條，`:152` `_merged_hooks_json` 把 repo 自己的其他定義原樣保留。
- Forward（第二組定義沒探針）：`.codex/hooks.json` 有 PreToolUse `Bash` → `.codex/hooks/loom-checker`，與 PostToolUse `Write|Edit` → `.codex/hooks/validate-skill-folder-structure.sh`、`.codex/hooks/remind-memory-mirror.sh`。這兩個 `.codex/` 副本是手抄的（`git log`：2908bedc 2026-06-17「Codex hook parity」、03d8312c、2ae644ec、4e25360c），沒有任何腳本產生它們、沒有測試比對它們：`validate-skill-folder-structure.sh` 副本程式碼與 `.claude/hooks/` 正本相同、只有註解漂移；`remind-memory-mirror.sh` 副本的提示文字已陳舊（副本 `:30-32` 仍指 `docs/loom/backlog/`，正本 `:58-59` 已改 intent）。兩個正本都先 `INPUT=$(cat)` 再用 jq 取 `tool_input.file_path`（`.claude/hooks/validate-skill-folder-structure.sh:27-31`、`remind-memory-mirror.sh:24-28`）。
- Forward（站文字）：`loom-code/skills/write-plan/references/codex-first-contact.md:53-83` §3 只講 `git push loom-trust-probe HEAD` 一條探針與 `/hooks` 的話；`write-plan/SKILL.md:118-132` step 0b 三步；`build/SKILL.md:37-43` §0 只說「檔案存在不代表 hook 會跑」、`:207-208` 說 Codex trust 是唯一的授權停點。文字測試 `test_write_plan_intake.py:185-187` 釘 SKILL.md 含 `/hooks`、`loom-trust-probe`。
- Reverse：`--trusted` 的呼叫者是 codex-first-contact §3 末段（人工查）與 `test_codex_scaffold.py:286-320,376-411`（marker 語意：shim 真跑會寫、self-test 不寫、外部寫入視為 fired）；`--self-test` 用 `PROBE_PAYLOAD`（`:135-141`，含 `hook_event_name`／`tool_name`／`tool_input`／`cwd`）餵 shim。`.gitignore:62` 忽略 marker。
- Data：Codex 的信任鍵含 `hooks.json` 絕對路徑（intent Problem；2026-09-04 在本 worktree 實測兩組定義都無信任紀錄）；Codex 把 `Write`／`Edit` 當 `apply_patch` 的 matcher 別名（openai/codex `hook_names.rs`，intent 引用）——PostToolUse 火痕裡的 `tool_name` 字串是什麼**未實測**，所以歸屬不能靠 matcher 比對 tool_name。
- Boundary：不改 `.codex/hooks.json` 任何 `command` 字串（改了信任失效）；不加 checker 規則（信任是機器本機事實）；火痕檔續放 `.codex/hooks/`、續 gitignore；探針不讀使用者家目錄下 Codex 的 config.toml；不動 Claude Code 側 hook；不讓 Codex 自動信任。契約散文不引用 `docs/` 路徑。

## 設計決定（agent-decided）
- **火痕檔從「存在與否」改成 ledger**：同一路徑 `.codex/hooks/.loom-hook-fired`，每次 hook 被執行追加一行 `<hook_event_name>\t<command>\t<tool_name>`（command＝該 hook 在 `hooks.json` 裡的相對路徑，腳本用 `$0` 相對 repo 算出）。零位元組的舊 marker 視為「PreToolUse Bash loom-checker fired（legacy）」，其餘定義 never——舊 clone 不會突然變成全 never 誤報，也不會被誤判成全 fired。
- **歸屬鍵＝(event, command)**，`tool_name` 只記錄不比對：因為 Codex 對 apply_patch 的 `tool_name` 字串未實測，靠 matcher fullmatch 會在別名上誤判成 never。同一 event 下同一 command 掛在兩個 matcher 的情況本 repo 沒有，`--trusted` 對這種定義印 `ambiguous`（不視為 fired）。
- **記錄器是一支共用腳本** `.codex/hooks/loom_record_fire.py`（由 scaffold 當 sibling 一起寫入）：stdin 讀 JSON、argv 收 `$0`，寫一行、永不 fatal、`LOOM_SELF_TEST` 設定時不寫。loom-checker shim 改成 `INPUT=$(cat)` → 記錄 → `printf '%s' "$INPUT" | exec python3 … push --hook`（stdin 只能讀一次）。
- **本 repo 的兩個 PostToolUse 副本改成薄殼**：`INPUT=$(cat)`、記錄、`printf '%s' "$INPUT" | exec .claude/hooks/<同名>.sh`——單一正本、漂移消失、exit code 原樣（`exec` 保留 2）。`hooks.json` 的 command 字串不動，所以既有信任不失效（信任綁定義不綁腳本內容，這正是 intent Proposed outcome 3 要文件明寫的事實）。薄殼是**本 repo** 的檔案，不由 loom-code 的 scaffold 產生；scaffold 只負責 loom 自己那條與記錄器；codex-first-contact 用一段說明「repo 自己的 hook 怎麼接記錄器」。
- **`--trusted` 逐條**：解析 `.codex/hooks.json` 全部定義，對每條印 `<event> <matcher> <command>: fired|never|ambiguous`；全 fired 才 exit 0；否則 stderr 印 `BLOCK: N of M Codex hook definitions have never fired in <abs repo path> — run /hooks in Codex in that folder once, then retry` 並列出 never 的定義鍵。self-test 不改語意（仍只證明副本能跑）。
- 不做：把 Claude Code 側 hook 也記火痕（沒信任閘，無此需求）；用 `~/.codex/config.toml` 反查（Constraints）。

## Task DAG

**W0-01 對抗者先寫探針**　after: —
- 檔：新增 `docs/loom/2026-09-04-codex-hook-trust-covers-every-definition-and-worktree/evidence/probes/test_abuse_hook_trust.py`（≥8 案例，用 `tmp_path` 暫存 repo＋`codex_scaffold.py --repo`，不碰真 Codex）。攻擊面：(1) hooks.json 三條定義（loom 的一條＋兩條 PostToolUse）→ `--trusted` 每條各一行、全 never 時 exit≠0、stderr 含 `/hooks` 與暫存 repo 的絕對路徑；(2) 腳本都存在、ledger 空 → 仍全 never（存在≠跑過）；(3) 以 PostToolUse payload 手動執行其中一條 hook → 只有那一條翻 fired，其餘 never；(4) `LOOM_SELF_TEST=1` 執行 shim → ledger 不變；(5) 零位元組舊 marker → 只有 loom-checker fired（legacy）；(6) 本 repo `.codex/hooks.json` 每個 `command` 字串與 `git show main:.codex/hooks.json` 逐位元相同；(7) `--list-rules` 行數與 main 相同；(8) 三份站文字（codex-first-contact §3、write-plan step 0b、build §0）各含「逐條／never／`/hooks`／停」的句子；(9) 本 repo 兩個 `.codex/hooks/*.sh` 薄殼對同一 PostToolUse payload 的 exit code 與 stdout/stderr 等於 `.claude/hooks/` 正本（薄殼多寫的 ledger 行除外）；(10) ledger 行格式：三欄 tab 分隔、command 為相對路徑、壞 JSON stdin 不 fatal；(11) plugin.json > 1.2.3 且 CHANGELOG 有該版。實作前 (1)(3)(5)(8)(9b)(10a)(11) 紅、(2)(4)(6)(7)(9a)(10b) 綠（守衛；(4) 現況已成立——`SHIM_TEMPLATE` 在 `LOOM_SELF_TEST` 下本來就不寫 marker，W0-01 實測後更正）；docstring 標 `RED until W1-0x`。
- 測：探針檔本身；記紅綠各幾條。
- 風：agent-decided——探針自己組 hooks.json 與 payload（用 `codex_scaffold.PROBE_PAYLOAD` 的形狀），不依賴 Codex 二進位；Codex 真跑的那一腿留給盲跑者。

**W1-01 記錄器＋shim 模板＋逐條 `--trusted`**　after: W0-01
- 檔：`loom-code/scripts/codex_scaffold.py`——新增 `loom_record_fire.py`（作為 `SIBLING_MODULES` 一起寫入 `.codex/hooks/`；內容也放在 `loom-code/scripts/loom_record_fire.py` 當來源）；`SHIM_TEMPLATE` 改成讀 stdin 一次、呼叫記錄器、再 pipe 給 checker；`trusted()` 改逐條（解析 hooks.json、ledger、legacy 空檔）；`NOT_TRUSTED_MESSAGE` 改成帶數量、絕對路徑、`/hooks`、never 清單；`--trusted` 的 docstring 與模組 docstring 同步。`loom-code/scripts/test_codex_scaffold.py`——既有 marker 測試改成 ledger 語意（`test_trusted_reports_whether_the_hook_ever_fired` 寫空檔＝legacy 仍 exit 0 但只對 loom 那條；`test_the_shim_leaves_a_marker_when_it_actually_runs` 斷言 ledger 有一行 `PreToolUse\t.codex/hooks/loom-checker\tBash`），新增逐條、legacy、ambiguous、壞 stdin 測試。
- 測：W0-01 探針 (1)(3)(4)(5)(10) 轉綠；新測試先紅。
- 風：agent-decided——記錄器用 Python 不用 jq（jq 在正本裡是可選依賴，記錄器不能因缺 jq 而不記）；ledger 追加用 `open(..., "a")`，不 lock（單機、單行、丟一行的後果只是 never 誤報一次，方向安全）。command 用 `os.path.relpath(argv[1], repo)`，repo＝ledger 所在 `.codex/hooks/` 的上兩層。

**W1-02 本 repo 的兩個 PostToolUse 副本改薄殼＋重跑 scaffold**　after: W1-01
- 檔：`.codex/hooks/validate-skill-folder-structure.sh`、`.codex/hooks/remind-memory-mirror.sh` 改成薄殼（讀 stdin 一次 → `python3 .codex/hooks/loom_record_fire.py "$0"` → `exec .claude/hooks/<同名>`）；`python3 loom-code/scripts/codex_scaffold.py --repo .` 重生 `.codex/hooks/loom-checker`、寫入 `loom_record_fire.py`（`hooks.json` 不變——scaffold 的 merge 保留既有定義，探針 (6) 守）；`.claude/hooks/test_*.py` 或 `loom-code/scripts/` 加一測：兩個薄殼對 `.claude/hooks/` 正本的等價（探針 (9) 的畢業版）。
- 測：W0-01 探針 (9) 轉綠、(6)(7) 留綠。
- 風：agent-decided——薄殼用 `exec` 而非 `source`，保住正本的 `set -e` 與 exit 2 語意；正本路徑寫相對（`.claude/hooks/…`），Codex 在 repo 根執行 hook（現有 `.codex/hooks/loom-checker` 也是相對路徑 `python3 .codex/hooks/loom_checker.py`，同一假設）。`.codex/hooks/` 是 gitignore 的 marker 所在但腳本本身有版控（現況如此）。

**W1-03 站文字＋文字測試**　after: W1-01
- 檔：`loom-code/skills/write-plan/references/codex-first-contact.md` §3 改成「先 `--trusted` 逐條，再 trust probe」並補一段：信任綁定義不綁腳本內容（改腳本不用重按，改 `hooks.json` 命令字串要重按）、綁絕對路徑（每個 worktree 各一次）、repo 自己的 hook 怎麼接記錄器（三行薄殼範例）；`write-plan/SKILL.md` step 0b 加一句：有任何一條 never 就列出定義鍵、要求在**這個資料夾**的 Codex 按 `/hooks`、停；`build/SKILL.md` §0 與派 Codex 腿（review 站 §2 second-vendor 段）前各加一句同樣的檢查。`test_write_plan_intake.py`（或 `test_station_summary_table.py` 旁的文字測試）斷言三處句子存在（探針 (8) 的畢業版）。
- 測：W0-01 探針 (8) 轉綠。
- 風：agent-decided——措辭指向可查動作（印出的定義鍵、資料夾路徑、`/hooks`），不寫「請確認 hooks 已啟用」（intent Proposed outcome 2）。write-plan SKILL.md body 已 4,077 詞（軟目標 3,750、硬帽 4,500）：SKILL 只加一句（≤30 詞），段落全放 codex-first-contact.md。

**W1-04 版本與 CHANGELOG**　after: W1-02, W1-03
- 檔：`loom-code/.claude-plugin/plugin.json` 1.2.3→1.2.4、`CHANGELOG.md` 一則（逐條信任探針、ledger、薄殼、站文字）；`.codex-plugin` 鏡射用 `sync_codex_manifests.py`；README 版本表；`.codex/hooks/loom-checker` 版本戳由 scaffold 重生。
- 測：W0-01 探針 (11) 轉綠；整包 `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q -n auto` 綠。
- 風：改 skill 內容必 bump。

## Questions asked
1 — what — 你要的是 Codex 的 hook 信任要每一條定義、每個 worktree 都驗過：探針涵蓋 `.codex/hooks.json` 裡每一條、逐條回報跑過／沒跑過，站在派 Codex 前看到任何一條沒跑過就列出來、請你在那個資料夾按一次 `/hooks` 並停；文件寫明信任綁定義與絕對路徑；不改命令字串。對嗎？（答：對）
1 — consequence — 這次要不要用 Codex 當第二位讀者？多花幾分鐘與額度（答：用）

## Risks
1. 全車道（`hooks/**` 是 gate 型、`codex_scaffold.py` 是 code、SKILL/reference 是 skill/docs）：W1-01／W1-02 探針先寫（W0-01）；一個 wave 四 task，W1-02 與 W1-03 可平行（各自 worktree、`--no-ff` 合回；不同檔案、W1-03 只需要 W1-01 定下的輸出格式），W1-04 最後。checkpoint 只有 branch-end（delta 預估 <8 檔／<400 行；若 codex_scaffold.py 改動超過 400 行則 wave-end 一次）。讀者 codex＋sonnet，帶 code＋skill＋docs 鏡。
2. 盲跑（Acceptance 1–2）：blind-runner 在暫存 repo 跑 scaffold → `--trusted` 全 never；再用 `codex exec --sandbox read-only` 各觸發一次 shell 與 apply_patch（不按 `/hooks`，預期 hook 不跑、ledger 不變、`--trusted` 仍全 never）；手動 pipe payload 執行一條 hook → 只那一條 fired。**Acceptance 之外、Constraints 明講的人工腿**：「按過 `/hooks` 之後守衛真的跑」要使用者在那個暫存資料夾的 Codex TUI 按一次——盲跑報告寫驗法（在該資料夾開 `codex`、輸入 `/hooks` 同意、再跑 `codex exec` 一次 shell 與一次 apply_patch、`--trusted` 全 fired），標「由使用者親手驗」。
3. Codex 對 apply_patch 的 PostToolUse `tool_name` 字串未實測——設計已避開（歸屬鍵不含 tool_name）；盲跑的 `codex exec` 腿若在使用者按 `/hooks` 後真跑，ledger 會把實際字串記下來，寫進報告當事實。
4. `.codex/hooks/` 同時裝版控腳本與 gitignore 的 ledger——薄殼 `exec` 正本時的 cwd 假設（repo 根）與現有 loom-checker shim 相同；若 Codex 換了 cwd，兩者一起壞，探針 (9) 在本機看不出來，只有盲跑的 `codex exec` 腿能看。
5. 舊 clone 的零位元組 marker：legacy 規則只讓 loom 那條算 fired，其他定義會顯示 never——這是**正確**的（它們確實從沒被證明跑過），站文字要說清楚「never 是沒證據，不是沒信任」（`codex_scaffold.py:41-44` 的原則）。
6. 同樹並行坑：branch-end 對抗者與盲跑者同時 commit——派工包寫「只路徑限定 commit、禁 amend」。
