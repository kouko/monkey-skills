## ADDED Requirements

### Requirement: Extract financial-statement tables as structured cells
The system MUST extract primary financial-statement tables (balance sheet,
income statement, cash flow, equity) from a filing as structured cells via
the XBRL-backed statement dataframe (edgartools), never by free-text or
regex parsing of the document body.

#### Scenario: Extract balance-sheet cells from a 10-K
- GIVEN a 10-K filing accessible via edgartools' XBRL statement API
- WHEN the balance-sheet table is extracted
- THEN each cell is returned with its concept, period, dimension, value,
  and a citation to the doc-table location (statement name + row + column)

#### Scenario: Extraction fails loud when no structured statement exists
- GIVEN a filing/statement variant with no XBRL-backed statement dataframe
  (e.g. pre-XBRL-adoption filing, or a statement edgartools cannot parse)
- WHEN extraction is attempted
- THEN the system reports an extraction failure for that statement rather
  than falling back to an LLM-guessed or regex-scraped cell value

### Requirement: Independently reconstruct the same facts from XBRL
The system MUST reconstruct the same financial-statement facts (concept,
period, dimension, value, scale, decimals) from the SEC XBRL companyfacts
API as a second, independent source — never derived from or copied out of
the doc-table extraction in the "Extract financial-statement tables"
requirement.

#### Scenario: Reconstruct a concept's value from companyfacts
- GIVEN a filing's CIK and accession number
- WHEN the same concept+period+dimension is looked up via companyfacts
- THEN a value is returned sourced independently from the XBRL fact graph,
  not from the previously extracted doc-table cell

#### Scenario: companyfacts source carries scale and decimals metadata
- GIVEN a companyfacts fact for a monetary concept
- WHEN it is reconstructed
- THEN the fact's `scale` and `decimals`/`precision` attributes are
  retained alongside the value (required input for the rounding
  cross-validation requirement below)

### Requirement: Match doc-table cell to XBRL fact by concept+period+dimension
The system MUST match each doc-table cell to its XBRL fact counterpart
using the triple of (concept, period, dimension/segment axis), and MUST
NOT match by table position, row label text, or label similarity alone.

#### Scenario: Match a non-dimensional concept by concept+period
- GIVEN a doc-table cell tagged `us-gaap:Revenues` for FY2024
- WHEN matching runs
- THEN it is paired with the XBRL fact sharing that concept and period,
  with no dimension member on either side

#### Scenario: Dimensional fact requires the dimension member to also agree
- GIVEN a doc-table cell for segment revenue (e.g. `us-gaap:Revenues` under
  `srt:ProductOrServiceAxis` member `ProductA`) for FY2024
- WHEN matching runs
- THEN the candidate XBRL fact is accepted only if its dimension member
  also equals `ProductA`; a same-concept/same-period fact under a
  different or no dimension member is NOT accepted as a match

#### Scenario: No XBRL counterpart exists for the concept+period+dimension
- GIVEN a doc-table cell whose concept+period+dimension triple has no
  matching fact in companyfacts
- WHEN matching runs
- THEN the cell is recorded as unmatched and routed to single-source
  handling rather than paired with an unrelated fact

### Requirement: Classify divergence with a tolerance band
The system MUST compute `abs_diff` and `pct_diff` between the doc value and
its matched XBRL value (after scale normalization) and classify the result
into a low/medium/high alert, where a divergence within ~1% is classified
low (rounding-consistent), a divergence above 1% and up to 5% is classified
medium, and a divergence above 5% is classified high.

#### Scenario: Divergence within the low band
- GIVEN a matched doc/XBRL pair with `pct_diff` of 0.4%
- WHEN classification runs
- THEN the alert is `low`

#### Scenario: Divergence above the high band
- GIVEN a matched doc/XBRL pair with `pct_diff` of 8%
- WHEN classification runs
- THEN the alert is `high`

#### Scenario: Undefined divergence is classified n/a, not dropped
- GIVEN a matched pair where the XBRL value is `0` (pct_diff undefined) or
  either side is `None`
- WHEN classification runs
- THEN the alert is `n/a` with a note explaining why, and the pair still
  appears in output rather than being silently omitted

