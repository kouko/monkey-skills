# philosophers-toolkit

> Twelve philosophical thinking frameworks turned into interactive Claude Code skills — guide thinking through questioning, not lecture.

Read this in: **English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

**Version**: 1.0.4
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)
**License**: MIT

## Background

Most "thinking framework" tools dump a checklist on the user and walk
away. This plugin does the opposite. Each skill turns Claude into a
philosophical interlocutor that runs the framework *with* you — asking
the right question at the right time, refusing to pre-judge the answer,
and leaving the conclusion in your hands.

The toolkit blends two traditions:

- **Western philosophy** — Socrates, Aristotle, Descartes, Hegel,
  Popper. Methods of decomposition, dialogue, and falsification.
- **Japanese philosophy / 日本哲学** — 守破離, 生き甲斐, 改善, 反省, 侘寂.
  Methods of stage diagnosis, purpose, continuous improvement,
  blame-free reflection, and good-enough.

Every skill is invocable as a slash command. A router skill
(`/using-philosophers-toolkit`) helps you pick the right one when you are
not sure.

## Install

This plugin lives in the `monkey-skills` marketplace.

```bash
# In Claude Code
/plugin marketplace add kouko/monkey-skills
/plugin install philosophers-toolkit
```

## Usage

Pick a skill directly when you know which method you want:

```
/philosophers-toolkit:socratic
/philosophers-toolkit:first-principles
/philosophers-toolkit:dialectics
```

Or let the router pick for you:

```
/philosophers-toolkit:using-philosophers-toolkit
```

The router asks one question — "what are you trying to do?" — and
points you at the best-fit skill.

## Skills

### Western philosophy

#### Socratic method

