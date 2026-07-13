# loom family practice-memory store

> Repo-native home for distilled loom-* practices, habits, processes,
> and recurring gotchas — knowledge not bound to a single commit that
> must travel with the repo (any machine, any host, headless agents).
> One fact per file. Machine-local Claude memory keeps only pointers
> here — this folder is the durable truth (versioned, host-agnostic,
> greppable). Stale facts are deleted, not archived — git history is
> the archive.

## Charter — jurisdiction

| Knowledge shape | Home |
|---|---|
| Open item / debt / re-trigger | `docs/loom/BACKLOG.md` (cross-plugin) or plugin README §parked (local) |
| Decision bound to a commit | git-memory trailers (`Decision:`) |
| Distilled practice / habit / process / recurring gotcha | **`docs/loom/memory/`** (this store) |
| One-off event artifact | `docs/loom/{specs,plans,audits,dogfood,research}/` |
| Harness/dcg friction (plugin-shipped) | `loom-code/.../environment-gotchas.md` — stays, NOT migrated |

## When to record

A fact already known before the branch closes (not merge-required to
observe) MUST land in that same branch/PR, never a separate post-merge
branch — a post-merge branch+PR just to record something you already
knew is pure overhead the close-out flow should have absorbed. The one
exception: a fact only confirmable by observing real post-merge/
installed behavior genuinely needs a follow-up branch — but even those
should be batched, not one-PR-per-discovery.

**Pull, not push.** Nothing auto-loads this folder. Retrieval = read
the index below / grep on demand. This preserves the documented
anti-preload decision (`dev-workflow/skills/git-memory/SKILL.md:193-197`);
evidence: a 2026 ETH Zurich study found always-loaded auto-generated
context files reduced agent task success by ~3% and raised inference
cost by ~20% (`dev-workflow/skills/git-memory/standards/memory-conventions.md`
§Pull retrieval).

## Format — one fact per file

The file is named `<name>.md` — the frontmatter `name` slug IS the
filename, so index links never diverge from filenames.

```markdown
---
name: <kebab-slug>
description: <one-line — used for relevance decisions at pull time>
type: practice | gotcha | process
origin: <PR / session / audit reference>
---

<the fact>

**Why:** <why the behavior matters>

**How to apply:** <the operative rule, readable standalone>
```

## Index

One line per memory: `[<name>](<file>.md) — <description>`.
`<description>` is the frontmatter `description` field copied
byte-identical — the index line IS the description, so the pull-time
relevance surface never diverges from the file.

