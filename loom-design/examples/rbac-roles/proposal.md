# RBAC: admin-defined roles & per-workspace permission assignment

**Seed:** "Let an admin define roles and assign permissions to users across
multiple workspaces."

This is the GENERATE-layer draft (spec-expansion → completeness-critic). It is
a high-recall fan-out, not a finished spec. Trust is earned by execution
(loom-code VERIFY), not by this document.

---

## USM backbone

Phase ① artifact — the happy-path spine of ordered user steps.

**Primary actor:** Admin (a user holding an administrative grant).
**Secondary actors:** Member (the user being granted/revoked), Workspace
Owner, System (authorization enforcement point / policy decision point),
Auth provider / IdP (external), Scheduler (for grant expiry), Auditor.

| # | Journey step (Admin's left-to-right spine) | Objects touched | CTA |
|---|--------------------------------------------|-----------------|-----|
| 1 | Admin opens a workspace's access settings | Workspace, Admin | view |
| 2 | Admin defines a Role (name it, describe it) | Role | create |
| 3 | Admin attaches Permissions to the Role | Role, Permission | grant |
| 4 | Admin selects a User (member of the workspace) | User, Membership | select |
| 5 | Admin assigns the Role to the User in this workspace | Assignment, Role, User, Workspace | assign |
| 6 | System evaluates the User's effective permissions in that workspace | Assignment, Permission, Workspace | evaluate |
| 7 | Admin reviews who-has-what (access matrix) | Assignment, Role, User | read |
| 8 | Admin revokes / re-assigns / edits a Role over time | Assignment, Role | update / revoke |

Note: "across multiple workspaces" makes the **scope axis** (workspace) a
first-class dimension on every grant — an assignment is `(user, role,
workspace)`, never `(user, role)` alone. This is the load-bearing seed
entailment.

---

## OOUX object model

Phase ② artifact — object inventory + per-object state machine. Fanned out
per-object (one expansion per object; objects are disjoint).

### Object: Workspace
- **Relationships:** has many Memberships; scopes many Assignments; may belong
  to an Organization (tenant); 1 Owner.
- **CTAs:** create, archive, delete, view.
- **Attributes:** id, name, org_id, owner_id, status, created_at.
- **States:** `active → archived → deleted`. (archived = read-only, grants
  frozen; deleted = tombstoned.)

### Object: User
- **Relationships:** has many Memberships (one per workspace); receives many
  Assignments; authenticated by IdP.
- **CTAs:** invite, activate, deactivate, remove-from-workspace.
- **Attributes:** id, identity (IdP subject), status, is_system_admin.
- **States:** `invited → active → suspended → deactivated`.

### Object: Membership  (User ↔ Workspace join)
- **Relationships:** binds one User to one Workspace; precondition for any
  Assignment in that workspace.
- **CTAs:** add, remove.
- **Attributes:** user_id, workspace_id, joined_at, status.
- **States:** `pending → active → removed`. Removing a Membership MUST cascade
  to (or block on) that user's Assignments in the workspace.

### Object: Role
- **Relationships:** belongs to a Workspace **or** is org/global (template);
  bundles many Permissions; referenced by many Assignments.
- **CTAs:** create, rename, edit-description, edit-permission-set, clone,
  deprecate, delete.
- **Attributes:** id, name (unique within scope), scope (workspace|org|system),
  permission_set, is_system_role (built-in, non-deletable), version.
- **States:** `draft → active → deprecated → deleted`. A Role with live
  Assignments MUST NOT hard-delete (deprecate first; block delete on
  references).

### Object: Permission
- **Relationships:** bundled into Roles; the atomic unit of authorization
  (verb × resource-type, e.g. `invoice:read`).
- **CTAs:** (system-defined catalog) read, list. (Not user-created in v1 —
  see blind spots re: custom permissions.)
- **Attributes:** key, resource_type, action, description, is_dangerous.
- **States:** `available` / `retired` (a permission removed from the catalog
  must not silently keep granting).

### Object: Assignment  (the grant: User × Role × Workspace)
- **Relationships:** the central fact — links User + Role + Workspace; created
  by an Admin (grantor recorded).
