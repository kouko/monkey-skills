# Mute one project’s activity email
originator: kouko
kind: product
needs-design: yes — the confirmed outcome includes a user-invoked product action with visible effects, and no existing spec was supplied
status: confirmed 2026-09-10

## Problem
Project activity email repeatedly interrupts project members.

## Proposed outcome
Users can mute one project so only that project’s activity email stops.

## Acceptance
1. Users can mute one project.
2. Only that project’s activity email stops for project members.
3. In-app notifications remain unchanged.
4. Global settings remain unchanged.

## Constraints
- The change applies to one project.
- In-app notifications remain unchanged.
- Global settings remain unchanged.

## Value case
GO — stopping repeated project activity email interruptions benefits project members.

## Out of scope
- This change does not design, implement, or verify unmute.

## Open questions
- none

Hand off `2026-09-10-mute-one-project-activity-email` to `loom-design:write-spec`.

Questions asked: none.

`write-plan` must not repeat decision point ① because the intent is already confirmed. Product-behaviour confirmation happens at `write-spec` before planning.
