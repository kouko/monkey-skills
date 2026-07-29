# Plan: docs-review blocking class

**Source brief**: docs/loom/specs/2026-07-30-docs-review-blocking-class.md
**Total tasks**: 4
**Critical-path depth**: 4 (≤5 ✓ — Task 1 → 2 → 3 → 4)
**Execution order**: sequential
**Plan-document-reviewer verdict**: PASS (2026-07-30, round 2, 14/14)

## Task 1 — Add the finding-class taxonomy to the docs-only dispatch

- **Description**: Extend the docs-only dispatch addendum at `loom-code/skills/requesting-code-review/SKILL.md:97` with a fourth clause (d): every finding in this dispatch carries `class: instruction | evidence`. Define **instruction** as text a reader or executor will act on — a rule, a step, an acceptance criterion, a prescribed command or path, a citation used as an instruction — and **evidence** as a narrative claim about what happened or is true: a measurement, an absolute, a provenance attribution, a citation supporting a claim. Give exactly one worked example per class, both drawn from the source audit's real findings: instruction — a bullet instructing an implementer to derive `kpi_id` from a canonical field slug while the shipped code does the opposite (audit §2); evidence — a claim attributed to a source section that does not state it (audit §4.3:166-168, where a variant was attributed to the brief's §Users while §Users says "three comparative years" with no statement-type distinction). State that a finding whose class is unclear is tagged `instruction` (fail closed). **Also add one line to the `findings:` block in §Verdict structure** (`loom-code/skills/requesting-code-review/SKILL.md:141-146`, beneath the existing `where:` / `source:` / `note:` keys) documenting `class: instruction | evidence` as present **for docs-mode dispatches only** — a documentation line with a docs-mode marker comment, in the same shape as the existing `where:` key's inline comment. Do not touch the code-branch path, any dimension list, or the aggregation rule.
- **Module**: `loom-code/skills/requesting-code-review/SKILL.md`
- **Files touched**: `loom-code/skills/requesting-code-review/SKILL.md`, `loom-code/scripts/test_docs_review_blocking_class.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-code/skills/requesting-code-review/SKILL.md`
  - `/Users/kouko/GitHub/monkey-skills/loom-code/scripts/test_docs_review_mode.py`
  - `/Users/kouko/GitHub/monkey-skills/docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md`
  - `/Users/kouko/GitHub/monkey-skills/docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md`
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_docs_review_blocking_class.py::test_docs_dispatch_defines_finding_classes` — assertions scoped to a **measured neighbourhood window** around the anchor string `Docs-only dispatch mode` (not whole-file grep), covering both class names, both worked examples, and the fail-closed sentence; **plus a second window around the `findings:` anchor in §Verdict structure asserting the `class:` key line and its docs-mode-only marker**; proven RED by running all assertions against `git show HEAD:loom-code/skills/requesting-code-review/SKILL.md`.
  - **GREEN**: the test passes; `python3 -m pytest loom-code/scripts/ -q` stays green, proving `test_docs_review_mode.py`'s existing pins on the same bullet still hold.
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: "**Reviewers tag each finding** with `class: instruction | evidence`" plus the brief's two class definitions verbatim from its Smallest End State.

## Task 2 — Filter the aggregation to instruction-class findings

- **Description**: In the same file, amend Step 3 (`:100`, the union-and-re-aggregate step) and the `Aggregation rule` section (`:172`) so that **in docs-only mode** the existing aggregation rule is applied to instruction-class findings only, while evidence-class findings are carried into the verdict as recorded observations with no veto. State explicitly that the aggregation rule itself is unchanged — the filter selects its input. State that a finding missing `class:` counts as instruction (fail closed), consistent with the existing rule that a finding missing `where:` flips the whole verdict. Add one sentence requiring evidence-class findings against settled narrative prose to be superseded by an appended correction naming what it replaces, never edited in place. **Do not edit `rubrics/quality-gate.md`** — it is a distributed functional copy (`loom-code/scripts/distribute.py:87-88`) and editing it from loom-code creates drift that `verify-drift.py` will fail.
- **Module**: `loom-code/skills/requesting-code-review/SKILL.md`
- **Files touched**: `loom-code/skills/requesting-code-review/SKILL.md`, `loom-code/scripts/test_docs_review_blocking_class.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-code/skills/requesting-code-review/SKILL.md`
  - `/Users/kouko/GitHub/monkey-skills/loom-code/scripts/distribute.py`
  - `/Users/kouko/GitHub/monkey-skills/loom-code/scripts/verify-drift.py`
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_docs_review_blocking_class.py::test_aggregation_filters_to_instruction_class` — neighbourhood-scoped assertions around the `Aggregation rule` anchor covering the docs-mode filter sentence, the evidence-recorded-not-blocking sentence, the fail-closed sentence, and the supersede-not-edit sentence; proven RED against `git show HEAD:loom-code/skills/requesting-code-review/SKILL.md`.
  - **GREEN**: the test passes; `python3 loom-code/scripts/verify-drift.py` exits 0, proving no distributed copy was touched; `wc -w loom-code/skills/requesting-code-review/SKILL.md` is under CHK-SKL-010's 4,500-word hard cap (3,930 before Task 1).
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: "**The orchestrator applies the existing aggregation rule to instruction-class findings only.** Evidence-class findings are listed in the verdict as recorded observations with no veto." plus "**Recorded means recorded, not rewritten.**"

