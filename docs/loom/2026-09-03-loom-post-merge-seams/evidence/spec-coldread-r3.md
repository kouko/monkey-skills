# Cold read — spec v4, round 3 (2026-09-03-loom-post-merge-seams)

## Acceptance 1 — close-before-merge order
Try: clean clone, follow ship order (push → gh pr create → commit
`status: closed <date> — PR #<N>` → review-only commit → push again);
also confirm 2026-09-02-simple-loom-flow's intent gets closed in this
diff; then run `loom_checker.py intake write-plan` on the closed intent.
Expect: second push passes on unchanged rules (no `!`); intake blocks
with the exact `intake.confirmed: … closed (PR #<N>) …` string (REQ-1).
Enough? Yes — commit order, message text, and file are all literal.
Guess G1: spec doesn't give the actual merged PR number for
2026-09-02-simple-loom-flow's own close line — must be looked up
(`gh pr list`/CHANGELOG), not a spec defect, just an execution step.

## Acceptance 2 — grammar + green tests
Try: `--list-rules | grep closed`; run the two package commands (local +
CI job at .github/workflows/loom-code-ci.yml:114 — verified exact).
Expect: both green, closed appears under intake.confirmed.
Enough? Yes, both commands are given verbatim.

## Acceptance 3 — plumbing exemption, changed this round
Try: (a) rerun `codex_scaffold.py --repo .` untouched, commit, no
`Task:` trailer → push passes. (b) alter one byte under `.codex/hooks/`
(or add a file), commit → same rule blocks.
Expect per REQ-3's canonical-comparison design (Path(__file__).resolve()
test, blob-equality against the source tree).
Enough? Yes once re-read carefully — this repo IS its own canonical
(loom-code/scripts/ vs the .codex/hooks/ copy), so no plugin-cache
setup is needed for the positive case despite the "Claude Code 這一側"
phrasing sounding like it needs one. Resolved by REQ-3's own text, not
a guess — flagging only because it took a second pass.

## Acceptance 4 — checkpoint cost table
Try: open docs/loom/2026-09-03-loom-post-merge-seams/evidence/checkpoint-cost.md
after the change lands; check per-checkpoint commits/dispatches/rounds +
`git rev-list --count` + one recommendation line, vs #771's 34/31.
Enough? Yes, path and content are literal (REQ-4); written by the
blind-runner per Design decision, so I'd be producing this file myself
at branch end, not just checking it.

## Acceptance 5 — plugin versions
Try: after `claude plugin update`, check plugin.json versions
(1.0.1/1.0.1/4.0.1) and run the cached `loom_checker.py --list-rules`.
Enough? Yes, versions and path pattern are literal (REQ-5).

## Acceptance 6 — five nits, promoted this round
Try: diff each anchor after the change — loom_checker.py:455 (docstring
"below"→"above"), test_check_mechanisms.py:664/670/672 (check=True,
literal 5, wc-spawn guard via inspect.getsource), test_session_start_words.py:49
(_run decodes bytes with errors="replace") — then run the package command.
Enough? Yes — Design decision names the exact file+fix per nit; I
verified all five anchors exist at the stated lines (spot-checked below).

## Anchor spot-check (all resolved, none broken)
ship/SKILL.md:326-336, loom_checker.py:1557/791/825-835/389-400/455/2085/2095,
test_loom_checker_intake.py:385-447, manifest.yaml:85, templates/intent.md:7,
codex_scaffold.py (SHIM_TEMPLATE/_checker_copy_content/CONTRACT_COPY),
test_check_mechanisms.py:664/670/672, test_session_start_words.py:49,
.github/workflows/loom-code-ci.yml:114 — all exist and match what the
spec says is there today (note: ship SKILL.md still shows the OLD
post-merge close order, which is correct — that's the "before" state
REQ-1 will rewrite, not a stale citation).

## Guess count: 1
G1 — PR number for closing the prior change's intent is a lookup, not
in the spec; everything else traces to a literal string, path, or line.

## Verdict
Spec v4 is executable without meaningful guessing; the one open item
(G1) is a data lookup, not an ambiguity, so nothing here blocks build.
