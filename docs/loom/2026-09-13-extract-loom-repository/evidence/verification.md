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

## Final W3 candidate

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

## Focused integration commands and results

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
