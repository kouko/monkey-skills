# Brief: loom memory hardening — implement O4 → O2 → O3 → O5 → O6

**Date:** 2026-07-17 · **Upstream artifact (approach SSOT):**
`docs/loom/research/2026-07-16-loom-memory-hardening-research.md` (merged #575;
option order user-ratified). Evidence base:
`docs/loom/research/2026-07-16-git-based-memory-viewpoints-and-comparison.md`.
**Mode:** continuous (user /goal directive: implement in the recommended order;
PR-open is the terminal stop, never auto-merge).

## Design-side on-ramp

N/A — process/tooling hardening on existing mechanisms (Axis 0 negative guard:
not product-shaped; silent skip).

## Problem

When a durable lesson is recorded at branch close-out, it must remain
retrievable later **regardless of merge mechanics or who merges**. PR #574
proved the current design fails this: the pre-push `--verify` gate passed, the
squash transform ran later, and the commit-trailer carrier landed
un-retrievable (`memory-grep --verify HEAD` → exit 4) — the second recurrence
of the same gotcha. The lesson survived only because the
`docs/loom/memory/` file store carried it. Additionally, the doctrine is
internally contradictory: git-memory's SKILL.md claims git artifacts are "the
durable substrate" and blesses `git log --grep` retrieval, while the store
charter claims the file store is the durable truth — and the deep-dive
evidence (CommitDistill arXiv:2605.18284: `git log --grep` retrieval 0.083 vs
distilled-file layer 0.750) says the charter is right.

## Users

- **Future Claude/Codex sessions** (any tier, incl. headless) doing loom work
  in this repo — they recall lessons via pull-based grep and must not lean on
  a measurably-weak retrieval path.
- **kouko** merging PRs by hand in the GitHub UI — a human merge must not be
  able to silently drop a memory carrier (今回の #574 は Claude 側 pre-push
  gate では防げなかった).
- **The close-out flow itself** (`finishing-a-development-branch` Step 9b) —
  its `--verify` gate needs a post-squash CI counterpart.

## Smallest End State

Five options, one branch, sequential atomic tasks in the ratified order, one
PR. Each option's minimum:

1. **O4 — carrier doctrine fix (wording, 2 files + sweep).**
   `dev-workflow/skills/git-memory/SKILL.md` re-states the hierarchy: the
   repo's committed file store (where one exists, e.g. `docs/loom/memory/`)
   is the **authoritative durable-lesson carrier**; commit trailers are
   **commit-bound decision capture, best-effort/secondary** — never the path
   you depend on to recover a durable lesson (evidence: 0.083). The charter
   (`docs/loom/memory/README.md`) jurisdiction row gains the same one-line
   hierarchy note. Plugin-wide grep sweep for "durable substrate" /
   "supported path" claims that contradict this (per
   `core-rule-removal-needs-plugin-wide-sweep` memory).
