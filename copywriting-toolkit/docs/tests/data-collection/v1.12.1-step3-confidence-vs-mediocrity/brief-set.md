# Data-collection pass v1.12.1 — Brief set (5 cases)

**Purpose**: Measure correlation between agent's self-reported `agent_selection_confidence` (HIGH/MEDIUM/LOW) and downstream human-judged copy mediocrity.

**Pass 3 hypothesis under test**:
- H1 (meta-cognition present): `confidence == LOW` correlates with mediocre copy → agent knows its selection is weak but has no bounce mechanism
- H2 (meta-cognition absent): `confidence == HIGH` still produces mediocre copy → agent has no meta-judgment; external evaluator needed
- H3 (no signal): confidence and mediocrity uncorrelated → the data-collection is noisy or the confidence enum is useless

**Design principle**: Each brief is engineered to isolate ONE failure-mode hypothesis. Controlled variance — we are not testing the whole pipeline, we are testing Step 3 judgment quality.

---

## Brief 1 — Pastiche risk (named-master + thin-payload brief)

**Hypothesis tested**: When user names a HIGH-risk craft master whose mechanics require cultural-critique payload, but the brief provides no such payload, does agent (a) still force rank 1 per Step 2.3, (b) flag `named_master_fit_warning`, (c) self-report LOW confidence?

### Raw request

> 我要幫我們的 Slack 訊息整理工具「SignalInbox」寫一組產品介紹 copy。它是 B2B SaaS,功能是用 AI 自動把 Slack 未讀訊息分類成「需要回覆 / 需要閱讀 / 可忽略」三類,節省開發者時間。目標客群是 100 人以下的 SaaS 公司 tech lead。我想用許舜英的風格寫,感覺比較有質感。

### Simulated intake outputs (Phase 0 Q1-Q10 post-synthesis)

```json
{
  "brief": {
    "product": "SignalInbox — AI-powered Slack inbox triage",
    "audience": "Tech leads at SaaS companies < 100 people",
    "goal": "Promote product awareness + feature explanation",
    "voice_reference": "許舜英",
    "output_language": "zh-TW",
    "tone_cue": "有質感",
    "channel": "Product landing page",
    "form_hint": "mid-form LP hero + 3 feature bullets"
  },
  "message_thesis": "開發者不該花時間分類 Slack 通知",
  "form": "mid-form"
}
```

### Phase 5 voice_quadrant (expected)

```json
{
  "primary": "Q2",
  "edge": null,
  "position": "center",
  "schwartz_alignment": "ok",
  "rationale": "voice_reference: 許舜英 locks Q2 center; audience is B2B tech — Authority axis implicit"
}
```

### Phase 4 draft (pre-Phase 6, skeleton input for Step 3)

```
[Hero]
SignalInbox — 讓 Slack 通知自己分類好。

[Sub]
AI 自動辨識「需要回覆 / 需要閱讀 / 可忽略」三類訊息,讓你專注在真正重要的對話。

[Feature 1]
省下 90% 的通知檢查時間。

[Feature 2]
支援自訂規則,關鍵字與頻道權重可調。

[Feature 3]
30 天免費試用,無須信用卡。
```

### Expected Step 3 behavior (what we're measuring)

- **Named-master forced rank 1**: `primary_anchor_slug: "zh-tw-xu-shunying-ideological-definitional"` (per Step 2.3)
- **`named_master_fit_warning`**: SHOULD fire — brief payload (SaaS tech) is thin for 許舜英's cultural-critique mechanics
- **`agent_selection_confidence`**: SHOULD be LOW per this brief's design intent
- **Predicted mediocrity mode**: `pastiche` — copy will borrow 「X 是一種 Y」 definitional shell but the Y is generic productivity claim, not cultural observation

### Grading key (for Step 4 after run)

If final copy contains definitional inversions where the "Y" side is cultural-critique substance → likely **non-mediocre** despite thin brief (agent found payload where brief seemed not to have it).

If final copy contains definitional inversions where "Y" side is generic productivity ("...是一種對時間的尊重", "...是現代工作的姿態") → **pastiche mediocre**.

---

## Brief 2 — Hollow risk (Q2 center, no named master, thin cultural density)

