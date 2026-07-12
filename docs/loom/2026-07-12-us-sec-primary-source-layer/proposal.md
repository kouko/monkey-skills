# Proposal — US SEC primary-source data layer (staged-C)

> **⚠️ Ungoverned spec (fail-loud).** No `docs/loom/PRINCIPLES.md` exists in
> this repo — this fan-out is **not governed by a product constitution**.
> Scope boundary + NFR posture below are drawn from the brainstorming brief
> (`docs/loom/specs/2026-07-12-us-sec-narrative-extraction.md`) and this
> session's research, not a constitution. Coverage claims are **relative to
> seed + lenses**, never "complete".

Seed: brief `docs/loom/specs/2026-07-12-us-sec-narrative-extraction.md`
+ research `/tmp/research-{us-sec,processing-layer,xbrl-coverage-boundary,kpi-timeseries}.md`.
Change-id: `2026-07-12-us-sec-primary-source-layer`. Three capabilities:
`narrative`, `financial-table-xval`, `operational-kpi`.

## USM backbone

Actors: **pipeline** (automated orchestrator, `inferred`), **human-confirmer**
(confirms a proposed KPI schema; adjudicates low-confidence extractions,
`seeded`), **memo-writer** (downstream `investing-team` consumer, `seeded`).

Data-flow spine (forward edges of the navigation graph):

| # | Stage | Object touched | CTA | Provenance |
|---|---|---|---|---|
| 1 | Acquire filing (edgartools) | filing | fetch | seeded |
| 2 | Segment narrative sections | section | segment | seeded |
| 3 | Extract tables (financial + operational) | table | extract | seeded |
| 4 | Cross-validate financial table ↔ XBRL | table | reconcile | seeded |
| 5 | Resolve company KPI schema (propose→confirm) | kpi-schema | propose / confirm | seeded |
| 6 | Locate KPI cell + parse number | kpi | locate / parse | seeded |
| 7 | Validate + provenance-stamp | kpi | validate | seeded |
| 8 | Detect definition drift → break event | break-event | flag | seeded |
| 9 | Store bitemporal series point | series-point | append | seeded |
| 10 | Reliability-gate evaluation | reliability-gate | evaluate | seeded |
| 11 | Feed trusted series + narrative to memo | (consumer) | consume | seeded |

Navigation graph (typed edges beyond `forward`):
- `abandon`/`resume_reenter`: stage 5 when schema unconfirmed → **review-item**
  queue; pipeline abandons that company's KPI path, resumes when confirmed.
- `error_escape`/`resume_reenter`: stage 6-7 low-confidence or unparseable
  cell → **review-item** queue; escape from auto-path, resume on adjudication.
- branch: stage 8 drift detected → **break-event**, series splits into
  as-reported vs recast; never naive-concatenates.
- `abandon`: stage 10 gate fails → series **withheld** from memo (not fed,
  not fabricated).

Single-surface note: this is a data pipeline, not a UI journey — the spine is
the data flow; the "richness" is in the object state machines + the
review/gate branches, not a multi-screen navigation.

## OOUX object model

Assembled from the three capability fan-outs. States shown as `A →(edge)→ B`.

**filing** (`narrative`) — Rel: HAS-MANY section; BELONGS-TO filer(CIK); 8-K HAS-MANY exhibit. CTAs: fetch, resolve-form, list-items. Attrs: accession, cik, form, filingDate, period_of_report, primaryDocument, items[], doc_url.
States: `unresolved →(resolve ok)→ resolved →(form present)→ segmentable`; `unresolved →(no CIK)→ not_found`; `resolved →(form never filed)→ form_unavailable`.

**section** (`narrative`) — Rel: BELONGS-TO filing; 8-K SOURCED-FROM exhibit_99x. CTAs: segment, follow-exhibit, write-text-file, emit-provenance. Attrs: item_id, form, text_path, source(primary|exhibit_99_x), status, provenance{accession,cik,item_id,filingDate,period,url}.
States: `pending →(ok)→ extracted`; `pending →(8-K item listed, no Ex-99.x)→ gap [loud]`; `pending →(throws)→ error [loud]`. **No silent-empty state — every non-extracted outcome is gap|error.**

