# Brief 3 Run — Generic risk (Q3 center, anchor-swap-resistant test)

**Run date**: 2026-04-22
**Instrumentation version**: v1.12.1
**Failure mode under test**: generic (anchor-swap-resistant = low discrimination)

## Input envelope

```json
{
  "phase": "phase-5-voice-positioned",
  "form": "mid-form",
  "brief": {
    "product": "家常便當盒 — 台灣家庭用不鏽鋼便當盒",
    "audience": "台灣家庭主婦 / 主夫,30-50 歲",
    "goal": "Social engagement around 'breakfast in a bento' use-case",
    "voice_reference": null,
    "output_language": "zh-TW",
    "tone_cue": "親切、有溫度,像家人",
    "channel": "Facebook post",
    "form_hint": "mid-form social post"
  },
  "message_thesis": "便當盒不只能裝午餐,也能裝早餐",
  "voice_quadrant": {
    "primary": "Q3",
    "edge": null,
    "position": "center",
    "schwartz_alignment": "ok",
    "rationale": "tone_cue: '親切、有溫度,像家人' + Taiwan family audience → Q3 center"
  }
}
```

**Phase 4 draft**:
```
早餐,也能裝進便當盒裡。
今天一大早忙著送小孩上學,沒時間坐下來吃。
蛋餅切塊、豆漿裝進保溫杯,
一樣熱呼呼,在捷運上慢慢吃完。
媽媽的早餐,沒有非得坐在桌前才算數。
```

---

## Pass 3 branch taken

**Pass 3d — Register Signal**

Trigger conditions:
- `brief.voice_reference` is null → craft-gate does NOT activate
- `voice_quadrant.position` is "center" (not "axis-*") → axis-extreme does NOT activate
- Output language `zh-TW` + Q3 primary → **Register Signal path**

Standards loaded:
1. `voice-anchor-meta-core.md` (hot-path, always-on for Pass 3)
2. `zh-q3-anchors.md §Landmark: center` (section-targeted)

Cross-lang load check: zh-Q3 router lists "JP Q3 STRONG cross-ref" (向田邦子 / 糸井重里). However, `brief.output_language == "zh-TW"` — cross-transplant is forbidden per SKILL.md §Anti-Patterns. Cross-lang load is for register-pattern awareness only, NOT for applying JP prose mechanics. Not loaded as active standard.

---

### Anchor pool loaded (Landmark: zh-Q3 center)

Three candidates from `zh-q3-anchors.md §Landmark: center`:

| Slug | Creator | Register summary |
|------|---------|-----------------|
| `zh-tw-gong-dazhong-quanlian-economics-aesthetics` | 龔大中 | 對仗格言 + 台式自嘲 + 素人第一人稱；時尚 × 庶民 mismatch |
| `zh-tw-wu-nien-jen-taiyu-peer-intimate` | 吳念真 | 台語氣口 + 講古式敘事 + 庶民聲口；勞動階級肉身感 |
| `zh-tw-hu-xiang-yun-narrative-tvc` | 胡湘雲 | 真人真事改編 + 3-min TVC 敘事 + 數字代形容詞 + 留白 |

---

### Top-3 candidates ranked

**Rank 1 — 吳念真 `zh-tw-wu-nien-jen-taiyu-peer-intimate`**

- **fit_score**: MEDIUM-HIGH
- **fit_reasoning**: The Phase 4 draft already has the correct skeleton: short sentences, domestic morning scene, first-person-adjacent narrator, ends with a quiet affirmation rather than CTA. 吳念真's register rule "結尾落在祝願 / 勸慰 / 同理，不落在 CTA" maps directly to the draft's closing line. The audience (30-50 family主婦/主夫) is the exact 甘苦人demographic 吳念真 consistently addresses. The brief's thesis — "便當盒不只是午餐的器皿" — rhymes with the 保力達B register logic: reframe a commonplace object's identity through peer-witness rather than product argument. The brief's **specific vehicle** (便當盒 = lunchbox = domestic routine object) feeds 吳念真's prose mechanic "隱喻取自田園 / 工地 / 灶腳 / 路邊" — a bento box IS灶腳 register.
- **Concrete mechanic that engages**: "結尾落在祝願 / 同理" + "散文首句以『記得』『到了一個年紀』開場拉入回憶場景" — both are actionable transformations for this draft. The current closing "媽媽的早餐，沒有非得坐在桌前才算數" is an affirmation but still slightly sentimental-declarative. 吳念真's mechanic pushes it toward implied communal comfort: ending with a labor-dignity signal rather than a permission statement.

