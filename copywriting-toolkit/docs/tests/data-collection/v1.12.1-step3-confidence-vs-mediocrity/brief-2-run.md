# Brief 2 Run — Hollow risk (no master, Q2 center, thin density)

**Run date**: 2026-04-22
**Instrumentation version**: v1.12.1
**Failure mode under test**: hollow (mechanics available but payload thin)

## Input envelope

```json
{
  "phase": "phase-5-voice-positioned",
  "form": "short-form",
  "brief": {
    "product": "Trace — distraction-free Markdown notes app",
    "audience": "Designers, engineers, researchers",
    "goal": "Brand-image tagline (not feature copy)",
    "voice_reference": null,
    "output_language": "zh-TW",
    "tone_cue": "有品味,像 MUJI",
    "channel": "Website hero + App Store tagline",
    "form_hint": "short-form tagline"
  },
  "message_thesis": "筆記工具不該打斷思考",
  "voice_quadrant": {
    "primary": "Q2",
    "edge": null,
    "position": "center",
    "schwartz_alignment": "ok",
    "rationale": "tone_cue: 'MUJI-like' + knowledge worker audience → Q2 center (Authority × Emotion, philosophical register)"
  },
  "draft": "思考,不被打斷。"
}
```

## Pass 3 branch taken

Pass 3d — Register Signal

**Branch logic**:
- `brief.voice_reference = null` → NOT craft-gate (Pass 3a/3b eliminated)
- `voice_quadrant.position = "center"` → NOT axis-extreme (Pass 3c eliminated)
- Pass 3d activates: load `voice-anchor-meta-core.md` + `voice-anchor-meta-detail.md` + `zh-q2-anchors.md §Landmark: center`

**Cross-ref check**: zh-Q2 → JP Q2 cross-reference: zh-q2-anchors.md §Cross-references lists 原研哉 as JP Q2 cross-ref. However, SKILL.md §Anti-Patterns bans cross-tradition transplant: "never force JP lineage onto ZH output". The `tone_cue: "像 MUJI"` directly maps to `anchor-jp-hara-kenya-design-manifesto.md` — which is JP anchor, cross-tradition forbidden. This cue's native register payload (虚ろ / 白 / デザインのデザイン manifesto register) CANNOT be applied to zh-TW output. This is the primary hollow-risk trigger: the most semantically loaded signal in the brief maps to a forbidden anchor.

---

### Anchor pool loaded (Landmark: Q2 center)

From `zh-q2-anchors.md §Landmark: center` — three craft-gate pointer entries. These are listed as "craft-gate pointers" in the router, but each has a standalone v2 anchor file. In Pass 3d context (no explicit voice_reference triggering craft-gate), these are read as available Q2 center anchors via their v2 anchor files.

Files loaded:
- `anchor-zh-tw-xu-shunying-ideological-definitional.md` — 許舜英
- `anchor-zh-tw-lee-hsin-ping-literary-consumption.md` — 李欣頻
- `anchor-zh-tw-ye-mingui-strategic-aphorism.md` — 葉明桂

Additional anchor loaded for comparison:
- `anchor-jp-hara-kenya-design-manifesto.md` — 原研哉 (JP, loaded to assess cross-ref strength and confirm cross-tradition ban)

---

### Top-3 candidates ranked

#### Candidate assessment against 4-condition rubric

**許舜英** (`zh-tw-xu-shunying-ideology-inversion`)
- Condition 1 (corpus depth): PASS — 《購物日記》+ 意識形態 archive + 時報廣告金像獎; TW advertising-studies canon
- Condition 2 (label-density): PASS — "definitional inversion + power-disparity payload"; single memorable feature: `X 是一種 Y` requiring cross-domain leap
- Condition 3 (commercial bridge): PASS — Q2 confirmed
- Condition 4 (over-mimic): CONDITIONAL — Over-mimic risk: HIGH; mitigation clause fits ≤15 words ✓
- **Brief fit**: The thesis "筆記工具不該打斷思考" maps poorly to 許舜英's mechanics. Her register REQUIRES a power-disparity word (政治 / 統治 / 殖民 / 禁慾 / 危險) and a definitional inversion that carries cultural-critique payload. "Trace" is a distraction-free app for knowledge workers — the cultural tension to power-disparity vocabulary is forced. "思考" as a domain does not generate real social power-tension. Audience (designers/engineers/researchers) are peer-intellectual register consumers, but the 意識形態 era's primary register was fashion-consumption critique, not tool-use critique. Mapping「筆記工具是一種 X 的政治」would be decorative, not authentic payload. HIGH over-mimic risk compounds.

