# Run decisions — 2026-09-10-okf-compatible-loom-memory

Decisions this run made under the Standing decision rule of its active goal
condition: choices the goal did not pre-decide are the run's to make, recorded
here with their candidates and sources instead of being asked.

## D-1 — Where W1-01's tests live

**Decision.** W1-01 adds its scaffolding assertions as new cases inside the
existing `scripts/test_loom_plugin_install_layout.py`, rather than creating a
new test module, even though plan.md lists that file under W4-01.

**Candidates.** (a) New `loom-memory/scripts/test_scaffold.py`; (b) extend the
existing install-layout harness now and let W4-01 extend it again.

**Why (b).** REQ-22 requires the existing harnesses to be extended "rather than
paralleled". A task ordering in plan.md names the file's final owner; it does
not forbid an earlier task from adding a case to a shared harness, and TDD needs
a failing assertion before W1-01's files exist.

**Sources.** spec.md REQ-22; plan.md W1-01 and W4-01 Files lines.

## D-2 — Root README plugin-table rows for loom-memory

**Decision.** W1-01 adds a `loom-memory` row to all three root READMEs'
plugin tables (`README.md`, `README.zh-TW.md`, `README.ja.md`), placed
immediately after the `loom-workflow` row, even though plan.md's W1-01
Files line does not name the root READMEs.

**Candidates.** (a) Leave the root tables untouched until a later task
adds them; (b) add the row now, alongside the per-plugin READMEs the
Files line does name.

**Why (b).** The root tables already carry a row per shipped plugin
(`loom-code`, `loom-design`, `loom-workflow`, …) with version/skills/
commands/description columns, mirroring `.claude-plugin/marketplace.json`.
Publishing `loom-memory` there without a root-table row would leave the
repo's own top-level index silently behind the marketplace listing added
in this same task — the kind of drift REQ-1 (independently installable
capability) exists to avoid at the distribution-surface level. The
dispatch packet also named this scope explicitly as agent-decided. Skills
and Commands columns are entered as `0` — the scaffold ships no skill or
slash command yet, per this task's stated boundary.

**Sources.** Dispatch packet ("Survey findings" — root README table row);
spec.md REQ-1; plan.md W1-01 Files line (per-plugin READMEs only,
root READMEs not excluded).

## D-3 — Plugin `description` wording

**Decision.** Both `loom-memory` manifests (`.claude-plugin/plugin.json`,
`.codex-plugin/plugin.json`) and the `marketplace.json` entry use, byte-
identical: "Optional, passively-triggered repository-memory capability
with an OKF v0.2-compatible store profile. Installs and works standalone
— no dependency on loom-code, loom-design, or loom-workflow. Claude Code
+ Codex."

**Candidates.** (a) Describe the four operations (Recall/Record/
Reconcile/Retire) in the description, as `loom-code`'s description names
its five stations; (b) describe the standalone/OKF-compatible property
without naming operations that this task does not build.

**Why (b).** REQ-1 and REQ-2 are this task's acceptance lines; the four
operations belong to W2-01. Naming unbuilt operations in a manifest that
ships now would overclaim scope the same way the READMEs were instructed
not to (packet: "without documenting commands that do not exist yet").
The wording states the two properties this task actually proves:
independent installability and OKF v0.2 store conformance.

**Sources.** Dispatch packet "What to build" step 2; spec.md REQ-1,
REQ-2, REQ-6.

## D-4 — Committed fixture location and shape