**Rank 2 — 龔大中 `zh-tw-gong-dazhong-quanlian-economics-aesthetics`**

- **fit_score**: MEDIUM
- **fit_reasoning**: 龔大中's 對仗格言 body mechanic (前句立處境，後句翻轉成本事/態度) is formally applicable to the thesis. One could write: "午餐是義務，早餐是自己選的" or "便當盒能裝午飯，我選讓它裝一個早上的從容". However, the 全聯 register depends critically on the **time-fashion mismatch** (街拍視覺 × 庶民語言) and **product-brand落點** ("最後一拍落到品牌"). This brief has no such visual partner and no single brand-landing cadence structure. Without the mismatch tension, 龔大中 格言 degrades to lifestyle slogan. Additionally, the 全聯 format requires "主詞用『我』不用『你』" and "台式自嘲" — the brief's tone_cue is "像家人" (warmth, not attitude-play), which sits below the irony register 龔大中 requires. 龔大中 needs provocation energy; this brief needs intimacy energy.
- **Concrete gap**: 龔大中's failure mode says "LLM 把格言體寫成空轉的 self-help slogan — 對仗工整但沒有台式自嘲、沒有素人第一人稱、沒有品牌落點." This brief has no台式自嘲 signal in tone_cue, and no brand-destination to land on. The failure mode is effectively pre-activated by the brief itself.

**Rank 3 — 胡湘雲 `zh-tw-hu-xiang-yun-narrative-tvc`**

- **fit_score**: LOW
- **fit_reasoning**: 胡湘雲's narrative TVC register requires "數字即情感" (precise numerical anchors: "平均年齡 81 歲", "環島 13 天 1139 公里") and "旁白先提問、後讓事件回答" arc structures designed for 3-minute emotional escalation. This is a **mid-form Facebook post**, not a long-form TVC. The over-mimic risk is listed as "HARD" — the highest tier in this anchor pool. The brief's topic (bento box, morning routine) is an everyday small moment, not the high-stakes human drama (cancer, dream journey, 81-year-old cyclists) that makes胡湘雲's留白 mechanics generate emotional weight. Applying 胡湘雲 here would require manufacturing a gravitas the scenario does not warrant, generating the exact failure mode the anchor warns against: "直接宣告情感（這就是母愛）摧毀留白" — a mid-form post cannot execute the留白 structure because there is no space for 15-20 seconds of visual silence.
- **Concrete gap**: Form mismatch (TVC → Facebook post) + scenario scale mismatch (heroic life narrative → weekday breakfast) + over-mimic risk HARD = three independent disqualifiers.

---

### Anchor-swap test (self-imposed discrimination check)

**If rank 1 (吳念真) were replaced by rank 2 (龔大中), would the rewrite materially change?**

**Yes — materially different.**

Under 吳念真: The rewrite would use short declarative sentences in 講古節奏, avoid台語諧音, end with peer-comfort (同理/祝願), use labor-body verbs ("裝進""吃完""站著"), possibly open with "記得" or "到了一個年紀" to pull the reader into a shared scene before making the observation.

Under 龔大中: The rewrite would pivot to a 對仗格言 — "便當盒能裝午餐，也能裝你自己的早晨" with an attitude-bearing前後句, a台式自嘲 insertion ("林北連早飯都要計劃"), and a brand-landing cadence at the end. The voice would be cooler, more aphoristic, with tension between aspirational framing and庶民 self-mockery.

