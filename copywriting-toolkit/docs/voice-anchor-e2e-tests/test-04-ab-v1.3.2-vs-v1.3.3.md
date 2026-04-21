# Test 04 — A/B v1.3.2 vs v1.3.3 anchor file

## Hypothesis

v1.3.3 native-vocabulary rewrite should produce Pass 3 rationale with **strictly more native critical vocabulary mentions** than v1.3.2 (which had English-structure-with-native-names).

## Method

Use the zh-q3 brief from Test 02. Dispatch two `copywriter` agents in parallel:

- **Arm A (v1.3.2)**: fed the v1.3.2 `zh-q3-anchors.md` from `git show c584d0f:...`
- **Arm B (v1.3.3)**: fed the current HEAD `zh-q3-anchors.md`

Both agents receive identical Phase 6 SKILL.md Pass 3 Register Signal instructions and identical envelope. Only the anchor file content differs.

## Metric

Count occurrences of native critical terms in each rationale:
- Native vocab set: {「氣口」, 「講古式敘事」, 「庶民聲口」, 「台語口白」, 「阿伯阿嬸語境」, 「勞動階級肉身感」, 「講古」, 「台味」}
- English-structure-only terms: {"peer-warm", "domestic-intimate", "rural-peer stance", "台語 peer-intimate register"}

Expected:
- Arm A (v1.3.2) rationale: majority English-structure terms, minimal native critical vocab
- Arm B (v1.3.3) rationale: cites multiple native critical vocab terms

## Success criterion

v1.3.3 arm cites ≥3 native vocab terms; v1.3.2 arm cites ≤1 → rewrite was worth it.

If v1.3.2 arm already cites ≥3 native vocab terms → v1.3.3 rewrite may be over-engineered (LLM already surfaces these from context).

If v1.3.3 arm cites ≤1 native term → rewrite failed to reach Phase 6 output → needs re-investigation.
