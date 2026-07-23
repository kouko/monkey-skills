---
name: wiki-update
description: One-verb wiki maintenance orchestrator — delegates wiki-ingest → wiki-cross-linker, runs the mechanical fix loop (safe-tier repairs on a proposal branch), triages work orders, reports a structural scorecard. Use for "update my wiki" / 整理 wiki / wiki 維護 / 維護 wiki / ウィキ更新・ウィキメンテナンス. Do NOT use for a single-purpose run — new-note ingest → wiki-ingest; link strengthening → wiki-cross-linker; read-only health check → wiki-lint; near-dup pair merge → wiki-merge; questions → wiki-query; research gap-fill → wiki-auto-research; first-time scaffold → wiki-setup.
---

# Wiki Update — One-Verb Wiki Maintenance

The single verb the user has to remember. Runs the whole maintenance
pipeline: ingest new notes → strengthen links → mechanically fix
lint violations (converge or stop honestly) → triage what the loop
must NOT touch → report a scorecard. All heavy lifting lives in the
member skills and the loop engine; this skill only sequences them.

## Routing

- One-sentence in-session goal with the user present and steering →
  built-in `/goal`. This pipeline (AFK-able artifact maintenance with
  a mechanical oracle) → `wiki-update`.

**When NOT to use:**
- Surgical single-page fix → invoke `wiki-ingest` /
  `wiki-cross-linker` / `wiki-merge` directly.
- Vault not under git → the fix-loop engine refuses to run (its
  proposal-branch exit requires a git repo; there is no unversioned
  in-place editing mode). Fix: `git init` the vault first, or stop
  after steps 1–2.
- repo-wiki / dbt-wiki → their own plugins.

## Pre-flight

1. Read `.obsidian-wiki.config` for `OBSIDIAN_WIKI_VAULT_PATH`
   (vault root; wiki lives at `<vault>/wiki`). Legacy `.env` only →
   instruct the user to run `/wiki-setup` to migrate.
2. Generate the run label ONCE, now, in your session:
   `date +%Y%m%d-%H%M%S` → `runLabel`. The engine is resume-safe and
   never calls `Date.now` — every timestamp/label reaches it via
   `args`, so it must be minted here, before dispatch.

## The 5 Steps

### Step 1 — Ingest new notes (delegate)