**table** (`financial` + `operational` variants) — Rel: BELONGS-TO filing; HAS-MANY cell; financial CROSS-VALIDATED-BY divergence; operational MAY-match kpi-schema entry. CTAs: locate, extract, classify(financial|operational), reconstruct(xbrl), match, link-to-schema. Attrs: table_id, filing_accession, statement_type|table_kind, doc_anchor, cells[]{concept,period,dimension,value,scale,decimals,doc_cite}.
States: `discovered →(extract)→ extracted →(classify)→ {financial | operational}`; financial `→ matched(has-XBRL-pair) | unmatched(single-source) → reconciled`; operational `→ {linked | unmatched}`.

**divergence** (`financial-table-xval`) — Rel: pairs one table-cell ↔ one XBRL fact (or none). CTAs: classify, annotate-source, surface(high), state-single-source. Attrs: concept, period, dimension, doc_value, xbrl_value(scale-normalized), abs_diff, pct_diff, alert(low|medium|high|n/a), source_tag(rounding|adjusted-non-gaap|restatement-signal|decimal-disagreement|tagging-error|none).
States: `unmatched →(match)→ matched →(classify)→ {low|medium|high|n/a}`; `matched(no-tag) → single_source [terminal, stated not guessed]`; `classified(high) → surfaced [never silently reconciled]`; `classified(low|med, legit) → annotated`.

**kpi** (`operational-kpi`, extraction instance pre-commit) — Rel: SOURCED-FROM table+cell; BELONGS-TO kpi-schema def; PROMOTES-TO series-point; MAY-SPAWN review-item. CTAs: locate, parse, validate, cross_check_xbrl, promote. Attrs: kpi_instance_id, company, kpi_id, period, value, confidence, source_cell_ref.
States: `located →(parse)→ parsed →(validate)→ validated →(gates)→ {promoted | review | rejected}`.

**kpi-schema** (`operational-kpi`) — Rel: company-scoped; HAS-MANY kpi defs; CONFIRMED-BY human-confirmer; SUPERSEDES prior on drift. CTAs: propose, confirm, amend, retire. Attrs: schema_id, company, version, status, confirmed_by/at.
States: `proposed →(human confirm)→ confirmed →(active)→ {active | superseded →(drift)→ new proposed}`. **Propose = LLM; confirm = human, once.**

**series-point** (`operational-kpi`, append-only) — Rel: BELONGS-TO series(company+kpi_id); SOURCED-FROM kpi; TAGGED as-reported|recast post break. CTAs: append, query_point_in_time, query_latest. Attrs: company, kpi_id, period, as_of, value, lineage, provenance{accession,table_id,cell_ref}.
States: append-only, terminal `appended` (never mutated — bitemporal).

**break-event** (`operational-kpi`) — Rel: LINKS old↔new def; SPLITS a series. CTAs: flag, adjudicate, confirm, apply, dismiss. Attrs: break_id, company, trigger(resegmentation|relabel|arithmetic-mismatch), mapping, status.
States: `flagged →(review)→ under_review →(adjudicate)→ {confirmed →(apply)→ applied | dismissed}`.

**review-item** (`operational-kpi`) — Rel: REFERENCES subject(kpi-schema|kpi|break-event); ASSIGNED human-confirmer. CTAs: enqueue, adjudicate, resolve, reopen. Attrs: review_item_id, subject_type/id, reason, status, resolution.
States: `open →(pick up)→ in_review →(resolve)→ {approved | rejected | edited} →(reopen)→ open`.

**reliability-gate** (`operational-kpi`) — Rel: evaluated per company(+schema version); GATES memo feed. CTAs: evaluate, record_metric, compare_to_threshold. Attrs: gate_id, company, metric(cell-level-accuracy), sample_size, verdict, evaluated_at.
States: `not_evaluated →(evaluate)→ evaluated →(compare)→ {trusted | withheld} →(schema bump)→ not_evaluated`.

