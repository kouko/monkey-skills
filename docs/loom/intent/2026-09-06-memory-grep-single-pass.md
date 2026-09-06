# memory-grep.sh 撈記憶只走一趟 git：逐 commit 開子行程換成單次 git log，本 repo 20 秒降到 1 秒內，輸出逐位元不變
originator: kouko
kind: engineering
needs-design: no — 只改一支 shell 腳本的內部實作與它的測試；命令列參數、輸出格式、exit code 一個都不動；沒有使用者讀或輸入的介面改變
evidence: [loom-workflow/tests/test-memory-grep-match.sh, loom-workflow/tests/test-memory-grep-supersedes.sh, loom-workflow/tests/test-memory-grep-verify.sh]
status: confirmed 2026-09-06

## Problem
`loom-workflow/skills/git-memory/scripts/memory-grep.sh` 是 git-memory skill 的取回工具：把 commit 的 `Decision:`／`Learning:`／`Gotcha:`／`Related:` 尾標和 merged PR 的 `## Memory` 段撈成一份摘要，寫 commit 訊息前、找過去決策時都靠它。它在本 repo 跑預設模式要 20 秒（2026-09-06 量測：近三個月 395 個非 merge commit，其中 63 個帶記憶尾標；`--no-pr` 19.9 秒，system time 17 秒）。`--verify-merged` 只查一個 commit，0.06 秒，不慢。

慢的原因是三個逐 commit 的迴圈：抽取迴圈對 395 個 commit 每個開 `git log -1`、`git interpret-trailers`、`grep` 三個子行程；supersession 索引為了算「哪條記錄被後來的 `Supersedes:` 取代」把同樣 395 個 commit **再掃一遍**；輸出時每筆記錄再用 `printf | jq` 逐欄取值（plain 格式每筆約 8 次）。合計約 3,000 次子行程，macOS 上每次 5 到 15 毫秒，隨 commit 數線性變慢。同樣的尾標掃描交給 git 一次做完（`git log --format='%(trailers:key=…)'`）只要 0.03 秒。

## Proposed outcome
1. **抽取與 supersession 索引合成一趟 `git log`**：用 `%(trailers:key=Decision,key=Learning,key=Gotcha,key=Related,key=Supersedes,unfold)` 讓 git 在同一次呼叫裡把每個 commit 的 sha、日期、主旨和篩過的尾標一起吐出來，用 git 自己不會出現在訊息裡的分隔符（`%x1E`／`%x1F`）切段，再交給**一次** `jq` 建出全部記錄與 supersession 表。腳本開頭選 git 原生 parser 避免分隔符撞車的理由保留：`%(trailers:…)` 與 `interpret-trailers --parse --unfold` 是同一個 parser。
2. **輸出階段不再逐欄開 `jq`**：plain 與 json 都從那一份 jq 結果一次渲染。
3. **看得見的行為零改變**：參數、預設值、`--match`／`--path`／`--top`／`--history` 語意、plain 與 json 的每一個位元組、五種 exit code、`--verify`／`--verify-merged`／`--verify-strict` 三個模式，全部照舊。這是效能修，不是功能修。
4. **既有五份 shell 測試不動一字**、全綠；新增一份計時與等價測試。
5. loom-workflow 版本 bump，CHANGELOG 記量測數字（前／後）。

## Acceptance
1. 在本 repo，`time bash loom-workflow/skills/git-memory/scripts/memory-grep.sh --no-pr` 在 2 秒內結束（改前 19.9 秒），`--no-pr --history`、`--no-pr --format=json` 也是；沙盒裡造一個 2,000 個 commit、其中 300 個帶記憶尾標的 repo，同樣 2 秒內。
2. 等價：對本 repo 用 main 上的舊腳本與新腳本各跑 `--no-pr`、`--no-pr --format=json`、`--no-pr --history`、`--no-pr --match=probe`、`--no-pr --path=loom-code/scripts`、`--no-pr --top=5` 六組，六組輸出 `diff` 全空（stdout 與 exit code 都相同）。**唯一例外（kouko 2026-09-06 核可）**：`fe9218d7` 這一個 commit——尾標分兩段、中間隔一條 `---`，舊腳本只讀到最後一段共 1 行，新腳本五行全讀到，多讀 4 行。只有它算例外，其餘每一 byte 的 stdout 與每一組的 exit code 仍須完全相同。視窗內的 commit 總數會隨分支長大（核可當時 423，盲跑複驗時 432），所以這裡不釘總數：盲跑報告寫出它量測時的 ref 與 `--since` 邊界，並附上可重跑的指令，數字以那份報告為準。
3. 邊界不變：沙盒裡 commit 的尾標值含 `|`、`:`、`#`、CJK 與折行（folded）續行，`Supersedes:` 指向 PR 編號與指向 sha 兩種，只帶 `Related:` 的 commit，記憶 commit 落在 `--since` 視窗外——舊腳本與新腳本輸出逐位元相同；每一種各一個測試。
4. `loom-workflow/tests/test-memory-grep-*.sh` 五份既有測試不動，全綠；`--verify`／`--verify-merged`／`--verify-strict` 的程式碼路徑 diff 為零。
5. loom-workflow 版本 bump、CHANGELOG 有一行寫改前改後秒數與量測方法；腳本檔頭寫明需要的最低 git 版本（`%(trailers:key=)` 的下限）。

## Constraints
- bash 3.2 相容（腳本現有承諾：無關聯陣列、無空陣列展開）；jq 仍是唯一必要相依。
- 只能用 git 原生 trailer parser 取尾標，不能自己用正則切 commit 訊息（腳本檔頭記錄的分隔符撞車教訓）。
- git 最低版本可以提高到 `%(trailers:key=…)` 所需的版本，但要寫在檔頭；CI 的 ubuntu-latest 與本機 2.50 都滿足。
- 走 loom 預設 full 車道，第二讀者 Codex。

## Out of scope
- `--verify`、`--verify-merged`、`--verify-strict` 三個模式（已經很快）。
- PR body 的那條路（`gh pr list`，1.6 秒是網路時間）。
- 任何輸出格式、參數或預設值的改變；加快取檔。
- git-memory SKILL.md 的文字。

## Open questions
- none