Check the configured source folders (wiki-ingest's config) for
new/changed notes. Any found → invoke `obsidian:wiki-ingest` with
full authority (it owns the page-format spec and SHA-256 delta
tracking — never re-implement either here). None → say so and move on.

### Step 2 — Strengthen links (delegate)

Invoke `obsidian:wiki-cross-linker` (its charter: run after each
ingest batch to catch newly-mintable links).

### Step 3 — Mechanical fix loop (Workflow engine)

Run the engine via the Workflow tool with
scriptPath `${CLAUDE_SKILL_DIR}/scripts/wiki_fix_loop.js` and these
args:

| arg | required | value |
|---|---|---|
| `runLabel` | yes | the label minted in pre-flight; `[A-Za-z0-9._-]+` only |
| `vaultDir` | yes | absolute vault path (must be a git repo) |
| `sandboxDir` | yes | absolute writable dir OUTSIDE the vault (e.g. session scratchpad); run artifacts land in `<sandboxDir>/<runLabel>/` |
| `validatorScript` | yes | absolute path to wiki-lint's `wiki_lint_check.py` — resolve `realpath "${CLAUDE_SKILL_DIR}/../wiki-lint/scripts/wiki_lint_check.py"` first; the engine rejects `..` path segments |
| `verdictScript` | yes | absolute path to `${CLAUDE_SKILL_DIR}/scripts/loop_verdict.py` |
| `maxRounds` | no | default 5, bounds [1, 10] |
| `maxDiffLines` | no | default 1500, bounds [100, 10000] |

**Freeze protocol.** Before round 1 the engine snapshots the
violations (`round0.jsonl`) and hashes the check config; any mid-loop
hash change is a hard stop — the loop never chases moving criteria.
Therefore while a run is active: do not edit wiki-lint's check
definitions (`lint-checks.md` / `wiki_lint_check.py`) and do not touch
the vault's `wiki/`. Preflight also refuses a dirty `wiki/` working
tree.

**Proposal exit (operator-facing — read before running).** Every
accepted round is a LOCAL commit on branch `wiki-fix/<runLabel>` in
the VAULT repo; the engine never merges and never pushes. When the
run ends, the vault's HEAD is left ON that proposal branch. The user
must review the diff, then merge or discard it by hand (e.g.
`git merge` from main, or `git checkout main && git branch -D …`)
before the next run — a dirty tree or leftover state makes the next
preflight refuse, and each run needs a fresh `runLabel` anyway.

Terminal states: `CONVERGED` / `PLATEAU` / `STUCK` (writes
`blockers-report.md`) / `BUDGET` / `SIZE_SPLIT` (cumulative diff cap
tripped AFTER the last winning round was committed — nothing is
reverted; the stop asks you to split the REMAINING work into smaller
runs) / `STUCK_EXECUTOR_OVERREACH` (conservation ratchet breach — the
offending round is deliberately left unstaged and uncommitted in the
working tree for inspection; review it, then stash or commit by hand before
the next run's preflight will pass) / `WORK_ORDERS_ONLY` / `MALFORMED` /
`INFRA_ABORT` (a dispatched agent died mid-run — session limit, overload,
or user skip, so `agent()` returned null — and the loop stopped honestly
instead of crashing on a null deref; nothing was committed for the
interrupted round, so just **re-run with a fresh `runLabel`** — the
interruption is usually transient).
Steps 4-5 run after EVERY terminal state — a stopped run still gets
its triage and scorecard; only the wording of step 5's point 3
changes with the stop reason.

**Tuning guide.** The first big cleanup (~1,900 violations measured
2026-07-23) is expected to take MULTIPLE runs — each run is one
reviewable proposal, not a failure. A single dominant class (e.g.
L01 at ~991 pages) may trip the `SIZE_SPLIT` circuit-breaker: that is
design intent (oversized proposals must be split, not reviewed).
Either accept several runs, or raise `maxDiffLines` / `maxRounds`
via args within the bounds above.

### Step 4 — Work-order triage

Read `<sandboxDir>/<runLabel>/work-orders.jsonl` and
`fix-loop-report.md`, and route each finding:

Check-id semantics live in wiki-lint's `references/lint-checks.md`
(SSOT) — the lanes below are keyed by finding TYPE; typical mappings:
L07-unresolvable → page creation, L01/L02/L03-underivable →
re-distillation, L14 → source-link repair.

| Finding | Lane |
|---|---|
| Missing page / broken link needing page creation or re-distillation | wiki-ingest to-do list (present to user) |
| Near-duplicate page candidates | wiki-merge candidates (human picks the pair) |
| LLM-judged concerns (wiki-lint's L05/L06/L08–L13/L15 lane) | note for the next full wiki-lint run |
| Unsafe-only classes (deletion / creation / judgment needed) | stays in `work-orders.jsonl` → human decision |

`PARSE` is the validator's error-lane check_id — a page the
mechanical validator cannot read (non-UTF-8, or frontmatter beyond
its minimal-parser subset), outside lint-checks.md's L-numbered SSOT.
The loop may select the PARSE class like any other; its executor
contract has no safe action for it, so the expected outcome is an
unsafe-only work order (with compare/ratchet brakes as backstop) —
final destination is always this human lane, never an auto-fix.

### Step 5 — Close-out scorecard

Read `<sandboxDir>/<runLabel>/scorecard.json` and report **in the
conversation language**, structural metrics first:

1. Violations base → final (+ delta), rounds run, classes fixed.
2. Diff lines / diff files (the size the reviewer will face).
3. Terminal state + stop reason, work-order classes routed in step 4.
4. Proposal branch name + the merge-or-discard instruction from
   step 3 (the user's next action).

No self-graded quality claims — the numbers come from the scorecard
file, nothing else.