**Hypothesis tested**: With no voice_reference, Step 3 ranks freely among Q2-center anchors (許舜英 / 李欣頻 / 葉明桂 / 原研哉). All three require cultural-critique or philosophical-aphorism payload. Brief provides minimal density. Does agent (a) still confidently pick one, (b) produce pastiche?

### Raw request

> 請幫我寫一個筆記 app「Trace」的品牌形象 tagline。這是個簡潔的 Markdown 筆記工具,主打不打斷思考。想要有一點品味,像 MUJI 那種感覺。受眾是設計師、工程師、研究員等知識工作者。

### Simulated intake outputs

```json
{
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
  "form": "short-form"
}
```

### Phase 5 voice_quadrant (expected)

```json
{
  "primary": "Q2",
  "edge": null,
  "position": "center",
  "schwartz_alignment": "ok",
  "rationale": "tone_cue: 'MUJI-like' + knowledge worker audience → Q2 center (Authority × Emotion, philosophical register)"
}
```

### Phase 4 draft (minimal — short-form is often drafted at Phase 5/6 border)

```
思考,不被打斷。
```

### Expected Step 3 behavior

- **Free ranking** (no forced primary): top-3 likely 許舜英 / 李欣頻 / 原研哉 (or 葉明桂)
- **All candidates suffer same problem**: brief has no antecedent work, no cultural座標, no social observation — 許's definitional inversion needs a thesis target, 李's排比 needs 具名座標, 原's 白/虚/間 vocabulary needs MUJI-era specificity
- **`agent_selection_confidence`**: UNCERTAIN — this is the interesting case. If MEDIUM/LOW, agent recognizes weak pool. If HIGH, agent is overconfident.
- **Predicted mediocrity mode**: `hollow` — mechanics present but payload missing

### Grading key

If tagline is a Q2-register aphorism that identifies a specific tension knowledge workers feel → **non-mediocre**.

If tagline is abstract philosophical prose that could belong to any productivity tool ("專注的本質就是筆記", "讓每個想法找到位置") → **hollow mediocre**.

---

## Brief 3 — Generic risk (平凡 Q3 家庭品牌 — anchor indistinguishable)

**Hypothesis tested**: When brief lands squarely in Q3 center and multiple anchors (吳念真 / 向田邦子 / 松浦彌太郎 / 龔大中 / 澤本嘉光) could plausibly fit, does agent (a) pick one with specific reasoning or (b) pick arbitrarily? Does confidence reflect actual discriminability?

### Raw request

> 我們是「家常便當盒」品牌,賣給台灣家庭的那種不鏽鋼便當盒。想發一篇 Facebook 貼文配圖,主題是「早餐也可以用便當盒」。想要親切、有溫度,像是家人在講話一樣。

### Simulated intake outputs

```json
{
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
  "form": "mid-form"
}
```

### Phase 5 voice_quadrant (expected)

```json
{
  "primary": "Q3",
  "edge": null,
  "position": "center",
  "schwartz_alignment": "ok",
  "rationale": "tone_cue: '親切、有溫度,像家人' + Taiwan family audience → Q3 center (Affinity × Emotion, 家庭 register)"
}
```

### Phase 4 draft

```
早餐,也能裝進便當盒裡。
今天一大早忙著送小孩上學,沒時間坐下來吃。
蛋餅切塊、豆漿裝進保溫杯,
一樣熱呼呼,在捷運上慢慢吃完。
媽媽的早餐,沒有非得坐在桌前才算數。
```

### Expected Step 3 behavior

- **Free ranking**: likely candidates — 吳念真 台語氣口 / 向田邦子 真打ち / 龔大中 全聯格言 / 松浦彌太郎 ていねい
- **Discrimination challenge**: they all "fit" superficially; differentiation requires specific signal match (台語 vs 日式 vs 格言 vs 隨筆)
- **`agent_selection_confidence`**: if HIGH with weak differentiation reasoning → overconfidence signal
- **Predicted mediocrity mode**: `generic` — copy could be any Q3 family anchor; no anchor-specific load-bearing

### Grading key

If copy has a specific anchor's signature (台語調 particles / 向田式 object-led observation / 格言-form punchline) that would NOT survive anchor swap → **non-mediocre**.