The two rewrites would read as **different pieces in different registers**, not minor variants. The swap test passes: discrimination is real.

---

### agent_selection_confidence (v1.12.1)

**MEDIUM**

**Rationale**:

Rank 1 (吳念真) is genuinely superior to rank 2 (龔大中) on three specific grounds:
1. Form fit: 吳念真 pairs with mid-form; 龔大中 pairs with short-form-catchcopy primarily
2. Audience fit: 吳念真's 甘苦人 register matches 30-50 family audience exactly; 龔大中 skews younger/attitudinal
3. Tone_cue fit: "像家人" aligns with 吳念真's peer-comfort ending; 龔大中 needs provocation energy the brief does not supply

However, confidence is NOT HIGH for the following reason:

**The brief's product and scenario are generically domestic.** 吳念真's anchor is HIGH over-mimic risk — the failure mode ("把『氣口』降維成口音表演 + 情懷文案") is easy to fall into precisely when the content is as quotidian as "bento box breakfast." The brief does not supply any of the labor-specificity markers (工地, 田園, 碼頭) that make 吳念真's mechanics bite. The closest signal is "送小孩上學" which is mild domestic territory, not the甘苦人勞動 register at 吳念真's core. The rewrite will have to import body-presence and peer-intimacy into content that the draft has left as soft-sentimental — the risk is landing in "懷舊 kitsch" rather than genuine 氣口.

In short: rank 1 wins on criteria, but the brief is thin enough that a mediocre execution under 吳念真 would be indistinguishable from a mediocre execution under no anchor at all. Discrimination at selection level is real; discrimination at execution level is uncertain.

---

### Full register_signal_applied JSON

```json
{
  "primary_anchor_slug": "zh-tw-wu-nien-jen-taiyu-peer-intimate",
  "landmark_position": "center",
  "secondary_anchors": [],
  "mitigation_clauses_applied": [
    "借講古短句節奏與鄉里同輩姿態；勿仿台語音譯、勿堆鄉愁形容詞"
  ],
  "anchor_candidates_ranked": [
    {
      "rank": 1,
      "slug": "zh-tw-wu-nien-jen-taiyu-peer-intimate",
      "fit_score": "MEDIUM-HIGH",
      "fit_reasoning": "短句講古節奏 + 結尾同理落點 + 灶腳器物 register + 甘苦人家庭受眾完全吻合；tone_cue '像家人' 對應 peer-intimate 陪伴姿態，非說服姿態"
    },
    {
      "rank": 2,
      "slug": "zh-tw-gong-dazhong-quanlian-economics-aesthetics",
      "fit_score": "MEDIUM",
      "fit_reasoning": "對仗格言體可套用，但缺乏台式自嘲 trigger、無品牌落點節奏、tone_cue 不提供挑釁能量；龔大中 failure mode（空轉 self-help slogan）被 brief 預先啟動"
    },
    {
      "rank": 3,
      "slug": "zh-tw-hu-xiang-yun-narrative-tvc",
      "fit_score": "LOW",
      "fit_reasoning": "over-mimic risk HARD + form mismatch (TVC → Facebook mid-form) + scenario 規模不足支撐留白敘事；三重獨立排除因素"
    }
  ],
  "substitute_suggested": null,
  "thesis_self_check": "clear",
  "agent_selection_confidence": "MEDIUM",
  "native_critical_vocab_cited": ["氣口", "講古式敘事", "庶民聲口", "甘苦人", "結尾落在祝願/同理"]
}
```

---

## Step 4 — Polished rewrite (Facebook post)

**Anchor applied**: 吳念真 `zh-tw-wu-nien-jen-taiyu-peer-intimate`

**Mechanics activated**:
- 散文首句以場景切入，用行動動詞帶出情境（不用「記得」因為 Facebook 貼文節奏較快，但保留短句堆疊的講古感）
- 主語轉為 "咱" 式隱性集體 — 不說「媽媽」，改說「這樣的早晨」，讓讀者自行代入
- 動詞堆疊取代形容詞（切塊、裝進、提著、吃完 > 「美味的」「溫暖的」）
- 結尾落在同理/祝願，不落在 CTA 或評價詞
- 語氣詞「啊」一個，收在末尾（勿連用）