## Path × edge matrix

The full `backbone × object × CTA × state` grid is realized as the **72
`#### Scenario:` blocks** across the three `specs/` deltas — those ARE the
surviving pruned paths. Lens application (which dominated where):

| Lens | Dominated at | Kept as paths | Flagged edges |
|---|---|---|---|
| state-transition legality | every object with a lifecycle | legal transitions (propose→confirm, flagged→applied) | illegal: append across un-adjudicated break; promote on unconfirmed schema |
| empty/error/loading | stages 1-3 (network/parse boundary) | not_found, form_unavailable, gap, error | 8-K item listed but Ex-99.x absent (loud gap) |
| BVA | divergence tolerance, confidence threshold | ~1% rounding boundary; confidence at-threshold | just-past 1% (rounding vs tagging-error); at-bar reliability |
| permissions | the human-confirm seam | LLM-propose vs human-confirm-once; adjudicate | auto-commit that skips confirm (denied) |
| CRUD | bitemporal store | append, point-in-time read, latest read | update/delete on series-point (forbidden — append-only) |
| NFR | reliability-gate, provenance | accuracy bar before trust; total provenance | empirical threshold unquantified → blind spot |

Sparse-output honesty: no padding — every path traces to a scenario or a
flagged edge case above.

## Cross-object combinations

One genuinely interaction-dense stage: **committing a KPI extraction into the
trusted, memo-fed series** — the reaction depends on the JOINT state of 5
co-active objects (kpi-schema, break-event, reliability-gate, review-item,
kpi.confidence), and the joint reaction is NOT the union of individual
reactions (a passing gate does not commit if the schema is unconfirmed).
≥4 co-active objects ⇒ **`pairwise.py` was run** (inline enumeration banned):

```
echo '{"params": {"kpi_schema":["CONFIRMED","PROPOSED_unconfirmed","SUPERSEDED"],
  "break_event":["none","FLAGGED_unadjudicated","CONFIRMED_applied"],
  "reliability_gate":["TRUSTED","WITHHELD","NOT_EVALUATED"],
  "review_item":["none_open","OPEN_blocking"],
  "kpi_confidence":["above_threshold","below_threshold"]}}' | pairwise.py
```

**Governing rule (two-level gate)** — validity gates decide whether the
extraction becomes a series-point at all; the trust gate decides whether the
series is fed to the memo:
- **Validity (A-D, any → NOT appended):** (A) schema not CONFIRMED → hold, enqueue schema-confirm; (B) break FLAGGED_unadjudicated → hold, route to break adjudication (never append across break); (C) review OPEN_blocking → hold pending adjudication; (D) confidence below_threshold → enqueue review-item.
- **Trust (E):** all A-D clear but gate ≠ TRUSTED → **append to bitemporal store, but WITHHOLD from memo** (valid datapoint, untrusted series).
- **Commit:** all clear → append AND feed memo.

Pairwise-covering set (10 combos) with governing reaction:

| # | schema | break | gate | review | conf | reaction |
|---|---|---|---|---|---|---|
| 1 | CONFIRMED | none | WITHHELD | none | above | E → store, withhold from memo |
| 2 | CONFIRMED | FLAGGED | TRUSTED | OPEN | below | B+C+D → hold (break adjudication first) |
| 3 | PROPOSED | CONFIRMED_applied | TRUSTED | none | above | A → hold, enqueue schema-confirm |
| 4 | PROPOSED | none | NOT_EVAL | OPEN | below | A+C+D → hold; also E untrusted |
| 5 | SUPERSEDED | CONFIRMED_applied | WITHHELD | OPEN | below | A(no active successor)+C+D → hold; E withhold |
| 6 | SUPERSEDED | FLAGGED | NOT_EVAL | none | above | A+B → hold |
| 7 | CONFIRMED | CONFIRMED_applied | NOT_EVAL | none | below | D → enqueue review; E untrusted |
| 8 | SUPERSEDED | none | TRUSTED | none | above | A → hold, enqueue schema-confirm |
| 9 | PROPOSED | FLAGGED | WITHHELD | none | above | A+B → hold; E withhold |
| 10 | CONFIRMED | none | TRUSTED | none | above | **COMMIT — append + feed memo** |

