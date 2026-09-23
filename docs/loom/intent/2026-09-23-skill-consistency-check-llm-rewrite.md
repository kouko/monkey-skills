# skill-consistency-check：改用 LLM 直接偵測矛盾的重寫版
originator: kouko
kind: engineering
needs-design: no — skill package files (SKILL.md, agents, references) are not a declared interface surface in this repo; the finding format is carried over from the validated experiment detector spec
evidence: [skill-dev-toolkit/skills/skill-consistency-check/, docs/loom/intent/2026-09-22-skill-consistency-check.md]
status: confirmed 2026-09-24
publication: automatic — authorized 2026-09-24 by kouko

## Problem
寫 skill 的人沒有可靠的方法找出 skill 內部互相矛盾的規則，例如一處要求做某件事、另一處又禁止，或是 SKILL.md 和它引用的參考檔講法不一致。矛盾的指示會讓照著 skill 做事的 agent 在某些情況下無論怎麼做都違規。

目前分支上的 `skill-consistency-check` 實作不能用：
- 把自然語言規則轉成邏輯再交給 Z3 的做法，在盲測中只抓到 7/27 個矛盾，精確率約 18%。
- 在正常的 skill 上報出大量誤判，同一個問題還會重複回報。
- 執行時會把報告寫進被檢查的資料夾，也會未經同意安裝套件到使用者的 Python 環境。
- 審查紀錄裡的「對抗測試通過」，靠的是一支永遠回報成功的空殼腳本。

## Proposed outcome
一個能對任意 skill 資料夾找出內部矛盾的檢查工具。它的做法和限制，依照 2026-09-22 到 09-23 共 10 輪盲測的結論：由 LLM 直接閱讀整個 skill 找矛盾，而不是先轉成邏輯；方法固定為「通讀」加「模擬執行」兩次；內容太大時分組檢查；只有高信心的發現會判定為需要修改。

## Acceptance
1. 對一個 skill 資料夾執行檢查後，會得到一份矛盾清單。每一項都寫出兩邊各自所在的檔案和行號、引用的原文、信心等級（高／中／低）和一句說明；另外有一個整體判定：只有存在高信心的發現時才是「需要修改」，否則是「通過」。
2. 對實驗留下的回歸測試資料執行檢查，每份測試資料都附有標準答案：埋入的矛盾至少抓到三分之二，而且沒有任何高信心的發現被標準答案判為錯誤。
3. 對一個內容超過大小上限的 skill 執行檢查時，工具會分組檢查，而報告會列出哪些檔案組合從來沒有被放在同一組檢查過。
4. 報告裡寫明：哪幾類矛盾可能被漏掉（有條件才成立的矛盾、需要推好幾步才看得出的矛盾）；這次實際用的模型；以及工具驗證時用的參考模型與內容量。兩個模型不同時，報告會提醒準確率未經驗證。
5. 執行檢查不會安裝任何套件，也不會在被檢查的 skill 資料夾裡新增或修改任何檔案。
6. 分支上舊的 Z3 版實作、空殼對抗測試腳本和不實的審查紀錄都已移除。
7. repo 既有的測試全部通過。
8. 在 Codex 上執行同一個檢查，能產出同樣格式的報告。

## Constraints
- skill 不寫死模型名稱，Claude Code 與 Codex 都要能用（使用者 2026-09-23 決定）；只要求使用主機上的中階以上模型——實驗已證明最小一級的模型（例如 haiku）不夠用。驗證用的參考模型是 20 萬 context 的 Claude Sonnet。
- 不使用 Z3、SMT 或任何「先把規則轉成邏輯」的做法。
- 大小上限是以 token 數計算的固定值，不隨模型調整，並寫明驗證時用的參考模型；要依賴其他模型的結果前，先跑回歸測試。
- skill 資料夾必須符合 repo 規定：子資料夾內不能再有子資料夾。
- 改動 skill 內容時必須調升 plugin 版本，並同步三種語言的 README。

## Out of scope
- 保證在未經驗證的模型上的準確率。
- 根據發現自動修改 skill。
- 把這個檢查接進 dogfood-skill-testing、skill-judge 或 CI 的流程。
- 再做實驗來細調大小上限或方法組合。

## Open questions
- none