**Decision.** W1-02 commits its OKF v0.2-compatible bundle at
`scripts/fixtures/loom-memory/okf-v0.2/` (repo-root `scripts/`, not inside
`loom-memory/`), containing a `README.md` charter concept
(`type: Memory Store Guide`), two lesson concepts of different `type`
values (`gotcha`, `practice` — so REQ-8's grouping-by-type is exercised),
one of which carries an unrecognized frontmatter key (`type_note`) to
exercise REQ-12, and a generated `index.md`.

**Candidates.** (a) `loom-memory/tests/fixtures/okf-v0.2/`, matching the
packet's own stated convention for plugin-committed fixtures ("Plugin
packages that do commit fixtures put them under `<plugin>/tests/fixtures/`
… with a module-level constant naming each file"); (b) the path the packet
already names in its "What to build" step 4 and in plan.md's W1-02 Files
line: `scripts/fixtures/loom-memory/okf-v0.2/`.

**Why (b).** REQ-22 is explicit that this fixture exists so `loom-memory`
can be validated "using only the installed `loom-memory` files" when copied
into an unrelated clean install root — the fixture itself is deliberately
OUTSIDE the plugin so it never ships as part of the plugin's own install
surface (it belongs to the *harness* that proves the plugin works standalone,
not to the plugin). Both the packet's own "What to build" step 4 and
plan.md's W1-02 Files line name this exact path; the `<plugin>/tests/
fixtures/` convention the packet cites is for fixtures a plugin ships and
tests against itself, which is a different case REQ-22 does not ask for
here.

**Sources.** Dispatch packet "Environment facts" and "What to build" step
4; spec.md REQ-22; plan.md W1-02 Files line.

## D-5 — `run_package_tests.py` scope: `memory` joins `--only`'s allow-set now

**Decision.** W1-02 adds a `memory` group to `loom_family_commands` (running
`pytest loom-memory/scripts/`) and to `--only`'s validated set at
`scripts/run_package_tests.py:58`, plus a matching case in
`scripts/test_run_package_tests.py`, even though plan.md's own Files line
for W1-02 does not name `run_package_tests.py`.

**Candidates.** (a) Leave the runner untouched until a later wave adds it;
(b) wire it now, recorded as a decision (the packet explicitly authorized
this: "This is beyond plan.md's Files line for W1-02 — take it and record
it as a decision").

**Why (b).** `python3 scripts/run_package_tests.py --loom-family -q` is the
one command CI and every other Loom station runs; without this wire-up, a
green package-test run would never execute this task's own new tests —
the acceptance criterion `--only memory` requires the group to exist. The
dispatch packet named this exact gap and pre-authorized taking it.

**Sources.** Dispatch packet "What to build" step 5 and "Acceptance
criteria"; `scripts/run_package_tests.py:26-48,58`.

## D-6 — Stdlib-only hand-rolled frontmatter parser (no PyYAML)

**Decision.** `loom_memory.py` parses frontmatter with a small
indentation-based mapping/sequence reader (`_parse_mapping` /
`_parse_sequence`), not PyYAML, even though PyYAML 6.0.2 is importable in
this environment.

**Candidates.** (a) `import yaml` — simpler, handles the full YAML grammar;
(b) hand-rolled stdlib-only parser scoped to exactly the shapes this
profile needs (scalar `key: value`, and one level of sequence-of-mappings
for `sources:`).

**Why (b).** The legacy validator this module retires made the identical
call for the identical reason (`scripts/check_loom_memory_integrity.py:25-27`):
this module ships inside an *installable plugin* — a third-party runtime
dependency here is a distribution-surface cost every consumer of
`loom-memory` pays, not a convenience. The Loom profile's frontmatter shape
is small and fixed (REQ-10), so a scoped parser is not a general-YAML
reimplementation risk — it is exactly the same "mechanize the small format"
argument the legacy checker already made and this repo's `CLAUDE.md`
contract-citation rule does not change.

**Sources.** Dispatch packet "What to build" step 1 ("Stdlib only");
`scripts/check_loom_memory_integrity.py:25-27,86`; spec.md REQ-12.

## D-7 — Generated `index.md` grouping and ordering rule

**Decision.** `generate_index` renders, in this fixed order: an `## Guides`
section (concepts with `type: Memory Store Guide`) first, then one `## `
section per remaining distinct `type` value sorted alphabetically by that
type string; within every section, entries are sorted alphabetically by
`name`. Each entry line is `- [name](file) — description`, with
`description` copied byte-identically after `.strip()` on both the
frontmatter value and the rendered line (mirroring the legacy checker's
already-proven `[d]`-invariant comparison rule, generalized to a value that
is now always generated rather than hand-authored).

**Candidates.** (a) Preserve file-glob (alphabetical-by-filename) order
with no type grouping — simplest, but does not satisfy REQ-8's explicit
"grouping lesson links by memory type" requirement; (b) group by `type`,
`Guides` pinned first, alphabetical within and across groups (chosen).

**Why (b).** REQ-8 requires grouping by memory type and placing the charter
concept under `Guides` — that rules out (a) directly. Alphabetical-by-type
and alphabetical-by-name within each group is the smallest total order that
makes two regenerations of the same store byte-identical (REQ-9) without
depending on filesystem iteration order or insertion history, which
`iter_concept_files`'s own `sorted(store.glob(...))` already establishes as
this codebase's convention for determinism.

**Sources.** spec.md REQ-8, REQ-9; `scripts/check_loom_memory_integrity.py`
`_format_index_line`/invariant `(d)` (the byte-identical-after-strip rule
this module reuses).

## D-8 — No hook shipped for W2-01

**Decision.** W2-01 ships no optional memory hook. The complete Recall /
Record / Reconcile / Retire mechanism is reachable through
`loom-memory/skills/loom-memory/SKILL.md` alone; no hook file is added.

**Candidates.** (a) Ship a non-blocking relevance-reminder hook now,
scoped to REQ-5's bound (no authoring, no deletion, no failing unrelated
Loom operations); (b) ship no hook, leaving the door open for a later
task if a measured need appears.

**Why (b).** REQ-5 makes a hook optional, and the spec's own "Hook is
removable" design decision states the mechanism must already be complete
through the skill alone. The dispatch packet's own risk note repeats
"prefer shipping no hook". Nothing in this task's scope (REQ-2, REQ-4,
REQ-5, REQ-11, REQ-13–17, REQ-20, REQ-21, REQ-23) requires a hook to be
satisfied, and no measured trigger-miss problem motivates adding one pre-
emptively — CLAUDE.md's Simplicity rule ("no speculative abstractions...
I didn't ask for") argues against authoring one on spec alone.

**Sources.** spec.md REQ-5 and its "Hook is removable" design decision;
plan.md W2-01 Risk line ("Prefer shipping no hook; if you ship one,
justify it in decisions.md").

## D-9 — Content split between `SKILL.md` and its two references

**Decision.** `SKILL.md` (1,017 words) carries: the git-memory boundary
statement, the two passive activation triggers, one compact
Trigger/Steps block per operation, the failure-behavior summary
(structural failure, legacy-store report), and the resource map.
`references/okf-profile.md` carries the six pinned OKF v0.2 clauses, the
Loom minimum concept schema table, the lesson body contract (`Trigger`/
`Correct path`/`Why`/`Limits`), and the `log.md`-omission rationale.
`references/operations.md` carries the fully expanded step-by-step
procedure for all four operations, including REQ-14's five-way
classification filter and REQ-15's reconcile-vs-narrow decision, spelled
out at a level of prose `SKILL.md`'s compact steps intentionally do not
repeat.

**Candidates.** (a) Put everything in `SKILL.md` — one file, no
progressive disclosure, but risks crowding toward the 4,500-word/6,000-
token hard cap as REQ-11's body contract and REQ-14/15's classification
and merge rules are spelled out in full; (b) split compact
trigger-and-steps into `SKILL.md`, move the OKF profile contract and the
expanded procedure into two references, loaded only when the compact
version is not enough.

**Why (b).** `SKILL.md` sits at 1,017 words — about 23% of the 4,500-word
hard cap — leaving headroom without needing compression. The split
mirrors this repository's own progressive-disclosure convention (the same
one REQ-8 requires of `index.md` itself): an agent reads the compact
operation contract every time, and opens `references/operations.md` or
`references/okf-profile.md` only when a specific step needs the fuller
rule. Neither reference is required reading for ordinary Recall/Record
use, which keeps the always-loaded surface small.

