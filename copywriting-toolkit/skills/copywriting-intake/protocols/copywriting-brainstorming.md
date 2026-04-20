# Copywriting Brainstorming Protocol

Derive clear production specs from a vague copy request. A checklist-driven
dialogue process. Do not proceed to copy creation until completion.

## Primary Sources

- `../standards/voice-and-tone.md` — Ogilvy / 糸井 / 岩崎 / 18F /
  Mailchimp voice axes. Task 6 voice selection options are based on
  §JP emotional-resonance tradition and §Ogilvy long-copy voice classics.
- `../standards/persuasion-psychology-anchor.md` — Schwartz 1966
  *Breakthrough Advertising* 5 levels of awareness. Task 5 long-form
  awareness level field is based here (Unaware / Problem-Aware /
  Solution-Aware / Product-Aware / Most-Aware).
- `../standards/short-form-catchcopy-canon.md` — §5 approach angles
  decision tree (benefit / fear / disruptive / target call-out /
  interactive question). Task 7 short-form approach selection is
  based here.
- `../standards/long-form-pasona-canon.md` — 旧 / 新 / PASBECONA
  usage rules. Basis for Task 7 long-form framework recommendation.
- `../standards/mid-form-beaf-canon.md` — BEAF (Benefit → Evidence
  → Advantage → Feature) scope (楽天 / Amazon / POP / briefing).
- Structural precedent: `../../planning-team/protocols/planning-brainstorming.md`
  — sequential checklist + Socratic grill + Understanding Summary +
  user confirmation gate canonical pattern. This protocol rewrites that
  structure for copywriting use.

## Hard Gate

Do NOT load `write-long-form-copy.md` / `write-mid-form-copy.md` /
`write-short-form-copy.md` / `copy-ideation-parallel.md` /
`copy-audit.md`, generate any copy draft, or dispatch ideation
subagents **until** this checklist is fully completed **and** the
user has explicitly approved the Understanding Summary.

Level 1 fields (form type / product / audience / form-specific must
fields) that remain missing will cause `intake-completeness-checklist.md`
MUST gate to return FAIL_FATAL → NEEDS_REVISION, resulting in BLOCKED.

## Template Rendering Rule

Q1-Q10 templates below are written in English as the baseline. Worker
MUST render each question in the user's `output_language` at runtime:

- `output_language: ja` → render in 日本語
- `output_language: en` → render in English (baseline)
- `output_language: zh-TW` → render in 繁體中文

Two representative questions (Q2 audience, Q7 framework) are shown
fully rendered in all 3 languages below as pattern examples. For
other questions, worker applies the same localization style.

## Checklist

Complete each task in order. Each task requires user input (or an
explicit "adopt recommendation") before proceeding. One question per
message. Prefer multiple choice with a **recommended answer** when
possible.

### Q1. Understand the request

Read the user's request **without judging**. Even a vague request
like "write me a キャッチコピー" is OK at this stage. Do not ask
questions here. Paraphrase what the user literally said in 1-2
sentences to confirm.

- Corresponds to ヤング (1988 JP translation) 『アイデアのつくり方』
  **material collection** stage. Absorb information without judging.
- If the request already contains form type / product / audience,
  do not re-ask those in subsequent Tasks ("don't ask what you can look up" rule).

### Q2. Identify form type

Determine what to write. Multiple choice:

- **Long-form** (LP / sales letter / advertorial / mail-magazine)
- **Mid-form** (EC product description / 楽天 / Amazon / in-store POP / briefing)
- **Short-form** (キャッチコピー / tagline / headline / SNS / banner)
- **Ideation Workshop** (diverge candidate angles from value prop → seed for subsequent protocol)
- **Audit** (review + improvement proposal for existing copy)

Recommend based on the request context (e.g., "10 LP headlines" →
Ideation or Short-form). Ask for clarification if ambiguous.

**[Triple-language rendering example — Q2]**

> **ja**: 何を書きますか？ 選択肢：
> - **ロングコピー**（LP / セールスレター / 記事広告 / メルマガ）
> - **中尺コピー**（EC 商品説明 / 楽天 / Amazon / 店頭 POP / 説明会）
> - **ショートコピー**（キャッチコピー / tagline / headline / SNS / banner）
> - **発想ワークショップ**（value prop から候補角度を発散 → 後続 protocol の種）
> - **コピーレビュー**（既存コピーのレビュー + 改善提案）
>
> 依頼文脈から推薦します（例：「LP の headline 10 本」→ 発想 or ショートコピー）。曖昧なら確認します。

