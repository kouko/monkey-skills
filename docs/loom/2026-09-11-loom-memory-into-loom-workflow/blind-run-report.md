# loom-memory 搬進 loom-workflow — 我試了什麼、結果如何

2026-09-11 在乾淨的一份專案副本上試的，分支 `codex/2026-09-11-loom-memory-into-loom-workflow`，commit `d1c4c2ba8`。我沒有寫過這個改動的任何一行程式碼。

## 你要的東西，一條一條來

### 1. 我在只裝了 loom-workflow 的環境裡，可以呼叫記憶能力，做 recall、record、reconcile、retire 四件事，不需要再裝任何別的 plugin

**成立。** 我把 `loom-workflow` 這一個資料夾單獨複製到 repo 以外的一個全新目錄，那個目錄裡除了 `loom-workflow`什麼都沒有——沒有 `loom-code`、沒有 `loom-design`、沒有 repo 根目錄的任何其他東西。在這個隔離環境裡，我從零建立一個新的記憶庫，把回想、記錄、調解、汰除四個操作各跑了一次。

- **我怎麼試的**：
  ```
  cp -R loom-workflow <全新目錄>/loom-workflow    # 目錄裡只有這一個資料夾
  cd <全新目錄>
  # 回想：對一個空記憶庫產生索引，看它安靜地回報「沒有教訓」而不是報錯
  python3 loom-workflow/skills/loom-memory/scripts/loom_memory.py regenerate-index mystore
  python3 loom-workflow/skills/loom-memory/scripts/loom_memory.py validate mystore
  # 記錄：新增一份教訓檔案，重新產生索引、驗證
  python3 loom-workflow/skills/loom-memory/scripts/loom_memory.py regenerate-index mystore
  python3 loom-workflow/skills/loom-memory/scripts/loom_memory.py validate mystore
  # 調解：改掉那份教訓的說明文字，重新產生索引、驗證
  python3 loom-workflow/skills/loom-memory/scripts/loom_memory.py regenerate-index mystore
  python3 loom-workflow/skills/loom-memory/scripts/loom_memory.py validate mystore
  # 汰除：刪掉那份教訓檔案，重新產生索引、驗證
  python3 loom-workflow/skills/loom-memory/scripts/loom_memory.py regenerate-index mystore
  python3 loom-workflow/skills/loom-memory/scripts/loom_memory.py validate mystore
  ```
- **看到的結果**：四個操作全部成功，四次驗證都回報 `OK`。空記憶庫回想時安靜地只顯示「Memory Store Index」標題，沒有任何錯誤；新增教訓後索引裡多了一行；改說明文字後那一行內容跟著變；刪除教訓後那一行也跟著消失，同樣沒有報錯。整個過程完全沒有用到 `loom-code`、`loom-design`，也沒有任何指令去尋找它們。
- **證據**：四次 `loom_memory validate` 的輸出皆為 `OK`；隔離目錄下 `ls` 只看到 `loom-workflow` 一個資料夾。
- **判定**：符合。

### 2. `loom-memory` 這個獨立 plugin 不存在了：marketplace 清單裡沒有它，plugin 目錄也沒有它

**成立。** 我檢查了 marketplace 的清單檔案，裡面列出的 24 個 plugin 名稱裡沒有 `loom-memory`；repo 根目錄下也已經沒有一個叫 `loom-memory` 的資料夾——連 Git 追蹤的檔案清單裡都查不到任何一個路徑是以 `loom-memory/` 開頭。原本的記憶能力現在整個住在 `loom-workflow/skills/loom-memory/` 這個子資料夾裡，是 loom-workflow 的一把工具，不是一個獨立安裝項目。

