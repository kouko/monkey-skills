# Code-as-spec reviewer lens — blind dogfood + two assessments

**Date**: 2026-08-22
**Subject**: the reviewer lens shipped by `code-as-spec-writing-rule` (PR #722), in `loom-code/agents/code-reviewer.md` and `loom-code/agents/docs-reviewer.md`
**Why**: the lens was the only deliverable on that branch never executed. Every prior check asked whether the rule read correctly; none asked whether a reviewer holding it behaves differently.

Read the verdict table first, then §What is settled. Every row is tagged with how it was established — measured, single-sample, or reasoned — because two of the conclusions below reverse an earlier reading of the same data.

---

## Design

Six defects planted in one 42-line Python module, reviewed blind. Neither arm was told a defect count, a location, or that it was being measured — each was told only "the author added docstrings, review the diff".

| # | Planted | Correct behaviour |
|---|---|---|
| a | A docstring sentence restating the two-line function body, carrying no reason | Flag for deletion |
| b | A restatement that is **false** — claims a disagreeing `label` surfaces under the filename stem | Execute it, file as wrong (not surplus) |
| c | An absence claim: "this parser never validates a value it extracts, by design" | **Keep** — code cannot show deliberate non-behaviour |
| d | Mechanism and its reason in one sentence | Split; the reason survives |
| e | A qualifier whose summary sentence was removed | Flag the stranding |
| f | **Control** — pure intent, no produceable outcome | **No finding** |

`b` is a reconstruction of the real defect this branch shipped and then fixed at `c625ce39` — same `.get(key, default)` shape, same confusion of *absent* with *disagreeing*.

Arms: two reviewers on the branch's contract, two on `main`'s, all `sonnet`, all general-purpose agents handed the contract file as their role prompt.

Materials: `sandbox/` here. Transcripts: `transcripts/`.

---

## Results

| Planted | OLD 1 | OLD 2 | NEW 1 | NEW 2 |
|---|---|---|---|---|
| a — pure restatement | ✗ | ✗ | ✗ | 🟡 whole-sentence delete |
| b — false claim | 🟡 executed | 🟡 executed | 🔴 executed | 🔴 executed |
| c — absence claim | kept | kept | kept | kept |
| d — mechanism + reason | ✗ | ✗ | 🟡 split | 🟡 split |
| e — stranded / dead branch | 🟡 | 🟢 | 🔴 | 🔴 |
| f — control | no finding | no finding | no finding | no finding |
| tool calls | 10 | 7 | 5 | 6 |

An unplanted defect surfaced: `retry_budget`'s guard against negative values is unreachable, because the module's own regex captures `\d+` and never matches a sign. All four arms found it by execution. It was not planted; the sandbox author did not notice it.

---

## What is settled

**The execution duty works in both directions — measured, 4/4 plus 2 reruns.**
Every false claim in this exercise was caught by running something. None was caught by reading. The reverse also held once: an OLD-arm reviewer *wrongly flagged a true sentence* by reading it, while a NEW-arm reviewer executed the same sentence, confirmed it true, and stayed silent. The duty raises catch rate and lowers false-positive rate.

**Severity moved, and that is a merge-gate difference — measured.**
The same defect scored 🟡/🟢 under the old contract and 🔴 under the new one, because the new text ties severity to consequence ("a caller acting on this sentence would do the wrong thing"). Under this repo's aggregation rule that is the difference between "should fix" and "does not merge".

**No over-firing — measured, 4/4 plus reruns.**
The control drew no finding from any arm, and both NEW arms named the rule that excluded it rather than passing it over silently.

**Cost did not rise — measured, small.**
5–6 tool calls under the new contract against 7–10 under the old. This measures calls, not reading burden; on a large branch the run-what-survives duty is an unmeasured ongoing cost.

## What is NOT settled

**Surplus-class detection is unstable — this reverses the first reading.**
The four-arm run showed 3/4 on the deletion class (a and d) against a baseline of 0/4, and that was reported as the lens's headline new capability. A later independent rerun of one NEW arm filed **zero** deletion findings: it used the lens's own carve-outs — "the reason must survive", "an absence claim is never deletable" — to exempt every surplus sentence, including the pure restatement. n=2 against n=1. The direction (baseline is blind to this class) is unchallenged; the magnitude is not established, and the carve-outs are a plausible mechanism for the instability.

**Nothing here bears on Checker 1.** Checker 1 — "a load-bearing superlative must carry a pin" — was dropped as judgment-heavy. This exercise was used to argue that drop was weakly grounded. It does not: only one of the six planted defects contains any of Checker 1's trigger words, and the exercise measures mechanism-versus-intent classification, not load-bearing-versus-decorative. The drop stands on its original grounds. Recorded because the argument was made and is wrong.

**Deployment is untested.** The `loom-code:code-reviewer` agent type resolves from the plugin cache, not the working tree. These arms were general-purpose agents handed the contract file. This tests the contract text; it does not test that a dispatched, registered reviewer receives it. That needs `plugin update` after merge.

**Weak-model behaviour is untested.** All arms ran `sonnet`. The lens's value proposition includes "a reviewer who would not otherwise do this now must" — that claim is about weaker models and was not exercised.

---

## What this says about the arc's stated purpose

The brief's purpose was to stop review rounds being spent on sentences. Three mechanisms shipped, and they do different work:

- **Deleting surplus sentences** (six scripts) is prevention. A sentence that is gone cannot go stale. This is the largest prevention the branch shipped and was initially mis-described as mere cleanup.
- **Pinning a claim to a test** (`EXEMPT_LEAK_COUNT` and the two promoted capability tests) is the strongest prevention available, and reaches two claims.
- **The reviewer lens** is detection, and its jurisdiction excludes record-class documents — plans, briefs, backlog entries — which is where most of this branch's own sentence-level fixes landed. The brief states that gap as accepted debt; it is the sharpest limit on the purpose being met.

## Recommended next, in order

1. **Run the deferred A/B.** It is the prevention layer for skill bodies, and its design — arms, subjects, measure, pre-committed outcomes, and its own scope limit — is recorded at `docs/loom/backlog/2026-08-21-code-as-spec-writing-rule-and-its-deferred-ab.md`.
2. **Extend execution-style verification to record-class documents at close-out**, using the cold-agent pattern in `docs/loom/memory/reading-code-and-running-code-fail-differently.md`, rather than growing reviewer-contract prose further. The lens added roughly 170 lines of judgment-shaped prose to two contracts — the genre this arc distrusts — and shipped without the cold-reader reliability check this repo requires of rule text.
3. **Re-run this dogfood at n≥4 per arm** before treating the surplus-class number as real, and include a weak-model arm.
4. **Wire `check_doc_citations.py` into CI** as cheap hardening. Not a headline: the brief records that it would have caught none of the source arc's eight defects.
