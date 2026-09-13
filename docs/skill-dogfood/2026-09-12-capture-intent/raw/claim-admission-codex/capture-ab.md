## A

### Final intent

```markdown
# Mute project activity emails
originator: user
kind: product
needs-design: yes — the change affects notification behaviour across a selected project and other projects, and no existing specification covers it
status: confirmed 2026-09-12

## Problem
Project members are repeatedly interrupted by activity emails from a project they do not want email updates from.

## Proposed outcome
Project members can mute activity emails for one project without changing their other notification settings.

## Acceptance
1. A member can mute activity emails for one selected project.
2. After that project is muted, its activity emails no longer reach the member.
3. In-app notifications remain available.
4. Global notification settings remain unchanged.

## Constraints
- Only email notifications for the selected project stop.
- In-app notifications must remain unchanged.
- Global notification settings must remain unchanged.
- No pull request is opened automatically.

## Value case
GO — project members need relief now because repeated activity emails interrupt their work, while muting all notifications would remove updates they still want.

## Out of scope
- Unmuting a muted project is not supported by this change.

## Open questions
- none
```

### Handoff

Hand off `2026-09-12-project-activity-email-muting` to `loom-design:write-spec`.

The following belongs in the plan’s `## Questions asked` section:

```text
decision point ① — what — You want project members to be able to mute activity emails for one project, so that emails from that project stop while in-app notifications and global settings remain unchanged. You also do not authorize an automatic pull request. Is that right?
```

Decision point ① is already complete, so `write-plan` must not repeat it. Decision point ②—what the member does and sees—happens at `write-spec`.

## B

### Final intent

```markdown
# Mute one project's activity emails
originator: user
kind: product
needs-design: yes — the outcome distinguishes one project from other notification scope, and no product behaviour has yet been specified
status: confirmed 2026-09-12

## Problem
Project activity emails repeatedly interrupt members.

## Proposed outcome
Members can stop activity emails for one project while keeping in-app notifications and global settings unchanged.

## Acceptance
1. Activity emails for one project can be stopped.
2. In-app notifications are unchanged.
3. Global settings are unchanged.

## Constraints
- Only email for the project is affected.
- In-app notifications stay unchanged.
- Global settings stay unchanged.
- No pull request is opened automatically.

## Value case
GO — the repeated email interruptions are the concrete reason to make this change now.

## Out of scope
- This change does not cover unmuting.

## Open questions
- none
```

### Handoff

Continue with the product-behaviour specification for muting one project’s activity emails.

Question already answered:

```text
decision point ① — what — You want members to stop activity emails for one project while in-app notifications and global settings stay unchanged, and you do not want an automatic pull request. Is that right?
```
