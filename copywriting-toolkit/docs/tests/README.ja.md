# Voice Anchor E2E Tests

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

Phase 6 Pass 3 Register Signal branch が v1.3.3 native-vocabulary anchor で実際に end-to-end で動作することを検証するための test harness。

## 検証する gap

v1.3.0 → v1.3.3 で 15 個の anchor standards + Pass 3 3-tier リファクタ + Gate Dimension 6 を出荷したが、これまで実際の brief を pipeline に通したことがなかった。以下の test が最初の実証チェック。

## Test 構成

- `test-01-jp-q3-center.md` — JP Q3 center brief + 期待される native vocab
- `test-02-zh-q3-center.md` — zh-TW Q3 center brief + 期待される native vocab
- `test-03-zh-q2-extreme-leak.md` — 意図的にリークした 王家衛 mimicry draft、Gate Dimension 6 検証用
- `test-04-ab-v1.3.2-vs-v1.3.3.md` — 同じ brief での A/B 比較

## 方法論

各 test では sonnet `copywriter` agent（gate test では opus `copywriter-evaluator`）を以下を付けて起動する：
- Phase 6 SKILL.md の Pass 3 Register Signal 指示
- 該当する anchor ファイル
- Phase 6 entry をシミュレートする事前構築 envelope

観察項目：
1. agent は正しい anchor をロードするか？
2. rationale は native vocabulary bullet を引用するか？
3. `tone_notes.register_signal_applied` は正しく構造化されるか？
4. （gate）Dimension 6 はリークを捕捉するか？

## 成功基準（最低ライン）

- [ ] Test 01：rationale が {「真打ち」、「ト書」、「無駄な言葉がない」、「懐かしさと哀愁」} のうち少なくとも 2 つを引用
- [ ] Test 02：rationale が {「氣口」、「講古式敘事」、「台語口白」、「庶民聲口」} のうち少なくとも 2 つを引用
- [ ] Test 03：Gate Dimension 6 が 🔴 Fatal を返し、meta-core 王家衛 mitigation を参照する
- [ ] Test 04：v1.3.3 の rationale が v1.3.2 よりも厳密に native-vocab-rich（定量化：domain-term mention の出現回数を数える）