**Sources.** CLAUDE.md Skill Structure section (SKILL.md token cap,
Anthropic progressive-disclosure convention); spec.md REQ-8 (the
progressive-disclosure precedent already established for `index.md`);
dispatch packet "What to build" steps 2–4.

## D-10 — README's authored `description`

**Decision.** `migrate_legacy_store.py`'s `README_DESCRIPTION` constant:
"This store's charter: one distilled loom-family lesson per file, the test
for whether a fact belongs here rather than in an open intent, a commit
trailer, or a one-off evidence record, and how to record, recall, and
reconcile an entry; read before adding, editing, or retiring any concept in
this store."

**Candidates.** (a) A one-line paraphrase of the README's title only
("Charter for the loom-* practice-memory store"); (b) a standalone durable
relevance rule that states what an agent gains by opening the file, mirroring
REQ-10's contract for every other concept's `description`.

**Why (b).** REQ-10 requires `description` to be "a standalone durable
relevance rule" for every concept, the guide included; (a) restates a title,
which fails REQ-14's classification test the way a bare label would for any
other concept. The chosen text names the file's actual jurisdiction (when a
fact belongs here vs. an intent/trailer/evidence record) and its four
operations, both durable properties of the store's charter that do not
change when tooling around it changes.

**Sources.** spec.md REQ-10, REQ-18; `docs/loom/memory/README.md` §Charter —
jurisdiction, §When to record (source material paraphrased, not quoted).

## D-11 — `sources[].resource` shape for a derived (no-origin) commit

**Decision.** When legacy `origin` is absent, the added source is
`{resource: "introducing commit <full 40-hex sha>"}` — the same shape for
both the one lesson (`the-resolved-test-command-must-cover-every-suite-root.md`)
and the `README.md` guide concept, both derived via
`git log --diff-filter=A --format=%H -- <path>`, taking the OLDEST line
returned (a file added exactly once has exactly one line; the oldest is
taken defensively in case history ever shows more than one Add event for
the same path).

**Candidates.** (a) A bare 40-hex string with no label, matching only the
positive case's `origin` strings (which are free-form prose, e.g. "branch
feat-x, session Y"); (b) a labelled `"introducing commit <sha>"` string.

**Why (b).** A bare hex string reads as ambiguous provenance (is drift a
commit? a build id?) to a later reader with no other clue, and REQ-18 asks
specifically for a source "describing" the introducing commit, not merely
naming it. The label is stable, greppable, and distinguishes a derived
source from a verbatim-preserved `origin` string on sight.

