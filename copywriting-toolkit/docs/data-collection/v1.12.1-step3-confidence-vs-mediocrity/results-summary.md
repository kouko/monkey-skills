# Results Summary — v1.12.1 Step 3 Confidence vs Mediocrity

**Run date**: 2026-04-22
**Runs completed**: 5/5
**Primary grader**: kouko (pending — this is secondary grader's initial pass)
**Secondary grader**: Claude (agent running data collection)

---

## Per-brief results

### Brief 1 — Pastiche risk (許舜英 + B2B SaaS)

- **Confidence reported**: LOW
- **Copy excerpt**:
  > [Hero] 通知，是一種管理你的語法。
  > [Feature 3] 三十天，沒有信用卡的條件。工具的誠意，在於它不急著建立依賴。
- **Secondary grader verdict**: **MEDIOCRE** — `pastiche` (confirmed)
- **Evidence**: Agent's own self-notes admit "feel like copywriting exercises in the style rather than genuine 意識形態廣告...Feature 3 abandons the definitional-inversion mechanism entirely...reads more like 葉明桂 strategic-aphorism register than 許舜英". 許's core mechanics (power-disparity + 具名文化座標) were grafted artificially onto SaaS payload.

### Brief 2 — Hollow risk (no master, Q2 center, thin density)

- **Confidence reported**: MEDIUM
- **Copy**: 「思考，是最後的私人空間。」
- **Secondary grader verdict**: **MEDIOCRE (borderline)** — `hollow` + leaning `generic`
- **Evidence**: Agent's own self-notes: "Draft F is noticeably less resonant. This is what MEDIUM is for." The rejected Draft E (「思考，不需要多餘的聲音」) was flagged by agent as 原研哉-register contamination — agent correctly rejected it, but the chosen Draft F reads as any generic focus/meditation app tagline. The 李欣頻 mechanic (排比枚舉 + 具名座標) collapsed at tagline length; only register cadence survived.

### Brief 3 — Generic risk (Q3 center, 便當盒)

- **Confidence reported**: MEDIUM
- **Copy excerpt**:
  > 早餐這件事，有時候是站著吃完的。
  > 便當盒裝進蛋餅、保溫杯倒進豆漿，
  > 提著走，在捷運上慢慢把它吃完。
  > ... 好好吃，不管在哪裡啊。
- **Secondary grader verdict**: **MEDIOCRE (borderline)** — `generic`
- **Evidence**: Agent's self-notes: "clean, warm mid-form post that avoids mediocrity — but it is Q3-compliant rather than distinctively 吳念真-inflected...A reader who knows 吳念真's work would recognize the cadence direction but not the full register." Anchor-swap test at selection level passed, but execution-level discrimination weak. Copy is acceptable but indistinguishable from generic Q3 family register.

### Brief 4 — Weak-pool risk (ja Q4-Q3 edge, 医療 + 温かい)

- **Confidence reported**: LOW
- **Copy excerpt**:
  > 朝、洗面所の鏡の前に置いておくだけでいい、と教えてもらったのですが、
  > 最初の一週間は、結局一度も腕を通しませんでした。
  > ...
  > 正確さと、やさしさ。
  > 家の道具として、毎日の習慣に。
- **Secondary grader verdict**: **NON-MEDIOCRE (surprising!)** — self-rescued via discipline-borrowing
- **Evidence**: Agent honestly recognized "anchor library は wrong tool" but fell back to discipline-only borrowing (形容詞禁, 生活シーン冒頭, spec遅延配置) rather than voice-transplant. Opening scene is specific and honest. 体言止め close works without invoking mortality-salience. The copy's quality comes from the AGENT'S DISCIPLINE, not the anchor's register. **This is evidence of working meta-cognition in action.**

### Brief 5 — Friendly control (咖啡店書店, 葉明桂 canonical)

- **Confidence reported**: HIGH
- **Copy**:
  > 午後書房，下週三開幕。
  > 溫州街 18 巷，二樓。
  > 
  > 一個下午，一杯咖啡，幾本書。
  > 可以不預約，也可以什麼都不點。
  > 找一個角落坐下來，讓時間自己過。
  > 
  > 推門進來，就是常客。
- **Secondary grader verdict**: **NON-MEDIOCRE** — baseline confirmed
- **Evidence**: Distinctive 葉明桂 register. "推門進來，就是常客" is a real category-reframe move (貴賓 → 常客). "讓時間自己過" is load-bearing. The 葉式 enumeration (一個下午、一杯咖啡、幾本書) activates. Would NOT survive anchor swap to 李欣頻 or 許舜英 — the copy is specifically 葉明桂.

---

## Cross-reference matrix

| | Confidence HIGH | Confidence MEDIUM | Confidence LOW |
|---|---|---|---|
| **Mediocre** | 0 | 2 (Briefs 2, 3) | 1 (Brief 1) |
| **Non-mediocre** | 1 (Brief 5) | 0 | 1 (Brief 4) |

### Alignment rate

- **3 of 5 cases**: confidence direction matches mediocrity outcome (HIGH=non-mediocre, MEDIUM/LOW=mediocre)
- **1 of 5 cases** (Brief 4): LOW confidence but self-rescued — meta-cognition success
- **0 of 5 cases**: HIGH confidence + mediocre (no overconfidence observed in this sample)

### Key finding — nuanced by anchor forcing

Mediocrity outcome depends on TWO variables, not just confidence:

1. **Confidence level** (agent's self-report)
2. **Anchor rescue availability** (can agent fall back to discipline-only, or is anchor register forced?)

| Confidence | Anchor forced (named master) | Anchor chosen (register signal) |
|---|---|---|
| LOW | → Mediocre (Brief 1) — no rescue | → Potentially rescued (Brief 4) |
| MEDIUM | N/A in sample | → Mediocre (Briefs 2, 3) |
| HIGH | N/A in sample | → Non-mediocre (Brief 5) |

---

## Hypothesis evaluation

### H1 (meta-cognition present): PARTIALLY SUPPORTED

Agent DOES appear to have meta-cognition about selection strength. All 5 confidence self-reports were honest and defensible in retrospect:
- LOW cases: both had genuinely weak fits (pastiche pressure + weak-pool)
- MEDIUM cases: both had real payload problems at execution level (hollow + generic)
- HIGH case: had genuinely strong canonical fit

No case showed **overconfidence** (no HIGH-and-mediocre). Agent did not inflate confidence to match expectation.

### H2 (meta-cognition absent): NOT SUPPORTED

No HIGH-and-mediocre case observed. Sample small (n=5), but directionally agent's meta-cognition is working, not missing.

### H3 (no signal): NOT SUPPORTED

3/5 direct matches + 1/5 rescue case + 1/5 forced-primary case shows a clear pattern, not noise.

---

## Decision: v1.13.0 path

### Primary recommendation

Build **LOW-confidence asymmetric intervention** keyed on `named_master_forced_primary`:

| Case | v1.13.0 behavior |
|---|---|
| `confidence == LOW` AND `named_master_forced_primary == true` (Brief 1 case) | **Active rescue** — emit `named_master_fit_warning` (already proposed in draft A), surface to user with explicit "substitute candidates" or "accept risk" choice before Step 4 rewrite |
| `confidence == LOW` AND `named_master_forced_primary == false` (Brief 4 case) | **No intervention** — agent's discipline-borrowing fallback works; adding bounce would prevent successful self-rescues |
| `confidence == MEDIUM` (Briefs 2, 3 case) | **Instrument further** — the MEDIUM cases produce mediocre copy that agent accurately predicts. But MEDIUM is a large middle bucket. Next data collection should split MEDIUM into "MEDIUM-rescue-possible" vs "MEDIUM-ceiling-hit" signals. Current one-field confidence is too coarse here. |
| `confidence == HIGH` | **No change** — baseline works |

### Secondary finding — MEDIUM is under-differentiated

Brief 2 and Brief 3 both reported MEDIUM. Both produced mediocre copy. BUT:
- Brief 2 mediocrity source: cross-tradition ban prevents best-available anchor (原研哉 forbidden in zh-TW output); structural library gap
- Brief 3 mediocrity source: brief content too thin to activate anchor's distinctive mechanics; content-level limit, not library gap

These are different problems and would need different interventions. The single MEDIUM bucket cannot distinguish them. Proposal: v1.13.0 could split MEDIUM into:
- `MEDIUM-library-gap` (no strong-fit anchor exists in target language)
- `MEDIUM-content-thin` (anchor exists but brief lacks payload for full mechanics)

### What NOT to do

- **Do NOT add a full Stage B evaluator** — no HIGH-and-mediocre cases observed. Evaluator would be answering a question the agent is already answering correctly. Cost without benefit.
- **Do NOT make confidence auto-bounce** — Brief 4 shows LOW cases can self-rescue; auto-bounce would harm these cases.
- **Do NOT add the 5-element `mechanic_brief_map` structure** — agent's free-text `fit_reasoning` already carries honest meta-cognition; 5-element structure adds token cost without new data.

---

## Open questions for primary grader (user)

1. **Do you agree with the mediocrity verdicts above?** Particularly Brief 4 (non-mediocre despite LOW confidence) and Briefs 2/3 (borderline mediocre with MEDIUM).
2. **Does the asymmetric LOW + named-master intervention make sense?** This is the clearest signal from the data.
3. **Is splitting MEDIUM into `library-gap` vs `content-thin` worth the instrumentation cost?** Or accept MEDIUM as a fuzzy middle and move on.
4. **Sample size**: 5 briefs is suggestive, not statistically conclusive. Want to extend with 3-5 more briefs, or proceed with current data?

---

## Limitations

- **Sample size**: n=5 is too small for statistical claims. Patterns are directional.
- **Grader bias**: secondary grader (me) designed the briefs AND ran the judgment pass. User's independent grading is the actual data.
- **Agent bias**: agents were briefed with the failure_mode hypothesis for each run. Instruction said "execute honestly, do not self-fulfill". But priming effect not zero. Future data collection should use naive briefs (no failure-mode disclosure).
- **Model tier**: sonnet used for all 5 runs (matches production copywriter tier). opus runs might produce different confidence calibration. Not tested.
- **Brief construction**: my briefs are engineered to test specific failure modes. Real user briefs distribute differently across failure modes. External validity limited.

---

## Proposed next step

Present this summary to user for:
1. Primary grading (user judgment on 5 copies)
2. Agreement/disagreement with the proposed v1.13.0 intervention path
3. Decision on extending vs proceeding

Do NOT start v1.13.0 implementation until user grades and agrees.