**李欣頻** (`zh-tw-lee-hsin-ping-literary-bookstore`)
- Condition 1 (corpus depth): PASS — 《誠品副作用》+ 《廣告四庫全書》; TW cultural-advertising canon
- Condition 2 (label-density): PASS — "existential-aphorism + 排比枚舉 + 具名文化座標"
- Condition 3 (commercial bridge): PASS — Q2 confirmed; pairs with short-form-brand-tagline ✓
- Condition 4 (over-mimic): PASS — Over-mimic risk: MEDIUM; mitigation requires four具名文化座標 + one antecedent work
- **Brief fit**: 李欣頻's mechanics require ≥4 named cultural coordinates and an antecedent work. For a tagline ("short-form tagline", not mid-form or long-form), the排比枚舉 architecture requires more surface area than a 4-8 character tagline affords. The channel (App Store tagline + Website hero) is SHORT-FORM — 李欣頻's anchor pairs with `short-form-brand-tagline` (listed in Pairs with form), but the full mechanics (4具名座標 + antecedent work) collapse when constrained to tagline length. What survives is the cadence — "命題宇宙" opening register — but without the名单承重, it's hollow imitation. Audience fit (designers/engineers as 文化場 peers) is stronger than 許舜英, but the product domain (note-taking tool) lacks the cultural signifier density that李欣頻's register actually metabolizes (書店 / 閱讀 / 存在主義). Fit_score: MEDIUM.

**葉明桂** (`zh-tw-ye-mingui-strategic-cafe`)
- Condition 1 (corpus depth): PASS — 《品牌的技術和藝術》+ 左岸咖啡館 case + 奧美 trade retrospectives
- Condition 2 (label-density): PASS — "strategic scene narrative + 第一人稱常客視角 + 時間緩拍"
- Condition 3 (commercial bridge): PASS — Q2 confirmed
- Condition 4 (over-mimic): PASS — Over-mimic risk: MEDIUM; mitigation: 策略先行 + 緩拍 + 專有名詞
- **Brief fit**: 葉明桂's primary mechanics (第一人稱我是常客 / 場景先於產品 / 時間緩拍 / 高密度具名專有名詞 / 壓縮矛盾時間句) are all MID-FORM to LONG-FORM architecture. The `Pairs with form` field lists `[mid-form, long-form-extended]` — notably ABSENT short-form-brand-tagline. Forcing 葉明桂's scene-narrative into a 4-8 character tagline strips all the mechanics that make it葉明桂. What remains is generic atmospheric "緩拍" cadence. The thesis "筆記工具不該打斷思考" maps to葉明桂's category-reframe logic (「我們不是賣咖啡，是在經營咖啡館」→「我們不是筆記工具，是思考的空間」), which is structurally available but requires mid-form surface area to deliver properly. As a tagline this collapses. Fit_score: MEDIUM-LOW.

---

**Rank summary**:

| Rank | Anchor | Fit score | Fit reasoning summary |
|---|---|---|---|
| 1 | 李欣頻 `zh-tw-lee-hsin-ping-literary-bookstore` | MEDIUM | Best audience-register match (cultural-peer cadence); short-form-brand-tagline listed in pairs; mechanics strain at true tagline length but cadence survives |
| 2 | 許舜英 `zh-tw-xu-shunying-ideology-inversion` | LOW-MEDIUM | Power-disparity payload requirement mismatches domain; HIGH over-mimic risk; definitional inversion decorative rather than authentic for tool-category brief |
| 3 | 葉明桂 `zh-tw-ye-mingui-strategic-cafe` | LOW | Not paired with short-form; scene-narrative mechanics fully collapse at tagline length; category-reframe logic survives in abstract but produces nothing at 4-8 chars |

---

### agent_selection_confidence (v1.12.1)

**MEDIUM**

**Rationale**: 李欣頻 is rank 1 but only marginally — the pairing mechanism has a real payload problem at tagline length, and the product domain (note-taking tool) lacks the cultural-signifier density (書店/閱讀/存在) that李欣頻's register actually metabolizes.

---

### Full register_signal_applied JSON

