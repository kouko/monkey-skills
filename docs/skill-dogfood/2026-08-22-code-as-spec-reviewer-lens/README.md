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

**Deployed run (2026-08-22, after merge).** Two more arms, same sandbox, same
model, dispatched as the registered `loom-code:code-reviewer` agent type against
a real two-commit git repo rather than as general-purpose agents holding a file.
Until `plugin update` landed, the earlier arms could only test the contract
text; nothing had tested that a dispatched, registered reviewer receives it.

Materials: `sandbox/` here. Transcripts: `transcripts/`.

---

## Results

| Planted | OLD 1 | OLD 2 | NEW 1 | NEW 2 | DEPLOYED 1 | DEPLOYED 2 | BARRED 1 | BARRED 2 |
|---|---|---|---|---|---|---|---|---|
| a — pure restatement | ✗ | ✗ | ✗ | 🟡 | ✗ | 🟡 | 🟡 | ✗ |
| b — false claim | 🟡 exec | 🟡 exec | 🔴 exec | 🔴 exec | 🔴 exec | 🔴 exec | 🔴 exec | 🔴 exec |
| c — absence claim | kept | kept | kept | kept | kept | kept | kept | kept |
| d — mechanism + reason | ✗ | ✗ | 🟡 split | 🟡 split | ✗ | 🟡 split | 🟡 split | 🟡 split |
| e — stranded / dead branch | 🟡 | 🟢 | 🔴 | 🔴 | 🔴 | 🟡 | 🔴 | 🟡 |
| f — control | none | none | none | none | none | none | **🟡 FALSE POSITIVE** | none |
| `deletion-first` scored | — | — | — | — | **PASS, "no-op"** | PASS_WITH_NOTES | NEEDS_REVISION | NEEDS_REVISION |
| tool calls | 10 | 7 | 5 | 6 | 21 | 8 | 7 | 7 |

BARRED 1 and 2 hold the contract carrying the no-op bar shipped by
`docs/loom/plans/2026-08-22-code-as-spec-lens-no-op-bar.md`. Same sandbox,
same blind framing, same model as every prior arm.

An unplanted defect surfaced: `retry_budget`'s guard against negative values is unreachable, because the module's own regex captures `\d+` and never matches a sign. All eight arms found it by execution. It was not planted; the sandbox author did not notice it.

---

## What is settled

**The execution duty works in both directions — measured, 6/6 arms plus 1 rerun.**
Every false claim in this exercise was caught by running something. None was caught by reading. The reverse also held once: an OLD-arm reviewer *wrongly flagged a true sentence* by reading it, while a NEW-arm reviewer executed the same sentence, confirmed it true, and stayed silent. The duty raises catch rate and lowers false-positive rate.

**Severity moved, and that is a merge-gate difference — measured.**
The same defect scored 🟡/🟢 under the old contract and 🔴 under the new one, because the new text ties severity to consequence ("a caller acting on this sentence would do the wrong thing"). Under this repo's aggregation rule that is the difference between "should fix" and "does not merge".

**No over-firing held for seven arms, then broke on the eighth — and the eighth is the one carrying the no-op bar.**
The control drew no finding from OLD, NEW, or DEPLOYED arms, and both NEW arms named the rule that excluded it rather than passing it over silently. BARRED 1 flagged it: it read "This module stays deliberately tolerant of a malformed header" as a mechanism the code shows, and filed it 🟡. The lens's own carve-out says an absence claim is never deletable, and deliberate tolerance is deliberate non-behaviour — so this is a false positive against the rule's own text, not merely against the sandbox's answer key. One sample. But the direction is the one a bar of this shape would be predicted to produce: removing the option to find nothing pushes toward finding something.

**Cost did not rise — measured, small.**
5–6 tool calls under the new contract against 7–10 under the old. This measures calls, not reading burden; on a large branch the run-what-survives duty is an unmeasured ongoing cost. The deployed arms spread wider (8 and 21), and the 21-call arm is the one that found *fewer* defects — call count does not track catch rate here.

