## ADDED Requirements

### Requirement: Filing Acquisition via edgartools
The system MUST acquire 10-K, 10-Q, and 8-K filings for a resolved ticker/CIK using the edgartools library (key-free, MIT), replacing the legacy raw-HTML fetch + regex parse path.

#### Scenario: Successful filing acquisition
- GIVEN a valid US ticker or CIK with a filed 10-K/10-Q/8-K matching the requested accession or form filter
- WHEN the narrative action requests that filing via edgartools
- THEN the system returns a filing object carrying accession, CIK, form, filingDate, period_of_report, primaryDocument, and a reconstructable SEC Archives URL

#### Scenario: Ticker or CIK not found
- GIVEN a ticker or CIK that does not resolve to a registered SEC filer
- WHEN the narrative action requests filings for that identifier
- THEN the system returns an error slot naming the unresolved identifier, and does not fabricate an empty-but-silent filing result

#### Scenario: Requested form type not available
- GIVEN a resolved filer that has never filed the requested form type (e.g. no 8-K on record) within the lookup window
- WHEN the narrative action requests that form type
- THEN the system returns a loud "form not available" result distinct from a resolution error, and does not silently substitute a different form or a different filing

### Requirement: Full-Body Item Segmentation (10-K/10-Q)
The system MUST segment a 10-K or 10-Q filing's primary document into ALL items present in that document — enumerated via edgartools' typed-object item API (`obj.items`) — emitting one section object per item, NOT a curated analysis-selected subset. This is a pure data-acquisition contract: the data layer preserves every body item (Business, Risk Factors, MD&A, Financial Statements, Controls, Governance, etc.) and defers the read/relevance decision to downstream consumers; it MUST NOT filter to a hand-picked item set. Segmentation uses edgartools' section API, never regex header-detection.

#### Scenario: 10-K all-item segmentation
- GIVEN a 10-K primary document whose `obj.items` enumerates the full item set (e.g. Item 1 through Item 16, including 1A/1B/1C/7A/9A/9B/9C)
- WHEN the system segments it
- THEN it emits a distinct section object for EVERY enumerated item — not only MD&A + Risk Factors — each carrying its own item id and extracted text (e.g. Item 1 Business, Item 7 MD&A, Item 8 Financial Statements are all present)

#### Scenario: 10-Q all-item segmentation
- GIVEN a 10-Q primary document
- WHEN the system segments it
- THEN it emits a distinct section object for every item `obj.items` enumerates, each carrying its item id and extracted text

#### Scenario: Enumerated item absent or empty in this filing
- GIVEN an enumerated item whose text is absent (`None`) in this specific filing (e.g. an item incorporated by reference or permitted-omitted)
- WHEN segmentation runs
- THEN the system returns a per-section error slot naming the item, rather than emitting an empty or fabricated section for it

### Requirement: 8-K Full-Item Segmentation with Exhibit-Following
The system MUST segment an 8-K by ALL reported item codes it declares (enumerated via `obj.items`), emitting one section per reported item — not a curated subset. For an item whose substantive content lives in an Exhibit 99.x (the results/announcement items 2.02/7.01/8.01, where the 8-K body carries only the announcement), the section text MUST be sourced from that item's Exhibit 99.x; every other reported item carries its own body text. No attachment other than an exhibit-bearing item's own Exhibit 99.x is fetched (other exhibits — material contracts, certifications, XBRL — are out of scope for this narrative layer).

#### Scenario: 8-K all reported items, exhibit-bearing item sourced from Exhibit 99.1
- GIVEN an 8-K reporting multiple items (e.g. Item 2.02 and Item 9.01) with an attached Exhibit 99.1
- WHEN the system segments it
- THEN it emits a section object for EVERY reported item; the exhibit-bearing item (2.02) is sourced from Exhibit 99.1 with the exhibit filename in provenance, and the other reported items carry their own body text

#### Scenario: 8-K Item 7.01/8.01 with Exhibit 99.x present
- GIVEN an 8-K filing reporting item 7.01 or item 8.01 with an attached Exhibit 99.x
- WHEN the system segments it
- THEN it emits a section object per reported item whose text is sourced from the corresponding exhibit, not from the 8-K body alone

### Requirement: 8-K Missing-Exhibit Gap
The system MUST treat an 8-K item (2.02/7.01/8.01) that is reported in the filing's items list but lacks a corresponding Exhibit 99.x attachment as a loud extraction gap, never a silent skip.

#### Scenario: Reported item without exhibit
- GIVEN an 8-K filing whose submissions metadata lists item 2.02 but whose accession folder contains no Exhibit 99.x document
- WHEN the system segments that item
- THEN it emits an explicit gap/error slot for that item, naming the accession and item code, rather than omitting the item from output or emitting an empty section

