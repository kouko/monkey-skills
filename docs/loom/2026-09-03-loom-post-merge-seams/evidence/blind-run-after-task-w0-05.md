# loom 1.0 合併後的接縫 — 這一輪我試了什麼、發生了什麼

試的時間：2026-09-03，在一份乾淨的專案複本上，短 sha `f9dea518`。

這一輪只驗證計畫項目 W0-05 這一小段（intent 第 3 條 Acceptance、spec REQ-3：「刷新
`.codex/hooks/` 副本不算 gate 工作，只在有正本可比對時」），不是整個 change 的全部
Acceptance。

## What you asked for, one line at a time

### 3. 在一個乾淨的 clone 裡（Claude Code 這一側，有 plugin 正本可比的情況）只重跑
`codex_scaffold.py --repo .`（刷新 `.codex/hooks/` 副本）並 commit，不帶 `Task:`
trailer：`loom_checker.py push` 不再因 `push.dispatch-covers-tasks` 擋這個
commit；而把副本裡任一檔改一個字、多放一個檔、刪掉一個檔、或只改檔案權限再
commit，同一條規則照樣擋。

- **How I tried it**：在乾淨複本裡建一個獨立的測試 git 倉庫（用這條分支自己的測試
  輔助函式 `build_repo` / `review_body` / `write_review`，跟 `loom-code/scripts/
  test_loom_checker_push.py` 用的是同一套，不是我自己編的假資料），照 spec 描述的
  順序操作：
  1. 先用 `codex_scaffold.scaffold(repo)` 把 `.codev/hooks/` 全套副本寫進去，
     commit（帶 `Task:` trailer，這是「第一次接觸」的正常流程，不算本次要測的行為），
     跑一輪 checkpoint。
  2. 再呼叫一次 `codex_scaffold.scaffold(repo)` 想製造「刷新」的 diff——結果第二次
     呼叫沒有任何變化（`git status --porcelain` 是空的，因為版本沒變、內容本來就一
     樣）。於是照 spec 給的作法：先把副本裡 `.codex/hooks/loom_checker.py` 的版本戳
     記那一行改成一個「假版本」（decoy），連同 `Task:` trailer commit 一次；再重新
     跑一次 `codex_scaffold.scaffold(repo)` 把它復原成正版——這次復原的 commit 就是
     題目要的「純刷新副本、不帶 trailer」的那個 commit。
  3. 對這個 commit 跑一輪正常的 checkpoint review（`review.json` 記 `reviewed_sha`
     指到它），然後執行：
     ```
     python3 loom-code/scripts/loom_checker.py push
     ```
     （用的是這棵乾淨複本自己的 checker，不是 `.codex/hooks/` 裡的副本，符合「Claude
     Code 這一側」的條件——正本跟副本擺在一起可比對。）
  4. 反例 1～4：各自從同一個「刷新後」的倉庫複製一份，分別：改
     `.codex/hooks/git_exec.py` 一個字元、在 `.codex/hooks/contract/` 底下多加一個
     檔案 `extra_file.txt`、刪掉 `.codex/hooks/git_exec.py`、只對
     `.codex/hooks/contract/manifest.yaml` 做 `chmod +x`（內容不變）。每次都 commit
     （不帶 trailer）、跑一輪 checkpoint、再 `push`。
  5. 反例 5：把 `.codex/hooks/loom_checker.py` 刪掉，改成指向 `git_exec.py` 的
     symlink，commit（不帶 trailer）、checkpoint、`push`。
  6. Codex 側：直接執行「刷新」那個 commit 上、位在 `.codex/hooks/loom_checker.py`
     的那份**副本**本身：
     ```
     python3 <repo>/.codex/hooks/loom_checker.py push
     ```
     （模擬 Codex 環境：跑 push 檢查的程式本身就是那份副本，不是 Claude Code 帶的正
     本。）

