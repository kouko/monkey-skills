# Baseline brainstorm — auto-generate weekly staff schedule

Seed: "Let a manager auto-generate a weekly staff schedule respecting availability, skills, and labor rules."

## Requirements / behaviors

### Inputs / data model
- **Staff roster**: each employee has id, name, employment type (full-time / part-time / casual), contracted/target hours, hourly cost (optional, for cost-aware scheduling).
- **Skills / qualifications**: each employee carries a set of skills/certifications (e.g. barista, cashier, shift-lead, forklift, RN). Some may have expiry dates (certs lapse).
- **Availability**: per-employee weekly availability — preferred, available, and unavailable time windows; recurring patterns plus one-off exceptions (approved time-off, appointments).
- **Demand / coverage requirements**: per day and time-block, how many people are needed and which skills (e.g. "Mon 09:00–13:00: 2 cashiers + 1 shift-lead"). May be expressed as headcount per role or as a coverage curve.
- **Shift templates**: predefined shift shapes (open 07:00–15:00, mid, close) or free-form start/end with min/max length.
- **Labor rules / constraints** (see below) as configurable policy.
- **Scheduling period**: the target week (with timezone and week-start day defined).

### Core scheduling behavior
- Generate an assignment of employees → shifts for the target week that **satisfies all hard constraints** and **optimizes soft preferences**.
- Respect **availability**: never assign someone outside their available windows or during approved time-off.
- Respect **skills**: only assign an employee to a slot whose required skill they hold (and whose cert is unexpired).
- Respect **coverage**: meet the required headcount per role per time-block (no under-staffing of hard requirements).
- Respect **labor rules** as hard constraints:
  - Max hours per day / per week; min/max shift length.
  - Minimum rest between shifts (e.g. ≥11h; no "clopen" close-then-open).
  - Max consecutive working days; required days off per week.
  - Mandatory breaks for shifts over a length threshold (meal/rest breaks).
  - Overtime thresholds and whether OT is allowed / needs approval.
  - Minor (under-18) restrictions if applicable (hours, late-night).
- **Soft optimization objectives** (configurable weights / priority order):
  - Honor stated preferences (preferred shifts, preferred days off).
  - Fairness — distribute desirable/undesirable shifts and total hours equitably over time.
  - Minimize labor cost / minimize overtime.
  - Continuity — keep people on consistent shifts week-to-week where possible.
  - Minimize number of distinct people per day (fewer handoffs) — optional.

### Output / interaction
- Produce a **draft schedule** (not auto-published) for manager review: grid by day × time, plus per-employee view.
- Show **why** a slot is filled / unfilled — explainability: which constraint blocked a candidate.
- Flag **violations and gaps**: unfilled required coverage, soft-constraint compromises, anyone over/under target hours.
- Allow **manual override / lock**: manager pins certain assignments, then re-runs auto-fill around the locked set.
- **Determinism / reproducibility**: same inputs → same (or explained) output; seedable if randomized.
- **Idempotent re-run**: regenerating shouldn't churn the whole schedule if inputs barely changed (stability).
- **Publish / notify**: once approved, publish and notify staff; track acknowledgements (out-of-MVP-able but worth specifying).
- **Total / partial generation**: generate from scratch, or fill only the gaps in a partially-built schedule.

### Non-functional
- Performance: solve a realistic week (e.g. 50 staff, 200 slots) within an acceptable time (seconds, not minutes); define the target.
- Timezone & DST correctness for all time math.
- Auditability: record who generated/edited what and when.
- Permissions: only authorized managers can generate/publish for their location/team.

## Edge cases & failure modes

### Infeasibility / coverage
- **No feasible solution** — demand exceeds available qualified staff, or constraints over-tight. Must not silently fail: return best partial schedule + explicit list of unmet coverage and the binding constraints.
- **Partial coverage** — some slots fillable, others not; prioritize critical roles (e.g. must always have a shift-lead) over nice-to-have.
- **Over-staffing** — more available staff than demand; decide who to leave unscheduled fairly, respect minimum-hours guarantees for full-timers.
- **Single point of failure skill** — only one person holds a required cert; if they're unavailable, that slot is structurally unfillable (flag clearly).

### Availability / data conflicts
- Overlapping or contradictory availability entries for one person.
- Approved time-off that overlaps a manager-locked assignment (which wins? — flag the conflict).
- Availability submitted after generation; stale availability.
- Employee available but at their max weekly hours already.
- Last-minute change: someone calls in sick after publish — re-optimization / find-replacement path (likely out of MVP but the model should not preclude it).

