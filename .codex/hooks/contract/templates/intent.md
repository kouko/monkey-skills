# <title>
originator: <who>            # 人名、"maintenance-loop"、或 map:<id>
kind: product | engineering
needs-design: yes | no — <reason>
map: <map-id>                # 可選
evidence: [<paths>]          # 可選；write-spec／review 必讀
status: open                 # open | confirmed <date> | withdrawn — <reason>；缺＝open

## Problem
<問題與誰受影響，白話。product：禁檔案路徑、函式／類別識別字、腳本檔名>

## Proposed outcome
<方向與解法形狀>

## Acceptance
1. <做完後我可以…；每條可被盲跑證明>

## Constraints
- <…>

## Value case
<可選；product 的 GO/NO-GO 與理由>

## Out of scope
- <…>

## Open questions
- <…>                     # 沒有就寫 `- none`：這一段必填，空的會被 intent.schema 擋
