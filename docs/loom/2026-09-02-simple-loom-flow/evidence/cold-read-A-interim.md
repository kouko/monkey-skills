# 冷讀 Task A（write-plan 站）— W1 期間兩輪（正式驗收在 W4-01）

Task A：六支腳本抽共用 git helper，只裝 loom-code，Codex。冷讀者只拿 `loom-code/skills/write-plan/SKILL.md`（＋同目錄 references/）。

| 輪 | commit | 開檔 | 時間 | 猜測 | 內容 |
|---|---|---|---|---|---|
| 1 | 4cbb40d0 | 2 | <5 min | 7 | needs-design 判準沒寫；`kind` 值域沒定義；「第二家 CLI」沒排除 host；slug 規則；review.json 誰建立；contract 規則 id；KICKOFF 不存在時怎麼辦 |
| 2 | dc6e8bf7 | 2 | — | 4 | 2 條任務事實未給（本機有無第二家 CLI、本題有無單向門），文件無責；2 條真缺口：無 spec 時 `intake.spec-pass` 怎麼算、Codex 上 Step 0 用的 checker 要 Step 0b 才寫入（順序矛盾）→ dead30e5 修 |

兩輪四項回答（產生哪些檔／誰決定／checker 何時擋／審查何時跑）路徑與決策點皆正確；第 2 輪自行套用 needs-design 規則得出 `no` 並引用文件範例。
