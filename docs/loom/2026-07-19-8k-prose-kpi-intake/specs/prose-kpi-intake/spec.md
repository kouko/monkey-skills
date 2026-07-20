## ADDED Requirements

### Requirement: Mechanical prose candidate extraction with verbatim anchor
The system MUST extract operational-KPI number candidates from an 8-K EX-99
earnings-release PROSE region (text outside any `<table>`) such that each
candidate's value, verbatim quote, and character-offset span are produced
MECHANICALLY from the source exhibit text — never by an LLM.

#### Scenario: locate a prose-stated KPI
- GIVEN a cached EX-99 exhibit whose prose contains "Family daily active people (DAP) was 3.56 billion on average for December 2025"
- WHEN the prose scanner runs
- THEN it emits a candidate with value 3560000000, verbatim_quote covering the "3.56 billion" phrase, and a char_offset_span [start,end] locating that phrase in the source text

#### Scenario: value is never LLM-produced
- GIVEN a prose candidate whose numeric value was located mechanically
- WHEN the LLM proposal step runs
- THEN the LLM sets only kpi_id/unit/period and MUST NOT alter value, verbatim_quote, or char_offset_span

### Requirement: Anti-fabrication substring gate
The system MUST verify that a candidate's verbatim matched token AND its
verbatim_quote are a verbatim substring of the canonical exhibit text (the
normalized numeric value is DERIVED from the token and is never itself required
to be a substring); any candidate failing this check MUST be rejected and never
committed.

#### Scenario: LLM-invented value is rejected
- GIVEN a proposed candidate whose matched token/quote is not a verbatim substring of the canonical exhibit text
- WHEN the substring-verification gate runs
- THEN the candidate is rejected and logged, and no store append occurs

#### Scenario: normalized value need not be a substring
- GIVEN prose "Family DAP was 3.56 billion" yielding matched token "3.56 billion" and normalized value 3560000000
- WHEN the substring gate runs
- THEN it checks "3.56 billion" against the canonical text and passes, and does NOT require "3560000000" to appear in the source

#### Scenario: legitimate zero value is not dropped
- GIVEN prose stating an operational KPI whose value is exactly 0 (e.g. "net additions were 0 in the quarter")
- WHEN the scanner locates it and the substring gate runs
- THEN a candidate with value 0 is located, passes the gate, and is eligible to commit (0 is NOT treated as "no value")

### Requirement: Three-layer trust — LLM proposes semantics, human confirms
The system MUST require a human confirm-all action before any prose candidate is
committed to the store; the LLM MAY propose kpi_id/unit/period and MUST mark a
candidate `needs_semantic` when those are unfilled; the system MUST NOT auto-commit.

#### Scenario: propose marks incomplete semantics
- GIVEN a located candidate with no kpi_id yet
- WHEN the LLM proposal step cannot confidently assign kpi_id/unit/period
- THEN the candidate is marked `needs_semantic` and is not eligible for commit

#### Scenario: commit requires human confirmation
- GIVEN a proposed candidate with complete semantics
- WHEN no human confirm-all has occurred
- THEN the candidate remains in `proposed` state and is not appended to the store

#### Scenario: bypassing confirmation is forbidden
- GIVEN a located candidate
- WHEN any actor other than the human confirm step attempts to move it directly to committed
- THEN the transition is rejected as illegal

#### Scenario: human edit of a mechanical field re-runs the gate
- GIVEN a mechanically-located candidate at confirm time
- WHEN the human edits value, verbatim_quote, or char_offset_span
- THEN the substring gate MUST re-run (or the edit is forbidden), so no committed point carries a value/quote absent from the canonical source text

#### Scenario: per-field provenance distinguishes machine from human
- GIVEN a candidate whose kpi_id a human corrected at confirm while value/quote/offset stayed mechanical
- WHEN it is committed
- THEN provenance flags kpi_id as human-edited and value/quote/offset as mechanical, distinctly

### Requirement: Byte-compatible store integration with prose anchor
The system MUST commit a confirmed candidate via the existing `kpi_store.append`
with per-point provenance carrying `source_kind="prose"`, an anchor of the form
`prose:{start}-{end}`, and the verbatim_quote; it MUST NOT modify `kpi_store.py`
or `kpi_validate.py`.

#### Scenario: committed prose point carries its anchor
- GIVEN a human-confirmed prose candidate
- WHEN it is committed
- THEN the appended point carries source_kind="prose", a prose:{start}-{end} anchor, and the verbatim_quote in its provenance, and the store schema is unchanged

### Requirement: Date and period tokens are not KPI values
The system MUST NOT emit a number that functions as a date or fiscal-period label
(e.g. "Q1 2026", "fiscal 2025", a bare year) as a KPI value.

#### Scenario: period label is not a candidate
- GIVEN prose containing "In the first quarter of fiscal 2026, deliveries rose"
- WHEN the prose scanner runs
- THEN "2026" is not emitted as a KPI value candidate

