# Codex 的 hook 信任要逐條、逐 worktree 驗證 — 我試了什麼、發生了什麼

2026-09-04 在乾淨的工作樹上試的（新開的 git worktree，checkout 到審查用的
commit `6eafb085`）。

## 你要的東西，一條一條核對

### 1. `--trusted` 對每一條 hook 定義各印一行 fired／never；乾淨暫存 repo 沒按過 `/hooks` 時全部是 never，exit 非 0，輸出含「/hooks」與那個資料夾的路徑

- **我怎麼試的**：另外開一個全新的暫存 git repo（`mktemp -d`、`git init`、一個 commit），跑
  `python3 <乾淨工作樹>/loom-code/scripts/codex_scaffold.py --repo <暫存 repo>` 把 loom 的檢查裝進去，再手動把這個 repo 現有的第二組定義（`PostToolUse Write|Edit` 上的兩支腳本）也複製進暫存 repo 的 `.codex/hooks.json`，然後跑一次
  `--trusted`。
- **發生了什麼**：印出三行，每條定義各一行，全部是 `never`：
  ```
  BLOCK: 3 of 3 Codex hook definitions have never fired in <暫存資料夾絕對路徑> — run /hooks in Codex in that folder once, then retry
  PreToolUse Bash .codex/hooks/loom-checker
  PostToolUse Write|Edit .codex/hooks/validate-skill-folder-structure.sh
  PostToolUse Write|Edit .codex/hooks/remind-memory-mirror.sh
  PreToolUse Bash .codex/hooks/loom-checker: never
  PostToolUse Write|Edit .codex/hooks/validate-skill-folder-structure.sh: never
  PostToolUse Write|Edit .codex/hooks/remind-memory-mirror.sh: never
  ```
  exit code 是 2（非 0），輸出裡有「/hooks」也有那個暫存資料夾的完整絕對路徑。三條全對，跟你要的一致。
- **證據**：`evidence/blind-run-acc1-trusted-before.txt`（完整輸出＋exit code）。
- **驗證**：works

### 2. 用 `codex exec` 各觸發一次 shell 與 apply_patch（不按 `/hooks`）——hook 不該跑；反向：手動餵一條 hook 的訊息，只有那一條翻成 fired

- **我怎麼試的**：在同一個暫存 repo 裡，先跑
  `codex exec --sandbox read-only "run: echo probe"`，再跑
  `codex exec --sandbox workspace-write "create a file named hello.txt containing hi"`（兩次都關掉互動輸入）；每次跑完檢查火痕檔（ledger）在不在、`--trusted` 有沒有變化。最後手動組一則 `PostToolUse` 的訊息（模擬 Codex 真的呼叫這支 hook 時會傳的內容），直接餵給其中一支 hook 腳本（`validate-skill-folder-structure.sh`），再看 `--trusted` 是不是只有那一條翻過來。
- **發生了什麼**：
  - `echo probe` 真的印出 `probe`（read-only 模式允許跑指令），但整個過程沒有出現我們的火痕檔（`.codex/hooks/.loom-hook-fired` 不存在）——這條 PreToolUse 定義沒被觸發。
  - 建立 `hello.txt` 也真的成功了（workspace-write 模式允許改檔案，檔案內容是 `hi`），但火痕檔一樣不存在——PostToolUse 那兩條定義也沒被觸發。
  - 這兩次之後再跑一次 `--trusted`，結果跟第一次一模一樣：三條全部還是 `never`（同一份三行輸出、exit 2）。這證明探針不會被「Codex 真的執行了這個資料夾裡的指令」誤判成信任已生效——因為這個資料夾從沒被按過 `/hooks`，Codex 就是把我們的 hook 靜靜跳過，連警告都不印。
  - 接著我手動把訊息餵給 `validate-skill-folder-structure.sh` 這一支腳本，再跑 `--trusted`：這次只有這一條翻成 `fired`，另外兩條（`loom-checker`、`remind-memory-mirror.sh`）仍然是 `never`。火痕檔裡也真的只多了一行，正是這一條定義的紀錄。
- **證據**：
  ```
  $ codex exec --sandbox read-only "run: echo probe"
  … exec /bin/zsh -lc 'echo probe' … succeeded … → probe
  （ledger 檔不存在）

  $ codex exec --sandbox workspace-write "create a file named hello.txt containing hi"
  … apply patch … patch: completed … hello.txt 已建立，內容 hi
  （ledger 檔仍不存在）

  $ codex_scaffold.py --trusted   # 兩次 codex exec 之後
  BLOCK: 3 of 3 … never / never / never   （跟之前一模一樣）

  # 手動餵訊息給其中一支 hook 之後：
  $ cat .codex/hooks/.loom-hook-fired
  PostToolUse    .codex/hooks/validate-skill-folder-structure.sh    Write

  $ codex_scaffold.py --trusted
  BLOCK: 2 of 3 …
  PreToolUse Bash .codex/hooks/loom-checker: never
  PostToolUse Write|Edit .codex/hooks/validate-skill-folder-structure.sh: fired
  PostToolUse Write|Edit .codex/hooks/remind-memory-mirror.sh: never
  ```
  完整原始輸出見 `evidence/blind-run-acc2-codex-exec-readonly.txt`、
  `evidence/blind-run-acc2-codex-exec-workspacewrite.txt`、
  `evidence/blind-run-acc2-trusted-after-codexexec.txt`、
  `evidence/blind-run-acc2-manual-shim-fire.txt`、
  `evidence/blind-run-acc2-trusted-after-manual-fire.txt`、
  `evidence/blind-run-acc2-ledger-snapshot.txt`。
