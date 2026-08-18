---
id: reuse_makes_loom_second_writer
type: CLAIM
seq: 11
summary: 接 render 的代價是 loom 變成 think-orbit 檔案格式的第二個寫端，讀寫必須共用 loader
status: current
branch: b_reuse_render
branch_type: exclusive
inputs:
  - {ref: reuse_render_saves_a_renderer, load_bearing: true}
  - {ref: shared_parser_lesson, load_bearing: true}
---
render 讀的是 think-orbit 的 frontmatter 契約。loom 的 brief／plan／commit 若各自寫這種節點，就是同一格式多了幾個寫端。Part 1 的教訓是讀寫兩端不共用 parser 就會靜默 no-op，所以這條路的技術前提是 loom 端經由 dag.py 的 loader 或同一份 schema 寫入，不能各自用 regex 拼。
