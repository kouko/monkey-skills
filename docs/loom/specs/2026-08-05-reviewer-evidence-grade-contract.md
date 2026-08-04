# Brief: reviewer evidence-grade contract (D-B-plus)

Date: 2026-08-05
Source: D-B decision discussion (2026-08-04/05 session) — user ratified
"D-B-plus 依照你的建議"; option A (contract carve-out) + purpose anchor +
packet-interface rule, docs-reviewer narrow. E-1(b) is a SEPARATE
follow-on arc, not this one.
Status: FROZEN.

## Problem

The four reviewer agent contracts forbid running tests while dispatch
packets and the dispatch institution (model-dispatch §5, verify ≠
self-verify) instruct reviewers to run them. Live evidence both ways in
one session: per-task reviewers who obeyed packets produced the arc's
best finding (mutation-proved missing coverage) and caught a red tip
self-report missed; whole-branch arms who obeyed the contract refused to
run and downgraded via R3. Same mechanism, coin-flip behavior.

Archaeology (verified via git log -S): the prohibition was born in PR
#301 (v0.7.0, four plugin-level agents) with only an economy/role-purity
rationale ("implementer's test_results is the test record"); PR #465
added R3 as an honesty patch ON TOP of the prohibition ("since you can't
run, don't pretend you verified") — its own PR body records reviewers
independently re-running suites. The prohibition never faced the
"self-report can be wrong" evidence; that evidence now exists twice.

## Scope correction (forced, reported to user in-session)

spec-reviewer joins the carve-out: R3 lives in the distribute.py-managed
SSOT (`loom-code/scripts/_reviewer-discipline.md:37`) shared by ALL FOUR
agents, so the R3 rewrite reaches spec-reviewer regardless; leaving its
per-file prohibition intact would recreate the falsified-neighbor seam
(`docs/loom/memory/a-rule-edit-falsifies-the-unchanged-prose-composed-with-it.md`)
inside its own contract. Practice already matches: this session's
spec-reviewers ran suites read-only in every task where the packet
allowed it.

## Decisions (user-ratified)

1. **Carve-out, not convention (option A).** Code-side contracts
   (code-quality-reviewer, code-reviewer) and spec-reviewer replace the
   per-file prohibition with a READ-ONLY test-running permission:
   preferred over trusting reported `test_results`; mutation/RED probes
   only on extracted copies or isolated worktrees with zero residual
   diff verified; evidence-gathering, never a substitute for reading.
   docs-reviewer gets the NARROW form: prose has no suite, but when
   `### Read context` includes code whose claims cite tests, running
   that suite read-only is permitted.
2. **R3 rewritten at the SSOT** from an absolute premise ("You may not
   run tests;") to a conditional fallback ("When you could not run the
   relevant check yourself…"), keeping the honest-downgrade duty intact
   verbatim in spirit; regenerated into all four contracts via
   `python3 loom-code/scripts/distribute.py`.
3. **Purpose anchor** added to each contract's role preamble: the
   reviewer's product is an evidence-grade verdict — prefer independent
   execution over reported results and experiments over static
   suspicion; reading the artifact is the foundation, tools only
   corroborate it.
4. **Packet-interface rule** added to each contract's input contract:
   a dispatch packet may carry an attention list; it only ADDS focus,
   never narrows the dimension set, never pre-judges a conclusion.
   (Codifies the currently unwritten "Scrutinize:" practice on the
   receiving side, where files are not word-capped.)
5. **Out of constitutional scope**: verdict vocabularies, dimension
   sets, writer≠judge separation, may-not-edit and may-not-dispatch
   rules — all unchanged.
6. **Verification**: agent-contract edits do not reach this session's
   subagents (recorded gotcha) — merge-gating behavioral verification
   uses by-path probes (dispatch an agent with the EDITED contract file
   path as its role prompt, per the 0490 arc's dogfood method), covering:
   carve-out fires (a probe reviewer runs the suite unprompted-by-packet),
   purpose anchor does not cause read-skipping, attention-list rule
   rejects a narrowing packet, docs-reviewer narrow gate.
7. loom-code plugin bump 0.52.0 → 0.53.0, four deliverables (manifest,
   codex sync, CHANGELOG, shipping-version pin test), suite green
   post-commit.

## Smallest End State

1. `scripts/_reviewer-discipline.md` R3 in conditional-fallback form;
   distribute.py run; all four agents' managed blocks byte-identical to
   SSOT (verify-drift clean).
2. Four agent contracts carry: adapted carve-out, purpose anchor,
   packet-interface rule; zero copies of the absolute prohibition
   remain operative (claim sweep: the 4 per-file copies + 1 SSOT copy
   all updated; the HANDOFF copy is gitignored history).
3. Prose-pin pytests in `loom-code/scripts/` for the new wording.
4. By-path probe record at `docs/loom/dogfood/` with all probes CLEAN.
5. 0.53.0 shipped with the four bump deliverables; full suite green.

## Out of scope

- E-1(b) extraction pilot (next arc).
- Any SKILL.md edit (word-capped files untouched — this design
  deliberately keeps every edit in uncapped agent/SSOT files).
- Third-layer dispatch-side regulation beyond what the receiving
  contracts state.
- model-dispatch.md (user dotfiles institution) — already consistent
  with option A; no edit needed.
