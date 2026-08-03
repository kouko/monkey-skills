# Brief: one resolver owns review scope, and it refuses a stale base

Date: 2026-08-03
Stage: brainstorming output — input to `writing-plans`

## Problem

When I close out or review a branch, I need the review to cover exactly what
that branch changed. Today the scope is recomputed from scratch at three
stations, each running its own `git diff main...HEAD --name-only`, and none of
them checks whether the branch's merge-base is still current — so a stale base
silently hands every downstream decision the wrong file list.

> When I ask for a review on a branch whose base has drifted, I want the scope
> computation to refuse rather than answer, so I can rebase before four
> reviewer agents spend their round on the wrong diff.

## Users

- **The orchestrating agent running a loom-code review station** — has git, has
  the repo, does not independently notice that a file list is implausible.
  Today it acts on the first list it is given.
- **The reviewer subagents dispatched from that list** — receive the scope as
  fact in their prompt. They cannot detect an over-wide scope; they will review
  whatever they are handed and return a well-formed verdict about it.
- **The human reading the resulting verdict** — sees a PASS or NEEDS_REVISION
  with no signal that the population under review was wrong.

## Smallest End State

One resolver call returns the branch's changed-file list **and** a base-freshness
verdict, and the three stations that currently compute scope call it instead of
running their own `git diff`. When the merge-base is stale, the resolver exits
non-zero with the concrete remedy (the `git rebase --onto` invocation with the
resolved shas filled in) and the station stops before dispatching anything.

Success criteria: (a) a branch whose base predates a squash-merge of its own
content is refused, not reviewed — the 2026-08-03 case; (b) a branch that is
merely behind a main which advanced normally is also refused — the
2026-06-04/05 case; (c) a normal branch on a current base resolves exactly as
today, same file list; (d) exactly one place in the repo computes review scope.

Explicit non-criteria: we will NOT measure how often the refusal fires, and we
will NOT try to auto-rebase on the user's behalf.

## Current State Evidence

- **Forward** — the scope list is the input to a three-way routing decision
  (`loom-code/skills/requesting-code-review/SKILL.md:96`): docs-only delegates
  the whole review, mixed splits per-file, code-only takes the default path. A
  wrong list therefore mis-routes the entire review, not merely its file set.
  Measured 2026-08-03: the true scope was 3 `.md` files; the stale-base
  three-dot diff returned 23 files including 6 non-`.md`, which routes
  docs-only → mixed.
- **Reverse** — three callers compute scope independently:
  `requesting-code-review/SKILL.md:96` (routing) and `:85` (the direct
  "review my branch" entry, same default scope),
  `requesting-docs-review/SKILL.md:53` (recomputes the list to confirm
  docs-only), and `finishing-a-development-branch/SKILL.md:100` reads
  `git diff main...HEAD` for branch state. The first three are decision inputs;
  the fourth is a display read.
- **Error** — no current failure handling: none of the four sites has any
  precondition before the `git diff`. The nearest existing fail-closed
  precedent is `_default_branch_ref`
  (`loom-code/scripts/loom_gate_markers.py:341-348`), which tries
  `origin/HEAD` → `main` → `master` and returns `None` when none resolve;
  callers then omit the dependent fields entirely rather than guess
  (`loom-code/scripts/loom_gate_markers.py:33-41`). The resolver should inherit
  that shape: unresolvable default branch → refuse, never assume fresh.
- **Data** — `compute_patch_id`
  (`loom-code/scripts/loom_gate_markers.py:360-372`) already computes
  `merge-base(default-branch, HEAD)` and records `base_sha` into the gate
  marker. The machinery this brief needs — default-branch resolution and
  merge-base computation — exists, is fail-closed, and is under test; what does
  not exist is any consumer asking whether that base is *current*.
- **Boundary** — `[FRAGILE]` the freshness answer depends on how recently
  `origin/main` was fetched; a check that reads a stale remote-tracking ref
  returns a false all-clear. `[FRAGILE]` `git rev-parse --abbrev-ref HEAD` on a
  detached HEAD and repos with no `origin` are both outside today's happy path.
  No network, DB, or API boundary is crossed unless the resolver is given the
  authority to `git fetch` (Open Question 1).

- **Evidence paths**
  - `loom-code/skills/requesting-code-review/SKILL.md:85`, `:96`
  - `loom-code/skills/requesting-docs-review/SKILL.md:53`
  - `loom-code/skills/finishing-a-development-branch/SKILL.md:100`
  - `loom-code/scripts/loom_gate_markers.py:33-41`, `:341-348`, `:360-372`
  - `~/.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/feedback_verify_branch_base_not_stale_before_finishing.md`
    (the 2026-06-04/05 occurrence and its unapplied prescription)

## Decision

We will add a single scope resolver — one entry point that returns the changed
file list together with a base-freshness verdict — and convert the three
decision-making stations to call it, deleting their own `git diff` invocations
in the same change. The resolver refuses on a stale base with the concrete
`git rebase --onto` remedy rather than returning a list the caller cannot judge.
We will NOT change the three-dot semantics: the research is unambiguous that
three-dot is the correct comparison and the defect is the base, not the dot
count. We will NOT enforce anything at merge or CI time — GitHub's
`required_status_checks.strict` (currently `false` on this repo) and the
CI-side refusal pattern both fire after the wrong review has already run. The
trade-off accepted: a script is roughly an order of magnitude more work than
adding a prose precondition to four files, bought for two properties prose
cannot give — the scope and the check arrive from the same call, so the check
cannot be skipped while still obtaining a scope; and one implementation
replaces three that can drift apart.

## Alternatives Considered

