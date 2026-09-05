# <title> — plan
intent: <change-id>@<sha>
spec: docs/loom/<change-id>/spec.md@<sha>     # only when needs-design: yes
charter: 1.0

## Current State Evidence                  # only when needs-design: no (spec doesn't exist, the five lines go here)
<!-- each bullet ≤30 words (checker rule plan.field-caps) -->
- Forward/Reverse/Error/Data/Boundary: <path and anchor>

## Task DAG
<wave segmentation; each task gets a stable ID; tasks with no dependency in the same wave can run in parallel>

**<W0-01> <title>**  after: <ids>  review: after-task
<!-- the first two after-task lines need no reason; the third onward is
     written as `review: after-task — <reason>`, read by checker rule
     intake.after-task-budget -->
- Files: <files this task touches>            <!-- ≤8 comma-separated entries -->
- Test: <the failing test written first>      <!-- ≤40 words -->
- Risk: <risk and the default choice; mark agent-decided>  <!-- ≤40 words -->

**<Wn-memory> Memory step — graduated probes and store entries**  after: <last task ids>
- Files: <graduated probe copies under the repo's permanent test directory; docs/loom/memory/ entries>
- Test: <the store integrity check; the graduated copies passing>
- Risk: <risk and the default choice; mark agent-decided>

## Questions asked                        # every question asked at decision point ① (and at ② when it runs here)
<decision point id> — <what|behaviour|done|consequence> — <verbatim quote>
<!-- the review station copies this section into review.json's questions[]
     at the first checkpoint -->

## Risks
<!-- each numbered item ≤40 words (checker rule plan.field-caps) -->
1. <plan-wide risk>