- **CTAs:** assign, revoke, view, (optional) set-expiry.
- **Attributes:** user_id, role_id, workspace_id, granted_by, granted_at,
  expires_at?, status.
- **States:** `active → expired` (scheduler) / `active → revoked` (admin).
  Re-assign after revoke = new Assignment, not resurrection (audit trail).

### Object: Admin grant / privilege boundary
- **Relationships:** the meta-permission `role:manage` + `assignment:manage`,
  itself a Permission — admins are made of the same RBAC fabric.
- **States:** held / not-held; **self-scope** (can an admin manage their own
  grants?) is a policy boundary, not a free state.

---

## Path × edge matrix

Phase ③ artifact — cartesian `backbone × object × CTA × state`, pruned through
the lens layer. Illegal cells dropped; system-layer aspects added (the grid
cannot see them).

### Surviving paths — happy + legal transitions (state-transition + CRUD lens)

| # | Path | Lens | Provenance |
|---|------|------|-----------|
| P1 | Admin creates Role in workspace → active | CRUD-C / state | seeded |
| P2 | Admin grants Permissions to Role (edit-permission-set) | CRUD-U | seeded |
| P3 | Admin assigns Role to User in Workspace → Assignment active | state | seeded |
| P4 | System evaluates effective permissions = union of active assignments' role permission-sets, scoped to workspace | eval | inferred |
| P5 | Admin reads access matrix (who-has-what per workspace) | CRUD-R | inferred |
| P6 | Admin revokes Assignment → revoked; effective perms recomputed | state | seeded |
| P7 | Admin renames / edits / clones / deprecates Role | CRUD-U | inferred |
| P8 | Admin deletes Role with zero live Assignments → deleted | CRUD-D | inferred |
| P9 | Assignment hits expires_at → scheduler flips to expired | state | critic-found |
| P10 | Same role assigned to user in workspace A and B independently (multi-workspace scope) | scope | seeded |

### Edges & dropped/illegal cells (BVA / permissions / empty-error-loading / NFR lenses)

| # | Edge case | Lens | Decision | Provenance |
|---|-----------|------|----------|-----------|
| E1 | Assign Role to a User who is **not a Member** of that workspace | state-legality | ILLEGAL — block or auto-require membership | inferred |
| E2 | Delete a Role that still has **live Assignments** | state-legality | BLOCK (deprecate path instead) | inferred |
| E3 | Duplicate Role name within the same scope | BVA / uniqueness | reject with conflict | inferred |
| E4 | Empty permission set on a Role (a role that grants nothing) | empty | allow but warn (legal, low value) | inferred |
| E5 | Role with **all/dangerous** permissions (super-role) | BVA-max / security | allow + flag is_dangerous; may need 2nd approval | critic-found |
| E6 | Assign a Role scoped to workspace A onto workspace B | scope-legality | ILLEGAL — scope mismatch | critic-found |
| E7 | Non-admin (no `role:manage`) attempts any define/assign CTA | permissions | DENY (403), audit the attempt | inferred |
| E8 | Admin escalates own privileges / grants self a higher role | permissions / policy | guarded — separation-of-duty / self-grant policy | critic-found |
| E9 | Last admin in a workspace revokes their own admin grant | BVA / lockout | BLOCK — prevent zero-admin lockout | critic-found |
| E10 | Workspace archived/deleted while Assignments live | cross-object | freeze/cascade assignments; deny new grants | critic-found |
| E11 | User deactivated while holding Assignments | cross-object | suspend effective perms; retain record | critic-found |
| E12 | Two admins assign/revoke the **same** (user,role,workspace) concurrently | concurrency | last-writer or optimistic-lock; no lost-update | critic-found |
| E13 | Permission removed from catalog while bundled in active Roles | cross-object | retire cleanly; deny silently-granting retired perms | critic-found |
| E14 | Effective-permission evaluation under N roles × M workspaces | NFR-perf | bounded latency; deterministic union; cache invalidation on revoke | critic-found |
| E15 | Assignment list empty (new workspace) | empty-state | render empty access matrix, not error | inferred |
| E16 | Authorization check while IdP/identity store unreachable | NFR-network | fail-closed (deny), not fail-open | critic-found |
| E17 | Role permission-set edited → must re-propagate to all live Assignments' effective perms | timing/consistency | propagate atomically or bounded-staleness, documented | critic-found |
| E18 | Conflicting grants (deny-perm in role X, allow same in role Y) | policy | define precedence (deny-overrides? union?) — needs policy | critic-found |