**Deployment carries the contract — measured, 2/2, and this is what the deployed run was for.**
The dispatched agents receive the reviewer contract in their *injected system prompt*, not by reading a file: one arm reported it "was already present in my system prompt when the task began" and quoted role-contract item 7 back verbatim, including "can the code show this? When it can, flag it for deletion". That sentence occurs 1× in 0.93.0's `agents/code-reviewer.md` and 0× in 0.92.0's. The other arm named `~/.claude/plugins/cache/monkey-skills/loom-code/0.93.0` as its standards source. Both stamped `standards_version: "0.93.0"`. `plugin update` is therefore the operative step — a merged contract that has not been deployed is not in force for any dispatch.

**The no-op bar closed the route it targeted — measured, 2/2, single run.**
Both barred arms scored `deletion-first: NEEDS_REVISION`. Neither declared the dimension not applicable, a no-op, or out of scope, and neither produced a zero on the deletion class — the two failure shapes that motivated the bar. The prior deployed arm's exact move (score PASS, list the dimension among "no-ops for this branch") did not recur.

What this does NOT establish: that the bar caused it. n=2 against a bimodal baseline where 2 of 5 prior samples were zeros; two clean draws are unsurprising even from an unchanged contract. The claim that survives is narrower — the specific declaration the bar forbids did not appear, and the dimension was evaluated in both runs.

## What is NOT settled

**Surplus-class detection is unstable — this reverses the first reading.**
The four-arm run showed 3/4 on the deletion class (a and d) against a baseline of 0/4, and that was reported as the lens's headline new capability. A later independent rerun of one NEW arm filed **zero** deletion findings: it used the lens's own carve-outs — "the reason must survive", "an absence claim is never deletable" — to exempt every surplus sentence, including the pure restatement. The deployed run split the same way: same contract, same model, same diff, one arm caught both surplus plants and the other caught neither and scored `deletion-first: PASS`, calling it "a no-op for this branch".

Seven samples of the deletion class now read `1/2, 2/2, 0/2, 0/2, 2/2`, then `2/2, 1/2` under the no-op bar. The direction is unchallenged — the baseline is structurally blind to this class, 0/4. The magnitude is not merely unestablished; the spread is bimodal — no arm has ever produced a partial catch except once. Runs are 0/2 or 2/2, so the mean describes nothing that happens.

**The two zeros were reached by different routes, and this was initially reported as one.** The rerun arm invoked the carve-outs explicitly and spared every surplus sentence with them. Deployed arm 1 never invoked either carve-out: it took each surplus sentence as a *truth* claim, executed it, found it true, and closed it, then listed `deletion-first` among the dimensions that are "no-ops for this branch". That is the lens's own two halves competing for one sentence — the run-what-survives duty is more salient than the delete-what-is-surplus duty, and it consumes the sentence first.

So there are two candidate defects in the rule text, not one: an exemption that can be adopted wholesale, and an ordering that lets the execution half absorb sentences the deletion half was supposed to see. Neither is settled as *the* cause; both are visible in transcripts. More sampling settles neither.

**Nothing here bears on Checker 1.** Checker 1 — "a load-bearing superlative must carry a pin" — was dropped as judgment-heavy. This exercise was used to argue that drop was weakly grounded. It does not: only one of the six planted defects contains any of Checker 1's trigger words, and the exercise measures mechanism-versus-intent classification, not load-bearing-versus-decorative. The drop stands on its original grounds. Recorded because the argument was made and is wrong.

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
3. **Fix the carve-out escape, or accept the class as coin-flip.** The deployed run added two samples and the split widened rather than converged (see §What is NOT settled). More samples will not settle a bimodal split — the next useful move is to change the rule text so an exemption cannot swallow the whole class, then re-measure. A weak-model arm is still unrun and is a separate question.
4. **Wire `check_doc_citations.py` into CI** as cheap hardening. Not a headline: the brief records that it would have caught none of the source arc's eight defects.
