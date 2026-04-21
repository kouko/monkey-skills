---
title: Axis Extreme Voice Anchors — cross-language
tier: 2
---

# Axis Extreme Voice Anchors

**Load scope**: Phase 6 Pass 3 AXIS EXTREME branch, when `voice_quadrant.position` starts with `axis-*`. Single cross-language file — each axis position lists anchors across EN / JP / zh-TW together since the underlying register concept is culturally universal (though surface execution requires native anchor).

**Status**: **MVP PLACEHOLDER — V2 research pending**. Current content is structural stub + candidate list; full corpus, primary sources, verbatim lines, voice signature dimensions to be populated in V2 research wave.

## Overview

Axis extremes are voices that sit **extreme on one axis while neutral on the other**. They genuinely don't fit any Q1-Q4 quadrant because they deliberately refuse one axis entirely. Uncommon (~5-10% of briefs) but valuable for edge cases.

Four axis extremes:

1. **Authority-extreme / Reason-Emotion neutral** — pure institutional voice that refuses both argumentation AND emotion (BBC News, Supreme Court decisions)
2. **Affinity-extreme / Reason-Emotion neutral** — pure peer voice that refuses both argumentation AND emotion (Mailchimp help center neutral mode, Reddit r/askhistorians)
3. **Reason-extreme / Authority-Affinity neutral** — pure analytical voice that refuses both institutional AND peer framing (Wikipedia, Stratechery analytical)
4. **Emotion-extreme / Authority-Affinity neutral** — pure emotional voice that refuses both institutional AND peer framing (Hallmark greeting cards, 昭和 CM お袋の味, cinematic MV VO)

Use case triggers: brief needs news reportage / documentation / emotional film voice / neutral documentation — where standard Q1-Q4 quadrant feels wrong-shaped.

## Landmark: axis-authority-extreme

Extreme institutional authority, Reason/Emotion neutral. Pure reportage / statement.

### Candidate anchors (V2 research)

- **EN**: BBC News VO register / Supreme Court decisions / FT Pink Paper / GOV.UK style
- **JP**: NHK ニュース9 reportage / 官邸声明 / 最高裁判決書
- **zh-TW**: 中央社 wire / 行政院聲明 / 最高法院判決

`<!-- V2 research needed: primary sources + verbatim lines + voice signature dimensions + over-mimic assessment -->`

## Landmark: axis-affinity-extreme

Extreme peer voice, Reason/Emotion neutral. Pure peer-information / neutral help.

### Candidate anchors (V2 research)

- **EN**: Mailchimp help center neutral mode / Reddit r/askhistorians peer-expert / StackOverflow top-answer voice
- **JP**: (gap — research candidate: 楽天 seller neutral Q&A / はてな知識系)
- **zh-TW**: (gap — research candidate: 批踢踢 資料串 / Dcard 冷知識小編)

`<!-- V2 research needed -->`

## Landmark: axis-reason-extreme

Extreme analytical, Authority/Affinity neutral. Pure logic / documentation register.

### Candidate anchors (V2 research)

- **EN**: Wikipedia article voice / Stratechery analytical mode / The Atlantic analytical essay
- **JP**: はてな科学 / ニコニコ大百科 / Wikipedia-ja formal entry
- **zh-TW**: 科學人雜誌 / 天下雜誌 analytical feature / 得到 App 知識產品 (CN 但 zh 通用)

`<!-- V2 research needed -->`

## Landmark: axis-emotion-extreme

Extreme emotion, Authority/Affinity neutral. Pure emotional / cinematic register.

### Candidate anchors (V2 research)

- **EN**: Hallmark greeting cards / Pixar opening-sequence VO / cinematic MV narration
- **JP**: 昭和 CM お袋の味 情感派 VO / TV ドキュメント涙誘い narration
- **zh-TW**: 電影 MV VO (侯孝賢-school) / 紀錄片情感旁白

`<!-- V2 research needed -->`

## V2 research triggers

Populate this file when any of:

1. Real brief triggers `voice_quadrant.position = axis-*` and fallback to Q1-Q4 quadrant produces wrong-shaped output
2. User explicitly requests BBC-news-voice / Hallmark-voice / Wikipedia-voice type anchors
3. Dedicated research cycle scheduled for axis-extreme expansion

## Cross-references

- [voice-anchor-meta-core.md](voice-anchor-meta-core.md) — schema applies uniformly; over-mimic mitigations for axis-extreme candidates to be added here when researched
- [voice-anchor-meta-detail.md](voice-anchor-meta-detail.md) — cross-culture label rubric; axis extremes fit poorly into the 19-label matrix (they are orthogonal to Q1-Q4), so separate classification may emerge from V2 research
