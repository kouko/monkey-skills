"""RED-first tests for the prose KPI candidate producer (kpi_prose_candidates.py).

Task 4 (Part 1 walking skeleton) pins the ANTI-FABRICATION substring gate: a pure
predicate that a candidate's verbatim matched TOKEN and its verbatim_quote are
substrings of the canonical exhibit text. The NORMALIZED numeric value is DERIVED
from the token and is NEVER itself required to appear in the text — this is what
stops an LLM (or any layer) from committing a value not present in the source.

No `@req` tag: this dispatch's plan (docs/loom/plans/2026-07-19-8k-prose-kpi-
intake-part-1.md) binds tasks by "Brief item covered", not by registered
loom-spec REQ-ids (same convention as test_kpi_8k_candidates_propose.py), so
there is no id in the living-spec namespace to bind to.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent
_SCRIPT = (
    _TESTS_DIR.parent
    / "skills"
    / "analysis-kpi"
    / "scripts"
    / "kpi_prose_candidates.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("kpi_prose_candidates", _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_gate_checks_token_rejects_invented():
    module = _load_module()

    # Canonical prose surface (the substring gate index). Note the printed token
    # carries thousands separators; the comma-stripped normalized value does NOT
    # appear anywhere in this text.
    canonical_text = (
        "The company had 1,576,000 full-time employees as of December 31, 2024."
    )

    # A candidate whose verbatim matched token IS present in the source.
    grounded = {
        "matched_token": "1,576,000",
        "verbatim_quote": "had 1,576,000 full-time employees",
        "value": 1576000,  # normalized (comma-stripped) — DERIVED, not verbatim
        "char_offset_span": [16, 25],
    }
    # A candidate whose token was invented — absent from the source text.
    invented = {
        "matched_token": "9,999,999",
        "verbatim_quote": "had 9,999,999 full-time employees",
        "value": 9999999,
        "char_offset_span": [16, 25],
    }

    # Precondition proving the gate cannot be leaning on the normalized value:
    # the comma-stripped "1576000" is genuinely NOT a substring of the source.
    assert str(grounded["value"]) not in canonical_text

    # Grounded token + quote are verbatim substrings -> gate admits it, EVEN
    # THOUGH the normalized numeric value is absent from the text.
    assert module.passes_substring_gate(grounded, canonical_text) is True

    # Invented token is absent from the source -> gate rejects it. This is the
    # load-bearing anti-fabrication rail.
    assert module.passes_substring_gate(invented, canonical_text) is False


_CANON = "The company had 1,576,000 full-time employees as of December 31, 2024."


def test_gate_rejects_missing_or_empty_matched_token():
    # Fail-CLOSED: a candidate with no verbatim token grounds NOTHING. Missing,
    # None, and "" all mean "no grounding" -> reject. The "" case is the fail-OPEN
    # hole (`"" in text` is always True) this pins shut; deleting the guard breaks
    # a test.
    module = _load_module()
    quote = "had 1,576,000 full-time employees"

    missing = {"verbatim_quote": quote}  # no matched_token key at all
    none_tok = {"matched_token": None, "verbatim_quote": quote}
    empty_tok = {"matched_token": "", "verbatim_quote": quote}

    assert module.passes_substring_gate(missing, _CANON) is False
    assert module.passes_substring_gate(none_tok, _CANON) is False
    assert module.passes_substring_gate(empty_tok, _CANON) is False


def test_gate_rejects_missing_or_empty_verbatim_quote():
    # Symmetric fail-CLOSED for the quote field. "" is the fail-OPEN case.
    module = _load_module()
    token = "1,576,000"

    missing = {"matched_token": token}  # no verbatim_quote key at all
    none_quote = {"matched_token": token, "verbatim_quote": None}
    empty_quote = {"matched_token": token, "verbatim_quote": ""}

    assert module.passes_substring_gate(missing, _CANON) is False
    assert module.passes_substring_gate(none_quote, _CANON) is False
    assert module.passes_substring_gate(empty_quote, _CANON) is False


def test_gate_requires_both_token_and_quote_present():
    # AND semantics: BOTH the token AND the quote must be substrings. Each partial
    # case (one present, the other a non-substring) must be rejected -> mutating
    # `and`->`or` at the return breaks this test.
    module = _load_module()

    # Token grounded, quote invented (absent from source).
    token_only = {
        "matched_token": "1,576,000",
        "verbatim_quote": "had 9,999,999 part-time contractors",
    }
    # Quote grounded, token invented (absent from source).
    quote_only = {
        "matched_token": "9,999,999",
        "verbatim_quote": "had 1,576,000 full-time employees",
    }

    assert module.passes_substring_gate(token_only, _CANON) is False
    assert module.passes_substring_gate(quote_only, _CANON) is False


def test_propose_emits_raw_candidate_needs_semantic():
    # Task 3 (Part 1 walking skeleton): the MECHANICAL producer. propose() turns
    # located number tokens (exhibit_prose.locate_numbers) into RAW candidate
    # points carrying ONLY mechanical fields — value DERIVED from the token,
    # verbatim_quote, char_offset_span — with every semantic slot NULL and
    # needs_semantic=True. The anti-fabrication contract: value + coordinates are
    # set mechanically here and NEVER pass through an LLM.
    module = _load_module()

    canonical_text = "The company had 1,576,000 employees as of year end."

    candidates = module.propose(canonical_text)

    # Single number token in the fixture -> exactly one candidate. Asserting the
    # total count (not just the matching subset) means a spurious extra candidate
    # cannot pass silently.
    assert len(candidates) == 1, "one number token -> one candidate"

    matches = [c for c in candidates if c["value"] == 1576000]
    assert len(matches) == 1, "exactly one candidate for the 1,576,000 token"
    candidate = matches[0]

    # Mechanical fields — all SET by propose, DERIVED from the located token.
    assert candidate["matched_token"] == "1,576,000"
    # value is the comma-stripped int, DERIVED from the token (not independently
    # supplied) — structural proof that value is never LLM-produced.
    assert candidate["value"] == 1576000
    assert candidate["value"] == int(candidate["matched_token"].replace(",", ""))
    # char_offset_span anchors back to the source: text[start:end] == token.
    start, end = candidate["char_offset_span"]
    assert canonical_text[start:end] == candidate["matched_token"]
    # In Part 1 the verbatim_quote IS the matched token.
    assert candidate["verbatim_quote"] == candidate["matched_token"]
    assert candidate["source_kind"] == "prose"

    # Semantic slots NULL, awaiting the LLM layer -> needs_semantic flagged.
    assert candidate["kpi_id"] is None
    assert candidate["unit"] is None
    assert candidate["period"] is None
    assert candidate["needs_semantic"] is True

    # The mechanically-produced candidate satisfies the EXISTING Task 4 gate:
    # its verbatim token + quote are literal substrings of the source. This ties
    # propose's output to the anti-fabrication rail.
    assert module.passes_substring_gate(candidate, canonical_text) is True


def test_normalize_value_decimal_token_becomes_float():
    # Coverage for the DECIMAL branch of _normalize_value (the integer branch is
    # exercised by the propose/gate tests; the float branch was untested). A
    # decimal token like "3.56" normalizes to the float 3.56 — the comma-stripped
    # value is DERIVED from the token, and a decimal has no thousands separators
    # to strip, so value and token share the same digits but different types.
    module = _load_module()

    assert module._normalize_value("3.56") == 3.56
    assert isinstance(module._normalize_value("3.56"), float)
    # A thousands-separated decimal: commas stripped, then parsed as float.
    assert module._normalize_value("1,234.5") == 1234.5
    assert isinstance(module._normalize_value("1,234.5"), float)
    # The integer branch stays int (not float) — no spurious "." introduced.
    assert module._normalize_value("1,576,000") == 1576000
    assert isinstance(module._normalize_value("1,576,000"), int)


def test_commit_requires_confirm():
    # Task 6 (Part 1 walking skeleton): the tier-① trust GATE. A prose candidate
    # is accepted for commit ONLY after an explicit human confirm-all. There is NO
    # auto-commit: confirmed defaults False (fail-CLOSED). Moving a candidate
    # located->committed WITHOUT the human confirm step is ILLEGAL and refused —
    # that is the three-layer boundary (mechanical produce -> LLM propose -> HUMAN
    # confirm) keeping unratified candidates out of the store.
    #
    # Scope: THIS pins the GATE (which candidates MAY commit), not the kpi_store
    # append (Task 7). commit() returns the accepted-for-commit set.
    module = _load_module()

    candidates = [
        {
            "matched_token": "1,576,000",
            "verbatim_quote": "had 1,576,000 full-time employees",
            "value": 1576000,
            "char_offset_span": [16, 25],
            "source_kind": "prose",
            "kpi_id": "employees_full_time",  # LLM-labeled + human-confirmed
            "unit": "count",
            "period": "2024-12-31",
            "needs_semantic": False,
        }
    ]

    # confirmed=False -> NO committed points (nothing accepted for append). The
    # fail-CLOSED, no-auto-commit direction.
    assert module.commit(candidates, confirmed=False) == []

    # confirmed OMITTED -> same refusal. The default must be fail-CLOSED, so a
    # bypass that just calls the accept path without the confirm arg commits
    # nothing (bypass illegal).
    assert module.commit(candidates) == []

    # confirmed=True -> the candidates are accepted for commit. This is the ONLY
    # path a candidate reaches "committed" — through the explicit human confirm.
    accepted = module.commit(candidates, confirmed=True)
    assert accepted == candidates


def test_commit_no_taxonomy_filter_admits_confirmed_candidate():
    # Interim no-taxonomy filter: a human-confirmed candidate is accepted for
    # commit REGARDLESS of its kpi_id — there is NO fixed-taxonomy check gating
    # commit (taxonomy is a deferred hardening). An arbitrary/plausible LLM-labeled
    # kpi_id, absent from any fixed taxonomy, still commits once the human
    # confirmed. The confirm step is the only gate; taxonomy membership is not.
    module = _load_module()

    plausible = [
        {
            "matched_token": "42",
            "verbatim_quote": "shipped 42 gigawatts",
            "value": 42,
            "char_offset_span": [8, 10],
            "source_kind": "prose",
            "kpi_id": "energy_shipped_gw_not_in_any_taxonomy",  # arbitrary id
            "unit": "GW",
            "period": "2024-Q4",
            "needs_semantic": False,
        }
    ]

    accepted = module.commit(plausible, confirmed=True)
    assert accepted == plausible, "no taxonomy check gates a confirmed candidate"


def test_build_candidates_preserves_decimal_matched_token():
    # The pure transform seam (build_candidates) wraps already-crossed located
    # numbers into candidates. A decimal token flows through as a float `value`
    # while `matched_token` stays the VERBATIM printed token "3.56" (the value is
    # NOT required to appear as a substring of the token — 3.56 the float and
    # "3.56" the token happen to share digits, but the contract is verbatim
    # token in / derived value out).
    module = _load_module()

    located = [{"token": "3.56", "start": 4, "end": 8}]
    candidates = module.build_candidates(located)

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate["matched_token"] == "3.56"
    assert candidate["verbatim_quote"] == "3.56"
    assert candidate["value"] == 3.56
    assert isinstance(candidate["value"], float)
    assert candidate["char_offset_span"] == [4, 8]
    assert candidate["source_kind"] == "prose"
    assert candidate["needs_semantic"] is True


def test_zero_value_survives_gate_and_commit(tmp_path, monkeypatch):
    # Task 5 (falsy-zero pin): a prose KPI whose value is exactly 0 ("net
    # additions were 0 in the quarter") must be LOCATED, PASS the substring gate,
    # and remain eligible to COMMIT + STORE — 0 must NOT be read as "no value" and
    # silently dropped. This is the repo's known falsy-zero trap
    # (docs/loom/memory/falsy-guard-rejects-legitimate-zero-provenance.md): a
    # `if not value` / `if not candidate["value"]` guard ANYWHERE on the numeric
    # value path would drop a legitimate 0. By inspection no such guard exists
    # today, so this is a GREEN-on-arrival REGRESSION GUARD, not RED-then-GREEN:
    # it fails the moment a falsy-value guard is introduced on any of the seams
    # below (produce / gate / commit / store).
    #
    # NOTE the guard-DISCRIMINATION: the string grounding fields (matched_token /
    # verbatim_quote) DO legitimately fail-CLOSED on falsy (empty ""); this test
    # pins only that the NUMERIC value is exempt from that treatment — a 0 value
    # with a grounded token "0" flows end-to-end.
    module = _load_module()

    # "0" is a genuine substring of this canonical prose surface (offset 19).
    canonical_text = "Net additions were 0 in the quarter, flat versus prior year."
    assert canonical_text[19:20] == "0"

    # --- PRODUCE seam: _normalize_value("0") -> int 0, build_candidates keeps it.
    # A `if not value` guard added here (skipping the candidate) would empty the
    # list and fail len == 1.
    produced = module.build_candidates([{"token": "0", "start": 19, "end": 20}])
    assert len(produced) == 1, "the 0-token located number -> exactly one candidate"
    zero_candidate = produced[0]
    assert zero_candidate["value"] == 0
    assert zero_candidate["value"] is not None, "0 is a value, not absence"
    assert zero_candidate["matched_token"] == "0"

    # --- GATE seam: token "0" is a substring -> gate admits it. The gate must NOT
    # read the falsy numeric value; a `if not candidate["value"]: return False`
    # added to passes_substring_gate would wrongly reject and fail this assert.
    assert module.passes_substring_gate(zero_candidate, canonical_text) is True

    # A CONFIRMED value-0 candidate (human filled the semantic slots + filing
    # attribution) to exercise the commit + store seams end-to-end.
    confirmed = {
        "matched_token": "0",
        "verbatim_quote": "Net additions were 0 in the quarter",
        "value": 0,
        "char_offset_span": [19, 20],
        "source_kind": "prose",
        "kpi_id": "net_additions",  # LLM-labeled + human-confirmed
        "unit": "count",
        "period": "2024-Q4",
        "needs_semantic": False,
        "source_accession": "0000320193-24-000999",
        "source_document": "8-K/EX-99.1",
        "filing_date": "2024-10-31",
        "as_of": "2024-10-31",  # accession-derived (NOT wall-clock)
    }

    # --- COMMIT-GATE seam: a confirmed value-0 candidate is ACCEPTED, not filtered.
    # A `if not c["value"]: continue` added to commit would drop it -> accepted []
    # and this assert fails.
    accepted = module.commit([confirmed], confirmed=True)
    assert accepted == [confirmed], "the value-0 candidate is accepted for commit"

    # --- STORE-APPEND seam: the value-0 point LANDS in the durable store, not
    # skipped. Hermetic: KPI_STORE_DIR -> tmp_path (mirrors T7) so the real store
    # is never touched.
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))
    scripts_dir = str(_SCRIPT.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    sys.modules.pop("kpi_store", None)
    import kpi_store  # noqa: E402

    summary = module.commit_to_store(
        [confirmed], company="AAPL",
        confirmer="kouko", confirmed_at="2026-07-20T10:00:00Z", confirmed=True,
    )
    assert summary["committed"] == 1, "the value-0 confirmed candidate is appended"

    point = kpi_store.query_latest("AAPL", "net_additions", "2024-Q4")
    assert point is not None, "the value-0 prose point must be in the store, not dropped"
    # The load-bearing assert: the stored value is exactly 0 (not None, not absent).
    # A falsy-value guard on _prose_candidate_to_point / commit_to_store would drop
    # the point (query None) or lose the value here.
    assert point["value"] == 0
    assert point["value"] is not None
    assert point["source_cell_ref"] == "prose:19-20"


def test_committed_prose_point_carries_anchor_and_attribution(tmp_path, monkeypatch):
    # Task 7 (Part 1 walking skeleton): the durable store-append path. This closes
    # the three-layer skeleton — mechanical produce (T3) -> LLM propose -> HUMAN
    # confirm (T6) -> DURABLE store append (here). A confirmed prose candidate,
    # committed with an explicit confirmer + confirm timestamp, becomes a
    # schema-valid point in the EXISTING tier-① kpi_store, appended through the
    # UNMODIFIED kpi_store.append (its provenance / accession-derived-as_of guards
    # are honored, never weakened). Queried back, the point must carry:
    #   - source_kind="prose"
    #   - a "prose:{start}-{end}" offset anchor (source_cell_ref-analog) built from
    #     the candidate's char_offset_span — a truthy string, so the store's
    #     falsy-provenance guard admits it (unlike a bare 0)
    #   - the verbatim_quote (so the surfaced number stays citable to source bytes)
    #   - filing attribution (accession / document / filing_date) + confirmer
    #     identity + confirm timestamp
    #   - an as_of that is the ACCESSION-derived filing date, DISTINCT from the
    #     wall-clock confirm timestamp (determinism: both passed IN, never read
    #     from the clock inside the function).
    #
    # Hermetic: KPI_STORE_DIR is redirected to tmp_path (mirrors
    # test_prose_memo_boundary.py) so nothing touches the real durable store.
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    # Share the SAME kpi_store module the producer's lazy sibling-import resolves:
    # put the scripts dir on sys.path and import kpi_store under its real name
    # (mirrors test_prose_memo_boundary._load_modules), so the query-back below
    # reads the very file the append wrote.
    scripts_dir = str(_SCRIPT.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    sys.modules.pop("kpi_store", None)
    import kpi_store  # noqa: E402

    module = _load_module()

    # A CONFIRMED prose candidate: the human filled the semantic slots
    # (kpi_id/unit/period) at confirm, atop the mechanical fields (verbatim token +
    # quote + char_offset_span + value) and the filing attribution + accession-
    # derived as_of carried from the filing fetch.
    candidate = {
        "matched_token": "1,576,000",
        "verbatim_quote": "had 1,576,000 full-time employees",
        "value": 1576000,
        "char_offset_span": [16, 25],
        "source_kind": "prose",
        "kpi_id": "employees_full_time",  # LLM-labeled + human-confirmed
        "unit": "count",
        "period": "2024-12-31",
        "needs_semantic": False,
        "source_accession": "0000320193-24-000999",
        "source_document": "8-K/EX-99.1",
        "filing_date": "2024-10-31",
        "as_of": "2024-01-01",  # accession-derived (NOT wall-clock)
    }

    confirmer = "kouko"
    confirmed_at = "2026-07-20T10:00:00Z"  # wall-clock confirm ts, passed IN

    summary = module.commit_to_store(
        [candidate], company="AAPL",
        confirmer=confirmer, confirmed_at=confirmed_at, confirmed=True,
    )
    assert summary["committed"] == 1, "the one confirmed candidate is appended"

    point = kpi_store.query_latest("AAPL", "employees_full_time", "2024-12-31")
    assert point is not None, "the confirmed prose candidate must be in the store"

    # Prose source marker + the offset anchor (source_cell_ref-analog).
    assert point["source_kind"] == "prose"
    assert point["source_cell_ref"] == "prose:16-25", (
        "the anchor is prose:{start}-{end} from char_offset_span [16, 25]"
    )

    # The verbatim quote is carried so a surfaced number stays citable.
    assert point["verbatim_quote"] == "had 1,576,000 full-time employees"
    assert point["value"] == 1576000

    # Filing attribution.
    assert point["source_accession"] == "0000320193-24-000999"
    assert point["source_document"] == "8-K/EX-99.1"
    assert point["filing_date"] == "2024-10-31"

    # Confirmer identity + confirm timestamp.
    assert point["confirmer"] == confirmer
    assert point["confirmed_at"] == confirmed_at

    # as_of is the ACCESSION-derived filing date, DISTINCT from the confirm ts —
    # the store's non-wall-clock as_of guard is honored.
    assert point["as_of"] == "2024-01-01"
    assert point["as_of"] != confirmed_at

    # Fail-CLOSED: without the explicit confirm, nothing is appended (no bypass).
    other = dict(candidate, kpi_id="employees_part_time")
    unconfirmed = module.commit_to_store(
        [other], company="AAPL",
        confirmer=confirmer, confirmed_at=confirmed_at,  # confirmed omitted
    )
    assert unconfirmed["committed"] == 0
    assert kpi_store.query_latest("AAPL", "employees_part_time", "2024-12-31") is None
