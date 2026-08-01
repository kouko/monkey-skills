# Brief — `BACKLOG.md` becomes one entry per file, with a generated index

- **Date**: 2026-08-01
- **Stage**: brainstorming brief (loom-code Stage 1) — input to `writing-plans`
- **Origin**: session of 2026-08-01. The arc began as the declared-vs-actual
  ship arc, pivoted twice, and landed here after two failures in the same
  session were traced to the backlog's shape (see §Problem).

## Problem

`docs/loom/BACKLOG.md` is the SSOT for cross-plugin open items. It is a single
2,545-line / 172 KB file holding 73 entries. It answers **known-item** queries
well (grep a heading you already know) and fails **exploratory** ones (*"what
has already been done in this area?"*) — the reader cannot form the keyword,
so the file is never opened at all.

This is not hypothetical. Twice in one session an agent asserted that work was
un-shipped when the BACKLOG already recorded it as shipped:

1. The `2026-07-27` provenance audit's §8 lists five "未裁決" candidates.
   Candidates 1-4 shipped at loom-code 0.39.0 **the same day**. BACKLOG
   already said so (`- Status: SHIPPED`, and *"the field shipped in loom-code
   0.39.0"*). Two independent agents — the `2026-07-31` backtest author and
   this session's orchestrator — read §8 as live and recommended already-done
   work. n=2 on the same trap.
2. The mixed-branch review split shipped at 0.42.0; a stale `0.41.0` changelog
   line ("*the mixed-branch case is explicitly not addressed here*") was read
   as current.

Both failures share one mechanism: **the living index was correct and was not
read**, because reading it means loading 172 KB to answer a question the
reader cannot pre-name. The information-science name for the missed query
class is *exploratory search* (as opposed to *known-item search*); the
documented remedy is a browsable index, not better keywords.

Three secondary defects compound it:

- **Deletion has stalled.** The header policy is *"Completed items are
  deleted, not archived — git history is the archive."* Deletion did happen
  historically (~15 commits, most recently `2026-07-26`), but **since
  2026-07-26: +19 entries, 0 deletions**. Removing a section from a
  2,545-line file is an invisible diff; the act is too expensive to be
  routine.
- **Entry bloat is invisible.** Median entry is 23 lines; the four largest are
  159 / 144 / 136 / 125 lines and together are 22% of the file. A 159-line
  section inside a 2,545-line file looks like nothing; a 159-line file looks
  wrong.
- **The repo violates its own pattern here.** `plans/` (169), `specs/` (160),
  `memory/` (121), `dogfood/` (51) and `audits/` (14) are all one-thing-per-
  file, retrieved by grep-then-read-hits. `BACKLOG.md` is the only monolith.

## Users

- **kouko** — sole maintainer. Needs to see what is open without scrolling,
  and needs closing an item to be a cheap, visible act.
- **AI agents (Claude Code sessions, subagents)** — the load-bearing reader.
  Context-bounded: cost is per-load, not per-scroll. Agents **do not
  traverse**: this session's own failure was reading an erratum that said
  *"read `docs/loom/BACKLOG.md` before citing this"* and not doing it. Any
  design that depends on the reader following a pointer to a second file is
  already known to fail here.

## Smallest End State

One directory of entry files, an index generated from them, a validator in the
existing CI lane, and archive-on-close. Specifically:

1. `docs/loom/backlog/<slug>.md` — one entry per file, YAML frontmatter
   carrying `name`, `description`, `status`, and (where present today)
   `origin`, `start`.
2. `docs/loom/BACKLOG.md` — stays at its current path, becomes the
   **generated** index, grouped by status. 394 existing references keep
   resolving.
3. A generator + a validator wired into `loom-code-ci.yml`'s existing pytest
   step.
4. Closing an item **moves** it to `docs/loom/backlog/archive/` and stamps
   `status: archived` into the moved file.
5. **`loom-pipeline/skills/loom-memory/SKILL.md:49` is rewritten** — it routes
   backlog-shaped items to `docs/loom/BACKLOG.md`, which after this change is a
   **generated** file. Left unchanged it directs every future agent to
   hand-edit generated output, corrupting the index on first use.

   **Correction (2026-08-02, found by Task 5's spec-reviewer).** This brief
   originally called it *the only* write-instruction in the repo. That was
   **false**: `.claude/hooks/remind-memory-mirror.sh:58` and its `.codex/`
   mirror fire automatically on every project-memory write and instructed the
   same thing — an automated instruction to hand-edit generated output, worse
   than a skill line because no human decides to follow it. Task 5's revision
   repointed both. The false claim traces to a `--include`-restricted grep
   that structurally could not see a `.sh` hook — the exact mistake named in
   §Recorded practice's first entry
   (`migration-acceptance-greps-scope-by-content-not-filetype.md`), quoted in
   this same brief. Citing a practice is not following it. **This forces a `loom-pipeline`
   plugin version bump** (repo rule: a PR changing skill content must bump the
   plugin version) — accepted as a necessary cost; nothing else in this arc
   touches a plugin.

Explicitly NOT in the smallest end state: rewriting any entry's body,
relocating the four oversized entries' content into `audits/`, or
back-porting the generator to the memory store. See §Out of Scope.

## Current State Evidence

- **Forward (who consumes it)** — exactly one skill instructs writing to it:
  `loom-pipeline/skills/loom-memory/SKILL.md:48-49` routes backlog-shaped
  items (*"open item / debt / re-trigger"*) to `docs/loom/BACKLOG.md`. A
  repo-wide grep for `BACKLOG` across `loom-code/`, `loom-pipeline/`,
  `dev-workflow/`, `domain-teams/`, `.claude/`, `AGENTS.md`, `CLAUDE.md`
  returns no other write-instruction; the remaining hits are the English
  common noun (`loom-code/ROADMAP.md:130` "累積 backlog"). One consumer
  outside the repo: the user's global
  `~/.claude/rules/institution-maintenance.md` §1 routes loom-family items
  here and states *"its header defines the entry format"*.
- **Reverse (SSOT ownership)** — the format contract for the analogous store
  lives in `docs/loom/memory/README.md` (§Format — one fact per file, line 54;
  §Index, line 74), and the enforcing script is
  `scripts/check_loom_memory_integrity.py`. That script is **already
  store-generic**: `--store` is a real flag with a default
  (`check_loom_memory_integrity.py:169-171`), verified live by pointing it at
  `docs/loom/audits` and watching it run all four invariants. Its glob is
  `store.glob("*.md")` excluding `README.md`
  (`check_loom_memory_integrity.py:108-109`) — **non-recursive, so an
  `archive/` subdirectory falls outside the invariant set for free**.
- **Error (what happens on malformed input today)** — nothing. `BACKLOG.md`
  has no schema and no validator. By contrast the memory store's four
  invariants are (a) every body file has an index line, (b) every index line
  points to an existing file, (c) filename == frontmatter `name`, (d) index
  description == frontmatter `description`
  (`check_loom_memory_integrity.py:113-125`); exit 0 clean / 1 violation
  (`:35`).
- **Data (the shape of what migrates)** — 73 entries. Field coverage:
  `Status` **72/73** (the sole miss:
  *"operational-kpi full-dimensional-signature slice — follow-ups
  (2026-07-15)"*), `Origin` 62/73, `Start` 54/73, `What` 53/73. Headings
  average 70 chars (min 24, median 68, max 146) and read as descriptions
  already. Status distribution: 55 OPEN / 7 PARKED / 5 SHIPPED / 2 UPSTREAM /
  1 COMMITTED-NEXT. Migration is therefore mostly mechanical; human judgment
  is needed for one missing status and for the handful of headings too short
  to serve as a `description`.
- **Boundary (edges and blast radius)** — 394 mentions of `BACKLOG` across 142
  files; keeping the index at `docs/loom/BACKLOG.md` preserves all path-level
  references. `loom-code-ci.yml:98` runs
  `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -v`, and its
  `paths:` filter already includes `scripts/**` and `docs/loom/**`
  (`:28,44,62,63,68`) — a new test under `scripts/` gates with no CI change.
  `check_doc_citations.py` runs per-file and currently reports
  `checked 52 / unchecked 17 / findings 0` on `BACKLOG.md`; per-entry files
  keep that coverage.

Evidence paths: `docs/loom/BACKLOG.md`,
`scripts/check_loom_memory_integrity.py`, `docs/loom/memory/README.md`,
`loom-code/scripts/archive_change_folder.py`,
`loom-pipeline/skills/loom-memory/SKILL.md`,
`.github/workflows/loom-code-ci.yml`,
`docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md`,
`docs/loom/audits/2026-07-31-a-class-interceptability-backtest.md`.

## Decision

Split `BACKLOG.md` into one file per entry under `docs/loom/backlog/`, with a
**generated** index at the existing `docs/loom/BACKLOG.md` path, a
frontmatter validator in the existing CI lane, and **archive-on-close
replacing delete-on-close**.

Four design decisions, each with an external precedent:

1. **Generate the index; never hand-maintain it.** Python's PEP 0 is built
   in-memory at Sphinx build time and explicitly not committed; Rust's book
   TOC is regenerated by `generate-book.py` scanning `text/`; Ethereum's EIP
   index is built by Jekyll from front matter; Kubernetes keeps no committed
   master catalog. **Four of five surveyed governance systems never commit an
   index**; the one that hand-maintains a table (TC39) is also the only one
   with no per-item files. This repo's own counter-example is decisive: the
   memory store's index IS hand-written, it drifted (`79de4f69`,
   `46dcb51f`), and the response was three successive detection layers
   (checker `#596` → finishing-step checkpoint `#635` → PostToolUse hook
   `#636`) in nine days — while loom-code 0.39.0's own shipped doctrine says
   a pointer *"makes the copy **unnecessary** rather than adding a detection
   step."*
   **Sub-decision: generate AND commit, with CI verifying no drift** (rather
   than PEP's build-time-only form). Our reader is an agent that greps files,
   not a website; a committed index is directly readable. CI verification
   demotes "hand-editable" to "hand-edit gets blocked."
2. **Status as a typed frontmatter field with a closed enum, validated by a
   small script in the existing verify path.** Python's `check-peps.py` hard-
   codes `ALL_STATUSES = frozenset({...})` and runs as a pre-commit hook;
   Kubernetes' `kep.yaml` carries a typed `status` plus `replaces`/`see-also`,
   checked by `hack/verify-kep-metadata.sh` inside the standard `hack/
   verify.sh` suite. Adopt the existing vocabulary already in the header:
   `COMMITTED-NEXT | OPEN | PARKED | UPSTREAM | SHIPPED | CLOSED — SUPERSEDED`
   (+ `archived` for moved entries).
3. **Lenient on untouched entries; hard-gate only the field being changed.**
   Ethereum's `eipw` (EIP-7199): *"Lint errors for untouched lines are
   considered ignorable ... unless it's changing the Status of the EIP."* This
   is what keeps a 73-entry migration from having to be perfect on day one.
4. **Archive on close, do not delete.** No surveyed system deletes; the one
   built for pruning (OpenSpec) archives — *"moves the change folder to
   `openspec/changes/archive/YYYY-MM-DD-<n>/`"*. This repo already implements
   that pattern in `loom-code/scripts/archive_change_folder.py`, which moves
   `docs/loom/<change-id>/` → `docs/loom/archive/<date>-<change-id>/` **and
   stamps `status: archived` into the moved file's frontmatter**, with
   path-safety refusals, an idempotency guard, a no-clobber guard, and
   rollback if the stamp fails. The stamp is the load-bearing half: an
   archived entry is **self-describing**, so an agent that greps into it
   learns it is closed without traversing anywhere. Deleting removes the only
   answer to *"has this been done?"* that does not require `git log` — and
   this session is the evidence that agents do not run that query.

## Decision — entry filenames (settled 2026-08-01, user call)

**Entry filenames carry a creation-date prefix: `docs/loom/backlog/YYYY-MM-DD-<slug>.md`.**
The date is assigned **once, at creation, and never changes** — archiving
moves the file and does not rename it.

Why this shape, and why the date must not be added at archive time:

- **Repo consistency**: `plans/` 169/169, `specs/` 160/161, `audits/` 14/14,
  `dogfood/` 17/17, `research/` 14/14 already use a creation-date prefix —
  374 of 375 files. Only `memory/` (0/121) does not, because a memory is a
  timeless fact retrieved by topic. The date prefix is also the ISO 8601
  convention endorsed by ISO, NASA, the Library of Congress, Stanford
  Libraries and the UK National Archives; its property is that lexical sort
  equals chronological sort.
- **Diagnostic value**: with a creation date in the name, a listing shows how
  long an entry has sat open. That matters here — measured close rate
  (~0.9/day) is under a third of the open rate (~2.7/day), so age is exactly
  the signal this store should surface.
- **A filename change breaks references.** The Zettelkasten convention states
  the constraint precisely: *"When using descriptive filenames instead of
  identifiers, filenames should be unique and immutable: a title cannot be
  changed without changing each reference to the note with that title."*
  The closest industry analogue agrees in practice — Backlog.md's
  `backlog/completed/` keeps the active-task filename verbatim
  (`back-100 - Add-embedded-web-server-to-Backlog-CLI.md`), no rename, no
  date added on completion.
- **Observed locally, in this repo**: the one existing archived change-folder
  is `docs/loom/archive/2026-07-18-2026-07-16-operational-kpi-quarterly/` — a
  **double date**, because `archive_change_folder.py` prefixes the archive
  date onto a name that already carried its creation date.
  `docs/loom/backlog/2026-07-17-investing-toolkit-quarterly-parked-capability-arcs.md`
  now cites that archive-date-bearing path, so the reference is pinned to
  when it was archived rather than to what it is.

**Consequence for the archive step**: generalizing
`archive_change_folder.py` must make the date-prefix behaviour **optional and
off for backlog entries** — the folder-unit caller keeps it (its change-folder
names can collide); the file-unit caller must not inherit it.

**Consequence for the frontmatter contract**: the frontmatter `name` is the
**full filename stem including the date** (`2026-08-01-<slug>`), so invariant
(c) *filename == frontmatter `name`* is reused verbatim with no change to
`check_loom_memory_integrity.py`'s logic. There is deliberately **no separate
`created:` field** — that would restate in frontmatter a fact the filename
already carries, which is the copy-that-drifts shape loom-code 0.39.0's
pointer-not-copy rule exists to prevent.

## Alternatives Considered

Researched live (EN + JA, four dispatched rounds; sources in the session
transcript).

- **Keep the monolith, add a generated TOC + an entry-size cap.** Solves the
  exploratory-search failure only. Leaves deletion expensive and entry bloat
  invisible, and adds a second generated artifact to keep honest. Rejected as
  strictly dominated once the split is affordable.
- **Move to GitHub Issues** — what **0 of 9** surveyed coding-agent/skill
  projects keep a tracked backlog file, and all route to Issues instead.
  Rejected: the documented cost is loss of git-diffability, greppability and
  PR-review — and Issues are not readable by the agents that are this file's
  primary consumers. The header's stated rationale (*"versioned,
  host-agnostic, greppable"*) already made this call.
- **Per-item files rejected outright** — the honest counter-evidence:
  `git-bug` (9,960★) explicitly stores issues as *"objects in a git
  repository — **not files!**"*, Fossil deliberately keeps tickets out of the
  source tree (*"we do not want ticket files cluttering the source tree"*),
  and three general-purpose file-based trackers are dead (ditz 2011,
  bugs-everywhere 2016, sit 2018). All of these address **externally-filed
  user bugs** needing merge-conflict resolution and non-developer access —
  neither applies here. The two implementations built for *our* case are both
  new and thriving: **Backlog.md** (6,339★, pushed 2026-07-30 — one `.md` +
  YAML frontmatter per task, explicitly for human+AI collaboration) and
  **mattpocock/skills `issue-tracker-local`** (host repo 198,348★, pushed
  2026-07-31 — one file per ticket plus a map file agents scan).
- **Delete-on-close (status quo).** Kept as a live option until the archive
  evidence landed; rejected per Decision 4.

**The one transferable failure mode** is recorded against mattpocock's design
(issue #203): *"without a CLI, every agent has to rediscover the issue folder
structure, parse Markdown front matter ad hoc, decide how to filter files, and
avoid accidentally corrupting metadata."* Its resolution was to add a thin
access layer, **not** to revert to a single file. Our equivalent access layer
is the charter + generated index + validator — all three must ship together or
this defect is inherited.

## What Becomes Obsolete

- The hand-maintained `BACKLOG.md` body (becomes generated output).
- The header's *"Completed items are deleted, not archived"* sentence
  (replaced by the archive rule) — must be rewritten in the same change, not
  left contradicting the new behaviour.
- `loom-pipeline/skills/loom-memory/SKILL.md:49`'s instruction to route items
  to `docs/loom/BACKLOG.md` (becomes: create an entry file).
- Nothing else. The memory store's hand-written index is a **separate**
  obsolescence candidate and is deliberately deferred (§Out of Scope).

## Out of Scope

- Rewriting entry bodies, or relocating the four oversized entries'
  (159/144/136/125-line) content into `audits/`. A second arc.
- Back-porting the index generator to `docs/loom/memory/` — desirable on the
  same argument, but it would double this arc's blast radius and touches a
  store guarded by a hook and a CI step.
- Updating the user's global `~/.claude/rules/institution-maintenance.md` §1
  path reference. Out of repo; its own edit-tier rules apply (a rules-file
  change must be shown to the user as a diff first). **This is the one
  deferral that knowingly leaves incorrect text in place** — after this arc
  §1's *"its header defines the entry format"* is false, because the format
  contract moves to the store charter. Track it as a REQUIRED post-merge
  follow-up, not an optional one.
- Any change to what an entry *means* or to the `Start` / re-trigger
  convention.

## Recorded practice this arc must obey

A `loom-memory` recall was re-run when the session pivoted to this task (the
earlier recall was scoped to the ship arc and did not reach these). Each rule
below is quoted from `docs/loom/memory/`; all named artifacts were verified
present on disk.

- **Acceptance greps scope by content, not filetype.**
  *"when a task renames or deletes a path/name, write the acceptance grep over
  the whole repo by content pattern (no `--include` file-type filter), then
  justify every residual hit as an explicit carve-out."*
  (`migration-acceptance-greps-scope-by-content-not-filetype.md`) — the 394
  `BACKLOG` mentions must be swept without an `--include` filter; `.py`,
  `.yml` and schema-doc consumers are otherwise invisible.
- **Relocation creates git state that `git diff` cannot show.**
  *"before committing run `git status --short` and pair every `D` (staged
  deletion) with its intended replacement. `git add` the replacement **by
  name** (never `git add -A` in this repo)... If a `D` has no matching
  `R`/`A`, the replacement is still untracked."*
  (`untracked-replacement-while-deletion-staged.md`); and after `git mv` of a
  directory, *"inspect `git diff --cached --name-status`: keep `R`/`M`
  entries, and unstage the `A` entries"* (`git-mv-sweeps-untracked-files.md`).
- **Certify the validator against the real corpus, not fixtures.**
  *"sweep it across the ENTIRE real corpus before trusting a single rate...
  treat the format doc as aspiration and the corpus as truth."*
  (`schema-shaped-fixtures-certify-the-rule-not-the-parser.md`) — this arc's
  direct predecessor made exactly this mistake; the 73 real entries are the
  corpus, not a hand-built sample.
- **A batch edit that no-ops reports success.**
  *"After any batch edit, grep for what should now be *absent*; 'applied' is
  not evidence, absence is."*
  (`a-silently-skipped-edit-reports-as-a-completed-one.md`)
- **Generalizing the archive script is a shared-helper decision, not a
  signature question.** *"before routing a second caller through a shared
  helper, ask what the helper's failure mode MEANS in the new lane, not
  whether its signature fits."*
  (`a-shared-helper-can-be-right-in-one-lane-and-destructive-in-another.md`)
  — bears directly on Open Question 1. And if folder-unit tests are retired,
  *"a test that tests a PROPERTY that moved to a new home... must be rewritten
  against the new home in the SAME task, not dropped"*
  (`retiring-a-mechanism-must-move-its-tests.md`).
- **Prose keeps the why; a deterministic carrier keeps the enforcement.**
  *"every consequence gets a deterministic carrier — validator check, critic
  literal pre-check, CI grep... prose keeps the why, never the enforcement."*
  (`prose-only-enforcement-dies-on-weak-executors.md`) — the validator is that
  carrier; the charter must not be the enforcement.
- **Pin the frontmatter schema wording once and transcribe from the pin.**
  *"add a §Pinned `<name>` block to the plan's `## Notes`, make each consuming
  task's Description say 'transcribe VERBATIM from the pin'."*
  (`pin-shared-wording-in-plan-copies-transcribe-from-pin.md`)
- **Assertions must encode the property they claim.** *"read its
  docstring/name as a claim, then ask 'would this assertion FAIL if that exact
  property were violated?' Relational claims... need relational predicates."*
  (`assertion-must-encode-the-property-it-claims.md`) — the byte-identical
  description invariant is relational; a membership-only check does not pin
  it.

**One recall gap, stated honestly**: no memory entry describes a
status-field-driven lifecycle/archive scheme for documents. The store's own
charter says *"Stale facts are deleted, not archived — git history is the
archive."* That is the memory store's convention, not a ruling on this arc,
but Decision 4 moves the backlog in the opposite direction — the two stores
will differ deliberately, and the charter's sentence must not be read as
governing `docs/loom/backlog/`.

## Decision — index shape and validation tiers (settled 2026-08-01, user call)

**Archived entries appear in the generated index in COMPACTED form** — live
entries listed in full, archived entries in a separate trailing section, one
line each (name + archive date).

Evidence: of the three systems checked, **none mixes settled items into the
live listing**. Python's PEP 0 keeps everything in one index but partitions it
by status (*"Open PEPs (under consideration)"* / *"Finished PEPs (done, with a
stable interface)"* / *"Rejected, Superseded, and Withdrawn PEPs"*); TC39 moves
them to separate files (*"This list contains only stage 2 proposals and higher
that have not yet been withdrawn/rejected, or become finished"*); Backlog.md
separates by directory (`backlog/tasks/`, `backlog/completed/`,
`backlog/archive/{tasks,drafts,milestones}/`, whose readme describes archive as
a *"soft delete"*). They differ only in whether the settled view is a section,
a file, or a directory.

Sizing (measured on this repo, `docs/loom/BACKLOG.md` full history): close rate
**~0.9/day** (18 deletion events, 20 entries, 2026-07-03 → 2026-07-26) against
open rate **~2.7/day** (+46 entries, 2026-07-15 → 2026-08-01). One-year
extrapolation: archive ≈ 300, live ≈ 730. A compact archive section stays
tolerable; the real growth risk is the LIVE set (see Open Question 3).

**Validation is two-tier** (archived entries ARE validated — user call):

| | live entries | archived entries |
|---|---|---|
| filename == frontmatter `name` | ✅ | ✅ |
| `status` in the closed enum | ✅ (live values) | ✅ (must be `archived`) |
| has an index line | ✅ full | ✅ compact line |
| index description == frontmatter description | ✅ | — (compact line carries no description) |

Note the existing checker globs `store.glob("*.md")` **non-recursively**
(`check_loom_memory_integrity.py:108`), so reaching `archive/` requires a code
change, not a config change.

## Open Questions

1. **One archive script, not two — generalize `archive_change_folder.py`.**
   (Settled 2026-08-01.) The five path-safety guards (symlink refusal,
   idempotency, no-clobber, path-segment validation, rollback-on-stamp-failure)
   must not exist in two copies — CLAUDE.md forbids copied gate logic.
   **Binding sequence**: first add tests pinning the CURRENT folder-unit
   behaviour, then generalize. Per
   `retiring-a-mechanism-must-move-its-tests.md`, any folder-unit test retired
   must have its property rewritten against the new home **in the same task**.
   The date-prefix behaviour becomes a parameter, **off for the file-unit
   (backlog) caller** — see §Decision — entry filenames.
2. **The index generator lives in top-level `scripts/`.** (Settled
   2026-08-01.) It sits beside its closest sibling
   (`check_loom_memory_integrity.py`), and top-level `scripts/` belongs to no
   plugin, so it needs no version bump. Both locations are collected by the
   same CI step (`loom-code-ci.yml:98`). Note this arc already bumps
   `loom-pipeline` for the SKILL.md rewrite; keeping the generator top-level
   avoids a second bump.
3. **Still open — the one entry with no `Status`**:
   *"operational-kpi full-dimensional-signature slice — follow-ups
   (2026-07-15)"*. Needs a human call at migration time; the implementer must
   surface the entry's text and ask rather than guess a status.
4. **Still open, deliberately out of scope — the live set outgrows the
   archive.** At the measured rates the live set reaches ~730 entries in a
   year. Splitting the file does not fix a close rate under a third of the
   open rate; that is a process question, not a storage one. Recorded here so
   it is not mistaken for something this arc solved.
