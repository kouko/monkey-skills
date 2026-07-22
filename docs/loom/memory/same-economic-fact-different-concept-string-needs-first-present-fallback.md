---
name: same-economic-fact-different-concept-string-needs-first-present-fallback
description: A producer can book the SAME economic item under DIFFERENT concept strings across sub-shapes of one taxonomy family — TW reinsurers record insurance-contract-liabilities under generic ifrs-full:LiabilitiesArisingFromInsuranceContracts while life/P&C insurers use tifrs-bsci-ins:InsuranceContractLiabilities_CB. A canonical mapper keyed on ONE concept string silently drops the field for the other sub-shape; resolve with a first-present candidate list (try the specific concept, fall back to the generic), not a single lookup.
type: practice
origin: branch feat-tw-ixbrl-fh (2026-07-22) — TW -ins insurer canonical; measured across life (三商壽) / P&C (台產/新產) / reinsurance (中再保) sub-shapes
---

Within one taxonomy family the "same field" is not always the same concept string.
Measured for TW `-ins`: life + P&C insurers carry
`tifrs-bsci-ins:InsuranceContractLiabilities_CB`; the reinsurer (中再保) books the identical
economic item under the GENERIC `ifrs-full:LiabilitiesArisingFromInsuranceContracts` /
`ifrs-full:ReinsuranceAssets` and does NOT emit the `tifrs-bsci-ins:` string at all. A
canonical builder that keys the insurance-liability field on the `tifrs-bsci-ins:` concept
only would return a populated field for life/P&C and a SILENTLY EMPTY one for reinsurers — a
wrong-answer (missing liability), not a loud error.

**Why:** this is the same wrong-answer class as the `-ci` arc's `total_debt`-defaults-to-0
and the `-fh` `net_income` key mismatch — a downstream consumer reads a field that's silently
absent because the producer used a different string. It only surfaces if a test exercises the
divergent sub-shape (here the reinsurer fixture), which is why the `-ins` RED test asserts the
liability field is populated for BOTH life (primary concept) and reinsurer (fallback concept).

**How to apply:** when a canonical field can come from more than one concept string across a
family's sub-shapes, resolve it with a `_first_present(by_concept, [specific, generic])`
helper (returns the first candidate that has facts — distinct from a sum-all helper), and pin
BOTH legs with a test on a fixture of each sub-shape. Before writing the map, measure every
sub-shape (life/P&C/reinsurance here), not one — the union of concepts, and which sub-shape
uses which string, is only visible across the whole set.
See [[market-canonical-must-satisfy-consumer-field-contract]] for the consumer-side twin.
