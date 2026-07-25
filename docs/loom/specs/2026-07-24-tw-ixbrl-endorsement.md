# TW iXBRL endorsement/guarantee (背書保證) ingestion

Brief (brainstorming output) — 2026-07-24. Branch `tw-ixbrl-endorsement`
off `6fb8505d` (main @ investing-toolkit 2.32.1). Origin: `docs/loom/BACKLOG.md`
§"TW iXBRL 2.27.0" item (b) — the endorsement/guarantee curated field,
deferred twice for structural difficulty, user-selected as the next arc.

## Problem

When someone assesses a Taiwanese company's credit risk, one of the classic
red flags is **off-balance-sheet contingent exposure**: how much has this
company endorsed or guaranteed *for other parties* (subsidiaries, affiliates,
or — the governance red flag — related/non-operating entities). An over-
endorsed company can be sound on its own books yet one counterparty default
away from a large contingent liability; endorsements to related parties are a
classic tunneling/self-dealing signal. Today the memo pipeline reads none of
this — the data is in the filing but silently unextracted, so a memo on a
group holding company shows no view of its guarantee book at all.

## Users

kouko running equity memos on TW companies — especially industrial groups
with many subsidiaries and cross-guarantees (台泥 1101 = 39 endorsement rows,
鴻海 2317 = 28 rows in the current filings). Job story: *when I evaluate a
TW company's credit/governance risk, I want to see its total endorsement/
guarantee exposure and whether it flows to non-subsidiaries, so I can flag
over-endorsement vs net worth and related-party self-dealing without opening
the raw MOPS filing.*

## Smallest End State

A new note extractor + a curated summary wired into the existing TW canonical,
**no parser change, no fetch change** (recon proved the data is reachable with
the current pipeline). Concretely:

- `extract_endorsement_guarantee_notes(facts)` in `twse_ixbrl_notes.py` —
  reconstructs per-endorser rows by **document-order segmentation on the
  `CompanyNameOfTheEndorserGuarantor` anchor** (the same trick
  `_fh_npl_tree_segments` uses; endorsement has no leaf `tuple_ref` and only
  a shared `context_ref`, so document order is the only handle). Recon proved
  this recovers all 39/28 rows cleanly; the inner `Counterparty2` tuple
  flattens (one `NameOfTheCompany`/`Relationship1` per span).
- A **curated aggregate summary** (the load-bearing memo signal): total actual
  amount provided (summed — no aggregate leaf exists), total ending balance
  (summed), counterparty count, ratio to net asset, and a **subsidiary-vs-
  external split** from the per-row Y/N flags
  (`EndorsementsGuaranteesProvidedToSubsidiaryByParentCompany` etc.) — this is
  the self-dealing signal without a full per-row table.
- Graceful **empty case**: filers with no endorsements render an empty
  `無此情形／免揭露` placeholder (台塑 1301, financial holdings) → the extractor
  returns an explicit "none" summary, never a crash or a silent zero.
- Wired into the notes routing (`_extract_notes` by taxonomy) so it surfaces
  for `-ci` industrials (where endorsements are common) — financial families
  carry it too where present.

**Scope (user-decided 2026-07-24): aggregate + per-counterparty detail.**
The extractor emits BOTH the curated aggregate summary AND the per-counterparty
detail rows (endorser → counterparty → individual limit / ending balance /
actual provided / collateral-secured / relationship flags), the same shape
`extract_fh_npl_coverage_notes` returns per-subsidiary. This lets a memo name
individual counterparties (related-party self-dealing is legible at the row
level, not just the aggregate split).

## Current State Evidence

- **Forward**: fetch pulls the full t164sb01 iXBRL instance
  (`twse_ixbrl_fetch.py:41,65-79`, C→A fallback `:158-177`); the endorsement
  data lives in `<div id="EndorsementGuaranteeProvidedToOthers">` of that same
  instance — already fetched, never extracted.
- **Reverse (closest existing pattern)**: `_fh_npl_tree_segments`
  (`twse_ixbrl_notes.py:221-254`) segments facts into per-subsidiary spans by
  document order between anchor markers; `extract_fh_npl_coverage_notes`
  (`:257-302`) returns per-subsidiary rows. Endorsement needs its OWN extractor
  (neither the `tuple_ref="^NPL\d+$"` handle nor the `-basi` `context_ref`
  suffix applies — endorsement facts are all `tuple_ref=None` with 2 shared
  context_refs), but the document-order segmentation generalizes.
