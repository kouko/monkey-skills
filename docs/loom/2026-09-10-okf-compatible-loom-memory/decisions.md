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
