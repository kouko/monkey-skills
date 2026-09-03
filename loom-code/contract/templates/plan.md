# <title> — plan
intent: <change-id>@<sha>
spec: docs/loom/<change-id>/spec.md@<sha>     # 只在 needs-design: yes

## Current State Evidence                  # 只在 needs-design: no（spec 不存在時，五條在這裡）
- Forward／Reverse／Error／Data／Boundary：<路徑與錨點>

## Task DAG
<wave 分段；每 task 穩定 ID；同 wave 無依賴者可平行>

**<W0-01> <title>**　after: <ids>　review: after-task
<!-- 前兩個 after-task 免理由；第三個起寫成 `review: after-task — <理由>`，
     checker 規則 intake.after-task-budget 讀這一行 -->
- 檔：<會動的檔案>
- 測：<先寫失敗的測試>
- 風：<風險與預設選擇；agent-decided 標記>

## Questions asked                        # 決策點 ①（與在此執行的 ②）問過的每一題
<決策點編號> — <what|behaviour|done|consequence> — <原話>
<!-- review 站在第一次 checkpoint 把這一段抄進 review.json 的 questions[] -->

## Risks
1. <全 plan 風險>
