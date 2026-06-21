# Baseline brainstorm — roles & permissions across workspaces

Seed: "Let an admin define roles and assign permissions to users across multiple workspaces."

## Requirements / behaviors

### Core domain model
- **Workspace** is the tenancy boundary. A user can belong to many workspaces; a role/permission grant is scoped to one workspace (no implicit cross-workspace leakage).
- **Permission** = an atomic capability (e.g. `documents.read`, `members.invite`, `billing.manage`). Permissions are defined by the system, not freely typed by admins (avoids typo-permissions that grant nothing or everything).
- **Role** = a named bundle of permissions, scoped to a workspace. A role belongs to exactly one workspace unless it's a built-in/system role available everywhere.
- **Assignment** = (user, role, workspace) tuple. A user can hold multiple roles in the same workspace; effective permissions = union of all assigned roles' permissions.

### Role management (admin-facing)
- Admin can **create** a custom role: name + description + selected set of permissions.
- Admin can **edit** a role: rename, change description, add/remove permissions. Edits propagate to all users currently holding the role (define propagation timing — immediate vs next-session).
- Admin can **delete** a role — but only after deciding what happens to users still assigned to it (block, reassign, or orphan-then-warn).
- Admin can **list/view** roles in their workspace and see which users hold each role.
- **Built-in roles** (e.g. Owner, Admin, Member, Viewer) ship by default, are non-deletable, and have a sane default permission set. Whether they're editable is a design decision.
- Role names must be **unique within a workspace** (not globally).

### Permission assignment
- Admin assigns/unassigns roles to users within a workspace.
- Bulk assignment (assign a role to many users at once) is likely needed at any real scale.
- Permission checks must be **enforced server-side** on every protected action — the UI hiding a button is not authorization.
- A permission-check API/middleware: `can(user, permission, workspace) -> bool`.

### Multi-workspace specifics
- The **Owner/super-admin** of a workspace is distinct from a platform/system admin who may operate across all workspaces.
- A user's role in workspace A grants nothing in workspace B.
- Inviting an existing platform user into a new workspace assigns them a default role there.
- Default role for newly-joined members should be configurable per workspace.

### Authorization semantics
- **Deny-by-default**: no permission unless explicitly granted by some assigned role.
- Decide whether explicit **deny** permissions exist (allow-only is simpler; deny-overrides adds power but complexity). Recommend allow-only for v1.
- **Self-protection**: an admin must not be able to remove their own last admin/owner permission and lock themselves (and possibly the workspace) out.

### Auditing & observability
- Every role create/edit/delete and every assignment change should be **audit-logged** (who, what, when, target, before/after).
- Ability to answer "who can do X?" and "what can user Y do?" for compliance.

### Non-functional
- Permission checks are on the hot path → must be **fast** (cache effective permissions, invalidate on role/assignment change).
- Concurrent edits to the same role must not corrupt the permission set (optimistic locking / last-write-wins decision).
- Scales to many workspaces, many users per workspace, many roles.

## Edge cases & failure modes

- **Last-owner removal**: removing/demoting the only Owner of a workspace → must be blocked or require ownership transfer first.
- **Self-demotion / self-lockout**: admin removes their own admin role → confirm intent or block.
- **Deleting a role still in use**: orphaned users, or actions that silently lose access. Need explicit policy.
- **Editing a role mid-session**: a user with an active session loses a permission — does the in-flight request fail, or only the next one? Token/permission cache staleness.
- **Permission removed from system entirely**: roles referencing a now-deleted permission ID → dangling references.
- **Duplicate role names**: same name in same workspace (reject) vs same name across workspaces (allow).
- **Conflicting roles**: user holds two roles, one grants and (if deny exists) one denies the same permission → precedence rule must be defined.
- **Cross-workspace leakage bug**: a check that forgets the workspace scope → user acts in the wrong workspace. This is the highest-severity failure class.
- **Privilege escalation**: a user with `roles.manage` could grant themselves more than they have ("grant ≤ own permissions" guardrail, or explicitly allow).
- **Assigning a role from workspace A to a user in workspace B**: must be rejected (scope mismatch).
- **User removed from workspace** but assignment rows remain → stale grants; deactivation must cascade.
- **User deactivated/deleted globally** while holding roles in N workspaces → cleanup.
- **Race**: two admins edit the same role simultaneously; or one deletes while another assigns.
- **Empty role** (zero permissions) — allowed? It's harmless but confusing; allow with a warning.
- **Massive bulk assign** partially fails midway → all-or-nothing vs partial-with-report.
- **Built-in role tampering**: attempt to delete/neuter Owner → must be refused.
- **Permission check for a user not in the workspace at all** → deny, don't error/leak existence.
- **Time-of-check/time-of-use**: permission revoked between the check and the action.
- **Caching staleness**: revoked permission still honored because cache wasn't invalidated → security hole.
- **Circular/nested roles** (if roles can contain roles) → infinite expansion; either disallow nesting or detect cycles.

## Open questions

1. **Permission granularity**: coarse (resource-level: `documents.*`) or fine (action-level: `documents.read/write/delete`)? Resource × action matrix?
2. **Role nesting / inheritance**: can a role inherit another role's permissions, or are roles flat bundles? (Flat is simpler; recommend flat for v1.)
3. **Deny rules**: allow-only, or allow + explicit deny with precedence? (Recommend allow-only v1.)
4. **Built-in role editability**: are Owner/Admin/Member/Viewer fixed, or can admins tweak their permission sets?
5. **Cross-workspace roles**: are roles always workspace-local, or can a platform admin define org-wide templates that propagate to all workspaces?
6. **Who can manage roles**: only Owner, or any role holding `roles.manage`? Can that be delegated?
7. **Escalation guardrail**: may an admin grant a permission they don't themselves hold? (Recommend "grant ≤ own".)
8. **Resource-scoped permissions**: is permission always workspace-wide, or can it be scoped to a specific resource/folder within a workspace (more like ReBAC)? Big scope decision.
9. **Propagation timing**: do role edits take effect immediately (force re-check / session invalidation) or at next login/token refresh?
10. **Audit retention & access**: how long are audit logs kept, and who can read them?
11. **Default member role**: per-workspace configurable, or a global default?
12. **Service accounts / API keys / bots**: do non-human principals get roles too? (Likely yes eventually — design the principal abstraction now.)
13. **Role/permission limits**: max roles per workspace, max permissions per role — any caps to prevent abuse/perf blowup?
14. **Migration/seed**: how are built-in roles seeded into existing workspaces when new built-ins ship later?
15. **UI vs API parity**: is everything API-first so the same authorization rules apply to programmatic access?