> **en**: What do we write? Options:
> - **Long-form** (LP / sales letter / advertorial / mail-magazine)
> - **Mid-form** (EC product description / 楽天 / Amazon / in-store POP / briefing)
> - **Short-form** (キャッチコピー / tagline / headline / SNS / banner)
> - **Ideation Workshop** (diverge candidate angles from value prop → seed for subsequent protocol)
> - **Audit** (review + improvement proposal for existing copy)
>
> I'll recommend based on your request context (e.g., "10 LP headlines" → Ideation or Short-form). If ambiguous, I'll ask.

> **zh-TW**: 要寫什麼？ 選項：
> - **長文案**（LP / 銷售信 / 業配文 / 電子報）
> - **中文案**（EC 商品說明 / 樂天 / Amazon / 店頭 POP / 說明會）
> - **短文案**（キャッチコピー / tagline / headline / SNS / banner）
> - **發想工作坊**（從 value prop 發散候選角度 → 後續 protocol 的種子）
> - **審稿**（既有文案的 review + 改善提案）
>
> 我會根據你的需求脈絡推薦（例：「LP headline 10 條」→ 發想 or 短文案）。不明確的話會確認。

### Q3. Clarify product / service

**Level 1 Must field** (BLOCKED if missing).

- What product / service?
- Core value proposition (in 1 sentence)
- If PRODUCT-SPEC.md / planning-team output already exists, point to
  it and read to extract ("don't ask what you can look up")

If the user proceeds without clarity, the 5 approaches / Schwartz
level / BEAF benefit stage all become unselectable. If the user cannot
verbalize the value prop, recommend `planning-team` and return BLOCKED.

### Q4. Identify target audience

**Level 1 Must field** (BLOCKED if missing). Depth varies by form type.

- **Short-form**: Prioritize confirming target emotion / pain
  ("What feeling do you want to address? / What pain point to target?")
  → prerequisite for the 5-approach map in Q7.
- **Long-form**: Confirm demographic + **Schwartz awareness level**
  (5 levels: Unaware / Problem-Aware / Solution-Aware /
  Product-Aware / Most-Aware). Recommendation: AI infers from product
  type + market maturity → user confirms or corrects.
- **Mid-form**: Confirm channel-assumption audience (楽天 users /
  Amazon Prime members / in-store POP shoppers, etc.).
- **Ideation / Audit**: Ask under the umbrella of the relevant form
  type above.

### Q5. Form-specific Level 1 fields (branching)

Obtain additional required fields based on form type.

- **Long-form**:
  - Word-count range (e.g., 800-1,200 / 2,000-3,000 / 5,000+ chars)
  - Schwartz awareness level (confirm here if not settled in Q4)
  - Framework recommendation based on `long-form-pasona-canon.md`
    §usage table: short-mid text → 旧 PASONA, mid-long text →
    新 PASONA, heavy persuasion → PASBECONA.
- **Mid-form**:
  - Benefits list (**concrete 3+ items**, no abstract terms)
  - Channel (楽天 / Amazon JP / in-store POP / briefing)
- **Short-form**:
  - Target emotion / pain (skip if already obtained in Q4) →
    prerequisite for 5-approach map
  - Intended channel (SNS / banner / tagline / CM, etc.)
  - Character limit (default 15 chars; JP 7-15 char band is canonical)
- **Ideation Workshop**:
  - Number of candidates (default 5, recommend 3-5 range)
  - Value prop source (user-supplied / planning-team /
    PRODUCT-SPEC / other)
- **Audit**:
  - Existing copy full text (original required, not a summary)
  - Review focus (framework / ethics / voice / form-appropriate / overall)

### Q6. Voice / tone preference (Level 2)

**Step 1 — Voice quadrant (optional, macro positioning)**: from
`voice-quadrant-positioning.md`:

- **Q1 Authority-Reason** — B2B, finance, medical, technical.
  Representatives: 葉明桂 / 林育聖 / Ogilvy / 報導者.
- **Q2 Authority-Emotion** — premium / luxury / bookstore / manifesto.
  Representatives: 許舜英 / 李欣頻 / 誠品 / Apple / MUJI.
- **Q3 Affinity-Emotion** — everyday retail, family, social.
  Representatives: 龔大中 / 盧建彰 / 全聯 / IKEA / 糸井 / 岩崎.
- **Q4 Affinity-Reason** — e-commerce, app onboarding, action push.
  Representatives: 織田紀香 / Shopee / Amazon.

