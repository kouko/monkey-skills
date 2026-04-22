# Test 01 — JP Q3 center (Register Signal branch)

## Brief

Japanese tea brand（伊藤園 hypothetical new canister product）launch copy，target 40-50 代女性、家族の朝の風景を想起させる。brand voice = 家庭的で温かい、押しつけがましくない。Long-form ~200 字 essay-style print ad body copy.

## Envelope fed to Phase 6 agent

```json
{
  "phase": "phase-5-voice-positioned",
  "form": "mid-form",
  "brief": {
    "output_language": "ja",
    "voice_reference": null,
    "product": "伊藤園お茶 (hypothetical)",
    "audience": "40-50代女性、家族あり",
    "tone_desired": "家庭的で温かい、押しつけがましくない",
    "form_hint": "print essay body copy ~200字"
  },
  "message_thesis": "毎朝のお茶は、家族の風景の一部",
  "voice_quadrant": {
    "primary": "Q3",
    "edge": null,
    "position": "center",
    "rationale": "Phase 5: Affinity × Emotion center — warm-domestic register best fits 40-50代 family-oriented reader; avoids aspirational manifesto (Q2) and peer-practical (Q4)",
    "schwartz_alignment": "ok"
  },
  "draft": "朝、まだ誰も起きていないキッチンで、お湯を沸かす音だけが聞こえる。いつもの急須、いつもの茶葉。忙しい一日が始まる前の、たった五分間。お茶を淹れる時間は、一日のうちで一番静かな時間かもしれない。家族が起きてきて、それぞれのマグカップに注ぐとき、この五分間が家族みんなの朝を支えていることを思い出す。",
  "next_stage": "copywriting-voice-tone-stage"
}
```

## Expected Pass 3 load

Per SKILL.md Pass 3 activation guard:
- voice_reference ∉ JP craft-gate masters → NOT Craft Gate
- voice_quadrant.position is "center", not "axis-*" → NOT Axis Extreme
- Falls into **Tier 2 Register Signal branch**
- Load: `voice-anchor-meta-core.md` + `voice-anchor-meta-detail.md` + `jp-q3-anchors.md §Landmark: center`
- Cross-ref check: JP Q3 center → zh-TW STRONG per meta-detail → also load `zh-q3-anchors.md §Landmark: center`

## Expected native-vocab uptake in rationale

From `jp-q3-anchors.md §Landmark: center`, anchor candidates:
- 向田邦子「真打ち」(Q3 center canonical peer-warm voice)
- 坂元裕二「言葉の魔術師」

Rationale should cite ≥2 of:
- 「真打ち」(向田 self-describing signature)
- 「ト書を拡張した文体」/ 「脚本家のト書き的簡潔さ」(高橋行徳評)
- 「情景が鮮やかに浮かぶ / 無駄な言葉がない」(文春書評定型)
- 「懐かしさと哀愁をまとった温かい言葉」

If rationale only says "domestic-intimate, warm peer register" without citing native critical terms → FAIL (English-translation residue).

## Structured output expected

```json
"tone_notes": {
  "register_signal_applied": {
    "anchor_slug": "jp-mukoda-kuniko-shinuchi-zuihitsu",
    "landmark_position": "center",
    "mitigation_clauses_applied": [],
    "native_critical_vocab_cited": ["真打ち", "ト書", "無駄な言葉がない"]
  },
  "lineage_applied": null,
  "axis_extreme_applied": null
}
```
