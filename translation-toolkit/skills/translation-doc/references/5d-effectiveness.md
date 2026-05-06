# 5D Reflection — Effectiveness (transcreation only)

**Status**: canonical reference (Single Source of Truth in `scripts/canonical/`; functional copies in active skills' `references/`)
**Cross-refs**: [`4d-reflection.md`](4d-reflection.md), [`core-loop.md`](core-loop.md), [`orthogonal-axes.md`](orthogonal-axes.md), [`verification-gates.md`](verification-gates.md)

---

## When this axis applies

The Effectiveness axis is **only used when `mode == transcreation`** (see [`orthogonal-axes.md`](orthogonal-axes.md)). In transcreation mode, the REFLECT output is a **5-axis JSON** (4D from [`4d-reflection.md`](4d-reflection.md) plus this 5th axis); in literal / faithful / localized modes, it is the standard 4-axis JSON.

Why a separate axis: transcreation is **re-creation in the target culture for the same persuasive intent**. Surface deviation is expected and desirable; the question shifts from "is the meaning preserved?" (Accuracy) and "does it read natural?" (Fluency) to **"does it persuade the same way the source persuades?"** That question fits poorly under Accuracy or Style — hence its own axis, gated to transcreation mode so it does not pollute fidelity-focused modes.

---

## Axis 5 — Effectiveness

**Definition**: persuasion intent preserved in target culture.

**Concerns**:

- **Cultural-reference fail** — source pun, idiom, allusion, or meme lost in target without local replacement
  - Example: source "Got Milk?" rendered as 「牛乳ありますか？」 — literal but loses the iconic-campaign register; equivalent JP campaign hook is needed
  - Example: source "I'm lovin' it" rendered as a flat 「私はそれが大好きです」 — slogan rhythm and possessive-progressive playfulness gone
- **CTA strength dilution** — call-to-action verb intensity downgraded
  - Example: "Buy now" → 「ご検討ください」 (over-polite, kills urgency); should be 「今すぐ購入」 or culture-appropriate equivalent
  - Example: "Limited time" → 「期間が限られています」 (descriptive, not urgent); should be 「今だけ」 / 「期間限定」
- **Emotional pull mismatch** — source's emotional register (excitement / fear / aspiration / nostalgia) flattened or shifted
  - Example: source aspirational "Reach for it" rendered as 「届こう」 (literal) instead of 「夢に向かって」 / 「目指せ」 (culturally resonant aspiration)
- **Target-culture taboo violation** — target has cultural / linguistic taboo source had no reason to consider
  - Example: ja-JP marketing using "4" (四 / し ≈ 死) in a sale price ("4,440 円 限定！") — neutral in source culture, unlucky in JP
  - Example: zh-TW / zh-CN gift copy invoking clocks (送鐘 / 送終 homophone)
  - Example: number / color associations differ (white = mourning in some East Asian contexts vs purity in Anglo)
- **Brand-voice drift** — brand's established voice (warm / authoritative / playful) lost when crossing cultures
  - Example: a brand that says "We get you" in EN rendered as 「弊社はお客様のことを理解しております」 (over-formal, brand-foreign); should be 「あなたのことを、わかってる」
- **Anchor-figure / reference substitution missed** — source uses a culture-anchor (author / framework / celebrity) that needs target-locale equivalent
  - Example: source EN copy invoking "Steve Jobs said..." may need substitution with target-culture business-anchor when the cultural weight of the anchor is the load-bearing element (NOT when the source intent is literally to quote Jobs himself)
  - Example: ja marketing reference 神田昌典 PASONA framework — when translating to en-US, the framework can be preserved as PASONA (recognized term in DR-marketing circles) but the **authority claim** "as 神田 teaches us" needs replacement with a target-locale authority figure
- **Genre-convention mismatch** — target-culture marketing genre conventions differ
  - JP direct-response copy convention: long-form, story-driven, testimonial-heavy, multiple CTAs
  - en-US DR copy convention: punchy headlines, scannable bullets, single dominant CTA
  - zh-TW retail conventions: price-anchor + scarcity + social proof
  - Translating EN punchy headlines verbatim into JP often misses the genre's "short" expectation in JP — JP catchy headlines run 7–15 chars
- **Phonetic / rhythm element lost** — source uses rhyme, alliteration, syllable-count rhythm as a persuasive element
  - Example: "Snap, Crackle, Pop" — rhythm IS the brand; literal target loses the brand entirely
  - Example: 7-7-5 rhythm of JP catch-copy not preserved when translating JP → ZH
- **Number / claim hedging shift** — "save 50%" preserved as a number in target, but target culture expects different framing
  - Example: en-US "save 50%" lands well; ja-JP shoppers respond more to 「半額」 than 「50% OFF」 in some contexts; zh-TW 「五折」 is the colloquial expectation
  - The numeric claim is the same; the surface framing differs

---

## Output format

Append `effectiveness` to the 4D JSON when `mode == transcreation`:

```json
{
  "accuracy":      [...],
  "fluency":       [...],
  "style":         [...],
  "terminology":   [...],
  "effectiveness": [
    {"issue": "CTA 'Buy now' rendered as 「ご検討ください」 — over-polite, kills urgency",
     "suggestion": "use 「今すぐ購入」 or 「いますぐ手に入れる」"},
    {"issue": "anchor 'as Steve Jobs said' preserved verbatim — JP audience won't carry the same authority weight here (this is a generic motivational claim, not a Jobs quote)",
     "suggestion": "substitute with target-locale business-anchor or rephrase as authority-neutral"}
  ]
}
```

Empty array `[]` is valid and indicates "no effectiveness concerns on this chunk".

---

## Concrete example (en-US → ja-JP transcreation)

**Source**:
> Stop wasting time. Get organized in 5 minutes. Try Notion free.

**Faithful-mode draft** (would be flagged in transcreation):
> 時間を無駄にしないでください。5分で整理整頓しましょう。Notion を無料でお試しください。

**Effectiveness critique**:
```json
{
  "effectiveness": [
    {"issue": "'Stop wasting time' as 「時間を無駄にしないでください」 is grammatically polite but rhetorically flat — JP marketing for productivity tools opens with empathy or a pain-question, not an imperative",
     "suggestion": "rework opening as pain-question: 「もう、時間に追われない。」 or 「『時間がない』を、終わりにする。」"},
    {"issue": "'Get organized in 5 minutes' as 「5分で整理整頓しましょう」 — 整理整頓 reads as housework / KonMari, not productivity",
     "suggestion": "use 「5分で、仕事が整う。」"},
    {"issue": "CTA 'Try Notion free' as 「無料でお試しください」 — passive, expected, low conversion; JP DR convention favors imperative + benefit reminder",
     "suggestion": "「いますぐ無料で始める」 or 「30秒で、無料登録。」"}
  ]
}
```

**Transcreation v2** (after IMPROVE):
> 「時間がない」を、終わりにする。
> Notion なら、5分で仕事が整う。
> いますぐ無料で始める。

The v2 deviates substantially from the source surface (a M1-only check would flag the divergence as concerning). The S1 back-translation gate for transcreation uses a relaxed cosine-similarity threshold of 0.70 (vs 0.85 for faithful) precisely to allow this kind of deviation while still catching outright topic drift. See [`verification-gates.md`](verification-gates.md) §S1.

---

## Anti-patterns

- **Treating Effectiveness as a license to invent**. Effectiveness is faithful to **persuasive intent**, not free-form. If the source promises "save 50%", the target may say 「半額」 but cannot say 「無料」.
- **Substituting culture-anchors when the source intent is the literal quote**. "Steve Jobs once said, 'Stay hungry, stay foolish'" — the entire point is to quote Jobs. Substituting with 「松下幸之助は言った」 is wrong here. Substitute only when the source uses the anchor as load-bearing authority decoration, not as the literal quoted source.
- **Treating literal/faithful modes as Effectiveness-eligible**. The 5th axis appears only in transcreation mode. Critics in other modes should resist the temptation to grade persuasion — that is out of scope and bleeds into Style.
- **Brand-voice changes without brand brief**. If the intake provides a brand brief, follow it. If not, conservative Effectiveness suggestions stay grounded in source rather than imagined-target voice.