- **驗證**：works

### 3. `write-plan` step 0b 與 `build` 站派 Codex 腿的文字各有一句：逐條檢查、列出 never 的定義、要求 `/hooks`、停；文字測試存在且通過

- **我怎麼試的**：打開 `write-plan/SKILL.md` 的 step 0b、`build/SKILL.md` 派 Codex 腿之前的段落、還有 `codex-first-contact.md` 的第 3 節，逐字讀；再跑
  `python3 -m pytest loom-code/scripts/test_codex_trust_station_text.py -q`。
- **發生了什麼**：三處都各有一句符合要求的話：
  - `write-plan/SKILL.md` step 0b 第 3 點：「Run `--trusted`; any definition reading `never` means print the BLOCK lines, ask for `/hooks` in Codex for this folder, and **stop**.」
  - `build/SKILL.md`（派 Codex 腿之前）：「Before dispatching a Codex leg, run `--trusted` yourself: any definition reading `never` means print the BLOCK lines, ask for `/hooks` in that folder, and **stop**.」
  - `codex-first-contact.md` 第 3 節整段都在講怎麼讀 `--trusted` 的逐條輸出、怎麼再用 `git push loom-trust-probe HEAD` 真的驗一次、沒信任時要印哪段話（含資料夾絕對路徑）並停下。
  文字測試 `test_codex_trust_station_text.py` 跑起來 6 個全過。
- **證據**：上面三段引文（逐字抄自檔案本身）；`python3 -m pytest loom-code/scripts/test_codex_trust_station_text.py -q` → `6 passed in 0.11s`。
- **驗證**：works

### 4. `.codex/hooks.json` 每個 `command` 字串跟 main 上逐位元相同；`--list-rules` 規則數不變；整包測試綠；版本 bump

- **我怎麼試的**：`git diff main -- .codex/hooks.json`；分別在這個分支的乾淨工作樹跟另一份 main checkout 各跑一次
  `loom_checker.py --list-rules | wc -l`；在乾淨工作樹跑整包測試指令；看 `plugin.json` 版本號跟 `CHANGELOG.md`。
- **發生了什麼**：`git diff main -- .codex/hooks.json` 完全沒輸出（0 位元組），代表這個檔案的內容跟 main 上逐位元相同，之前已經按過的信任不會失效。`--list-rules` 這個分支跟 main 都是 **27 行**，數字一樣。整包測試指令跑出 **1289 通過、1 個預期內失敗（xfail）、0 個真失敗**。`plugin.json` 版本是 `1.2.4`，`CHANGELOG.md` 有對應的 `[1.2.4]` 條目，內容就是這次改的逐條信任、ledger、薄殼、站文字。
- **證據**：
  ```
  $ git diff main -- .codex/hooks.json
  （空，代表沒有差異）

  $ python3 loom-code/scripts/loom_checker.py --list-rules | wc -l   # 這個分支
  27
  $ python3 /Users/kouko/GitHub/monkey-skills/loom-code/scripts/loom_checker.py --list-rules | wc -l   # main
  27

  $ python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q -n auto
  1289 passed, 1 xfailed in 40.94s

  $ grep '"version"' loom-code/.claude-plugin/plugin.json
  "version": "1.2.4",
  ```
  完整輸出見 `evidence/blind-run-acc4-hooksjson-diff.txt`（空檔）、
  `evidence/blind-run-acc4-pytest.txt`。
- **驗證**：works

## Constraints 裡明講的那一腿——按過 `/hooks` 之後守衛真的跑

這一段我沒辦法自己驗，因為要在 Codex 的互動介面裡按一次同意，只有你能做：

1. 打開終端機，`cd` 到這個暫存資料夾（我這次測試留著沒刪，路徑見下方）。
2. 在那個資料夾裡開 `codex`（互動模式，不是 `codex exec`）。
3. 輸入 `/hooks`，把跳出來的授權請求按同意。
4. 同意之後，離開或另開一個終端機，在同一個資料夾裡跑第 2 條測過的那兩個指令：
   `codex exec --sandbox read-only "run: echo probe"`、
   `codex exec --sandbox workspace-write "create a file named hello.txt containing hi"`。
