# deep-deep-research vs built-in deep-research — bake-off (2026-07-07)

**Verdict: plugin arm (deep-deep-research) wins on blind quality (2/2
judges) at ~1/4 the cost, but died 2/2 unattended at claims
consolidation until the file-carrier fix this branch ships was applied
as an operator hint.** Directional evidence (n=1 question), not proof.

- Fix brief motivated by this run:
  `docs/loom/specs/2026-07-07-deep-deep-research-file-carrier.md`
- Prior firing A/B: `docs/loom/dogfood/2026-07-06-research-toolkit-firing-ab.md`
- Method: one research question (Apache Iceberg vs Delta Lake in the
  AWS ecosystem — Redshift / Glue / Athena / S3 Tables, 2025-2026, for
  a Redshift+dbt mid-size team); two arms, identical prompts and
  output contract, explicit skill invocation, clean scratch cwd each,
  headless `claude -p --model sonnet --max-turns 120
  --dangerously-skip-permissions`. Arm A = built-in deep-research;
  Arm B = `research-toolkit:deep-deep-research` (installed plugin 0.3.0).
- Blind quality eval: reports de-identified as K (= arm A) and
  Q (= arm B); two opus judges, opposite reading orders, 5 dimensions
  (coverage/depth, citation-claim fit, verification rigor,
  recency/correctness, actionability), 0-10 each.

## Blind-judge scores

| Judge (reading order) | K (= A, built-in) | Q (= B, plugin) | Verdict |
|---|---|---|---|
| Judge 1 (K→Q) | 40 | **43** | hand Q to the team lead |
| Judge 2 (Q→K) | 36 | **41** | hand Q to the team lead |

Q's recurring edge: AWS primary-source citations with dates, precise
Redshift-write timeline, decision-ready trade-off table. K's edge:
stricter refusal of a biased survey; caught the dbt-glue≠dbt-redshift
error.

## Citation spot-check — tie

5 citations sampled per report, live-fetched by sonnet agents:
K 4/5 SUPPORTED + 1 PARTIAL; Q 4/5 SUPPORTED + 1 PARTIAL.

## Cost (full campaign to a delivered report)

| Arm | Cost | API time |
|---|---|---|
| A built-in | ≈ $39.08 | 105.6 min |
| B plugin | ≈ $10.30 total ($4.83 failed leg + $5.47 resumed completion) | ~37 min |

## Failure modes observed

1. **Headless 600s bg ceiling — both arms.** Each arm was killed once
   by headless print-mode's default 600s background-task wait ceiling.
   Remedy: `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0` — applied on the
   rerun; no further background kills occurred.
2. **Monolithic inline payload → mid-response 5xx — plugin arm, 2/2
   unattended.** The plugin arm died at claims consolidation both
   times: SKILL.md's `echo '[<all claims>]'` monolithic inline payload
   (88 claims) was cut by "API Error: Server error mid-response".
   Recovered only via operator `--resume` with a "write payloads to
   files incrementally" hint — that hint is exactly the file-carrier
   fix this branch ships. Companion memory entry:
   `docs/loom/memory/file-carrier-for-bulk-payloads.md`.
3. **Built-in synthesize crash — self-disclosed.** The built-in arm's
   own report disclosed its synthesize step crashed and was
   hand-reassembled.

## Caveats / limits

- n=1 question, one domain, sonnet driver both arms — directional
  evidence, not proof.
- Built-in deep-research stays enabled; positioning = heavyweight asks
  (徹底研究 / 多輪) route to deep-deep-research.
