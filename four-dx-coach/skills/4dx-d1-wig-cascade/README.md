# 4DX D1 — Team WIG Cascade

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Coach or audit you (the leader-of-leaders) on translating an already-set org Primary WIG into Team WIGs across 3-7 subordinate teams via Ch 7's four cascade rules. **Two modes**: coach (build from scratch) + audit (diagnose existing cascade map + sub-leader complaints).

## When this skill activates

**Coach-mode** (build from scratch):
- "How do I translate the org WIG to my team-leaders?"
- "Each of my managers needs a WIG — how do we pick them?"
- A WIG was handed down from above and you have to decompose it
- Multi-team org cascading region → district, division → team

**Audit-mode** (diagnose existing cascade):
- "Audit our cascade — sub-leaders complaining"
- "Boss says cascade is wrong, here's the map"
- Sub-leaders saying "imposed on us" / "doesn't ladder up" / "we have to do many things"
- First-attempt cascade produced 7+ Battle WIGs or assigned the same WIG verbatim to every team — and you want diagnosis (not rebuild)

## What it does

Consultant-to-leader-of-leaders. Two protocols (load on demand):

### `protocols/coach-mode.md` — Socratic 10-step build

Primary work: enforcing **Rule 3 — veto, don't dictate**.

1. Confirm the upstream Primary WIG (X→Y→When)
2. Enumerate subordinate teams (3-7 ideal)
3. Classify cascade shape (functionally diverse vs similar)
4. Identify Key Battles (Opryland: 17 → 3; 2-3 typical)
5. Solicit Team WIG proposals (pull, not push)
6. Apply the ladder-up test (arithmetic, not vibe)
7. Apply the veto test (accept or return; never rewrite)
8. One-WIG-per-individual rule
9. Cascade-depth check (>2 layers? re-run per layer)
10. Output the cascade map

### `protocols/audit-mode.md` — Consultant verdict on existing cascade

Reads cascade map + sub-leader critique → per-rule verdict table → revision + re-negotiation scripts.

- "imposed on us" → Rule 3 violation
- "doesn't ladder up" → Rule 2 violation
- "have to do many things" → Rule 1 violation
- "can't tell whether we won" → Rule 4 violation
- 5+ Battles → Battles-count fail (narrowing incomplete)
- Action-list Team WIG → Targets-not-Plans fail

## When NOT to use

| Situation | Where to go instead |
|---|---|
| Org Primary WIG not yet set | `4dx-d1-wig-formulation` |
| Leader runs only ONE team (no subordinate team-leaders) | `4dx-d1-wig-formulation` |
| Solo / individual goal | `4dx-d1-wig-formulation` |
| Single Team WIG audit (no cascade involved) | `4dx-d1-wig-formulation` audit-mode |
| Cross-layer audit (cascade + leads + scoreboard + cadence) | `4dx-audit` (full-stack) |
| OKR / KR / quarterly objectives cascade | `using-four-dx-coach` |
| Single-shot project with fixed end-state | Project management (WBS / Gantt) |
| Methodology-fit unclear | `4dx-meta-strategy-triage` |

## Source

Distilled from *The 4 Disciplines of Execution* (2nd ed., 2021), Chapter 7 — Translating Organizational Focus Into Executable Targets. Three anchor cases: Opryland Hotel (functionally diverse cascade — 75 teams, 17 → 3 Battles), Multi-outlet retailer (functionally similar cascade with leaf-team Battle-selection autonomy), Sydney accounting firm (small-company cascade, intermediate Battle layer collapses).

See [`SKILL.md`](SKILL.md) for the orchestrator, [`protocols/coach-mode.md`](protocols/coach-mode.md) for the Socratic 10-step build (incl. Rules 1-4, Targets-not-Plans, cascade-too-deep-in-one-pass anti-pattern), and [`protocols/audit-mode.md`](protocols/audit-mode.md) for the consultant verdict matrix on existing cascade artifacts.
