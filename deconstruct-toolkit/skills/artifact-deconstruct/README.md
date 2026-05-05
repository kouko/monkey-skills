# artifact-deconstruct

> Recover the design blueprint behind any polished, non-code artifact — what was decided, what was borrowed, what was deliberately left unsaid.

The flagship skill of `deconstruct-toolkit`. Reverse-engineers the design
blueprint of any external, non-code, polished artifact (copy / document
packs / SOPs / playbooks / presentations / UI screenshots / advertising
/ literature). The goal is **design archaeology** — recovering what the
creator decided, what frameworks they borrowed, and what they
deliberately omitted.

## When to use

Trigger phrases (any language):

- EN: "deconstruct this", "reverse engineer", "design behind this", "teardown", "why does this work"
- JP: 「この制作物を脱構築して」「なぜこれはこんなに刺さるのか」「設計を逆引きして」
- ZH-TW: 「拆解這份」「反推這個」「為什麼這份寫得這麼好」「這份是怎麼設計的」

Skip when:

- User wants a **summary** — use plain reading
- Artifact < 200 words and not a structured argument — not enough design to recover
- Target is purely informational reference (Wikipedia, dictionary, raw data)
- Target is source code → use `sourceatlas`
- Target is the user's own thinking → use `philosophers-toolkit`

## How it works (6 steps)

1. **Detect type** — marketing / playbook / SOP / deck / UI / article / speech / literature / UI screen
2. **Select lenses** — 1–3 from the 6-lens library (decision tree in [`protocols/lens-selection.md`](protocols/lens-selection.md))
3. **Run six dimensions** — always-on backbone, regardless of lens choice
4. **Apply lenses** — variant-resolved per [`protocols/lens-variant-selection.md`](protocols/lens-variant-selection.md) for the 4 cultural lenses
5. **Generate report** — 6-section deconstruction with ethical-position verdict
6. **Self-check** — run [`checklists/anti-patterns.md`](checklists/anti-patterns.md) before delivery

Full instruction body in [`SKILL.md`](SKILL.md).

## Lens library

6 lenses, applied in selectable combinations (NOT all six — that signals indecision):

| Lens | Sources | Cultural variants |
|---|---|---|
| `lens-semiotic` | Barthes 1970 (S/Z, 5 codes) | (none — Anglo-grounded only as of v0.2.0) |
| `lens-rhetoric` ✱ | Burke 1945 + Toulmin 1958 (anglo) · Hinds 1983/1987 + Oh 2025 kishōtenketsu (ja) · 劉勰《文心雕龍》六觀 (zh) | -anglo / -ja / -zh |
| `lens-frame` ✱ | Goffman 1974 + Lakoff 1980 (anglo) · + Doi 1971 / Yamamoto 1977 / Markus & Kitayama 1991 (ja) · + Hu 1944 / Hwang 1987 / Peng & Nisbett 1999 (zh) | -anglo / -ja / -zh |
| `lens-genre` ✱ | Swales 1990 + Bhatia 1993 (anglo) · + 木下 1981 + Hinds 1987 (ja) · + 行政院公文程式條例 (zh) | -anglo / -ja / -zh |
| `lens-ux` | Nielsen 1994/2020 + Norman 1988/2013 | (none) |
| `lens-persuasion` ✱ | Cialdini 2021 + Brignull 2024 (anglo) · + Doi 1971 + cross-cultural empirical work (ja) · + Hwang 1987 面子/關係/人情 (zh) | -anglo / -ja / -zh |

(✱ = language-variant-routed; resolve variant before applying via [`protocols/lens-variant-selection.md`](protocols/lens-variant-selection.md))

## Six-dimension backbone

Every artifact gets all six dimensions, regardless of which lenses you also apply:

1. **Audience routing** — Who reads what, when?
2. **Creation sequence** — Reading order vs probable writing order
3. **Source genealogy** — What existing frameworks were borrowed?
4. **Rhetorical structure** — How does it persuade?
5. **Design patterns** — What recurring techniques appear?
6. **Negative space** — What is deliberately omitted?

The negative-space dimension is mandatory — what the artifact does NOT
say is data, not gap.

## What you get (output format)

A 6-section deconstruction report (template at [`assets/report-template.md`](assets/report-template.md)):

```
1. Surface observations    (what you see)
2. Design decisions        (audience / sequence / rhetoric)
3. Borrowed frameworks     (genealogy)
4. Rhetorical mechanisms   (with ethical position 🟢/🟡/🔴/⚫)
5. Replicable lessons      (5 concrete takeaways)
6. Weaknesses / warnings   (missing moves / suspicious warrants / dark-pattern risk)
```

Ending with a one-line **bottom-line verdict**.

Each detected persuasion or UX mechanism gets one of four ethical
positions:

| Position | Meaning |
|---|---|
| 🟢 Transparent | Principle used, user can see and reject |
| 🟡 Gray zone | Principle used, user is unaware |
| 🔴 Manipulation | Creates urgency or false belief |
| ⚫ Dark pattern | Actively deceives, harms user |

No neutral description allowed.

## Cultural-variant routing (v0.2.0+)

For the 4 culturally-sensitive lenses (rhetoric / persuasion / genre /
frame), variant is selected by **artifact register**, not author or
brand origin. A Toyota English landing page applies `-anglo` (English-
language artifact), not `-ja` (Japanese-brand). Algorithm in
[`protocols/lens-variant-selection.md`](protocols/lens-variant-selection.md).

The output report MUST state which variant was applied:

> "Applied lens-rhetoric-ja (kishōtenketsu mode, op-ed register) to artifact at [URL] in Japanese."

This makes the analysis auditable — a reader who disagrees with the
variant choice can re-run with a different one.

## Worked examples

Anglo:

- [`assets/sample-dropbox-landing-2024.md`](assets/sample-dropbox-landing-2024.md) — real-fetched 2026-05-05 Dropbox landing page (must-find ground truth in `eval/cases/artifact-deconstruct-01-dropbox-landing.yaml` at the plugin root)
- [`assets/sample-notion-onboarding-pack.md`](assets/sample-notion-onboarding-pack.md)
- [`assets/sample-stripe-signup-flow.md`](assets/sample-stripe-signup-flow.md)

Cultural-variant fixtures (8 total, JP + ZH):

- JP: `sample-ja-op-ed.md` · `sample-ja-ec-lp.md` · `sample-ja-business-letter.md` · `sample-ja-political-speech.md`
- ZH: `sample-zh-op-ed.md` · `sample-zh-ec-lp.md` · `sample-zh-gongwen.md` · `sample-zh-political-speech.md`

All 11 cases have matching `must_find` ground-truth specs in `eval/cases/` at the plugin root.

## When NOT to use this skill

- Argument-focused deep dive → use `argument-deconstruct` (Toulmin + Burke pentad with hidden-warrant focus)
- Atomic hidden-assumption surfacing → use `assumption-surface` (reverse-Toulmin + Althusser symptomatic reading)
- Code reverse-engineering → use `sourceatlas`
- Self-thinking → use `philosophers-toolkit`
- < 200 words and not a structured argument — not enough design

## See also

- [`SKILL.md`](SKILL.md) — full canon (this README is the GitHub-browser-facing front; SKILL.md is the LLM-facing instruction body)
- [`protocols/six-dimensions.md`](protocols/six-dimensions.md)
- [`protocols/lens-selection.md`](protocols/lens-selection.md)
- [`protocols/lens-variant-selection.md`](protocols/lens-variant-selection.md)
- [`checklists/anti-patterns.md`](checklists/anti-patterns.md)
- Plugin overview: [`../../README.md`](../../README.md)