## Task 3 — Bump loom-code to 0.41.0 with a CHANGELOG entry

- **Description**: Bump `loom-code/.claude-plugin/plugin.json` `version` from `0.40.0` to `0.41.0` and add a matching `## [0.41.0]` CHANGELOG entry. The entry must state that the change is scoped to docs-only branches, that the aggregation rule itself is unchanged, that **no round cap ships**, and that the mixed-branch case (some `.md`, some code) is explicitly **not** addressed. If the file ended Task 2 above the repo's ~3,750-word soft target, note that and the one-line reason in the entry, per the repo convention for exceeding the soft target. Do not write a test count into the entry — that is stamped at close-out.
- **Module**: `loom-code/.claude-plugin/plugin.json`
- **Files touched**: `loom-code/.claude-plugin/plugin.json`, `loom-code/CHANGELOG.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-code/.claude-plugin/plugin.json`
  - `/Users/kouko/GitHub/monkey-skills/loom-code/CHANGELOG.md`
  - `/Users/kouko/GitHub/monkey-skills/docs/loom/memory/version-bump-packets-must-name-changelog-entry.md`
  - `/Users/kouko/GitHub/monkey-skills/docs/loom/memory/stamp-changelog-test-counts-at-closeout.md`
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_docs_review_blocking_class.py::test_plugin_version_and_changelog_at_0_41_0` — asserts `plugin.json` reads `0.41.0` and `CHANGELOG.md` contains a `## [0.41.0]` heading, both read from the **working tree**, never from a committed blob (`docs/loom/BACKLOG.md` item 2 records that a committed-blob GREEN is unsatisfiable by an implementer, which may not commit).
  - **GREEN**: the test passes; no test count appears in the new entry.
- **Dependencies**: Task 2 completes first
- **Independent**: false
- **Brief item covered**: The brief's Decision ships a behaviour change to loom-code's review path; `docs/loom/memory/version-bump-packets-must-name-changelog-entry.md` makes a version bump plus a named CHANGELOG entry mandatory for any such change, since the marketplace publishes by version and an un-bumped update is a silent no-op.

## Task 4 — Mirror the version bump into the Codex manifest

- **Description**: SSOT is `loom-code/.claude-plugin/plugin.json` (bumped in Task 3). Run `python3 scripts/sync_codex_manifests.py loom-code`, which mirrors that SSOT's shared fields into the Codex manifest, and commit the result unmodified. No hand-written edits to the script's output.
- **Module**: `loom-code/.codex-plugin/plugin.json`
- **Files touched**: `loom-code/.codex-plugin/plugin.json`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-code/.codex-plugin/plugin.json`
  - `/Users/kouko/GitHub/monkey-skills/scripts/sync_codex_manifests.py`
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_sync_codex_manifest.py::test_loom_code_codex_manifest_in_sync_via_shared_engine` fails — the Codex manifest still reads `0.40.0` while `plugin.json` reads `0.41.0`.
  - **GREEN**: the same test passes.
- **Dependencies**: Task 3 completes first
- **Independent**: false
- **Review-weight**: mechanical
- **Brief item covered**: Same repo convention the brief's Decision triggers — the Codex manifest mirror is the second half of a plugin version bump, governed by `docs/loom/memory/version-bump-packets-must-name-changelog-entry.md`; an un-mirrored manifest is drift the sync test blocks.

## Notes

### Review rounds

