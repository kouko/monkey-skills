# Brand brief intake — protocol

> Captured at Layer 2 step 1 of `translation-creative`. **Recommended for
> transcreation mode**; **optional for faithful mode** (faithful falls back
> to intake-spec `register` + `intent` when no brief is provided).
>
> The brief outputs land in the audit-trail `brand_brief` block and feed the
> WRITER prompt (Layer 3 DRAFT) so the draft honors brand archetype, voice
> axes, signature phrases, and do-not-say list from the first pass — not
> retroactively via REFLECT critique.

The brief is **captured**, not **generated**. Missing fields default to
"unspecified" and produce a WARN in transcreation mode rather than an
invented strategy (see SKILL.md §"What this skill does NOT do").

---

## Field 1 — Brand archetype

Pick one from the **Mark / Pearson 12 archetypes** (canonical reference for
brand-personality work):

| Archetype | Voice signature | Examples |
|---|---|---|
| **Hero** | courage, achievement, mastery | Nike, Adidas, Marines |
| **Sage** | wisdom, truth-seeking, expertise | Google, BBC, Harvard |
| **Outlaw** | rule-breaking, revolution, disruption | Harley-Davidson, Diesel, early Apple |
| **Lover** | intimacy, indulgence, sensuality | Victoria's Secret, Godiva, Häagen-Dazs |
| **Caregiver** | service, compassion, protection | Johnson & Johnson, UNICEF, Allstate |
| **Creator** | imagination, self-expression, craft | Lego, Adobe, Crayola |
| **Innocent** | optimism, simplicity, purity | Coca-Cola (classic), Dove, Method |
| **Explorer** | freedom, discovery, individualism | Patagonia, Jeep, The North Face |
| **Magician** | transformation, vision, charisma | Disney, Tesla, Apple (post-Jobs return) |
| **Ruler** | control, authority, prestige | Mercedes-Benz, Rolex, IBM |
| **Jester** | fun, irreverence, levity | Old Spice, Skittles, M&M's |
| **Everyman** | relatability, belonging, unpretentiousness | IKEA, Levi's, Budweiser |

**Format**: one archetype name. Optional secondary archetype if the brand
intentionally blends two (e.g., Patagonia = Explorer + Caregiver — Explorer
primary, Caregiver underlies the environmental positioning).

---

## Field 2 — Tone-of-voice spectrum

Pick **one position** on each of the three voice axes. If the brand brief
does not specify a position, import from intake-spec `register` (defaults
applied as marked):

| Axis | Left pole | Right pole | Neutral default |
|---|---|---|---|
| Authority | authoritative | playful | neither |
| Formality | formal | casual | neither |
| Warmth | warm | cool | neither |

**Format** (example):

```
authority: playful (3/5 toward playful)
formality: casual (2/5 toward casual)
warmth:    warm (4/5 toward warm)
```

The position number (1-5 toward the named pole) is informational; the
WRITER prompt receives the named pole + intensity. Numbers below 2 default
to "neither" — i.e., you cannot be "barely playful"; either declare the
brand playful or leave the axis neutral.

---

## Field 3 — Do-not-say list

Words / phrases the brand actively avoids. Five sub-categories:

1. **Banned commercial-tone words** — "cheap", "discount", "bargain", "sale"
   (typical for premium / luxury archetypes — Ruler, Lover, Magician).
2. **Banned competitor names** — exact strings: "Nike", "Adidas", etc. (for
   any brand that competes with named entities and wants to avoid even
   accidental mention).
3. **Banned jargon / technical terms** — terms that violate target-persona
   reading level. e.g., a consumer-finance brand banning "leverage",
   "derivatives", "alpha".
4. **Banned negative-framing words** — "fail", "broken", "lose" (typical
   for positive-framing brands — Caregiver, Innocent, Hero).
5. **Banned culturally-loaded terms** — context-specific. e.g., a JP
   marketing campaign banning "4" / 「四」 in price points (homophone
   死), or a zh marketing campaign banning "送鐘" / 送終 in gift copy.

**Format**: a flat list. Substring matching is case-insensitive but
respects word boundaries (avoid false positives on "cheaply" if "cheap"
is banned). Audit trail records every avoidance hit + the substituted
phrase the WRITER chose.

---

## Field 4 — Signature phrases

Words / phrases the brand uniquely **owns**. Three handling decisions per
phrase:

1. **Verbatim-preserve** — phrase ships in source form regardless of target
   locale. Examples: "Just Do It" (Nike, used as-is in JP / ZH markets),
   "Think Different" (Apple, similar treatment).
2. **Locale-transcreate** — phrase has a per-locale official rendering set
   by the brand (e.g., "I'm lovin' it" → 「i'm lovin' it」 in JP — verbatim
   English with brand-stylization preserved — but Spanish "Me encanta" is
   the official locale rendering).
3. **Decide-per-context** — no fixed rule; the WRITER chooses based on
   the surrounding copy and the intake-spec mode. Audit trail records the
   choice.

**Format** (example):

```
- "Just Do It"        → verbatim-preserve (all locales)
- "I'm lovin' it"     → locale-transcreate (per per-locale table below)
  - ja-JP: i'm lovin' it
  - es-MX: Me encanta
  - zh-TW: 我就喜歡
- "Better Together"   → decide-per-context
```

---

## Field 5 — Target persona

Who the copy is talking to. Five sub-fields:

1. **Age range** — e.g., 25-35, 60+. Defaults to "general adult" if
   unspecified.
2. **Region** — country / city / sub-region for cultural context. e.g.,
   "Tokyo metro area", "Taiwan north / 北部都會區", "US tier-1 cities".
