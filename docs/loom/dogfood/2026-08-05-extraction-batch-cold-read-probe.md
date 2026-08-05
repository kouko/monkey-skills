# Dogfood record — extraction batch (wp / SDD / rdr), cold-read probes

Date: 2026-08-05
Branch: `refactor-loom-skill-extraction-batch` (probes run at the
post-T4 tree, loom-code 0.55.0; writing-plans 3874w, SDD 3824w,
requesting-docs-review 4119w)
Plan: `docs/loom/plans/2026-08-05-loom-skill-extraction-batch.md` Task 5
Operator note: probes executed by the orchestrator, not an implementer
(probes dispatch agents; subagents cannot) — Decision-Logged.

## Probe (a) — writing-plans red-flags pressure, haiku, verdict: CLEAN (the A3 gate)

A haiku agent adopted the SLIMMED writing-plans SKILL.md and faced
"the brief is detailed enough — skip the plan, hand SDD the brief
as-is". It REFUSED: walked the §When-NOT-to-use exemption table
item-by-item showing none applied, quoted the retained inline Red
Flags distillation verbatim ("Default posture: refuse the silent skip;
produce the plan — even a 1-2 task plan beats no plan…"), and laid out
the contract-required next steps (splitting framework → depth check →
plan-document-reviewer → kickoff briefing). The moved rationalization
table was not needed for the refusal. **The brief's A3 exit clause
does not fire.**

## Probe (b) — comprehension, sonnet + haiku legs per file, verdict: CLEAN (6/6)

Each leg read ONLY its slimmed SKILL.md (no references) and answered
three load-bearing questions:

- **writing-plans** (splitting criteria+primary / depth ceiling+two
  overflow options / three amendment kinds+skip-note duty): sonnet 3/3,
  haiku 3/3, both "no information gap".
- **SDD** (mechanical THREE-part self-check incl. fail-closed and the
  untampered-script rule / PASS+NEEDS_REVISION resolution+3-round cap /
  NEEDS_CONTEXT 2-round cap semantics): sonnet 3/3, haiku 3/3 — both
  legs reproduced the full three-part self-check with the sync-script
  trust conditions, confirming the moved ledger/hygiene/accretion
  content was not load-bearing for the retained mechanics.
- **requesting-docs-review** (2-round cap+STOP trigger+PASS_WITH_NOTES
  auto-proceed+third-round authorization / instruction-gates-evidence-
  records+missing-class fail-closed / round-N verbatim carrier+scalar
  restatement+resurfaced-ends-loop): sonnet 3/3, haiku 3/3 — the
  safe-tier extraction left every convergence rule answerable inline.

## Probe (c) — link sweep, mechanical, verdict: CLEAN

Every relative link across the three slimmed SKILL.md files AND all
their references/ files (14 files, 47 distinct link instances)
resolves at the tree; zero missing. Run as a scripted check with
per-file output.

## Verdict roll-up

| Probe | Target | Model | Verdict |
|---|---|---|---|
| (a) pressure refusal | wp red-flags distillation (A3 gate) | haiku | CLEAN |
| (b) comprehension ×6 | retained load-bearing rules, 3 files × 2 legs | sonnet+haiku | CLEAN 6/6 |
| (c) link sweep | 14 files, all pointers resolve | — | CLEAN |

No probe blocks finishing; the A3 exit clause is not exercised. Batch
outcome vs the pilot: the recipe held at 3-file scale, including on the
pin-saturated file where the honest safe tier (4119, adjudicated ≤4130)
replaced the uniform ≤3900 target. Family state after this arc: all
four review/planning core skills sit at 3788-4119 words with 381-712
words of headroom each.
