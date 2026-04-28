# Voice Anchor E2E Tests

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

用來驗證 Phase 6 Pass 3 Register Signal branch 在 v1.3.3 native-vocabulary anchor 下實際能 end-to-end 運作的 test harness。

## 待測 gap

v1.3.0 → v1.3.3 出貨了 15 個 anchor standards + Pass 3 3-tier 重構 + Gate Dimension 6, 但我們從未把真實的 brief 跑過 pipeline。下方的 test 是第一輪實證檢查。

## Test 配置

- `test-01-jp-q3-center.md` — JP Q3 center brief + 預期 native vocab
- `test-02-zh-q3-center.md` — zh-TW Q3 center brief + 預期 native vocab
- `test-03-zh-q2-extreme-leak.md` — 刻意洩漏的 王家衛 mimicry draft, 用來測 Gate Dimension 6
- `test-04-ab-v1.3.2-vs-v1.3.3.md` — 同一 brief 上的 A/B 比較

## 方法

每個 test 啟動一個 sonnet `copywriter` agent（gate test 則用 opus `copywriter-evaluator`）, 帶上：
- Phase 6 SKILL.md 的 Pass 3 Register Signal 指示
- 相關的 anchor 檔
- 模擬 Phase 6 進入點的預建 envelope

觀察項目：
1. Agent 是否載入正確的 anchor？
2. Rationale 是否引用 native vocabulary bullet？
3. `tone_notes.register_signal_applied` 結構是否正確？
4. （Gate）Dimension 6 是否抓到洩漏？

## 通過門檻（最低標準）

- [ ] Test 01：rationale 至少引用 {「真打ち」、「ト書」、「無駄な言葉がない」、「懐かしさと哀愁」} 中 2 項
- [ ] Test 02：rationale 至少引用 {「氣口」、「講古式敘事」、「台語口白」、「庶民聲口」} 中 2 項
- [ ] Test 03：Gate Dimension 6 回傳 🔴 Fatal, 並參照 meta-core 王家衛 mitigation
- [ ] Test 04：v1.3.3 的 rationale 嚴格比 v1.3.2 更 native-vocab-rich（量化方式：計算 domain-term mention 次數）
