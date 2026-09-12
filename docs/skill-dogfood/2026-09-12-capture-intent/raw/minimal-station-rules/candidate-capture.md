# Mute one project's activity email
originator: kouko
kind: product
needs-design: no — no new user-read or user-input surface or multi-object behaviour is established
status: confirmed 2026-09-12

## Problem
Project activity email repeatedly interrupts project members.

## Proposed outcome
Project members can mute one project so that project's activity email stops.

## Acceptance
1. Project activity email for the muted project stops.
2. In-app notifications remain unchanged.
3. Global settings remain unchanged.

## Constraints
- In-app notifications stay unchanged.
- Global settings stay unchanged.

## Value case
GO — stopping repeated project activity email interruptions benefits project members.

## Out of scope
- Unmuting the project.

## Open questions
- none

---

Hand off `2026-09-12-mute-one-project-activity-email` to `loom-code:write-plan`.

Automatic PR publication: opted out; the `publication` field is absent.

Questions for the plan’s `## Questions asked` section:

Decision point ① — what — You want project members to be able to mute one project so that project's activity email stops, while in-app notifications and global settings remain unchanged. When it is done, the muted project's activity email will stop. Is that right?

`write-plan` must not run decision point ① again because the intent is already confirmed. Decision point ② happens at `write-spec` only when `needs-design: yes`; this intent proceeds directly to planning.
