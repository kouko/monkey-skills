---
name: product-principles
description: |
  Interview the user and write a ratified PRINCIPLES.md constitution — Who, Non-negotiables, Won't do, Failure we must avoid, Fixed choices. Use when a product change needs principles and the repo has none ratified yet, or when asked what should govern a product/design/engineering trade-off. Triggers: 產品原則 / 設計原則 / 工程原則 / 產品憲章 / プロダクト指針.
version: 1.0.0
---

## What this tool does

Relative paths in this document are relative to this skill's own directory.

The user names a product idea. You run one short interview, write
`PRINCIPLES.md` at the consumer project's root, restate it, and — on
"yes" — write the `ratified-by:` line that makes it the repo's standing
constitution. You never invent a principle the user did not confirm, and
you never ask them to judge anything but their own answers.

Most of the time you are not invoked directly: `capture-intent` (or, when
`loom-design` is absent, `loom-code`'s `write-plan`) runs this same
interview inline, in the same conversation as decision point ①, the first
time a `kind: product` change meets a repo with no ratified
`PRINCIPLES.md`. **The interview is the same one `loom-code`'s
`write-plan` runs when `loom-design` is absent** — this tool exists so a
user can also run it stand-alone, on request, before any change is in
flight.

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

## Step 1 — Run the interview

Read `<loom-code>/contract/templates/PRINCIPLES-interview.md` and ask
exactly its five questions, in the user's own words, until each answer is
clear. One line each on their intent:

1. **Who** it is for, and how they solve this today without it.
2. **The one thing** that cannot be compromised (fast, accurate, cheap,
   private, offline, good-looking) — ranked.
3. **What it explicitly will not do.**
4. **The worst failure**, and who it hurts.
5. **What is already fixed** and cannot change (platform, language, a
   paid service, a data format).

Push until each answer is falsifiable — a later decision can be checked
against it, not just admired.

## Step 2 — Write PRINCIPLES.md

Emit `PRINCIPLES.md` at the consumer project's root (not per-feature),
with exactly these five `##` sections, in this order:

```
# Product principles
## Who
## Non-negotiables (ordered)
## Won't do
## Failure we must avoid
## Fixed choices
```

`## Non-negotiables` is an ordered list of **at least three** entries,
each **falsifiable**: state the choice and a concrete pair that would
tell a stranger it held or broke. For example — good: "offline-first: the
app must complete a save with the network off (bad: 'the app should feel
fast')." A non-negotiable with no such pair is a slogan, not a principle;
push back and ask again rather than write it down.

## Step 3 — Restate and ratify

Read the whole file back to the user in their own words — not a diff, the
actual sections. On a correction, fix it and read back again; there is no
round limit. On "yes", write one line at the top of the file, directly
under the title:

```
ratified-by: <name> <date>
```

`<name>` is the user's own name or handle; `<date>` is today,
`YYYY-MM-DD`. A file with no `ratified-by:` line, or one whose
`## Non-negotiables` has fewer than three entries, is not ratified —
`loom-code`'s checker (`standing.product-principles-reject`) recomputes
both conditions itself and rejects a `kind: product` change against an
unratified file; nothing here can talk it out of that.

## Step 4 — Commit

```
git add PRINCIPLES.md
git commit -m "docs(loom): PRINCIPLES.md ratified"
```

## Downstream — how the rest of the flow uses it

`PRINCIPLES.md` is the standing, always-on constraint every later station
reads: `write-spec` loads it before drafting `Requirements`; a product
change with no ratified copy is refused there
(`standing.product-principles-reject`), never silently allowed through.
At `review`, the `principles-conformance` dimension scores the diff
against these Non-negotiables; when nothing in the file speaks to a given
finding, the dimension is scored **N/A with a one-line reason**, never
forced to a number it cannot support. Engineering-only changes are never
blocked by a missing or unratified file — the reject rule fires only on
`kind: product`.

<!-- gate: product-principles.ratified-requires-user-yes -->
**No `ratified-by:` line is ever written without the user having said
yes to the restatement in Step 3.** Writing it on an assumed confirmation
makes a constitution nobody actually agreed to.
