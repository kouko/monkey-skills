---
id: ruling_waits_for_checkpoint
type: CLAIM
seq: 13
summary: 兩條路已可比較，但裁決卡在 Part 1 檢查點；檢查點前唯一能做的是資料層前置的低成本 spike
status: current
inputs:
  - {ref: reuse_render_saves_a_renderer, load_bearing: true}
  - {ref: reuse_makes_loom_second_writer, load_bearing: true}
  - {ref: defer_keeps_four_carriers, load_bearing: true}
  - {ref: timing_bound_by_checkpoint, load_bearing: true}
---
接 render 的好處是省一個渲染器，代價是 loom 變第二寫端、且押在 inputs 形狀不改。不接的好處是不押注，代價是路徑繼續留在 transcript。兩邊的差額全繫在檢查點結果與 schema 是否大改，這正是 `part1_checkpoint_go` 那條假設。

所以這一坐的結論是開放問題，不是裁決。使用者說等檢查點跑完再說；屆時若 go，可先驗 `carriers_can_carry_inputs`（一次 spike 看四載體塞不塞得下 ref 清單），再回來決定接不接。
