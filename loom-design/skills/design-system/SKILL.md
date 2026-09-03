---
name: design-system
description: |
  Interview the user and write a ratified DESIGN.md visual design system — colors, typography, layout, component tokens. Use for a product with a UI, before or during write-spec; never required — DESIGN.md never blocks a change. Triggers: 視覺設計系統 / 設計語言 / デザインシステム.
version: 1.0.0
---

## What this tool does

Relative paths in this document are relative to this skill's own
directory.

The user names a product with a UI. You run one short interview, write
`DESIGN.md` at the consumer project's root, restate it, and — on "yes" —
write the `ratified-by:` line. `DESIGN.md` documents the product's
**visual system only** — brand, color, type, spacing, elevation, shape,
and component tokens — never flows, screens, or navigation.

## Station summary

| station | artifact | who decides | checker | checkpoint |
|---|---|---|---|---|
| capture-intent | intent — `docs/loom/intent/<change-id>.md`; `PRINCIPLES.md` and `DESIGN.md` at the repo root are side outputs of the tools it calls | user — decision point ① | `intent.schema`, `intent.product-no-identifiers`, `intent.needs-design-reason`, `intent.needs-design-recompute` | N/A |
| write-spec | spec — `docs/loom/<change-id>/spec.md` | user — decision point ②, product only | `intake.confirmed`, `standing.product-principles-reject` | spec lens must pass before a plan exists |
| write-plan | plan — `docs/loom/<change-id>/plan.md` | agent-decided (runs ① itself when loom-design is absent) | `intake.confirmed`, `intake.confirmed-behavior`, `intake.spec-pass`, `intake.after-task-budget` | calls review with scope `spec` |
| build | diff — commits on the change branch, one `Task: <id>` trailer each | agent-decided | none during build; writes the `dispatch[]` the push rules read | wave end when the unreviewed delta exceeds 8 files or 400 lines; immediately after an `after-task` task; ≤5 checkpoints during build, NEEDS_REVISION fix rounds not counted; branch end always |
| review | review — `docs/loom/<change-id>/review.json`, and `docs/loom/<change-id>/blind-run-report.md` from the blind run | two or more fresh-context reviewers; no averaging | `push.verdicts-ge-2`, `push.reviewer-ne-implementer`, `push.dismissed-by-reviewer`, `push.open-findings-closed`, `push.second-vendor-honoured` | `branch-end` always runs |
| ship | diff / PR — the pushed change branch and its pull request | user — decision point ③, reads the blind-run report | `push.review-only-head`, `push.reviewed-sha`, `push.review-schema`, `push.probes-package-tests`, `push.probes-adversarial`, `push.dispatch-covers-tasks`, and every review rule above, re-run at push | before push; a missing `branch-end` pass sends the change back to review |
| maintain | intent — a fresh `docs/loom/intent/<change-id>.md` | agent (dedupe is mechanical) | `intent.schema`, `intent.needs-design-reason`, `intent.needs-design-recompute`, `intent.product-no-identifiers` on a new intent | before hand-off to write-plan |

## Step 0 — Check the contract version

This tool's artifact is defined by `loom-code`'s contract package, so
refuse to run against a version that does not declare it.

Plugins cannot read each other's files, so there is no
`${CLAUDE_PLUGIN_ROOT}` path that reaches `loom-code` from here. Find its
checkout on this host:

| Host | Where `loom-code` lives |
|---|---|
| Claude Code | the plugin cache — `~/.claude/plugins/cache/<marketplace>/loom-code/<version>/`, one directory per installed version; take the newest |
| Codex CLI | the scaffold copy `.codex/hooks/loom_checker.py` inside this repo, written by `loom-code`'s `write-plan` when it first met this repo — use it directly, no `/scripts/` suffix |

Then run, with that directory in place of `<loom-code>`:

```
python3 <loom-code>/scripts/loom_checker.py contract --require 1.0
```

Exit 0: continue. Anything else, the rule is `contract.requires`: print
what the checker printed, tell the user to update `loom-code`, and
**stop**. Do not work around it and do not guess a path.

(Codex form: `python3 .codex/hooks/loom_checker.py contract --require 1.0` —
the scaffold copy is the whole path, so do not append `/scripts/` to it.)