| Field | Value |
|-------|-------|
| Origin | Ancient Athens, c. 5th century BCE |
| Philosopher | Socrates (via Plato's dialogues) |
| Core idea | Maieutics — the "midwife of ideas". Knowledge is drawn out of the learner, not poured in. |
| Method | Claude refuses to lecture. Every turn ends in a question that pushes you to articulate your own thinking. |
| Use when | You want your thinking challenged through open dialogue; you say "explain to me" or "I'm stuck". |
| Command | `/philosophers-toolkit:socratic` |

#### Aristotle's Four Causes

| Field | Value |
|-------|-------|
| Origin | *Physics* and *Metaphysics*, c. 350 BCE |
| Philosopher | Aristotle |
| Core idea | Anything that exists has four explanatory causes — material, formal, efficient, and final. Examine all four to reach complete understanding. |
| Method | Claude structures the analysis through the four lenses: what it is made of, what makes it that thing, what brought it about, what it is for. |
| Use when | You want to deeply understand the essence of a system, product, or concept. |
| Command | `/philosophers-toolkit:four-causes` |

#### First Principles

| Field | Value |
|-------|-------|
| Origin | Aristotle's *Posterior Analytics*; revived in modern engineering practice |
| Philosopher | Aristotle |
| Core idea | Decompose to fundamental truths that cannot be reduced further, then rebuild — rejecting reasoning by analogy. |
| Method | Claude helps you strip away "best practices" and conventions until only the irreducible facts remain, then reason upward. |
| Use when | Legacy assumptions constrain new thinking; you want to rethink a problem from zero. |
| Command | `/philosophers-toolkit:first-principles` |

#### Hegelian Dialectics

| Field | Value |
|-------|-------|
| Origin | Early 19th century German idealism |
| Philosopher | Georg Wilhelm Friedrich Hegel |
| Core idea | Every position contains the seed of its contradiction. Thesis → antithesis → synthesis arrives at a higher-order frame where the tension dissolves. |
| Method | Claude makes the opposition explicit, then drives toward synthesis — not compromise. |
| Use when | You face a binary choice, competing priorities, or stakeholders holding opposing views. |
| Command | `/philosophers-toolkit:dialectics` |

#### Popper's Falsifiability

| Field | Value |
|-------|-------|
| Origin | *The Logic of Scientific Discovery*, 1934 |
| Philosopher | Karl Popper |
| Core idea | A claim is meaningful only if you can specify what evidence would prove it wrong. A theory that explains everything explains nothing. |
| Method | Claude turns vague claims into testable hypotheses and helps you design tests that could falsify them. |
| Use when | You have an assumption to verify; you said "X is better than Y" without measurable criteria. |
| Command | `/philosophers-toolkit:falsify` |

#### Descartes' Methodical Doubt

| Field | Value |
|-------|-------|
| Origin | *Meditations on First Philosophy*, 1641 |
| Philosopher | René Descartes |
| Core idea | If there is any reason to doubt it, treat it as false — until you reach what cannot be doubted at all. Then rebuild on that bedrock. |
| Method | Claude systematically eliminates each layer of uncertainty, surfacing what survives maximum skepticism. |
| Use when | You audit trust assumptions, evaluate evidence, or stress-test a plan before committing resources. |
| Command | `/philosophers-toolkit:doubt` |

### Japanese philosophy / 日本哲学

#### 守破離 (Shu-Ha-Ri)

| Field | Value |
|-------|-------|
| Origin | Japanese martial-arts tradition; codified in Aikido by 遠藤征四郎 |
| Tradition | 武道 (budō) |
| Core idea | Mastery passes through three stages — 守 follow the form, 破 break the form, 離 leave the form behind. Stage is per-domain, not absolute. |
| Method | Claude diagnoses your stage in a specific skill or methodology and gives stage-appropriate guidance. |
| Use when | You wonder "should I follow the rules or do it my way?"; you assess your mastery level for a technology. |
| Command | `/philosophers-toolkit:shu-ha-ri` |

#### 生き甲斐 (Ikigai)

| Field | Value |
|-------|-------|
| Origin | Okinawan / mainland Japanese concept of life purpose |
| Tradition | Japanese life-purpose tradition |
| Core idea | The intersection of "what you love", "what you are good at", "what the world needs", and "what pays" sustains meaning. A missing axis leaves something hollow. |
| Method | Claude walks you through each of the four axes and diagnoses where the gap is. |
| Use when | A project or product feels purposeless; PMF feels missing; a career inflection point. |
| Command | `/philosophers-toolkit:ikigai` |

#### 改善 (Kaizen)

| Field | Value |
|-------|-------|
| Origin | Postwar Toyota Production System; codified by 大野耐一 and 今井正明 |
| Tradition | 製造業 (manufacturing); now broadly applied |
| Core idea | Make today's work a little better than yesterday's. Small, continuous improvements compound into large outcomes. |
| Method | Claude leads a six-step loop to identify the smallest viable improvement and act on it. |
| Use when | Something feels inefficient; existing process has friction or waste; "I want to change a lot but don't know where to start". |
| Command | `/philosophers-toolkit:kaizen` |

#### 反省 (Hansei)

| Field | Value |
|-------|-------|
| Origin | Japanese reflective tradition; integrated into Toyota's continuous-learning culture |
| Tradition | Japanese self-cultivation |
| Core idea | Retrospect for learning, not blame. Ask "what was I missing?", not "whose fault was it?". |
| Method | Claude leads a four-stage introspective process focused on structural blind spots, not surface lessons. |
| Use when | A project missed its deadline; a feature was not adopted; a decision backfired; quarterly or annual reflection. |
| Command | `/philosophers-toolkit:hansei` |

#### 侘寂 (Wabi-Sabi)

| Field | Value |
|-------|-------|
| Origin | Tea-ceremony aesthetics; codified by 千利休, deepened by 松尾芭蕉 |
| Tradition | Japanese aesthetics |
| Core idea | Beauty in imperfection, impermanence, and incompleteness. Cut what can be cut. Let time and use add value. Leave deliberate gaps for participation. |
| Method | Claude asks whether more polish raises essence — or hides fear. |
| Use when | You debate "MVP or polish more"; the API feels too complex; perfectionism stalls release. |
| Command | `/philosophers-toolkit:wabi-sabi` |

### Getting started

#### `/using-philosophers-toolkit` router

| Field | Value |
|-------|-------|
| Skill | `using-philosophers-toolkit` |
| Core idea | Match intent to method. The right framework matters more than the most fashionable one. |
| Method | Claude asks one question — "what are you trying to do?" — and routes you to the right skill. |
| Use when | You want to think deeper but are not sure which method fits; you have a vague problem and need to clarify it. |
| Command | `/philosophers-toolkit:using-philosophers-toolkit` |

## Design principles

These principles run through every skill in the toolkit:

**Interactive process, not a lecture.** Every skill turns Claude into
a thinking partner. The skill asks. You answer. The skill probes
deeper. The conclusion is yours, not Claude's.

**Acknowledge the topic, never pre-judge the answer.** Each skill
confirms what you want to analyze before it starts. It refuses to
declare what the synthesis, the indubitable bedrock, or the right
stage will be.

**Language of origin.** Japanese frameworks live in Japanese — 守破離,
生き甲斐, 改善, 反省, 侘寂 — not in romaji or forced English glosses.
Western philosopher names stay verbatim. Concepts route through
their original cultural form.

**Operational, not academic.** Every skill outputs a sharper problem
definition or a more complete analysis — not a philosophy paper. Each
runs as a procedure with concrete steps, not a freeform discussion.

**One method per situation.** Each skill's `Do NOT use when` block
routes you elsewhere when the wrong tool is selected. Falsify a claim,
doubt a premise, decompose a problem, dialogue an open question — each
has its own skill.

## Roadmap

See [ROADMAP.md](ROADMAP.md) for frameworks under consideration —
including Occam's Razor, pragmatism, utilitarian and deontological
ethics, 三現主義, and 道家 / 無為.

## Contributing

Contributions welcome. Open an issue first if you are proposing a
new framework. Each new skill must:

- Map to a clear problem class with `When to Use` and `Do NOT use when` blocks
- Run as an interactive procedure, not as a static reference
- Preserve the language of origin for non-Western frameworks
- Pass the [domain-teams skill-team](https://github.com/kouko/monkey-skills/tree/main/domain-teams/skills/skill-team) structural gates

PRs follow [Conventional Commits](https://www.conventionalcommits.org/).

## License

MIT — see [LICENSE](../LICENSE) at the repository root.
