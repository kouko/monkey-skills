# W1-02 capture-intent refactor evidence

Date: 2026-09-13  
Mode: `skill-refactor` package-resource mode  
Overall verdict: **PROCEED**

## Frozen baseline

- Revision: `d5548b0d10f15769093c5aa18336395cef0cbaac`
- Canonical manifest: `/Users/kouko/.codex/baselines/2026-09-13-shrink-three-loom-skill-entrypoints/capture-intent/baseline/manifest.json`
- External manifest SHA-256: `177330ec403a2ea2ac2e71a93cd0d1241baa936797fdc48f6a9e4a8a47e9243c`
- `package_gate.py verify`: PASS before candidate comparison.
- Candidate: `/Users/kouko/.codex/candidates/2026-09-13-shrink-three-loom-skill-entrypoints/capture-intent/package`.

The candidate was applied only after Q1-Q3 and the layered reducer passed.
`test-prompts.json` is the confirmed W0 evaluation input and is included in
the corrected cumulative candidate package total.

## Refactor

Only `SKILL.md` changed. The round compressed the user-stop overview, interview
field summary, one-way-door classes, consequence examples, and implementation-
question examples. The station summary and exact test-pinned carriers remain.
Both bundled references are byte-identical to the frozen baseline, so the
reduction is deletion/compression rather than relocation.

Confirmation, user-claim, irreversible existing-state, automatic-publication,
question-recording, and downstream handoff duties remain visible in the
entrypoint. No loom-code private reference or sibling-plugin dependency was
added.

## Q1 — behavioral equivalence

Frozen baseline and isolated candidate packages were separately replayed by
Codex collaboration agents against all three confirmed prompts: normal
engineering capture, a pinned irreversible notes migration, and an ambiguous
product aspiration. No Claude Code validation was used.

`equivalence_check.py` returned `PASS_LAYER_1`: output type, section structure,
paths, tool sequence, and word-count tolerance passed. Three independent Codex
judges used utility, information-completeness, and boundary framings with
alternating A/B labels. All three returned `equivalent`; none identified a
specific lost behavior. The candidate's shorter first question in the two
incomplete cases still asks one gap-driven `what` question and preserves every
later-required field and safety boundary.

Verdict: **PASS (3/3 equivalent, high confidence)**.

## Q2 — whole-package reduction

| Measure | Baseline | Candidate | Reduction |
|---|---:|---:|---:|
| `SKILL.md` words | 3,553 | 2,711 | 842 (23.70%) |
| `SKILL.md` bytes | 22,925 | 18,527 | 4,398 (19.18%) |
| Package words | 4,822 | 4,267 | 555 (11.51%) |
| Package bytes | 30,711 | 28,560 | 2,151 (7.00%) |

The package is below the at-most-4,339-word target. The skill-specific body cap
also passes.

Verdict: **PASS (whole package reduced by at least 10%)**.

## Q3 — invariants

- Frontmatter `name: capture-intent` and `version: 1.0.0` are unchanged.
- `references/interview.md` and `references/second-vendor.md` are byte-identical
  to the frozen baseline; declared dependencies and package structure remain.
- Required anchors remain: Steps 1, 2, 4, and 5 plus both registered prose gates.
- The one-message confirmation still states automatic publication, opt-out, and
  separate merge consequences before informed consent.
- Pinned handling of irreversible existing state is restated, not re-asked.
- User-supplied claims, open-question blocking, question logging, and downstream
  `write-spec` / `write-plan` routing remain explicit.
- Standalone loom-design boundary and isolated-install checks pass; no private
  loom-code file dependency was introduced.

Verdict: **PASS**.

## Layered reducer and focused checks

`package_gate.py reduce` returned `PASS` for resource, owning-skill, package,
and two permitted Codex host evidence records. Claude Code was not used.

Commands and results against the isolated pinned repository plus candidate:

```text
python3 -m pytest loom-design/scripts/spec/test_capture_intent_contract.py -q
33 passed

python3 scripts/check-skill-structure.py loom-design
All 4 skills PASS

python3 scripts/check_plugin_boundaries.py loom-design
OK

python3 -m pytest scripts/test_loom_plugin_install_layout.py -q
14 passed
```

The first isolated focused run found two exact-phrase pins removed by otherwise
equivalent compression. Both carriers were restored before the verdict; the
second run found one more paired phrase, which was restored before the final
33/33 pass.

After applying the candidate, the shared worktree run passes 33/33 tests. The
concurrent W1-01 candidate initially removed `write-plan`'s station summary,
but its replacement restored that cross-plugin contract before this task was
committed. `git diff --check` passes.
