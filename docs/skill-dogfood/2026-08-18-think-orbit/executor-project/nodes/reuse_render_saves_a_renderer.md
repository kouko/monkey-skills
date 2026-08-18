---
id: reuse_render_saves_a_renderer
type: CLAIM
seq: 10
summary: 走「接 render」路線，loom 只需供資料，不必再養第五個渲染器
status: current
branch: b_reuse_render
branch_type: exclusive
inputs:
  - {ref: render_question_is_downstream, load_bearing: true}
  - {ref: proposed_shape_no_type_port, load_bearing: true}
  - {ref: gap_is_data_not_renderer, load_bearing: false}
---
`dag.py render` 已存在、決定性、只讀 frontmatter。loom 若把四載體的決策寫成帶 `inputs` 的節點形狀，render 直接可畫，loom 不需要新的圖程式。BACKLOG 條目的提議形狀就是這條路，且明確排除移植 think-orbit 的四種節點型別。
