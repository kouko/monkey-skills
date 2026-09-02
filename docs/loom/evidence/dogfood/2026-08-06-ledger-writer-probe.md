# Dogfood: ledger writer duty — haiku cold-read probe + first-user note

Date: 2026-08-06
Branch: feat-ledger-writer-and-plan-tooling-hardening (probe at the T4
commit 7ebbb754's SDD duty sentence, embedded verbatim)
Verdict: **CLEAN** (one honest scope note)

## Probe — does the duty sentence route a cold reader to the command?

Haiku, fresh context, no tools, given ONLY the Progress-ledger
paragraph + a "T2 finished, sha abc1234, update the ledger" scenario:

- Q1 (what do you do): produced the exact command shape
  `python3 scripts/plan_card.py <plan-path> --set-status "T2=<status>"`
  — reached for the tool, not the editor.
- Q2 (when to hand-edit): "Only when scripts/plan_card.py does not
  exist at the repo root", quoting the sentence's own condition — a
  verifiable action, not a judgment.
- Q3 (what the tool protects): all four refusal classes named
  (unknown task, bad grammar, duplicate Status lines, missing Status
  line) and the hand-edit bypass risk articulated.

Scope note: the probe guessed at status enum values (PASS /
REVIEWERS_PASS / MERGED) while honestly flagging "the skill text does
not specify the exact enum". By design: the four-kind grammar lives in
the schema and in the writer's loud error message — a wrong kind gets
refused with the grammar quoted at run time, so the duty sentence does
not need to carry the enum. The probe's hedge confirms the sentence
does not mislead; the mechanical layer corrects.

## First-user note — this arc dogfooded the writer

Every ledger flip after the writer's birth commit went through it:
T1 done(fb6f552d) — the writer's own first flip — then T2
done(383c314d), T3 done(a499cfce), T4 done(7ebbb754), and T5's own
flip in the close-out. Each printed the old→new pair; zero
hand-edited flips (the Stage line edits are hand edits by design —
the writer only rewrites Status), zero flip errata through T5 (the
previous arc had two).
