---
id: defer_keeps_four_carriers
type: CLAIM
seq: 12
summary: 走「不接、先不動工」路線，四載體維持現狀，決策路徑繼續靠 transcript 與人工翻檔
status: current
branch: b_defer
branch_type: exclusive
inputs:
  - {ref: render_question_is_downstream, load_bearing: true}
  - {ref: timing_bound_by_checkpoint, load_bearing: true}
  - {ref: four_carriers_no_edge, load_bearing: false}
---
不動工的成本是已知的：三週後要開四種檔案，路徑在 transcript 裡。好處是不在檢查點之前押注一個可能改形的 schema，也不必現在就替四載體設計 `inputs` 欄位。這條路和「接 render」互斥，因為前者的第一步就是替載體長邊。
