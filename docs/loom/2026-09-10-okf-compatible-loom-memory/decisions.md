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
