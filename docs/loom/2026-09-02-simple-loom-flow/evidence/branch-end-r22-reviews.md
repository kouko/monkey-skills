# Branch-end round 22 — reviews (fix round after the first real push-gate run)

Delta: `c3c4d478..65c55387`. Two fresh reviewers; the second-vendor leg ran on Codex CLI (`codex exec --sandbox read-only`, gpt-5.6-sol/high), egress approved by the user 2026-09-03.

## opus-review-code-branch-end-r22 (anthropic, lens: code) — NEEDS_REVISION

```yaml
verdict: NEEDS_REVISION
lens: code
reviewed_sha: c3c4d478
dimension_scores: {security: PASS, architecture: PASS_WITH_NOTES, correctness: NEEDS_REVISION, naming: PASS, tests: NEEDS_REVISION, refactoring: PASS, cross-task-coherence: NEEDS_REVISION, external-surface-grounding: PASS, principles-conformance: NEEDS_REVISION, deliberate-simplification: NEEDS_REVISION, deletion-first: PASS}
findings:
  - {id: R22-O1, severity: fatal, dimension: tests, anchor: "scripts/test_codex_git_guard_shim.py:27", text: "W4-06 deleted .codex/hooks/git-guard-shim.sh but left the five tests that exec it; declared package command is red: 5 failed, 1001 passed in 128.94s (exit 127 on the deleted shim).", fix: "git rm scripts/test_codex_git_guard_shim.py in the task that deleted the shim; re-run the package command; re-record the package-tests probe at the new sha."}
  - {id: R22-O2, severity: fatal, dimension: principles-conformance, anchor: "loom-code/scripts/codex_scaffold.py:205", text: "hooks.json is written wholesale, deleting any hook block the repo already had (PRINCIPLES.md non-negotiable 5); this repo's own PostToolUse block was destroyed in W4-06 and codex-first-contact.md tells agents to run this against any adopting repo.", fix: "Load the existing hooks.json, merge loom's PreToolUse Bash entry, leave every other event/matcher untouched, write back only on difference; test that an existing PostToolUse block survives a scaffold run."}
  - {id: R22-O3, severity: important, dimension: correctness, anchor: "loom-code/scripts/loom_checker.py:387", text: "HOST_PLUMBING_PREFIX = '.codex/hooks/' drops the whole directory from changed_paths, but this repo keeps its own gate scripts there; real gate code under that path is invisible to push.probes-adversarial and the intent recomputes.", fix: "Exempt exactly the set the scaffold writes (loom-checker, loom_checker.py, git_exec.py, contract/**, .loom-hook-fired), derived from codex_scaffold's constants; extend the test with a .codex/hooks/other-hook.sh case that must stay visible."}
  - {id: R22-O4, severity: important, dimension: cross-task-coherence, anchor: "docs/loom/2026-09-02-simple-loom-flow/review.json:2018", text: "The six orchestrator-inline notes say the short shas are pre-rewrite, but commit 2ac26023 already remapped them; all 14 resolve at HEAD with the claimed trailers.", fix: "Replace the clause with: the short shas above were remapped to their post-rewrite successors on 2026-09-03 (commit 2ac26023)."}
  - {id: R22-O5, severity: nit, dimension: cross-task-coherence, anchor: "docs/loom/evidence/mechanisms.yaml:53", text: "Eval repointed to cold-read-A.md but the comment '# interim; W4-01 replaces' was carried along (also lines 276, 279).", fix: "Delete the three comments."}
notes:
  - "W4-07 confirmed: ADVERSARIAL_TYPES unchanged (used at :1967); only check_dispatch_covers_tasks reads TRAILER_DUTY_TYPES (:2118); both spec tests proven RED-able in a scratch copy."
  - "hooks.json verified live (PreToolUse loom-checker + two PostToolUse hooks, all +x); --self-test exit 0, no trust marker; --list-rules line 12 accurate."
  - ".codex checker copy differs from source only by the designed '# loom-checker 1.0.0' stamp line."
```

## codex-review-docs-branch-end-r22 (openai, lens: docs) — NEEDS_REVISION

```yaml
verdict: NEEDS_REVISION
lens: docs
reviewed_sha: c3c4d478
dimension_scores: {omission: NEEDS_REVISION, ambiguity: PASS, inconsistency: NEEDS_REVISION, incorrect-fact: NEEDS_REVISION, missing-population: PASS}
findings:
  - {id: R22-C1, severity: fatal, dimension: incorrect-fact, anchor: "docs/loom/2026-09-02-simple-loom-flow/blind-run-report.md:3", text: "The acceptance report still claims it tested the clean tree at a5ca1bcf; the W4 fix round happened afterwards and its 63 dispatches are stale against review.json's 75. Not a blind-run report for the branch-end tree.", fix: "Extend the blind run against the final pre-review sha, update the tested sha and derived counts, and cover W4-06..W4-10 before decision point 3."}
  - {id: R22-C2, severity: fatal, dimension: inconsistency, anchor: "docs/loom/2026-09-02-simple-loom-flow/plan.md:211", text: "Plan risk 1 still describes the deleted 0.110.0 git-guard as the current push blocker and instructs a `!`-prefixed push; W4-06 replaced that shim and ship forbids bypasses.", fix: "Mark the risk superseded by W4-06 and state the current state: repo-local scaffold installed, shim absent, push only after the checker returns exit 0."}
  - {id: R22-C3, severity: fatal, dimension: incorrect-fact, anchor: "docs/loom/memory/README.md:255", text: "The memory index and entry say cross-host enforcement lives only in git-guard.py forwarded by .codex/hooks/git-guard-shim.sh; both are retired.", fix: "Rewrite the entry to the current arrangement (plugin hooks on Claude Code, scaffolded .codex/hooks/loom-checker on Codex) without naming deleted files; regenerate the index."}
  - {id: R22-C4, severity: important, dimension: omission, anchor: "docs/loom/2026-09-02-simple-loom-flow/concept-model.md:165", text: "The rule summary for push.dispatch-covers-tasks records only trailer→dispatch mapping; it omits that code/skill/gate commits must carry a trailer and that spec is exempt like intent and plan.", fix: "Replace the summary with the checker's complete contract."}
  - {id: R22-C5, severity: important, dimension: inconsistency, anchor: "loom-code/skills/ship/SKILL.md:213", text: "The ship table says the rule blocks only when a trailer names an unclaimed task; the checker also blocks untrailered code/skill/gate commits.", fix: "Document both failure modes with their return paths (missing trailer → build/history repair; unclaimed id → review dispatch-record repair) and the spec exemption."}
notes: []
```

## Disposition

All ten findings accepted. R22-O1/O2 → W4-06 fixes; R22-O3/O5 and R22-C2..C5 → W4-10; R22-O4 → the round-22 review-only commit; R22-C1 → blind-run addendum after the fixes land.
