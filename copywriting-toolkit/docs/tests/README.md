# Voice Anchor E2E Tests

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

Test harness to validate Phase 6 Pass 3 Register Signal branch actually works end-to-end with v1.3.3 native-vocabulary anchors.

## Gap being tested

After v1.3.0 → v1.3.3 shipped 15 anchor standards + Pass 3 3-tier refactor + Gate Dimension 6, we never ran a real brief through the pipeline. Tests below are the first empirical check.

## Test layout

- `test-01-jp-q3-center.md` — JP Q3 center brief + expected native vocab
- `test-02-zh-q3-center.md` — zh-TW Q3 center brief + expected native vocab
- `test-03-zh-q2-extreme-leak.md` — deliberately-leaky 王家衛 mimicry draft for Gate Dimension 6
- `test-04-ab-v1.3.2-vs-v1.3.3.md` — A/B comparison on same brief

## Methodology

Each test launches a sonnet `copywriter` agent (or opus `copywriter-evaluator` for gate tests) with:
- Phase 6 SKILL.md Pass 3 Register Signal instructions
- The relevant anchor file(s)
- A pre-built envelope simulating Phase 6 entry

Observe:
1. Does the agent load the correct anchor?
2. Does the rationale cite native vocabulary bullets?
3. Does `tone_notes.register_signal_applied` get structured correctly?
4. (Gate) Does Dimension 6 catch leaks?

## Success criteria (minimum bar)

- [ ] Test 01: rationale cites at least 2 of {「真打ち」, 「ト書」, 「無駄な言葉がない」, 「懐かしさと哀愁」}
- [ ] Test 02: rationale cites at least 2 of {「氣口」, 「講古式敘事」, 「台語口白」, 「庶民聲口」}
- [ ] Test 03: Gate Dimension 6 returns 🔴 Fatal with reference to meta-core 王家衛 mitigation
- [ ] Test 04: v1.3.3 rationale is strictly more native-vocab-rich than v1.3.2 (quantify: count domain-term mentions)
