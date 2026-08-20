---
name: 2026-08-18-archive-on-close-recovers-bound-folder-by-name-form-key-only
description: finishing-a-development-branch's archive-on-close row recovers a plan's bound change-folder by grepping the name-form join key `<change-id> / Requirement: <name> / Scenario: <name>` only — an id-mode plan citing `<change-id> / REQ-<n> / Scenario: <name>` (or a bare `REQ-<n>`) reads as unbound, so the folder is never archived at close-out
status: open
origin: requirement-identity-hybrid arc, whole-branch docs review (2026-08-18) — surfaced as an out-of-scope observation by both docs-reviewer arms; the file was not in the arc's touch set
start: first arc that consumes an id-mode change-folder (the first real user of `REQ-<n> — <name>` headers), or the next touch of `loom-code/skills/finishing-a-development-branch/SKILL.md` Step 8 — whichever comes first
---

- Where: `loom-code/skills/finishing-a-development-branch/SKILL.md`
  Step 8 "Archive-on-close" row — "Recover bound-ness by grepping the
  branch's plan for change-folder join keys (the `<change-id> /
  Requirement: <name> / Scenario: <name>` pattern …)".
- Fix shape: widen the grep to both key forms plus a bare `REQ-<n>`
  referent that resolves in the bound folder; point at
  `writing-plans/references/plan-format.md` §`Brief item covered` kind
  (d) as the SSOT rather than restating the grammar.
- Related: `2026-08-13-requirement-identity-splits-between-birthplace-and-living-spec`
  (the arc that introduced kind (d)).
