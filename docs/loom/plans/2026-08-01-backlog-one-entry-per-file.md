# Plan: `BACKLOG.md` becomes one entry per file, with a generated index

Source brief: docs/loom/specs/2026-08-01-backlog-one-entry-per-file.md
Total tasks: 9
Critical-path depth: 5 (≤5)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-08-01, round 5, 15/15)

## Notes

- **Verdict-stamp amendment note**: the header's `PENDING` → `PASS (2026-08-01,
  round 5, 15/15)` edit is amendment kind 1 (stamping the reviewer's
  already-returned verdict); no technical content changed, so no re-review.
  Review trajectory: rounds 1-2 judged concurrently-edited text and are not
  reliable evidence; rounds 3, 4 and 5 judged frozen text and returned 3 gaps,
  1 gap, then PASS.

- **Post-PASS kickoff note**: the three `Kickoff decision:` entries immediately
  below were added AFTER the round-5 PASS. This is the documented kickoff-
  briefing flow (`writing-plans/references/kickoff-briefing.md` fires after
  PASS, before SDD handoff; `subagent-driven-development/SKILL.md:73` rides
  these lines into each implementer packet), not an amendment to reviewed
  content — no task's Description, Acceptance, Dependencies, scope or cited
  facts changed.

- **Kickoff decision — index section order is fixed by urgency**, not
  alphabetically: `COMMITTED-NEXT` → `OPEN` → `PARKED` → `UPSTREAM` →
  `SHIPPED` → `CLOSED — SUPERSEDED` → `Archived`. The index's most common
  question is "what is next", not "what is finished". Any other order makes
  `--check` report false drift, so this is a hard contract for Tasks 3 and 4,
  not a preference.

- **Kickoff decision — slug derivation (ONE-WAY DOOR).** The filename is the
  entry's identity and 73 of them are minted at once; renaming later breaks
  every reference. Rule: lowercase, replace each run of non-alphanumerics with
  a single `-`, strip leading/trailing `-`, and cap the slug at **72
  characters** (the measured longest existing `docs/loom/memory/` slug — 121
  slugs, min 6, median 46, max 72). **ASCII only**: no existing filename in
  `docs/loom/memory/` or `docs/loom/plans/` contains CJK, and exactly one
  BACKLOG heading does (`investing-toolkit 非金錢營運 KPI 自動化 …`) — that one
  entry's slug is **authored by the user**, not transliterated by the
  implementer.

- **Kickoff decision — status suffixes are stripped, from both the slug and
  the `description`.** 56 of the 73 headings end in a status marker
  (`(OPEN)` / `(PARKED)` / `(SHIPPED)` / `(UPSTREAM)` / `(CLOSED — …)`), and
  `status` is already its own frontmatter field. Keeping the marker in the
  description stores one fact twice and lets the two drift — the exact shape
  loom-code 0.39.0's pointer-not-copy rule forbids, and the same reasoning
  that made this arc generate the index rather than hand-maintain it.

- **Kickoff decision — generating the index removes three of the four
  invariants.** The memory store checks (a) every body file has an index line,
  (b) every index line resolves, (c) filename == frontmatter `name`, (d) index
  description == frontmatter description. When the index is *generated from*
  the body files, (a), (b) and (d) are structurally impossible to violate. The
  validator therefore only enforces (c) plus the status enum, and drift is
  caught by regenerate-and-compare (`--check`) rather than by cross-checking a
  hand-written list. This is why no task extends
  `scripts/check_loom_memory_integrity.py`: the backlog store needs *fewer*
  invariants, not more, and widening the memory checker would import
  backlog-only concepts into a script guarded by a PostToolUse hook and a
  finishing-branch step.

  **Correction (2026-08-02, whole-branch review remediation).** This claim did
  not hold past kickoff. `scripts/backlog_index.py --validate` shipped with
  six invariant families, not one: (i) name, (ii) status enum, (iii)
  archive-tier agreement, (iv) `archived:` date shape, (v) frontmatter <->
  body field-agreement (`_FIELD_BULLET_PATTERNS`, added during Task 3's
  drafting to close a real drift the charter's freeform-body rule otherwise
  permitted), and (vi) `description` presence (added by this same
  remediation commit, closing a gap where a missing `description` rendered a
  dangling em dash into the index). Separately — outside `--validate`'s six
  families, since it lives in the archive script, not the generator — a
  file-unit stamp guard is being added by Task 7 concurrently with this
  remediation. "The store needs fewer invariants, not more" is therefore
  false as a durable claim; it described the plan's *starting* comparison to
  the memory store's four, not a ceiling the shipped validator respected.
  Left in place above rather than rewritten, per this plan's own convention
  of dated correction blocks over silent edits.

- **Kickoff decision — no CI file is edited.** Verified: `loom-code-ci.yml:98`
  runs `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -v`, and
  its `paths:` filter already covers `scripts/**` (`:44` pull_request, `:68`
  push) and `docs/loom/**` (`:33` pull_request, `:65` push). A test placed in
  `scripts/` gates with no workflow
  change. The real-store drift gate is a pytest case, not a new CI step.

- **Kickoff decision — no change-folder is bound.** Two non-archived
  change-folders exist (`docs/loom/2026-07-12-us-sec-primary-source-layer/`,
  `docs/loom/2026-07-19-8k-prose-kpi-intake/`); the user has already recorded
  the decision not to bind either. Detection's `>1 → ask` branch is answered by
  that standing decision, not re-asked. This plan's input is the brainstorming
  brief, so `check_scenario_coverage.py` does not apply.

- **§Pinned frontmatter contract** — Tasks 1, 2 and 5 each write this schema
  into a different artifact. Transcribe **VERBATIM from this pin**, never from
  each other and never re-derived:

  ```
  ---
  name: <YYYY-MM-DD-slug — identical to the filename without .md>
  description: <one line; what the item is>
  status: <COMMITTED-NEXT | OPEN | PARKED | UPSTREAM | SHIPPED | CLOSED — SUPERSEDED | archived>
  origin: <optional; where the item came from>
  start: <optional; the start / re-trigger condition>
  ---
  ```

  Live entries carry any status except `archived`; entries under
  `docs/loom/backlog/archive/` carry `archived` and no other value.

- **§Pinned index shape** — Task 3 writes the generator; Task 4 pins its
  stability. Transcribe VERBATIM:

  ```
  # loom family backlog

  <!-- GENERATED by scripts/backlog_index.py — do not edit by hand. -->

  ## OPEN
  - [<name>](backlog/<name>.md) — <description>

  ## COMMITTED-NEXT
  ...same shape, one section per live status, sections omitted when empty...

  ## Archived
  - <name> (archived <YYYY-MM-DD>)
  ```

  Live sections carry the full `description`; the `## Archived` section carries
  one compact line per entry and **no** description.

- **§Pinned date-derivation command** — Task 5 needs a creation date for every
  entry. Measured on this corpus 2026-08-01: only **28 of 73** entries carry a
  date on their `Origin` line and **65 of 73** carry one anywhere in the entry,
  so a text-scan alone cannot date the store. The git fallback was run over all
  73 headings and resolved **73/73** (range 2026-07-03 → 2026-08-01). Use this
  command VERBATIM — take the **last** line, which is the oldest commit:

  ```
  git log --format='%ad' --date=short -S"<first 35 chars of the heading>" -- docs/loom/BACKLOG.md | tail -1
  ```

  **Do not add `--diff-filter=A`.** It filters for commits where the *file* was
  added, not where the *string* was added, and returns empty for every entry —
  verified failing before the fix. Prefer the `Origin` date when the entry
  states one; otherwise use this command.

- **Deferred to a follow-up, tracked, not silently dropped**: the user's global
  `~/.claude/rules/institution-maintenance.md` §1 says of `BACKLOG.md` *"its
  header defines the entry format"*, which this arc makes false. Out of repo;
  its own edit-tier rules require showing the user a diff first.

## Task 1 — Write the backlog store charter

- Description: Create `docs/loom/backlog/README.md` as the store's format SSOT.
  It defines the frontmatter contract (transcribe VERBATIM from §Pinned
  frontmatter contract), the closed status vocabulary, the rule that the
  filename carries a creation-date prefix assigned once and never changed, the
  rule that `docs/loom/BACKLOG.md` is generated output that must never be
  hand-edited, and the archive rule (close = move to `archive/` + stamp
  `status: archived`, never rename, never delete). State explicitly that this
  store's archive-not-delete policy **differs deliberately** from the memory
  store's delete-and-rely-on-git-history charter, so a reader of one is not
  misled about the other.
- Module: docs/loom/backlog/README.md
- Files touched: docs/loom/backlog/README.md
- Context paths:
  - docs/loom/memory/README.md
  - docs/loom/specs/2026-08-01-backlog-one-entry-per-file.md
- Acceptance:
  - RED: `scripts/test_backlog_index.py::test_charter_documents_the_closed_status_vocabulary` — asserts `docs/loom/backlog/README.md` exists and its text contains every one of the seven status values in §Pinned frontmatter contract; fails on a missing file.
  - GREEN: the charter file exists and the test passes; a reader can derive the entry format without opening any other file.
- Dependencies: none
- Independent: true
- Review-weight: prose
- Brief item covered: "`docs/loom/backlog/<slug>.md` — one entry per file, YAML frontmatter carrying `name`, `description`, `status`"

## Task 2 — Validate an entry's frontmatter, two tiers

- Description: Create `scripts/backlog_index.py` with the parse + validate
  half only: read every `*.md` under `docs/loom/backlog/` (excluding
  `README.md`) and under `docs/loom/backlog/archive/`, and enforce (i)
  filename stem == frontmatter `name`, (ii) `status` is a member of the closed
  vocabulary, (iii) an entry under `archive/` carries `status: archived` and a
  live entry does not. Transcribe the vocabulary VERBATIM from §Pinned
  frontmatter contract. Stdlib only, hand-parsed frontmatter, mirroring
  `scripts/check_loom_memory_integrity.py`'s no-PyYAML convention. Exit 0
  clean, 1 on any violation, and name every violating file.
- Module: scripts/backlog_index.py
- Files touched: scripts/backlog_index.py, scripts/test_backlog_index.py
- Context paths:
  - scripts/check_loom_memory_integrity.py
  - docs/loom/backlog/README.md
- Acceptance:
  - RED: `scripts/test_backlog_index.py::test_rejects_entry_whose_filename_does_not_match_frontmatter_name` — builds a temp store with `2026-08-01-alpha.md` whose frontmatter says `name: 2026-08-01-beta`, asserts exit 1 and that the message names the file.
  - GREEN: `python3 scripts/backlog_index.py --validate --store <tmp>` exits 1 on the mismatch fixture and 0 on a clean fixture; a live entry carrying `status: archived` and an archived entry carrying `status: OPEN` are each rejected.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "Validation is two-tier (archived entries ARE validated — user call)". **Not** Decision 3: that decision cites `eipw`, whose leniency is *diff-scoped* (errors on untouched lines are ignorable unless the status changes), whereas this validator is a static corpus-wide check with no notion of which field an edit touched. What this task achieves instead is **narrow field scope** — three fixed checks and nothing else — which serves the same goal (a 73-entry migration cannot be failed retroactively by a rule none of those entries were authored against) by a different mechanism. Decision 3's diff-scoped form is not implemented by this arc; recorded here so no one reads it as shipped.

## Task 3 — Generate the index from the entry files

- Description: Add `--write` mode to `scripts/backlog_index.py`: scan the
  store, group live entries by status, emit one section per non-empty status
  followed by a compact `## Archived` section, and write the result to
  `docs/loom/BACKLOG.md`. Transcribe the output shape VERBATIM from §Pinned
  index shape. Live lines carry the frontmatter `description`; archived lines
  carry name + archive date only. Section order is fixed and deterministic so
  two runs over identical input produce byte-identical output.
- Module: scripts/backlog_index.py
- Files touched: scripts/backlog_index.py, scripts/test_backlog_index.py, docs/loom/backlog/README.md
  <!-- Declaration corrected mid-execution (2026-08-01): the charter edit was
       authorized at dispatch ("ONLY IF your date decision requires a charter
       change") and both reviewers judged it required, but the field was not
       updated to match. Third declared-vs-actual gap in this arc. -->
- Context paths:
  - docs/loom/backlog/README.md
- Acceptance:
  - RED: `scripts/test_backlog_index.py::test_write_groups_live_entries_by_status_and_compacts_archived` — a temp store with two OPEN, one PARKED and one archived entry; asserts the emitted text has an `## OPEN` section carrying both descriptions, a `## PARKED` section, and an `## Archived` line with no description.
  - GREEN: `--write` emits the pinned shape, omits empty sections, and running it twice over unchanged input produces byte-identical output.
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: "`docs/loom/BACKLOG.md` — stays at its current path, becomes the **generated** index, grouped by status"

## Task 4 — Fail CI when the committed index drifts

- Description: Add `--check` mode to `scripts/backlog_index.py`: regenerate
  the index in memory, compare against the committed
  `docs/loom/BACKLOG.md`, exit 1 with a diff summary when they differ, 0 when
  identical. This is the doctoc `--dryrun` pattern — the committed index stays
  readable by agents, and a hand-edit is blocked rather than merely
  discouraged. Add a pytest case that runs `--check` against the **real**
  store so the gate rides the existing CI pytest step with no workflow edit.
- Module: scripts/backlog_index.py
- Files touched: scripts/backlog_index.py, scripts/test_backlog_index.py
- Context paths:
  - .github/workflows/loom-code-ci.yml
- Acceptance:
  - RED: `scripts/test_backlog_index.py::test_check_detects_a_hand_edited_index` — generates an index into a temp store, appends one line to it, asserts `--check` exits 1 and reports the drift.
  - GREEN: `--check` exits 0 on a freshly generated index and 1 after any hand edit; the real-store case runs inside `python3 -m pytest scripts/`.
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: "A generator + a validator wired into `loom-code-ci.yml`'s existing pytest step"

## Task 5 — Migrate the 73 entries

- Description: Split `docs/loom/BACKLOG.md`'s 73 `## ` entries into
  `docs/loom/backlog/YYYY-MM-DD-<slug>.md`, one per entry, frontmatter
  transcribed VERBATIM from §Pinned frontmatter contract. The heading becomes
  `description`; the existing `- Status:` line becomes `status`; `Origin` and
  `Start` map to their fields where present; the rest of the entry becomes the
  body verbatim — **no entry body is rewritten**. The creation-date prefix is
  the entry's `Origin` date where it states one, else the date of the commit
  that introduced the entry — **transcribe that command VERBATIM from §Pinned
  date-derivation command; do not retype it, and never add `--diff-filter=A`,
  which that note proves returns empty for all 73 entries**. Then
  regenerate the index with `--write`. **One entry —
  "operational-kpi full-dimensional-signature slice — follow-ups
  (2026-07-15)" — carries no `Status` line: surface its text to the user and
  ask; do not guess.** Second human call, same discipline: headings too short
  to serve as a `description` (the shortest is 24 chars,
  *"Segment-3 first live run"*, against a 68-char median) must be **surfaced
  for the user to reword**, not silently expanded by the implementer — a
  description is the entry's whole retrieval surface in the generated index.
  Also rewrite the store header's stale policy sentence: the old
  *"Completed items are deleted, not archived — git history is the archive"*
  cannot survive into the generated index, and the archive-not-delete rule now
  lives in the charter (Task 1). Stage with `git add` **by name** (never `git add -A` in
  this repo) and confirm via `git status --short` that no staged deletion is
  left without its replacement.
- Module: docs/loom/backlog/
- Files touched: docs/loom/BACKLOG.md, docs/loom/backlog/
- Context paths:
  - docs/loom/BACKLOG.md
  - docs/loom/backlog/README.md
- Acceptance:
  - RED: `scripts/test_backlog_index.py::test_real_store_has_every_migrated_entry_and_validates_clean` — asserts `docs/loom/backlog/` holds 73 entry files and `--validate` over the real store exits 0; fails while the store is empty.
  - GREEN: 73 entry files exist, `--validate` exits 0, `--check` exits 0 against the regenerated `docs/loom/BACKLOG.md`, and `git status --short` shows no `D` without a paired `R`/`A`. **Reference sweep, content-scoped**: run `grep -rn 'BACKLOG' .` with **no `--include` filter** (the recorded practice this arc must obey — a filetype filter hides `.py` / `.yml` / schema-doc consumers), and confirm every one of the ~394 hits still resolves: a hit citing the path `docs/loom/BACKLOG.md` stays valid, and any hit citing an in-file heading anchor or a line number inside the old monolith is repointed at the entry file that now owns it. Residual hits that are the English common noun (e.g. `loom-code/ROADMAP.md`'s "rolling backlog") are justified in the task report as explicit carve-outs, not silently ignored.
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: "Split `BACKLOG.md` into one file per entry under `docs/loom/backlog/`"

## Task 6 — Pin the archive script's current folder-unit behaviour

- Description: Add characterization tests to
  `loom-code/scripts/test_archive_change_folder.py` pinning the behaviour the
  generalization must not break: the destination is
  `docs/loom/archive/<date>-<change-id>/`, `status: archived` is stamped into
  the moved `proposal.md`, and each of the five refusals fires before any
  filesystem mutation (missing source, symlink source, already-archived,
  destination exists, unsafe change-id). Characterization tests over existing
  behaviour — no production change in this task.
- Module: loom-code/scripts/test_archive_change_folder.py
- Files touched: loom-code/scripts/test_archive_change_folder.py
- Context paths:
  - loom-code/scripts/archive_change_folder.py
- Acceptance:
  - RED: `loom-code/scripts/test_archive_change_folder.py::test_date_prefixed_destination_is_the_current_contract` — asserts the destination folder name is `<date>-<change-id>`; this is the assertion the next task must consciously parameterize rather than silently change.
  - GREEN: every listed behaviour has a test, and `python3 -m pytest loom-code/scripts/` passes.
- Dependencies: none
- Independent: true
- Brief item covered: "**Binding sequence**: first add tests pinning the CURRENT folder-unit behaviour, then generalize."

## Task 7 — Generalize the archive script to single files

- Description: Extend `loom-code/scripts/archive_change_folder.py` to archive a
  single entry file as well as a change-folder, keeping ONE copy of the five
  path-safety guards. The date-prefix behaviour becomes a parameter: **on** for
  the folder-unit caller (unchanged), **off** for the file-unit caller — a
  backlog entry already carries its creation date, and prefixing the archive
  date produces the observed double-date defect. The file-unit path moves
  `docs/loom/backlog/<name>.md` to `docs/loom/backlog/archive/<name>.md`
  unrenamed and stamps **two** fields into its frontmatter — `status: archived`
  **and `archived: <YYYY-MM-DD>`** — with the same rollback-on-stamp-failure
  guarantee.

  **Mid-execution spec correction (2026-08-01, post-PASS).** The second field
  did not exist when this plan passed review. Task 3 introduced it: the pinned
  index shape's compact archived line (`- <name> (archived <date>)`) needs a
  date, the frontmatter contract had no field carrying one, and deriving it
  from git history would have made `build_index()` impure and untestable
  against non-git temp stores. Task 3 therefore added `archived:` to the
  charter's frontmatter contract and to its Archive rule as step 3, and made
  `--write` fail loud on an archive-tier entry missing it. Task 7's text was
  written before that field existed, so implementing Task 7 literally would
  produce archived entries that break index generation on the next run. Gap
  confirmed independently by Task 3's spec-reviewer against
  `docs/loom/backlog/README.md` §Frontmatter contract (the `archived:` line and
  the paragraph below it) and §Archive rule step 3, plus
  `scripts/backlog_index.py`'s `_check_archived_date` (the `--validate`
  invariant) and `_bucket_entry`'s archive-tier branch (the `--write` fail-loud
  path). Recorded here rather than silently carried in a dispatch packet, so the
  plan and the charter do not disagree.

  **Citation correction (2026-08-02, twice).** The `scripts/backlog_index.py`
  pointer above originally read `:200-206`, which is `parse_frontmatter`'s
  header, not the fail-loud behaviour it was cited for. It was repointed at
  `:286-302` / `:343-346` during Task 7, and those anchors had drifted again by
  the time the whole-branch review read them — `:343-346` had become
  `_check_field_agreement`'s definition. The third round replaced all four
  anchors with **symbol and section names**, which do not move when the files
  are edited. Line anchors into files this arc is actively changing were the
  wrong carrier from the start; that is the durable fix, not a third repoint.
  The content was present in the cited file all along — only the line anchor
  had drifted. Caught by Task 7's code-quality-reviewer and re-verified against
  the file before amending.

  **Eighth carry-over site, found during Task 7 (2026-08-02).** The
  `Reuse-adequacy` block below enumerates seven hard-coded sites, all of them
  *path* expressions, and Task 7's first implementation branched all seven
  correctly. It missed an eighth: the frontmatter stamp regex's **value
  pattern** (`(\S+)` — a single whitespace-free token, inherited from
  `_STATUS_LINE_RE`). That was behaviour-preserving for the folder unit, whose
  `proposal.md` statuses are single tokens, and became wrong the moment the
  stamp was pointed at the backlog store's vocabulary, whose
  `CLOSED — SUPERSEDED` value contains spaces — the regex missed, so the stamp
  *appended* a second `status:` line instead of replacing the first, and
  `parse_frontmatter`'s last-wins reading let `--validate` pass on the
  corrupted file. Any later task reusing this stamp against a different
  vocabulary must re-audit that pattern.
- Module: loom-code/scripts/archive_change_folder.py
- Files touched: loom-code/scripts/archive_change_folder.py, loom-code/scripts/test_archive_change_folder.py
- Context paths:
  - docs/loom/backlog/README.md
  - loom-code/skills/finishing-a-development-branch/SKILL.md
- Acceptance:
  - RED: `loom-code/scripts/test_archive_change_folder.py::test_file_unit_archive_keeps_the_filename_unchanged` — archives `2026-08-01-alpha.md`, asserts the destination is `docs/loom/backlog/archive/2026-08-01-alpha.md` with no second date prefix and **both** `status: archived` and `archived: <YYYY-MM-DD>` stamped (see the mid-execution spec correction in this task's Description).
  - GREEN: both units work from one script, Task 6's folder-unit tests still pass unchanged, the refusals fire on both paths, and a file-unit archive that cannot write the stamp **fails loudly** rather than leaving an unstamped file at the destination (pinned by its own case — an unstamped archived entry reads as live to a grepping agent). The module docstring (`:121-127`) and the identifier-guard error text (which today says *"must be a non-empty folder name"*) both describe two units, not one — a file-unit caller must not receive an error message about folders. Behaviour note, verified: `_validate_change_id` does **not** reject dots, so a `<name>.md` identifier passes it unchanged; only the wording needs updating, not the guard.
- Reuse-adequacy:
  - Observed: the script moves `docs/loom/<change-id>/` to `docs/loom/archive/<date>-<change-id>/`, stamps `status: archived` into the moved `proposal.md`'s frontmatter, and validates every path before any filesystem mutation — `read loom-code/scripts/archive_change_folder.py:4-9`
  - Observed (second site): the no-clobber refusal keys on "a prior archive of the same change-id **+ date**", so the date participates in destination uniqueness rather than being decorative — `read loom-code/scripts/archive_change_folder.py:27-28`
  - Observed (third site): the existence guard is `if not source.is_dir():` — hard-coded to the directory unit — `read loom-code/scripts/archive_change_folder.py:135`
  - Observed (fourth site): the already-archived idempotency check reads its status from `proposal_path = source / "proposal.md"`, a fixed child of the source directory — `read loom-code/scripts/archive_change_folder.py:145`
  - Observed (fifth site): the post-move stamp WRITE target is a different expression again, `dest_proposal = dest / "proposal.md"`, computed from the destination and applied only `if dest_proposal.is_file()` — `read loom-code/scripts/archive_change_folder.py:162-163`
  - Observed (sixth site): the SOURCE base path is equally hard-coded — `source = root / "docs" / "loom" / change_id` — the line immediately preceding the existence check — `read loom-code/scripts/archive_change_folder.py:134`
  - Observed (seventh site): the DESTINATION base path is hard-coded in the same way — `dest = root / "docs" / "loom" / "archive" / f"{stamp}-{change_id}"` — one expression carrying both the archive root and the date prefix — `read loom-code/scripts/archive_change_folder.py:155`
  - Intended: reuse the refusal SET, the idempotency guard and the rollback for single entry files — but **three things do not carry over unchanged and must branch on unit type**, so a blanket reuse would fail closed on every file-unit call:
    1. **Existence check** (`:135`) — `source.is_dir()` is never true for a file, so reused as-is it refuses every file-unit archive with "does not exist", the exact opposite of this task's goal. Must become `is_dir()` for the folder unit / `is_file()` for the file unit.
    2. **Pre-move status READ** (`:145`) — `source / "proposal.md"` is meaningless for a single file, where the moved object IS the file whose status must be read. This is the read that powers the already-archived idempotency refusal, so **that refusal does NOT carry over unchanged** — it carries over only once its source expression branches by unit type.
    2b. **Post-move stamp WRITE** (`:162`) — a *separate* expression, `dest / "proposal.md"`, computed from the destination. Branching only the read at `:145` leaves this one writing to a nonexistent child path on the file-unit path. Both sites must branch; neither implies the other.
    3. **Date prefix** — per `:27` it earns its place as part of the change-folder destination's uniqueness key (`same change-id + date`), while a backlog entry already carries a creation date and is unique on its slug; reusing it produces the double-date defect observed at `docs/loom/archive/2026-07-18-2026-07-16-operational-kpi-quarterly/`. Must become a parameter, on for the folder caller and off for the file caller.
    4. **Destination base path** (`:155`) — `dest = root / "docs" / "loom" / "archive" / …` is hard-coded to the change-folder archive. Backlog entries archive to `docs/loom/backlog/archive/`, beside their own store, not into the change-folder archive. Must be parameterized alongside the date flag.
    4b. **Source base path** (`:134`) — symmetric to item 4 and equally hard-coded: `source = root / "docs" / "loom" / change_id` resolves a file-unit call to `docs/loom/<name>.md`, which does not exist; the entry lives at `docs/loom/backlog/<name>.md`. Reused unchanged, the file-unit path fails at the very first guard for the wrong reason. Both base paths must be parameterized, not just the destination.
    5. **The stamp is conditional, and for the file unit it must not be** (`:163`) — the `if dest_proposal.is_file():` wrapper means a change-folder with no `proposal.md` is moved and **silently not stamped**. That is tolerable for a folder, where the stamp is one artifact among several; it is **not** tolerable for a backlog entry, where the stamp is the entire reason the archive is self-describing — an unstamped archived entry looks live to any agent that greps it, which is the exact failure the archive-over-delete decision exists to prevent. The file-unit path must stamp unconditionally and fail loudly if it cannot.
    What genuinely carries over unchanged — note this list deliberately **excludes** the already-archived idempotency refusal, which item 2 shows is source-expression-dependent: the symlink refusal, the destination-exists refusal, the unsafe-identifier refusal, the validate-before-any-mutation ordering, and the rollback-on-stamp-failure guarantee.
- Dependencies: Task 6 completes first
- Independent: false
- Brief item covered: "Closing an item **moves** it to `docs/loom/backlog/archive/` and stamps `status: archived` into the moved file."

## Task 8 — Redirect the skill's write-instruction, and bump the plugin

- Description: Rewrite `loom-pipeline/skills/loom-memory/SKILL.md:49` so a
  backlog-shaped item routes to "create an entry file in
  `docs/loom/backlog/` per its charter" instead of to `docs/loom/BACKLOG.md`,
  which is now generated output. Point at the charter; do not restate the
  frontmatter schema in the skill (SSOT stays in one place). Bump
  `loom-pipeline/.claude-plugin/plugin.json` per the repo rule that a PR
  changing skill content bumps the plugin version, and add the matching
  CHANGELOG entry.
- Module: loom-pipeline/skills/loom-memory/SKILL.md
- Files touched: loom-pipeline/skills/loom-memory/SKILL.md, loom-pipeline/.claude-plugin/plugin.json, loom-pipeline/CHANGELOG.md
- Context paths:
  - docs/loom/backlog/README.md
- Acceptance:
  - RED: `scripts/test_backlog_index.py::test_loom_memory_skill_does_not_route_writes_to_the_generated_index` — asserts the skill text no longer instructs writing to `docs/loom/BACKLOG.md` and does name `docs/loom/backlog/`; fails against the current wording.
  - GREEN: the skill routes to the store directory, the plugin version is bumped, and a repo-wide grep by content (no `--include` filter) surfaces no remaining instruction to hand-write the generated index.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "`loom-pipeline/skills/loom-memory/SKILL.md:49` is rewritten" — note the brief's "only write-instruction in the repo" wording was falsified in Task 5 (a hook was a second one, since repointed); see the brief's correction block.

## Task 9 — Record the deferred follow-up as the store's first hand-authored entry

- Description: Author `docs/loom/backlog/2026-08-01-institution-maintenance-backlog-pointer.md` by hand, against the charter only, recording the REQUIRED post-merge follow-up: the user's global `~/.claude/rules/institution-maintenance.md` §1 states of `BACKLOG.md` *"its header defines the entry format"*, which this arc makes false — the format contract now lives in `docs/loom/backlog/README.md`. Note in the entry that the file is outside this repo and its own edit-tier rules require showing the user a diff before changing it. Then regenerate the index so the new entry appears. This task doubles as the store's authoring dogfood: it is written from the charter alone, with no reference to the migrated entries, so a charter that cannot be followed by a fresh author fails here rather than in six months.
- Module: docs/loom/backlog/2026-08-01-institution-maintenance-backlog-pointer.md
- Files touched: docs/loom/backlog/2026-08-01-institution-maintenance-backlog-pointer.md, docs/loom/BACKLOG.md
- Context paths:
  - docs/loom/backlog/README.md
- Acceptance:
  - RED: `scripts/test_backlog_index.py::test_the_deferred_rules_follow_up_is_tracked_in_the_store` — asserts an entry exists whose body names `institution-maintenance.md`, that it validates clean, and that it appears in the regenerated index under a live status; fails while the follow-up lives only in prose.
  - GREEN: the entry file exists and validates, `--check` exits 0 against the regenerated index, and the follow-up is discoverable by grepping the store rather than by reading this plan.
- Dependencies: Task 5 completes first
- Independent: false
- Brief item covered: "**This is the one deferral that knowingly leaves incorrect text in place** ... Track it as a REQUIRED post-merge follow-up, not an optional one."