- **What happened**（逐字擷取 stderr 的 `BLOCK` 行；沒有列出的表示該規則沒有擋）：

  | 情境 | `push` 結果 | `push.dispatch-covers-tasks` |
  |---|---|---|
  | 正例：純刷新副本、無 trailer | **exit 0，通過** | 未擋（也沒有其他規則擋） |
  | 反例 1：副本改一個字 | exit 1，擋下 | `BLOCK push.dispatch-covers-tasks: no \`Task:\` trailer on 1 commit(s) that change dispatched work: 52f5b537 touches gate. …` |
  | 反例 2：`contract/` 下多放一個檔 | exit 1，擋下 | 同上訊息，指到那個 commit 的 sha `3703b645` |
  | 反例 3：刪掉 `git_exec.py` | exit 1，擋下 | 同上，sha `ba193d76` |
  | 反例 4：`manifest.yaml` 只改權限（+x） | exit 1，擋下 | 同上，sha `40c1520b` |
  | 反例 5：`loom_checker.py` 換成 symlink | exit 1，擋下 | 同上，sha `d8cb1968` |
  | Codex 側：跑副本本身做 push | exit 1，擋下 | 同上，sha `479fdd11`（跟正例是同一個刷新 commit，但因為執行的 checker 換成副本自己，沒有正本可比對，規則照樣擋） |

  正例那一輪，`push` 的 stdout 只列出 package-tests 與三個對抗探針都通過（exit
  0），stderr 完全是空的——沒有任何規則名稱出現，代表不只是目標規則
  `push.dispatch-covers-tasks` 沒擋，這個 fixture 上其餘規則也都放行。

- **Evidence**：完整逐字輸出存在
  `/private/tmp/claude-501/.../scratchpad/req3_work/results.log`（本機暫存，session
  結束會清除；上面表格已把每個情境的 `BLOCK` 那一行逐字抄進來）。用來建構這些情境的
  腳本是 `blindrun_req3.py`（暫存目錄同上），呼叫的是這條分支自己
  `loom-code/scripts/test_loom_checker_push.py` 裡已經在用的同一套 helper
  （`build_repo` / `review_body` / `write_review` / `run_checker` /
  `blocked_rules`），不是我另外編的模擬資料。

- **Verdict**：**works**——正例乾淨通過，五種反例（改字、加檔、刪檔、改權限、換
  symlink）跟 Codex 側跑副本的情境全部被同一條規則擋下，訊息逐字可讀、指名哪個
  commit。這一條 Acceptance 我按 spec 給的順序完整走過一輪。

## 對你既有的資料做了什麼 (what this did to data you already had)

沒有——這一輪測試全程在一個獨立、臨時建立的 git 倉庫裡進行（在乾淨複本外的暫存目
錄），沒有讀寫這個專案原本的任何檔案，也沒有改動這棵複本本身（複本用完會整棵刪
掉）。

## I decided for你

- **正例的「刷新副本」步驟用了 decoy-stamp 手法** — spec 交代「若第二次 scaffold
  沒有 diff，就把版本戳記改成假版本、commit、再重跑 scaffold 復原」，我照做了；這
  是題目本身給的作法，不是我自己的判斷，但我把它記在這裡讓你知道正例的那個「刷新」
  commit 實際上經過了兩步（先製造假差異、再復原），不是最單純的「跑一次 scaffold
  就有 diff」情境。如果你想看最單純情境的行為，需要在版本號本身有變動的狀況下重測
  一次（例如兩個不同 plugin 版本之間的刷新）。
- 這一輪沒有收到審查站交下來的「被駁回的 important 以上發現」清單，所以沒有東西要
  在這裡揭露。

## Things I am not sure you want

- 這一輪只測了 intent 第 3 條 Acceptance（對應 spec REQ-3），沒有涵蓋 intent 的其他
  五條 Acceptance（關 intent 的推送順序、`closed` 文法、checkpoint 成本表、plugin
  版號、五個測試小瑕疵）——如果你要的是整個 change 的驗收結論，還需要另外跑那五條。
- 反例都是「單一改動」（只改一個字/只加一個檔/只刪一個檔/只改權限/只換 symlink）；
  沒有測試「同一個 commit 裡混合刷新副本＋改別的程式碼檔案」這種組合（spec 提到這
  屬於「per-path 不是 per-commit」的豁免，另有測試檔案覆蓋，但我這輪沒有重複驗
  證）。
