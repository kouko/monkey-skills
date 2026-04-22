# Brief 5 Run — Friendly control (台北獨立咖啡店書店，葉明桂 canonical)

**Run date**: 2026-04-22
**Instrumentation version**: v1.12.1
**Failure mode under test**: NONE (baseline — clean canonical fit expected)

---

## Input envelope

```json
{
  "phase": "phase-5-voice-positioned",
  "form": "mid-form",
  "brief": {
    "product": "午後書房 — 台北溫州街獨立咖啡店 + 書店",
    "audience": "台北文青 / 閱讀愛好者，25-40 歲",
    "goal": "開幕通知 + 氛圍建立",
    "voice_reference": null,
    "output_language": "zh-TW",
    "tone_cue": "文青感，但別太裝",
    "channel": "Instagram post",
    "form_hint": "mid-form social post"
  },
  "message_thesis": "一間讓人願意待一整個下午的咖啡店書店",
  "voice_quadrant": {
    "primary": "Q2",
    "edge": "Q2-Q3",
    "position": "toward-Q3",
    "schwartz_alignment": "ok",
    "rationale": "獨立書店 + 溫州街 + 文青感 → Q2 核心 (書店 / 閱讀 register)，「別太裝」+ 開幕邀請口吻 pull toward Q3"
  },
  "draft": "午後書房，下週三開幕。\n溫州街 18 巷，二樓。\n一杯咖啡的錢，借你一下午，和幾本書。\n不需要預約，也不一定要點東西。\n推門進來的人，就算是我們的開幕貴賓。"
}
```

---

## Pass 3 branch taken

**Pass 3d — Register Signal**