Recorded as `voice_quadrant: Q1 | Q2 | Q3 | Q4 | not-declared`.
If declared, gate Dim 5 (Voice Quadrant Coherence) fires.

**Step 2 — Voice maestro (optional, tactical reference)**:

- **糸井系** (state-proposal, ambiguity, particle endings) —
  `voice-and-tone.md` §JP 情緒共鳴傳統 §糸井. Q3 quadrant.
- **岩崎系** (life philosophy, seasonal sensibility, warmth of life) —
  same §岩崎. Q3 quadrant.
- **眞木系** (掛詞, phonetics, short-form craft) — representative work:
  「恋が着せ、愛が脱がせる。」lineage. Q2↔Q3 border.
- **谷山系** (entry design, separating "what you want to write" from
  "what you want to say") — `../standards/ideation-taniyama-discipline.md`
  overall.
- **Ogilvy系** (benefit-clear, respect the reader, fact-based) —
  `voice-and-tone.md` §Ogilvy long-copy voice classics. Q1 quadrant.
- **龔大中系** (經濟美學 observational wit — ZH) — `voice-quadrant-
  positioning.md` §Q3 ZH entries. Q3 quadrant.
- **許舜英系** (意識形態廣告 literary-ideological — ZH) —
  `voice-quadrant-positioning.md` §Q2 ZH entries. Q2 quadrant.
- **Default** (AI recommends based on audience + form + channel; user
  approval demotes to Level 3).

If the brand already has a voice guide, honor it and skip this Task.

### Q7. Framework / approach preference (Level 2 — branching)

Options differ by form type:

- **Long-form**:
  - 旧 PASONA (short-mid text, DM / email)
  - 新 PASONA (mid-long LP / mail-magazine, Affinity entry)
  - PASBECONA (2,000+ char band, B/E/C adds persuasion depth)
  - Recommendation based on Q5 word-count range + Q4 awareness level;
    AI proposes (if undetermined, default to Solution-Aware + 新 PASONA).
- **Mid-form**:
  - BEAF (Benefit → Evidence → Advantage → Feature) default.
  - Confirm channel-dependent order tweaks (POP = Benefit-heavy /
    briefing = Evidence-heavy, etc.).
- **Short-form** (キャッチコピー / tagline, 7-15 chars):
  - 5 approaches (benefit / fear / disruptive / target call-out /
    interactive question). AI recommends based on audience emotion per
    `short-form-catchcopy-canon.md` §5 approach angles decision tree.
- **Light-action** (opt-in / subscribe / download / LP click-through,
  50-1,500 chars, micro-conversion per Kaushik 2007):
  - **PREP 法** (4 stages: Point-Reason-Example-Point) — logical
    payload, no explicit CTA. Best for SNS posts, email openers,
    presentation slides, share-triggering content.
  - **CREMA 法** (5 stages: Conclusion-Reason-Evidence-Method-Action)
    — explicit Action stage. Best for opt-in pages, newsletter
    subscribe, free-download LPs, LINE 登録, light affiliate.
  - See `light-action-frameworks.md` §Selection criteria. AI
    recommends CREMA as default for any non-purchase action prompt;
    PREP for share-triggering / non-CTA logical content.
  - **Action-weight routing**: if brief turns out to target
    high-ticket purchase (heavy action), re-route to Long-Form
    framework selection above (PASONA-family / QUEST / PASTOR).
- **Ideation**:
  - Mandal-Art 8 fan-out + VS / VS standalone / short-form 5-approach
    integration — recommend per `copy-ideation-parallel.md` §Phase 1
    tool combination decision.
- **Audit**:
  - If form type is known, apply the same framework; if unknown,
    use `copy-audit.md` Type ID step for preliminary estimation.

**[Triple-language rendering example — Q7]**

> **ja**: フレームワーク / アプローチを選んでください：
>
> **ロングコピーの場合**:
> - 旧 PASONA（短中尺、DM / メール向け）
> - 新 PASONA（中長尺 LP / メルマガ、Affinity 入口）— **推薦**
> - PASBECONA（2000 字+、B/E/C で説得力を厚くする）
>
> Task 5 の字数範囲 + Task 4 の awareness level に基づき推薦します。
> 未確定の場合は Solution-Aware + 新 PASONA をデフォルトとします。
>
> **ショートコピーの場合**:
> - 利益 / 願望
> - 恐怖 / ペインポイント
> - 常識破り
> - ターゲット呼びかけ
> - 問いかけ
>
> audience の emotion から AI が推薦します。

