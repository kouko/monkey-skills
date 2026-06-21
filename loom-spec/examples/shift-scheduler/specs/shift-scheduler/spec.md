# shift-scheduler — spec delta

## ADDED Requirements

### Requirement: Auto-generate a weekly schedule from availability, skills, and labor rules
The system MUST generate a weekly staff schedule that assigns employees to shifts only when the employee is available, holds every required skill (valid at shift time), and the assignment violates no HARD labor rule.

#### Scenario: Happy-path generation produces a feasible schedule
- GIVEN a planning unit with shifts, available employees who hold the required skills, and an active HARD labor-rule profile
- WHEN the manager triggers auto-generation
- THEN the engine returns a feasible schedule in which every assigned employee is available, skill-eligible, and violates no HARD rule

#### Scenario: Unavailable employee is never assigned
- GIVEN an employee whose Availability marks a shift's window as a hard-block (unavailable)
- WHEN the engine generates the schedule
- THEN that employee is not assigned to that shift

#### Scenario: Missing required skill blocks the assignment
- GIVEN a shift that requires a skill no available employee holds in a Certified or ExpiringSoon state at the shift's date
- WHEN the engine generates the schedule
- THEN the shift is reported as having an unsatisfiable skill requirement and no skill-ineligible employee is assigned to it

### Requirement: Enforce HARD labor rules and price SOFT rules
The system MUST treat HARD labor rules (legal minima such as minimum rest, minor-hour caps, mandatory breaks) as infeasibility constraints that cannot be violated, and SHOULD treat SOFT rules (cost/preference) as a penalty added to the optimization objective.

#### Scenario: Minimum-rest violation is infeasible
- GIVEN a minimum-rest HARD rule of 11 hours between consecutive shifts
- WHEN a candidate assignment would leave fewer than 11 hours between an employee's two shifts
- THEN the engine rejects that assignment as a HARD-rule violation

#### Scenario: Overtime is allowed at a soft cost, not blocked
- GIVEN a SOFT overtime rule applying a premium beyond 40 weekly hours
- WHEN the only feasible coverage requires an employee to exceed 40 hours
- THEN the engine MAY produce the assignment and records the overtime premium in the schedule's cost

#### Scenario: Boundary at exactly max weekly hours
- GIVEN an employee with a HARD max-weekly-hours cap of 40 who is currently scheduled for exactly 40 hours
- WHEN the engine evaluates assigning one more hour to that employee
- THEN the assignment is rejected (the cap is inclusive: 40 is allowed, 41 is not)

### Requirement: Report generation outcome with an actionable infeasibility explanation
The system MUST return a generation outcome of feasible, partial, or infeasible, and on a partial or infeasible outcome it MUST name the binding constraint(s) so the manager can act.

#### Scenario: Infeasible outcome names the binding constraint
- GIVEN a week whose required coverage cannot be met under the HARD rules
- WHEN generation completes
- THEN the outcome is infeasible and the result names the binding constraint (e.g. the understaffed shift and the unmet skill or headcount)

#### Scenario: Demand exceeding total capacity is reported, not silently under-staffed
- GIVEN total required staffed hours that exceed the total available capacity of all eligible employees
- WHEN generation runs
- THEN the outcome is infeasible with the shortfall quantified, and the engine does not silently publish an under-staffed schedule as success

#### Scenario: Empty inputs yield a defined result, not a crash
- GIVEN a week with zero shifts (or zero available employees)
- WHEN generation runs
- THEN the engine returns a defined result (a valid empty schedule for zero shifts; an explicit unfillable outcome for zero available employees) rather than an error

### Requirement: Schedule lifecycle is review-then-publish with auditable transitions
The system MUST require a manager review-and-approve step before a generated schedule becomes Published, and MUST keep an append-only audit record of post-publish changes.

#### Scenario: Generated schedule cannot skip review
- GIVEN a schedule in a Generated state (feasible or partial)
- WHEN a publish is attempted without an approval step
- THEN the publish is refused until the manager approves it via UnderReview

#### Scenario: Post-publish change is recorded in the audit log
- GIVEN a Published schedule
- WHEN a manager edits an assignment after publish
- THEN an append-only audit entry records the actor, timestamp, and change, and (where applicable) the predictability-pay trigger

### Requirement: Every roster mutation re-validates against labor rules and coverage
The system MUST re-validate against HARD labor rules and shift coverage on every roster mutation — engine placement, manager override, and applied swaps alike — before the mutation reaches a Confirmed or Applied state.

#### Scenario: Manager override is re-validated
- GIVEN a manager overrides an engine-proposed assignment
- WHEN the override is submitted
- THEN the engine re-validates it against HARD rules; a HARD violation is flagged at confirm time and the override is not silently confirmed

#### Scenario: Approved swap still re-validates before it applies
- GIVEN a SwapRequest that a manager has approved
- WHEN the system attempts to apply it
- THEN the engine re-validates the receiving employee against minimum-rest and overtime and the giving side against minimum coverage, and a failing check moves the swap to Rejected rather than Applied

