# Brief: backlog ready verb + close loop + inventory reset

Date: 2026-08-06
Status: FROZEN (user: 「開始吧」 accepting the proposed arc — the arc
runs to a PR; endpoint named via accepted recommendation)
Consumer: writing-plans → SDD; skill-side changes ship as loom-code 0.59.0

## Problem

The backlog store is write-only: 90 live entries in ~5 weeks, zero ever
closed (archive/ does not exist; git history has zero deletions), and
no loom flow ever reads the store. Root causes (measured 2026-08-06,
confirmed by industry survey): (1) no READ moment — retrieval is "a
file someone should remember", never a queryable command (industry: the
tools whose items actually close all expose one — `bd ready`,
`task-master next`, `TaskList`); (2) no CLOSE moment in the work loop —
close is a post-hoc human ritual (industry: effective close is a state
transition inside the same loop that does the work); (3) the pool is
dirty — statuses predate five weeks of shipped arcs (live evidence: a
COMMITTED-NEXT entry whose defect shipped fixed in 0.51.0/PR #648
still reads COMMITTED-NEXT).

Design stance from the survey: ready-set filtering beats total
ordering; the store's shape (one file per entry, frontmatter status,
generated index, never-delete archive) is already industry-standard —
the gap is verbs, not nouns.

## Users

- The user deciding "what next" at arc boundaries (the queue surfaces
  instead of being remembered).
- Orchestrators at arc kickoff (ready query) and close-out (close
  duty).
- Weak-tier agents reading the new prose (probe-gated).

## Smallest End State

Partition A — the READ verb (repo-root script, no plugin version):
1. `scripts/backlog_index.py --ready` prints an actionable shortlist:
   §COMMITTED-NEXT entries first (the "now" queue, file-date order),
   then §OPEN entries each with its one-line `description` and, when
   present, its `start:` line (so the caller judges readiness);
   PARKED/UPSTREAM/SHIPPED/CLOSED/archived excluded; ends with one
   count line ("N committed / M open / K excluded by status"). Exit 0;
   `--ready` composes with `--store` like existing modes. Tests extend
   scripts/test_backlog_index.py RED-first (CI lane confirmed:
   loom-code-ci runs `pytest ... scripts/`).

Partition B — the two moments (loom-code 0.59.0):
2. Arc-kickoff read moment: `brainstorming/SKILL.md` Axis 0 gains one
   short block — before exploring a new arc, run
   `python3 scripts/backlog_index.py --ready` (when the target repo
   has `docs/loom/backlog/`; N/A silently otherwise) and surface to
   the user any COMMITTED-NEXT items plus OPEN items related to the
   seed idea — the queue informs the arc decision, never hijacks it.
   Pin test.
3. Close-out close moment: `finishing-a-development-branch/SKILL.md`
   Step 8 gains an orchestrator-only, once-per-branch bullet — when
   the repo has `docs/loom/backlog/`, check whether THIS branch ships
   or supersedes any backlog entry (grep the store for the branch's
   topic terms; read hits); on a hit, flip the entry's `status:` to
   SHIPPED (or CLOSED — SUPERSEDED) in the same close-out commit,
   regenerate the index (`--write`), and stage both; no hit → skip
   silently (auditable from the diff, same rationale as the
   memory-store bullet). The Step 13 report ends with one line naming
   the top of the remaining COMMITTED-NEXT queue (or "queue empty").
   Pin tests.

Partition C — charter + inventory reset (data, no mechanism):
4. `docs/loom/backlog/README.md` documents the ready verb and the two
   moments (short §Verbs section; pointer-style, no procedure copies).
5. One-time inventory sweep of all 90 entries against the shipped
   record (CHANGELOG entries 0.49.0-0.58.0, merged PRs #645-#655,
   repo state): entries whose subject demonstrably shipped → SHIPPED;
   demonstrably superseded → CLOSED — SUPERSEDED; stale
   COMMITTED-NEXT re-judged; everything without concrete evidence
   stays untouched (conservative — a wrong flip is worse than a stale
   OPEN). Every flip's entry gets one appended line naming the
   evidence (version/PR). Index regenerated; `--validate` exit 0.

Partition D — bump + verification:
6. loom-code → 0.59.0 (manifests + CHANGELOG + version-pin rewrite).
7. Haiku probes: (a) ready-verb output comprehension (given --ready
   output, which item is the default next-arc candidate and why);
   (b) finishing close duty (branch shipped an entry's subject → what
   must happen before the close-out commit); (c) kickoff read moment
   (repo without docs/loom/backlog/ → N/A silently, no invented
   check). Dogfood report under docs/loom/dogfood/.

## Alternatives considered

- Full dependency-DAG ready-set (beads-style `start-after:` machine
  field): deferred — 71 entries carry prose `start:` conditions; the
  survey shows agent-judged readiness over a printed condition is
  sufficient at this scale; upgrade to a machine field only if the
  prose judgment misfires in practice (recorded as a possible future
  entry, not built now).
- Separate ROADMAP.md: rejected — dual-copy drift; the repo already
  has one rotted instance (loom-code/ROADMAP.md, untouched since
  v0.1.0-era; its retirement is OUT of scope here — it belongs to
  loom-code's own doc housekeeping, not this arc).
- Ordinal field on COMMITTED-NEXT: not yet — queue is 3 entries;
  file-date order + ≤5 soft cap documented in the charter suffices
  until the queue actually grows.
- Auto-close on merge (GitHub "Closes #N" analogue): rejected — the
  store is not issue-linked; the finishing bullet is the same loop
  with human-auditable judgment.

## What becomes obsolete

Nothing removed. The write path, statuses, archive script, and
generated index stay as-is.

## Out of scope

- loom-code/ROADMAP.md retirement (separate housekeeping).
- Any ordering field or dependency-graph upgrade.
- Auto-triggering `--ready` from hooks (pull stays pull).
- Backfilling archive/ moves for flipped entries (status flip + index
  is this arc's close semantics; physical archive migration can batch
  later via the existing script).
- Codex-side ports.

## Decisions

- The ready verb lives in backlog_index.py (one store, one script, one
  query surface — industry pattern "write path and read path are the
  same artifact").
- Kickoff read is conditional on `docs/loom/backlog/` existing and
  N/A-silent otherwise (matches the memory-store bullet's auditable
  rationale; brainstorming fires in repos without the store).
- Inventory flips are conservative and evidence-cited in the entry
  body (the store's own honesty convention).
- Counting convention `len(text.split())`; ceilings: brainstorming
  3183 (headroom large), finishing 3923 ≤ 4500.
