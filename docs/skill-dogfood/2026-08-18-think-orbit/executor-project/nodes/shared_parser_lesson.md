---
id: shared_parser_lesson
type: FACT
seq: 6
summary: 同一檔案格式的讀寫兩端必須共用同一個 parser，否則寫端會靜默 no-op
status: current
source: sources/a-reader-and-writer-over-one-file-format-must-share-one-parser.md（loom memory practice）
quote: "reader and writer must call one shared span/parse routine, and a writer that cannot locate its target must fail loud, never return quietly"
inputs: []
---
這條教訓來自 think-orbit Part 1 的 whole-branch review：loader 容忍的分隔線寫法，`break` 的 rewriter 不認，結果 `check` 過、`break` 印 stale 但假設沒改。它跟本題相關，因為 loom 若成為 think-orbit 格式的第二個寫端，就是同樣的讀寫分家形狀。
