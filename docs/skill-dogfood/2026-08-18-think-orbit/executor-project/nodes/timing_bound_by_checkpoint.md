---
id: timing_bound_by_checkpoint
type: CLAIM
seq: 9
summary: 幾週內的決定實際上被 Part 1 檢查點綁住，檢查點之前只能決定「要不要準備」，不能決定「接」
status: current
inputs:
  - {ref: start_after_checkpoint, load_bearing: true}
  - {ref: loom_trail_goal, load_bearing: false}
---
條目的 start 條件已經寫死在檢查點 go 之後。若檢查點沒過或 schema 大改，render 的輸入形狀就會變，現在接等於接一個會動的目標。所以幾週內能下的判斷是「檢查點過了要不要接」，而不是「現在就接」。