**Sources.** spec.md REQ-18 ("add a source describing the full introducing
commit"); verified fact that exactly 1 of 293 lessons plus `README.md` need
this path.

## D-12 — No generic frontmatter quoting for the migration's own writer

**Decision.** `migrate_legacy_store.py` renders frontmatter with a small
local `render_frontmatter()` that never wraps a scalar value in quotes,
rather than reusing `loom_memory.dump_frontmatter()`.

**Candidates.** (a) `lm.dump_frontmatter()` — already exists, already
round-trip-tested for the general case; (b) a migration-local renderer that
never quotes.

**Why (b).** `dump_frontmatter`'s `_quote_scalar` wraps any scalar
containing a colon in `"..."`. The real corpus has 21 `description` values
that contain BOTH an internal colon AND an internal `"` character, 4 of
which END in a literal `"`; wrapping those in an added pair of quotes
produces a line whose OUTERMOST quote-stripping on re-parse leaves a stray
trailing `"` inside the recovered value — a real, not hypothetical,
corruption risk measured against this exact corpus before writing the
renderer (see the module's own docstring). Every value migrated here was
already stored on disk unquoted, on one physical line; `loom_memory.
parse_frontmatter`'s reader only needs the line's FIRST colon to be the key
delimiter, which always holds since no key name here contains a colon —
so an unquoted renderer is both simpler and provably safe against this
corpus, verified directly by `test_migrate_handles_description_with_colon_
and_trailing_quote` and by the real migration's own
`loom_memory.py validate` passing clean.

**Sources.** Corpus scan (21 colon+quote descriptions, 4 trailing-quote
descriptions, 0 leading-quote descriptions) performed before implementation;
`loom_memory.py`'s `_parse_mapping` first-colon-partition rule.

## D-13 — README's charter prose stays byte-identical; the legacy-tool
references inside it are a documented residual, not silently left broken

**Decision.** `migrate_legacy_store.py` changes README.md's prose ONLY by
removing the `## Index` heading and its 293 hand-maintained entry lines
(replaced by generated `index.md`, per the spec's "Charter location"
decision). Every other sentence, including the §Format and §Index
subsections that still describe `type: practice | gotcha | process`,
`origin:`, and `python3 scripts/check_loom_memory_integrity.py [--write|
--check]`, is left byte-identical to the pre-migration text — those
subsections now describe a superseded authoring format and a deleted
script. This staleness is a known, reported residual (see the task report's
"references left" section), not fixed in this task.

**Candidates.** (a) Rewrite §Format/§Index to describe the OKF profile and
`loom_memory.py` as part of migration; (b) leave the charter body
byte-identical except for removing the Index section, and report the
staleness.

**Why (b).** The task's own "What to build" instructions state the
migration "gives README.md complete concept metadata... while its charter
prose stays byte-identical" — a scope boundary distinct from the general
"update every reference to the deleted script" instruction, which this
decision reads as covering LIVE operative references outside the store
(fixed: `AGENTS.md`; and the now-retired `.claude/hooks/
check-memory-store-integrity.sh` + its test, which literally shelled out to
the deleted script and is retired in the same commit — see the report's
`files_outside_task_list`). Rewriting README's own multi-paragraph §Format
contract is a content redesign, not a reference substitution, and doing it
inside the byte-preserving migration step would make the Git-based
byte-identity proof for the guide concept (REQ-18's own acceptance
evidence) unable to assert anything meaningful. `loom-code/scripts/
check_doc_citations.py`'s own three-bucket design (resolved / finding /
UNCHECKED) means a backticked citation to the now-deleted script inside
README.md becomes UNCHECKED, not a FINDING, so this residual does not
redden CI.

**Sources.** Dispatch packet "What to build" step ("charter prose stays
byte-identical"); spec.md REQ-18, "Charter location" design decision;
`loom-code/scripts/check_doc_citations.py` docstring (round-2 fallback,
three-bucket design).

## D-14 — W3-01b: restore the shift-left hook (repointed), correct the
now-stale README §Format/§Index, and narrow the byte-identity test that
would otherwise block that correction

**Context.** D-13 retired `.claude/hooks/check-memory-store-integrity.sh`
and its test because they shelled out to the deleted
`scripts/check_loom_memory_integrity.py`. The hook's own header records
that the invariant it guards — an entry edited without its index kept in
sync — shipped broken three times, twice caught only after push under a CI
job whose display name names a different check. Deleting the guard to make
a change go green, rather than repointing it at the invariant's new home,
is exactly the failure mode the hook exists to prevent recurring.

**Decision — restore, repoint, don't reinvent.** The hook is recovered
verbatim from Git at `bd7c080a0` and repointed at
`loom-memory/scripts/loom_memory.py validate <store>` (exit 0/1, not the
legacy checker's own exit convention) in place of the deleted checker. The
header prose is rewritten to describe the CURRENT invariant — OKF-profile
validation plus `index.md` drift, not the retired §Index-in-README format —
while keeping the three-incidents rationale verbatim in substance, because
that rationale is the reason the hook exists and losing it during the
repoint would be the same class of silent loss this decision exists to
avoid. The fix-hint in the hook's stderr output is updated to the new CLI
(`regenerate-index` / `validate`) so a blocked agent is not handed a dead
command. The test file is rewritten with the same case coverage (path
match, near-miss spellings, checker/validator-absent no-op, exit codes) —
the two cases specific to the old §Index-in-README format (the "index line
missing/present" fixture shape) are replaced with an equivalent-purpose
fixture built on the new profile (a store an OKF-aware `_make_store` helper
either makes valid — entry + a freshly regenerated `index.md` — or leaves
with a broken entry frontmatter and no index), because the old format no
longer exists to test against. `.claude/settings.json` gets its
`PostToolUse` entry back, appended after `remind-memory-mirror.sh` (its
prior position) rather than reordered.
`.claude/hooks/remind-memory-mirror.sh` was checked and carries no
reference to the legacy format or the deleted script — nothing to repoint
there.

**Decision — narrow `test_guide_concept_metadata_and_charter_prose`'s
byte-identity assertion, don't delete or weaken it.** That test's original
assertion compared the ENTIRE post-migration README body, byte-for-byte,
against the pre-migration charter fetched from Git at
`PRE_MIGRATION_SHA` — proof that migration itself did not silently rewrite
any charter prose (D-13's own "byte-identical" commitment; REQ-18's
acceptance evidence). But that same assertion also blocks any later,
separately-motivated, deliberately-committed correction to the README's
prose — this task's fix to `## Format — one fact per file`, which the
migration left describing a legacy `type: practice | gotcha | process` /
`origin:` shape and a deleted `--write`/`--check` command (README.md:75,
README.md:127-130 pre-fix — a charter that teaches a deleted command is
worse than no charter). Two mechanically distinct properties were living in
one assertion: (1) migration fidelity, and (2) the README's prose has never
changed since migration. Property (2) is not something REQ-18 promises
going forward, only something the migration commit itself had to hold.

The test is narrowed, not weakened: it now partitions both the
pre-migration charter and the current README body at the
`## Format — one fact per file` heading. Everything before that heading —
title, blockquote, the full jurisdiction table, "When to record" in its
entirety — is still required byte-for-byte identical; a silent rewrite
anywhere in that region (the majority of the charter) still fails the
test. Inside the Format section, five load-bearing clauses this task's fix
did NOT touch — the filename-slug rule, the "description states the
durable rule" clause, the description-vs-body test (with its Fails/Passes
bullets), the recorded-instance case study, and the forward-only binding
clause — are pinned as exact multi-line substrings required present,
verbatim, in BOTH the pre-migration and the current text. Only the code
block (legacy frontmatter shape) and the two paragraphs that named the
deleted script/command are left uncompared, because those are precisely
what this task's report says it changed and why. A future accidental loss
of any of the five pinned clauses — even one nested inside a
Format-section edit — still fails this test; only a deliberate,
documented, narrowly-scoped Format-section rewrite (like this one) can
pass it while changing prose.

This is the "assert the specific load-bearing sections survive" option
from the task's own two offered narrowings, not the "compare against
79692695f" option — that alternative would re-encode the SAME pre-fix
text as the new baseline and block this exact fix for the same reason as
before, since W3-01's migration was itself byte-preserving (D-13) and so
`79692695f`'s README is byte-identical to the pre-migration charter this
test already fetches from Git.

**Sources.** Dispatch packet Task A/Task B and their acceptance criteria;
`.claude/hooks/check-memory-store-integrity.sh` header (recovered,
rewritten); D-13 above; `loom-memory/scripts/loom_memory.py` CLI
(`validate` / `regenerate-index`, exit 0/1).

## D-15 — W3-02: Ship/git-memory line, and how the contract-pin sweep was
scoped

**Context.** REQ-24 retires every repository-memory coupling from
`loom-code/contract/manifest.yaml` while REQ-20 keeps `git-memory` as the
owner of commit- and PR-bound Decision/Learning/Gotcha carriers, and Ship
may still route through it for that. The dispatch asked me to read both
`manifest.yaml`'s Ship action and `loom-code/skills/ship/SKILL.md` before
deciding where the line falls.

**Ship/git-memory line.** `loom-code/skills/ship/SKILL.md` was read in
full and greped for `memory`; its only mention (§2, "Use
`loom-workflow:git-memory` to classify the change and contribute durable
Decision, Learning, and Gotcha material inside this schema when earned")
is exactly the commit-carrier behavior REQ-20 keeps — it never mentions
`docs/loom/memory/**`, a `memory` action, or store ownership. **No edit
was made to `ship/SKILL.md`**: there was nothing to remove from it. The
only manifest-side coupling was the `actions: - name: memory / owner:
ship` entry (git-memory trailers *plus* `docs/loom/memory/` entries via
`templates/memory-README.md`) — that whole action, and its `summary:`
line, were deleted; the `tools: - name: git-memory` declaration stays
untouched.

**Sweep scope — production contract pins fixed (RED before, GREEN
after).** Beyond the two files REQ-24 names, two more operative contract
pins turned out to assert the retired artifact/template against the REAL
committed manifest/templates directory (not a synthetic copy), so they
would have gone RED the moment `manifest.yaml`/the template were touched
and are equally "equivalent contract pins" under REQ-24's own wording:
- `loom-code/scripts/test_contract_charter.py` — `EXPECTED_ARTIFACTS`
  asserted the `charter` sub-command's row order against the live
  manifest; `memory` removed from the list.
- `loom-code/scripts/test_probes_language_policy.py` — `_template_files()`
  glob-counts `loom-code/contract/templates/*`; asserted `== 8`, now `==
  7` after `memory-README.md`'s deletion (REQ-25). Its docstring's
  GREEN-file list also dropped the retired filename with a one-line note
  pointing at `loom-memory/templates/memory-store/`.

**`loom-code/scripts/test_probes_charter_charter.py`.** This probe file
builds its OWN synthetic tmp-path manifest copy (never the real one) to
exercise the generic `contract.charter-complete` rule — it does not
require `memory` to be a real production artifact. Even so, two tests
(`test_charter_row_goes_to_unknown_artifact_blocked`,
`test_charter_command_renders_complete_rows_on_valid_manifest`) used the
name `memory` as their placeholder row and would have silently kept
"testing" a row that no longer exists in production. Renamed the
placeholder to `sample-row` throughout (`NEW_ARTIFACTS`, `ALL_ROWS`, both
`data["artifacts"][...]` mutations, and the matching docstring line) so
the fixture cannot be mistaken for a claim that the production artifact
survives. `test_charter_command_renders_complete_rows_on_valid_manifest`'s
`len(data_rows) == 7` held unmodified: 6 real production rows (after
`memory`'s removal) + 1 synthetic `sample-row` = 7, same as before.

**Found but left alone — a genuinely out-of-scope pre-existing RED.**
`loom-code/scripts/test_probes_coldread_abuse_coldread_branch_end.py::
test_memory_step_store_integrity_check_exits_zero` shells out to
`scripts/check_loom_memory_integrity.py`, which W3-01
(`79692695f`) already deleted — this test has been RED since before W3-02
started, for a task this plan attributes to W3-01/REQ-26, not W3-02. I
first rewrote it to call the new `loom-memory/scripts/loom_memory.py
validate docs/loom/memory` command (GREEN), but that edit broke this same
file's OTHER test,
`test_graduated_probe_copies_byte_identical_to_evidence_originals`, which
enforces byte-identity between this graduated probe and its FROZEN
evidence original at
`docs/loom/2026-09-04-adversary-three-way-attribution-measured/evidence/
probes/test_abuse_coldread_branch_end.py` — a closed change's evidence
directory, out of bounds for this task's sweep. Editing only the
graduated copy is exactly the "compression/edit without updating the
paired original" failure mode `graduated-probes-survive-squash` warns
about. I reverted the edit (recovered via `git show HEAD:<path>`, since
`git checkout --` is dcg-blocked here) rather than touch the frozen
evidence file to make the pair agree again. The RED stays, reported as an
unresolved risk for whichever task closes out REQ-26's loose end, not
silently fixed by widening W3-02's scope into a closed change's evidence.

**Sources.** `docs/loom/2026-09-10-okf-compatible-loom-memory/spec.md`
REQ-20, REQ-24, REQ-25; `loom-code/skills/ship/SKILL.md` (full read);
`loom-code/contract/manifest.yaml` diff; the four edited/deleted files
above; the operator's own (machine-local, not this repository's) session
memory entry `graduated-probes-survive-squash`, named here for the
pattern it documents, not as a repository-committed source.

## D-16 — W4-01: extend, not add a new CI gate; version numbers; Acceptance
coverage map

**Extended `loom-code-ci.yml` and `skill-structure.yml`, did not add a
fourth workflow file.** The plan's own risk note for W4-01 says "extend
existing boundary and install harnesses rather than add a new gate," and
`loom-code-ci.yml` already houses the repo-wide drift gates
(`sync_codex_manifests.py --check --all`, boundary checks) that run
irrespective of which plugin changed — the natural home for a new
plugin's boundary check and its `memory` pytest group is a new step there,
not a parallel `loom-memory-ci.yml` that duplicates the trigger-path
bookkeeping `loom-design-ci.yml` carries for a single plugin. Added
`loom-memory/**` to both trigger blocks (matching the existing
`loom-design/**` / `loom-workflow/**` fail-open rationale already written
into the file), a `Run pytest suite (loom-memory)` step calling
`run_package_tests.py --loom-family --only memory`, and
`check_plugin_boundaries.py loom-memory` alongside the two existing calls.
No job was renamed (branch-protection pins job display names).

**Found and fixed a live CI bug, not part of any test file's RED→GREEN:**
`skill-structure.yml`'s `loom-memory-store-integrity` job still called
`scripts/check_loom_memory_integrity.py`, which W3-01 (`79692695f`)
deleted — every push/PR since has been failing that job (confirmed by
running the command directly: `No such file or directory`). Repointed it
at `loom-memory/scripts/loom_memory.py validate docs/loom/memory`, the
validator the store's own plugin ships. Job name (`loom memory store
integrity`) kept unchanged. Also added a `check-skill-structure.py
loom-memory` step to the `structure` job, matching the per-plugin pattern
the three existing loom plugins already use there.

**Version numbers.** `loom-memory` stays at `0.1.0` — this is its first
release, so there is nothing to bump against; its own CHANGELOG.md (new
file) records the release. `loom-code` bumps `2.0.9` → `2.0.10`: its
`contract/manifest.yaml`, `contract/README.md`, and the deleted
`contract/templates/memory-README.md` are published plugin content even
though `check_version_bump.py`'s `SKILL_CONTENT_DIRS` tuple does not
count `contract/` (only `skills,hooks,agents,references,scripts`) — the
dispatch brief's explicit instruction to bump loom-code overrides the
checker's narrower automatic definition here, and the checker still
passes on this diff (a plugin the gate considers unchanged does not need
to move, so bumping anyway is never a violation). Ran
`sync_codex_manifests.py loom-code` to mirror the bump into
`.codex-plugin/plugin.json` (the pre-commit hook enforces this).
`loom-design`'s version is untouched — W4-01 touched no `loom-design`
file.

**Acceptance-line coverage, six lines, positive/negative/boundary per
plan's own naming** (nodeid = proved by that test; "new" = written in this
task):

- A1 valid-install / invalid-okf: `loom-memory/scripts/test_loom_memory.py::
  test_valid_profile_passes` (positive, non-isolated) +
  `scripts/test_loom_plugin_install_layout.py::
  test_isolated_loom_memory_validates_the_committed_fixture_using_only_installed_files`
  (positive, isolated — new) +
  `...::test_isolated_loom_memory_rejects_a_corrupted_fixture_copy_using_only_installed_files`
  (negative, isolated — new).
- A2 indexed-recall / bounded-load: `loom-memory/scripts/test_loom_memory.py::
  test_bounded_index_lets_an_agent_pick_without_opening_bodies` (positive) +
  `...::test_drifted_index_is_a_validation_failure_naming_the_mismatch`
  (boundary/negative). Not re-run under isolation: A2 is a pure-Python
  property of `loom_memory.py`'s parser, already exercised isolated by A1's
  new tests calling the same installed script.
- A3 operations / unauthorized-retire: `loom-memory/scripts/
  test_skill_contract.py::test_four_operations_contract` (positive) +
  `...::test_retire_requires_explicit_user_approval_before_deleting`
  (negative).
- A4 consumers-work / absent-plugin: `scripts/test_loom_plugin_install_layout.py::
  test_isolated_loom_code_completes_write_plan_intake_without_loom_memory_sibling`
  (positive, new — REQ-3's concrete absence proof for loom-code) +
  `...::test_isolated_loom_design_keeps_complete_surface_without_loom_memory_sibling`
  (boundary, new — same proof for loom-design) +
  `...::test_memory_plugin_installs_alone` /
  `...::test_code_design_manifests_have_no_memory_dependency` (W1-01,
  manifest-level boundary).
- A5 migrated-corpus / fingerprint-loss: `loom-memory/scripts/
  test_migrate_legacy_store.py::test_lesson_and_guide_concept_counts_are_293_and_1`
  and `...::test_lesson_bodies_and_descriptions_survive_migration_byte_for_byte`
  (positive — recomputed from Git at `PRE_MIGRATION_SHA`, never a
  committed snapshot). No separate "fingerprint-loss" test exists or is
  needed: the byte-for-byte `assert post_body == pre_body` / `assert
  post_fm["description"] == pre_fm["description"]` comparison in that same
  test IS the fingerprint check — any lost or altered byte fails that
  exact assertion by construction, so the test proves both directions at
  once.
- A6 valid-store / corrupt-fixture: same two new isolated-install tests
  cited under A1 (the fixture IS the store this line is about).

**Unresolved risk carried forward, not this task's to close:** none new.
D-15's "found but left alone" RED
(`test_memory_step_store_integrity_check_exits_zero`) was already resolved
by the later `6780d70dd` (W3-02b) commit — confirmed here by running it:
it now reports 1 skipped with a named reason, not RED.

## D-17 — R2-fixes F1: the exact rule that closes a frontmatter block

**Decision.** `parse_frontmatter`'s closing-delimiter scan now requires
BOTH conditions on a candidate line: `_indent_of(line) == 0` (column 0,
no leading whitespace) AND `line.strip() == "---"` (the line's only
content, once trailing whitespace/CRLF remnants are stripped, is three
dashes). A line that is `---` but indented under a nested key (e.g.
`notes:` opening a block whose first line happens to be `  ---`) no
longer closes the frontmatter — only an unindented `---` does, matching
how `_parse_mapping`/`_parse_sequence` already reason about indentation
for everything else in this parser.

**Why not `lines[i] == "---"` (exact-equality, no `.strip()`).**
Considered and rejected: `splitlines()`/`read_text`'s universal-newline
translation should already remove a trailing `\r`, but the module has no
guarantee against a stray trailing space on an otherwise-bare `---` line,
and the boundary/abuse probes in this same suite deliberately exercise
CRLF and BOM inputs. Requiring `_indent_of(line) == 0` is the load-bearing
half of the fix (indentation-blindness was the actual defect); keeping
`.strip() == "---"` on top costs nothing and avoids a needless new
failure mode for trailing whitespace.

**Verified no behavior change on the real store.** Compared
`parse_frontmatter` output (before vs. after this fix) over every one of
the 294 files in `docs/loom/memory/` (293 lessons + `README.md`) — zero
mismatches. The real store contains no line that is a bare, indented,
literal `---`, so this is a pure defect fix with no migration implied.

## D-18 — R2-fixes F4: narrowed forbidden-list + the assertion that replaces it

**Decision.** `test_no_host_specific_path_or_private_api` no longer
forbids `${CLAUDE_PLUGIN_ROOT}` or the bare token `CLAUDE_PLUGIN_ROOT` —
REQ-21 bans a path that only resolves on one specific host, and
`${CLAUDE_PLUGIN_ROOT}` is the opposite: the one form Claude Code
substitutes correctly on every host that runs it, and every sibling skill
already uses it this way. The narrowed forbidden list keeps only
genuinely host-specific tokens: `.claude-plugin`, `.codex-plugin`,
`/Users/`, plus a new regex check for an absolute `/home/<user>` path.

**The assertion that replaces the removed protection.**
`test_no_bare_repo_root_relative_script_path` (new) scans every line of
`_all_skill_text()` and fails if any line contains the literal substring
`loom-memory/scripts/` — the repo-root-relative form that only resolves
inside this authoring repository (F3's actual defect) and is exactly what
F4's old forbidden-list entry was structurally incapable of catching
(it forbade the *fix*, not the *defect*). This is the test that would now
catch F3 recurring.

## D-19 — R3-fixes: the design correction replacing eight point-fixes

**Decision.** The eight defects the Round 3 adversary found were not eight
independent bugs — every one was one of `loom_memory.py`'s three ad-hoc
scanners (frontmatter quote-stripping, a whole-text `[..](..)` substring
scan, and `read_text()`-based drift comparison) applied outside the shape
it can actually handle, plus one non-atomic write path in
`migrate_legacy_store.py`. Patching each symptom would have produced a
ninth; instead the five rules below replace the scanners themselves.
Each probe named is now a plain passing assertion (marker removed,
docstring rewritten past-tense) — none deleted, none weakened.

- **R1 — frontmatter values are byte-preserving.** Removed `_strip_quotes`
  from `_parse_mapping` entirely; a scalar is everything after the first
  `:` separator (the mandatory single space after the delimiter is still
  trimmed — that space is the delimiter's own convention, not part of the
  value). REQ-8's whitespace-only stripping stays where it already lived,
  at the index-copy site (`_collect_index_items_strict`'s `.strip()`),
  never at parse time. Consequence: `generate_index`'s own hardcoded
  `okf_version: "0.2"` line now parses back with its quote characters
  intact, so `INDEX_FRONTMATTER` was updated to `{"okf_version": '"0.2"'}`
  to match the byte-literal form it is compared against — this is the one
  place a "stored value changes" ripple was expected, and it is
  self-consistent (the generator and the comparator agree). Verified
  against the real 294-file corpus (below): only `index.md` itself
  differs in parsed form, and `validate`/`regenerate-index` both still
  exit 0 and are byte-identical, so no corpus rewrite was needed.
  Proves: `test_generate_index_quoted_description_is_copied_byte_identically`.
  One incidental collateral fix: `test_adversarial_okf_memory_probes.py`'s
  `test_parse_frontmatter_nested_dash_only_line_does_not_drop_trailing_keys`
  asserted an unquoted `resource` value that only held because the (now
  removed) quote-stripping ran; its expected value was updated to the
  byte-preserved quoted form, its docstring corrected from "unquoted" to
  reflect what the source text actually contains — the defect the test
  pins (indentation-blind `---` scan dropping `sources`) is untouched.

- **R2 — the index is checked by the generator's own grammar, not a
  substring scan.** `_check_index_targets` no longer scans the whole
  index text for any `[..](..)` occurrence. It now matches only lines
  shaped exactly like a generated entry (`^-\s+\[name\]\(href\)\s+—\s+`,
  anchored at line start, href captured lazily up to the first
  `) <space> em-dash <space>` — the entry's own closing delimiter, never
  the first `)` byte or a link quoted later in the description). This
  removes the phantom-href class (a description containing
  `[the plan](plan.md)`, a filename containing `(b)`) while still
  flagging a hand-edited bogus link (`ghost.md`) and a store-escaping
  target (`../../../etc/passwd`) — both still exercised by
  `test_adversarial_okf_memory_probes.py`'s still-green
  `test_check_index_targets_rejects_href_that_escapes_the_store` and
  `test_loom_memory.py`'s `test_all_offenders_are_reported_not_just_the_first`.
  Proves:
  `test_validate_freshly_regenerated_index_with_link_in_description_is_clean`,
  `test_validate_concept_filename_with_parentheses_is_clean`.

- **R3 — the drift comparison is unconditionally byte-for-byte.**
  `check_index_drift` now compares `index_path.read_bytes()` against
  `generate_index(...).encode("utf-8")`, never `read_text()` (which
  folds CRLF to LF and would hide real drift). The diff message still
  decodes for a human-readable unified diff; only the pass/fail
  comparison is byte-exact, per REQ-9's unconditional statement.
  Proves: `test_validate_crlf_index_that_byte_differs_from_regeneration_is_reported`.

- **R4 — migration writes are staged, and a rerun is harmless.**
  `migrate()` now computes every lesson rewrite in memory first —
  reading, splitting, and validating each legacy file's `name` and
  `description` (a new `_check_legacy_concept_frontmatter` helper) —
  before writing a single byte; a failure anywhere in the batch raises
  `MigrationError` naming the offending file with zero files written.
  The same helper also refuses a legacy-shaped store whose concept file
  already carries a `sources` key (already in the OKF profile, not
  legacy) — the guard that keeps a rerun from ever reaching the old
  demote-verbatim-origin-to-a-stray-key bug, independent of the
  atomicity fix. Proves:
  `test_migrate_legacy_file_missing_name_leaves_every_other_file_untouched`,
  `test_migrate_rerun_after_partial_failure_keeps_the_store_valid`.

- **R5 — the walk matches the pinned clause, and an absent store is
  named.** `iter_concept_files` stays non-recursive (concept identity
  stays flat — a nested document is never a concept), but a new
  `iter_nested_markdown_files` (`store.rglob("*.md")`, filtered to
  `parent != store`) feeds a new `validate_bundle` check that reports
  every nested Markdown document as its own `nested-document` offender,
  named by its path relative to the store — satisfying pinned clause 1's
  coverage of the whole bundle without ever treating a nested file as a
  concept. Separately, `validate_bundle` now checks `store.is_dir()`
  first and returns a single `store-missing` violation naming the store
  path itself when the store is absent or not a directory, instead of
  falling through to a misdiagnosed `index-missing`. Superseded
  `loom-memory/skills/loom-memory/references/okf-profile.md` clause 1's
  prior sentence claiming a nested subdirectory is simply "out of this
  profile's scope entirely" — the pinned clause does not permit that
  escape; the reference now states what the validator does: nested
  documents are reported, not skipped. Proves:
  `test_validate_nested_markdown_document_without_frontmatter_is_reported`,
  `test_validate_absent_store_directory_names_the_store_path`.

**Real-corpus verification (all 294 files under `docs/loom/memory/`).**
Compared `parse_frontmatter` output before vs. after R1 over every file:
only `index.md` differs (its own `okf_version` value now carries its
quote characters, matched by the updated `INDEX_FRONTMATTER` constant) —
no lesson or guide concept's stored value changed. No nested Markdown
document exists under the store (R5 is a no-op on this repository's
actual data). `validate docs/loom/memory` exits 0; two consecutive
`regenerate-index` runs are byte-identical to each other and to the
committed `index.md` (confirmed via `cmp`); `git status` shows no diff
on `index.md` after regeneration.

## D-20 — Writing is byte-preserving too, and refuses what it cannot represent

**Decision.** `_quote_scalar` becomes `_scalar_literal` and no longer quotes a
value for containing a colon. `okf_version` keeps its schema-mandated quoted
literal. An empty value, or one carrying leading or trailing whitespace, raises
instead of being silently quoted.

**Candidates.** (a) Leave the serialiser quoting and teach the parser to strip
quotes again; (b) make both directions byte-preserving and abort on the two
shapes that have no faithful unquoted form.

**Why (b).** R1 removed quote stripping from the parser on the ground that
REQ-8 permits stripping whitespace only. Re-adding it to satisfy the writer
would restore the defect R1 fixed. The parser splits on the first colon and
takes the remainder verbatim, so a colon never needed quoting; the quoting was
the whole defect, and it accumulated a pair on every rewrite. Aborting on an
unrepresentable value follows the module's existing abort-rather-than-launder
rule.

**Sources.** REQ-8; D-17 (R1); the round-trip regression in
`loom-memory/scripts/test_loom_memory.py::test_dump_then_parse_returns_the_same_bytes`.

## D-21 — Second-vendor findings: no special case in the serialiser, and stage-time identity checks

**Decision.** (a) `_scalar_literal` drops its `okf_version` special case: REQ-7's
exact text `"0.2"` lives in the constant, quotes included, so the value is
written verbatim like any other. (b) The migration's pre-write check also
verifies `name` equals the filename stem, the identity that index regeneration
enforces at the end of the run.

**Candidates.** For (b): keep the check only in regeneration and document that a
mismatch leaves a partial store; or move the identity check into staging.

**Why.** Both defects share one shape — a rule enforced at a different point
from where the bytes are decided. The serialiser re-quoted a value the parser
had already handed back with its quotes; the migration validated identity after
it had already rewritten earlier files, so the zero-writes-on-failure guarantee
held for a missing `name` and silently failed for a mismatched one.

**Sources.** Codex second-vendor review of `e075c3ff3`, two important findings
with reproductions; regressions at
`test_loom_memory.py::test_okf_version_round_trips_without_gaining_a_quote_pair`
and `test_migrate_legacy_store.py::test_name_stem_mismatch_aborts_before_any_file_is_written`.
