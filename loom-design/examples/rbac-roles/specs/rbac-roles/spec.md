# RBAC roles & per-workspace assignment — delta

## ADDED Requirements

### Requirement: Admin defines roles
An admin with the `role:manage` permission MUST be able to create a role within
a scope, name it uniquely within that scope, and edit its permission set.

#### Scenario: Create a role in a workspace
- GIVEN an admin holding `role:manage` in workspace W
- WHEN the admin creates a role named "Editor" scoped to W
- THEN the role is persisted in W with status active and an empty permission set

#### Scenario: Reject a duplicate role name in the same scope
- GIVEN workspace W already has a role named "Editor"
- WHEN an admin creates another role named "Editor" scoped to W
- THEN the system rejects the creation with a uniqueness-conflict error and no role is created

#### Scenario: A non-admin cannot define a role
- GIVEN a user without `role:manage` in workspace W
- WHEN that user attempts to create a role in W
- THEN the system denies the action with a 403 and records the denied attempt in the audit log

### Requirement: Admin attaches permissions to a role
An admin MUST be able to grant catalog permissions to a role, and a permission removed from the catalog SHALL NOT continue to grant access through any role.

#### Scenario: Grant a permission to a role
- GIVEN an admin holding `role:manage` and a role "Editor" in workspace W
- WHEN the admin adds the `document:write` permission to "Editor"
- THEN "Editor"'s permission set includes `document:write`

#### Scenario: A retired catalog permission stops granting
- GIVEN a role "Editor" bundling permission `legacy:action` and an active assignment of "Editor"
- WHEN `legacy:action` is retired from the permission catalog
- THEN the retired permission no longer appears in any effective-permission evaluation

### Requirement: Admin assigns a role to a user within a workspace
An admin MUST be able to assign a role to a user in a specific workspace, and the assignment SHALL be scoped to that workspace only; the target user MUST be a member of that workspace.

#### Scenario: Assign a role to a workspace member
- GIVEN an admin in workspace W and a user U who is an active member of W
- WHEN the admin assigns role "Editor" to U in W
- THEN an active assignment (U, Editor, W) exists and U's effective permissions in W include "Editor"'s permission set

#### Scenario: Cannot assign a role to a non-member
- GIVEN a user U who is not a member of workspace W
- WHEN an admin attempts to assign role "Editor" to U in W
- THEN the system blocks the assignment and reports that U must be a member of W first

#### Scenario: A workspace-scoped role cannot be assigned in another workspace
- GIVEN role "Editor" scoped to workspace A
- WHEN an admin attempts to assign "Editor" to a user in workspace B
- THEN the system rejects the assignment with a scope-mismatch error

#### Scenario: The same role is assigned independently per workspace
- GIVEN a user U who is a member of both workspace A and workspace B
- WHEN an admin assigns an "Editor"-equivalent role to U in A and revokes it in B
- THEN U's effective permissions reflect the grant in A and the absence of the grant in B independently

### Requirement: Effective permissions are evaluated per workspace
The system MUST compute a user's effective permissions in a workspace as the union of the permission sets of that user's active, non-expired assignments scoped to that workspace, and SHALL recompute on any grant change.

#### Scenario: Revoking an assignment removes its permissions
- GIVEN user U with an active assignment (U, Editor, W) granting `document:write`
- WHEN an admin revokes that assignment
- THEN U's effective permissions in W no longer include `document:write` and the assignment status is revoked

#### Scenario: An expired assignment grants nothing
- GIVEN an assignment (U, Editor, W) with an expires_at in the past
- WHEN the scheduler evaluates expiries
- THEN the assignment status becomes expired and contributes no permissions to U's effective set

### Requirement: Role deletion is blocked while live assignments exist
The system MUST NOT hard-delete a role that has live assignments; the admin SHALL deprecate it instead.

#### Scenario: Block deletion of a role in use
- GIVEN a role "Editor" with at least one active assignment
- WHEN an admin attempts to delete "Editor"
- THEN the system blocks the deletion and offers to deprecate the role instead

### Requirement: Privilege-management actions are guarded
The system MUST prevent a workspace from being left with zero admins and SHOULD guard self-privilege-escalation according to policy.

#### Scenario: Prevent zero-admin lockout
- GIVEN workspace W has exactly one user holding `role:manage`
- WHEN that user attempts to revoke their own admin-granting assignment
- THEN the system blocks the revocation to keep at least one admin in W

### Requirement: Authorization fails closed
When the identity store or permission data is unavailable, the system MUST deny the action rather than allowing it.

#### Scenario: Deny on identity-store outage
- GIVEN the identity provider is unreachable during a permission check
- WHEN a user attempts an action requiring `document:write`
- THEN the system denies the action (fail-closed) and surfaces a retriable error

### Requirement: Concurrent grant changes do not lose updates
The system MUST serialize or optimistically guard concurrent changes to the same (user, role, workspace) assignment so that no update is silently lost.

#### Scenario: Concurrent revoke and re-assign
- GIVEN two admins acting on the same assignment (U, Editor, W) at the same time
- WHEN one revokes while the other edits
- THEN the system applies a single consistent final state and rejects the stale write with a conflict
