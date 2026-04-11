# Product Spec Completeness Checklist Gate

## Evaluation Instructions

Check that the PRODUCT-SPEC.md covers all required sections and
anchors load-bearing claims to the primary sources in the team's
standards files. A complete product spec lets any team start their
work without ambiguity.

Reference standards:
- `standards/planning-frameworks.md` — JTBD, BMC, Lean Canvas, 4 Big Risks, 3C, VPC
- `standards/discovery-frameworks.md` — Lean Startup, MVP, Product Discovery, PR/FAQ
- `standards/goals-and-metrics.md` — OKR, North Star Metric, AARRR, Goals/Non-Goals
- `standards/spec-completeness-standards.md` — 5W2H completeness, decision rationale, JP 企画 anchors

## CHK-PROD-001: Vision & Problem [FATAL if missing]

- [ ] Problem or opportunity is clearly stated
- [ ] Target users are identified (not just "users")
- [ ] **Job-to-be-Done** is expressed using the Job Story template
      "When [situation], I want to [motivation], so I can [outcome]"
      (Adams 2016 Intercom, `standards/planning-frameworks.md` §Job
      Story template) — NOT the "As a user, I want..." user-story form
- [ ] Success criteria are **measurable** — per
      `standards/goals-and-metrics.md`, use OKR Key Results, North
      Star Metric, or AARRR funnel metrics (not vague "successful")

## CHK-PROD-002: Scope Definition [FATAL if missing]

- [ ] **Goals** section exists with concrete items; if using OKRs,
      the format is "I will [Objective] as measured by [3-5 Key
      Results]" per `standards/goals-and-metrics.md` §OKRs (Grove
      1983 / Doerr 2018)
- [ ] **Non-Goals** section exists and names **plausible goals that
      were considered and rejected** (Ubl 2020 convention,
      `standards/goals-and-metrics.md` §Goals/Non-Goals). Empty or
      trivial Non-Goals ("not in scope: anything not mentioned") is
      a FATAL failure
- [ ] **MVP** scope is explicitly defined per
      `standards/discovery-frameworks.md` §MVP (Ries 2011 Part Two):
      the minimum product to collect maximum **validated learning**.
      The spec must state what the MVP is trying to **learn**, not
      just what it will ship. "MVP = smallest shippable feature set"
      is a FATAL misdefinition.

## CHK-PROD-003: Assumption Discovery [FATAL if missing]

- [ ] Top 3 riskiest assumptions identified and tagged `[ASSUMPTION]`
- [ ] Each assumption maps to one of the **4 Big Risks** (Value /
      Usability / Feasibility / Business Viability) per
      `standards/planning-frameworks.md` §The 4 Big Risks (Cagan 2017
      *Inspired* 2nd ed Part III). Attribution NOTE: the 4-axis
      framework is Cagan, NOT Bland & Osterwalder (Bland uses 3 axes
      only).
- [ ] Each assumption has a named validation approach
      (experiment / interview / desk research / prototype test)
      per Bland & Osterwalder (2020) *Testing Business Ideas*.

## CHK-PROD-004: UX Direction [FIXABLE]

- [ ] Core user flow is described (entry → task → outcome)
- [ ] Interaction model is specified (CLI / GUI / API / etc.)
- [ ] Key design constraints documented

## CHK-PROD-005: Technical Direction [FIXABLE]

- [ ] Architecture approach stated with **rationale** per
      `standards/spec-completeness-standards.md` §Decision Rationale
      Rule — every "we chose X" needs a nearby "because Y"
- [ ] Key technical constraints listed
- [ ] Technical risks identified
- [ ] External dependencies listed

## CHK-PROD-006: Decision Rationale [FIXABLE]

- [ ] Major decisions include "because" explanations
- [ ] Alternative approaches mentioned for key choices
- [ ] Trade-offs acknowledged

## CHK-PROD-007: Handoff Readiness [FIXABLE]

- [ ] Open questions marked with `[OPEN]` tag
- [ ] Downstream team assignments identifiable
- [ ] No section is entirely placeholder or TBD

## CHK-PROD-008: 5W2H Completeness Cross-Check [FIXABLE]

Per `standards/spec-completeness-standards.md` §5W2H — Per-Letter
Checks, verify the spec answers all 7 questions (genealogy: Kipling
1902 → 1960s JUSE → Ohno 1978 TPS, NOT purely "Japanese business
convention"):

- [ ] **Why** — problem / opportunity driving this (Background section)
- [ ] **What** — product / service being delivered (Core Concept)
- [ ] **Who** — target customer + team executing (Target Users)
- [ ] **When** — timeline / milestones (Scope & Phasing)
- [ ] **Where** — platform / distribution channel (UX + Business)
- [ ] **How** — technical approach / realization method (Tech Direction)
- [ ] **How much** — resources / cost / budget estimate (Success Criteria)

Missing any of the 7 letters is a FIXABLE completeness gap.

## CHK-PROD-009: Formatting [FIXABLE]

- [ ] Consistent heading hierarchy
- [ ] No broken references or orphaned sections
- [ ] Tables and lists properly formatted

## Verdict Rules

- Any FATAL check missing → NEEDS_REVISION
- 1 FIXABLE check missing → PASS_WITH_NOTES
- 2+ FIXABLE checks missing → NEEDS_REVISION
- All checks present → PASS
