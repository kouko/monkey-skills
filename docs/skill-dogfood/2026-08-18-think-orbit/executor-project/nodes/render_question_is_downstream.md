---
id: render_question_is_downstream
type: CLAIM
seq: 8
summary: 「要不要接 render」是下游問題，真正的前置工作是給四種載體一個機器可讀的 inputs 欄位
status: current
inputs:
  - {ref: loom_trail_goal, load_bearing: true}
  - {ref: four_carriers_no_edge, load_bearing: true}
  - {ref: gap_is_data_not_renderer, load_bearing: true}
  - {ref: decision_log_shape, load_bearing: false}
---
render 只是把 frontmatter 裡的 `inputs` 邊畫出來。四種載體今天沒有任何一個帶這種邊，Decision Log 甚至連 id 都沒有。所以不管最後選哪個觀看面，「先有邊」都是必要條件；接 render 本身不會產生邊。

這也表示問題可以拆成兩層。第一層是資料層：四載體要不要長 `inputs`，這一層不依賴 think-orbit。第二層才是觀看面：有了邊之後，用 think-orbit 的 render 看，還是 loom 自己畫。
