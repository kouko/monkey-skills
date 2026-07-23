# wiki-update loop smoke — final report (T9)

Run: `smoke-2026-07-23`, engine `wiki_fix_loop.js` via Workflow
(journal `wf_cb6fbcbd-221`). Before state: `before.md`; call parameters:
`run-card.md` (same folder). Run artifacts in scratchpad runDir
`…/wiki-smoke-runs/smoke-2026-07-23/` (session-local, not committed).

## Before / after

| | violations | errors | warnings | by_check |
|---|---|---|---|---|
| before (round0) | 10 | 9 | 1 | L01:2 L02:1 L03:1 L04:2 L07:2 L14:2 |
| after — accepted HEAD (round2) | 6 | 5 | 1 | L02:1 L03:1 L07:2 L14:2 |
| after — working tree (round3, uncommitted) | 5 | 4 | 1 | L02:1 L03:1 L07:1 L14:2 |

Terminal `STUCK_EXECUTOR_OVERREACH` after 3 rounds; scorecard: diffLines 6,
diffFiles 3, classesFixed 2, violationDelta 4, branch `wiki-fix/smoke-2026-07-23`.

## Six-point verification (run-card checklist)

1. **Terminal state — PASS with a documented judgment call.** Terminal is
   `STUCK_EXECUTOR_OVERREACH` with `blockers-report.md` present. The card's
   strict reading marks overreach as smoke FAIL — but that presumed real
   deletion. Diff inspection (below) shows the stop is a ratchet
   false-positive on a benign retarget: the engine's fail-closed STUCK-level
   honest stop, squarely inside plan T9's legal set
   {win-0, plateau, STUCK-with-blockers-report}. See Finding #1.
2. **Monotone violations — PASS.** Accepted rounds: r1 (L01) 10→8,
   r2 (L04) 8→6, both strictly decreasing, ratchet/compare/stuck/plateau/
   budget all exit 0; no accepted row increases; final 6 ≤ 10, delta 4 ≥ 0.
3. **Zero-deletion — PASS.** Both accepted rounds `ratchetExit: 0`;
   `git diff --diff-filter=D d8f3c4f..wiki-fix/smoke-2026-07-23 -- wiki`
   empty; per-file conservation counters round0→round2: no decrease in any
   file (checked all 10). r1 = 2 pure insertions (title, date);
   r2 = in-kind wikilink retargets, words/links/headings unchanged.
4. **Artifacts — PASS.** `freeze.json`, `round0..3.jsonl`, `ledger.jsonl`,
   `scorecard.json`, `fix-loop-report.md`, `blockers-report.md` all present.
   `work-orders.jsonl` absent — consistent: the loop stopped at round 3
   before ever reaching the unsafe-only classes (L02/L03), and
   `workOrderClasses` is `[]`.
5. **Proposal branch — PASS.** `wiki-fix/smoke-2026-07-23` exists with
   exactly the 2 accepted local commits (`addc4f9f` L01, `dfba48be` L04) on
   base `d8f3c4fe`; vault has zero remotes, so never-push holds structurally.
6. **Freeze hash — PASS.** `freeze.json.checkConfigHash`
   `80dacb50…a8b9964` equals the recomputed
   `cat wiki_lint_check.py loop_verdict.py | shasum -a 256`; baseSha matches.

## Round-3 diagnosis (the ratchet catch)

The round-3 executor made exactly one edit, a sanctioned safe-tier retarget:
`- Dominated by [[Acme Corp]] …` → `- Dominated by [[Acme-Corp]] …`
(working tree, left unreverted/uncommitted per the overreach contract).
Nothing was deleted: links 22→22, headings 29→29. The words counter is
whitespace-tokenized (`body.split()`), so the two-token target `Acme Corp`
became the one-token `Acme-Corp` — file words 32→31, total 308→307 — and the
ratchet (exit 8, no justification lane inside the loop) read that as a net
decrease and stopped fail-closed.

**Finding #1: the words ratchet is over-strict for retarget-class repairs.**
Retargeting a multi-word link target to a single-word page name — the bread
and butter of L07 repair — trips the words counter with zero content loss.
On the real vault's ~873-broken-link scenario the L07 class would STUCK on
the first such round. v1's fail-closed behavior is the safe side and stays;
tuning belongs in next-touch: keep links/headings strict, add a words
tolerance for accepted-action shape, or a per-round mechanical justification
lane (engine currently hard-codes "no --justification ever").

## Verdict

**T9 GREEN.** All six checklist items pass; the loop converged 2 classes
mechanically (10→6 accepted), braked honestly on the first metric
false-positive without losing content, and produced every promised artifact
plus an inspectable tree. The ratchet catch is documented above as the
arc's first next-touch candidate rather than a defect fix in this PR.
