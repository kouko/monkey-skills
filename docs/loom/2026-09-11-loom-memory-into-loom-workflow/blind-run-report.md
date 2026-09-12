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

### 5. 這次改動沒有讓「沒裝 loom-workflow」這件事變得更糟：loom-design 在沒有 loom-workflow 時測試全綠；loom-code 的測試套件在改動前後以完全相同的方式失敗（同一組既有的跨 plugin 讀檔），而且沒有新增任何 loom-code 或 loom-design 對 loom-workflow 的依賴

**先說一件事：這條驗收標準的文字，是在我第一次盲跑之後被改過的。** 我原本試的第 5 條寫的是「loom-code 與 loom-design 在完全沒裝 loom-workflow 時各自測試全綠」，我盲跑出來是部分成立——loom-design 全綠，但 loom-code 有 4 支測試因為寫死要讀 loom-workflow 底下的檔案而跑不起來。這個結果讓 kouko（這個 repo 的負責人）發現，這條標準本身問錯了：那 4 支測試在改動之前、這個 repo 從未真正「沒裝 loom-workflow」跑起來過的狀態下，其實就已經是這樣，所以「全綠」是一條這個 repo 從來沒有滿足過的性質，寫的人（上一輪）沒有先量過基準線就寫下去了。kouko 在同一天把這條標準改成上面這個可以被證明的版本，把「每個 plugin 完全獨立可測」這個更大的目標留給另一次改動。讀者應該知道，這不是我事後幫忈動了目標，是委託人自己把靶子移到量得出來的地方。

**這條改過的標準，我自己重新量了一遍，成立。** 這次我沒有沿用自己上次的數字，也沒有先看已經寫好的測量紀錄，而是從頭做了一份獨立的度量：分別用兩份完整的 git 副本（一份是這次改動完成後的版本、一份是改動之前的主幹版本），各自把 `loom-workflow` 整個資料夾拿掉，然後把 `loom-code` 和 `loom-design` 的完整測試組分開跑（兩個套件裡有同名的測試檔案，混在一起跑會因為工具本身的限制而互相打架，所以一定要分開跑，這是這個 repo 自己的測試執行方式，不是我的偏好）。

- **loom-design**：拿掉 loom-workflow 之後，改動前、改動後都是 183 個通過、1 個跳過，完全沒有紅燈。
- **loom-code**：拿掉 loom-workflow 之後，改動前、改動後都是同樣的 3 支測試失敗、1 支測試連收集階段都進不去、824 個通過、2 個跳過——而且逐支核對失敗訊息的文字，改動前後一字不差。失敗的原因都是同一組早就存在的問題：一支測試會去跑一支背景檢查程式，那支程式的「已知違規清單」裡登記了幾筆現在已經不再違規的舊項目；一支測試會去核對一份規則清單裡登記的每個測試檔案是否存在；一支測試會去讀幾個站別的說明文件；還有一支測試在收集階段就因為讀不到一份協定文件而直接報錯。這四個問題全部指向同一件事——這個 repo 原本就有幾處會去讀 `loom-workflow` 裡檔案的測試，跟這次「搬記憶功能」這個動作無關，改動前後長得一模一樣。
- 我也核對過這次改動有沒有偷偷幫 loom-code 或 loom-design 增加新的、指向 loom-workflow 的依賴：把改動前後的差異限定在這兩個資料夾裡看過一遍，裡面提到 loom-workflow 的地方只有一行說明文字（記在變更紀錄裡，說明記憶功能搬家後這個既有的掃描範圍現在也涵蓋到它的新家）和一行程式碼被拿掉（移除的是「舊獨立 plugin 位址」那一行，不是新增）；原本就存在、指向 loom-workflow 的那一行掃描設定，這次改動完全沒有動它。沒有新增依賴。