Research was run in English and Japanese, and **they disagree in a way worth
recording: the English sources prescribe discipline, the Japanese source ships
a mechanism.** This repo has already falsified the discipline answer twice.

| Alternative | Who ships it | Why rejected |
|---|---|---|
| "Merge the base branch into your topic branch frequently" | GitHub Docs [EN] | Relies on the human/agent remembering. This is precisely what failed on 2026-06-04/05 and again on 2026-08-03; the prescription has also sat unapplied in this repo's memory for 58 days. |
| Branch protection `required_status_checks.strict` — require branches up to date before merging | GitHub [EN] | Fires at merge time. The wrong review has already run and already minted. Measured: currently `false` on this repo. Worth flipping as a separate, unrelated decision. |
| Refuse to run CI when the branch is older than main | `sue445` [JA] | Right instinct, wrong stage — CI runs after push; the failure happens before push, at scope computation. |
| Prose precondition at each of the four call sites | — | The command is a zero-judgment exit-code check, so prose *could* hold. Rejected on two counts: four copies are four drift surfaces, and prose cannot remove the three redundant computations the user explicitly asked to collapse. |

Sources: [Reviewing a branch: `git diff` wants three dots](https://blog.shukebeta.com/2026/07/02/reviewing-a-branch-git-diff-wants-three-dots-git-log-wants-two) [EN] · [GitHub Docs — About comparing branches in pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-comparing-branches-in-pull-requests) [EN] · [mainブランチよりも古いブランチでCIを実行できなくしたい](https://sue445.hatenablog.com/entry/2023/07/04/144904) [JA] · [Gitでブランチの派生元を間違えたときの解決方法](https://www.granfairs.com/blog/entry-3219/) [JA]

## What Becomes Obsolete

- The three independent `git diff main...HEAD --name-only` invocations at
  `requesting-code-review/SKILL.md:85` and `:96` and
  `requesting-docs-review/SKILL.md:53`. These are replaced, not supplemented —
  leaving any of them alongside the resolver reinstates the drift this change
  exists to remove.
- Nothing else. `finishing-a-development-branch/SKILL.md:100`'s read is for
  display; whether it also routes through the resolver is Open Question 2.

## Resolved Questions

1. **Which `main`, and who fetches it?** — **RESOLVED (user, 2026-08-03): the
   resolver runs the fetch itself.** A local `origin/main` ref is only as fresh
   as the last fetch, so a resolver reading it unfetched can return a false
   all-clear — the worst available failure shape, since it is indistinguishable
   from a genuine pass. The mechanism's entire value is not depending on the
   operator remembering something, and leaving the fetch outside it reinstates
   exactly that dependency. Accepted cost: one network round trip ahead of a
   review. Two sub-decisions this forces, both for `writing-plans` to task
   explicitly rather than leave to the implementer:
   - **Fetch failure (offline, auth prompt, timeout) must fail closed** — the
     resolver cannot vouch for freshness, so it refuses, matching
     `_default_branch_ref`'s omit-rather-than-guess precedent
     (`loom-code/scripts/loom_gate_markers.py:341-348`). Named cost: reviews
     become impossible offline. If that proves intolerable in practice the
     escape hatch is an explicit operator override, not a silent degrade to the
     unfetched ref.
   - **Fetch narrowly** — the default branch ref only, not a full `git fetch`
     that updates every remote branch and tag on an already-slow path.

2. **The resolver may be invoked more than once per close-out, and each
   invocation now costs a fetch** — **RESOLVED (agent, 2026-08-03): the
   delegating station passes its resolved scope down; the delegate resolves
   only when it was not given one.** On a docs-only branch,
   `requesting-code-review` resolves scope to route and then delegates to
   `requesting-docs-review`, whose Step 1 resolves again — two fetches for one
   review once the fetch lives inside the resolver. Pass-down is preferred over
   a cache because **the entry-path distinction it needs already exists in the
   contract**: `requesting-docs-review`'s own trigger table already separates
   "this skill IS that delegated dispatch" (rows at
   `loom-code/skills/requesting-docs-review/SKILL.md:25-26`) from "direct
   invocation" (`loom-code/skills/requesting-docs-review/SKILL.md:27`).
   Pass-down adds a
   payload to a distinction already drawn; a cache would add a store, a key, and
   an invalidation rule — three new failure surfaces, in the same
   `.git/loom/` directory whose statefulness produced this arc's predecessor
   defects. Resolving exactly once per review also keeps the freshness
   guarantee single-valued: two fetches could disagree mid-review.

## Open Questions

1. **Does `finishing-a-development-branch`'s display read also route through
   the resolver?** Consistency argues yes; it is not a decision input, so
   correctness does not require it.
2. **What does the resolver do on a detached HEAD, or a repo with no resolvable
   default branch?** `_default_branch_ref`'s existing answer is to return
   `None` and let callers omit rather than guess; the resolver's equivalent is
   presumably to refuse, but "refuse" on a legitimately unusual repo state is a
   friction cost worth naming before it is built.

## Out of Scope

- Flipping GitHub's `required_status_checks.strict` toggle (a separate,
  one-setting decision, recorded above as measured `false`).
- Any CI-side or merge-time enforcement.
- Changing three-dot to two-dot, or otherwise altering diff semantics.
- Auto-rebasing on the user's behalf.
- The origin-ledger durability question (`.git/loom/` is machine-local) — a
  separate arc, with its own closing window.
- The `plan-format.md` §`Reuse-adequacy` refresh-policy vacuum — measured at one
  occurrence, below this repo's two-occurrence legislation threshold; it belongs
  in a memory entry, not a rule change.

## Design-side on-ramp

Not offered — Axis 0's negative guard fired: this is a defect fix against
existing skills and an existing script, not product-shaped work.
