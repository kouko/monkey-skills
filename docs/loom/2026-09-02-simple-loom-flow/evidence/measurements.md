# W4-04 量測 — 2026-09-03（HEAD 於 W4-01 之後）

| 項目 | 值 | 目標／基線 | 來源指令 |
|---|---|---|---|
| skill 數（計數） | 17（loom-code 5、loom-design 4、loom-workflow 8＋2 standalone） | ≤18（REQ-8） | `check_mechanisms.py --measure`；`ls */skills` |
| artifact 種類（manifest） | 4（intent／spec／plan／review）＋diff/PR＝5 形狀 | ≤5（REQ-5／REQ-8） | 同上 |
| session-start 注入字數 | 655（LC_ALL=C；先前 658／5281 是 Mac 語系下數的） | ≤2639（基線 5278 的一半；REQ-8） | `bash loom-code/hooks/session-start </dev/null \| LC_ALL=C wc -w`（空 repo）；基線由 923fb84a 重算相符 |
| checker 規則 | 27 | — | `loom_checker.py --list-rules \| wc -l` |
| 機制淨數 | 128（不含 host-hygiene） | 基線 41 為近似值（origin/main 無 mechanisms.yaml）；R3 在 merge 後才真正 gate | `check_mechanisms.py --baseline origin/main` |
| 名詞（手數，§3 規則） | 61 | ≤40 為 intent Open question，**未達** | concept-model §3（W3-06） |
| needs-design: yes 的 intent | 1／1 | 記錄 | `grep -l` |
| 逾期未確認 intent | 0 | 記錄 | — |
| 本 change 決策點 | 2（① intent、② 可見行為）＋③ 待 W4-05 | product ≤3（REQ-1） | review.json |
| 本 change 決策點內問題 | 7（① 5、② 2） | 不限；每題可歸三型或後果形 | review.json `questions[]` |
| 本 change 派工 | 59（implementer 21、reviewer 29、blind-runner 4、adversary 5） | — | review.json `dispatch[]` |
| 本 change commit（至 W4-01） | 173，其中 81 帶 `Task:` trailer | — | `git log` |
| checkpoint 輪次 | spec 6（含 1 對抗）、W0 3、W1 5、W2 5、W3 2 | build 階段 ≤5 個 checkpoint（修正輪不計）：W0–W3 各 1 個 checkpoint＝4 | review.json |

備註：本 change 是「重寫整套機制」，commit／派工數不能與 REQ-10 的三個 replay 比較；REQ-10 見 replay-*.md。