5. 最後跑
   `python3 <乾淨工作樹>/loom-code/scripts/codex_scaffold.py --repo <暫存資料夾> --trusted`。

**預期結果**：三條全部變成 `fired`，exit code 是 0。這時候火痕檔裡會多出真正由 Codex 執行 apply_patch 時記下來的 `tool_name` 字串——這個字串到今天為止還沒有人實際看過（plan 裡明講「未實測」），這次盲跑也沒能補上，等你按過 `/hooks` 真跑一次才會知道答案。

由使用者親手驗。暫存資料夾：
`/private/tmp/claude-501/-Users-kouko--herdr-worktrees-monkey-skills-simple-loom-flow/9394655d-4917-441f-af10-33c73e42aab6/scratchpad/scratch-repo-JWQz`
（沒有刪除；裡面已經有一個手動翻成 `fired` 的定義，跟按 `/hooks` 前的三條全 `never` 狀態混在一起——如果你想要一個乾淨的三條全 never 的暫存資料夾再測，跟我說一聲我可以另外開一個）。

## 對你既有的資料做了什麼

沒有——這次改動只碰了探針腳本（`codex_scaffold.py`）、一支新的共用記錄器
（`loom_record_fire.py`）、本 repo 自己那兩支 `.codex/hooks/` 副本改成薄殼、三處站文字、還有版本號跟 CHANGELOG。所有測試都在全新的暫存資料夾裡跑，沒有讀寫任何你原本就有的 change 記錄或設定；`.codex/hooks.json` 的內容逐位元沒變，你原本按過的信任照樣有效。

## 我幫你決定的事

- **火痕檔從「存不存在」改成一行一行的紀錄檔（ledger），不是重新設計成別的東西**——舊版只要那個檔案存在就當作「信任生效」，這次改成每次真的被呼叫就追加一行 `事件\t定義\t工具名`。這個決定不是我這次盲跑做的（是 plan 站定的），但盲跑親自驗過：手動觸發一條 hook 後，確實只有那一條的紀錄被加進去，其他還是空的，沒有被誤判。
- **舊的零位元組 marker 檔案，只算是 loom 自己那條 PreToolUse 定義「(legacy) 已跑過」，不算別的定義都跑過**——這代表如果你之前用過舊版探針、只留下一個空檔案，升級後你的 PostToolUse 那兩條定義（結構檢查、記憶提醒）還是會被回報成 `never`，不會因為舊檔案存在就被誤判成安全。這個規則的方向是「寧可多問一次 `/hooks`，也不要漏掉真的沒驗過的守衛」。
- **判斷「哪一條定義被觸發」用「事件＋指令路徑」這組鍵，不看 Codex 回報的工具名稱字串**——因為 Codex 對 apply_patch 這個動作在 PostToolUse 裡到底填什麼工具名稱，到今天都沒人實際驗過。這次盲跑也還是沒能補上這個事實（見上面「由使用者親手驗」那一段），這是刻意選擇「先用查得到的鍵，不用查不到的鍵」的結果。
- **本 repo 自己的兩支 `.codex/hooks/` 副本改成三行的薄殼腳本，指令字串本身完全沒動**——目的是讓既有的信任不失效（Codex 把信任綁在 `hooks.json` 裡的指令字串上，改字串就要重按 `/hooks`）。我讀過薄殼與原本的 `.claude/hooks/` 正本，兩邊邏輯一致，薄殼只是多讀一次 stdin、多寫一行記錄，再原封不動把輸入轉給正本執行。

## 你可能還沒想到的事

- **Codex 對 apply_patch 在 PostToolUse 裡回報的 `tool_name` 到底是什麼字串，這次盲跑仍然沒有答案**——這是 intent 跟 plan 都提前寫明的已知缺口（設計上刻意繞開，不靠這個字串判斷），要等你親手按過 `/hooks`、真的跑一次 `codex exec` 之後，火痕檔裡才會第一次出現這個真實字串。
- **我留下的那個暫存資料夾，狀態已經不是「三條全 never」的乾淨起點**——因為我在第 2 條驗收裡手動觸發過一次 hook，裡面已經有一行紀錄。如果你想照上面的步驟從頭驗「按過 `/hooks` 之後全部變 fired」，用這個資料夾也可以（反正只會讓已經是 `fired` 的那條繼續是 `fired`），但如果你想要一個「起點乾乾淨淨、什麼都沒發生過」的資料夾，要另外請我開一個。
- **這次改動涉及的兩個 codex exec 呼叫，用的模型是 `gpt-5.6-sol`、approval 設定是 `never`**——這是我這台機器目前的 Codex 設定，不是這次改動指定或需要的行為；如果你自己的 Codex 設定不同（例如互動式核准開著），實際跑起來的畫面可能會多幾個確認步驟，但不影響信任閘本身有沒有生效。