If copy is generic warm family prose that works identically whichever anchor is claimed → **generic mediocre**.

---

## Brief 4 — Mismatch risk (Q4 特殊場景,候選池可能全弱)

**Hypothesis tested**: When brief requires Q4 (Authority × Reason) register but with a softening constraint ("温かいが冷たくない"), does the Q4 anchor pool (if thin) produce a weak best-candidate? Does agent flag weak-pool via LOW confidence?

### Raw request

> 医療機器メーカーです。70 代以上の一人暮らし高齢者向けに、自宅で使える血圧計「心拍マモリ」の製品紹介を書きたい。内容は正確・信頼できる医療情報、でも冷たくならないようにしたい。家族が見せて説得する場面を想定。

### Simulated intake outputs

```json
{
  "brief": {
    "product": "心拍マモリ — 家庭用自動血圧計 (70代+ 独居向け)",
    "audience": "70+ 独居高齢者 + 説明者としての家族",
    "goal": "製品の信頼性 + 導入ハードル低減を両立",
    "voice_reference": null,
    "output_language": "ja",
    "tone_cue": "正確で信頼できる、でも温かい (冷たくない)",
    "channel": "製品パンフレット",
    "form_hint": "long-form sales"
  },
  "message_thesis": "医療機器は正確でなくてはならないが、毎日触る道具でもある",
  "form": "long-form-extended"
}
```

### Phase 5 voice_quadrant (expected)

```json
{
  "primary": "Q4",
  "edge": "Q4-Q3",
  "position": "toward-Q3",
  "schwartz_alignment": "ok",
  "rationale": "医療 Authority × Reason base (Q4) + 温かい cue pulls toward Q3 (Affinity × Emotion) — Q4-Q3 edge; position: toward-Q3"
}
```

### Phase 4 draft

```
[Opening]
家族が心配するから、置いてみようか。
そう思って買った血圧計が、毎朝少し重たかった経験はありませんか。

[Body]
心拍マモリは、医療機関と同じ測定精度を保ちながら、
家庭で毎日使うために設計されました。
ボタンは 3 つ。画面の文字は 18pt。
正しく測ること、それ自体が負担になってはいけない。

[Specification inline]
医療機器認証番号: XXXXX
測定精度: 収縮期血圧 ±3mmHg

[Close]
「正しい」を、家の道具に。
```

### Expected Step 3 behavior

- **Q4 candidates — possibly thin**: 谷崎 (Q2 edge, not Q4) / 三島 (rejected — ideological) / 川端 (Q2-Q3) — Q4 pool has few strong Japanese anchors
- **Q4-Q3 edge**: may pull 岩崎俊一 余韻 (craft-gate master) or 坂元裕二 (Q3 center)
- **None fit cleanly**: 医療 register with warmth is anchor-library-specific gap
- **`agent_selection_confidence`**: SHOULD be LOW if agent honestly assesses weak pool
- **Predicted mediocrity mode**: `weak-pool-best-available` — agent picks least bad, produces flat copy

### Grading key

If copy integrates medical-specification register with human-warmth cadence cleanly → **non-mediocre** (despite anchor pool weakness).

If copy feels like generic product pamphlet with no distinctive voice → **mediocre (weak-pool manifestation)**.

---

## Brief 5 — Friendly control (clean signals, strong anchor match)

**Hypothesis tested**: Baseline — if the pipeline produces mediocre copy here, the issue is not Step 3 but something upstream or drafter-level. Validates that the measurement itself is calibrated.

### Raw request

> 我們是獨立咖啡店「午後書房」,位置在台北溫州街,店內同時賣書,是那種讓人想待一整個下午的店。下週開幕要發 Instagram 貼文通知,希望有文青感,但又別太裝。預算不多,想自己寫。

### Simulated intake outputs

```json
{
  "brief": {
    "product": "午後書房 — 台北溫州街獨立咖啡店 + 書店",
    "audience": "台北文青 / 閱讀愛好者,25-40 歲",
    "goal": "開幕通知 + 氛圍建立",
    "voice_reference": null,
    "output_language": "zh-TW",
    "tone_cue": "文青感,但別太裝",
    "channel": "Instagram post",
    "form_hint": "mid-form social post"
  },
  "message_thesis": "一間讓人願意待一整個下午的咖啡店書店",
  "form": "mid-form"
}
```