- **我怎麼試的**：讀取 marketplace 清單檔案，列出所有 plugin 名稱；在 repo 根目錄找有沒有 `loom-memory` 資料夾；在 Git 追蹤的完整檔案清單裡搜尋任何以 `loom-memory/` 開頭的路徑。
- **看到的結果**：marketplace 清單裡的 24 個名稱不含 `loom-memory`；根目錄沒有這個資料夾；Git 追蹤清單裡搜尋不到任何一筆。
- **證據**：marketplace 清單解析結果（24 個 plugin 名稱，逐一核對不含 `loom-memory`）；`test -d loom-memory` 回報不存在；`git ls-files | grep "^loom-memory/"` 沒有輸出。
- **判定**：符合。

### 3. 已經遷移好的 293 條 lesson 與那份索引，內容一個位元組都沒變

**成立。** 我把這個分支和它出發前的主幹版本做逐檔比對，範圍限定在存放 293 條教訓的那個資料夾。結果只有一份「使用說明」文件（不是教訓本身，是給人看的操作指南）被改了幾行——改的是文字裡提到驗證程式新家的路徑，教訓內容完全沒被動到。索引檔案本身，以及 293 份教訓檔案，逐位元組比對下來完全沒有任何差異。

- **我怎麼試的**：
  ```
  git diff origin/main...HEAD -- docs/loom/memory/index.md    # 索引本身
  git diff origin/main...HEAD -- docs/loom/memory              # 整個資料夾
  ls docs/loom/memory | grep -v -E "^(index.md|README.md)$" | wc -l   # 數教訓檔案數量
  ```
- **看到的結果**：索引檔案的差異是 0 行——完全沒變。整個資料夾唯一的差異落在「使用說明」文件（README.md）身上，改動只是把裡面提到的驗證程式路徑，從舊路徑換成新路徑，一共 4 處文字，教訓內容一個字都沒動。教訓檔案數量核對下來正好是 293 份，全部沒有差異。
- **證據**：`git diff` 的輸出（索引 0 行差異；資料夾差異只集中在說明文件的路徑文字，統計為「1 個檔案改動，4 行加、4 行刪」）；教訓檔案計數 293。
- **判定**：符合。

### 4. 驗證儲存庫記憶格式的指令仍然可用，指向 loom-workflow 裡的新位置；舊位置沒有留下任何還能跑的殘骸

**成立。** 我直接用新路徑對 repo 現有的真實記憶庫跑了一次驗證，成功回報格式合格。我也確認了負責在你編輯記憶檔案時自動把關的那支背景檢查程式，裡面寫的也是新路徑；然後在整個 repo 裡搜尋，找不到任何檔案還在把舊路徑（獨立 plugin 時代的路徑）當成一個可以執行的指令來引用。

- **我怎麼試的**：
  ```
  python3 loom-workflow/skills/loom-memory/scripts/loom_memory.py validate docs/loom/memory
  grep -n "VALIDATOR=" .claude/hooks/check-memory-store-integrity.sh
  grep -rn "python3 loom-memory/scripts" .  # 找有沒有人還在用舊路徑當指令
  ```
- **看到的結果**：驗證指令直接成功回報 `OK`；背景檢查程式裡指向的驗證器路徑已經是新家的路徑；全 repo 搜尋不到任何一處還把舊路徑當可執行指令使用。
- **證據**：`loom_memory validate: OK` 的輸出；背景檢查程式裡的路徑變數；空的搜尋結果。
- **判定**：符合。

### 5. loom-code 與 loom-design 在完全沒裝 loom-workflow 的情況下，各自的測試仍然全綠

**部分成立——loom-design 全綠，loom-code 不是。** 我另外開了一份乾淨的專案副本，把整個 `loom-workflow` 資料夾從這份副本裡刪掉（原本的 repo 完全沒有動），然後在「`loom-workflow` 完全不存在」的狀態下，把 `loom-code` 和 `loom-design` 各自的完整測試組跑過一遍。

