---
name: 2026-08-17-spec-expansion-skill-md-escapes-plugin-boundary-with-a-relative-path
description: loom-design/skills/spec-expansion/SKILL.md reaches into loom-code with `../../../loom-code/skills/...`, a filesystem escape across a plugin boundary that the repo's own cross-plugin delegation contract forbids — it resolves today only because both plugins sit in this monorepo
status: open
origin: 2026-08-17 whole-branch review of the loom-design-merge arc (6→2 consolidation), finding 🟡 F4 — surfaced while auditing the reverse-dependency invariant; the reference predates the merge and its depth is still correct, so it was out of that branch's scope
start: the next edit to spec-expansion/SKILL.md's §Adjudication-view section, OR the first report that the adjudication-view pointer fails to resolve on an installed (non-monorepo) host — whichever comes first
---

- Start: the next edit to spec-expansion/SKILL.md's §Adjudication-view section, OR the first report that the adjudication-view pointer fails to resolve on an installed (non-monorepo) host — whichever comes first

- Origin: 2026-08-17 whole-branch review of the loom-design-merge arc (6→2 consolidation), finding 🟡 F4 — surfaced while auditing the reverse-dependency invariant; the reference predates the merge and its depth is still correct, so it was out of that branch's scope

- The defect: `loom-design/skills/spec-expansion/SKILL.md:457` links the
  adjudication-view protocol as
  `../../../loom-code/skills/using-loom-code/protocols/adjudication-view.md`.
  That traverses UP out of the `loom-design` plugin and back DOWN into
  `loom-code` — a filesystem path that only resolves because both plugins
  happen to be checked out as siblings in this monorepo. On a host that
  installed the two plugins from the marketplace, they live in separate
  versioned cache directories and the `../../../` walk lands nowhere.

- Why it is a contract violation, not just a fragile path: this repo's
  CLAUDE.md §"Cross-Plugin Delegation Contract" rule 5 states cross-plugin
  references use the plugin name (`loom-code:using-loom-code`), never a
  filesystem path. Every other cross-plugin pointer in the family already
  follows that form.

- Not fixed in the merge branch on purpose: the reference predates the
  6→2 consolidation and its `../../../` depth is still arithmetically
  correct after the move, so it is neither caused by nor broken by that
  arc. Fixing it means deciding how a SKILL.md should point at another
  plugin's protocol FILE (as opposed to invoking its skill) — the
  delegation contract covers skill invocation, and a bundled-file
  reference across plugins may need its own convention.

- Decision inputs when the arc opens: (i) does any other SKILL.md in the
  family point at another plugin's bundled file, or is this the only one;
  (ii) whether the adjudication-view protocol should be referenced by
  plugin-qualified name, duplicated, or moved to a shared location;
  (iii) whether a mechanical check should reject `../` chains that escape
  a plugin root, since prose review has now missed this one across
  multiple arcs.