#### Scenario: Giveaway that would understaff a shift is rejected
- GIVEN a give-away SwapRequest with no replacement pickup that would drop the shift below required headcount
- WHEN the swap is validated
- THEN the swap is rejected with an understaffing reason

### Requirement: Concurrent edits and duplicate generation runs are made safe
The system MUST prevent lost updates from concurrent edits via version checking, and MUST ensure a duplicate generation trigger does not start a second writing run against the same schedule.

#### Scenario: Stale concurrent write is rejected
- GIVEN two managers both editing schedule S at version v3
- WHEN the first save commits (advancing the version) and the second save is submitted against stale v3
- THEN the second write is rejected with a version-conflict and the first manager's edits are not overwritten

#### Scenario: Duplicate generate trigger is de-duplicated
- GIVEN a generation run already in flight for schedule S
- WHEN the manager triggers generation for S again
- THEN the second request is de-duplicated (returns the in-flight run's handle) and no second run writes S

#### Scenario: Crash mid-generation leaves no torn schedule
- GIVEN the engine has written part of the assignments for a run
- WHEN the process crashes before completion
- THEN the schedule is left in its pre-generation state (the write is all-or-nothing) and is not surfaced as a valid partial result

### Requirement: Skill and certification validity is checked at shift time
The system MUST evaluate skill and certification validity as of the shift's date, not as of the generation time, and MUST hard-block assignment when a required certification is Expired or Revoked at the shift's date.

#### Scenario: Certification expiring mid-week blocks the later shift
- GIVEN an employee whose required certification expires on Wednesday
- WHEN the engine considers assigning them to a Thursday shift requiring that certification
- THEN the assignment is rejected because the certification is not valid at the shift's date

### Requirement: Only Active employees are schedulable and terminations re-open future assignments
The system MUST schedule only employees in the Active state, and when an employee becomes OnLeave, Suspended, or Terminated, it MUST re-open their future assignments in the affected published week rather than silently retaining them.

#### Scenario: Mid-week termination orphans and re-opens future shifts
- GIVEN an employee with assignments on published shifts later in the week
- WHEN their employment is terminated effective immediately
- THEN their future assignments for that week become Open/flagged, the schedule is marked needs-attention, and the historical audit record of prior assignments is preserved

#### Scenario: Protected leave excludes from assignment without a fairness penalty
- GIVEN an employee on approved protected leave (e.g. FMLA/parental/jury/medical) spanning the week
- WHEN the engine generates the schedule and computes fair-distribution metrics
- THEN the employee is excluded from assignment and the exclusion is not counted against them as declined shifts in fairness or disparate-impact metrics

### Requirement: Time-related computations are correct across week, timezone, and DST boundaries
The system MUST compute rest gaps and notice windows using elapsed (UTC) time so that week boundaries, multiple timezones, and daylight-saving transitions do not mask a violation.

#### Scenario: Minimum rest is enforced across a DST transition
- GIVEN a clopening pair (close then open) within a week that contains a daylight-saving transition
- WHEN the minimum-rest rule is checked
- THEN rest is computed in elapsed UTC time so the transition hour does not falsely satisfy or falsely violate the rule

#### Scenario: Minimum rest is enforced across the week seam
- GIVEN the last shift of week N ends at 23:00 and the first shift of week N+1 starts at 05:00
- WHEN the two weekly schedules are generated independently
- THEN the minimum-rest rule is still enforced across the seam between the two weeks

### Requirement: Access control and PII confidentiality
The system MUST restrict each action and each data field to authorized actors, and MUST treat hourly cost and date of birth as sensitive PII not exposed to peers.

#### Scenario: Employee cannot assign a coworker
- GIVEN an employee (not a manager) attempting to assign another employee to a shift
- WHEN the action is submitted
- THEN it is denied because only a manager (or authorized role) may assign

#### Scenario: Cost and birthdate are hidden from peers
- GIVEN an employee viewing the published schedule
- WHEN they open a coworker's shift detail
- THEN neither the coworker's hourly cost nor date of birth is exposed; minor status is surfaced only as a derived non-PII flag if needed

### Requirement: Staff are notified of publish and changes, and the notice timestamp is recorded
The system MUST notify each affected employee when a schedule is published or their assignment changes, MUST record the delivery timestamp, and MUST NOT start the predictive-scheduling notice clock until delivery is confirmed.

#### Scenario: Publish notifies affected staff and records delivery time
- GIVEN a schedule is published
- WHEN publish completes
- THEN each affected employee is notified via their preferred channel and the delivery timestamp is recorded

#### Scenario: Failed notification does not start the notice clock
- GIVEN a publish notification that fails to deliver
- WHEN the failure is detected
- THEN it is retried and escalated, and the predictability-pay / advance-notice clock does not start until delivery is confirmed
