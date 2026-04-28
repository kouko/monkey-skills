# Philosophers Toolkit

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

Philosophical thinking frameworks that guide users through structured
reasoning — not lectures, but interactive methods for deeper thinking.

## Skills

### Western Philosophy

#### Socratic Method / ソクラテス式対話 / 蘇格拉底式對話

| | |
|--|--|
| **Origin** | Socrates (470–399 BC), Ancient Greece |
| **Core Idea** | Guide users to discover knowledge through disciplined questioning, not direct instruction. "I know that I know nothing." |
| **Method** | Dialogue-driven state machine: Topic Discovery → Initial Exploration → Hypothesis Testing (Elenchus) → Aporia → Deepening → Synthesis |
| **Use When** | User wants their thinking challenged, not when they want information |
| **Command** | `/philosophers-toolkit:socratic` |

Adapted from [malkreide/socratic-method-skill](https://github.com/malkreide/socratic-method-skill).

#### Aristotle's Four Causes / アリストテレスの四原因説 / 亞里斯多德四因說

| | |
|--|--|
| **Origin** | Aristotle (384–322 BC), Ancient Greece. *Physics* and *Metaphysics* |
| **Core Idea** | Everything can be understood through four questions: What is it made of? What makes it what it is? What brought it about? What is it for? |
| **Method** | Framework-driven: Material Cause → Formal Cause → Efficient Cause → Final Cause → Synthesis |
| **Use When** | User wants to deeply understand the essence of a system, product, or concept |
| **Command** | `/philosophers-toolkit:four-causes` |

#### Aristotle's First Principles / アリストテレスの第一原理 / 亞里斯多德第一原理

| | |
|--|--|
| **Origin** | Aristotle (384–322 BC), Ancient Greece. *Posterior Analytics* |
| **Core Idea** | Decompose problems to fundamental truths that cannot be reduced further, then rebuild from scratch. Reject reasoning by analogy. |
| **Method** | Process-driven: Problem Essence → Challenge Assumptions → Establish Ground Truths → Reason Upward → Validate Reasoning |
| **Use When** | User is trapped by "best practices" or convention and wants to rethink from zero |
| **Command** | `/philosophers-toolkit:first-principles` |

Five-phase structure inspired by [awesome-skills/first-principles-skill](https://github.com/awesome-skills/first-principles-skill) (MIT).

#### Hegelian Dialectics / ヘーゲル弁証法 / 黑格爾辯證法

| | |
|--|--|
| **Origin** | Georg Wilhelm Friedrich Hegel (1770–1831), Germany. *Phenomenology of Spirit* |
| **Core Idea** | Every position contains the seed of its own contradiction. By making it explicit and working through it, you arrive at a higher-order understanding. Synthesis ≠ compromise. |
| **Method** | Phase-driven: Thesis → Antithesis → Synthesis (optional iteration: synthesis becomes new thesis) |
| **Use When** | User faces trade-offs, binary choices, or opposing views |
| **Command** | `/philosophers-toolkit:dialectics` |

#### Popper's Falsifiability / ポパーの反証可能性 / 波普可否證性

| | |
|--|--|
| **Origin** | Karl Popper (1902–1994), Austria. *The Logic of Scientific Discovery* (1934) |
| **Core Idea** | A hypothesis is meaningful only if it can be proven wrong. Design tests that would disprove your claim — if it survives, it's provisionally accepted. |
| **Method** | Process-driven: State Hypothesis → Operationalize → Design Falsification Test → Evaluate Evidence → Verdict (falsified / survived / unfalsifiable) |
| **Use When** | User needs to test assumptions or validate product hypotheses |
| **Command** | `/philosophers-toolkit:falsify` |

#### Descartes' Methodical Doubt / デカルトの方法的懐疑 / 笛卡兒方法性懷疑

| | |
|--|--|
| **Origin** | René Descartes (1596–1650), France. *Meditations on First Philosophy* (1641) |
| **Core Idea** | Systematically doubt everything that CAN be doubted until you reach what CANNOT be doubted — the indubitable foundation. |
| **Method** | Process-driven: State Belief → Apply Doubt Layers (sensory / reasoning / systemic) → Identify Survivors → Rebuild from Indubitable |
| **Use When** | User needs to audit foundational assumptions — security trust models, data sources, organizational beliefs |
| **Command** | `/philosophers-toolkit:doubt` |

### Japanese Philosophy / 日本哲学 / 日本哲學

#### 守破離 / Shu-Ha-Ri / 守破離

| | |
|--|--|
| **Origin** | Japanese martial arts tradition (aikido, tea ceremony). Formalized by Endo Seishiro |
| **Core Idea** | 守 (follow rules exactly) → 破 (understand why, start adapting) → 離 (transcend rules, create your own way). Not linear — one person can be 守 in one area and 離 in another. |
| **Method** | Framework-driven diagnostic: Identify Domain → Diagnose Stage → Stage-Appropriate Guidance → Transition Signals |
| **Use When** | User wants to assess their mastery level and get appropriate guidance |
| **Command** | `/philosophers-toolkit:shu-ha-ri` |

#### 生き甲斐 / Ikigai / 生之甲斐

| | |
|--|--|
| **Origin** | Japanese concept of life purpose. Popularized in Okinawan longevity research |
| **Core Idea** | Purpose lives at the intersection of four axes: what you love, what you're good at, what the world needs, and what you can be paid for. |
| **Method** | Framework-driven: analyze each axis, diagnose which is missing or weak, find the intersection |
| **Use When** | User wants to validate project purpose, product-market fit, or career direction |
| **Command** | `/philosophers-toolkit:ikigai` |

#### 改善 / Kaizen / 改善

| | |
|--|--|
| **Origin** | Post-war Japanese manufacturing. Formalized in Toyota Production System |
| **Core Idea** | Small, continuous improvements beat big transformations. Change daily habits, not annual strategies. |
| **Method** | Process-driven cycle: 現状把握 → 問題発見 → 根本原因 → 改善案 → 実行と検証 → 標準化 |
| **Use When** | User wants to improve an existing process incrementally, not redesign from scratch |
| **Command** | `/philosophers-toolkit:kaizen` |

#### 反省 / Hansei / 反省

| | |
|--|--|
| **Origin** | Japanese cultural practice of self-reflection. Core to Toyota Way and Japanese education |
| **Core Idea** | Blame-free introspection after events. Focus on "what did I not see?" not "who messed up?" Deeper than Western postmortem — personal and humble. |
| **Method** | Phase-driven: 事実確認 → 内省 → 学び → 次の一歩 |
| **Use When** | User wants to reflect on a completed project, decision, or event to extract structural lessons |
| **Command** | `/philosophers-toolkit:hansei` |

#### 侘寂 / Wabi-Sabi / 侘寂

| | |
|--|--|
| **Origin** | Japanese aesthetic philosophy rooted in Zen Buddhism and tea ceremony (Sen no Rikyu) |
| **Core Idea** | Find beauty in imperfection, impermanence, and incompleteness. Counter over-engineering and perfectionism. Constraints are design features, not flaws. |
| **Method** | Framework-driven: 3 lenses — 侘 (simplicity/austerity) + 寂 (patina/age) + 不完全の美 (beauty of incompleteness) |
| **Use When** | User needs to judge "good enough" vs more polish, or wants to embrace constraints as strengths |
| **Command** | `/philosophers-toolkit:wabi-sabi` |

### Getting Started

#### Using Philosophers Toolkit

Not sure which method to use? Start here:

| | |
|--|--|
| **Command** | `/philosophers-toolkit:think` |
| **What it does** | Asks what you're trying to do, then routes you to the best-fit method |
| **Categories** | Understand → Decide → Improve → Reflect |
| **Default** | If unsure, falls back to Socratic Method |

## Design Principles

- Every skill is an **interactive process**, not a lecture
- Output is "better thinking" or "clearer understanding", not a report
- Agent guides through questioning — user discovers, agent doesn't prescribe
- Written in the **language of origin** where culturally appropriate (Japanese methods in Japanese)
- Each skill follows the [skill structure standard](standards/skill-structure.md)

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned future skills.