Residue not guaranteed by pairwise (higher-order interactions, e.g. a break
whose recast series itself fails the gate) → carried as a blind spot, not
padded.

## Journey navigation

0-switch walk of the Phase ① typed edges (each exercised once):
- `forward` (spine 1→11): each stage's reaction is its capability scenarios.
- `abandon`+`resume_reenter` (stage 5, schema unconfirmed): pipeline abandons the company's KPI path → enqueues review-item; resumes at stage 6 when the schema is CONFIRMED. Reaction: no KPI promoted meanwhile; narrative + financial paths continue unaffected.
- `error_escape`+`resume_reenter` (stage 6-7, low-confidence/unparseable): escape to review-item; on adjudication (approved/edited) resume promote; (rejected) → kpi REJECTED, no series-point.
- branch (stage 8, drift): emit break-event; series splits as-reported/recast with visible break flag; downstream queries must pick a basis — **never naive-concatenate**.
- `abandon` (stage 10, gate WITHHELD/NOT_EVALUATED): series appended to store but withheld from memo; re-evaluated on next schema-version bump.

## Provenance

- **narrative** (8 Req): 7 `seeded` (brief Decision §1 + research-us-sec Q1-Q4), 1 `inferred` (8-K missing-exhibit gap scenario — invariant applied to the specific case).
- **financial-table-xval** (9 Req): 8 `seeded` (research-xbrl-coverage §3-4, comps pattern), 1 `inferred` (the low/medium/high tolerance bands + 5% upper cut — extrapolated from comps `_classify_divergence_alert`, seed gives only ~1%).
- **operational-kpi** (18 Req): all `seeded` from the brief Decision + research-kpi-timeseries, EXCEPT the JSON-file bitemporal substrate choice = `inferred-from-codebase-precedent` (matches `cache_util.py` XDG file-per-key convention).
- **critic-found** (round 1, +5 narrative / +14 operational-kpi Req): the C1-C18 gaps re-seeded from the 5-lens panel — see §Critic findings for the per-item lens convergence that is each item's rank signal. Tagged `critic-found` (distinct from the writer's `seeded`/`inferred`).

## Critic findings (completeness-critic, round 1)

Panel: 5 fixed lenses (principles lens N/A — no PRINCIPLES.md), fresh-context.
**Overlap judgment: diverse enough** (~25-35% pairwise; healthy 0.22-0.40
range) — convergence only on genuinely cross-cutting gaps. **1 productive
round; no new defect class surfaced** → terminated per targeted-re-seed rule
(not a silent skip — the reasoning is named). Ranked consolidated union
(severity × cross-lens convergence); load-bearing items re-seeded as
`critic-found` scenarios in the `specs/` deltas:

| # | Gap | Sev | Lenses | Disposition |
|---|---|---|---|---|
| C1 | SEC access NFR — mandatory `User-Agent`, ~10 req/s rate-limit + 429/403 backoff, filing cache/dedup | 3 | NFR, policy, object | → scenarios (narrative + xval) |
| C2 | Append idempotency — dedup key incl. `source_accession`; **`as_of` provenance undefined** (wall-clock vs accession-derived) → re-run double-appends | 3 | system, object | → scenario (operational-kpi) |
| C3 | Concurrency/locking on the file-based series store + review-queue (parallel company runs race/corrupt) | 3 | system, NFR | → scenario (operational-kpi) |
| C4 | Amended filings (10-K/A, 10-Q/A) supersede prior bitemporal points; draft names only 10-K/10-Q/8-K | 3 | object, state, system | → scenario (operational-kpi) |
| C5 | Authorization on the human-confirm seam — pipeline can self-confirm → anti-fabrication seam is convention, not enforced | 3 | policy, object | → scenario + blind-spot (scope boundary) |
| C6 | Memo-feed contract undefined — stage 11 "consume" has no interface artifact (bundle? manifest? divergence-flag schema?) | 3 | object | → scenario (operational-kpi) |
| C7 | Ground-truth label-set as a first-class object/lifecycle — the gate is unimplementable without it | 3 | object | → scenario + blind-spot (who maintains) |
| C8 | Prompt-injection via filing content — LLM-locate reads untrusted filer text; can steer *which* cell (locate-then-parse blocks value-injection, not cell-steering) | 3 | NFR | → scenario (operational-kpi + narrative) |
| C9 | Audit identity on review-item/break-event (`adjudicated_by/at`, immutable) | 3 | policy | → scenario (operational-kpi) |
| C10 | SUPERSEDED schema with no confirmed successor — pairwise names it, no Scenario | 3 | state | → scenario (operational-kpi) |
| C11 | Recast series that itself fails the gate — proposal residue, needs a real decision | 3 | state | → scenario (operational-kpi) |
| C12 | Furnished-vs-filed status (8-K Ex-99.x is *furnished*, different §18 liability) not propagated to memo | 2 | policy | → scenario (narrative) |
| C13 | Unparseable-cell taxonomy incomplete (`$1,234` / `NM` / `—` / true-zero vs blank) — strip/fail/zero unspecified | 2 | state | → scenario (operational-kpi) |
| C14 | Reliability gate: at-threshold inclusive/exclusive + minimum sample size (a 1-cell held-out set yields spurious 100%) | 2 | state | → scenario (operational-kpi) |
| C15 | Out-of-order processing breaks chronological drift-detection (a /A before its original) | 2 | system | → blind-spot + note (ties C4) |
| C16 | Observability — per-stage attempted/succeeded/gapped/errored counts + LLM locate latency/cost | 2 | NFR | → scenario (operational-kpi) |
| C17 | KPI silently discontinued (N consecutive not-founds never escalates to schema-retire) | 2 | state | → blind-spot |
| C18 | edgartools version-drift returning wrong data silently (vs throwing); network timeout as a distinct error class | 2 | NFR | → scenario (narrative) |

Long-tail sev-1 (review SLA/escalation, segregation-of-duties, partial-table
completeness status, token/cost ceiling, break mapping-undeterminable third
path, overlapping breaks same period, empty-series-file init) → named residue,
not padded into requirements.

## Blind spots — needs human/field input

1. **Empirical reliability threshold** — the metric (cell-level accuracy on a held-out set) is specced; the numeric bar is not determinable without pilot data → `[deferred]`.
2. **Per-industry KPI taxonomy** — which KPIs matter (iPhone units vs RevPAR vs load factor) is domain-expert judgment per sector; spec owns the mechanism (schema registry), not any taxonomy content.
3. **Pilot ticker selection** (1-3) — a business call; picks which schema is built first.
4. **Locate-confidence threshold calibration** — the number needs labeled data; behavior at threshold-crossing is specced, the value is not.
5. **Held-out label set construction/maintenance** (C7) — who builds and refreshes the ground-truth labels the gate evaluates against is an ongoing human-ops question; the spec owns the object + lifecycle, not who staffs it.
6. **Higher-order commit interactions** (③b residue, C11) — combinations beyond pairwise coverage (e.g. a recast series that itself fails the gate) need case-by-case adjudication.
7. **Authorization-layer ownership** (C5) — whether the confirm-seam authorization is enforced in this data layer or delegated to an ops/CLI wrapper (per the repo's Cross-Plugin Delegation Contract) is a boundary decision the user must make; the spec now requires the boundary be *stated*, but not *where* it lives.
8. **KPI-discontinuation policy** (C17) — how many consecutive not-founds should escalate to a schema-retire suggestion is a domain-cadence judgment (annual KPIs legitimately gap 3 quarters).
9. **Out-of-order/backfill semantics** (C15) — whether historical backfill re-derives break-events or trusts processing order needs a human call on the ops model.

Coverage statement: **coverage relative to seed + 5 lenses (principles N/A) +
pairwise on the one wide stage + 1 critic round**; blind spots above are the
known ceiling, not a completeness claim.

