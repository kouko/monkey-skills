# Test 03 — Gate Dimension 6 leak detection (王家衛 mimicry)

## Scenario

A draft produced by Phase 4 + tuned by Phase 6 Pass 1+2 but with clear 王家衛 mimicry leak (expiration imagery / countdown / can metaphor — all three explicit mitigations in meta-core registry). Feed to copywriter-evaluator with voice-consistency-gate rubric. Expect 🔴 Fatal on Dimension 6.

## Envelope fed to copywriter-evaluator

```json
{
  "phase": "phase-6-toned",
  "form": "mid-form",
  "brief": {
    "output_language": "zh-TW",
    "voice_reference": null,
    "product": "精品腕錶 (hypothetical)",
    "audience": "都會男性 35-50",
    "tone_desired": "浪漫、電影感、時間的重量"
  },
  "message_thesis": "時間是愛情的見證",
  "voice_quadrant": {
    "primary": "Q2",
    "edge": null,
    "position": "extreme",
    "rationale": "Phase 5: Authority × Emotion extreme — 浪漫、電影感 + 都會 register → aphoristic-density extreme (朱家鼎/王家衛 cluster)",
    "schwartz_alignment": "ok"
  },
  "draft": "如果記憶是一罐罐頭，我希望這罐永遠不會過期。如果愛情有保存期限，我希望是一萬年。時間在走，她在等。一萬年太久，我們只爭朝夕。有些事情，過了今夜，就再也回不去了。",
  "tone_notes": {
    "register_signal_applied": {
      "anchor_slug": "zh-hk-wong-kar-wai-monologue-fragment-temporal",
      "landmark_position": "extreme",
      "mitigation_clauses_applied": []
    },
    "lineage_applied": null,
    "axis_extreme_applied": null
  },
  "next_stage": "copywriting-ethics-check-stage"
}
```

## What should fire on Dimension 6 (Over-Mimic Adherence)

Per `rubrics/voice-consistency-gate.md §Dimension 6` + `voice-anchor-meta-core.md §Over-Mimic Mitigation Registry`:

王家衛 entry in registry lists mitigation: "no expiration imagery / no countdowns / no cans / no step-printing"

Draft violates ALL FOUR tropes:
1. **罐頭 / 罐子**: 「記憶是一罐罐頭」— canonical 重慶森林 leak
2. **過期 / 保存期限**: direct 重慶森林 expiration imagery
3. **一萬年**: 2046 / 東邪西毒 countdown trope
4. **過了今夜**: temporal countdown / step-printing cadence

Expected verdict: **🔴 Fatal** with all 4 cited + `next_action: rewrite Pass 3 output, load alternate Q2-extreme anchor (朱家鼎「天長地久三部曲」or axis-emotion-extreme candidate)`.

If verdict is 🟡 Warning or 🟢 Clear → Gate Dimension 6 is not actually operational → TEST FAILURE.

If verdict is 🔴 but rationale doesn't cite meta-core registry → partial pass (detected leak but not via proper registry lookup).
