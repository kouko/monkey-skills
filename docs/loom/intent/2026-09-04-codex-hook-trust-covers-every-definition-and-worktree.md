# Codex 的 hook 信任要逐條、逐 worktree 驗證：沒被同意的守衛會靜默不跑
originator: kouko
kind: engineering
needs-design: no — 改 codex scaffold 的探針與站文字；沒有使用者讀或輸入的介面
evidence: [docs/loom/intent/2026-09-04-prefer-harness-native-file-tools.md, docs/loom/2026-09-04-prefer-harness-native-file-tools/plan.md]
status: confirmed 2026-09-04

## Problem
Codex 對專案自帶的 hook 有一道安全閘：每一條 hook **定義**（`hooks.json` 路徑＋事件＋序號）要使用者在那個資料夾按過一次 `/hooks` 才會執行；沒同意的 **靜默跳過**，`codex exec` 不印任何警告（`loom-code/scripts/codex_scaffold.py:20` 已記錄）。信任綁在「定義」上，而且鍵值含 `hooks.json` 的**絕對路徑**（`~/.codex/config.toml` 的 `[hooks.state."<path>:<event>:<i>:<j>"]`），所以每開一個新 worktree 就全部歸零。現有的探針只驗一條：`write-plan` step 0b 用 `git push loom-trust-probe HEAD` 試 PreToolUse 的 `loom-checker`，`codex_scaffold.py --trusted` 也只讀那條 shim 寫的 `.codex/hooks/.loom-hook-fired`。`.codex/hooks.json` 還有第二組定義——PostToolUse `Write|Edit` 上的 `validate-skill-folder-structure.sh` 與 `remind-memory-mirror.sh`（Codex 把 `Write`／`Edit` 當成 `apply_patch` 的 matcher 別名，所以這組在 Codex 上是活的守衛）——**沒有任何探針**。2026-09-04 在 `simple-loom-flow` worktree 實測：`config.toml` 的 `hooks.state` 只有全域 dcg 與 code-toolkit 的 SessionStart，本 repo 的兩組定義都沒有信任紀錄；Codex 在這裡改 skill 資料夾或 memory store，結構檢查與索引檢查一個都不會跑，也沒有人知道。第一組（push 閘）至少有站在問；第二組是完全的盲區。

## Proposed outcome
1. 探針涵蓋 `.codex/hooks.json` 裡**每一條**定義，不只 loom-checker：每個 hook 腳本（或一個共用的記錄 shim）在被執行時記下「哪條定義、哪個事件、哪個工具名」到同一個火痕檔；`codex_scaffold.py --trusted` 逐條回報 fired／never，而不是一個總的 yes/no。
2. `write-plan` step 0b 的首次接觸與 `build` 站派 Codex 腿之前，讀逐條結果：有任何一條 never 就印出「哪幾條沒被信任、請在這個資料夾的 Codex 裡按一次 `/hooks`」並停，不當成一切正常。措辭指向可查動作（列出定義鍵），不寫「請確認 hooks 已啟用」。
3. 文件明寫兩件事實：信任綁定義不綁腳本內容（改腳本不用重按，改 `hooks.json` 命令字串要重按）；信任綁絕對路徑，每個 worktree 各自一次。
4. 不改 `hooks.json` 的命令字串（改了現有信任就失效）；火痕檔的寫入不能成為信任的替身——它只回答「有沒有跑過」，不回答「Codex 信不信」（`codex_scaffold.py:41-44` 的原則保留）。

## Acceptance
1. `python3 loom-code/scripts/codex_scaffold.py --repo <repo> --trusted` 對 `.codex/hooks.json` 的每一條定義各印一行 `<event> <matcher> <command>: fired|never`；在一個乾淨的暫存 repo 跑 scaffold 後、沒按過 `/hooks` 時，全部是 never，exit 非 0，且輸出含「/hooks」與那個資料夾的路徑。
2. 在同一個暫存 repo 用 `codex exec` 各觸發一次 shell 與 apply_patch（不需人按 `/hooks`，預期兩組都不跑）：`--trusted` 仍全 never——證明探針不會被「腳本存在」或「Codex 跑過」誤判成 fired；反向：手動執行任一 hook 腳本一次後，只有那一條翻成 fired。
3. `write-plan` step 0b 的文字與 `build` 站派 Codex 腿的文字各有一句：逐條檢查、列出 never 的定義、要求 `/hooks`、停；文字測試斷言存在。
4. `.codex/hooks.json` 的每個 `command` 字串與 main 上逐位元相同（現有信任不失效）；`--list-rules` 規則數不變；整包測試綠；loom-code 版本 bump（patch）。

## Constraints
- 不加 checker 規則：信任狀態是機器本機的事實，不能從 git 重算。
- 火痕檔繼續放 `.codex/hooks/`、繼續 gitignore；探針只讀它，不讀 `~/.codex/config.toml`（那是使用者的私人設定，格式也沒承諾穩定）。
- 「按過 `/hooks` 之後守衛真的跑」這一腿需要人按同意，盲跑無法自動化；盲跑報告要明講這一腿由使用者親手驗、附驗法。

## Out of scope
- Claude Code 側的 hook（設定在 `.claude/settings.json`，沒有信任閘）。
- 讓 Codex 自動信任（那是 Codex 的安全設計，不繞）。
- `.codex/hooks.json` 裡要不要多掛別的守衛。

## Open questions
- none
