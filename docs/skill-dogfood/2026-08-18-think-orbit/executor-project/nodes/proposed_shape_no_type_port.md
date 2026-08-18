---
id: proposed_shape_no_type_port
type: FACT
seq: 4
summary: 條目提議四載體共用一個 inputs 欄位並重用 dag.py render，但不移植 GOAL／FACT／CLAIM／DECISION 型別
status: current
source: sources/2026-08-18-loom-decision-trail-as-dag-view-via-think-orbit-render.md §Proposed minimal shape
quote: "Do NOT port think-orbit's GOAL/FACT/CLAIM/DECISION node types onto loom decisions: the granularity differs (one inference vs one decision/requirement/task) and the 2026-08-18 double-blind experiment showed richer taxonomies collapse agreement."
inputs: []
---
提議的最小形狀是給四種載體一個共用的「踩在什麼上面」欄位，工作名 `inputs`，鏡射 think-orbit 節點的 `inputs: [{ref, load_bearing}]`。視圖則直接重用 think-orbit 的 `dag.py render`，讓 think-orbit 變成 loom 的觀看面。條目自己標明這是「to brainstorm, not decided」，不是定案。
