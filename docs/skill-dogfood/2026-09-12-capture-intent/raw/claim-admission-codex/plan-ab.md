## A

```markdown
# Project activity email mute — plan
intent: <change-id>@<confirmed-intent-sha>
spec: docs/loom/<change-id>/spec.md@<confirmed-spec-sha>
charter: 1.0

## Task DAG

### Wave 0

**W0-01 Apply project mute at the existing notification boundary**  after: none  acceptance: 1, 2, 3
- Files: existing ProjectNotificationPolicy file, existing project mute-action file, existing email dispatch file, existing notification tests
- Test: A1 positive: a1-muted-email; boundary: a1-channel-boundary. A2 positive: a2-in-app-unchanged; boundary: a2-email-only. A3 positive: a3-global-unchanged; boundary: a3-project-scope.
- Risk: REQ-1–REQ-3; agent-decided: use the existing policy and separate dispatch paths because they are the stated implementation boundary.

## Questions asked

None at this station.

## Risks

1. Applying project mute outside the email dispatch boundary could change in-app notifications or global settings.
```

## B

```markdown
# Mute project activity emails — plan
intent: <change-id>@<confirmed-intent-sha>
spec: docs/loom/<change-id>/spec.md@<confirmed-spec-sha>
charter: 1.0

## Task DAG

### Wave 0

**W0-01 Connect the existing project mute action to activity-email dispatch**  after: none  acceptance: 1, 2, 3
- Files: existing ProjectNotificationPolicy file, existing mute-action file, existing email dispatch file, existing notification test files
- Test: A1 positive: muted-project-email; boundary: notification-channel. A2 positive: in-app-unchanged; boundary: email-path-only. A3 positive: global-settings-unchanged; boundary: project-policy-scope.
- Risk: REQ-1–REQ-3; agent-decided: keep the change within the existing project policy and dispatch boundary.

## Questions asked

None at this station.

## Risks

1. Scope leakage could affect the unchanged in-app path or global notification settings.
```