### Requirement: Recognize scale/rounding as a legitimate divergence source
The system MUST apply the XBRL fact's `scale` and `decimals`/`precision`
attributes before diffing, since iXBRL tags the value as displayed
(rounded, often in millions), and MUST NOT classify a divergence that is
fully explained by display rounding as a tagging error.

#### Scenario: Millions-scale rounding stays within tolerance
- GIVEN a doc-table cell showing `$1,234` (millions) and an XBRL fact of
  `1233800000` with `scale=6, decimals=-6`
- WHEN the XBRL value is scale-normalized and diffed against the doc value
- THEN the resulting `pct_diff` falls within the low band and is annotated
  `scale/rounding`, not flagged as a tagging error

### Requirement: Do not force-match adjusted or non-GAAP figures to a GAAP tag
The system MUST NOT match or diff a doc-table adjusted/non-GAAP metric
against a similarly-labeled but conceptually different GAAP-tagged fact;
where no matching GAAP concept exists for the metric, it MUST be recorded
as single-source rather than forced into a comparison.

#### Scenario: Adjusted EBITDA has no GAAP counterpart
- GIVEN a doc-table row labeled "Adjusted EBITDA" with no us-gaap concept
  covering that non-GAAP measure
- WHEN matching runs
- THEN the cell is recorded as doc-only/no-XBRL-counterpart; it is NOT
  paired with `us-gaap:OperatingIncomeLoss` or any other GAAP concept on
  label-similarity grounds

### Requirement: Treat period/restatement mismatch and decimal-disagreement as signals, not bugs
The system MUST key matching on the reporting period and, when a later
filing's comparative figure for that period diverges from an earlier
filing's tagged value, MUST classify the divergence as a restatement
signal (citing both filing dates) rather than a data error. The system
MUST also detect decimal-disagreement per XBRL US DQC rule 2.4.1 — where a
fact's `decimals`/precision attribute is inconsistent with what its value
implies — and surface that as its own divergence category, distinct from a
plain value mismatch.

#### Scenario: Prior-year comparative restated in the current filing
- GIVEN the FY2023 comparative figure for a concept as tagged in the
  FY2023 10-K, and the same period's comparative figure as tagged in the
  FY2024 10-K
- WHEN the two are cross-checked
- THEN a divergence between them is classified `restatement-signal` with
  both filings' accession numbers cited, not surfaced as a doc-vs-XBRL
  tagging error

#### Scenario: Decimal-disagreement flagged per DQC 2.4.1
- GIVEN an XBRL fact whose `decimals` attribute implies a precision
  inconsistent with the digits actually reported for that fact
- WHEN validation runs
- THEN the fact is flagged `decimal-disagreement (DQC 2.4.1)` as a
  distinct category from a doc/XBRL value mismatch

### Requirement: Surface high-alert divergence loudly, never silently reconcile
The system MUST surface any `high`-alert divergence prominently in the
output and MUST NOT silently pick one source's value, discard the other,
or average them — both values are retained side by side, mirroring the
comps direct-vs-compute alert surfacing.

#### Scenario: High alert appears in output with both values intact
- GIVEN a matched pair classified `high`
- WHEN the divergence report is produced
- THEN the report surfaces the pair under a high-alert section with the
  doc value, the XBRL value, `pct_diff`, and both citations all present —
  no value is dropped or silently overwritten by the other

### Requirement: State single-source honesty and cite both sources for every compared number
The system MUST state explicitly — not guess or fabricate — when a
doc-table cell has no corresponding XBRL fact, recording it as
"doc-only, no XBRL counterpart" rather than omitting it or inventing a
comparison value. For every fact that IS compared, the system MUST attach
a provenance citation to both the doc-table source (filing accession +
statement name + cell location) and the XBRL source (concept id + context
ref / fact id).

#### Scenario: Doc-only cell stated, not guessed
- GIVEN an unmatched doc-table cell (no XBRL counterpart, per the matching
  requirement)
- WHEN it is included in the divergence report
- THEN it appears with status "doc-only, no XBRL counterpart" and no
  synthesized XBRL value is invented to fill the gap

#### Scenario: Every compared fact carries both citations
- GIVEN a matched and classified doc/XBRL pair
- WHEN it appears in the divergence report
- THEN it carries both a doc-table citation (accession + statement + cell)
  and an XBRL citation (concept id + context ref), regardless of alert level