`loom-design` 的測試組完全通過，沒有任何一項因為找不到 `loom-workflow` 而出錯。但 `loom-code` 的測試組沒有全綠：有 4 支測試會在收集階段就直接報錯或失敗，原因都是它們裡面寫死了要去讀 `loom-workflow` 資料夾底下的特定檔案（例如某個站的說明文件、某支背景規則清單），一旦 `loom-workflow` 不在，這些測試連跑都跑不起來。

我額外核對過：這 4 支測試的內容，在這次改動出發之前的主幹版本上就已經長這樣，這次改動完全沒有碰過它們——換句話說，這不是「搬記憶功能」這個動作造成的新問題，是這個 repo 原本就存在、這次改動之前就有的一個舊有耦合。但驗收標準問的是「測試仍然全綠」這個結果，而結果確實不是全綠，所以我如實回報為不成立，而不是因為找到了原因就自動算過關。

- **我怎麼試的**：
  ```
  git worktree add <乾淨副本> HEAD
  cd <乾淨副本>
  git rm -r loom-workflow        # 這份副本裡完全沒有 loom-workflow 了
  cd loom-design && python3 -m pytest scripts -q
  cd ../loom-code && python3 -m pytest scripts -q
  # 額外核對：這幾支失敗測試在改動前的主幹版本上是不是本來就長這樣
  git diff origin/main...HEAD -- loom-code/scripts/test_simplified_station_text.py
  git diff origin/main...HEAD -- loom-code/scripts/test_check_contract_citations.py
  git diff origin/main...HEAD -- loom-code/scripts/test_check_mechanisms.py
  git diff origin/main...HEAD -- loom-code/scripts/test_legacy_contract_removed.py
  ```
- **看到的結果**：
  ```
  loom-design: 183 passed, 1 skipped   # loom-workflow 完全不存在的情況下
  loom-code:   824 passed, 2 skipped, 3 failed, 1 collection error
  ```
  4 支出問題的測試，逐一核對下來在這次改動出發前的主幹版本上內容完全相同（每一支的差異都是 0 行）——證實這 4 個問題不是這次「搬記憶功能」造成的，而是這個 repo 一直以來就有的舊狀況。
- **證據**：兩次 pytest 完整輸出；4 支測試檔案的 `git diff` 皆為 0 行差異的紀錄。
- **判定**：loom-design 這一半符合；loom-code 這一半不符合（原因是舊有問題，不是這次改動造成的新問題，但驗收標準要求的結果沒有達成）。

## 對你既有的資料做了什麼

這次改動把 `docs/loom/memory/` 裡給人看的「使用說明」文件（README.md）改了幾行字——只是把裡面提到的驗證程式路徑，從舊路徑換成新路徑，說明的意思沒有變。你既有的 293 條教訓內容，以及那份自動生成的索引，完全沒有被碰過，逐位元組相同。沒有留下舊版備份檔——如果之後想回頭看改動前的原始檔案，靠 Git 歷史就可以找回來，這條歷史在這次改動裡沒有被截斷過。

## 我幫你決定的事

沒有——五條驗收標準都是照著它原本寫的方式直接試出結果，沒有遇到需要我自己判斷、挑一個讀法的岔路。

不過有一件事我認為你應該知道，雖然嚴格說不是這五條標準裡任何一條沒過：驗收第 5 條「loom-code 與 loom-design 在完全沒裝 loom-workflow 的情況下，各自的測試仍然全綠」，loom-code 那一半沒有通過，原因是這個 repo 原本就有 4 支測試寫死要去讀 `loom-workflow` 資料夾裡的檔案（不是這次搬家造成的新問題，這次改動幾乎沒碰過 `loom-code`）。但這代表如果你真的打算讓 `loom-code` 完全獨立於 `loom-workflow` 之外運作，這件事目前還沒有做到——它需要另外一次改動來處理，這次的「搬家」本身沒有讓情況變得更糟，也沒有讓它變得更好。

## 你可能還沒想清楚的地方

沒有。五條標準都親自試過，沒有含糊不清、需要你再判斷一次的地方。