2. **O2 — mechanize the raw trailer footer (compose-pr.md).**
   For memory-worthy PRs, the PR body MUST end with a blank-line-separated
   **raw trailer block** (`Decision:` / `Learning:` / `Gotcha:`, unbolded) as
   the **absolute last block — after even the `🤖 Generated with` footer**
   (live-found #575: any non-trailer line after it empties `%(trailers)`).
   The existing opt-in hatch (`SKILL.md:123-130`) becomes a pointer to the
   compose-pr mandate.
3. **O3 — post-merge CI + wire the orphan tests.**
   New `.github/workflows/dev-workflow-ci.yml`:
   (a) PR+push job running the three existing
   `dev-workflow/tests/test-memory-grep-*.sh` (currently run by NO workflow);
   (b) push-to-main job: if HEAD commit body contains the `## Memory` heading
   (deterministic memory-worthiness signal under PR_BODY squash mode) then
   `memory-grep.sh --verify HEAD` must exit 0, else the workflow fails.
4. **O5 — parser-strict verification + retrieval guidance.**
   `memory-grep.sh` gains `--verify-strict <ref>`: same as `--verify` but the
   keys must be **parseable by `git interpret-trailers --parse`** (catches the
   #575 refinement where text-grep passes but `%(trailers)` is empty). Keep
   `--verify` semantics untouched (mid-body grep survival is deliberate;
   exit codes 0/1/2/4 are test-pinned). SKILL.md's recall table stops
   recommending bare `git log --grep` as a durable path (aligns with O4).
5. **O6 — staleness/supersede at the file store.**
   `loom-pipeline/skills/loom-memory/SKILL.md` record verb gains a mandatory
   contradiction check: before writing, grep the store for entries the new
   fact contradicts; on a hit, update/replace that entry (delete + rewrite,
   charter policy: git history is the archive) instead of adding a
   contradicting sibling — mirroring git-memory's backward-pointing
   `Supersedes:` doctrine. Charter §record guidance gains the matching
   one-liner. No new frontmatter field, no validator infra (O7 watch-the-
   threshold applies).

## Current State Evidence

- **Forward** (how a lesson flows today): finishing Step 6 invokes git-memory
  (`loom-code/skills/finishing-a-development-branch/SKILL.md:132-141`);
  compose-pr inserts `## Memory` after `## Test plan`, **before** the `🤖`
  footer (`dev-workflow/skills/git-memory/protocols/compose-pr.md:90-101`);
  Step 9b runs `--verify HEAD` pre-push, exit 4 = STOP
  (`finishing-a-development-branch/SKILL.md:197-210`).
- **Reverse** (SSOT ownership/direction):
  `dev-workflow/skills/git-memory/standards/memory-conventions.md` owns the
  trailer format ("use git's own trailer parser — do not invent a custom
  delimiter", `:299-321`); `docs/loom/memory/README.md:13-18` owns the
  jurisdiction table; `loom-pipeline/skills/loom-memory/SKILL.md:33-41`
  points-never-copies at the charter. Contradiction to fix: git-memory
  `SKILL.md:9-10` ("commit messages / PR body as the durable substrate") and
  `:91-98` (`git log --grep` = supported main-retrieval) vs charter
  `README.md:8-9` ("this folder is the durable truth").
- **Error** (failure paths): exit codes 0/1/2/3/4 at
  `dev-workflow/skills/git-memory/scripts/memory-grep.sh:36-42`; `--verify`
  is a plain text grep over `%B` (`:181-187`) — passes even when
  `%(trailers)` parses empty (the #575 refinement); verify keys exclude
  `Related:` (`:62-63`). Incident: #574 squash → exit 4 (pre-push gate blind
  to the squash transform).
- **Data** (formats): trailer schema + `Supersedes:` backward-pointing,
  liveness computed-never-stored
  (`memory-conventions.md:16-17, 23-49, 344-350`); supersession index built
  via interpret-trailers (`memory-grep.sh:324-386`); store file format =
  frontmatter name/description/type/origin (`docs/loom/memory/README.md:39-57`).
- **Boundary** (CI/cross-plugin edges): NO dev-workflow CI exists; the three
  `dev-workflow/tests/test-memory-grep-*.sh` run in no workflow (gap);
  push+PR-to-main workflow pattern to copy:
  `.github/workflows/loom-siblings-ci.yml:52-64` (checkout → setup-python
  3.11 → pip install pytest → pytest) and `loom-pipeline-ci.yml:25-36`;
  loom-code CI pins the charter's §When to record via
  `loom-code/scripts/test_loom_memory_timing_convention.py:28-43` — O4/O6
  charter edits must not break those pins; repo squash mode already
  `PR_BODY` (`docs/loom/memory/github-squash-merge-single-commit-drops-body.md`
  §Status).

## Decision

Build: the five options above, one branch
(`feat/loom-memory-hardening-o4-o2-o3-o5-o6`), sequential SDD tasks in order
O4 → O2 → O3 → O5 → O6, single PR, PR-open = terminal stop. dev-workflow
plugin bumps 2.21.0 → 2.22.0 (skill content changed); loom-pipeline bumps
0.7.1 → 0.7.2 (loom-memory skill changed). NOT building: any vector/graph/DB
memory substrate, O7 team-scale validators (watch-the-threshold), rebase-merge
policy changes, changes to `--verify`'s existing exit-code contract, or a new
frontmatter schema for the store.

**Pinned shared wording** (per `pin-shared-wording-in-plan-copies-transcribe-
from-pin`): the carrier-hierarchy sentence to transcribe VERBATIM wherever it
ships (git-memory SKILL.md, charter README):

> Durable lessons live in the repo's committed memory store
> (`docs/loom/memory/` here) — the authoritative carrier. Commit trailers are
> commit-bound capture: best-effort, secondary, and never the retrieval path
> a durable lesson depends on.

## Out of Scope

- O7 (team-scale graduation: CI-enforced schema/status on the store) — watch
  the threshold, don't pre-build.
- Migrating existing trailer-recorded decisions into the file store.
- Changing `finishing-a-development-branch` Step 9b semantics (stays the
  pre-push gate; O3 adds the post-squash net, O5's strict mode is additive).
- loom-code SDD / writing-plans skills (#559 frozen) — untouched.
- The parked calibration-B brief and all pre-existing untracked debris.

## Alternatives Considered

Axis-4 research already done and adversarially verified (24/25 claims) in the
upstream research doc — EN+JA, 6 angles, 17 sources. Key rejected
alternatives recorded there: rebase-merge-only policy (rejected: repo-wide
merge-mode change for a memory concern), vector/graph memory substrate
(rejected: file store + pull already matches/leads field consensus for this
repo's scale), commit-trailer-as-primary (refuted by CommitDistill 0.083).

## What Becomes Obsolete

- git-memory SKILL.md's "git artifacts are THE durable substrate" doctrine and
  the `git log --grep`-as-supported-path recall guidance (`SKILL.md:9-10,
  91-98`) — replaced by the carrier hierarchy (O4/O5), removed in the same PR.
- The opt-in framing of the raw-footer hatch (`SKILL.md:123-130`) — becomes
  the compose-pr mandate pointer (O2).
- The "manual post-merge `--verify` habit as the only post-squash net" —
  CI takes the duty (O3); the habit remains as documented fallback for
  human-merge-without-CI contexts.

## Open Questions

None blocking. Two plan-level notes: (a) O3's workflow must not name-collide
with branch-protection-pinned job display names (see
`feedback_branch_protection_pins_ci_job_display_names`) — new job names are
additive, no renames; (b) new grep-pin tests for compose-pr.md / SKILL.md
wording must scope to a measured neighborhood and go RED first
(`grep-tests-scope-to-measured-neighborhood`).
