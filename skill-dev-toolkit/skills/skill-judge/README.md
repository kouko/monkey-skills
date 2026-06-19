# Skill Judge

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Score a SKILL.md on an 8-dimension rubric (0–120 points + letter grade)
> and surface what to fix — measures genuine expert knowledge density,
> not surface polish.

A user-invoked **evaluation skill**: when you have a draft or shipped
SKILL.md and want to know whether it's actually carrying expert
knowledge or just compressing things Claude already knows, you invoke
this skill to get a structured report with dimension scores, critical
issues, and prioritized improvements.

This README is for humans reading the skill on GitHub. The operational
file Claude actually loads is [`SKILL.md`](SKILL.md).

---

## Why does this skill exist?

**The recurring failure mode**: most skills waste tokens. The author
sets out to "teach Claude about X" and ends up writing a tutorial —
explaining what PDF is, how a for-loop works, generic best practices
("write clean code", "handle errors"). All of that is content Claude
already has. The context window is a shared resource; redundant
content crowds out the bits that genuinely matter.

The author can't reliably catch this themselves. The skill *feels*
helpful because the explanations are clear. Only when measured against
"is this content already in the model?" does the waste become visible.

This skill captures the discipline of that measurement. The core
formula:

> **Good Skill = Expert-only Knowledge − What Claude Already Knows**

Every section in a SKILL.md is classified as:

- **Expert** — Claude genuinely doesn't know this; this is the value
- **Activation** — Claude knows but the reminder is useful
- **Redundant** — Claude definitely knows; should be deleted

A good skill is >70% Expert. A bad skill is <40% Expert with a long
trail of redundant tutorial content.

---

## How does it work?

The skill applies an 8-dimension rubric (120 points total) to any
SKILL.md you point it at, producing:

```
Total: X/120 (X%)  →  Grade A / B / C / D / F
Pattern: Mindset / Navigation / Philosophy / Process / Tool
Knowledge Ratio: E:A:R = X:Y:Z

Dimension scores:
  D1 Knowledge Delta          (20)  ← THE CORE DIMENSION
  D2 Mindset + Procedures     (15)
  D3 Anti-Pattern Quality     (15)  ← specific NEVER lists with WHY
  D4 Spec Compliance          (15)  ← description quality (WHAT/WHEN/KEYWORDS)
  D5 Progressive Disclosure   (15)
  D6 Freedom Calibration      (15)
  D7 Pattern Recognition      (10)
  D8 Practical Usability      (15)

Critical Issues + Top 3 Improvements
```

The rubric draws on patterns observed across 17+ official Anthropic
skills, plus 9 common failure patterns ("The Tutorial", "The Dump",
"The Orphan References", "The Invisible Skill", etc.) with concrete
remediation guidance.

---

## When to use

- Reviewing a draft SKILL.md before shipping
- Auditing an existing skill that "feels off"
- Comparing two skills' design quality on consistent criteria
- Learning skill-design principles by applying the rubric

## When NOT to use

- **Behavioral / runtime testing** — use [`skill-creator-advance`](../skill-creator-advance/)
  (it has the eval-loop with test prompts and quantitative assertions)
- **Domain-team skill convention enforcement** — use
  domain-team structural convention gates
  (PASS/FAIL gates on monkey-skills convention: 4-tier gate hierarchy,
  3-commit split, primary-source grounding, ~6,000-token cap)
- **Generic code review** — wrong tool for the job

These three skills are complementary:

| Skill                                             | Mode      | Output                         |
|---------------------------------------------------|-----------|--------------------------------|
| `skill-judge` (this skill)                        | Static    | 0–120 advisory score           |
| `skill-dev-toolkit:skill-creator-advance`              | Behavioral| Pass/fail on test prompts      |
| structural convention gates                         | Structural| PASS/FAIL on convention gates  |

A skill can pass structural convention gates and still score D in `skill-judge`
(no convention violations, but the content is mostly redundant). It can
also score A in `skill-judge` and fail structural convention gates (great
content, wrong directory layout). They measure different things.

---

## Adaptation for monkey-skills domain-team skills

When evaluating skills under `domain-teams/skills/{team}/`, the rubric
applies a small adaptation:

- **D7 Pattern Recognition**: domain-team skills fit the upstream
  **Process** pattern by structural characteristics (phased workflow +
  checkpoints + medium freedom). Line count is a correlate, not the
  criterion — domain-team skills exceed upstream typical line counts
  by design and are not penalized for it.
- **D4 / D5 supplementary checks**: the structural convention gates' `CHK-SKL-001`
  (40–200-word description) and `CHK-SKL-010` (~6,000-token cap) are
  surfaced as **Critical Issues** in the report when they fail, but
  scoring uses the upstream rubric without arbitrary caps.
- **Focus dimensions**: D4/D5/D8 are partially covered by the structural convention layer's
  gates, so D1/D3/D6 carry the most net-new value when the gates
  already pass.

See [`SKILL.md` §Adaptation for monkey-skills domain-team skills](SKILL.md)
for full details.

---

## Attribution

This skill is adapted from
[`softaworks/agent-toolkit`](https://github.com/softaworks/agent-toolkit/tree/main/skills/skill-judge)
(MIT, Copyright (c) 2026 Leonardo Flores), which provides the 8-dimension
rubric, E:A:R knowledge classification, evaluation protocol, and 9 common
failure patterns.

Modifications by kouko: frontmatter rewritten to dev-workflow plugin
convention; new "Adaptation for monkey-skills domain-team skills" section
added; cross-references inserted to sibling skills for scope
disambiguation. See [`NOTICE`](NOTICE) for the full upstream chain and
modification summary, and [`LICENSE`](LICENSE) for the dual-copyright
header.
