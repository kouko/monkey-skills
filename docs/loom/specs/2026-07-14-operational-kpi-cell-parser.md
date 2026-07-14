# Brief — operational-kpi slice 9: deterministic cell parser + token taxonomy

Status: brainstorming output, awaiting sign-off → `writing-plans`
Arc: US SEC primary-source layer — capability 3 (`operational-kpi`), **slice 9**. The
DETERMINISTIC-PARSE half of locate-then-parse (the LLM-LOCATE half + real HTML/companyfacts
fetches are the network/LLM layer, still ahead — they need the pilot + ground-truth). Stacked
on slice 8. Spec: `docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`.

## Design-side on-ramp

Axis 0: brownfield increment; validated change-folder covers discovery. Proceed direct.

## Problem

**Job:** *When an LLM has LOCATED a cell (a table/row/column reference) for a KPI, I want a
DETERMINISTIC parser — never the LLM — to emit the actual numeric value from that cell's raw
text, and to FAIL LOUD (no value, no guess, no interpolation, never coerce to 0) when the cell
is a non-numeric / not-meaningful token — so a number in the store always came from a real
parse, and a `NM`/`—`/blank cell becomes a review-item, never a fabricated 0.*

The LLM's job is to LOCATE (return a cell reference); this deterministic parser's job is to
EMIT THE NUMBER from that located cell. This slice builds the parser + the unparseable-cell
token taxonomy — pure compute, no LLM, no network.

## Users

**Job story:** *When the locate step hands me a cell's raw text, I want `parse_cell` to
return the number for `$1,234` / `1,234.56` / `1234` / `0` / `(123)`, and to RAISE loud for
`NM` / `n/a` / `—` / blank — so the caller (a later slice) can store the number or enqueue a
review-item, but never store a guessed or zero-filled value for a genuinely-missing cell.*

Consumers (later slices): the extraction pipeline (locate → parse → validate → store); a
parse failure is one of the confidence-gated review-enqueue triggers (slice 5's queue).

## Smallest End State

A new **pure-compute** module `investing-toolkit/skills/analysis-kpi/scripts/kpi_parse.py`
(stdlib only, no persistence/network/LLM — mirrors kpi_validate):

1. **Numeric parse** — `parse_cell(cell_text)` → a `float` for a genuinely-numeric cell:
   strips a leading currency symbol (`$`) and thousands separators (`,`), handles a decimal
   point, a leading sign, and the accounting parenthesized-negative convention (`(123)` →
   `-123.0`). A true `"0"` → `0.0` (distinct from a blank — see #2). The DETERMINISTIC parser
   emits the number; the value is read from the located cell's text, never typed by an LLM.
2. **Unparseable-cell token taxonomy (fail loud)** — `parse_cell` RAISES loud (a distinct
   `UnparseableCell`/ValueError naming the token) for the not-a-number tokens: `NM`, `n/a` /
   `N/A`, an em/en/figure dash or a bare hyphen used as "not applicable" (`—` / `–` / `-`),
   and blank / whitespace-only. These MUST NOT be coerced to `0` — a missing cell is a
   review-item, never a fabricated zero. A `0` (or `0.0`) is a real value and parses to
   `0.0`, NOT treated as missing (the true-zero-vs-blank distinction).
3. A thin **CLI** — `parse` (cell text on stdin/--arg → the number, or a non-zero
   fail-loud exit for an unparseable cell).

**Explicitly NOT in this slice:** the LLM LOCATE step (returns the cell reference — a prompt/
LLM call, the network/LLM layer); acquiring the HTML / the located cell's text from a real
filing (network fetch, needs pandas/lxml + pilot); wiring parse into the pipeline; validating
the parsed value (slice 4's kpi_validate does that). This slice = the deterministic parser +
token taxonomy ONLY.

## Current State Evidence

- **Forward (consumer):** the locate→parse→validate→store pipeline (a later slice) will call
  parse_cell on each located cell; not built.
- **Reverse (sibling pattern):** `kpi_validate.py` is the pure-compute precedent (stdlib,
  value-in/verdict-out, no persistence) — `kpi_parse.py` follows it. The parse FAILURE
  becoming a review-item reuses slice-2/5's review-queue (a later wiring slice, not here).
- **Error (fail-loud, no fabrication):** the CORE of this slice — an unparseable cell RAISES
  (no value stored/guessed/interpolated/zero-filled). Only a genuinely-numeric cell returns a
  number; a true `0` is a value, not a miss.
- **Data (shapes):** spec Requirements "Locate-then-parse parser-emits-number invariant"
  (`operational-kpi/spec.md` :64) — "a deterministic parser — never the LLM — emit the actual
  numeric value"; Scenario "Located cell is empty or non-numeric → fails loud" (:75);
  "Unparseable-cell token taxonomy is defined" (:408) — `$1,234` | `NM`/`n/a` | `—`/blank |
  true `0` handling (:411).
- **Boundary:** the `str.strip()`-then-classify is a required-string guard; reject
  whitespace-only (the recorded whitespace-guard memory applies).

Evidence paths: `investing-toolkit/skills/analysis-kpi/scripts/kpi_validate.py`,
`docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`.

## Decision

Build `kpi_parse.py`: `parse_cell(cell_text)` — a stdlib deterministic parser that strips
currency/thousands, handles decimals/sign/parenthesized-negatives, returns `0.0` for a true
zero, and RAISES loud (never coerces to 0) for `NM`/`n/a`/dash/blank/other non-numeric tokens;
+ a CLI. Pure compute, no LLM, no network.

**We will NOT:** run the LLM locate (later); fetch real HTML (later); coerce a missing token
to 0; store/guess/interpolate a value; validate the parsed number (kpi_validate does that).

## Alternatives Considered

Fork — **return a sentinel vs raise on an unparseable cell** — resolved by the spec ("fails
loud … creates a review-item") + the anti-fabrication intent: RAISE (fail loud), so a missing
cell can never silently flow on as a value. No external library fork; stdlib `re`/`decimal`.

## What Becomes Obsolete

Nothing removed — additive. Makes the "parser-emits-number, never the LLM" invariant a real,
tested boundary the later locate step must route through.

## Out of Scope

- LLM locate; HTML acquisition; pandas/lxml table extraction; pipeline wiring; validation;
  XBRL cross-check; non-US markets; archiving.

## Open Questions

1. **Percent / unit-suffixed cells** — `12.5%`, `1.2x`? The spec's named taxonomy is
   `$1,234`/`NM`/`—`/`0`; default this slice to those + plain numerics, and treat a `%`/`x`
   suffix as out-of-scope (a suffixed cell is either handled by a later enrichment or raises
   as non-plain-numeric). Confirm in plan (don't over-build speculative unit handling).
2. **Parenthesized negatives** — `(1,234)` → `-1234.0` (accounting convention). Default: yes,
   include it (common in SEC tables); confirm in plan.
