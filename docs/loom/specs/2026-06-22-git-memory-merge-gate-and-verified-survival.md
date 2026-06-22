# Brief — git-memory P1+P2: merge-gate trigger + verified substrate survival

Date: 2026-06-22 · Stage: brainstorming output → `writing-plans`
Target: `dev-workflow:git-memory` (SKILL.md + `protocols/compose-pr.md` + `scripts/memory-grep.sh`)
Source findings: `docs/skill-mining/2026-06-22-git-memory-findings.md` (F1–F4)
Prior art (do not re-litigate): `docs/loom/specs/2026-05-31-git-memory-squash-retrieval-caveat.md`

## Problem (Axis 1 — JTBD)

A future session must be able to reconstruct **why** past work was done by reading the
repo's durable memory substrate. On recent memory-worthy work this **silently failed**:
the decisions were captured in the session and in Claude-native `MEMORY.md`, but **nothing
was written to any git-side carrier** — not per-commit trailers, not the PR `## Memory`
section. The job: **guarantee that when memory is decided, it actually lands in a durable,
retrievable git carrier — and is verified to have landed — before the branch closes.**

**Root-cause correction over the findings doc's first framing.** F1 first read as "squash
drops footer trailers." Live check refutes that: PR #444's squash commit (`5c2d08bb`, repo
setting `squash_merge_commit_message = COMMIT_MESSAGES`) concatenates the 8 branch commits'
messages mid-body — yet `git log --grep` finds **no** `Decision:`/`Learning:`/`Gotcha:`
anywhere, only subject lines. Under COMMIT_MESSAGES, if per-commit trailers existed they
would survive mid-body and `git log --grep` (text match) would find them on main (this is
exactly what the 2026-05-31 prior spec established). They don't — because **they were never
authored to the substrate.** The leak is at **authoring/PR time, not squash time.**

## Users (Axis 2)

- A future developer/agent running `git log --grep='^Decision:'` on **main** to recall "why
  did we X?" — today gets nothing for ~half of memory-worthy PRs.
- The orchestrating agent at branch-close (`finishing-a-development-branch` Phase 3, which
  delegates to git-memory) — currently can finish a branch and open/merge a PR with the
  memory substrate empty and **no signal that it's empty**.

## Smallest End State (Axis 3)

Two coordinated changes to git-memory, no new mechanism, no repo-setting change:

**P1 — extend the gate's trigger surface to include merge.**
- SKILL.md description (`:4`) and §Invocation policy table (`:18-21`): the gate fires
  "before every git commit / `gh pr create` / **`gh pr merge`**". Merge is the last moment
  before memory can be lost; the gate must have a checkpoint there.

**P2 — make substrate survival required + verified for memory-worthy PRs (user chose the
"both carriers" option).** A memory-worthy PR must land memory in **both**:
1. **git-native carrier** — `Decision:`/`Learning:`/`Gotcha:` trailers on the per-commit (or
   branch close-out) commits. Under the current `COMMIT_MESSAGES` squash setting these
   concatenate mid-body of the squash commit and are retrieved on main via
   `git log --grep='^Decision:'` (**text** match — works mid-body; `%(trailers)` footer-parse
   does **not**, and we do not require it). **No repo-setting change needed.**
2. **PR carrier** — the `## Memory` section in the PR body, retrieved via `gh pr view` /
   `memory-grep.sh` (already extracts it).
- **Verify step (the key lever):** after composing, confirm the memory is actually
  retrievable by **both** paths before the branch closes. This is what catches the #444
  failure — where both carriers were silently empty. Add a verify mode to
  `scripts/memory-grep.sh` (e.g. `--verify <ref>` → non-zero exit if a memory-worthy
  ref/PR yields no memory on either path) and reference it from the protocol.
- **`protocols/compose-pr.md`:** `## Memory` becomes **required** for memory-worthy PRs
  (currently "optional / skip if none apply" — that framing stays only for
  non-memory-worthy PRs).