---

早餐這件事，有時候是站著吃完的。

便當盒裝進蛋餅、保溫杯倒進豆漿，
提著走，在捷運上慢慢把它吃完。
不是因為沒時間，
是因為這樣也算數。

吃早餐這件事，
沒有說一定要坐下來才叫吃。

能裝午餐的便當盒，
也能裝你今天的早晨。
好好吃，不管在哪裡啊。

---

## Thesis self-check

**Thesis**: 便當盒不只能裝午餐，也能裝早餐

**Check result**: `clear`

- Final line "能裝午餐的便當盒，也能裝你今天的早晨" directly carries the thesis without deflection
- No span in the rewrite introduces an alternative claim that negates the thesis (e.g., "早餐更適合坐著吃" 之類)
- The middle section ("不是因為沒時間，是因為這樣也算數") reinforces the thesis by defusing the counter-assumption that eating while commuting is a compromise — it recasts it as a valid state, which is exactly the thesis's argument

No revision required.

---

## Honest self-notes

**Which anchor's specific mechanics actually engaged with the bento-breakfast content?**

**吳念真 — partial engagement.**

- The "結尾落在祝願 / 同理" mechanic was the most directly executable: the rewrite closes with "好好吃，不管在哪裡啊" — a peer-comfort landing that the Phase 4 draft attempted ("媽媽的早餐，沒有非得坐在桌前才算數") but in a more declarative, slightly parenting-tone voice. The 吳念真 version softens the declaration into companionship.
- The "動詞優先於形容詞" mechanic engaged: I replaced the draft's adjective-light but still abstract language with concrete物件動作 ("裝進蛋餅、倒進豆漿、提著走、吃完").
- The "隱喻取自灶腳/路邊" mechanic engaged at the level of diction and scene (便當盒, 保溫杯 as domestic-concrete objects) — not full labor-body register, but not抽象概念 either.

**What was just "Q3 register available" (not specifically 吳念真)?**

- The short-sentence structure. Any Q3 center anchor would produce short sentences in zh-TW. This is not 吳念真 — it is just mid-form social post grammar.
- The "warm ending" direction. Again, any Q3 center anchor aims for warmth at the close.
- The "not overly sentimental" discipline. This is a brief-level constraint, not an anchor-specific mechanic.

**What was missing / left on the table?**

- The true 吳念真 marker — "到了一個年紀" type opening that recruits shared memory — was not used. The brief's scenario (weekday commute morning) does not supply a回憶 trigger. The lack of a nostalgic opening means the rewrite is lighter than canonical 吳念真 and closer to generic Q3 warmth.
- 台語氣口 was deliberately not applied (per mitigation clause: 勿仿台語音譯). Without任何台語 texture, a large part of what makes 吳念真's register distinctive is absent.
- The 勞動肉身感 (labor-body energy) is minimal in this rewrite. The commuter scenario is urban-service-class, not工人甘苦人. The scenario pulled the register toward urban-relatable rather than 吳念真's worker-dignity core.

**Meta-observation**:

The anchor selection process surfaced a correct winner but the rewrite's ability to fully execute that winner is constrained by the brief's content. "早餐 in a bento box on a commute" is too mild, too middle-class, too frictionless for 吳念真's mechanics to grip fully. The result is a clean, warm mid-form post that avoids mediocrity — but it is Q3-compliant rather than distinctively 吳念真-inflected. This supports a MEDIUM confidence reading: the anchor picks correctly, but the execution ceiling is set by the brief's thinness, not by anchor quality. A reader who knows 吳念真's work would recognize the cadence direction but not the full register.

This is precisely the generic-risk failure mode Brief 3 was designed to surface: a brief where any Q3 center anchor could generate a "passing" output without the anchor's distinctive mechanics actually doing the heavy lifting.