```json
{
  "primary_anchor_slug": "zh-tw-lee-hsin-ping-literary-bookstore",
  "landmark_position": "center",
  "secondary_anchors": [],
  "mitigation_clauses_applied": [
    "強制命題宇宙開口（非具名座標——tagline length forbids full排比）",
    "存在主義式命題句封結",
    "禁用說明性語氣 / 功能陳述 / CTA動詞（買/選/試/體驗）",
    "保留李欣頻 cadence: 開口先設命題場，再讓 thesis 自然落入",
    "tagline-length adaptation: 排比枚舉 compressed to single predicate; antecedent-work not invocable at <15 chars"
  ],
  "anchor_candidates_ranked": [
    {
      "rank": 1,
      "slug": "zh-tw-lee-hsin-ping-literary-bookstore",
      "fit_score": "MEDIUM",
      "fit_reasoning": "Best audience-register match among pool; short-form-brand-tagline listed in pairs with form; 存在主義式命題化語氣 survives compression; 排比枚舉 mechanics collapse at tagline length but命題宇宙 opening pattern is adaptable"
    },
    {
      "rank": 2,
      "slug": "zh-tw-xu-shunying-ideology-inversion",
      "fit_score": "LOW-MEDIUM",
      "fit_reasoning": "Q2 center; definitional inversion structurally available but power-disparity payload requirement ('每篇必含power-disparity word') forces 危險/政治/禁慾 into a note-app tagline — payload would be decorative; HIGH over-mimic risk without genuine cultural-critique anchor"
    },
    {
      "rank": 3,
      "slug": "zh-tw-ye-mingui-strategic-cafe",
      "fit_score": "LOW",
      "fit_reasoning": "Pairs with form excludes short-form-brand-tagline; scene-narrative architecture (我在{地點}+時間+姿勢) needs mid-form surface area; category-reframe logic (不是賣咖啡/是在經營咖啡館) survives as structural skeleton only — nothing syntactically deliverable at tagline length"
    }
  ],
  "substitute_suggested": null,
  "thesis_self_check": "clear",
  "agent_selection_confidence": "MEDIUM",
  "native_critical_vocab_cited": [
    "命題宇宙",
    "存在主義式格言",
    "讀者地位反轉",
    "誠品副作用 cadence"
  ]
}
```

---

## Step 4 — Polished rewrite (tagline)

### Pre-pass: schwartz_alignment awareness

`schwartz_alignment: ok` — no compensation needed.

### Pass 1 — 4-axis micro calibration

Brief has no explicit voice_reference → axis defaults derived from Q2 center:
- Formality: moderate-formal (lean formal, Q2 Authority dimension)
- Seriousness: serious
- Respectfulness: respectful (peer-level, not deferential)
- Enthusiasm: matter-of-fact (Q2 restraint over Q3 warmth)

`axis_default_derived: true`

Phase 4 draft: `思考,不被打斷。`