### Time / boundary math
- Shifts crossing midnight; week boundary (Sun→Mon) shift attribution.
- DST spring-forward / fall-back changing shift duration.
- Timezones across multi-location teams.
- Public holidays — different demand and possibly holiday-pay / different rules.
- Rest-period rule spanning two scheduling periods (last shift of this week vs first of next).

### Labor-rule conflicts
- Two hard rules conflict (e.g. min-hours guarantee vs max-hours cap for the same person) — undefined-behavior risk; need a documented precedence / detection.
- Break insertion changing effective coverage (person on break ≠ covering).
- Overtime needed to meet coverage but OT disallowed — which gives way? policy decision.
- Minor-worker rules interacting with late shifts.

### Data quality / input
- Missing or malformed inputs: no availability submitted, employee with zero skills, demand for a skill nobody holds.
- Duplicate staff records; inactive/terminated staff still in roster.
- Expired certification not flagged → illegal assignment.
- Demand defined with gaps or overlaps in time-blocks.
- Empty roster / empty demand (degenerate but must not crash).

### Process / concurrency
- Two managers generate for overlapping teams simultaneously — conflicting writes.
- Re-generate after partial manual edits — must respect locks, not blow them away.
- Generation runs against a roster that changes mid-run.
- Huge org → performance blowup / timeout; need a bound and graceful degradation.

### Trust / correctness
- Optimizer returns a technically-feasible but obviously bad/unfair schedule (one person every closing shift) — fairness must be a real objective, not an afterthought.
- Non-determinism causing manager distrust ("ran it twice, got different results").
- Silent constraint relaxation (solver drops a soft rule without telling anyone).

## Open questions

- **Constraint hardness**: which rules are hard (never violate, legal) vs soft (preferences)? Is this fixed or per-tenant configurable? What's the priority order when soft constraints conflict?
- **Infeasibility policy**: when no full solution exists, do we return best-effort partial + report, or refuse? How are roles prioritized for partial coverage?
- **Optimization objective**: single objective or weighted multi-objective? Who sets the weights (fairness vs cost vs preference)? Is fairness measured within-week or rolling over weeks?
- **Demand definition**: headcount-per-role-per-block, or a continuous coverage curve, or derived from forecast/sales? What granularity (15-min? hourly?)?
- **Shift shape**: fixed templates only, or solver free to choose arbitrary start/end within bounds?
- **Scope of labor rules**: which jurisdiction(s)? Are rules hardcoded, config, or pluggable per region/union? Any union/contract rules (seniority bidding)?
- **Locking & regeneration semantics**: exactly how do manual locks interact with re-runs? Does the solver minimize churn vs the prior published schedule?
- **Determinism requirement**: must runs be reproducible? Is any randomness acceptable?
- **Publish/notify scope**: is notification + acknowledgement in scope, or is the deliverable just the draft grid?
- **Performance envelope**: expected staff count, slots, locations — to pick algorithm (greedy heuristic vs CP/ILP solver) and set a time budget.
- **Real-time vs batch**: one-shot weekly generation, or continuous re-optimization on disruptions (sick calls)?
- **Self-service**: do employees submit availability/preferences in-system, or does the manager enter everything?
- **Pay/cost awareness**: is cost an input/objective at all, or purely coverage + rules in MVP?
- **History / fairness memory**: does the generator need prior weeks' data to balance fairness over time, or is it stateless per week?
- **Definition of "respecting"**: in the seed, does "respecting labor rules" mean hard-guarantee (legal) or best-effort? Drives the whole hard/soft architecture.

## Acceptance criteria (what I'd want specified)

- Given valid roster + availability + skills + demand + rules, the generator produces a schedule where **every assignment lies within the employee's availability**, the employee **holds the required unexpired skill**, and **no hard labor rule is violated** — verified by an independent checker.
- Given demand that **can** be fully covered, **all required coverage slots are filled**.
- Given **infeasible** demand, the system returns a partial schedule **plus an explicit, complete list** of unmet slots and the **binding reason** for each (no silent failure).
- Given **manager-locked** assignments, a re-run **preserves every lock** and fills only the remainder.
- Given **identical inputs**, two runs produce **identical output** (or differences are explained), per the determinism decision.
- Hard constraints are **never** silently relaxed; any soft-constraint compromise is **reported**.
- Time math is correct across **midnight, week boundaries, DST, and timezones** (covered by explicit test cases).
- Malformed/empty inputs produce a **clear validation error**, not a crash or a silently-wrong schedule.
- Fairness objective demonstrably **spreads undesirable shifts and total hours** within the configured fairness window (measurable metric, e.g. max-min spread under threshold).
- A realistic-scale instance solves **within the stated time budget**.