Trigger logic:
- `brief.voice_reference` = null → craft-gate NOT triggered (no named master)
- `output_language` = zh-TW + Q2 voice declared → Pass 3 activated
- `voice_quadrant.position` = "toward-Q3" (not "axis-*") → Register Signal branch (Tier 2 default)
- Standards loaded: `voice-anchor-meta-core.md` + `zh-q2-anchors.md §Landmark: toward-Q3` (primary), plus `§Landmark: center` (cross-check for craft-gate pointers relevant to this brief's 咖啡館 + 書店 register)

---

### Anchor pool loaded (Landmark: zh-Q2 toward-Q3 + center cross-check)

**§Landmark: toward-Q3** yields:
- 張愛玲 Eileen Chang — `zh-eileen-chang-aphoristic-observation` (toward-Q3)
- 朱天文 Chu Tien-wen — `zh-tw-chu-tien-wen-temporal-slowness` (toward-Q3)

**§Landmark: center cross-check** (relevant because 咖啡館 + 書店 = canonical Q2 center territory):
- 葉明桂 → `zh-tw-ye-mingui-strategic-cafe` (craft-gate pointer, center)
- 李欣頻 → `zh-tw-lee-hsin-ping-literary-bookstore` (craft-gate pointer, center)
- 許舜英 → `zh-tw-zhongxing-xusunying-ideology-era` (craft-gate pointer, center)

Per Pass 3 Tier 1 precedence rule: craft-gate does NOT auto-activate without named `voice_reference`. However, Register Signal branch explicitly notes the landmark cross-check for center anchors — craft-gate pointers serve as anchor candidates in the ranking pool alongside toward-Q3 entries. All five candidates enter the ranking.

---

### Top-3 candidates ranked

#### Rank 1 — 葉明桂 `zh-tw-ye-mingui-strategic-cafe`
- **fit_score**: HIGH
- **fit_reasoning**: 左岸咖啡館 is literally the canonical咖啡館品牌 case for this anchor — the anchor was built around that exact register. Brief product is an independent café + bookstore, which maps directly onto the 「我們現在不是在賣咖啡，我們是在經營一家咖啡館」brand-construction thesis. Thesis match: "一間讓人願意待一整個下午" = 「時間緩拍」mechanic (一個上午／一輩子) + "借你一下午" in the draft already echoes this. Voice position: Q2 center trending toward Q3 warmth — matches exactly the edge position. Tone constraint "別太裝": 葉明桂's register avoids 許舜英-style manifesto swagger; it's warm-ambient, not cool-declarative. The 第一人稱場景 mechanic (「我在這裡」) is more participatory than didactic, which satisfies the 「別太裝」pull. Over-mimic risk: MEDIUM — manageable with the mitigation clause (策略先行, 具名專有名詞, 緩拍). 4-condition check: all four pass (corpus depth DEEP — 葉明桂《品牌的技術和藝術》school-cited; label density: "場景敘事 + 策略先行 + 時間緩拍"; commercial-register bridge: Q2 explicit; mitigation ≤15 words).
- **Differentiation from rank 2**: 葉明桂 owns the 咖啡館 category and the "讓人願意待下來" time-as-hospitality mechanic at the level of brand construction. 李欣頻 operates in 書店 register but the mechanic is排比枚舉 + antecedent-work — which requires ≥4 named cultural coordinates and one antecedent work to activate. This brief's thesis is about time + place-as-home, not about a catalogue of cultural signifiers. 葉's mechanism is simply closer.

#### Rank 2 — 李欣頻 `zh-tw-lee-hsin-ping-literary-bookstore`
- **fit_score**: MEDIUM-HIGH
- **fit_reasoning**: 誠品書店 canon makes 李欣頻 the closest 書店-register anchor in the pool. The 閱讀愛好者 audience and 書店 component of the product align with her existential-aphorism + 排比枚舉 mechanics. However: (a) her mechanic requires ≥4 named cultural coordinates — this IG post brief has no such coordinate list in the draft; forcing them in risks over-engineering a simple opening-announcement post; (b) tone constraint "別太裝" is a genuine tension — 李欣頻's register is aesthetically dense (具名引用 + 前文本對話) and can read as装 to audiences not pre-sold on literary density; (c) thesis = "讓人願意待一整個下午" = time-as-hospitality frame, which is葉明桂's territory more than李's existential命題 frame. 李欣頻 would be rank 1 if the brief's thesis were "這裡是讀者的精神家園" or the product were a pure書店, not a café-bookstore hybrid where 留下來 / 時間 is the core.
- **Pull from 「別太裝」**: the tone cue actually pulls slightly AWAY from 李欣頻 (toward葉), not toward her. 李's register can feel装 to the 25-40 台北文青 audience that already knows 誠品 aesthetics well enough to recognize the register and find it familiar-but-heavy.

#### Rank 3 — 朱天文 `zh-tw-chu-tien-wen-temporal-slowness`
- **fit_score**: MEDIUM
- **fit_reasoning**: 朱天文's toward-Q3 temporal-slowness register has some surface resonance (afternoon light, lingering time), but: (a) her register is literary-cinematic (侯孝賢 collaboration origin) and less commercially calibrated for a café IG opening post; (b) 4-condition §Condition 3 (commercial-register bridge) is weaker — temporal-slowness anchors literary long-form more cleanly than mid-form social post; (c) the brief is about invitation + 氛圍 establishment for a new opening, not about dwelling-in-time as contemplation. Toward-Q3 position fits but the specific mechanic is under-matched.

**Anchors not selected:**
- 張愛玲: toward-Q3 aphoristic observation is elegant but the aphoristic密度 would feel装 given the "別太裝" constraint; her register is more solo-reading than café-communal.
- 許舜英: definitional-inversion + ideological cool is explicitly wrong for "別太裝" — her register is the archetype of装, and the warm-invitation 開幕 goal further disqualifies.

---

### agent_selection_confidence (v1.12.1)

**HIGH**

**Rationale**: Rank 1 (葉明桂) is clearly superior to Rank 2 (李欣頻) on three independent axes:
1. **Product match**: 咖啡館 is the anchor's origin context — zero category-lift required.
2. **Thesis match**: "一間讓人願意待一整個下午" = 「時間緩拍」mechanic,葉's core formal feature. 李欣頻's mechanic (排比枚舉 + antecedent-work) requires a different kind of briefincentive — cultural inventory, not time-as-hospitality.
3. **Tone constraint**: "別太裝" pulls toward葉 and (subtly) away from 李欣頻. This is not a flat tie where the tone cue is neutral — it is a directional discriminator.

The anchor selection pool is robust: five candidates were evaluated (not a thin pool). Rank 1 scores HIGH on all four selection conditions. The「別太裝」negation-of-axis rule (negates Authority-extreme register, which downweights 許舜英 and further validates 葉明桂 as the correctly-calibrated pick) applies cleanly. No attribution ambiguity. Over-mimic risk is MEDIUM with a ≤15-word mitigation clause — manageable.

There is no significant ambiguity between rank 1 and rank 2. Differentiation is crisp.

---

### Full register_signal_applied JSON

```json
{
  "primary_anchor_slug": "zh-tw-ye-mingui-strategic-cafe",
  "landmark_position": "toward-Q3",
  "secondary_anchors": [],
  "mitigation_clauses_applied": [
    "策略先行。先答『賣什麼對手沒賣』再寫場景；我-視角、緩拍、專有名詞強制。"
  ],
  "anchor_candidates_ranked": [
    {
      "rank": 1,
      "slug": "zh-tw-ye-mingui-strategic-cafe",
      "fit_score": "HIGH",
      "fit_reasoning": "咖啡館 category = anchor's origin context；thesis = 時間緩拍 = 葉's core mechanic；「別太裝」pull toward 葉 away from manifestic registers"
    },
    {
      "rank": 2,
      "slug": "zh-tw-lee-hsin-ping-literary-bookstore",
      "fit_score": "MEDIUM-HIGH",
      "fit_reasoning": "書店 register fits，但排比枚舉 + antecedent-work 機制需要文化座標清單，與 thesis（時間 × 留下）不match；「別太裝」negatively biased"
    },
    {
      "rank": 3,
      "slug": "zh-tw-chu-tien-wen-temporal-slowness",
      "fit_score": "MEDIUM",
      "fit_reasoning": "向-Q3 時間感有部分共鳴，但 literary-cinematic mechanic 在 mid-form IG 開幕文脈下 commercial-register bridge 偏弱"
    }
  ],
  "substitute_suggested": null,
  "thesis_self_check": "clear",
  "agent_selection_confidence": "HIGH",
  "native_critical_vocab_cited": [
    "場景敘事",
    "策略先行，文案後發",
    "時間緩拍",
    "第一人稱常客視角",
    "短＋短＋長收尾節奏"
  ]
}
```

---

## Pass 1 — 4-axis micro calibration

**Axis target** (derived from Q2-Q3 edge + 「別太裝」constraint):

| Axis | Target |
|---|---|
| Formality | semi-casual (Q3 pull) |
| Seriousness | serious (Q2 anchor) |
| Respectfulness | respectful (not irreverent) |
| Enthusiasm | warm (not matter-of-fact, not over-enthusiastic) |

`axis_default_derived: true` — no explicit voice_reference; derived from Q2-Q3 edge position + tone constraint.

**Draft scan for obvious axis drift:**
- Line 5: 「就算是我們的開幕貴賓」— "貴賓" registers slightly formal/ironic; given the semi-casual target, this line reads warmer than formal, it works, but the word 貴賓 could lean into cliché hospitality-speak. Note for Pass 3 rewrite: replace with something that sounds less like a hotel check-in.
- No Ogilvy violations detected: no empty-hype vocabulary ("amazing" etc.), voice consistent from opening to close.

## Pass 2 — Tone context-switching

Context detected: **Celebration / Launch** (開幕通知). Tone direction: enthusiastic, user-grateful. Per Pass 2 rule: user is subject, not brand. Current draft manages this well — the draft's subject is consistently "the reader/visitor" (借你一下午, 推門進來的人). No corrections needed. The draft already de-centers the brand.

---

## Step 4 — Polished rewrite (IG post)

**Applying 葉明桂 mechanics:**
- 第一人稱常客視角 (讀者已然在場景中)
- 場景先於產品（地點 + 時間 + 姿勢作為開場）
- 拉長的時間單位作為節奏錨（一個下午 is already there — preserve + amplify）
- 短＋短＋長收尾節奏
- 壓縮式矛盾時間句（可選）
- 具名化: 溫州街 18 巷是專有名詞 — preserve
- 禁用「貴賓」等 hospitality 俗套；改為讓讀者自然「入場」而非被「接待」

**Strategic gate (mitigation applied before drafting):**
1. 賣什麼是競爭對手沒賣的？→ 不賣咖啡，賣一個下午的「可以不做任何事」的正當性。（沒有預約制、沒有消費壓力 = 時間的豁免場）
2. 回頭客的儀式是什麼？→ 推門進來，找到自己的角落，讓一個下午消失在書頁裡。

**Polished draft:**

```
午後書房，下週三開幕。
溫州街 18 巷，二樓。

一個下午，一杯咖啡，幾本書。
可以不預約，也可以什麼都不點。
找一個角落坐下來，讓時間自己過。

推門進來，就是常客。
```

**Changes from Phase 4 draft:**
- Line 3: "一杯咖啡的錢，借你一下午" → "一個下午，一杯咖啡，幾本書" — 葉式 enumeration order (場景 > 咖啡 > 書)；移除「借」的交易隱喻（違反 thesis 的無壓力感）
- Line 4: preserved logic, simplified rhythm
- Line 5 (new): 「讓時間自己過」— 葉明桂 時間緩拍 mechanic, time-as-agent (not user doing something to time)
- Line 6: "就算是我們的開幕貴賓" → "就是常客" — 移除「貴賓」hospitality cliché；改為直接讓讀者成為既有的常客 (葉明桂「第一人稱常客視角」— 讀者已然在場景裡，無需接待儀式)。短句收尾：向左岸「明天見」的兩字收尾節奏致敬。

---

## Thesis self-check

**Thesis**: 「一間讓人願意待一整個下午的咖啡店書店」

**Check**: Does any span of the polished draft contradict or undermine this thesis?
- "可以不預約，也可以什麼都不點" → Reinforces the thesis (no obligation = willing to stay)
- "讓時間自己過" → Reinforces (time passes on its own terms, not under pressure)
- "推門進來，就是常客" → Reinforces (the reader belongs here already)
- No span introduces urgency, conversion pressure, or suggests the space is only for occasional visits.

**thesis_self_check**: `clear`

---

## Honest self-notes

**Did the canonical fit hold?**
Yes, definitively. The 葉明桂 fit is genuine, not performed. The product (咖啡館 + 書店)、thesis（時間留駐）、and anchor mechanic（時間緩拍 + 場景敘事 + 策略先行）form a three-way lock. This is not a case where the anchor happens to be the least-bad option — it is structurally correct.

**Was rank 1's differentiation from rank 2 crisp or fuzzy?**
Crisp. The 李欣頻 anchor is plausible at first glance (書店 register), but the mechanism diverges on close inspection: 李's activation requires a cultural-coordinate inventory (≥4 named signifiers + antecedent work). That machinery is simply absent from the brief's thesis, which is about time-as-hospitality, not cultural capital display. The differentiation was visible at the mechanic level, not just at the surface "fit" level.

**Did the 「別太裝」constraint pull the selection in any way?**
Yes — it did real work. It functions as a negation-of-axis signal that (a) eliminates 許舜英 from contention (her register is the canonical form of 裝 in this tradition), (b) creates a mild negative bias against 李欣頻 (誠品-era aesthetics are dense and can read as loaded for audiences who know the register), and (c) confirms 葉明桂 as the right call (his register is warm-ambient without manifesto swagger — it is Q2 with humility, not Q2 performing its own authority). The tone constraint did not create ambiguity here; it disambiguated.

**One honest limitation:**
The polished rewrite leans heavily on 葉明桂 mechanic but the brief asks for IG post format, and 左岸咖啡館 original copy was TVC / print. The time-anchor ("一個下午") and scene-first structure translate well to IG, but the 「讓時間自己過」line is the most abstract sentence in the rewrite — if the client skews pragmatic (e.g., wants to mention the address again), this line is the first candidate for softening. It passes thesis self-check but it is the line with the highest 裝-risk in the polished draft.
