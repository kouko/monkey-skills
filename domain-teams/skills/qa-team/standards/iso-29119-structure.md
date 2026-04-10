# ISO/IEC/IEEE 29119-3 Document Structure (Shared Standard)

Test plan document structure checklist, derived from ISO/IEC/IEEE 29119-3:2021
Annex A. Used as a **structural reference**, not a mandatory template.

Primary source: [IEEE SA — IEEE/ISO/IEC 29119-3](https://standards.ieee.org/ieee/29119-3/7499/)
ISO page: [ISO 29119-3:2021](https://www.iso.org/standard/79429.html)

## Design Intent

We adopt 29119-3 structure without imposing ceremonial process. This is a
deliberate response to the "Stop 29119" critique — the standard's document
hierarchy is useful as a checklist, but requiring every test plan to fill
every section is exactly the over-documentation the critique warns against.

Use this standard to **verify completeness**, not to **generate boilerplate**.

> [Stop 29119 controversy](https://en.wikipedia.org/wiki/ISO/IEC_29119):
> The Association for Software Testing and the International Society for
> Software Testing petitioned in 2014 that 29119 lacks genuine professional
> consensus and "will detract from the actual process of software testing."

## 29119-3 Document Hierarchy (three tiers)

| Tier | Documents |
|------|-----------|
| **Organizational** | Test Policy, Organizational Test Strategy |
| **Test Management** | Test Plan (incorporating Test Strategy), Test Status Report, Test Completion Report |
| **Dynamic Test Process** | Test Design Specification, Test Case Specification, Test Procedure, Test Data Requirements, Test Environment Requirements, Test Data/Environment Readiness Reports, Actual Results, Test Results, Test Execution Log, Test Incident Report |

qa-team's primary artifact is **TEST-PLAN.md** at the Test Management tier.
The Dynamic tier is produced implicitly during execution and need not be
pre-authored as separate files.

## TEST-PLAN.md Section Checklist (29119-3 Annex A)

Every TEST-PLAN.md should address these sections. Sections can be omitted
with explicit rationale — absence without rationale is a completeness gap.

| § | Section | Purpose |
|---|---------|---------|
| 1 | **Scope** | What is tested, what is explicitly out of scope, assumptions |
| 2 | **References** | TECH-SPEC.md, PRODUCT-SPEC.md, related standards, other test plans |
| 3 | **Test items** | Components, modules, features, or systems under test with versions |
| 4 | **Risk register** | Product risks identified via Likelihood × Impact (see `risk-assessment.md`) |
| 5 | **Test strategy / approach** | Test levels, types, techniques selected and why |
| 6 | **Entry criteria** | What must be true before testing starts |
| 7 | **Exit criteria** | What must be true before testing is considered complete |
| 8 | **Suspension and resumption criteria** | When to pause, when to resume |
| 9 | **Test environment and data** | Infrastructure, test data, external service dependencies |
| 10 | **Test deliverables** | What documents/artifacts the test activity produces |
| 11 | **Schedule** | Test milestones and timing |
| 12 | **Roles and responsibilities** | Who does what |

## Minimum Viable Test Plan

When the project is small or the overhead cost of a full plan exceeds its
value, produce a minimal subset. The minimum is:

1. **Scope** — what is in/out
2. **Risk register** — top risks with Likelihood × Impact
3. **Test strategy** — which levels + types + techniques
4. **Exit criteria** — when testing is "done enough"

This aligns with Google's "10-Minute Test Plan" philosophy: the plan should
enable a go/no-go decision, not document everything.

## Output Format

TEST-PLAN.md should be **markdown**, flat structure, scannable in under 5 minutes.
Tables preferred over prose for test items, risks, and criteria.

## Sources

- [IEEE SA — IEEE/ISO/IEC 29119-3](https://standards.ieee.org/ieee/29119-3/7499/) — standard metadata
- [ISO 29119-3:2021](https://www.iso.org/standard/79429.html) — official ISO page
- [Wikipedia — ISO/IEC 29119 (Controversy section)](https://en.wikipedia.org/wiki/ISO/IEC_29119) — Stop 29119 petition context
- [Google Testing Blog — The 10-Minute Test Plan (2011)](https://testing.googleblog.com/2011/09/10-minute-test-plan.html) — minimum viable inspiration