#### Scenario: bounding qualifiers are not stored as bare equality values
- GIVEN prose "up to 45,000 deliveries" or "approximately 3.5 billion"
- WHEN the scanner runs
- THEN the bounding/approximation qualifier is captured or flagged and the number is NOT committed as a bare equality point value

### Requirement: Honest gaps for empty and multi-exhibit cases
The system MUST return an honest empty result when no prose KPI is found (never
fabricate), and MUST emit a gap marker without extraction when an 8-K carries two
or more exhibits (inheriting the Route B ceiling), never silently selecting one.

#### Scenario: no prose KPI found
- GIVEN an EX-99 exhibit whose prose contains no operational-KPI number
- WHEN the prose scanner runs
- THEN it returns zero candidates with an explicit "0 prose candidates" note and the pipeline succeeds

#### Scenario: two or more exhibits yields a gap
- GIVEN an earnings 8-K with two EX-99 exhibits
- WHEN prose intake runs
- THEN it emits a gap marker for that filing and extracts nothing, loudly

### Requirement: Table-versus-prose deduplication
When the same {kpi_id, period, dimensional signature} is present from both a
Route B table candidate and a prose candidate, the system MUST keep the table
point and MUST NOT emit a duplicate; conflicting values MUST be raised for human
review, never auto-resolved.

#### Scenario: table point wins on duplicate
- GIVEN a table candidate and a prose candidate for the same kpi_id and period with equal values
- WHEN both are present for one filing
- THEN only the table point is committed and the prose candidate is not appended as a second point

#### Scenario: conflicting values raise
- GIVEN a table candidate value 3.55B and a prose candidate value 3.56B for the same kpi_id and period
- WHEN dedup runs
- THEN the conflict is raised for human review and neither is auto-selected

#### Scenario: prose-versus-prose collision is arbitrated
- GIVEN two located prose candidates the LLM labels with the same {kpi_id, period, signature}
- WHEN commit runs
- THEN the collision is raised or deduped, never double-appended as two points

#### Scenario: dedup outcome is order-independent
- GIVEN a prose point committed for a KPI, THEN a Route B table run later extracts the same KPI/period
- WHEN table intake runs
- THEN the table point supersedes the prose point (or dedup runs at a barrier after both producers), so the surviving source does not depend on run order

### Requirement: Capture taxonomy [deferred]
The set of prose numbers that qualify as trackable operational KPIs is a
domain-convention question deferred for Slice A (`deferred: taxonomy is a later
hardening; Slice A default is LLM-proposed kpi_id filtered by human confirm-all`).
The system SHOULD, in the interim, treat any human-confirmed candidate as valid
regardless of a fixed taxonomy.

#### Scenario: interim no-taxonomy filter
- GIVEN a located candidate the LLM labels with a plausible operational kpi_id
- WHEN the human confirms it
- THEN it is committed even though no fixed KPI taxonomy is enforced

### Requirement: Canonical text surface and anchor durability
The system MUST define a SINGLE canonical text surface (the flattened exhibit
text) over which the char_offset_span and the substring gate operate, MUST store
alongside each committed point a content hash of that canonical text plus the
flattener/edgartools version, and MUST re-verify on read that the quote still
equals canonical_text[start:end] — flagging the anchor stale (loudly) on mismatch
rather than silently returning a drifted span.

#### Scenario: offset basis is the named canonical surface
- GIVEN a located candidate whose char_offset_span was computed over the flattened canonical text
- WHEN the candidate is committed
- THEN the anchor indexes that named canonical surface (not raw_html), and markup is excluded from the span and quote

#### Scenario: anchor drift is detected on read
- GIVEN a committed point whose stored content hash was computed under flattener v1
- WHEN the exhibit is later re-flattened under v2 shifting the text
- THEN a reader detects quote != canonical_text[start:end] and flags the anchor stale, never mapping it to different text

### Requirement: Consistent text normalization
The system MUST apply ONE normalization policy (non-breaking/thin spaces, HTML
entity decoding, smart quotes, full-width/Arabic-Indic digits) consistently to
parsing, the quote, the offset, and the substring gate, so a legitimately
formatted number is neither false-rejected nor mis-indexed.

#### Scenario: nbsp-separated number is not false-rejected
- GIVEN prose "3 560 000 subscribers" with non-breaking-space separators
- WHEN scan and substring gate run under the normalization policy
- THEN the candidate is not rejected as non-substring and its offset still maps to the canonical text

### Requirement: Word-scale magnitude parsing
The system MUST parse a trailing magnitude word (thousand / million / billion /
trillion) that follows a number into the candidate: the matched_token AND
verbatim_quote MUST include the magnitude word (so the offset anchor and the
substring gate cover the whole "3.56 billion" phrase verbatim), and the derived
numeric `value` MUST apply the multiplier (3.56 billion → 3,560,000,000). A number
with NO magnitude word is unchanged. This closes the live-observed gap where a
big-tech prose KPI (META Family DAP "3.56 billion") was captured with value 3.56
instead of 3,560,000,000 — the anti-fabrication anchor must still hold
(canonical_text[start:end] == matched_token, now spanning the magnitude word).

