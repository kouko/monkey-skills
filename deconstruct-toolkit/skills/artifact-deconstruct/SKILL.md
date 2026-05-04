---
name: artifact-deconstruct
description: >-
  Reverse-engineer the design blueprint of any polished artifact (copy,
  document pack, SOP, playbook, presentation, UI screenshot, advertising,
  literature). Surfaces audience targeting, creation sequence, borrowed
  frameworks, rhetorical mechanisms, design patterns, and intentional
  omissions. Outputs a 6-section deconstruction report with ethical
  position verdict. Use when user asks "deconstruct / 拆解 / 反推 /
  reverse engineer" a polished artifact, or "why is this written so
  well" / "what's the design behind this" / "teardown this". Do NOT use
  for code (use sourceatlas), self-thinking (use philosophers-toolkit),
  or summarization (use plain reading).
  制作物の脱構築。文物逆向解構。
---

# Artifact Deconstruct

Reverse-engineer the design decisions behind any polished artifact. The
goal is not summary — it is **design archaeology**: surface what the
creator decided, what frameworks they borrowed, and what they
deliberately omitted.

## When to use

Trigger phrases (any language):

- 「拆解這份」「反推這個」「為什麼這份寫得這麼好」「這份是怎麼設計的」
- "deconstruct this", "reverse engineer", "design behind this", "teardown"
- "why does this work" / "what is this artifact's blueprint"

Skip when:

- User wants a **summary** — use plain reading
- Artifact is < 200 words and not a structured argument — there is not enough design to deconstruct
- Artifact is purely informational reference (Wikipedia, dictionary, raw data) — no *design* to recover
- Target is source code — use `sourceatlas` instead
- Target is the user's own thinking — use `philosophers-toolkit`

## Workflow

Six steps, run in order. Track progress with this checklist:

```
Deconstruction Progress:
- [ ] Step 1: Identify artifact type
- [ ] Step 2: Select lens combination
- [ ] Step 3: Run six-dimension analysis
- [ ] Step 4: Apply selected lenses
- [ ] Step 5: Generate deconstruction report
- [ ] Step 6: Self-check against anti-patterns
```

### Step 1: Identify artifact type

Detect which type the input belongs to. Use signals, not just user
labels.

| Type | Signals |
|---|---|
| Marketing copy / advertising | Short, persuasion-focused, has CTA, hero section |
| Document pack / playbook | Multi-file, README present, role-routed sections |
| Single SOP / how-to | Sequential numbered steps, checklist format |
| Presentation deck | Slide structure (1 slide ≈ 1 idea), visual-heavy |
| Onboarding flow | UI screens or sequential steps, progressive disclosure |
| Long-form article | Argumentative or narrative prose, 1000+ words |
| Speech / political text | First-person plural, emotional cadence, call to collective |
| Literature / film | Narrative, character arcs, symbolic imagery |
| UI screen | Visual layout, interactive elements, status indicators |

Record the detected type. If multiple apply, pick the **dominant** one
and note secondary types in the report.

### Step 2: Select lens combination

Read [protocols/lens-selection.md](protocols/lens-selection.md) for
the full decision tree. Default mappings:

| Artifact type | Lens combination |
|---|---|
| Marketing copy | `lens-persuasion` + `lens-rhetoric` |
| Document pack | `lens-genre` + 6-dimension full pass |
| SOP / playbook | `lens-genre` |
| UI / onboarding | `lens-ux` + `lens-persuasion` |
| Speech / political | `lens-rhetoric` + `lens-frame` |
| Literature / film | `lens-semiotic` + `lens-frame` |
| Presentation deck | `lens-rhetoric` + `lens-genre` |

You may add a third lens if the artifact has unusual depth (e.g., a
landing page that also embeds a long argument benefits from
`lens-rhetoric` + `lens-persuasion` + `lens-genre`). Do NOT use all
six — that signals indecision, not thoroughness.

### Step 3: Run six-dimension analysis

Always run these six dimensions, regardless of which lenses you
selected. They are the structural backbone.

1. **Audience routing** — Who reads what, when?
2. **Creation sequence** — Reading order vs probable writing order
3. **Source genealogy** — What existing frameworks were borrowed?
4. **Rhetorical structure** — How does it persuade?
5. **Design patterns** — What recurring techniques appear?
6. **Negative space** — What is deliberately omitted?

See [protocols/six-dimensions.md](protocols/six-dimensions.md) for the
prompts that operationalize each dimension.

### Step 4: Apply selected lenses

Before reading lens references, **resolve the language variant** for
any of the 4 culturally-sensitive lenses (`lens-rhetoric` /
`lens-persuasion` / `lens-genre` / `lens-frame`) per
[`protocols/lens-variant-selection.md`](protocols/lens-variant-selection.md).
The universal-core `lens-{rhetoric,persuasion,genre,frame}.md` files
contain meta-only routing content; the analytical questions live in
the per-language variant (`-anglo` / `-ja` / `-zh`). `lens-semiotic`
and `lens-ux` do not have language variants in v0.2.0.

Read each selected lens reference (variant-resolved) and apply its
analytical questions to the artifact. Each lens reference contains:

- Primary-source citation (locked)
- Specific analytical questions
- Worked example
- "Do not over-apply" pitfalls

Available lenses (* = language-variant routing required):

- [`references/lens-semiotic.md`](references/lens-semiotic.md) — Barthes 5 codes (HER / PRO / SEM / SYM / REF)
- [`references/lens-rhetoric.md`](references/lens-rhetoric.md) ✱ — universal core; routes to `-anglo` (Burke + Toulmin) / `-ja` (Hinds + kishōtenketsu) / `-zh` (文心雕龍 六觀)
- [`references/lens-frame.md`](references/lens-frame.md) ✱ — universal core; routes to `-anglo` (Goffman + Lakoff) / `-ja` (建前/本音 + ma) / `-zh` (面子/關係 + 陰陽)
- [`references/lens-genre.md`](references/lens-genre.md) ✱ — universal core; routes to `-anglo` (Swales + Bhatia) / `-ja` (序論-本論-結論 + 拝啓 letter) / `-zh` (緒論-本論-結論 + 公文)
- [`references/lens-ux.md`](references/lens-ux.md) — Nielsen-Norman 10 heuristics + Norman affordance
- [`references/lens-persuasion.md`](references/lens-persuasion.md) ✱ — universal core; routes to `-anglo` (Cialdini + Brignull) / `-ja` (Cialdini + JP cultural) / `-zh` (Cialdini + 面子/關係)

**Always state which variant was applied in the report** (e.g., "Applied lens-rhetoric-ja") — see `protocols/lens-variant-selection.md` §"Step 5".

### Step 5: Generate deconstruction report

Use [`assets/report-template.md`](assets/report-template.md). Six
sections:

1. **Surface observations** (what you see)
2. **Design decisions** (audience / sequence / rhetoric)
3. **Borrowed frameworks** (genealogy)
4. **Rhetorical mechanisms** (with ethical position 🟢/🟡/🔴/⚫)
5. **Replicable lessons** (5 concrete takeaways)
6. **Weaknesses or warnings** (missing moves / suspicious warrants / dark-pattern risk)

End with a one-line **bottom-line verdict**.

### Step 6: Self-check

Before delivering, run [`checklists/anti-patterns.md`](checklists/anti-patterns.md)
self-check. Most common failures:

- Output drifted toward summary ("this document covers A, B, C") — must be design-decision focused
- Persuasion mechanisms named but no ethical position assigned
- All six dimensions not covered
- Negative space ignored — only analyzed what IS written
- Single lens tunnel vision — applied one lens to a multi-lens artifact

## Lens Library Quick Reference

All lens files are in `references/`, one level deep. Lenses marked ✱
are language-variant-routed — see `protocols/lens-variant-selection.md`.

| Lens | Variants | Authors (per variant) | When to apply |
|---|---|---|---|
| `lens-semiotic` | (no variants) | Roland Barthes (S/Z, 1970) | Literature, film, advertising imagery, texts with strong subtext |
| `lens-rhetoric` ✱ | -anglo / -ja / -zh | Burke 1945 + Toulmin 1958 / Hinds 1983 + 1987 + Oh 2025 (kishōtenketsu) / 劉勰《文心雕龍》六觀 | Speeches, proposals, political texts, arguments needing structural validation |
| `lens-frame` ✱ | -anglo / -ja / -zh | Goffman 1974 + Lakoff 1980 / + Doi 1971 + Yamamoto 1977 + Markus & Kitayama 1991 (建前/本音, 空気, ma) / + Hu 1944 + Hwang 1987 + Peng & Nisbett 1999 (面子/臉, 陰陽) | Texts with strong metaphors, suspected hidden assumptions, ideological texts |
| `lens-genre` ✱ | -anglo / -ja / -zh | Swales 1990 + Bhatia 1993 / + 木下 1981 + Hinds 1987 (序論-本論-結論, 拝啓 letter) / + 行政院公文程式條例 (緒論-本論-結論, 公文) | Document packs, SOPs, academic papers, business proposals — anything genre-recognizable |
| `lens-ux` | (no variants) | Jakob Nielsen + Don Norman (1988, 2013) | UI screens, app flows, websites, onboarding experiences (yes, docs are UX too) |
| `lens-persuasion` ✱ | -anglo / -ja / -zh | Cialdini 2021 + Brignull 2024 / + Doi 1971 + cross-cultural empirical work / + Hwang 1987 (面子/關係/人情) | Marketing copy, sales pages, landing pages, onboarding, political/policy texts |

## Output template

See [`assets/report-template.md`](assets/report-template.md) for the
full 6-section format.

## Anti-patterns

See [`checklists/anti-patterns.md`](checklists/anti-patterns.md) for
the self-check list. Run before every delivery.

## Sample artifacts (eval fixtures)

- [`assets/sample-dropbox-landing-2024.md`](assets/sample-dropbox-landing-2024.md)
- [`assets/sample-notion-onboarding-pack.md`](assets/sample-notion-onboarding-pack.md)
- [`assets/sample-stripe-signup-flow.md`](assets/sample-stripe-signup-flow.md)