### Requirement: Section Provenance Completeness
Every emitted section MUST carry a complete provenance tuple: accession number, CIK, item id, filingDate and period_of_report (where available), and a reconstructable SEC Archives URL to the source document.

#### Scenario: Provenance tuple present on every section
- GIVEN any successfully segmented section from a 10-K, 10-Q, or 8-K
- WHEN the section is emitted
- THEN its provenance carries accession, CIK, item id, filingDate/period_of_report, and a URL of the form `https://www.sec.gov/Archives/edgar/data/{cik}/{accession-no-dashes}/{document}` that is reconstructable without an additional lookup

### Requirement: Fail-Loud Per-Section Extraction
The system MUST surface a section that cannot be extracted as a per-section error slot feeding `pack_inventory`/`_status`, and MUST NOT emit a fabricated or silently empty section in its place.

#### Scenario: One section fails within a multi-section filing
- GIVEN a 10-K where Item 7 extracts successfully but Item 1A extraction throws or returns unparseable content
- WHEN the narrative action completes
- THEN Item 7's section object is emitted normally, Item 1A's slot carries an explicit error, and the overall action result classifies as partial (feeding `_status`) rather than reporting success

#### Scenario: All requested sections fail
- GIVEN a filing whose primary document cannot be fetched or parsed at all
- WHEN the narrative action runs
- THEN every requested section slot carries an explicit error and no top-level success is claimed

### Requirement: Paths-Not-Content Section Emission
The system MUST write each extracted section's text to a file and MUST return the file path in the section object rather than embedding the full section text inline in the action's JSON output.

#### Scenario: Section text written to file
- GIVEN a successfully segmented section
- WHEN it is emitted
- THEN the section object carries a `text_path` field pointing to a file containing the section text, and the JSON result itself does not inline that text

### Requirement: CLI Surface Preserved Across the edgartools Migration
The system MUST preserve the existing `--action narrative` CLI action name and its accession-based invocation contract while replacing the internal implementation (`parse_item_sections`, `action_narrative` regex internals, exhibit-index skip heuristic) with edgartools-based acquisition and segmentation.

#### Scenario: Existing CLI invocation still resolves
- GIVEN a caller invoking `sec_edgar_client.py --action narrative --accession <accession>` as before the migration
- WHEN the command runs against the migrated implementation
- THEN it returns a result under the same `--action narrative` contract (accession/cik/form/filingDate/sections keys), now populated via edgartools instead of the retired regex parser

#### Scenario: Regex internals no longer on the code path
- GIVEN the migrated implementation
- WHEN any 10-K/10-Q/8-K narrative section is segmented
- THEN the TOC-vs-body regex heuristic (`parse_item_sections`, `_ITEM_HEADER_RE`) is not invoked — edgartools' own section API performs segmentation instead

<!-- critic-found (completeness-critic round 1) -->

### Requirement: SEC EDGAR fair-access compliance
The system MUST identify itself and respect SEC rate limits on every request to sec.gov (filing acquisition and companyfacts/XBRL alike).

#### Scenario: Missing User-Agent is rejected before send
- GIVEN a fetch to sec.gov
- WHEN no compliant `User-Agent: <app> <contact-email>` header is configured
- THEN the request MUST be rejected before send, not left to a library default

#### Scenario: Rate-limit backoff
- GIVEN sustained requests approaching the ~10 req/s SEC ceiling
- WHEN a 429 or 403 is returned
- THEN the system MUST back off with jitter and retry, not fail immediately nor silently drop the fetch

#### Scenario: Filing cache avoids re-fetch
- GIVEN an accession already fetched within the cache window
- WHEN the same stage re-runs
- THEN it MUST read the cached copy instead of re-hitting SEC

### Requirement: Furnished-vs-filed status propagates to the memo
The system MUST tag each 8-K-sourced section with its legal disclosure status so downstream consumers can weight it.

#### Scenario: Exhibit 99.x marked furnished
- GIVEN a section sourced from an 8-K Item 2.02/7.01 Exhibit 99.x
- WHEN the section provenance is emitted
- THEN it MUST carry `disclosure_status: furnished` (distinct from `filed`), and the memo-feed surfaces it

### Requirement: Distinct acquisition failure classes
The system MUST distinguish transient/library failure modes from content gaps.

#### Scenario: Network timeout is its own class
- GIVEN a fetch that exceeds the timeout
- WHEN it is abandoned
- THEN it MUST classify as `timeout` (retryable), not merge into generic `gap`/`error`

#### Scenario: edgartools version-drift is caught, not silently trusted
- GIVEN an edgartools upgrade that changes a section API surface
- WHEN a segmented section returns an unexpected shape
- THEN the system MUST fail loud on the shape mismatch rather than emit possibly-wrong section text