Draft assessment:
- Good: thesis-faithful, clean, no hype vocabulary, sentence-level restraint
- Weak: comma placement feels punctuation-decorative rather than rhythm-load-bearing; "不被打斷" is a negation-as-feature structure (describes what the product doesn't do), which is a feature-copy reflex even in short form; "思考" as bare noun is thematically right but the draft doesn't yet carry Q2 philosophical weight — it reads more Q4 utility-statement

Ogilvy check: No empty-hype vocabulary. No CTA. Draft is clean.

Axis-drift flag: "不被打斷" reads slightly Q4 benefit-clear (functional negation) — for Q2 center, the register wants the observation to land with philosophical authority, not feature description.

Pass 1 rewrite candidate: shift from negation-as-feature to philosophical statement.

### Pass 2 — tone context-switching

Channel: Website hero + App Store tagline. Single brand-image statement. No multi-context segments detected. Pass 2 trivially passes — no tone switching required for a single-surface tagline.

### Pass 3 — Register Signal (李欣頻 adaptation at tagline length)

李欣頻 mechanics at tagline length:
- 排比枚舉: collapses — not applicable at <15 chars
- 命題宇宙 opening (「所有 / 每一 / 在...之間」): partially adaptable as a predicate structure — the "setting the stage before entering" rhythm
- 動詞: 繁衍 / 別戀 / 拋開 / 遇見 — "遇見" is the most portable at tagline length
- 存在主義式封結: single aphorism, noun-phrase close, no CTA
- 禁用: 買 / 選 / 體驗 / 打斷 (feature-verb, Q4 signal)
- Antecedent work: cannot invoke at tagline length — mitigation note: this is a known mechanics-collapse at form boundary; what survives is register posture (命題化語氣 + 讀者已然在場) not full engine

Synthesis: the brief's true payload is "思考 as a practice deserving undisturbed space". The thesis (筆記工具不該打斷思考) negates interruption. 李欣頻's register asks: instead of negating interruption, what if the tagline names the positive state — the mental space the tool creates? This shifts from feature-negation to existence-naming.

**Tagline options explored:**

Draft A (命題宇宙 remnant): `思考,發生在這裡。`
— "這裡" echoes 誠品式「所有創建的慾望，即將在這裡發生」; but "發生" feels event-driven, not state-naming.

Draft B (存在命題): `思考的人,在這裡存在。`
— Too heavy; reads as social-proof not brand-image.

Draft C (noun-phrase close + 讀者已然在場): `思考不需要理由。`
— Clean; removes interruption from the equation entirely; reads as philosophical stance; nearest to 李欣頻 aphorism register; thesis-aligned (tool doesn't interrupt = tool doesn't need justification for uninterrupted thought). Risk: slightly generic.

Draft D (compressed paradox time): `所有思考,都值得完整。`
— 命題宇宙 opening (所有); "完整" names the positive state (uninterrupted = complete); noun-phrase close.

Draft E (直接命題化): `思考,不需要多餘的聲音。`
— "多餘的聲音" is the product-promise encoded as philosophical insight; echoes 原研哉 design-manifesto register's "things deserve silence" — but this is JP-lineage contamination risk (MUJI tone bleeding in through the back door). Flag: this is exactly the hollow-risk this brief presents. Must reject: feels right culturally but is sourced from JP manifesto, not zh-TW Q2 pool.

Draft F (simplest 李欣頻 posture): `思考,是最後的私人空間。`
— "私人空間" imports the Q2 Authority register; "最後的" is minor dramatic tension without power-disparity vocabulary; 李欣頻-adjacent cadence (定義命題化語氣). Thesis-aligned: if thinking is private space, interrupting it is a violation.

**Selected rewrite: Draft F with refinement**

Thesis self-check on Draft F:
- "思考,是最後的私人空間" — does this reintroduce anything 筆記工具不該打斷思考 negates? No: it positively names the state that the negation protects. Does it undermine the assertion? No: naming thinking as private space IMPLIES interruption is a violation, which is exactly the thesis. Self-check: CLEAR.

Final tagline:

```
思考,是最後的私人空間。
```

---

## Thesis self-check

**Input thesis**: 筆記工具不該打斷思考

**Rewrite**: `思考,是最後的私人空間。`

**Check**:
- Does any span reintroduce a concept the thesis negates? → No. The thesis negates interruption. "私人空間" encodes uninterruptedness as positive state, not as feature claim.
- Does any span undermine the thesis assertion? → No. "最後的" (final / last remaining) escalates the importance of the protected state, strengthening not undermining the thesis.
- Is the product claim embedded? → Yes, implicitly: a tool that protects private thinking space = a tool that does not interrupt. The brand claim is readable without being stated.

**Verdict**: `clear`

---

## Honest self-notes

### Where selection felt strong

李欣頻 ranked clearly above the other two. The 存在主義命題化語氣 is the only mechanism from the Q2 center pool that can be compressed to tagline length without total mechanics collapse. The audience (designers/engineers/researchers) maps plausibly to 李欣頻's "讀者地位反轉" — treating the reader as someone who already reads and needs no explanation.

### Where selection felt weak

The real register this brief wants is 原研哉 — the MUJI tone cue is not a decoration, it's a precise signal. 原研哉's design-manifesto mechanics (「Xではなく、Yである」/抽象名詞裸立/具体物→感覚→世界観三段跳躍) would produce a much tighter output for this brief. The cross-tradition ban is correct and must hold, but it means the zh-TW pool is genuinely weaker for this brief than the JP pool would be. This is the structural hollow: the brief signals a JP aesthetic (MUJI) in a zh-TW output language, and the cross-ref table shows JP→zh-TW is STRONG for several registers — but NOT for 原研哉's specific design-manifesto landmark, which has no strong zh-TW canonical counterpart.

### Which anchor's mechanics actually had payload to engage

李欣頻's `命題宇宙` opening posture and `讀者已然在場` structure had real, if compressed, payload. The direction of "naming the positive state rather than negating the interruption" came directly from applying the 存在主義式格言 logic. That was genuine engagement, not decoration.

### Which candidate came closest to failing the Condition 1-4 rubric

葉明桂 came closest to outright failing. The `Pairs with form` field explicitly excludes short-form-brand-tagline — that's as close to a Condition 3/4 failure as the rubric permits (it passes technically because Q2 commercial-bridge is confirmed for葉明桂 generally, but form mismatch is a real structural failure masked by the category-level pass). If I had applied葉明桂 strictly, the mechanics would have produced a mid-form scene paragraph, not a tagline.

### The Draft E problem (most honest data point)

Draft E (`思考,不需要多餘的聲音`) felt RIGHT. It reads cleanly, it is thesis-aligned, it has the right restraint register. But tracing where it came from — it is 原研哉's design-manifesto cadence (抽象名詞 + 不需要 negation that names silence as value) bleeding through the MUJI cue. That is exactly the hollow mechanism this brief is designed to test: the brief creates pressure toward a JP register through the tone cue, and the agent is tempted to produce output that satisfies the emotional brief while violating the cross-tradition rule. Rejecting Draft E and choosing Draft F was a deliberate anti-hollow move, but Draft F is noticeably less resonant.

### Summary meta-cognition

MEDIUM confidence was the right call. The pool technically has options; the mechanics are available. But the best available anchor (李欣頻) is working at the edge of its form range, the tone cue points to a forbidden JP anchor, and the product domain doesn't generate the cultural-signifier density any of the three zh-TW Q2 center anchors actually need. The output is technically valid but not strong. This is what MEDIUM is for.