- **SKILL.md Pillar 2 (`:93-98`):** the "two opt-in escape hatches" prose is upgraded — the
  **verification** becomes a required step for memory-worthy PRs; the `PR_BODY` repo setting
  stays genuinely opt-in (only needed for `%(trailers)` footer-parse, which we don't require).

## Current State Evidence

- **Forward (trigger surface)**: `SKILL.md:4` description = "before every git commit / gh pr
  create" — **merge absent**. `SKILL.md:18-21` Invocation-policy table lists commit + pr
  create only.
- **Reverse (SSOT/ownership)**: git-memory is **not** under any `distribute.py` / sync /
  drift-gate (grep of `scripts/` + `dev-workflow/scripts/` for `git-memory` → empty). Edits
  are house-local; no synced-SSOT drift risk. (Confirmed, not inferred.)
- **Error**: `scripts/memory-grep.sh:35-39` exit codes 0 success / 1 usage / 2 not-a-repo /
  3 missing dep — a `--verify` mode should add a distinct non-zero (e.g. 4) for "memory-worthy
  but no memory found."
- **Data (the two carriers)**: `memory-grep.sh:5-14` already extracts **both** commit
  trailers (`git interpret-trailers --parse`) and PR `## Memory` (`gh pr list --json body |
  jq contains "## Memory"`); `standards/memory-conventions.md:178-217` specs the PR section.
- **Boundary**: squash caveat `SKILL.md:77-98`; live repo setting
  `squash_merge_commit_message = COMMIT_MESSAGES`, `squash_merge_commit_title =
  COMMIT_OR_PR_TITLE` (`gh api repos/:owner/:repo`); #444 squash body = 8 subject lines,
  zero trailer bodies.
- **Consumer**: `loom-code/skills/finishing-a-development-branch/SKILL.md:27-40,79` already
  makes git-memory P3-D MANDATORY at branch close and says "PR body uses git-memory's PR-body
  convention" — so tightening git-memory's compose-pr + adding verify is **inherited** by the
  consumer via delegation; a light wiring touch there is an Open Question, not a requirement.

## Decision

Ship P1 (merge in the trigger surface) + P2 (required-and-verified dual-carrier survival for
memory-worthy PRs), as prose/convention + a `--verify` mode on `memory-grep.sh`.

**Primacy (confirmed by the 3-angle confirmation round — see findings §4b):** the dominant
failure is the gate **never firing** at commit/PR/merge (loaded in only ~31% of sessions;
45% of memory-worthy merged PRs ship empty), not firing-then-returning-empty. So **P1 is the
primary lever** (make the gate fire at more checkpoints, incl. merge); **P2/verify is the
deterministic backstop** for the residual fired-but-recorded-nothing cases. The earlier
"squash drops footer trailers" framing is superseded — no repo-setting change is on the
critical path. Rely on
`git log --grep` (text) for the git-native retrieval path on squash `main` — **no repo-setting
change** — consistent with the 2026-05-31 prior spec. The verify step is the load-bearing
piece: it converts "we composed memory" into "memory is provably retrievable," which is the
exact gap that let #444-class PRs ship with an empty substrate.

## Alternatives Considered (Axis 4 — research-grounded, EN + JA)

- **Change `squash_merge_commit_message` → `PR_BODY` so footers parse on main** ([GitHub
  since 2022-08](https://github.blog/changelog/2022-08-23-new-options-for-controlling-the-default-commit-message-when-merging-a-pull-request/)).
  Rejected as a requirement: repo-wide setting affecting all PRs; the recall use case is
  already served by `git log --grep` mid-body under COMMIT_MESSAGES. Stays opt-in (matches
  prior spec's "user's call").
- **Per-PR merge-commit for memory-worthy PRs** — trailers survive verbatim in footer.
  Rejected as default: messier history + per-PR merge-strategy discipline. Stays opt-in.
- **git notes (git-adr)** — survives squash independently. Rejected: not fetched/pushed by
  default, poor GitHub UI, whole new mechanism (over-engineering).
- EN+JA agreement (GitHub Docs "Configuring commit squashing"; m3tech / excite / quartetcom
  JA tech blogs): GitHub has **no** automatic trailer preservation across squash; the only
  knob is the repo-level squash-message setting; footer trailers require PR-body-as-message
  or a real merge. No EN/JA disagreement. This confirms the lever is authoring + verification,
  not a hidden GitHub feature.

## What Becomes Obsolete (Axis 5)

- `protocols/compose-pr.md` "If none apply, skip `## Memory` entirely" (`:38-39`) and the
  "When to skip" section (`:160-168`) — **kept for non-memory-worthy PRs**, but for
  memory-worthy PRs the optional framing is obsoleted → tightened to required. A tightening,
  not a deletion.
- `SKILL.md:93-98` "Two opt-in escape hatches" — the verification within becomes required for
  memory-worthy PRs; the `PR_BODY`/merge-commit settings stay opt-in. Tightening, not removal.
- Nothing is deleted wholesale.

## Out of Scope

- Changing the repo's `squash_merge_commit_message` (not needed; grep retrieval works under
  COMMIT_MESSAGES — prior spec's "user's call" stands).
- Mandating a per-PR merge strategy; git notes.
- git-memory Phase-2 pre-commit validate hook and Phase-3 rebuild pipeline.
- The distill-sessions `/insights` facet gap (F5 — not a git-memory defect).
- Auto-merge (finishing-a-development-branch keeps user agency on the final merge).

## Open Questions

1. **Version bump**: dev-workflow minor (new `--verify` behavior + trigger-surface change) vs
   patch. Lean **minor** (behavior addition).
2. **finishing-a-development-branch wiring**: does P1's merge-trigger + P2's verify need an
   explicit step added to that consumer's Phase 3, or is delegation-inheritance enough? Lean
   inheritance-enough for this change; a one-line cross-ref to the verify step may help.
3. **`--verify` strictness**: should an empty-substrate memory-worthy PR be a hard non-zero
   exit (blocks the close-out flow) or a loud warning? Lean hard exit for the verify command,
   surfaced as a warning the orchestrator can act on (consistent with "no auto-merge / user
   agency").