> **en**: Choose a framework / approach:
>
> **For long-form**:
> - 旧 PASONA (short-mid text, for DM / email)
> - 新 PASONA (mid-long LP / mail-magazine, Affinity entry) — **recommended**
> - PASBECONA (2,000+ chars, B/E/C adds persuasion depth)
>
> Recommendation based on Q5 word-count range + Q4 awareness level.
> If undetermined, defaults to Solution-Aware + 新 PASONA.
>
> **For short-form**:
> - Benefit / aspiration
> - Fear / pain point
> - Disruptive
> - Target call-out
> - Interactive question
>
> AI recommends based on audience emotion.

> **zh-TW**: 選擇框架 / 切入方式：
>
> **長文案**:
> - 舊 PASONA（短中文、DM / 電子郵件用）
> - 新 PASONA（中長文 LP / 電子報、Affinity 入口）— **推薦**
> - PASBECONA（2000 字+、B/E/C 增加說服深度）
>
> 根據 Q5 字數範圍 + Q4 awareness level 推薦。
> 未確定時預設為 Solution-Aware + 新 PASONA。
>
> **短文案**:
> - 利益 / 願望
> - 恐怖 / 痛點
> - 顛覆常識
> - 目標呼喚
> - 提問互動
>
> AI 根據受眾情緒推薦。

### Q7.5. Neta injection opt-in (Level 3 — default No)

Ask whether the copy may inject cultural references per
`neta-injection-techniques.md` (4 techniques: **Reversal** /
**Substitution** / **Subcultural Capital** / **Cross-domain Mapping**)
and `neta-websearch-pipeline.md` (Phase A-D pipeline). Default: **No**
(neta injection off).

When to flag **Yes**: brand voice explicitly allows cultural references;
campaign is SNS-native (ULSSAS-era) UGC-triggering OR campaign
leverages literary/classical allusion for brand sophistication,
cultural authority, or long-lived copy; audience profile is well-defined
(not broad general-public); shelf life ≤6 months for SNS/meme sources
(memes expire per Shifman 2014) OR using literary/classical sources
(evergreen by definition) OR using evergreen-only techniques (Technique
1 Reversal on classics + Technique 4 Cross-domain Mapping).

When to default **No**: brand voice / channel policy forbids neta;
audience is broad (general-public); high-stakes legal / regulated
context (finance, healthcare, pharma).

**If user sets Yes — follow-up: source-type preference.**
Ask: "Which source types are acceptable for this brief?" Options:
- `all` (default) — SNS/meme + literary + contemporary culture
- `sns-meme` — SNS/meme and contemporary culture only
- `literary` — classical literature, modern literature, quotes only
- `mixed` — explicitly combining SNS and literary sources

If user sets Yes: route the resulting workflow through **Neta
Injection Overlay** variant (see `SKILL.md §Workflows`) — base-
framework draft + `copy-neta-injection.md` Phase A-D + `neta-safety-
gate.md` SHOULD gate (with hard legal vetoes on copyright + 景表法
ステマ告示 per 消費者庁 2023-10-01).

Record in Understanding Summary as:
`neta_opt_in: Yes | No`
`neta_source_type_preference: all | sns-meme | literary | mixed`
(only when neta_opt_in = Yes).

### Q8. Grill — challenge assumptions

Using the information collected in Q1-Q7.5, question the user's
intent and assumptions to build shared understanding. One question
at a time.
Attach a **recommended answer** to each question. Adapted from the
3-axis grill in `planning-brainstorming.md` §Task 4b Grill for
copywriting:

- **Challenge premises**: "You mentioned X, but considering the
  audience's awareness level, would approach Y be more effective?"
  Example: "Specifying a direct Offer closer for a Problem-Aware
  audience violates the Schwartz 1966 core rule — entering via
  Affinity with 新 PASONA is canonical. Was this intentional?"
- **Dig into dependencies**: "If the audience assumption turns out to
  be wrong, would the entire copy need rewriting? Locking the key
  fields before divergence reduces backtracking."
- **Boundary conditions**: "Are there expressions to ethically avoid?
  For example, '業界 No.1' or '24 時間限定' carry 景品表示法 risk
  for superlative / scarcity claims. Disparaging competitors, fake
  deadlines, and fabricated testimonials are also flagged."
- **Voice conflict check**: "Does the existing brand voice guide
  conflict with the Q6 selection? The voice guide takes priority over
  framework (`voice-and-tone.md` §Framework と voice の接点)."

Do not ask questions whose answers can be found in the request text /
PRODUCT-SPEC / existing brand assets — look them up yourself. Continue
until no unresolved branches remain, or the user says to move on.

