# `capture-intent` real-session audit

- **Date:** 2026-09-12
- **Repository snapshot:** `3f8ed28080d3a41be95a42d17f0106a57b64bbe2`
- **Target:** `loom-design:capture-intent`
- **Mode:** local transcript mining plus user-approved external analysis
- **Production changes:** none

## Question

Does real `capture-intent` use show that the station asks too few questions,
and does that justify replacing its interview with grilling?

## Population and limits

The local deterministic miner found eight qualifying sessions, not the planned
10–15. It emitted nine analysis trajectories because one high-friction session
had both failure and success views.

Five trajectories were above the miner's one-million-token admission limit and
were skipped. Three more were below the miner's rough estimate but Claude Code
rejected them after accounting for runner system and tool context. One complete
trajectory ran successfully. No transcript was truncated.

The miner also supplied a nonexistent target path and an empty
`target_skill_md_content` value. The one external result therefore did not
receive the target contract through its declared input, even though the session
events themselves included a loaded copy. It is degraded single-session
evidence and cannot support a generated cross-session proposal.

## Deterministic observation

For each unique session, the audit located the `capture-intent` invocation and
the first subsequent tool call that wrote under `docs/loom/intent/`. It then
counted non-tool assistant messages containing a question mark before that
write.

| Session | User-facing question messages before first intent write |
|---|---:|
| `50cdbb50-dd27-4a6b-9ff2-6bf6dc4c9206` | 0 |
| `53fa9fd9-1e9f-4469-9dc4-d27dbd232767` | 0 |
| `9394655d-4917-441f-af10-33c73e42aab6` | 0 |
| `a3ef9505-ef2a-4404-9a08-591052bff074` | 1 message containing 2 questions |
| `a577fc38-31aa-4a67-b47a-5fba9e33916c` | 0 |
| `eb96f6ca-ecaf-4959-8558-75f1ce5f470b` | 0 |
| `f14c84f2-522e-46bf-aa65-553a2642d167` | 0 |
| `f513c7aa-2f0a-4ef6-b372-c90d3aad24e7` | 0 |

This confirms that the observed station did not execute the then-documented
engineering four-to-six or product eight-to-ten interview counts literally.
The pre-change contract at `25a3b935e:loom-design/skills/capture-intent/SKILL.md`
carried both the fixed counts and the instruction to stop when the five fields
could be filled without guessing; this change removes the counts.

## Interpretation

The result does **not** prove that seven sessions were under-interviewed. In
most sampled sessions, `capture-intent` was invoked after substantial research,
discussion, or an explicit user instruction such as “open an intent for these
five items.” Reusing already supplied answers is correct and cheaper than
asking a quota of duplicate questions.

One session does show the target failure shape directly. A prior artifact had
described memory as independently installable and later labeled the
standalone-plugin fork `user-decided`, but the transcript available to the
agent could not establish that the fork had been asked. The user subsequently
clarified that memory belonged inside the `loom-workflow` toolbox, requiring a
new intent to undo the shipped shape. This is evidence for distinguishing an
explicit user decision from an agent inference before confirmation; it is not
evidence that every branch of a grilling decision tree should be explored.

The single degraded external analysis found a different issue: one engineering
intent converted a rough performance estimate into a precise Acceptance bound,
which later caused renegotiation and another review round. It also proposed an
engineering cost/benefit gate and a contract-volatility check. Each item has
only one-session support, and the missing target skill input weakens its
attribution. None should modify `capture-intent` from this run.

## Finding classification

| Candidate explanation | Evidence | Status |
|---|---|---|
| `capture-intent` usually asks fewer questions than its numeric prose says | 7/8 had zero pre-write question messages; 1/8 had one | supported for this sample |
| fewer questions are inherently a defect | most invocations followed detailed prior context | not supported |
| an unasked decision can be inferred and mislabeled as user-decided | one directly observed correction and replacement intent | supported once; needs recurrence |
| `write-spec` is the main source of expansion | this sample targeted `capture-intent`, not downstream semantic diffs | not tested |
| full grilling would prevent the observed problem at acceptable cost | no real session executed full grilling | not supported |

## Recommendation

Do not replace the interview with full grilling. Do not enforce minimum
question counts. The smallest evidence-backed next candidate is a confirmation
rule:

> Before calling a fork `user-decided`, state the two materially different
> outcomes in plain language and obtain an explicit answer. Information merely
> present in an accepted restatement is not evidence that the fork itself was
> asked.

This candidate should be tested only on cases containing a consequential fork
and on detailed cases containing none. It needs no decision-tree artifact,
question ID, checker rule, new station, or reviewer loop.

## Evidence identity

Raw transcripts remain in their host stores. Run-local normalized payloads and
external outputs were retained under `/private/tmp` and identified here:

| File | SHA-256 |
|---|---|
| `capture-intent-top.json` | `71989a02783acac703448dc664babeed99c508c5a7d7469000de7f08120ebafe` |
| `capture-intent-analysis-2.md` | `372e683305e34752032e364c2549239792ee0c2306a35916364b35cee3ab8a8c` |
| `capture-intent-analysis-3.md` | `c070b28d1b0bc64212297b28c4bb7e84cdec89a69660eb70b057d0f755fcd3dc` |
| `capture-intent-analysis-5.md` | `0b23bb13f688e5ba71f9025c853516e9a99598977db2b22ee1443c486c371b34` |
| `capture-intent-analysis-8.md` | `44b8119d27390e0ef62dff66f03a3dca79005c78b189840923d2eb3b1e36b3c1` |

The three 295-byte analysis files record Claude Code's context-limit refusal;
only `capture-intent-analysis-5.md` contains an analyst response. Subscription
execution did not expose a monetary charge, so actual cost is unknown rather
than zero.