**跟已經寫好的那份測量紀錄比對，數字不一樣，但結論一致，而且我認為我的方法更可靠。** 委託人指的那份既有紀錄用的是「打包匯出一份程式碼快照」的方式做副本，這種副本裡沒有 `.git` 資料夾；而 loom-code、loom-design 裡有幾支測試本身就會呼叫 git 指令去讀版本紀錄，副本裡沒有 `.git` 就會讓這些測試用另一種方式壞掉（是量測方式本身造成的假象，不是程式碼的問題），所以那份紀錄看到的失敗清單跟我看到的不同，而且它把 loom-design 也算進「有失敗」——但那筆失敗一樣是「沒有 `.git`」這個量測方式造成的假象，不是 loom-design 真的有問題。我這次改用「完整的 git 副本」而不是「程式碼快照」，兩邊都留著 `.git`，量出來的 loom-design 確實全綠，跟這條標準的文字直接吻合；loom-code 那 4 個問題，也正好跟我自己第一次盲跑量到的那 4 個問題對得上。也就是說：兩份測量都同意「改動前後沒有變糟」這個核心結論，但既有紀錄裡的具體失敗清單，是它自己量測方式的產物，不是這次改動真正呈現的樣子。

- **我怎麼試的**：
  ```
  git worktree add <改動後副本> HEAD
  git worktree add <改動前副本> origin/main
  cd <改動後副本> && git rm -r loom-workflow
  cd <改動前副本> && git rm -r loom-workflow
  # 兩份副本分別執行
  cd loom-design && PYTHONDONTWRITEBYTECODE=1 python3 -m pytest scripts -q
  cd ../loom-code && PYTHONDONTWRITEBYTECODE=1 python3 -m pytest scripts -q --continue-on-collection-errors
  # 核對這次改動有沒有新增 loom-workflow 依賴
  git diff origin/main...HEAD -- loom-code loom-design | grep -n "loom-workflow"
  ```
- **看到的結果**：
  ```
  loom-design（改動前／改動後皆同）：183 passed, 1 skipped
  loom-code（改動前／改動後皆同）：824 passed, 2 skipped, 3 failed, 1 collection error
  ```
  3 支失敗與 1 支收集錯誤的測試名稱、失敗訊息文字，改動前後逐字相同；差異比對裡沒有找到任何新增的 loom-workflow 依賴，只有一行既有掃描設定被沿用、一行舊路徑設定被刪除。
- **證據**：四次 pytest 完整輸出（改動前後各兩個套件）；`git diff origin/main...HEAD` 限定在 loom-code、loom-design 兩個資料夾裡搜尋 loom-workflow 字樣的比對結果；已委託人接受、同日寫入 intent 文件 Amendments 段落的標準修訂紀錄。
- **判定**：符合（依修訂後的標準）。這條標準本身在盲跑過程中被改過一次，讀者應該知道原先的版本問的是這個 repo 從未具備過的性質。

## 對你既有的資料做了什麼

這次改動把 `docs/loom/memory/` 裡給人看的「使用說明」文件（README.md）改了幾行字——只是把裡面提到的驗證程式路徑，從舊路徑換成新路徑，說明的意思沒有變。你既有的 293 條教訓內容，以及那份自動生成的索引，完全沒有被碰過，逐位元組相同。沒有留下舊版備份檔——如果之後想回頭看改動前的原始檔案，靠 Git 歷史就可以找回來，這條歷史在這次改動裡沒有被截斷過。

## 我幫你決定的事

沒有——五條驗收標準都是照著它原本寫的方式直接試出結果，沒有遇到需要我自己判斷、挑一個讀法的岔路。

不過有一件事我認為你應該知道，雖然嚴格說不是這五條標準裡任何一條沒過：驗收第 5 條「loom-code 與 loom-design 在完全沒裝 loom-workflow 的情況下，各自的測試仍然全綠」，loom-code 那一半沒有通過，原因是這個 repo 原本就有 4 支測試寫死要去讀 `loom-workflow` 資料夾裡的檔案（不是這次搬家造成的新問題，這次改動幾乎沒碰過 `loom-code`）。但這代表如果你真的打算讓 `loom-code` 完全獨立於 `loom-workflow` 之外運作，這件事目前還沒有做到——它需要另外一次改動來處理，這次的「搬家」本身沒有讓情況變得更糟，也沒有讓它變得更好。

## 你可能還沒想清楚的地方

沒有。五條標準都親自試過，沒有含糊不清、需要你再判斷一次的地方。
