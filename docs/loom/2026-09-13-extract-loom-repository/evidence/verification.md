# Independent repository verification

W3 started from the W2 full-lineage candidate. Its retained root tests exposed
six failures: missing package lock, description corpus and a valid repository
memory store, plus monorepo-wide manifest eligibility. Two targeted bootstrap
regressions failed before implementation. The bootstrap now retains the exact
existing dependencies, scopes eligibility and marketplace membership to the
three plugins, and starts a new valid memory store without importing unrelated
monkey-skills lessons.

History-sensitive tests require original commit IDs for frozen evidence. Two
bootstrap test copies now translate only Git command arguments through the
complete committed map, preserving original evidence identities. The matching
historical probe copy receives the same adaptation to preserve its byte-equality
contract. The lookup regression first failed with a missing helper.

Full package verification remains the closing-review gate; a passing focused
matrix is not claimed as the full suite.

The first focused W3 matrix found three remaining monorepo test examples naming
dbt-wiki/research-toolkit and a root README table contract. Bootstrap copies now
use actual Loom plugins and preserve the README's version/skill-count row.
Template test files have a `.template` suffix in monkey-skills to prevent source
pytest collection; the extractor strips it when creating the candidate.

The history-sensitive test matrix also proved four cited development commits
are outside fixed main ancestry. The extraction now validates an exact auxiliary
manifest: every tip must exist and its full SHA must appear in a current retained
file. Only those tips and required ancestry are added under local archive refs;
unreferenced branches are discarded. The fixture regression initially failed
with an unsupported auxiliary argument, then passed while proving unknown tips,
unjustified tips, unrelated citations and abandoned branch imports are rejected.

The W3c focused matrix passed 159 code/root/hook/history tests (one pre-existing
retired-checker skip), six design configuration tests and four workflow tests.
Manifest drift, both plugin boundaries, cross-references, mechanism population,
contract citations and operative doc citations passed. Doc citation output
reported two checked citations and three existing unchecked forms, with no
findings; unchecked forms are not claimed as verified.

The measurement gate correctly failed because the baseline snapshot `923fb84a`
had no retained delta and was pruned. It is now the fifth explicitly cited
auxiliary tip, justified by KICKOFF-DEFAULTS. Abbreviated citations are accepted
only when Git resolves them uniquely to the manifest's full commit ID. The
bootstrap measurement command resolves this old ID through the same committed
map before actually running the historical hook. Its baseline limit is unchanged.

## W3 candidate before closing-review fixes (superseded)

Local candidate: `/private/tmp/loom-candidate-20260913-w3d`.
Source commit: `6fc6fef8969f411f81e9cb566539d7068d379e10`.
Git-filter-repo version: `a40bce548d2c`.

- Primary ancestry: 1,709 commits.
- Complete mapped population including required auxiliary ancestry: 1,720.
- Verified retained commits and explicit snapshot tips: 489.
- Mixed commits with retained and removed paths: 323.
- Selected source-tree files before bootstrap: 562.
- Filtered main: `f730d30aa8da935420f6795514d0db4a1710b545`.
- Bootstrap/provenance HEAD: `bc86be145c987651130d67b362e34c9317143f41`.
- Complete map SHA-256: `7ff5f7e758f4f12482318318d97a9298f2432dc37f16c32f4a735a041d8537b4`.

All 489 retained/snapshot commits matched their original selected file trees,
blob IDs, modes, author/committer identities, dates and messages. The source
snapshot was unchanged. The final candidate has exactly five local evidence
archive refs, no remote, and a clean worktree. No push, source deletion or source
history rewrite occurred. Each source plugin remains unchanged until the explicit
bootstrap adaptation layer, which changes only development/test history lookups
and repository infrastructure; no station/runtime behavior is redesigned.

## W3 focused integration commands and results (superseded)

Commands used the existing Python 3.12 pytest environment; no packages were
installed. The ambient Python in the temporary directory lacked pytest, so the
already-available test interpreter was selected explicitly.

```sh
python3 -m pytest scripts/ .claude/hooks/ loom-code/scripts/test_contract_manifest.py loom-code/scripts/test_hooks_json.py loom-code/scripts/test_check_mechanisms.py loom-code/scripts/test_probes_cumulative_boundary_reassessment.py loom-code/scripts/test_probes_coldread_abuse_coldread_branch_end.py -q
# 216 passed, 1 skipped in 13.99s
python3 -m pytest loom-design/scripts/test_marketplace_entry.py loom-design/scripts/test_ci_workflow.py -q
# 6 passed in 0.10s
python3 -m pytest loom-workflow/scripts/test_handoff_compaction.py loom-workflow/scripts/test_independent_advisor_plugin_readmes.py -q
# 4 passed in 0.10s
```

The root `scripts/` run includes the existing isolated-install suite and its
negative sibling-private-path cases. The one skip is the pre-existing probe for
the retired `check_loom_memory_integrity.py`, not a new extraction exception.

All of the following exited zero in the final candidate:

```sh
python3 scripts/sync_codex_manifests.py --check --all
python3 scripts/check_plugin_boundaries.py loom-code
python3 scripts/check_plugin_boundaries.py loom-design
python3 scripts/check_plugin_boundaries.py loom-workflow
python3 loom-code/scripts/check-skill-crossrefs.py
python3 loom-code/scripts/check_mechanisms.py --baseline f730d30aa8da935420f6795514d0db4a1710b545
python3 loom-code/scripts/check_mechanisms.py --measure
python3 loom-code/scripts/check_contract_citations.py
```