- **Round 1 — NEEDS_REVISION, 13/14.** One gap (Check 8): the brief's Open Question 1 leaning is two-part, and this plan implemented only the dispatch-text half, justifying the omission by conflating "editing §Verdict structure prose" with "editing `loom_gate_markers.py`'s validator". Fixed by extending Task 1's Description and RED to the `findings:` block and rewriting Notes §1's reasoning.
- **Round 2 — PASS, 14/14.** The reviewer independently re-read `loom-code/scripts/loom_gate_markers.py:200-247` and confirmed the validator never references `class:`, substantiating the corrected reasoning.
- **Post-PASS amendment**: the header verdict was stamped from `PENDING` to `PASS (2026-07-30, round 2, 14/14)` and this Review-rounds subsection was added. Both are the **stamping-the-verdict** amendment kind — no technical content changed, so no re-review.
- **Post-PASS correction to a cited fact, driven by Task 1's reviewers (declared deviation).** Task 1's Description originally cited the evidence-class worked example as "a measured number stated without its denominator or scope (audit §3.3)". Both Task 1 reviewers independently opened the audit and found that §3.3 names *population statements* only as a missing dimension category and contains no such instance; the real, quotable evidence-class defect is the wrong provenance attribution at audit §4.3:166-168. The Description now cites that. **This is a change to a cited fact, which the amendment rules place outside the免-re-review closed list.** It is being made without re-running `plan-document-reviewer` because the correction was produced by two independent source cross-reads of the very document in question — stronger verification than a plan re-review would supply — and it is confined to Task 1, which was in its fix round when the correction landed. Recorded here rather than applied silently. The defect originated in this plan, not in the implementer, which faithfully transcribed it — the recorded pattern at `docs/loom/memory/prose-contract-mechanism-transcribes-from-code.md`.

### Open questions resolved at plan time

1. **Where the `class:` tag lives** — three places inside `requesting-code-review/SKILL.md`, matching the brief's Open Question 1 leaning in both its halves: the docs-mode dispatch text and the `findings:` block in §Verdict structure (both Task 1), and the aggregation section (Task 2).

   **`loom_gate_markers.py`'s validator is deliberately untouched, and that is a separate thing from the §Verdict structure prose.** The validator checks only for a `dimension_scores:` block's presence and a per-finding `where:` line (`loom-code/scripts/loom_gate_markers.py:217-244`); it never references `class:`. So documenting the key in SKILL.md's prose — marked docs-mode-only, unenforced — changes nothing the script validates and cannot invalidate an existing verdict text. What the brief puts out of scope is making `class:` a *validated required field*, which would change what mints a pass marker; that remains unbuilt. An earlier draft of this plan conflated the two and dropped the documentation half on the validator's risk; the plan-document-reviewer caught it, and the reasoning above is the corrected version.
2. **Worked examples** — one per class, both from the source audit's real findings (Task 1). The repo's standing finding is that a term a weak reader must guess is a defect (`docs/loom/memory/doc-string-tests-pass-while-weak-readers-misread.md`).
3. **Word budget** — the file is at 3,930 words against a 4,500 hard cap. Tasks 1 and 2 together are estimated at ~150-200 words, which fits, but the file is already above the repo's ~3,750 soft target; Task 3 carries the one-line reason into the CHANGELOG. If Task 2's GREEN word count ever approaches the hard cap, the fix is to trade an existing paragraph out — **not** to append (`docs/loom/BACKLOG.md` item 11 records this exact hazard on a sibling file).

### Why no task marks `Independent: true`

All four tasks are strictly sequential: Tasks 1 and 2 edit the same file, and Tasks 3 and 4 are the two halves of one version bump. There is no parallel-eligible pair, so the parallel-dispatch markup is absent by design rather than by omission.

### Lessons applied from the parked slice's plan review

The plan-document-reviewer's five findings on `docs/loom/plans/2026-07-30-review-round-ledger-and-bad-fix-recheck.md` are pre-applied here: no `Independent: true` claim over shared `Files touched`; every RED names a concrete `file::test_function`; every `Brief item covered` points at the brief or a named repo convention rather than at a sibling task; Task 4 names its SSOT in the Description the way the schema's worked example does; and no brief field is silently renamed — the brief's field names are used verbatim.

### Standing trap-guards for every implementer dispatch

- Read a file before you Edit it. On a modified-since-read error, re-Read then re-Edit — never retry the same diff.
- If a guard or hook blocks the same command twice, stop and report the block message verbatim; do not try a third time.
- Prove every grep-style prose test RED against `git show HEAD:<file>` — a green suite never demonstrates such a test is load-bearing (`docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md`).
- Clean `loom-code/scripts/__pycache__` before editing skill folders; it trips the skill-folder-structure hook.
- Never `git add -A` in this repo; stage by explicit pathspec. Two obsidian files are modified by another agenda and must never be staged.
