# OKF 相容 loom-memory — 我做了什麼、看到了什麼

2026-09-10 於乾淨環境測試，分支 `codex/2026-09-10-okf-compatible-loom-memory`，commit `bc70151ab`。我沒有寫過這個改動的任何一行程式碼。

## 你要求的東西，逐條核對

### 1. 一個乾淨的安裝，不需要另一個 Loom 外掛，就能驗證記憶庫是否符合 OKF v0.2 相容規範

**成立。** 我把 `loom-memory` 這個資料夾單獨複製到 repo 以外的乾淨目錄，確認旁邊沒有 `loom-code`、`loom-design` 或任何其他 Loom 外掛存在，然後在這個孤立環境裡直接執行驗證程式。它能正確判定一個乾淨的範本記憶庫合格，也能正確抓出我故意做壞的一份記憶檔案（缺少必要欄位）。

- **怎麼做的**：
  ```
  cp -R loom-memory <乾淨目錄>/loom-memory     # 目錄裡只有 loom-memory，沒有其他 Loom 外掛
  cd <乾淨目錄>
  python3 loom-memory/scripts/loom_memory.py validate loom-memory/templates/memory-store
  ```
- **看到的結果**：
  ```
  loom_memory validate: OK — OKF v0.2-compatible Loom memory profile holds.
  ```
  接著我自己動手做了一份缺少 `name`/`type`/`sources` 欄位的壞檔案，同一支程式立刻擋下來：
  ```
  loom_memory validate: FAIL — the following invariants are violated.
    [name] broken-lesson.md: frontmatter missing a non-empty 'name'
    [sources] broken-lesson.md: frontmatter missing at least one 'sources' entry
    [type] broken-lesson.md: frontmatter missing a non-empty 'type'
  ```
- **證據**：終端機輸出如上；孤立目錄裡 `ls` 確認只有一個資料夾 `loom-memory`，沒有其他外掛。
- **判定**：works。

### 2. 代理人可以透過一份小型的自動生成索引找到相關的舊教訓，只載入被選中的那幾筆

**成立。** repo 現有的記憶庫有 293 筆教訓，總大小約 1.4MB；生成的索引檔只有約 150KB（約十分之一），每筆只列標題和一行說明，不含全文。我用一個關鍵字在索引裡搜尋，只打開了命中的那一份完整檔案，其餘 292 份完全沒讀取。

- **怎麼做的**：
  ```
  grep -n "xdist" docs/loom/memory/index.md      # 只讀索引，不讀全部檔案
  cat docs/loom/memory/a-parallel-wave-shares-one-git-index.md   # 只打開命中的那一份
  ```
- **看到的結果**：索引裡命中 4 筆帶著一行說明的候選；打開其中一份完整檔案（2.8KB），內容完整、可用。
- **證據**：`docs/loom/memory/index.md` 共 317 行、約 150KB，對照整個記憶庫資料夾 1.4MB；單一命中檔案 2.8KB。
- **判定**：works。

### 3. 使用者或代理人可以回想、記錄、調解、汰除教訓，而不需要把記憶變成 Build、Review 或 Ship 的必經站

**成立。** 我在一個孤立的範本記憶庫裡，親自把「記錄一筆新教訓 → 調解（修改）它 → 汰除（刪除）它」這四個操作各跑了一輪，索引在每一步都正確重新生成、驗證都通過。另外我確認了 `loom-code` 的 Build、Review、Ship 三個站的操作文件裡完全沒有出現任何一句話要求呼叫 `loom-memory`。

- **怎麼做的**：新增一份合法的教訓檔案 → `regenerate-index` + `validate` →（模擬調解）編輯該檔案的說明文字 → 再次 `regenerate-index` + `validate` →（模擬汰除）刪除該檔案 → 再次 `regenerate-index` + `validate`；另外對 `loom-code` 的 `build`、`review`、`ship` 三份操作說明檔案做關鍵字搜尋。
- **看到的結果**：四步全部 `OK`，索引內容也隨每一步正確變化（新增出現一行、調解後說明文字變成新的、汰除後那一行消失）；`build`、`review`、`ship` 三份文件裡搜尋不到任何一次提及記憶功能。
- **證據**：四次 `loom_memory validate` 的輸出皆為 `OK`；索引檔案前後內容對照。
- **判定**：works。

### 4. `loom-code` 與 `loom-design` 在 `loom-memory` 沒有安裝、記憶庫不存在，或是回想沒有命中時，都照常工作

**成立，而且是用最嚴格的方式測的。** 我另外開了一份乾淨的專案複本，把 `loom-memory` 整個資料夾從這份複本裡刪掉（原本的 repo 完全沒有動），然後在「`loom-memory` 完全不存在」的狀態下分別把 `loom-code` 和 `loom-design` 各自的完整測試組跑過一遍。兩邊都全數通過，沒有任何一項因為找不到 `loom-memory` 而出錯。我也試了「搜尋一個絕對不存在的關鍵字」，確認回想沒有命中時只是安靜地查無結果，不是錯誤。

- **怎麼做的**：
  ```
  git worktree add <乾淨副本> HEAD
  cd <乾淨副本>
  git rm -r loom-memory        # 這份副本裡完全沒有 loom-memory 了
  cd loom-code && python3 -m pytest scripts -q
  cd ../loom-design && python3 -m pytest scripts -q
  grep -in "一個查無此教訓的關鍵字" docs/loom/memory/index.md   # 回想沒有命中
  ```
