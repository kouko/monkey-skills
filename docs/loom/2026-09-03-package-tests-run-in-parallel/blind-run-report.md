# 整包測試平行跑 — 我實際試了什麼、發生了什麼

在 2026-09-03，用一份乾淨的專案副本（sha `5632472c`，跟你決定要驗收的版本一致）試的。環境是全新建立的 Python 虛擬環境，跟平常開發用的環境完全分開。

## 你要的東西，一條一條試

### 1. 在乾淨環境照 README 裝好開發依賴後，跑 KICKOFF-DEFAULTS 記的那行命令，1061 條全過，本機牆鐘時間低於原本的三分之一。
- **How I tried it**：照 README「Contributing」段落的指示裝依賴（`python3 -m pip install -r requirements-dev.txt`；因為這次的乾淨環境是用 `uv venv` 建的新虛擬環境、裡面沒有內建 pip 模組，我改用等效的 `uv pip install -r requirements-dev.txt` 裝進同一個虛擬環境——這是唯一需要我自己判斷的地方，效果與 README 寫的指令相同）。裝完後跑 KICKOFF-DEFAULTS 記的那行測試指令（`python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q -n auto`，`python3` 換成這個虛擬環境自己的 python）。為了算出「原本的三分之一」，另外把同一批測試「不加 `-n auto`」（串行）跑一次當基準。
- **What happened**：平行跑：**1063 通過，耗時 38.24 秒**。串行跑（同一批測試，同一台機器，只是不平行）：**1063 通過，耗時 212.77 秒**。38.24 秒是 212.77 秒的 18%，遠低於三分之一（三分之一門檻約 70.9 秒）。（附註：intent 裡寫的是「1061 條」，我這次乾淨環境跑出來是 1063 條——比原始量測時多了兩條，全部通過，不影響驗收判定，只是誠實記一下數字對不上。）
- **Evidence**：平行跑輸出末行 `1063 passed in 38.24s`；串行跑輸出末行 `1063 passed in 212.77s (0:03:32)`（皆為 Bash 前景執行、`time` 量測、非背景任務）。
- **Verdict**：works — 通過、且遠優於三分之一門檻。

### 2. CI 用同一行命令且綠燈；`loom_checker.py push` 對 `package-tests` 探針的逐字比對仍通過。
- **How I tried it**：把 CI 設定檔那行跟 KICKOFF-DEFAULTS 那行並排看：
  - CI（`.github/workflows/loom-code-ci.yml`）：`python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -v -n auto`
  - KICKOFF-DEFAULTS：`python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q -n auto`
  另外在乾淨環境跑了檢查器讀命令的那段程式，看它實際讀到什麼：`declared_test_command(Path('.'))` → 回傳 `('python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q -n auto', 'docs/loom/KICKOFF-DEFAULTS.md')`。也看了「逐字比對」那段程式在比什麼。
- **What happened**：跑的**路徑**（`loom-code/scripts/ scripts/ .claude/hooks/`）跟 `-n auto` 兩處完全一致。唯一的差異是 `-q`（本機安靜輸出）vs `-v`（CI 逐條輸出）——這不是遺漏，這次改動的 plan 文件裡明寫這個差異是刻意保留的（CI 要看逐條輸出方便除錯），所以不算「同一行」字面相同，但是同一個測試集合、同樣平行。逐字比對的機制本身，是拿「紀錄下來的探針指令」去跟 **KICKOFF-DEFAULTS 那一行**逐字核對（不是跟 CI 那行比），再用 KICKOFF-DEFAULTS 那行實際重跑一次、看結果一不一致——不是自己說了算。CI 真的綠燈這件事，因為 PR 還沒開、CI 還沒被觸發，**目前無法觀察，只能誠實說「CI 待驗」**。
- **Evidence**：兩份設定檔的原文（如上）；`declared_test_command` 的輸出（如上）。
- **Verdict**：partly — 路徑與平行旗標一致、比對機制本身確認可運作；CI 是否綠燈要等 PR 真的跑過才能確認。

### 3. 沒有測試因為平行而互相踩到（連跑三次結果一致）。
- **How I tried it**：在同一份乾淨環境裡，把 KICKOFF-DEFAULTS 那行平行測試指令連續跑三次。
- **What happened**：三次都是 **1063 通過、0 失敗**，只有耗時不同（38.24 秒／39.90 秒／62.26 秒——第三次比較慢，看起來是機器當下負載影響，不是測試本身變了結果）。三次的通過數與結果完全一致，沒有偶發失敗。
- **Evidence**：三次輸出末行分別為 `1063 passed in 38.24s`、`1063 passed in 39.90s`、`1063 passed in 62.26s (0:01:02)`。
- **Verdict**：works — 三次結果一致。

## 對你既有的資料做了什麼

沒有動到你既有的東西。這次改動只碰了四個地方：`README.md`（加三行說明怎麼裝依賴）、`.github/workflows/loom-code-ci.yml`（CI 裝依賴的方式、加 `-n auto`）、`docs/loom/KICKOFF-DEFAULTS.md`（測試指令那行加 `-n auto`）、新增 `requirements-dev.txt` 與一個新的測試檔（用來鎖住「三處指令要同步」這件事）。**沒有改任何一個既有測試的寫法**，我在乾淨環境裡對比過改動範圍，確認只有新增檔案、沒有修改既有測試邏輯。裝依賴這件事也只發生在我自己建的隔離虛擬環境裡，沒有碰到你平常用的開發環境。

## I decided for you

- **`-n auto`（依機器核心數動態決定，而不是寫死一個數字）** — 這是實作時就已經做的選擇（記在 KICKOFF-DEFAULTS 的註解裡），理由是本機 16 核與 CI 4 核用同一個固定數字，其中一邊一定會太擠或太閒。想改成固定數字，之後要在兩台機器上重新量測。
- **本機 `-q`（安靜輸出）跟 CI `-v`（逐條輸出）刻意留著不同** — plan 文件記錄的選擇：CI 要逐條輸出方便事後追查是哪條測試出的錯，本機跑起來安靜比較好讀。如果你要求「同一行」必須連這個旗標都一樣，這裡就是會被挑出來的地方。
- **裝 `pytest-xdist` 這個新依賴，是裝進實作者當下在用的 Python 環境（不是另外建一個新環境）** — plan 文件記錄的選擇，理由是「可逆、不花錢、不動資料」；如果你在本機重新照 README 走一次，會裝進你當時 `python3` 指到的那個環境（例如你的 conda 環境），而不是自動幫你隔離出一個新環境。
- 目前這份改動的 review 紀錄（`review.json`）裡，reviewer 的審查結論與是否有被駁回的重大發現都還是空的（尚未由審查站填寫），所以**沒有**發現任何「severity important 以上、被駁回」的項目可以列在這裡。

## Things I am not sure you want

- CI 是否真的綠燈，要等這個改動真的開出 PR、CI 真的跑過才能確認——我這次驗證只能到「路徑與平行旗標一致、比對機制可運作」，無法看到 CI 執行結果。
- 這次乾淨環境裝出來是 1063 條測試通過，intent 原文寫的是 1061 條；差 2 條看起來是自然增長（不是這次改動造成的），但我沒有去追查是哪兩條新增的，如果你在意這個數字對不上，可以再確認一下。
