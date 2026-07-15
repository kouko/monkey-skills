# Adaptation for monkey-skills domain-team skills

> Companion to [`../SKILL.md`](../SKILL.md). Load WHEN the skill under
> evaluation lives at `domain-teams/skills/{team}/` (follows the
> `standards/protocols/checklists/rubrics` 4-tier convention and is governed
> by the domain-team structural-gate convention). Not needed otherwise.

**Core principle**: skill-judge is *advisory* (0-120 scoring on design
quality). The structural convention gates are *authoritative* (PASS/FAIL
on monkey-skills convention). When a structural convention gate fails, surface it as
a **Critical Issue** in the Step 5 report — but score D1-D8 on the
upstream rubric without inventing arbitrary caps. The two systems
overlap; neither subordinates to the other.

## D7 Pattern Recognition — clarification (no rescale)

domain-team skills fit the upstream **Process** pattern by structural
characteristics:
- Phased workflow (e.g. 7-phase New Skill Creation, 10-phase Redesign)
- Checkpoints between phases (4-tier gate hierarchy: SELF/MUST/SHOULD/MAY)
- Medium-to-low freedom (exact templates with evaluator judgment latitude)

Line count is a typical correlate of upstream patterns, not the criterion
— D7 scoring criteria measure "masterful application of appropriate
pattern", not adherence to the typical line count. monkey-skills
convention (4-tier gates + primary-source grounding + 3-commit split)
increases SKILL.md length above upstream Process exemplars (e.g.
mcp-builder ~200 lines vs domain-team structural gates ~400 lines), but the structural
shape is unchanged.

**Rule**: score D7 on merit per Process pattern criteria. Do NOT deduct
for line count exceeding upstream typical — that's expected by design.
A masterful Process implementation earns 9-10 regardless of length.

**Report Pattern field**: fill `Process` for domain-team skills.

## D4 Specification Compliance — supplementary check

monkey-skills enforces a stricter frontmatter convention via its
structural-gate checklist (CHK-SKL-001): a substantive description with
an explicit `Use when` clause and positive delegation redirects (see your
domain-team plugin's structure standard for the rigorous version).

Run CHK-SKL-001 **in addition to** the upstream WHAT/WHEN/KEYWORDS check.
- If CHK-SKL-001 fails → list it under **Critical Issues** in the Step 5
  report. The skill cannot ship via the structural convention gates' MUST gate regardless of
  D4 score.
- Score D4 normally on the upstream rubric. Do not invent a cap.

## D5 Progressive Disclosure — supplementary check

monkey-skills caps SKILL.md at ~6,000 tokens via CHK-SKL-010 (FATAL
gate). This is a structural budget, not a D5 quality measure — a 7K-token
skill with excellent reference-disclosure design could legitimately
score 12-15 on D5 while still failing CHK-SKL-010.

- If CHK-SKL-010 fails → list it under **Critical Issues** in the Step 5
  report.
- Score D5 normally on the upstream rubric. Penalize the *Dump* pattern
  (no structure, references unused) per the original criteria; do not
  conflate with token-budget overrun.

## Focus dimensions for domain-team skills

The structural convention gates *partially* cover D4, D5, and D8:
- CHK-SKL-001 covers D4 frontmatter completeness (not WHAT/WHEN/KEYWORDS quality)
- CHK-SKL-010 / CHK-SKL-012 cover D5 structural floor (not loading-trigger quality)
- skill-coherence's Workflow Completeness flag covers part of D8 (not decision-tree depth, error handling, edge cases)

The dimensions providing the most net-new value above what the structural convention gates already check:
- **D1 Knowledge Delta** — does the skill compress real expert knowledge?
- **D3 Anti-Pattern Quality** — does it have specific NEVER lists with WHY?
- **D6 Freedom Calibration** — is specificity matched to task fragility?

When time-boxed, prioritize D1/D3/D6.

## Complementary, not replacement

This rubric does NOT replace the structural convention gates.
- the structural convention layer produces PASS/FAIL verdicts for convention enforcement
- `skill-judge` produces 0-120 advisory scoring for design quality

Use both:
- A skill can pass all structural convention gates (PASS) and still score D in
  skill-judge (poor knowledge delta, vague anti-patterns)
- A skill can score A in skill-judge but fail structural convention gates (great
  content, wrong directory layout)
