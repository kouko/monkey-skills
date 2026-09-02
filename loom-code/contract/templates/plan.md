# <title> — plan
intent: <change-id>@<sha>
spec: docs/loom/<change-id>/spec.md@<sha>     # 只在 needs-design: yes

## Current State Evidence                  # 只在 needs-design: no（spec 不存在時，五條在這裡）
- Forward／Reverse／Error／Data／Boundary：<路徑與錨點>

## Task DAG
<wave 分段；每 task 穩定 ID；同 wave 無依賴者可平行>

**<W0-01> <title>**　after: <ids>　review: after-task（每 plan ≤ 2）
- 檔：<會動的檔案>
- 測：<先寫失敗的測試>
- 風：<風險與預設選擇；agent-decided 標記>

## Risks
1. <全 plan 風險>
