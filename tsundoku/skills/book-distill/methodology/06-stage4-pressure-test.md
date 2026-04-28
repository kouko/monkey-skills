# Stage 4 — Adversarial pressure test

## Goal

Before shipping a skill, validate it on a test prompt battery to verify
**activation precision** AND **post-activation output quality**.

Failures are not patched at the surface (don't just tweak `description`).
Failures send the skill back to Stage 2 for A2 / E / B revision.

## Why it's mandatory

A2 (trigger) is the hardest part of skill design. A beautifully-written
skill with a sloppy trigger is invisible — the agent never invokes it,
or invokes it on the wrong cue.

**Pressure testing is the only way to catch trigger problems pre-ship.**

## test-prompts.json schema (forward-compatible with darwin-skill format)

```json
{
  "skill": "inversion-thinking",
  "version": "0.1.0",
  "source_book": "Poor Charlie's Almanack — Charlie Munger",
  "test_cases": [
    {
      "id": "should-trigger-01",
      "type": "should_trigger",
      "prompt": "I'm deciding whether to take this new project. I keep listing benefits but it doesn't add up.",
      "expected_behavior": "Activate inversion-thinking; ask 'what would make this fail?'",
      "notes": "positive scenario: decision wrestling"
    },
    {
      "id": "should-not-trigger-01",
      "type": "should_not_trigger",
      "prompt": "Look up the parameters for this API.",
      "expected_behavior": "Pure information lookup; no decision skill should fire.",
      "notes": "lure: information lookup"
    },
    {
      "id": "edge-01",
      "type": "edge_case",
      "prompt": "I'm wondering what to have for dinner.",
      "expected_behavior": "Daily trivia; should NOT fire (despite the surface 'decision' word).",
      "notes": "boundary: distinguishes serious decisions from daily picks"
    }
  ]
}
```

## Three test categories — all required

| Type | Min count | Purpose |
|---|---|---|
| `should_trigger` | 3 | Does it fire when it should? |
| `should_not_trigger` (lure) | 2 | Does it abstain when it shouldn't fire? |
| `edge_case` | 1 | Reasonable judgment on ambiguous boundary cases? |

**A skill without lure tests is not allowed to ship.** Positive-only
testing makes every skill look brilliant in QA but lights up wrong on
deployment.

## Execution flow

1. For each skill, populate `test-prompts.json` from the template.
2. Run each test case as an independent activation judgment: feed the
   prompt to a fresh Claude context with the skill loaded, and ask "would
   this skill activate? give the reasoning."
3. Compute pass rate:
   - **100% pass** → ship
   - **≥80% pass** → analyze failures; decide fix-skill vs. fix-test
     (be skeptical of fix-test — risk of self-justification)
   - **< 80% pass** → **must redo Stage 2 A2 / E / B**, not surface
     patches
4. Re-run after fixes until threshold met.

## Decide: fix the skill, or fix the test?

- **Fix the skill** if: the failure exposes ambiguity in the trigger
  description, or the failure is a legitimate scenario the original
  A2 missed
- **Fix the test** if: the failure is a lure case you designed to be
  unfair / pathological. **Document the reasoning**; do not silently
  remove tests.

## Output

- `<skill-dir>/test-prompts.json` — darwin-compatible format
- `<skill-dir>/test-results.md` — pass rate + failure analysis (audit
  trail; required for the user to inspect later)

## Output language

- `test-prompts.json` content (`prompt`, `expected_behavior`, `notes`) —
  match source book language (so test prompts read like real user
  queries in that language)
- `test-prompts.json` field names — English (machine-parseable)
- `test-results.md` body — match source book language for prompt
  reproduction; English for analysis sections (engineer-facing)

## Hand-off note

After all skills pass, report to the user:

> Distillation complete. <N> skills shipped. To enable continuous
> evolution, feed `<distill-dir>/` to a darwin-style ratcheting tool
> (separate concern; not part of `book-distill`).

## Trilingual glossary (Stage 4 — adversarial pressure test)

| English | 日本語 | 繁體中文 | Note |
|---|---|---|---|
| trigger / activation | トリガー条件 / 発動条件 | 觸發條件 | Google/MS official zh-tw |
| adversarial test | 敵対的テスト | 對抗式測試 | NIST IR 8269 邦訳 / NTU 計中 |
| stress / pressure test | ストレステスト | 壓力測試 | NOT 圧力テスト = mechanical |
| lure / distractor | 錯乱肢 / おとり | 誘答選項 / 干擾項 | educational measurement: 誘答 (TW MCQ) / 干擾項 (Cambridge zh-tw) |
| edge case | エッジケース | 邊緣案例 | NOT 境界条件 (= BVA testing technique) |
| sanity check | サニティチェック | 合理性檢查 | NOT 妥当性確認 (= ISO validation) |
| ground truth | 正解データ | 標準答案 / 真實標籤 | NOT 真値 (= metrology) / NOT 基準真相 (calque) |
| ship gate / release criteria | リリース基準 / 品質ゲート | 發布條件 / 品質關卡 | Stage-Gate / Azure DevOps register |
| ratcheting | ラチェット式 | 棘輪式 | progressive evolution metaphor |
| regression test | リグレッションテスト / 回帰テスト | 迴歸測試 | well-established |
| fix-skill / fix-test | スキル修正 / テスト修正 | 修正 skill / 修正測試 | |