[argparse-subparser-default-shadows-parent](argparse-subparser-default-shadows-parent.md) — Python argparse — a subparser's default silently overwrites the parent parser's already-parsed option value (silent wrong-value bug class)
[assertion-must-encode-the-property-it-claims](assertion-must-encode-the-property-it-claims.md) — A guard whose docstring claims an ORDERING/relational property but whose assertion only tests membership ("before" in text and "candidate round" in text) is vacuous — it passes on the violated state; read each guard's own claim and ask "would this fail if the claimed property broke?"
[big-rename-operative-frozen-sweep](big-rename-operative-frozen-sweep.md) — Big-rename recipe — split operative vs frozen references, regex look-behind guards for path collisions, git mv to preserve history, closing grep-guard for zero operative survivors
[cache-key-collision-across-migration](cache-key-collision-across-migration.md) — A new function reusing a legacy cache key but writing an incompatible payload shape under an immutable TTL is a never-self-healing 'works on my machine' landmine — give each payload shape a distinct key + a cross-function pre-seed regression test
[chrome-debug-port-ipv6-gotcha](chrome-debug-port-ipv6-gotcha.md) — A user's main Chrome can hold 127.0.0.1:9222 answering 404 while the fresh debug instance binds IPv6-only — chrome-devtools MCP dials IPv4, so fall back to puppeteer-core over the IPv6 WebSocket
[ci-skill-structure-scan-gap-obsidian](ci-skill-structure-scan-gap-obsidian.md) — .github/workflows/skill-structure.yml scans only domain-teams + loom plugins — an obsidian (or other unscanned plugin) SKILL.md CHK-SKL-010 word-cap breach merges silently; check wc -w ≤4,500 before adding text
[cold-read-and-adversarial-review-catch-different-failures](cold-read-and-adversarial-review-catch-different-failures.md) — A fresh-context cold-read verifies a reader UNDERSTANDS a rule; an adversarial whole-branch review verifies the rule is ROBUST against a reader trying to exploit it — these are different failure classes and one does not substitute for the other on exemption/gate-mechanism changes
[core-rule-removal-needs-plugin-wide-sweep](core-rule-removal-needs-plugin-wide-sweep.md) — A load-bearing rule (e.g. writing-plans' task-sizing criterion) gets quoted/paraphrased across far more files than the one defining it — router cards, agent contracts, sibling READMEs in every shipped language, living design docs — grep the whole plugin, not just the defining skill file, before considering a removal complete
[count-only-regression-pins-false-confidence](count-only-regression-pins-false-confidence.md) — Regression tests that pin only element COUNTS can be coincidentally satisfied by the pre-change (broken) state — pin at least one exemplar value per collection plus a shape assertion that the known-bad form violates, and verify each parametrized case individually went RED
[cross-module-field-contracts-execute-probes](cross-module-field-contracts-execute-probes.md) — In build-assembled programs, cross-module field contracts are the systemic risk — review by concatenating the modules and executing behavioral probes, not by grep
[dogfood-evidence-anchors-shipped-commit](dogfood-evidence-anchors-shipped-commit.md) — A dogfood behavioral PASS certifies only the commit it ran against — post-dogfood remediation ships unexercised unless the probes re-run at the remediated text, and reports must anchor on-branch SHAs (pre-squash SHAs dangle)
[dont-finish-flag-definitions-rename](dont-finish-flag-definitions-rename.md) — The "Flag Definitions" heading in domain-teams rubrics is a deliberate convention — do not sweep it into the loom-code flags→findings rename
[dont-fix-guards-jtbd-isbn-and-5axis-names](dont-fix-guards-jtbd-isbn-and-5axis-names.md) — Don't-fix guards — the JTBD 1997 ISBN 978-0875845852 in four-dx-coach is CORRECT (Innovator's Dilemma context, not Competing Against Luck), and the 5-axis long/short names in loom-code brainstorming (Alternatives vs Alternatives Considered) are deliberate description-vs-body usage, not drift
[equivalence-test-prompts-must-satisfy-target-intake-contract](equivalence-test-prompts-must-satisfy-target-intake-contract.md) — A behavioral-equivalence test prompt that violates the target skill's own input contract cannot arbitrate equivalence — it produced a false 3/3 not_equivalent verdict (baseline/candidate each picked different defensible readings of the invalid input); validate prompts against the skill's intake contract first, and confirm any single-run divergence with n≥2 replicates per side before believing it
[eval-oracle-tokens-stable-fragments](eval-oracle-tokens-stable-fragments.md) — Substring-matched eval-oracle tokens must be the shortest distinctive stable fragment (surname / product name) with |-alternatives for alias-language-case variance — full names break on translation, spacing, word order; and a miss's class (form vs genuine drop) must be re-derived per run, never carried over from an earlier run
[execute-cheap-loom-simplify-upgrades-at-review](execute-cheap-loom-simplify-upgrades-at-review.md) — When a LOOM-SIMPLIFY marker's recorded upgrade turns out one-line-cheap at review time, execute it on the spot instead of leaving the marker
[file-carrier-for-bulk-payloads](file-carrier-for-bulk-payloads.md) — Bulk data between agent-skill pipeline stages must travel by file path, never as inline JSON in a command or one giant response — a large single response is a reproducible mid-response 5xx killer (proven live 2026-07-07, 2/2 inline failures, success after file hand-off)
[fixtures-mirror-producer-shape](fixtures-mirror-producer-shape.md) — Test fixtures must mirror the producer's actual field shape — a hand-shaped fixture can certify code that fails on the real producer's output
[gate-review-weight-on-task-kind-not-loc](gate-review-weight-on-task-kind-not-loc.md) — When deciding how much review a change deserves, gate on task KIND (mechanical/prose/version-bump vs logic/heuristic/hook/security-surface), never on diff LOC size — LOC is a weak, sometimes wrong proxy
[git-mv-sweeps-untracked-files](git-mv-sweeps-untracked-files.md) — git mv of a directory physically relocates UNTRACKED files too — a later git add of the new dir sweeps WIP into the commit; unstage by status A via git diff --cached --name-status
[github-squash-merge-single-commit-drops-body](github-squash-merge-single-commit-drops-body.md) — GitHub's default squash-merge message for a single-commit PR keeps only the PR/commit title — the full body (including git-memory Decision/Learning/Gotcha trailers) is silently dropped from main's git history; a multi-commit PR concatenates all bodies instead
[grep-tests-scope-to-measured-neighborhood](grep-tests-scope-to-measured-neighborhood.md) — Whole-file substring grep-tests over prose files go false-green when the asserted phrase pre-exists elsewhere in the file — scope assertions to a measured window around the feature's anchor string and verify RED against the pre-change content
[headless-branch-plugin-testing-recipe](headless-branch-plugin-testing-recipe.md) — Recipe for behaviorally testing an unpushed branch's Claude Code plugins headlessly — --plugin-dir wrapper, neutral empty cwd, probe hook injection first, parse_corpus takes content
[imperative-trigger-cards-beat-descriptive-preloads](imperative-trigger-cards-beat-descriptive-preloads.md) — Preloading a rule into session context fixes "rule never read", NOT "rule read but not obeyed" — weak models act on short imperative action-moment cards ("before typing X → invoke Y FIRST", 2/2 flip) while descriptive discipline prose provably in context moved behavior 0/2; phrase always-loaded cards as imperatives anchored to the acting moment
[interactive-fixups-still-route-through-implementer](interactive-fixups-still-route-through-implementer.md) — In interactive fix-up rounds outside an SDD dispatch, reviewer findings must still be routed through an implementer dispatch — the main agent fixing them by direct edit is the recorded test-skipping leak path
[migration-acceptance-greps-scope-by-content-not-filetype](migration-acceptance-greps-scope-by-content-not-filetype.md) — A migration task's acceptance grep scoped by file type (SKILL.md/README only) leaves .py/.yml/schema-doc consumers of the migrated names unscanned — sweep by content pattern repo-wide and justify carve-outs, or the blind spot ships
[parallel-wave-commit-discipline](parallel-wave-commit-discipline.md) — Parallel subagent waves share one git index — commit orchestrator-serially with explicit pathspecs (never git add -A, never plain git commit), verify with git show --stat HEAD
[per-task-review-misses-duplicated-fallback-fix](per-task-review-misses-duplicated-fallback-fix.md) — A fix at one location that shares a contract with other locations (code call-sites reading a data shape, OR a doc section's promise and its downstream enforcing check) can PASS individual per-task review while the sibling locations stay unfixed — only whole-branch cross-task-coherence review catches the gap
[pipeline-enforced-gates-beat-drafter-instructions](pipeline-enforced-gates-beat-drafter-instructions.md) — When a weak-model drafter keeps violating a coverage obligation despite prose instructions, move enforcement into the PIPELINE (harness runs a deterministic checker, verbatim miss list feeds one bounded fix round) — measured 22%→67% pass-rate with the dominant failure class displaced to input-side extraction quality, after three prose-hardening proposals had been mechanically rejected as no-ops
[preamble-wording-is-contract-surface](preamble-wording-is-contract-surface.md) — In prompt-artifact work, a station preamble's vocabulary steers downstream machine classification — treat preamble word choice like an API field name
[process-mechanism-dogfood-via-coldreader-real-commits](process-mechanism-dogfood-via-coldreader-real-commits.md) — To dogfood a shipped process RULE (not a whole skill's triggering/output), give a fresh context-blind agent ONLY the rule text + real sandbox git commits (not fabricated data) and ask it to decide+execute each branch — cheaper than a full nested-subagent live run, still catches real misuse
[python-path-parent-resolve-gotcha](python-path-parent-resolve-gotcha.md) — Python pathlib — Path(".").parent is still ".", so resolve() before any parent-directory lookup on a relative path
[re-multiline-whitespace-captures-across-lines](re-multiline-whitespace-captures-across-lines.md) — Python re — \s* matches newlines even under re.M, so an empty-valued key swallows the next line and chains wrong-field parses; use [ \t]* or anchor the value
[retire-numbered-checks-dont-renumber](retire-numbered-checks-dont-renumber.md) — When a numbered check/criterion is dropped but other files cross-reference it by number, retire it in place (mark permanently N/A) rather than renumber — renumbering cascades edits into every file citing a specific number
[reviewer-dispatch-isolated-worktree](reviewer-dispatch-isolated-worktree.md) — A reviewer subagent comparing commits can overwrite tracked files in the main checkout — dispatch prompts must explicitly order an isolated scratch dir or detached worktree
[reviewers-rerun-mutations-before-accepting-fix](reviewers-rerun-mutations-before-accepting-fix.md) — Reviewers should re-run the breaking mutation themselves (e.g. delete the guard in scratch and watch the test fail) before accepting a fix claim
[shared-classifier-over-open-dialects-needs-allowlist](shared-classifier-over-open-dialects-needs-allowlist.md) — A predicate shared across N producers that each emit their own error/metadata dialect must decide by a POSITIVE allowlist of what counts as real data, never a denylist of known error keys — a denylist silently fails toward the dangerous direction the moment an unsampled producer adds a key you did not list
[skill-triggering-diagnose-listing-before-text](skill-triggering-diagnose-listing-before-text.md) — Skill under-firing recipe — diagnose the live listing first (host evicts least-used descriptions over the ~1% budget), fix with an entry router + repositioned descriptions (routers survive eviction; CJK keyword stuffing is A/B-refuted), measure with a corpus A/B on the firing harness
[snippet-stats-need-primary-source-check](snippet-stats-need-primary-source-check.md) — A web-search snippet paraphrasing a statistic needs a primary-source check before citing — a different-agent reviewer with web access catches what the generator's shared priors miss
[stamp-changelog-test-counts-at-closeout](stamp-changelog-test-counts-at-closeout.md) — CHANGELOG test counts go stale during multi-round review fix-ups — stamp the number with pytest --collect-only at branch close-out, not mid-branch
[static-text-pins-blind-to-courier-runtime-holes](static-text-pins-blind-to-courier-runtime-holes.md) — Static text-pin tests on Workflow JS are structurally blind to runtime security holes in courier surfaces — a green 240+-test suite coexisted with a live path-traversal bypass and a dcg-blocked revert command; security-critical courier code needs an adversarial reviewer that EXECUTES probes (standalone node eval, in-repo guard-doc grep), plus an executable pin mirroring the repro once fixed
[test-except-branches-explicitly](test-except-branches-explicitly.md) — A green suite can hide a crash in an except branch with zero coverage — e.g. catching tokenize.TokenizeError, which is not a real stdlib name (it's TokenError)
[untracked-replacement-while-deletion-staged](untracked-replacement-while-deletion-staged.md) — During a file relocation, a replacement created with Write stays UNTRACKED while the deletion of the file it replaces is already staged — committing the index as-is ships the deletion without the replacement, and git diff cannot reveal it because untracked files never appear in a diff
[verify-agent-mechanisms-on-disk-not-self-report](verify-agent-mechanisms-on-disk-not-self-report.md) — Behavioral verification of agent-facing mechanisms on cheap model tiers — real-session drive with unique markers, disk-verified effects, transcript grep for output fingerprints, per-verb cold-reader agents, two consecutive clean rounds; never accept the model's self-report as the oracle
[workflow-agent-results-and-courier-args-need-guards](workflow-agent-results-and-courier-args-need-guards.md) — Workflow scripts — every agent() result can be null (skip/terminal error) and must degrade to a failed item; agent() can also THROW (schema-forced output failure), and a sync try/catch around a RETURNED promise cannot catch its rejection — the stage must be async with await inside the try; any operator arg interpolated into a courier agent's Bash instruction text needs a per-segment character allow-list; and the allow-list MUST explicitly reject '.'/'..' segments — the character class ^[A-Za-z0-9._-]+$ admits them (traversal found live TWICE: improve-loop T4 and the matrix guard it was never back-ported to)