- **看到的結果**：
  ```
  786 passed, 2 skipped        # loom-code，loom-memory 完全不存在的情況下
  183 passed, 1 skipped        # loom-design，同樣情況
  ```
  搜尋不存在的關鍵字：找不到任何一行，安靜地沒有結果，不是錯誤訊息。
- **證據**：兩次 pytest 完整輸出；`git rm -r loom-memory` 的操作紀錄確認那份副本真的沒有這個外掛。
- **判定**：works。

### 5. 既有的記憶項目可以被搬過去，不遺失教訓內容、來源、索引說明或 Git 歷史

**成立。** 我抽查了 repo 既有的 293 筆教訓中的一筆，比對搬遷前後：教訓正文、原始出處、索引裡的一行說明都逐字相同，唯一變的是「出處」欄位的寫法（從舊的 `origin:` 欄位換成新格式 `sources: - resource:`，內容不變）。這筆檔案的 Git 歷史（`git log`）在搬遷前後也連續沒有中斷。另外我執行了這個改動自帶的「搬遷後回頭核對」測試，它會直接從 Git 重新算出搬遷前的 293 筆內容去比對，而不是相信一份寫死的清單 —— 這個測試也全數通過。

- **怎麼做的**：
  ```
  git show <搬遷前 commit>:docs/loom/memory/README.md | grep -A1 "gate-review-weight-on-task-kind-not-loc"
  grep "gate-review-weight-on-task-kind-not-loc" docs/loom/memory/index.md
  git log --oneline -- docs/loom/memory/gate-review-weight-on-task-kind-not-loc.md
  python3 -m pytest loom-memory/scripts/test_migrate_legacy_store.py -q
  ```
- **看到的結果**：索引裡的一行說明搬遷前後逐字相同；`git log` 顯示搬遷前後的提交都掛在同一個檔案上，沒有斷掉；搬遷回頭核對測試「15 passed」。
- **證據**：上述指令輸出；搬遷那次提交的說明文字也寫著「Every lesson body and description is preserved byte-for-byte」。
- **判定**：works。

### 6. 結構性損壞會在明確呼叫的記憶操作裡清楚失敗，同時不相關的 Loom 工作不受影響

**成立。** 我把記憶庫複製一份出來，先刪掉它的索引檔（只留教訓檔案本身），再故意弄壞一份教訓檔案的必要欄位，兩次都用驗證指令清楚地指名是哪個檔案、缺了哪個欄位而失敗 —— 不是含糊的錯誤，也沒有把壞掉的資料誤判成「沒有教訓」。同時我在真正的 repo 裡（記憶庫完全沒被動到）執行了幾個跟記憶無關的 `loom-code` 測試，照常通過，證明記憶庫的損壞不會波及其他工作。

- **怎麼做的**：
  ```
  cp -R docs/loom/memory <損壞副本>
  rm <損壞副本>/index.md
  python3 loom-memory/scripts/loom_memory.py validate <損壞副本>

  # 恢復索引，改弄壞另一份檔案的 name 欄位
  python3 loom-memory/scripts/loom_memory.py validate <損壞副本>

  python3 -m pytest loom-code/scripts/test_contract_manifest.py -q
  ```
- **看到的結果**：
  ```
  loom_memory validate: FAIL — the following invariants are violated.
    [index-missing] index.md: the Loom profile requires a generated index.md
  ```
  以及
  ```
  loom_memory validate: FAIL — the following invariants are violated.
    [name] gate-review-weight-on-task-kind-not-loc.md: frontmatter missing a non-empty 'name'
  ```
  同時 `loom-code` 的測試「12 passed」，完全不受影響；真正的 repo 記憶庫再驗一次仍然是 `OK`。
- **證據**：上述兩段 FAIL 輸出各指名了具體檔案與欄位；`loom-code` 測試通過紀錄；`git status` 確認真實的記憶庫檔案沒有被動過。
- **判定**：works。

## 對你既有的資料做了什麼

這次改動把你現有的 293 筆記憶（`docs/loom/memory/` 底下）就地改寫了格式 —— 每一份檔案的「出處」欄位從舊的單行 `origin:` 換成新的 `sources: - resource:` 結構，教訓正文與索引說明文字保持逐字不變。原本手寫維護的 README 索引段落被拿掉，改成自動生成的 `index.md`；README 其餘的說明文字保持不變。這不是新增一個副本、留一個舊版當備份 —— 舊格式不會再出現在工作樹裡，往回找舊版本要靠 Git 歷史（我在第 5 條已經確認 Git 歷史沒有斷掉，可以隨時 `git show` 回去看搬遷前的原始檔案）。

## 我幫你決定的事

沒有需要我在測試過程中額外決定的分岔 —— 六條驗收標準都是照著它原本寫的方式直接試出結果，沒有遇到「兩種讀法都通、要挑一個」的情況。

不過有一件事我認為你應該知道，雖然它不是六條驗收標準裡的任何一條：`loom-memory/README.md` 開頭的「Status」那一行還寫著「v0.1.0 — scaffolding only. 這個功能、驗證器、搬遷都還沒做」，但我實際測試下來，這些東西全部都已經做好而且能用（六條標準都通過）。同一個資料夾裡的 `CHANGELOG.md` 反而正確描述了完成的狀態。這是一份會被使用者第一眼看到、內容卻是舊的文件 —— 建議在合併前把 README 的 Status 那一行改成跟 CHANGELOG 一致。

## 我不確定你是否想要的事

沒有。六條標準都親自試過，沒有含糊不清、需要你再判斷一次的地方。