#### Scenario: billion magnitude scales the value, token stays verbatim
- GIVEN prose "Family DAP was 3.56 billion on average"
- WHEN the scanner locates the number and its magnitude word
- THEN the matched_token is "3.56 billion", canonical_text[start:end] == "3.56 billion", and the derived value is 3560000000

#### Scenario: million magnitude
- GIVEN prose "added 500 million monthly active users"
- WHEN the scanner runs
- THEN the matched_token is "500 million" and the derived value is 500000000

#### Scenario: a plain number without a magnitude word is unchanged
- GIVEN prose "operates 931 warehouses"
- WHEN the scanner runs
- THEN the matched_token is "931" (no magnitude word absorbed) and the derived value is 931

### Requirement: Resource bounds on scan and proposal
The system MUST enforce a maximum input size and a per-scan time bound (degrading
to a loud gap, never a hang), cap candidates emitted per exhibit, and cap or batch
LLM proposal calls; overflow MUST surface to the human rather than fan out
unboundedly.

#### Scenario: pathological input degrades to a loud gap
- GIVEN an EX-99 exhibit exceeding the size bound or containing a pathological digit run
- WHEN the prose scanner runs
- THEN it stops within the time/size bound and emits a loud gap instead of hanging, and caps candidates emitted

### Requirement: Slice-A concurrency scope and batch-commit atomicity
Slice A MUST run as a single-process serial intake (manual invocation); the
confirm-all batch commit MUST be atomic by MECHANISM (e.g. temp-file write +
atomic rename / journal) so a crash mid-commit leaves either all or none of the
batch in the store; cross-process concurrent append is OUT OF SCOPE for Slice A
and MUST be declared (a store-level uniqueness contract is deferred).

#### Scenario: crash mid-batch leaves all-or-none
- GIVEN a confirmed 3-candidate batch
- WHEN the process is killed after the first append
- THEN on restart the store contains either all three or none, never a partial batch

### Requirement: Exhibit prose is untrusted input to the proposer
The LLM proposal step MUST treat exhibit prose strictly as data; text shaped like
instructions MUST NOT alter kpi_id/unit/period assignment or the needs_semantic flag.

#### Scenario: injected directive is ignored
- GIVEN EX-99 prose containing text shaped like an instruction to the proposer
- WHEN the LLM proposal step runs
- THEN kpi_id/unit/period and needs_semantic are unaffected by the injected directive

### Requirement: Proposal infra-failure is distinct from needs_semantic
A failure, timeout, or rate-limit of the LLM proposal step MUST mark the candidate
`propose_failed` (retryable), distinct from `needs_semantic`, so a transient infra
failure is never presented to the human as a genuine semantic gap.

#### Scenario: rate-limit is not a semantic gap
- GIVEN a 5-candidate batch whose LLM proposal call rate-limits after candidate 2
- WHEN the step returns
- THEN candidates 3-5 are marked propose_failed (retryable), not needs_semantic

### Requirement: Committed point carries filing attribution and confirmer identity
A committed prose point MUST carry the accession, document, and filing date
sufficient to cite its source filing, and MUST record the confirming actor
identity and confirm timestamp.

#### Scenario: provenance is auditable and citable
- GIVEN a human-confirmed prose point
- WHEN its provenance is inspected
- THEN it carries accession, document, filing date, the confirming actor identity, and a confirm timestamp

### Requirement: Prose points do not surface in the memo (Slice-A boundary)
Committed prose points MUST land only in `kpi_store`; the existing quarterly memo
feed reads the XBRL series payload (`build_quarterly_series`), not `kpi_store`
(`kpi_memo_feed.py:13` — decoupled), so prose points MUST NOT surface in the memo
under Slice A. Any memo wiring of prose evidence is owned by Slice B.

#### Scenario: a committed prose point is absent from the memo feed
- GIVEN a prose point committed to kpi_store
- WHEN the existing quarterly memo feed runs
- THEN the memo feed output does not include the prose point (it reads the XBRL series, not the store)

### Requirement: Amended-filing conflict is raised (Slice-A minimal)
When an 8-K/A (amended earnings release) for the same period yields a prose value
differing from an already-committed prose point, the system MUST raise the
cross-accession same-period conflict for human review and MUST NOT silently retain
both or auto-overwrite; full supersession/versioning is deferred to the
longitudinal store (Slice C).

#### Scenario: amendment conflict raises
- GIVEN a committed prose point for accession X and period P
- WHEN an 8-K/A (accession X′) for period P yields a different value for the same kpi_id
- THEN the conflict is raised for human review, never silently retained-both or auto-overwritten

### Requirement: Minimal provenance capture for privacy
The committed provenance MUST store the minimal verbatim token span plus a bounded
surrounding context window sufficient to verify the datum — not an unbounded full
sentence or paragraph — to limit incidental capture of personal data (names,
compensation figures) present in SEC prose.

#### Scenario: bounded context window, not full paragraph
- GIVEN a KPI sentence embedded in a paragraph that also mentions an executive's name and compensation
- WHEN the point is committed
- THEN provenance stores the matched token span plus a bounded context window, not the entire surrounding paragraph
