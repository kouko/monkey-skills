# Shu-Ha-Ri Skill

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

Diagnose mastery stages and provide stage-appropriate guidance for any skill domain.

## The Three Stages

| Stage | Kanji | Meaning | Behavior Pattern |
|-------|-------|---------|-----------------|
| Shu | 守 | Protect / Follow | Follow rules exactly. Learn the form. Don't deviate. |
| Ha | 破 | Break / Adapt | Understand WHY rules exist. Adapt to context. |
| Ri | 離 | Transcend / Detach | Rules internalized. Move freely. Create your own way. |

## Method Type

Framework-driven diagnostic (not dialogue-driven like Socratic method).
Agent diagnoses the user's current stage through behavioral questions,
then provides stage-appropriate guidance and transition signals.

Key principle: stages are domain-specific. A practitioner may be Shu in
one area and Ri in another.

## Diagnostic Signals

| Signal | Shu | Ha | Ri |
|--------|-----|----|----|
| Rules | Follow faithfully | Understand and adapt | Optimal judgment without conscious effort |
| Problem-solving | Consult docs/guides | Apply principles to novel problems | Intuitively reach optimal solutions |
| Teaching | Convey rules/procedures | Explain principles and reasoning | Adapt instruction to learner's stage |
| Exceptions | Stuck when rules don't apply | Recognize and adjust rules | Handle naturally |
| Creativity | Improve within the form | Combine existing forms into new approaches | Create original forms for the situation |

## Examples in SKILL.md

| Example | Domain | Key Insight |
|---------|--------|-------------|
| TypeScript + TDD | Software Development | Two domains assessed separately; TDD diagnosed as Shu based on skipping Refactor step |
| Scrum Team Coaching | Agile Methodology | Team stuck in Shu stagnation; ceremonies followed by form but not purpose |

## Additional Cases

See `references/shu-ha-ri-cases.md` for more examples:
React component design, UI design principles, code review practices.

## Common Traps

| Trap | Description | Remedy |
|------|-------------|--------|
| Stage skipping | Jumping to Ri without mastering Shu | Diagnose gaps, return to appropriate stage |
| Shu stagnation | Following rules perfectly but unable to adapt | Introduce "why" questions, encourage experiments |
| False Ri | Confusing ignorance with transcendence | Test with diagnostic questions to reveal gaps |
| Uniform assessment | Treating all domains as one stage | Always specify and assess per-domain |

## Applicable Domains

| Domain | Shu Example | Ha Example | Ri Example |
|--------|-------------|------------|------------|
| Programming Language | Follow style guide, use standard patterns | Know trade-offs, choose patterns by context | Write idiomatic code instinctively |
| Methodology (Agile, TDD) | Follow ceremonies/cycles exactly | Adapt processes to team needs | Embody principles without rigid process |
| Design (UI/UX) | Follow design system guidelines | Understand when to break guidelines | Develop design taste and intuition |
| Code Review | Use checklist, apply rules | Evaluate trade-offs, context-aware feedback | Sense quality holistically |

## Cultural Origin

Shu-Ha-Ri originates from Japanese martial arts (aikido, via Endo Seishiro)
and is deeply connected to the Japanese tradition of mastery through
disciplined practice. The concept parallels the Dreyfus model of skill
acquisition but emphasizes the practitioner's relationship with rules
rather than cognitive stages.
