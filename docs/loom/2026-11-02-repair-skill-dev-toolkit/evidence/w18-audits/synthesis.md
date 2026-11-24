# W18 replay — blind audit synthesis

Two independent fresh-context audits read the frozen sources and the three
replay decision sets; neither saw the other's output, the W17 evidence, or the
grading spec. This file records their conclusions, the one factual
disagreement between them, and the resulting finding. It does not decide
whether the W18 candidate stands.

## Audits

- `audit-a.md` — verdict matrix per candidate per run.
- `audit-b.md` — same scope, independently derived.

## Agreement (both audits, source-grounded)

| Candidate | Runs | Audit A | Audit B |
|---|---|---|---|
| `read-1.json F1` (W17 veto candidate) | three `excluded` | PASS ×3 | PASS ×3 |
| `simulate-1.json F1` | three `confirmed` | PASS ×3 | PASS ×3 |
| `read-1.json F2` `confirmed` direction | — | defect | defect |
| `simulate-1.json F3` `confirmed` direction | — | defect | defect |

On the preregistered veto: **both audits answer no** — the W18 replay did not
reproduce the W17 overbreadth class on F1. Every run excluded the overstated
original and kept the parenthetical (`writing style, prose, design feel`)
inside the creative/non-deterministic category its source assigns.

On the divergence that inverted W17: **both audits call the W18 `confirmed`
disposition of `simulate-1.json F1` correct, not overbroad.** The claim is
narrow (creative/non-deterministic only, explicitly not all prose), and the
entry self-abort text and the ensemble file's :165–166 instruction give
genuinely opposite actions for that class. The W17 exclusion was the weaker
reading, not the W18 confirmation.

On the delegated-scope reading: **both audits agree the `confirmed` direction
for `read-1.json F2` and `simulate-1.json F3` is a semantic defect** — the
replay lifts `multi-judge-ensemble.md:162` "Layer 1 pass = PROCEED" out of the
Q1 Layer 2 scope that the same file declares at :3–4, and treats it as an
overall-verdict override of `SKILL.md:155–165`'s all-three-checks rule.

## Factual disagreement between the audits

Audit B reports `run-3` as `confirmed` for `read-1.json F2` and
`simulate-1.json F3` and rates those two FAIL. The committed files show run-3
decided **`excluded`** for both (verified by reading
`runs/run-3/original/decisions.json`):

| Run | read F2 | simulate F3 |
|---|---|---|
| trial | excluded | excluded |
| run-2 | confirmed | confirmed |
| run-3 | **excluded** | **excluded** |

So audit B's run-3 FAIL ratings rest on a misread status; audit A's run-3 PASS
ratings match the files. The direction analysis the two audits share is
unaffected. Recorded rather than reconciled: two independent readers produced
one fact-set and one misread, and the artifact is the arbiter.

## Finding carried forward

W18 fixes the preregistered W17 failure class (F1: 3/3 clean, both audits),
and its `simulate-1.json F1` confirmation is a genuine conflict both audits
endorse. But **run-2 produced two unsupported confirmations**
(`read-1.json F2`, `simulate-1.json F3`) that both audits independently call a
semantic defect, on candidates the W17 runs had consistently excluded. The
three W18 runs also disagree with each other on those two candidates
(trial/run-3 excluded, run-2 confirmed), where the three W17 runs had been
identical.

That is a new defect surface in the candidate's behavior, not a recurrence of
the preregistered veto class. Whether it fails the W18 candidate, and whether
the caller's existing text should change again, is a decision for the change
owner — this evidence record does not decide it.

## Limits

- Two audits, one fixture, three runs; not accuracy measurement.
- Audit B's run-3 status misread is recorded above and not silently taken as
  majority.
- Neither audit verified the `decisions.json` source SHA256 maps; the merger
  validates structure and coverage, not reason truth.
- Requested model identity `gpt-6.1-sol` is not observed by the executor; no
  cross-model or repaired-Claude claim follows.