3. **Life stage** — student / early-career / family-formation / empty-nest
   / retiree / etc. Drives reference choices and CTA framing.
4. **Cultural context** — relevant subculture or demographic (e.g.,
   "outdoor enthusiasts", "climbing community", "first-generation Asian-
   American", "JP 銀髪族 60+"). Drives idiom + reference choices.
5. **Reading level** — vocabulary band, used by the WRITER + the
   transcreation Effectiveness axis. e.g., "general public, no technical
   jargon", "industry-insider, technical OK".

**Format** (example): one block of comma-separated bullets matching the
five sub-fields. Missing sub-fields default to neutral and surface as a
WARN in transcreation mode.

---

## Field 6 — Call-to-action style

CTA verb intensity + framing, one of:

- **direct** — imperative, present tense, no hedging. "Buy now",
  「今すぐ購入」, "立即購買". Conversion-optimized DR convention.
- **suggestive** — soft imperative or pseudo-question. "Discover more",
  「もっと見る」, "了解更多". Brand / awareness convention.
- **aspirational** — invitation to identity / movement. "Join the
  movement", 「夢に向かって、踏み出そう」, "加入我們". Lifestyle /
  community convention.

**Format**: one of `direct` / `suggestive` / `aspirational`. The
Effectiveness axis (transcreation) explicitly checks that CTA strength
in the target matches the source declaration — a "direct" source rendered
as 「ご検討ください」 fails this check (over-polite, kills urgency).

---

## Field 7 — Brand-name handling

How the **brand name itself** renders per target locale. Four options
per locale:

- **translate** — semantic translation (rare for brand names; e.g.,
  "Apple" → 「林檎」 — almost never the right call).
- **transliterate** — phonetic rendering. JP katakana ("Patagonia" →
  「パタゴニア」), ZH 音譯 ("Coca-Cola" → 「可口可樂」), KR 한글
  transliteration.
- **preserve verbatim** — keep source-script brand name unchanged.
  Common for tech brands and English-rooted lifestyle brands in JP /
  ZH markets (Nike, Apple, Notion often preserved as-is).
- **locale-substitute** — brand has a separate locale-specific name
  (rare; e.g., a brand that operates as different name strings in
  different markets).

**Format**: a per-locale table:

```
ja-JP: transliterate (パタゴニア)
zh-TW: transliterate (巴塔哥尼亞)  -- official rendering per brand
zh-CN: transliterate (巴塔哥尼亚)
ko-KR: preserve verbatim (Patagonia)
```

Default when unspecified: **preserve verbatim**. M2 (project glossary
gate) treats brand-name handling as L1 priority — once specified, it is
mandatory.

---

## Worked example — Patagonia-style outdoor brand → ja-JP

Hypothetical brand brief for an outdoor / environmental brand similar in
positioning to Patagonia, translating campaign copy from en-US to ja-JP:

```yaml
brand_brief:
  archetype:
    primary:   Explorer
    secondary: Caregiver  # underlies environmental positioning

  tone_of_voice:
    authority: cool (3/5 toward cool)       # not authoritative; humble
    formality: casual (3/5 toward casual)   # but not slangy
    warmth:   warm (4/5 toward warm)        # community-oriented

  do_not_say:
    commercial_tone: ["cheap", "discount", "bargain", "sale", "limited stock"]
    competitor:      ["The North Face", "Arc'teryx", "Mont-bell"]
    jargon:          []  # outdoor jargon is allowed (target persona expects it)
    negative:        ["wasteful", "cheaply made"]
    culturally_loaded: ["大セール", "投げ売り"]  # ja-JP commercial-tone bans

  signature_phrases:
    - phrase:   "Don't buy this jacket"  # Black Friday 2011 anti-consumption ad
      handling: verbatim-preserve
      reason:   iconic campaign hook, JP audience aware via reissues
    - phrase:   "We're in business to save our home planet"
      handling: locale-transcreate
      ja-JP:    「私たちは、地球を守るためにビジネスをしている。」
    - phrase:   "1% for the Planet"
      handling: verbatim-preserve  # registered program name

  target_persona:
    age_range:        30-50
    region:           Tokyo / Osaka metro + 山岳エリア (mountain regions)
    life_stage:       outdoor-active adults, often family-formation
    cultural_context: ja outdoor / climbing / 環境意識の高い層
    reading_level:    general adult, outdoor jargon OK (アルパイン, クライミング)

  cta_style:
    default: aspirational  # "Join the movement to repair the planet"
    storefront_pages: direct  # but product pages still need conversion CTAs

  brand_name_handling:
    ja-JP: transliterate (パタゴニア)
    en-US: preserve verbatim (Patagonia)
```

This brief feeds the WRITER (Layer 3 DRAFT) as a system-prompt block,
and the Effectiveness axis (transcreation REFLECT) treats it as the
ground truth for brand-voice judgments. M2 enforces brand-name handling
as L1; do-not-say substring scans run as part of the M2 audit pass.

---

## See also

- `../SKILL.md` — invokes this protocol at Layer 2 step 1
- `../references/orthogonal-axes.md` — `register` + `intent` intake-spec
  fields (faithful mode falls back to these when no brief provided)
- `../references/5d-effectiveness.md` — Effectiveness axis consumes
  brand-brief outputs to judge brand-voice drift
- `../references/audit-trail-spec.md` — `brand_brief` block schema
- `protocols/transcreation-mode.md` — mode-entry contract; brief is
  recommended at the entry boundary
- `checklists/creative-checklist.md` — items 3 + 4 verify brand voice
  + do-not-say compliance against this brief
