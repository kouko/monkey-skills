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