If `.codex/hooks/loom_checker.py` does not exist on Codex, **stop**: run
`loom-code`'s `write-plan` step 0b (the scaffold and its trust probe; that
station writes the procedure out in `codex-first-contact.md` under its own
`references/`, which this plugin cannot read — hand the change over rather
than reproducing it here) first. Do not produce any
artifact without the checker. The file existing is not proof the hook runs:
an untrusted Codex hook is skipped in silence, and step 0b's trust probe is
what tells the two apart.

## Step 1 — When to run

Run this **before or during `write-spec`**, for any product with a UI a
user reads or types into. `DESIGN.md` is **never required**: an absent or
unratified `DESIGN.md` never blocks a change, at any station — unlike
`PRINCIPLES.md`, there is no reject rule for it. Run it on request, or
when `write-spec` surfaces that the UI has no governing visual system yet
and the user wants one before drafting flows.

Read `PRINCIPLES.md` at the consumer project's root first, when present,
as the governing constraint every token must be defensible against. If it
is absent, derive the direction from the user's own words in the interview
below, say explicitly that the mood is derived rather than inherited, and
proceed only on the user's say-so — never invent a constitution to satisfy
this step.

Before inventing any color, type, or component convention not derivable
from `PRINCIPLES.md` or the user's own words, check
`references/knowledge-triage.md` and classify the question first; never
guess a domain-semantic default.

## Step 2 — Interview → DESIGN.md

Ask, in the user's own words:

1. **Brand and mood** — a few adjectives for how the product should feel,
   and one committed visual direction (e.g. "editorial print weekly" /
   "utilitarian terminal").
2. **Palette** — the brand color(s), and whether dark mode matters.
3. **Type** — an existing type choice, or a general character (serif /
   sans / mono, tight / generous).
4. **Density and shape** — compact or spacious, sharp or rounded.

Emit `DESIGN.md` at the consumer project's root (product-level, one per
product — never per-feature), following `references/design-md-schema.md`
for the section shape and content. Its YAML token blocks use the token
groups **`scripts/interface/design_md_spec_keys.py`** freezes as the
schema's source of truth — read `TOKEN_GROUPS` there for the exact set
and do not retype it here; a value in this file that drifts from the
script's is a defect in this file, not the script. Verify WCAG-AA
contrast (body ≥ 4.5:1, large text ≥ 3:1) for every color pairing before
presenting it; a failure is a blocker, not a note.

Then check the file's structure before showing it to anyone, with
`<loom-design>` standing for this plugin's own checkout:

```
python3 <loom-design>/scripts/interface/validate_design_output.py DESIGN.md
```

Exit 0: go to step 3. Non-zero: fix what it names and run it again. Never
read a `DESIGN.md` back to the user that has not exited 0 here — the
restatement is the user's only view of the file, so a structural defect
they cannot see is one they will ratify by accident.

## Step 3 — Restate and ratify

Read the whole file back to the user in plain words — the committed
direction, the palette, the type, the density — not a diff. On a
correction, fix it and read back again. On "yes", write one line at the
top of the file, directly under the title:

```
ratified-by: <name> <date>
```

`<name>` is the user's own name or handle; `<date>` is today,
`YYYY-MM-DD`.

## Step 4 — Commit

```
git add DESIGN.md
git commit -m "docs(loom): DESIGN.md ratified"
```

## Downstream — how the rest of the flow uses it

`write-spec` reads `DESIGN.md`, when present, for its UI-flow vocabulary —
the palette, component, and spacing tokens a flow's screens and states are
described against — so its `UI flows` section names things this file
already named, instead of inventing new visual vocabulary mid-spec. At
`review`, the `design-conformance` dimension scores the diff against
`DESIGN.md`'s tokens; with no `DESIGN.md`, or a finding it cannot speak
to, the dimension is scored **N/A with a one-line reason**, never forced.
A missing or unratified `DESIGN.md` never blocks any station.

<!-- gate: design-system.never-blocks -->
**This tool never rejects a change for lacking a ratified `DESIGN.md`.**
Only `PRINCIPLES.md` carries a reject rule
(`standing.product-principles-reject`); `DESIGN.md`'s absence is at most
a WARN the checker prints, never a gate any station enforces.
