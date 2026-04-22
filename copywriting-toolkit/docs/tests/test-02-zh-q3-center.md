# Test 02 — zh-TW Q3 center (Register Signal branch)

## Brief

Taiwan local drink brand (假想「老蘇打」台灣古早味汽水)，針對 25-45 歲台灣人懷舊情感的廣告 body copy，brand voice 要台味、peer-warm、不要文青腔。Mid-form ~150 字。

## Envelope fed to Phase 6 agent

```json
{
  "phase": "phase-5-voice-positioned",
  "form": "mid-form",
  "brief": {
    "output_language": "zh-TW",
    "voice_reference": null,
    "product": "老蘇打台灣古早味汽水 (hypothetical)",
    "audience": "25-45歲台灣人、懷舊情感",
    "tone_desired": "台味、peer-warm、不要文青腔",
    "form_hint": "mid-form ~150字"
  },
  "message_thesis": "古早味不是懷舊，是我們今天還在過的日常",
  "voice_quadrant": {
    "primary": "Q3",
    "edge": null,
    "position": "center",
    "rationale": "Phase 5: Affinity × Emotion center — 「台味 + 不要文青腔」rules out Q2 aspirational manifesto (許舜英/李欣頻 register); Q3 center captures peer-warm 庶民 voice",
    "schwartz_alignment": "ok"
  },
  "draft": "阿嬤家的冰箱，最下層永遠有一瓶冰冰的汽水。不是什麼特別的日子，就是想喝。現在長大了，走進便利商店還是會找那個熟悉的瓶身。老味道沒有變，變的是我們。但喝下去的那一口，還是把我們拉回小時候那個熱得要命的下午。",
  "next_stage": "copywriting-voice-tone-stage"
}
```

## Expected Pass 3 load

- voice_reference ∉ ZH craft-gate masters (許舜英/李欣頻/葉明桂) → NOT Craft Gate
- position == "center" → NOT Axis Extreme
- Falls into **Tier 2 Register Signal**
- Load: meta-core + meta-detail + `zh-q3-anchors.md §Landmark: center`
- Cross-ref: zh-TW Q3 center → JP STRONG per meta-detail → also load `jp-q3-anchors.md §Landmark: center`

## Expected native-vocab uptake

From `zh-q3-anchors.md §Landmark: center`, anchor candidates:
- 全聯 TV-era「經濟美學」/「格言體」(2006-2014)
- 吳念真 保力達B 系列「氣口」/「講古式敘事」
- 胡湘雲 大眾銀行 narrative-TVC「不平凡的平凡大眾」

Given brief emphasizes「台味、peer-warm、不要文青腔」— 吳念真 anchor is most fit.

Rationale should cite ≥2 of:
- 「氣口」(台語 CW 術語)
- 「講古式敘事」/「說故事而非說服」
- 「台語口白 / 台味」
- 「庶民聲口 / 阿伯阿嬸語境」
- 「勞動階級肉身感」

If rationale only says "peer-warm nostalgic register" without citing「氣口」or「講古」→ FAIL.

## Expected output

```json
"tone_notes": {
  "register_signal_applied": {
    "anchor_slug": "zh-tw-wu-nien-jen-taiyu-peer-intimate",
    "landmark_position": "center",
    "mitigation_clauses_applied": ["do not attempt 台語 reproduction; borrow 講古 structure + rural-peer stance only"],
    "native_critical_vocab_cited": ["氣口", "講古式敘事", "庶民聲口"]
  }
}
```

## Over-mimic mitigation sanity check

吳念真 mitigation: "do not attempt 台語 reproduction; borrow 講古 structure + rural-peer stance only"

Draft is in Mandarin, not 台語 — so mitigation clause applies vacuously (no 台語 to leak). Agent should still record the mitigation clause as "considered, not-fired" to show awareness.