- **Error/empty path**: 台塑 1301 and financial-holding 6005 render the
  endorsement section as an empty `無此情形／免揭露` placeholder — the extractor
  must treat "section present but empty" as a first-class "none" result.
- **Data (real structure, 1101 台泥)**: nested `ix:tuple` — one OUTER
  `tifrs-notes:EndorsementGuaranteeProvidedToOthers` per row, INNER
  `tifrs-notes:Counterparty2` holding the counterparty name. Per-row concepts
  (all `tifrs-notes:`): `CompanyNameOfTheEndorserGuarantor`,
  `LimitOnEndorsementGuaranteeAmountProvidedToIndividualCounterparty`,
  `EndingBalance2`, `ActualAmountProvided`,
  `AmountOfEndorsementsGuaranteesSecuredWithCollateral`,
  `RatioOfAccumulatedEndorsementGuaranteeAmountToNetAsset`,
  `LimitOfTotalGuaranteeEndorsementAmount` (per-endorser ceiling, NOT a single
  aggregate), plus Y/N relationship flags. No total-actual leaf →
  SUM(ActualAmountProvided)=105.9bn, SUM(EndingBalance2)=107.6bn reconstructed.
  Full evidence: `scratchpad/endorsement-recon-evidence.md` (migrate the key
  table into a committed reference or trim per the stale-citation lesson).
- **Boundary (deferral to remove)**: the current test
  `test_twse_ixbrl_notes.py:109-120`
  (`test_curated_notes_excludes_endorsement_guarantee`) asserts endorsement is
  DEFERRED and must NOT surface — this flips to an inclusion test.

Evidence paths: `investing-toolkit/skills/data-markets/scripts/twse_ixbrl_notes.py`,
`twse_ixbrl_parser.py`, `twse_ixbrl_canonical.py`, `twse_ixbrl.py`,
`investing-toolkit/tests/data/test_twse_ixbrl_notes.py`.

## Alternatives Considered

- **Extraction handle** — document-order segmentation (proven in recon) vs. a
  real nested-`ix:tuple` parser upgrade (capture the outer/inner tuple
  hierarchy so rows self-disambiguate). Rejected the parser upgrade for this
  arc: it is a larger, riskier change to a module every taxonomy shares, and
  the document-order trick already recovers 100% of rows in the recon. (This
  is a TW-MOPS-iXBRL-specific structure — no industry-standard parser exists;
  Axis-4 external research returns nothing shippable, honestly noted.)
- **Aggregate vs per-counterparty detail** — the §Smallest End State open
  scope decision, surfaced to the user.
- **Producer-side sum vs. leaf** — there is no aggregate leaf (confirmed), so
  summing rows in the extractor is the only option, not a choice.

## What Becomes Obsolete

- `test_curated_notes_excludes_endorsement_guarantee`
  (`test_twse_ixbrl_notes.py:109-120`) — flips from a deferral assertion to an
  inclusion test in the same change.
- The BACKLOG §2.27.0 (b) deferral note — marked shipped.
- The stale `scratchpad/endorsement-recon-evidence.md` citation — migrate the
  operative measurement into a committed reference or inline fact (apply the
  producer-marker arc's citation-cleanup lesson from the start, not as debt).

## Decision

Build a new `extract_endorsement_guarantee_notes` extractor that reconstructs
endorsement rows by document-order segmentation and emits a curated aggregate
summary (total exposure, ratio to net worth, counterparty count, subsidiary-
vs-external split) **AND the per-counterparty detail rows** (user-decided
scope), wired into the TW canonical notes routing, with the empty placeholder
handled as a first-class "none". NO parser change, NO fetch change, NO
memo-render wiring beyond surfacing the curated field (the memo protocol
consuming it is a separate, smaller follow-up if wanted).

## Out of Scope

- A nested-`ix:tuple` parser upgrade (deferred — document order suffices).
- 資金貸與 (loans-to-others) and other MOPS related-party schedules — same
  structural family, separate arcs.
- Memo-protocol rendering of the endorsement signal (domain-teams layer) —
  a small follow-up once the data field exists.
- 興櫃 multi-period series (the other remaining BACKLOG arc).

## Open Questions

- None blocking. Scope resolved (aggregate + per-counterparty detail,
  user-decided 2026-07-24).