---

## Provenance

Every emitted item tagged `seeded` / `inferred` / `critic-found`.

**seeded** (in or directly entailed by the seed):
- Admin actor; Role object; Permission object; assign CTA; multi-workspace
  scope axis (P10); define-role (P1); grant-permission (P2); assign-to-user
  (P3); revoke (P6).

**inferred** (from OOUX/USM/lens priors, not in seed):
- Membership object & the member-precondition (E1); effective-permission
  evaluation (P4); access-matrix read (P5); Role CRUD lifecycle / clone /
  deprecate (P7, P8); duplicate-name & empty-set edges (E3, E4); non-admin
  deny (E7); empty access matrix (E15); Workspace/User/Assignment state
  machines.

**critic-found** (surfaced by the completeness-critic loop, re-seeded):
- Grant expiry / scheduler (P9, set-expiry CTA); super-role / dangerous-perm
  flag (E5); cross-workspace scope mismatch (E6); self-grant / privilege
  escalation / separation-of-duty (E8); zero-admin lockout (E9); archived
  workspace with live grants (E10); deactivated user with live grants (E11);
  concurrent assign/revoke race (E12); retired-permission cascade (E13);
  evaluation-latency / cache invalidation (E14); fail-closed on IdP outage
  (E16); permission-set edit re-propagation (E17); deny-vs-allow precedence
  (E18).

---

## Blind spots — needs human/field input

The critic's load-bearing output: aspects no generator can manufacture from a
sparse seed. Each names the human/field source that could close it.

- **Permission model semantics — allow-only vs allow+deny.** Does the system
  support explicit *deny* permissions, or allow-only (absence = denied)? E18's
  precedence rule is undefinable until this is fixed. *Needs: product owner /
  security architect decision.*
- **Role inheritance / hierarchy.** Are roles flat, or do they inherit
  (role-of-roles, RBAC1)? Whole subtrees of the object model depend on this.
  *Needs: product/domain decision.*
- **Scope model — is "workspace" the only scope, or is there org/tenant
  nesting and global roles?** Whether a role can be org-wide vs
  workspace-local changes every assignment legality rule. *Needs: domain /
  architecture input.*
- **Custom permissions vs fixed catalog.** Can admins mint new permission
  keys, or only compose from a system catalog? v1 assumed catalog-only.
  *Needs: product scope decision.*
- **Self-grant / separation-of-duty policy (E8).** Is an admin allowed to
  modify their own grants? Is a second approver required for dangerous roles?
  This is an org-governance policy, not a derivable fact. *Needs: security /
  governance / compliance owner.*
- **Real authorization-latency SLA (E14).** "Bounded latency" is a placeholder;
  the actual p99 budget for a permission check is a measured/contracted number.
  *Needs: field measurement + SLA owner.*
- **Audit & retention obligations.** Who-granted-what-to-whom-when retention
  period, immutability, and export format are legal/compliance constraints
  (e.g. SOC2 / ISO 27001 / GDPR access-log duties) not inferable from the seed.
  *Needs: legal / compliance review.*
- **Consistency model for permission propagation (E17).** Atomic vs
  eventually-consistent re-propagation after a role edit is a deliberate
  architecture trade-off with a real staleness budget. *Needs: architecture
  decision + measured budget.*
- **Cross-workspace bulk operations.** "Across multiple workspaces" may imply
  assign-one-role-to-many-workspaces-at-once; the seed does not say whether
  bulk grant/revoke is in scope. *Needs: product clarification with the
  requester.*
- **Regulatory / data-residency constraints per workspace.** If workspaces map
  to tenants in different jurisdictions, access rules may be jurisdiction-bound.
  *Needs: legal review.*

---

**Coverage statement:** coverage relative to seed + 7 lenses (state-transition /
BVA / CRUD / permissions / empty-error-loading / NFR / policy-legal). This is
**not** complete — see Blind spots above for aspects requiring human/field
input that no generator can close.