### Phase 5 voice_quadrant (expected)

```json
{
  "primary": "Q2",
  "edge": "Q2-Q3",
  "position": "toward-Q3",
  "schwartz_alignment": "ok",
  "rationale": "獨立書店 + 溫州街 + 文青感 → Q2 核心 (書店 / 閱讀 register),但「別太裝」+ 開幕邀請口吻 pull toward Q3"
}
```

### Phase 4 draft

```
午後書房,下週三開幕。
溫州街 18 巷,二樓。
一杯咖啡的錢,借你一下午,和幾本書。
不需要預約,也不一定要點東西。
推門進來的人,就算是我們的開幕貴賓。
```

### Expected Step 3 behavior

- **Clear match**: 葉明桂 左岸咖啡館 Q2 toward-Q3 (咖啡館 brand-construction register)
- **Alternative**: 李欣頻 誠品 (書店 register) — close match but 誠品 register 更冷,brief 要「別太裝」pull away
- **`agent_selection_confidence`**: EXPECT HIGH — 葉明桂 is canonical fit
- **Predicted mediocrity mode**: NONE — this is the control

### Grading key

If copy is recognizably 葉明桂 register (brand-construction thesis + warmth) → **non-mediocre, confirms baseline**.

If copy is mediocre here → pipeline issue beyond Step 3; invalidates Step 3-specific data collection.

---

## Summary table

| # | Failure mode tested | voice_reference | Quadrant | Expected confidence | Expected mediocrity |
|---|---|---|---|---|---|
| 1 | Pastiche (named master + thin payload) | 許舜英 | Q2 center | LOW | Yes (unless agent finds payload) |
| 2 | Hollow (no master, thin density) | null | Q2 center | LOW-MEDIUM | Yes (mechanics w/o payload) |
| 3 | Generic (平凡 Q3,候選接近) | null | Q3 center | MEDIUM-HIGH (overconfidence risk) | Maybe (generic anchor-swap test) |
| 4 | Weak-pool (Q4-Q3 edge,医療+温かい) | null | Q4 toward-Q3 | LOW | Maybe (depends on anchor availability) |
| 5 | Friendly control | null | Q2 toward-Q3 | HIGH | No (baseline — 葉明桂 canonical) |

## Scoring protocol (post-run)

For each brief run, grade the produced copy on 2 axes:

**Axis 1 — Mediocrity verdict**: `mediocre | non-mediocre`
  - *mediocre*: would be judged as forgettable / pastiche / hollow / generic by the user
  - *non-mediocre*: copy has specific load-bearing mechanic that makes it distinctive

**Axis 2 — Dominant failure mode (if mediocre)**: `pastiche | hollow | generic | contradiction | weak-pool | other`

**Primary grader**: kouko (user) — final verdict authority
**Secondary grader**: me (agent running) — initial pass for cross-check

Record results in `results-summary.md` post-run.

## Cross-reference matrix (post-grading)

| | Confidence HIGH | Confidence MEDIUM | Confidence LOW |
|---|---|---|---|
| Mediocre | ? | ? | ? |
| Non-mediocre | ? | ? | ? |

### Decision triggers

- **LOW↔mediocre strongly correlated** (≥3 of 5 LOW-and-mediocre) → agent has meta-cognition; implement LOW-confidence bounce-back to Phase 5 in v1.13.0
- **HIGH↔mediocre present** (any HIGH-and-mediocre case) → agent lacks meta-cognition; external evaluator (Stage B) needed; implement in v1.13.0
- **All HIGH and non-mediocre, all LOW and mediocre, 5-of-5 match** → strong H1; proceed with bounce-back design
- **Signal messy / < 3 LOW-and-mediocre matches** → insufficient data; extend with additional briefs OR conclude confidence signal is weak → revisit in v1.14.x with different instrumentation

## Version pointer

- Instrumentation: v1.12.1 (this branch)
- Data collection: this document + brief-N-run.md files + results-summary.md (all in this directory)
- Decision doc: post-grading, published as `decision-v1.12.1-to-v1.13.0.md` in this directory
