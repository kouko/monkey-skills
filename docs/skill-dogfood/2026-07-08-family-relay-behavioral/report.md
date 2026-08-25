# Dogfood report — family relay discipline (behavioral, weak-model actor)

- Date: 2026-07-08
- Target: **installed behavior** of the loom family relay discipline
  (loom-pipeline 0.6.1 `hooks/family-relay.md` + language hooks; loom-code
  0.27.0 seams) — NOT a raw working-tree skill; probes adapted accordingly
  (Probe B executor+blind-auditor is the core; Probe A triggering was
  covered by the existing firing corpus; Probe C cold-read is covered by
  the branch's mechanical pointer tests).
- Actor: `claude -p --model sonnet` (weak tier, real harness, real hooks),
  blind to the observation target. 3 chained headless turns
  (brainstorm → RED stall on permission → GREEN + closing), sandbox todo-CLI
  repo (real 30-line fixture), total actor cost ≈ $2.10.
- Auditors: 2× blind sonnet agents, identical rubric (the discipline's own
  contract + non-expert comprehension), independent runs.

## Severity summary

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 0 |
| Medium | 1 |
| Low | 1 |
| Pass observations | 8 |

## Findings

### F1 — Medium · Convention-violation (table default not followed at fork)
- **Probe**: run 1 — actor presents the input-format fork (strict ISO vs
  relative dates) as the session's one decision.
- **Expected**: family-relay §(b): "≥2 options at a fork → a markdown
  comparison table is the default form."
- **Actual**: A/B as bold-header bullet lists with 優點/缺點. Both blind
  auditors independently scored criterion-4 FAIL (letter), while noting
  comprehension was not hurt.
- **Root cause**: the relay pointer wired into brainstorming (SKILL.md
  ~§Output Contract, summary-relay rule) fires at the SUMMARY seam; the
  fork-presentation moment inside the 5-axis walk carries no table nudge a
  weak model reliably obeys.
- **Why static review missed it**: the pointer string exists → mechanical
  test green; only a behavioral run shows the weak model not carrying the
  default into the ask itself.
- **Suggested fix direction**: one line in brainstorming's ask-phrasing
  guidance naming the table default AT the fork moment; alternatively
  accept as tolerated deviation (it is a default, not a mandate) and
  re-measure at post-ship acceptance.
- **Repro**: `actor-run1.jsonl` final text.

### F2 — Low · Jargon-leak (unglossed code-level terms; mechanism-first closer)
- **Probe**: runs 1 & 3.
- **Actual**: `argv[1:]`, `datetime.date.fromisoformat`, ANSI, `dateutil`
  unglossed in the run-1 briefing (both auditors: criterion-2 PARTIAL);
  run-3 closing report opens "RED→GREEN→REFACTOR 都完成" — mechanism token
  first, though RED was glossed 「(先失敗)」 at first use in run 2 and the
  rest of the closer is plain zh bullets.
- **Assessment**: borderline — the persona owns a CLI tool, code
  identifiers are arguably content; kept Low. Watch in real sessions via
  the confusion-signal metric.
- **Repro**: `actor-run1.jsonl` / `actor-run3.jsonl`.

## Pass observations (what the weak model held)

1. Routing: using-loom-code → brainstorming → tdd-iron-law, unprompted.
2. **Narration zh end-to-end** (7/7 substantive turns zh-dominant) in a
   real harness session where English skill bodies loaded — the language
   anchor demonstrably effective at the exact seam that failed in the
   baseline (B1: 70% EN worst session).
3. State anchor first line of every user-facing message.
4. Stakes-first fork framing (「這會變成你以後每天打指令的習慣」 before any
   mechanism) — the baseline's canonical failure (A1) inverted.
5. Recommendation + one-line why + open ending; reversible details decided
   without asking (gate ① held; no confirmation spam).
6. Zero verdict/orchestration tokens dumped (no PASS_WITH_NOTES/Wave/派工
   console-speak reached the reader).
7. TDD iron law on disk: failing tests written and verified RED before
   implementation; 5 passed at close.
8. Discipline under friction: permission block → stopped after two
   attempts and asked, quoting the rule; closing report honestly names
   what is NOT done (commit + review pending) instead of claiming done.

## Coverage gaps (not tested — do NOT read as pass)

- **SDD wave/rollup-card seam**: task was correctly too small for SDD
  (1 module, <1 hr → direct TDD), so the per-wave rollup card never had a
  chance to appear. Needs a multi-module dogfood or real usage.
- **Stop-hook block path**: no English drift occurred to block (plausibly
  because the anchor worked); the block path is covered by unit tests +
  installed-copy probes only.
- Single scenario, single weak-model tier, n=1 conversation.

## Raw outputs

- `scratchpad/relay-dogfood-sandbox/actor-run{1,2,3}.jsonl` (full streams;
  session-scoped scratch — quote-of-record excerpts are embedded above)
- Sandbox end state: 5 passed; feature implemented per decision A;
  uncommitted (actor correctly deferred to review flow).
- Blind audit transcripts: both auditors converged (acceptable; criterion-4
  FAIL, criterion-2 PARTIAL, all else PASS; comprehension sentence correct
  in both).

## Verdict framing (floor, not ceiling)

No pass stamp. Behavioral evidence says: the shipped discipline **holds on
a weak model** for brainstorm-phase relay, language anchoring, TDD, and
honesty conventions; the table default is the one letter-level miss; the
SDD rollup card remains unexercised. Post-ship acceptance (~10 real
sessions, ruler v2) stays the decisive gate.