### Q9. Produce Understanding Summary

Before proceeding to the Q10 user confirmation gate, present a
structured summary of understanding:

```
## Understanding Summary

### Request
[User's request paraphrased in Q1]

### Form Type
[long / mid / short / ideation / audit]

### Product / Value Proposition
[Confirmed in Q3]

### Target Audience
[demographic / persona / Schwartz level (long) / emotion (short)]

### Form-Specific Spec
[Confirmed in Q5 — word count / channel / benefits / candidate count, etc.]

### Voice Reference
[Q6 selection — 糸井 / 岩崎 / 眞木 / 谷山 / Ogilvy / default]

### Framework / Approach
[Q7 selection — 新 PASONA / BEAF / 利益切入, etc. + recommendation basis]

### Confirmed Assumptions
[Assumptions verified in Q8 grill]

### Resolved Ambiguities
[Issues that were ambiguous but resolved]

### Level 2/3 Defaults Accepted
[Items where the user did not choose and adopted the AI default —
 intake-completeness-checklist PASS_WITH_NOTES target]
```

### Q10. User confirmation gate

Present the Understanding Summary and offer the following options:

- **Confirm — start writing** → load the next-phase protocol per form
  type (`write-long-form-copy.md` / `write-mid-form-copy.md` /
  `write-short-form-copy.md` / `copy-ideation-parallel.md` /
  `copy-audit.md`)
- **Adjust item** → return to the relevant Task for re-confirmation
- **Start over** → restart from Q1 (when the user fundamentally
  changes the request)

Do not proceed to the next phase without the user's explicit
confirmation. **Silent proceed is prohibited**.

## Rules

- **One question at a time**. Do not bundle multiple questions into
  one message.
- **Multiple choice first**. Prefer options over open-ended questions.
- **Attach a recommended answer to each question**. Do not just ask —
  also propose (in Q6/Q7, present AI-inferred recommendations based on
  audience + form).
- **Don't ask what you can look up**. Read information obtainable from
  the request text / PRODUCT-SPEC / existing voice guide before asking
  the user — only ask about missing parts.
- **Understanding Summary is a hard gate**. Do not load the next-phase
  protocol until the user gives explicit confirmation.
- **Level 1 missing → BLOCKED**. If any of form type / product /
  audience / form-specific must fields remain unobtained after one
  round of questioning, `intake-completeness-checklist.md` returns
  FAIL_FATAL → NEEDS_REVISION.
- **Level 2 default adoption is disclosed in Summary**. Items where
  the user did not choose and AI recommendation was adopted are
  disclosed in Understanding Summary §Level 2/3 Defaults Accepted.
  Silent defaults are prohibited (intake gate FAIL_FIXABLE).
- **voice guide > framework**. If the existing brand voice guide
  conflicts with the Q6 selection, voice guide takes priority.
- **Do not skip the grill**. Even when the request is clear, Q8 may
  be abbreviated but not fully skipped (minimum 1 question: ethics
  boundary condition).

## Anti-Patterns

- **Batch questioning**: "Form type? Audience? Word count? Voice?" all
  in one message. Increases user's cognitive load and lowers answer
  quality. Follow the one-question-per-message rule.
- **Skipping Q8 grill to jump to Q9**: Writing the Summary without
  assumption verification allows silent assumptions to pass through to
  the next phase, causing "audience assumption was wrong" rework
  downstream.
- **Proceeding to next phase with Level 1 missing**: Loading
  `write-*.md` with form type / product / audience incomplete is an
  intake gate violation. Always return BLOCKED.
- **Asking voice preference open-ended**: "What voice should we write
  in?" is unanswerable for the user. Reduce burden with 糸井 / 岩崎 /
  眞木 / 谷山 / Ogilvy / default multiple choice + representative work
  samples for each.
- **Asking when the answer is already in the request**: User writes
  "Amazon JP product description, 800 chars" and you ask "What form
  type?" — this erodes trust. Read what you can, then ask only about
  gaps.
- **Questions without recommendations**: Asking "Which of the 5
  approaches?" without a recommendation. AI should infer from audience
  emotion + product type and add "I recommend 利益切入, because ~".
- **Silent default adoption**: AI adopts its own recommendation for
  Level 2 because the user did not choose, but does not write it in
  the Summary. Must disclose in §Defaults Accepted.
- **Loading next protocol without confirmation**: Presenting the
  Understanding Summary and immediately "Now loading
  write-long-form-copy.md". Wait for the user's explicit confirmation.
