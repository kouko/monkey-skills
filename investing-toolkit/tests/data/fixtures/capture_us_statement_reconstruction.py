#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.33.1", "edgartools==5.42.0"]
# ///
"""Regenerate `us_statement_reconstruction_2026-07-26.json` — the live capture
that lets plan Task 3's statement-assembly suite run OFFLINE
(docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md).

WHAT IT ANSWERS. Task 3 assembles a filing's three statements from
`XBRL.get_statement(role)`. Nothing in this repo can answer what that call
actually returns — every existing fixture stores `companyfacts` values, which
carry no presentation role, no level, no label and no calculation parent. Four
questions, none settleable from in-repo data:

  M1 ROLE INVENTORY — a filing declares 14-132 presentation roles, and
     `presentation_roles` stores EVERY one of them verbatim, classified by
     nobody. Does one filing ever offer SEVERAL roles classifying to the SAME
     kind? That is the premise of Task 3's role-selection obligation ("prefer
     a pure income role over a combined income-and-comprehensive one when both
     exist"), and the answer is a JUDGEMENT of the live classifier, so the
     capture deliberately stores the INPUT and lets the suite re-derive the
     answer on every run. MEASURED 2026-07-26 by that re-derivation: no filing
     offered more than one role per kind — including Realty Income, whose only
     income role IS the combined one. Five filings is a small sample, and the
     multi-role case was NOT observed here, so any selection rule built on it
     is grounded in convention rather than in this capture.

     Storing the full list is also what gives the suite the ~90-170 NOTE roles
     per filing that role selection must REJECT. A capture holding only the
     accepted roles would leave that half of the work with nothing real to run
     against.

  M2 STATEMENT ROWS, VERBATIM — the full `get_statement(role)` return for every
     classified role of the two `rows` filings below. This is the suite's
     offline input: rows are captured exactly as edgartools returns them, with
     no key dropped and no value rounded, because a fixture that normalises the
     shape would stop testing the shape.

  M3 ROW-KEY CENSUS — which keys occur on the rows of each classified role, and
     on how many rows. Task 1's `is_statement_line` presumes a row carrying no
     dimension-bearing key is undimensioned, and the plan's Decision Log leaves
     Task 3 to re-confirm that against the live shape instead of inheriting it.
     The census is that confirmation, per role and per era.

  M4 DIMENSION-SIGNAL SPLIT — the census's load-bearing consequence, counted
     separately because it is the measurement that matters: how many rows carry
     a ROW-LEVEL dimension signal (`is_dimension` / `full_dimension_label` /
     `dimension_metadata` — this row IS a segment slice) versus
     `has_dimension_children` (this row is an ORDINARY consolidated line whose
     segment slices follow it). Both key names contain "dim"; they mean
     opposite things about the row that carries them. On KO FY2017's income
     role, 49 rows carry the first and 10 carry the second, and all 10 of the
     second are real statement lines — `NET OPERATING REVENUES`,
     `OPERATING INCOME`, `INCOME BEFORE INCOME TAXES` among them.

WHAT IS DELIBERATELY NOT CAPTURED: any VERDICT produced by
`is_statement_line` / `statement_kind` / `statements_for`. Those are live
functions THIS ARC IS ACTIVELY CHANGING, and a committed number produced by
one of them stops reproducing the moment it changes, with nothing surfacing the
drift — the hazard `capture_us_statement_shapes_probe.py` documents under "M4
BASELINE" and froze a vendored copy to avoid. Everything stored here is a
property of the FILING (immutable: an amendment is a new accession), so the
suite recomputes every verdict and no number here can go stale.

WHERE `statement_kind` IS STILL USED, stated precisely because an earlier
version of this note claimed it was not used at all and was two-thirds true:
this script calls it ONCE, to decide which roles are worth fetching rows for.
That is a capture-time SELECTION, and its result is not stored — no `kind`
field, no per-kind count, no per-kind grouping. `roles_captured` is a flat list
in the filing's own presentation order, and every consumer re-derives the kind
from the role URI. THE COST OF THAT SELECTION, stated as measured rather than
as hoped: if the classifier is later CHANGED to accept a role this capture
skipped, the suite does NOT reliably fail loudly. A regression simulation over
KO's 93 real roles (the `parenthetical` rejection ceasing to fire) showed
assembly staying SILENT — the already-captured role won the tie-break, so the
newly-accepted one was never fetched and its missing rows were never reached.
The `KeyError` on missing rows is a PARTIAL guard: it fires only when the newly
accepted role is also the one selected.

The real guard is
`test_a_filing_declares_one_role_per_kind_in_the_captured_sample`, which
re-derives kinds live over all 694 stored role URIs and fails the moment any
filing yields a second role for a kind — which is exactly what the simulation
above tripped. An earlier version of this paragraph claimed the loud failure;
the identical claim was corrected in the test module and survived here for one
round, which is why it now carries its evidence instead of its intention.

FILER SAMPLE — five filings, chosen per question, not for breadth:
  * KO 0000021344-18-000008 (FY2017) — the plan's acceptance case: 80 income
    rows reducing to 26 statement lines, carrying a filer-custom concept
    (`ko_UnusualOrInfrequentItemOperating`) and EPS rows outside every sum.
    All three statements captured with rows.
  * IBM 0000051143-26-000010 (FY2025) — the modern era, where filers
    disaggregate revenue through `srt:ProductOrServiceAxis` and the domain
    members appear as presentation rows carrying NO dimension label. All three
    statements captured with rows.
  * O 0000726728-26-000011 (FY2025) — the observed COMBINED income-and-
    comprehensive-income role (census only).
  * KO 0001628280-26-010047 (FY2025) — the same filer as the acceptance case,
    two eras apart, so an era difference cannot be confused with a filer
    difference (census only).
  * DUK 0001326160-18-000036 (FY2017) — a filer whose statements carry
    subsidiary registrants as dimensions, so its roles are an order of
    magnitude larger (338/510/402 rows). Census only; it is here because the
    dimension-signal split is the whole question and this is the filing where
    the signals are most numerous.

NETWORK. Hits `www.sec.gov` live through the repo's shared acquirer
`sec_edgar_client._acquire_raw_filing` (the boundary the brief names at
`sec_edgar_client.py:928`) plus `Filing.xbrl()`; identity is configured by that
module from its own `USER_AGENT`. NOT part of the offline suite — this is not a
`test_*` module and pytest never collects it. edgartools disk-caches its parse,
so a re-run against a warm cache costs ~1.3s per filing rather than ~10.7s.
Re-run by hand when the captured shape is questioned:

    PYTHONDONTWRITEBYTECODE=1 uv run --quiet --with 'edgartools==5.42.0' \\
      python investing-toolkit/tests/data/fixtures/\\
      capture_us_statement_reconstruction.py > \\
      investing-toolkit/tests/data/fixtures/\\
      us_statement_reconstruction_2026-07-26.json
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

_HERE = Path(__file__).resolve()
_REPO_ROOT = _HERE.parents[4]
_DATA_MARKETS_SCRIPTS = _REPO_ROOT / "investing-toolkit" / "skills" / "data-markets" / "scripts"
_ANALYSIS_KPI_SCRIPTS = _REPO_ROOT / "investing-toolkit" / "skills" / "analysis-kpi" / "scripts"
sys.path.insert(0, str(_DATA_MARKETS_SCRIPTS))
sys.path.insert(0, str(_ANALYSIS_KPI_SCRIPTS))
import sec_edgar_client as sec  # noqa: E402
from kpi_us_statement_shape import statement_kind  # noqa: E402

sec._QUIET = True

# (accession, ticker, what the filing is here to answer, capture rows?)
FILINGS = (
    ("0000021344-18-000008", "KO", "FY2017 — the plan's 80->26 acceptance case", True),
    ("0000051143-26-000010", "IBM", "FY2025 — the modern ProductOrServiceAxis era", True),
    ("0000726728-26-000011", "O", "FY2025 — the observed combined income role", False),
    ("0001628280-26-010047", "KO", "FY2025 — same filer as the acceptance case, later era", False),
    ("0001326160-18-000036", "DUK", "FY2017 — subsidiary registrants carried as dimensions", False),
)

# Keys whose truthiness says THIS ROW IS A SEGMENT SLICE. Observed spellings
# only — the census (M3) is what proves the list is complete for a filing, and
# it is recomputed on every re-run rather than trusted from last time.
_ROW_LEVEL_DIMENSION_KEYS = ("is_dimension", "full_dimension_label", "dimension_metadata")

# The key that means the OPPOSITE — this row is an ordinary consolidated line
# and its segment slices follow it in document order. Counted separately from
# the keys above, because the two are indistinguishable to any rule that only
# looks for the substring "dim" in a key name.
_CHILD_DIMENSION_KEY = "has_dimension_children"


def _row_census(rows: list[dict]) -> dict:
    """M3 + M4 for one role: key occurrence counts, and the dimension-signal
    split that the key names alone cannot distinguish."""
    keys = Counter()
    for row in rows:
        keys.update(row.keys())
    row_level = [
        row for row in rows
        if any(row.get(key) for key in _ROW_LEVEL_DIMENSION_KEYS)
    ]
    child_level = [row for row in rows if row.get(_CHILD_DIMENSION_KEY)]
    return {
        "n_rows": len(rows),
        "key_occurrences": dict(sorted(keys.items())),
        "keys_containing_dim": sorted(k for k in keys if "dim" in k.lower()),
        "n_rows_row_level_dimensioned": len(row_level),
        "n_rows_with_dimensioned_children": len(child_level),
        "n_rows_abstract": sum(1 for row in rows if row.get("is_abstract")),
        # The labels are the readable evidence that the two signals mean
        # opposite things: these are consolidated statement lines, not slices.
        "labels_of_rows_with_dimensioned_children": [
            row.get("label") for row in child_level
        ],
    }


def _capture_one(accession: str, ticker: str, why: str, with_rows: bool) -> dict:
    filing = sec._acquire_raw_filing(accession)
    if isinstance(filing, dict):  # a loud acquisition-error slot
        return {"accession": accession, "ticker": ticker, **filing}
    xbrl = filing.xbrl()
    if xbrl is None:
        return {"accession": accession, "ticker": ticker,
                "error": "filing carries no XBRL"}

    # EVERY presentation role, verbatim and in the filing's own order — not
    # just the ones that classify. Two reasons, both learned in review:
    # a stored per-kind COUNT would freeze this classifier's verdict, so a
    # regression that started accepting a second role per kind would keep the
    # test green while its stated grounding quietly became false; and a capture
    # holding only accepted roles gives the suite no real note role to REJECT,
    # leaving half of role selection unexercised offline. ~130 strings against
    # 564KB of rows, and immutable.
    roles = [str(role) for role in xbrl.presentation_roles]

    captured = []
    for role in roles:
        if statement_kind(role) is None:
            continue
        rows = list(xbrl.get_statement(role))
        entry = {"role": role, "census": _row_census(rows)}
        if with_rows:
            entry["rows"] = rows
        captured.append(entry)

    return {
        "accession": accession,
        "ticker": ticker,
        "why_this_filing": why,
        "form": filing.form,
        "cik": filing.cik,
        "filing_date": str(filing.filing_date),
        "period_of_report": str(filing.period_of_report),
        "document_url": filing.filing_url,
        "presentation_roles": roles,
        "rows_captured": with_rows,
        "roles_captured": captured,
    }


def main() -> None:
    filings = [_capture_one(*spec) for spec in FILINGS]
    doc = {
        "_capture": {
            "what": (
                "Live capture of XBRL.get_statement(role) for the three "
                "statements of five 10-K filings across two eras, grounding "
                "plan Task 3 (statement assembly) in "
                "docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md. "
                "Rows are verbatim: no key dropped, no value rounded."
            ),
            "captured_at": "2026-07-26",
            "sdk": "edgartools==5.42.0",
            "endpoints": ["www.sec.gov (via edgartools Filing.xbrl())"],
            "acquirer": (
                "sec_edgar_client._acquire_raw_filing — the repo's shared "
                "accession->Filing boundary; no new network primitive."
            ),
            "regenerate": (
                "investing-toolkit/tests/data/fixtures/"
                "capture_us_statement_reconstruction.py"
            ),
            "not_captured": (
                "No VERDICT from is_statement_line / statement_kind / "
                "statements_for: no kind field, no per-kind count, no "
                "per-kind grouping. Those are live functions this arc "
                "changes, and a committed verdict from one of them stops "
                "reproducing the moment it changes with nothing surfacing "
                "the drift (see capture_us_statement_shapes_probe.py 'M4 "
                "BASELINE'). statement_kind IS called once at capture time, "
                "to select which roles are worth fetching rows for; that "
                "selection is not stored, and the module docstring states "
                "what it costs. Every value here is a property of the "
                "FILING, which is immutable (an amendment is a new "
                "accession), so the suite recomputes every verdict."
            ),
            "role_multiplicity": (
                "M1: re-derive it — `presentation_roles` holds every role "
                "each filing declares, verbatim and unclassified, so the "
                "suite answers 'how many roles per kind?' by running the "
                "live classifier over that list rather than reading a "
                "frozen count. As measured on 2026-07-26 the answer was one "
                "role per kind for all five filings; the multi-role case "
                "Task 3's role-selection obligation is written for was NOT "
                "observed here. Five filings is a small sample and this "
                "records the absence rather than claiming it cannot happen."
            ),
            "dimension_signal_split": (
                "M4: `is_dimension`/`full_dimension_label`/"
                "`dimension_metadata` mark a row that IS a segment slice; "
                "`has_dimension_children` marks an ordinary consolidated line "
                "whose slices follow it. All four key names contain 'dim'. "
                "See labels_of_rows_with_dimensioned_children on each role "
                "for what the second group actually contains."
            ),
        },
        "filings": filings,
    }
    print(json.dumps(doc, indent=1, default=str))


if __name__ == "__main__":
    main()
