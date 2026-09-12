```markdown
# Mute project activity email
originator: kouko
kind: product
needs-design: yes — a user-invoked product action has visible effects and no existing spec covers it
status: confirmed 2026-09-12

## Problem
Project activity email repeatedly interrupts project members.

## Proposed outcome
Project members can mute activity email for one project.

## Acceptance
1. A project member can mute one project.
2. After they mute that project, subsequent activity emails for that project stop.
3. In-app notifications and global settings remain unchanged.

## Constraints
- Muting one project must leave in-app notifications and global settings unchanged.

## Value case
GO — project members benefit now because repeated project activity email interrupts them.

## Out of scope
- Unmuting a project.

## Open questions
- none
```

Handoff to `loom-design:write-spec`:

```text
Change: 2026-09-12-mute-project-activity-email
Publication: automatic PR publication was explicitly opted out; the publication field is intentionally absent.

Questions asked for the plan's ## Questions asked section:
Decision point ① — what — You want project members to be able to mute one project so that subsequent activity emails for that project stop, while in-app notifications and global settings remain unchanged. Automatic publication after Review and publication checks would authorize a later non-forced push and Ready PR, while merge would remain a separate decision; you may opt out before publication. Is that right?

The intent is already confirmed, so write-plan must not run decision point ① again. Decision point ② — what the user does and what visible result follows — happens at write-spec.
```
