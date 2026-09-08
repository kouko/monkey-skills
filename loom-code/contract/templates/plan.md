# <title> — plan
intent: <change-id>@<sha>
spec: docs/loom/<change-id>/spec.md@<sha>     # only when needs-design: yes
charter: 1.0

## Current State Evidence                  # only when needs-design: no (spec doesn't exist, the five lines go here)
<!-- each bullet ≤30 words (checker rule plan.field-caps) -->
- Forward/Reverse/Error/Data/Boundary: <path and anchor>

## Task DAG
<!-- When a spec requirement changes after this commit, the un-landed
     tasks it touches are replaced and the reason is named in the commit
     message. Landed tasks stay as they are. -->
<wave segmentation; each task gets a stable ID; tasks with no dependency in the same wave can run in parallel>

**<W0-01> <title>**  after: <ids>  acceptance: <numbers>
- Files: <files this task touches>            <!-- ≤8 comma-separated entries -->
- Test: A<n> positive: <case-id>; negative|boundary: <case-id>.  <!-- one pair per referenced Acceptance; ≤40 words -->
- Risk: <risk and the default choice; mark agent-decided>  <!-- ≤40 words -->

## Questions asked                        # every question asked at decision point ① (and at ② when it runs here)
<decision point id> — <what|behaviour|done|consequence> — <verbatim quote>
<!-- this is the durable record; closing review reads it directly -->

## Risks
<!-- each numbered item ≤40 words (checker rule plan.field-caps) -->
1. <plan-wide risk>