Mechanism population: 122, matching the filtered baseline. Actual historical
session-start recomputation: 5,278 words; current session-start: 745 words.
The operative doc-citation scan exited zero: 2 checked, 3 existing unchecked
forms, 0 findings. These unchecked forms remain an explicit limit.

Source-side extraction regression suite: `python3 -m pytest
scripts/test_extract_loom_repository.py -q` — 31 passed in 6.76s. Collection of
`scripts/loom-repository-bootstrap` found no tests (expected pytest exit 5),
proving the `.template` suffix prevents source-side duplicate collection.

## Closing-review Round 2 fixes

The first targeted regression run was RED: five failures covered nontransportable
archive refs, hostile Git routing, the undeclared filter-repo dependency and
standalone historical-probe import order. The whole-extraction hostile test
injects Git directory, worktree, common-dir, index, object-store, config and
template overrides directed at a decoy repository. It requires extraction to
succeed while source and decoy snapshots remain unchanged and a hostile hook
sentinel remains absent. Every Git/clone/filter-repo subprocess now receives a
fresh controlled environment with inherited `GIT_*` input removed.

The two identical historical probe templates import the migration helper after
their explicit script-path setup. A fresh pytest process collecting only the
historical probe verifies this independently of earlier imports.

Evidence tips now use `refs/tags/loom-evidence/<original-sha>`. A normal
`git clone --no-local` regression proves a branch-only evidence tip survives
transport and its historical file contents remain available; abandoned refs
remain excluded. Earlier W3 archive-ref claims above describe superseded runs.

The dependency is pinned as `git-filter-repo==2.47.0` in requirements-dev.txt and
the existing hash lock was regenerated with its documented `uv pip compile`
command. The declared isolated environment ran extraction and lock regressions:
37 passed in 8.77s. Dependencies were downloaded only into a temporary uv cache,
not a conda environment. The same dependency/lock/test expectations are copied
into the candidate bootstrap. Primary upstream grounding is recorded in
`external-contracts.md`, including the distinction between preserving hash text
inside messages and preserving commit IDs.

The extractor was mechanically separated into source validation, auxiliary
validation, clone/filter, map-reading, verification and bootstrap helpers. No
extractor function exceeds 100 lines.

### Final Round 2 candidate and focused results

The current candidate is `/private/tmp/loom-candidate-20260913-review-r2`,
with bootstrap HEAD `2c34c48151677232007a2c310a805e21158f3a7d`.
Its source remains `6fc6fef8969f411f81e9cb566539d7068d379e10` and filtered
main remains `f730d30aa8da935420f6795514d0db4a1710b545`. Counts are unchanged:
1,709 primary commits, 1,720 complete mapping rows, 489 verified retained/tip
commits, 323 mixed commits and 562 selected source files. The complete map
SHA-256 remains `7ff5f7e758f4f12482318318d97a9298f2432dc37f16c32f4a735a041d8537b4`.
The tool reports `a40bce548d2c`; installed package metadata confirms 2.47.0.
Git is `2.50.1 (Apple Git-155)`.

The following commands ran with the declared hash-locked dependencies, prefixed
by `uv --cache-dir /private/tmp/loom-uv-cache run --isolated
--with-requirements requirements-package-tests.lock`:

```sh
# Source repository: GREEN after the five targeted RED failures.
python -m pytest scripts/test_extract_loom_repository.py scripts/test_kickoff_defaults.py -q
# 37 passed in 8.77s
# Current candidate:
python -m pytest scripts/ .claude/hooks/ loom-code/scripts/test_contract_manifest.py loom-code/scripts/test_hooks_json.py loom-code/scripts/test_check_mechanisms.py -q
# 173 passed in 8.94s
python -m pytest loom-design/scripts/test_marketplace_entry.py loom-design/scripts/test_ci_workflow.py -q
# 6 passed in 0.02s
python -m pytest loom-workflow/scripts/test_handoff_compaction.py loom-workflow/scripts/test_independent_advisor_plugin_readmes.py -q
# 4 passed in 0.01s
```

A separate normal `git clone --no-local` into
`/private/tmp/loom-candidate-20260913-review-r2-transport` received all five
`refs/tags/loom-evidence/*` tags without a custom refspec. Its local origin
configuration was removed after cloning. In that transported clone, the same
declared environment ran:

```sh
python -m pytest loom-code/scripts/test_probes_cumulative_boundary_reassessment.py loom-code/scripts/test_probes_coldread_abuse_coldread_branch_end.py -q
# 43 passed, 1 skipped in 4.18s
python -m pytest docs/loom/2026-09-04-adversary-three-way-attribution-measured/evidence/probes/test_abuse_coldread_branch_end.py -q
# 16 passed, 1 skipped in 0.05s (independent fresh process)
python loom-code/scripts/check_mechanisms.py --measure
# exit 0: 745 current words; actual historical baseline 5,278 words
```

Both skips are the same pre-existing retired-checker probe in its two copies.
Both local repositories have clean worktrees and no remotes. Extraction's
source snapshot comparison passed; no source refs/configuration/worktree were
changed by extraction. No candidate push, source deletion or source history
rewrite occurred. Full package tests remain reserved for closing review.
