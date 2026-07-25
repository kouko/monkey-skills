"""Tests for analysis-kpi/scripts/kpi_xbrl_ingest.py — the store-feed driver
that wires the pure-compute `kpi_xbrl.facts_to_points` output into the durable
`kpi_store` (plan Task 3: store-feed driver — append each vintage, no collapse).

Two lanes:
  - RED 1 (`test_ingest_appends_each_vintage`): a real 2-vintage restatement
    fact-pack ingests as TWO store points under ONE kpi_id; the store's
    `dump` groups them into one period entry carrying BOTH observations with
    `disagreement=True` (the bitemporal † survives — no collapse). Exercised
    end-to-end through the `ingest` CLI subprocess, store redirected to a tmp
    dir via `KPI_STORE_DIR` (the durable ~/.local/share store is never
    touched).
  - RED 2 (`test_ingest_kpi_id_derivation`): the deterministic, injective
    kpi_id derivation from the FULL dimensional signature — distinct
    signatures → distinct ids, same signature → same id, a ConsolidationItems
    qualifier never changes the id, and the id is a readable stripped-member
    slug (never a human-authored string).

A third lane was added by the company-total-revenue arc (plan
`docs/loom/plans/2026-07-25-company-total-revenue.md` Task 5): FLAT facts
(`dimensions == {}`) route to the ONE canonical `total_revenue` series, carry
per-LANE provenance, and fail loud on a same-dedup-key value disagreement with
the already-stored series. Those tests live under the `Top-line (FLAT) lane`
banner at the bottom of this file and read the committed live-probe oracle
`tests/data/fixtures/topline_probe_2026-07-25.json`.

The real fixture is `tests/analysis/fixtures/xbrl_restatement_factpack.json`
(INTC CCG FY2020, two 10-Ks, same period, differing accession/value). It is
loaded and augmented with the producer's `period_start` field (Task 1 emits
it; the captured fixture predates it) — a real-shaped derivative, never a
hand-typed pack.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from conftest import FIXTURES, KPI_STORE_SCRIPT, SKILLS

import pytest

INGEST_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_xbrl_ingest.py"
RESTATEMENT_FIXTURE = FIXTURES / "xbrl_restatement_factpack.json"
# The live INTC Lane B capture (2026-07-25) sliced to the ONE signature that
# arrives under BOTH ConsolidationItemsAxis variants — see its `_comment`.
CONSOLIDATION_VARIANT_FIXTURE = FIXTURES / "xbrl_consolidation_variant_factpack.json"

# INTC FY2020 was a 52-week fiscal year ending 2020-12-26 → it began
# 2019-12-29. Both 10-K vintages report the SAME window, so both facts carry
# the same period_start — this is what lets the store's `same_period` group
# the two vintages into ONE period entry (the restatement †).
_FY2020_PERIOD_START = "2019-12-29"


@pytest.fixture(scope="module")
def ingest_module():
    """Load kpi_xbrl_ingest.py as an importable module for unit tests of its
    pure derivation surface (mirrors test_kpi_store.py's importlib pattern).
    """
    spec = importlib.util.spec_from_file_location("kpi_xbrl_ingest_test", INGEST_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_xbrl_ingest_test"] = module
    spec.loader.exec_module(module)
    return module


def _real_shaped_pack() -> dict:
    """Load the REAL 2-vintage restatement fixture and add the producer's
    `period_start` (Task 1) to every fact — a real-shaped derivative, never a
    hand-typed pack. Values / accessions / dimensions are untouched.
    """
    pack = json.loads(RESTATEMENT_FIXTURE.read_text(encoding="utf-8"))
    for fact in pack["facts"]:
        fact["period_start"] = _FY2020_PERIOD_START
    return pack


def _run_ingest(pack_path, env) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", "--script", str(INGEST_SCRIPT), "ingest", "--pack", str(pack_path)],
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )


def _run_dump(company, env) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", "--script", str(KPI_STORE_SCRIPT), "dump", "--company", company],
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )


def _assert_digest_suffixed(kpi_id, expected_prefix):
    """Assert `kpi_id` is exactly `expected_prefix + "__" + <12-lowercase-hex>`
    — `derive_kpi_id`'s shipped shape since Task 2 (the CASE-FOLDED-identity
    digest, `docs/loom/plans/2026-07-25-kpi-id-injective-identity.md` Task 2).
    A shared shape-check so each call site does not hand-roll the regex; the
    digest's exact VALUE is never asserted (it is a derived hash, not a
    literal this suite pins), only its shape and that the readable prefix it
    is appended to is unchanged.
    """
    match = re.fullmatch(re.escape(expected_prefix) + r"__([0-9a-f]{12})", kpi_id)
    assert match is not None, (
        f"expected {expected_prefix!r} + __<12-hex digest>; got {kpi_id!r}"
    )


def test_ingest_appends_each_vintage(tmp_path):
    """The real 2-vintage restatement pack (ONE dimensional signature) ingests
    as TWO store points under ONE kpi_id. `kpi_store dump` groups them into a
    single period entry holding BOTH observations with disagreement=True —
    the non-collapsing path preserves the restatement †. All store writes land
    under the tmp KPI_STORE_DIR; the durable store is never touched.
    """
    store_dir = tmp_path / "store"
    env = {**os.environ, "KPI_STORE_DIR": str(store_dir)}

    pack_path = tmp_path / "pack.json"
    pack_path.write_text(json.dumps(_real_shaped_pack()), encoding="utf-8")

    result = _run_ingest(pack_path, env)
    assert result.returncode == 0, (
        f"ingest failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )

    # Writes landed ONLY in the tmp store dir (durable store untouched).
    assert store_dir.exists(), "ingest did not write to the tmp KPI_STORE_DIR"
    assert list(store_dir.glob("*.json")), "no series file written to tmp store"

    dump = _run_dump("INTC", env)
    assert dump.returncode == 0, (
        f"dump failed: stdout={dump.stdout!r} stderr={dump.stderr!r}"
    )
    payload = json.loads(dump.stdout)

    assert len(payload["series"]) == 1, (
        f"expected exactly ONE kpi_id, got {[s['kpi_id'] for s in payload['series']]}"
    )
    series = payload["series"][0]
    periods = series["periods"]
    assert len(periods) == 1, (
        f"expected the two vintages to GROUP into one period entry, got {len(periods)}"
    )
    entry = periods[0]
    values = sorted(obs["value"] for obs in entry["observations"])
    assert values == [40057000000.0, 40535000000.0], (
        f"both vintages must survive as observations (no collapse); got {values}"
    )
    assert entry["disagreement"] is True, (
        "two distinct vintages of one period must flag disagreement (the †)"
    )


def _namespace_variant_pack() -> dict:
    """SYNTHETIC namespace-variant probe — NOT a real filing. Built from the
    real fixture's fact shape (accession/fiscal_calendars untouched), varying
    ONLY the dimension member's namespace prefix (`ns1:` vs `ns2:`) so the two
    facts share ONE readable-prefix slug (both strip to local-name `product`)
    but remain STRUCTURALLY distinct under `derive_kpi_id`'s digest (Task 2),
    which folds on CASE only, never on namespace. Real us-gaap/srt taxonomies
    never actually collide this way — this fixture exists to prove the
    readable-prefix collision that used to reach `_claim_kpi_id`'s raise
    (pre-Task-2) is now resolved by construction, one layer below the guard.
    """
    pack = _real_shaped_pack()
    base = pack["facts"][0]
    fact_a = dict(base)
    fact_a["dimensions"] = {"StatementBusinessSegments": "ns1:ProductMember"}
    fact_a["accession"] = "0000050863-22-000007"
    fact_b = dict(base)
    fact_b["dimensions"] = {"StatementBusinessSegments": "ns2:ProductMember"}
    fact_b["accession"] = "0000050863-23-000006"
    fact_b["value"] = 999.0
    pack["facts"] = [fact_a, fact_b]
    return pack


def test_ingest_splits_namespace_variant_signatures_into_distinct_series(tmp_path):
    """Two facts with DISTINCT dimensional signatures (`ns1:ProductMember` vs
    `ns2:ProductMember` — different namespace prefixes, so different raw
    dimension VALUES) whose OLD readable-prefix-only slug used to COLLAPSE to
    the same kpi_id (both strip to `product`) now mint DIFFERENT ids and
    ingest as TWO series — no raise.

    RE-PINNED (`docs/loom/memory/a-test-can-pin-behaviour-with-a-false-
    rationale.md`): this test used to assert the guard raised, on the theory
    that `derive_kpi_id`'s readable prefix WAS the whole id, so a namespace-
    stripped collision at that layer was a real collision needing a fail-loud
    catch. Since Task 2, `derive_kpi_id` appends a `__<12-hex>` digest of the
    CASE-FOLDED (never namespace-folded) raw identity tuple:
    `ns1:ProductMember`.casefold() != `ns2:ProductMember`.casefold(), so the
    two digests differ and the ids are genuinely distinct BY CONSTRUCTION —
    the guard has nothing left to fire on for this scenario, and correctly
    so: these ARE two different segment breakdowns under two different vendor
    namespaces, not one series split by a filer's spelling quirk. Regression
    (same test, so both directions stay coupled): the real 2-vintage
    SAME-signature pack — where multiple vintages legitimately share one
    kpi_id — must still NOT raise.
    """
    store_dir = tmp_path / "store"
    env = {**os.environ, "KPI_STORE_DIR": str(store_dir)}

    namespace_variant_path = tmp_path / "namespace_variant_pack.json"
    namespace_variant_path.write_text(
        json.dumps(_namespace_variant_pack()), encoding="utf-8"
    )
    namespace_variant_result = _run_ingest(namespace_variant_path, env)
    assert namespace_variant_result.returncode == 0, (
        "structurally distinct namespace-variant signatures must ingest as "
        f"two series, not raise: stdout={namespace_variant_result.stdout!r} "
        f"stderr={namespace_variant_result.stderr!r}"
    )
    summary = json.loads(namespace_variant_result.stdout)
    assert len(summary["kpi_ids"]) == 2, (
        "the two namespace-variant signatures must mint distinct ids; got "
        f"{summary['kpi_ids']}"
    )

    # Regression: the real SAME-signature 2-vintage pack must NOT trip the
    # guard — vintage grouping under one kpi_id is expected, not a collision.
    vintage_path = tmp_path / "vintage_pack.json"
    vintage_path.write_text(json.dumps(_real_shaped_pack()), encoding="utf-8")
    vintage_result = _run_ingest(vintage_path, env)
    assert vintage_result.returncode == 0, (
        "SAME-signature vintages must still ingest without raising: "
        f"stdout={vintage_result.stdout!r} stderr={vintage_result.stderr!r}"
    )


def _case_variant_pack() -> dict:
    """REAL observed spelling-drift shape (brief §Probe evidence: AMD's 10-Q
    `DataCenterMember` vs its 10-K `DatacenterMember`). Built from the real
    fixture's two vintages (accession/value/window untouched), varying ONLY
    the dimension member's letter case, so both facts share ONE signature
    under `derive_kpi_id`'s case-folded digest (Task 2) but arrive as TWO raw
    spellings — each spelling is its own `_fact_matches` selector (fact
    matching is untouched by this arc), and both selectors must feed the SAME
    kpi_id.
    """
    pack = _real_shaped_pack()
    fact_a = dict(pack["facts"][0])
    fact_a["dimensions"] = {"StatementBusinessSegments": "DataCenterMember"}
    fact_b = dict(pack["facts"][1])
    fact_b["dimensions"] = {"StatementBusinessSegments": "DatacenterMember"}
    pack["facts"] = [fact_a, fact_b]
    return pack


def test_ingest_folds_case_variant_selectors_into_one_series(tmp_path):
    """A pack carrying ONE dimensional signature under TWO spellings — a REAL
    observed shape (AMD's 10-Q `DataCenterMember` vs its 10-K
    `DatacenterMember`, brief `docs/loom/specs/2026-07-25-kpi-id-injective-
    identity.md` §Probe evidence) — must ingest into ONE series holding every
    vintage from BOTH spellings, instead of raising.

    Task 2 already folds case into `derive_kpi_id`'s digest, so both
    spellings' selectors derive the IDENTICAL kpi_id; what still blocked this
    before this task's fix was `_claim_kpi_id` itself — it compared each
    selector's RAW (un-folded) `_signature_key`, so two selectors landing on
    one id read as a distinct-signature collision and the guard raised. The
    fix relaxes ONLY that comparison to case-insensitive equality;
    `_fact_matches` still exact-matches each selector's own spelling, so both
    selectors keep hitting only their own facts and the union of both lands
    on the shared id.
    """
    store_dir = tmp_path / "store"
    env = {**os.environ, "KPI_STORE_DIR": str(store_dir)}

    pack = _case_variant_pack()
    pack_path = tmp_path / "case_variant_pack.json"
    pack_path.write_text(json.dumps(pack), encoding="utf-8")

    result = _run_ingest(pack_path, env)
    assert result.returncode == 0, (
        "a pure case-variant pair must fold into ONE series, not raise: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )

    summary = json.loads(result.stdout)
    assert len(summary["kpi_ids"]) == 1, (
        f"both spellings must land in ONE series; got {summary['kpi_ids']}"
    )
    assert summary["appended"] == len(pack["facts"]), (
        f"every fact from BOTH spellings must be appended: {summary['appended']} "
        f"appended for {len(pack['facts'])} facts"
    )

    dump = _run_dump(pack["company"], env)
    assert dump.returncode == 0, (
        f"dump failed: stdout={dump.stdout!r} stderr={dump.stderr!r}"
    )
    payload = json.loads(dump.stdout)
    assert len(payload["series"]) == 1, (
        f"expected ONE series, got {[s['kpi_id'] for s in payload['series']]}"
    )
    stored_values = sorted(
        obs["value"]
        for period in payload["series"][0]["periods"]
        for obs in period["observations"]
    )
    assert stored_values == sorted(fact["value"] for fact in pack["facts"]), (
        f"every vintage from BOTH spellings must survive; got {stored_values}"
    )


def test_claim_kpi_id_still_raises_on_a_forced_collision(ingest_module):
    """SYNTHETIC-BY-NECESSITY. After Task 2, `derive_kpi_id`'s digest is
    injective over the raw (case-folded-only) identity tuple, so no ordinary
    production input can make two STRUCTURALLY different signatures land on
    one kpi_id any more — that unreachability is the whole point of the
    digest. This test therefore forces the collision directly at
    `_claim_kpi_id`, bypassing `derive_kpi_id` entirely, because that is the
    only way left to exercise the guard's raise branch at all.

    This is NOT proof that today's production inputs can reach the raise
    path. It is defense-in-depth: proof the raise still fires if some future
    change to `derive_kpi_id` (a shorter digest, a weaker fold, a
    hash-truncation bug) reintroduces a real collision.

    One caveat, found by the close-out review and deliberately not fixed here:
    the raise IS reachable by a hand-built pack that puts
    `srt:ConsolidationItemsAxis` inside `dimensions` instead of in its own
    `consolidation` field — `derive_kpi_id` drops that axis from the breakdown
    pairs while `_signature_key` keeps it, so one id gets two claim keys and
    the guard raises a FALSE collision. The shipped SEC producer cannot emit
    that shape (`_dimension_signature` allowlists four breakdown axes and
    routes the consolidation axis elsewhere), and the failure is loud rather
    than a silent merge, so it is filed as a BACKLOG next-touch. Stated here
    because "unreachable" was the claim this test rested on, and it is
    unreachable only through the producer — not in principle.
    """
    claim_kpi_id = ingest_module._claim_kpi_id
    claimed_by: dict = {}
    key_a = (
        "us-gaap:Revenues",
        (("StatementBusinessSegments", "Alpha"),),
        "OperatingSegmentsMember",
    )
    key_b = (
        "us-gaap:Revenues",
        (("StatementBusinessSegments", "Beta"),),
        "OperatingSegmentsMember",
    )

    claim_kpi_id(claimed_by, "forced-collision-id", key_a)
    with pytest.raises(ValueError, match="collision"):
        claim_kpi_id(claimed_by, "forced-collision-id", key_b)


def test_casefold_claim_key_agrees_across_axis_name_case_and_reordered_axes(
    ingest_module,
):
    """SYNTHETIC-BY-NECESSITY, same class as
    `test_claim_kpi_id_still_raises_on_a_forced_collision` above: exercises
    `_casefold_claim_key`/`_claim_kpi_id` directly rather than through the
    `ingest` CLI, because a REAL multi-axis fact where only the AXIS NAME's
    case drifts between two selectors ALSO flips `derive_kpi_id`'s readable
    prefix (its `breakdown_axes = sorted(dimensions)` is the same raw,
    case-sensitive sort `_signature_key` uses), so today the two selectors
    would mint two DIFFERENT full kpi_ids and never reach this guard's
    comparison through `ingest_pack` — this exact pair is unreachable via a
    real ingest today (code-quality finding, kpi_xbrl_ingest.py:198-200 vs
    :291-296). That is exactly why this is tested at the guard's own unit
    level: the guard's documented invariant ("mirrors `derive_kpi_id`'s own
    digest fold") must hold on its own terms, not merely by coincidence of
    today's prefix/signature-key sort coupling — a future caller (or a
    `derive_kpi_id` prefix change) could hand two such selectors the SAME
    kpi_id, exactly as this test does directly.

    `_signature_key` (`kpi_xbrl_ingest.py:274-278`) sorts `dimensions.items()`
    RAW (case-sensitive) — the identical sort basis `derive_kpi_id`'s prefix
    uses. With >=2 axes, changing ONLY one axis NAME's case can flip that raw
    sort order, so the two claim keys' dims tuples differ in ELEMENT ORDER,
    not just in case. `derive_kpi_id`'s digest re-sorts by the CASEFOLDED
    value (Task 2), so it folds both to the identical digest regardless of
    that order — `_casefold_claim_key` must do the same (casefold, THEN
    re-sort) or it reads the pre-casefold order mismatch as a distinct
    signature.
    """
    signature_key = ingest_module._signature_key
    casefold_claim_key = ingest_module._casefold_claim_key
    claim_kpi_id = ingest_module._claim_kpi_id

    key_a = signature_key(
        "us-gaap:Revenues", {"Alpha": "One", "Zeta": "Two"}, None
    )
    key_b = signature_key(
        "us-gaap:Revenues", {"alpha": "One", "Zeta": "Two"}, None
    )
    assert key_a[1] != key_b[1], (
        "fixture must actually diverge in pre-casefold element order — "
        f"got {key_a[1]!r} == {key_b[1]!r}, this pair does not exercise the bug"
    )

    assert casefold_claim_key(key_a) == casefold_claim_key(key_b), (
        "the two claim keys are ONE signature under derive_kpi_id's own "
        f"case-fold; got {casefold_claim_key(key_a)!r} != "
        f"{casefold_claim_key(key_b)!r}"
    )

    claimed_by: dict = {}
    claim_kpi_id(claimed_by, "shared-kpi-id", key_a)
    claim_kpi_id(claimed_by, "shared-kpi-id", key_b)  # must NOT raise


def _consolidation_variant_pack() -> dict:
    """The REAL live-captured pack whose ONE dimensional signature arrives under
    BOTH ConsolidationItemsAxis variants (see the fixture's own `_comment`).
    Loaded verbatim — no augmentation, the 2026-07-25 producer already emits
    every field `facts_to_points` requires.
    """
    return json.loads(CONSOLIDATION_VARIANT_FIXTURE.read_text(encoding="utf-8"))


def test_ingest_collapses_consolidation_variants_of_one_signature(tmp_path):
    """A signature whose facts arrive under BOTH `consolidation=
    'OperatingSegmentsMember'` and `consolidation=None` is ONE series, and must
    ingest as one.

    WHY this is not the guard's job: `_fact_matches` normalizes the qualifier on
    BOTH sides (`kpi_xbrl.py:428-432`), so the consumer already treats the two
    raw values as the same series. A `_signature_key` that carried the RAW value
    would split them into two selectors deriving one `kpi_id` and the collision
    guard would OVER-FIRE — aborting the whole ingest, dimensional and top-line
    alike (the live INTC Lane B failure, 2026-07-25). The guard's notion of
    "distinct" must equal the consumer's notion of "same"
    (`docs/loom/memory/derived-durable-id-slug-is-a-lossy-one-way-door.md`).

    The point count is the load-bearing assertion, not the exit code: one
    normalized selector must emit each fact EXACTLY once. Two selectors would
    each match ALL four facts (both normalize identically), double-emitting; a
    selector keyed on the raw value in a way that failed to normalize would drop
    the other variant's facts. `appended == len(facts)` rules out both.
    """
    store_dir = tmp_path / "store"
    env = {**os.environ, "KPI_STORE_DIR": str(store_dir)}

    pack = _consolidation_variant_pack()
    pack_path = tmp_path / "consolidation_variant_pack.json"
    pack_path.write_text(json.dumps(pack), encoding="utf-8")

    result = _run_ingest(pack_path, env)
    assert result.returncode == 0, (
        "the two ConsolidationItemsAxis variants of ONE signature are one "
        "series to the consumer — the collision guard must not over-fire: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )

    summary = json.loads(result.stdout)
    assert len(summary["kpi_ids"]) == 1, (
        f"both variants must land in ONE series; got {summary['kpi_ids']}"
    )
    _assert_digest_suffixed(
        summary["kpi_ids"][0],
        "revenuefromcontractwithcustomerexcludingassessedtax"
        "__productorservice-assemblyandtest"
        "__statementbusinesssegments-intelfoundry",
    )
    assert summary["appended"] == len(pack["facts"]), (
        "every fact must be appended EXACTLY once — fewer means a variant was "
        f"dropped, more means it was double-emitted: {summary['appended']} "
        f"appended for {len(pack['facts'])} facts"
    )

    # Read the store back: every captured value survives, so the collapse is a
    # merge of two tagging variants and not a silent loss of one of them.
    dump = _run_dump(pack["ticker"], env)
    assert dump.returncode == 0, (
        f"dump failed: stdout={dump.stdout!r} stderr={dump.stderr!r}"
    )
    payload = json.loads(dump.stdout)
    assert len(payload["series"]) == 1, (
        f"expected ONE series, got {[s['kpi_id'] for s in payload['series']]}"
    )
    stored_values = sorted(
        obs["value"]
        for period in payload["series"][0]["periods"]
        for obs in period["observations"]
    )
    assert stored_values == sorted(fact["value"] for fact in pack["facts"]), (
        f"every captured fact's value must reach the store; got {stored_values}"
    )


def test_ingest_splits_namespace_variant_signatures_across_consolidation_variants(
    tmp_path,
):
    """The qualifier normalization in `_signature_key` must not accidentally
    mask a genuine BREAKDOWN difference: two namespace-variant signatures
    (`ns1:` vs `ns2:` — see `_namespace_variant_pack`) still mint DISTINCT ids
    and ingest as two series even when they ALSO differ on the consolidation
    qualifier.

    RE-PINNED (`docs/loom/memory/a-test-can-pin-behaviour-with-a-false-
    rationale.md`): this test used to assert the guard raised, on the theory
    that normalizing the qualifier out of `_signature_key` could be "fixed" by
    dropping the key's discriminating power altogether, so the guard had to
    catch a namespace-stripped readable-prefix collision the consumer's own
    normalization could not tell apart. Since Task 2's digest is injective
    over the raw (non-namespace-folded) breakdown member text, the two facts
    below now mint distinct ids BY CONSTRUCTION regardless of their
    consolidation qualifier — `OperatingSegmentsMember` and `None` both
    normalize to the SAME default qualifier and add no token to either id, so
    the split is driven entirely by the breakdown member, exactly as it
    should be. The sibling
    `test_ingest_splits_namespace_variant_signatures_into_distinct_series`
    pins the same-qualifier case; this one pins the axis the fix touches.
    """
    store_dir = tmp_path / "store"
    env = {**os.environ, "KPI_STORE_DIR": str(store_dir)}

    pack = _consolidation_variant_pack()
    fact_a, fact_b = (dict(pack["facts"][0]), dict(pack["facts"][1]))
    # Distinct breakdown members that used to slug-collapse to the same
    # readable-prefix kpi_id, carried under DIFFERENT consolidation qualifiers.
    fact_a["dimensions"] = {"StatementBusinessSegments": "ns1:ProductMember"}
    fact_a["consolidation"] = "OperatingSegmentsMember"
    fact_b["dimensions"] = {"StatementBusinessSegments": "ns2:ProductMember"}
    fact_b["consolidation"] = None
    pack["facts"] = [fact_a, fact_b]

    pack_path = tmp_path / "cross_variant_split_pack.json"
    pack_path.write_text(json.dumps(pack), encoding="utf-8")

    result = _run_ingest(pack_path, env)
    assert result.returncode == 0, (
        "distinct BREAKDOWN signatures must ingest as two series even when "
        f"their consolidation qualifiers differ: stdout={result.stdout!r} "
        f"stderr={result.stderr!r}"
    )
    summary = json.loads(result.stdout)
    assert len(summary["kpi_ids"]) == 2, (
        "the two breakdown-distinct signatures must mint distinct ids; got "
        f"{summary['kpi_ids']}"
    )


def test_ingest_splits_default_and_non_default_consolidation_into_distinct_series(
    tmp_path,
):
    """Two facts sharing one concept+breakdown but carrying the DEFAULT
    `OperatingSegmentsMember` view on one side and a NON-DEFAULT
    `ConsolidationItemsAxis` member on the other must ingest as TWO series,
    not collide.

    Re-pinned polarity (`docs/loom/memory/a-test-can-pin-behaviour-with-a-false-
    rationale.md`): this test used to assert `returncode != 0` on the theory
    that `derive_kpi_id` dropped the qualifier entirely, so both facts derived
    ONE id the guard had to reject to avoid a silent drop. `derive_kpi_id` no
    longer drops it — a non-default `consolidation` now appends its own
    `__<member-slug>` token to the readable prefix (Task 1's change, this same
    arc). A non-default member is DISCRIMINATING for identity: `Operating
    SegmentsMember` and `IntersegmentEliminationMember` are genuinely different
    amounts — a segment's operating view vs its intersegment eliminations,
    adjacent columns of one reconciliation table, not two spellings of the
    same number. So the two facts now mint DIFFERENT ids by construction, the
    collision guard has nothing to fire on, and ingest succeeding with two
    series is the correct outcome, not a gap the guard must patch over.

    Without this test the suite cannot distinguish the shipped `derive_kpi_id`
    (which appends the non-default member's slug) from a mutant that keeps
    dropping the qualifier: that mutant would derive ONE id for both facts and
    either silently collapse them into one series or spuriously trip the
    guard — either way the two REAL amounts stop being two series. Asserting
    two distinct ids AND two distinct stored series rules out both. What this
    test does NOT cover — two GENUINELY non-default members discriminating
    against EACH OTHER, rather than against the default — is pinned instead by
    `test_derive_kpi_id_discriminates_non_default_consolidation`'s
    `elimination`-vs-`corporate` assertion.

    SYNTHETIC probe (mirrors `_namespace_variant_pack`): no real INTC filing
    tags this concept with an intersegment-elimination member, so the pack is
    the live fixture's own facts RE-TAGGED on the qualifier axis only. Values /
    dimensions / accessions / windows are the captured ones, never hand-typed.
    """
    store_dir = tmp_path / "store"
    env = {**os.environ, "KPI_STORE_DIR": str(store_dir)}

    pack = _consolidation_variant_pack()
    operating, elimination = (dict(pack["facts"][0]), dict(pack["facts"][3]))
    operating["consolidation"] = "OperatingSegmentsMember"
    elimination["consolidation"] = "IntersegmentEliminationMember"
    pack["facts"] = [operating, elimination]

    pack_path = tmp_path / "non_default_members_pack.json"
    pack_path.write_text(json.dumps(pack), encoding="utf-8")

    result = _run_ingest(pack_path, env)
    assert result.returncode == 0, (
        "a non-default consolidation member discriminates the id — two "
        "genuinely different amounts must ingest as two series, not collide: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )

    base_id = (
        "revenuefromcontractwithcustomerexcludingassessedtax"
        "__productorservice-assemblyandtest"
        "__statementbusinesssegments-intelfoundry"
    )
    summary = json.loads(result.stdout)
    assert len(summary["kpi_ids"]) == 2, (
        "the default-member fact keeps the bare signature and the non-default "
        f"member appends its own token — two ids expected; got {summary['kpi_ids']}"
    )
    # `derive_kpi_id`'s digest sorts a hex-suffixed id before an
    # `intersegmentelimination`-suffixed one (every hex char is < 'i'), so the
    # producer's `sorted(kpi_ids)` output is deterministic here.
    _assert_digest_suffixed(summary["kpi_ids"][0], base_id)
    _assert_digest_suffixed(
        summary["kpi_ids"][1], base_id + "__intersegmentelimination"
    )
    assert summary["appended"] == len(pack["facts"]), (
        "each fact belongs to its own series, so both must be appended: "
        f"{summary['appended']} appended for {len(pack['facts'])} facts"
    )

    dump = _run_dump(pack["ticker"], env)
    assert dump.returncode == 0, (
        f"dump failed: stdout={dump.stdout!r} stderr={dump.stderr!r}"
    )
    payload = json.loads(dump.stdout)
    stored_ids = sorted(s["kpi_id"] for s in payload["series"])
    assert len(stored_ids) == 2, (
        "the operating view and the intersegment-elimination view must be "
        f"stored as TWO series; got {[s['kpi_id'] for s in payload['series']]}"
    )
    _assert_digest_suffixed(stored_ids[0], base_id)
    _assert_digest_suffixed(stored_ids[1], base_id + "__intersegmentelimination")


def test_ingest_kpi_id_derivation(ingest_module):
    """kpi_id is derived deterministically and INJECTIVELY (up to case) from
    the FULL dimensional signature — readable prefix (concept + sorted
    breakdown axis:member local-names, Member/Axis stripped, lowercased) plus
    a `__<12-hex>` digest of the case-folded identity tuple (Task 2):

      - two DISTINCT signatures → DISTINCT ids (injective);
      - the SAME signature → the SAME id (groups vintages);
      - a signature differing ONLY in srt:ConsolidationItemsAxis → the SAME id
        (it is a reconciliation qualifier, never a breakdown axis — memory
        `match-kpi-on-full-dimensional-signature-not-one-axis`);
      - the id is a readable stripped-member slug followed by a 12-hex digest,
        never a bare human string.
    """
    derive = ingest_module.derive_kpi_id
    concept = "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"

    ccg = derive(concept, {"StatementBusinessSegments": "ClientComputingGroupMember"})
    dcg = derive(concept, {"StatementBusinessSegments": "DataCenterGroupMember"})

    # Distinct signatures → distinct ids (injective).
    assert ccg != dcg

    # Same signature (fresh dict instance) → same id (so vintages group).
    ccg_again = derive(
        concept, {"StatementBusinessSegments": "ClientComputingGroupMember"}
    )
    assert ccg == ccg_again

    # A ConsolidationItems qualifier does NOT change the id — it is a separate
    # reconciliation axis, not a breakdown axis (else every segment filer looks
    # falsely cross-dimensioned).
    ccg_with_consol = derive(
        concept,
        {
            "StatementBusinessSegments": "ClientComputingGroupMember",
            "srt:ConsolidationItemsAxis": "OperatingSegmentsMember",
        },
    )
    assert ccg_with_consol == ccg

    # A readable slug from stripped member local-name(s): the Member suffix is
    # gone, it is lowercased, and it is signature-faithful (not a human name).
    assert "clientcomputinggroup" in ccg
    assert "member" not in ccg
    assert "datacentergroup" in dcg

    # New shape (Task 2): a `__<12-lowercase-hex>` digest suffix on every id.
    _assert_digest_suffixed(
        ccg, "revenuefromcontractwithcustomerexcludingassessedtax"
        "__statementbusinesssegments-clientcomputinggroup"
    )
    _assert_digest_suffixed(
        dcg, "revenuefromcontractwithcustomerexcludingassessedtax"
        "__statementbusinesssegments-datacentergroup"
    )


def test_derive_kpi_id_folds_case_and_stays_injective(ingest_module):
    """The id gains a `__<12-lowercase-hex>` sha1 digest of the CASE-FOLDED
    consumer identity tuple `(concept, breakdown dimensions, normalized
    consolidation)` — mirrors `kpi_store._series_key`'s readable-stem-plus-
    digest precedent (`kpi_store.py:71-92`: a readable prefix alone is not
    collision-proof).

    (a) A REAL observed spelling pair — AMD's 10-Q `DataCenterMember` vs its
    10-K `DatacenterMember` (brief `docs/loom/specs/2026-07-25-kpi-id-
    injective-identity.md` §Probe evidence table) — must mint the SAME id.
    Case is FOLDED, not preserved: preserving it would file a filer's
    quarterly history apart from its annual history (the C->C' amendment).
    (b) A structurally distinct signature (different breakdown MEMBER, not
    merely different case) must mint a DIFFERENT id.
    (c) The id ends with a `__` delimiter followed by EXACTLY 12 lowercase
    hex characters.
    """
    derive = ingest_module.derive_kpi_id
    concept = "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"

    q_spelling = derive(concept, {"StatementBusinessSegments": "DataCenterMember"})
    k_spelling = derive(concept, {"StatementBusinessSegments": "DatacenterMember"})
    assert q_spelling == k_spelling, (
        f"a pure case-variant pair must fold to ONE id: {q_spelling!r} != {k_spelling!r}"
    )

    other = derive(
        concept, {"StatementBusinessSegments": "ClientComputingGroupMember"}
    )
    assert other != q_spelling, (
        f"a structurally distinct signature must mint a different id: "
        f"{other!r} == {q_spelling!r}"
    )

    match = re.fullmatch(r".+__([0-9a-f]{12})$", q_spelling)
    assert match is not None, (
        f"id must end with __ followed by exactly 12 lowercase hex chars: {q_spelling!r}"
    )


def test_derive_kpi_id_discriminates_non_default_consolidation(ingest_module):
    """A non-default `ConsolidationItemsAxis` qualifier (e.g.
    `IntersegmentEliminationMember`) must mint a DIFFERENT kpi_id than the
    default `OperatingSegmentsMember` view over the SAME (concept,
    dimensions) pair — `kpi_xbrl._normalize_consolidation` does NOT fold
    non-default members together, and `derive_kpi_id` dropping the axis
    entirely is exactly what would force two series the consumer keeps apart
    into one id. A default OR absent qualifier must mint the SAME id as no
    qualifier at all, so the 2.36.0 consolidation-variant fold
    (`test_ingest_collapses_consolidation_variants_of_one_signature`)
    survives by construction.

    Also covers the pair the default-vs-non-default split above cannot: TWO
    GENUINELY non-default members (`IntersegmentEliminationMember` vs
    `CorporateNonSegmentMember` — both observed on the live 47-filer probe,
    `tests/data/fixtures/kpi_id_identity_probe_2026-07-25.json`
    `_summary.consolidation_member_domain`) over the SAME breakdown must
    ALSO mint distinct ids from each other, not just from the default —
    `_normalize_consolidation` does not fold any two non-default members
    together, so `derive_kpi_id` appending each member's own token must
    discriminate every pair, not only the default/non-default one.
    """
    derive = ingest_module.derive_kpi_id
    concept = "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"
    dimensions = {"StatementBusinessSegments": "ClientComputingGroupMember"}

    operating = derive(concept, dimensions, "OperatingSegmentsMember")
    elimination = derive(concept, dimensions, "IntersegmentEliminationMember")
    absent = derive(concept, dimensions, None)
    corporate = derive(concept, dimensions, "CorporateNonSegmentMember")

    assert operating != elimination, (
        f"a non-default consolidation member must discriminate the id: "
        f"got {operating!r} for both"
    )
    assert absent == operating, (
        f"an absent qualifier must mint the SAME id as the default member: "
        f"{absent!r} != {operating!r}"
    )
    assert elimination != corporate, (
        "two GENUINELY non-default consolidation members must discriminate "
        f"each other, not just the default: got {elimination!r} for both"
    )


def test_derive_kpi_id_prefix_orders_axes_by_folded_key_not_raw_case(ingest_module):
    """Whole-branch close-out finding (feat-kpi-id-consolidation-axis): the
    readable PREFIX must order its axis=member tokens by the SAME folded key
    `_canonical_dimension_fold` (and therefore the digest) uses, not by raw
    (case-sensitive) `sorted(dimensions)`. Two multi-axis signatures whose
    axis NAMES differ only in case can flip `sorted()`'s raw-text order
    between them even though every axis is the SAME axis once folded — before
    the fix this mints two DIFFERENT ids (and therefore two different store
    series) for what is the identical dimensional identity.
    """
    derive = ingest_module.derive_kpi_id
    concept = "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"

    sig_a = derive(
        concept,
        {"ProductOrService": "AssemblyMember", "productOrServiceB": "TestMember"},
    )
    sig_b = derive(
        concept,
        {"productOrService": "AssemblyMember", "ProductOrServiceB": "TestMember"},
    )
    assert sig_a == sig_b, (
        f"axis-name case flipping raw sort order must not change the id: "
        f"{sig_a!r} != {sig_b!r}"
    )


def test_derive_kpi_id_consolidation_default_compared_case_insensitively(
    ingest_module,
):
    """Whole-branch close-out finding: the prefix's own default-vs-non-default
    consolidation comparison used a raw `!=` against
    `kpi_xbrl._DEFAULT_CONSOLIDATION_MEMBER`, so a differently-cased spelling
    of the SAME default member (`OperatingsegmentsMember` vs
    `OperatingSegmentsMember`) was wrongly treated as non-default and appended
    a spurious `__operatingsegments` token — minting a second id for what the
    digest (and `_fact_matches`' own normalized comparison) already treats as
    the default view.
    """
    derive = ingest_module.derive_kpi_id
    concept = "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"
    dimensions = {"StatementBusinessSegments": "ClientComputingGroupMember"}

    canonical_case = derive(concept, dimensions, "OperatingSegmentsMember")
    other_case = derive(concept, dimensions, "OperatingsegmentsMember")
    assert canonical_case == other_case, (
        f"a differently-cased spelling of the DEFAULT consolidation member "
        f"must add NO token, same as the canonically-cased default: "
        f"{canonical_case!r} != {other_case!r}"
    )


def test_derive_kpi_id_prefix_folds_non_ascii_case_via_casefold(ingest_module):
    """Whole-branch close-out finding: the prefix folded each token with
    `.lower()`, not `.casefold()`. The two agree on every ASCII XBRL name in
    the observed corpus (the digest's own docstring says so), but diverge on
    German sharp-s: `"Straße".lower() == "straße"` while
    `"STRASSE".lower() == "strasse"` — genuinely different strings — whereas
    `.casefold()` maps both to `"strasse"`, matching the digest's own fold
    (Task 2 already uses `.casefold()` there). `_strip_axis_member_suffix`
    still runs on the ORIGINAL (un-folded) string first — the `Member` suffix
    match is case-sensitive, so folding before stripping would silently break
    it for every existing id.
    """
    derive = ingest_module.derive_kpi_id
    concept = "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"

    sharp_s = derive(
        concept, {"StatementBusinessSegments": "StraßeMember"}
    )
    double_s = derive(
        concept, {"StatementBusinessSegments": "STRASSEMember"}
    )
    assert sharp_s == double_s, (
        f".lower() vs .casefold() disagreement on non-ASCII case must not "
        f"split one identity into two ids: {sharp_s!r} != {double_s!r}"
    )


def test_derive_kpi_id_folds_every_spelling_of_one_identity(ingest_module):
    """PROPERTY, not one example: every prior case-fold test above (688-725,
    773, 800, 825) happened to use the ONE worked pair that passes —
    `DataCenterMember`/`DatacenterMember`, whose case drift lands mid-token,
    never on the `Axis`/`Member` suffix itself. None of them exercise the
    close-out finding: `_strip_axis_member_suffix` matched `Axis`/`Member`
    CASE-SENSITIVELY and ran BEFORE `.casefold()`, so a spelling whose case
    drift lands ON the suffix token (e.g. `DataCenterMEMBER`) keeps the
    suffix attached in the READABLE PREFIX while every conventionally-cased
    spelling strips it — while the DIGEST (built from the raw string,
    casefolded whole, never suffix-stripped) is unaffected and stays
    identical. Prefix and digest disagreeing mints a SECOND kpi_id for the
    SAME signature, and because the collision guard (`_claim_kpi_id`) is
    keyed on kpi_id, the two ids never meet it — a permanently split series
    with no fail-loud.

    Several spellings of ONE member identity, and an Axis-suffix analogue
    (case drift landing on the AXIS token's own suffix), must ALL mint the
    identical kpi_id.
    """
    derive = ingest_module.derive_kpi_id
    concept = "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"

    member_spellings = [
        "DataCenterMember",
        "DatacenterMember",
        "DataCenterMEMBER",
        "datacentermember",
    ]
    member_ids = {
        spelling: derive(concept, {"StatementBusinessSegments": spelling})
        for spelling in member_spellings
    }
    assert len(set(member_ids.values())) == 1, (
        "every spelling of ONE member identity must mint the identical "
        f"kpi_id, got {member_ids}"
    )

    axis_spellings = [
        "ProductOrServiceAxis",
        "ProductOrServiceAXIS",
        "productorserviceaxis",
    ]
    axis_ids = {
        spelling: derive(concept, {spelling: "AssemblyMember"})
        for spelling in axis_spellings
    }
    assert len(set(axis_ids.values())) == 1, (
        "every spelling of ONE axis identity (case drift landing on the "
        f"Axis suffix) must mint the identical kpi_id, got {axis_ids}"
    )


# --------------------------------------------------------------------------
# Top-line (FLAT) lane — plan docs/loom/plans/2026-07-25-company-total-revenue.md
# Task 5. Flat facts (`dimensions == {}`) are no longer skipped: they land in
# ONE canonical `total_revenue` series, carry their OWN provenance label, and
# a same-dedup-key value disagreement against the already-stored series fails
# loud instead of being silently swallowed by `kpi_store.append`'s first-record-
# wins dedup.
# --------------------------------------------------------------------------

# The CAPTURED live-probe oracle (8 filers, 2026-07-25) committed by Task 1 —
# the source of record for real top-line concept strings, period windows and
# values. Never hand-typed (memory `hand-authored-fixture-is-a-fabrication-risk`).
TOPLINE_PROBE = (
    Path(__file__).resolve().parents[1]
    / "data" / "fixtures" / "topline_probe_2026-07-25.json"
)

_INTC_TOPLINE_CONCEPT = "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"
_INTC_LEGACY_TOPLINE_CONCEPT = "us-gaap:Revenues"

# REAL INTC accessions. The first is the probe record's own 10-K; the other two
# are the restatement fixture's two vintages of FY2020.
_INTC_FY2025_ACCESSION = "0000050863-26-000011"
_INTC_FY2020_FIRST_ACCESSION = "0000050863-22-000007"
_INTC_FY2020_RESTATED_ACCESSION = "0000050863-23-000006"

# The probe captured no `filed` date, so the FY2025 facts below supply one
# explicitly. It serves only as the store's bitemporal `as_of` key here — no
# assertion depends on its real-world accuracy, only on two vintages carrying
# DIFFERENT `as_of` values.
_INTC_FY2025_AS_OF = "2026-01-22"


def _fixture_fact(accession: str) -> dict:
    """The restatement fixture's fact for one accession, READ off the committed
    capture. Nothing about that fact (`filed`, `value`, `period_end`,
    `fiscal_year`) is transcribed into a constant here: a hand-copied date that
    only ever gets compared against itself drifts from its fixture in total
    silence, which is the shape memory `hand-authored-fixture-is-a-fabrication-
    risk` records — and did happen to this file's first draft.
    """
    facts = json.loads(RESTATEMENT_FIXTURE.read_text(encoding="utf-8"))["facts"]
    for fact in facts:
        if fact["accession"] == accession:
            return fact
    raise AssertionError(f"restatement fixture carries no {accession!r} fact")


def _probe_flat_sample(ticker: str, concept: str) -> dict:
    """The captured `A_flat` sample for one filer's flat top-line concept —
    real concept string, real `period_start`/`period_end` window, real value.
    """
    records = json.loads(TOPLINE_PROBE.read_text(encoding="utf-8"))
    for record in records:
        if record["ticker"] == ticker:
            return record["A_flat"][concept]["sample"]
    raise AssertionError(f"probe fixture carries no {ticker!r} record")


def _flat_topline_fact(
    *, concept, period_start, period_end, value, fiscal_year, accession, filed
):
    """One FLAT (`dimensions == {}`) top-line fact in the producer's emitted
    shape: the real restatement fixture's fact field-set (`duration_months`,
    `fiscal_quarter`, `derivation_basis`, … — the fields `classify_fact_period`
    and `_require_source_form` hard-require) with the top-line identity fields
    replaced. A real-shaped derivative, never a hand-typed pack.
    """
    fact = dict(json.loads(RESTATEMENT_FIXTURE.read_text(encoding="utf-8"))["facts"][0])
    fact.update(
        concept=concept,
        dimensions={},
        consolidation=None,
        value=value,
        period_start=period_start,
        period_end=period_end,
        fiscal_year=fiscal_year,
        accession=accession,
        filed=filed,
        calendar_year=int(str(period_end)[:4]),
    )
    return fact


def _intc_fy2025_topline(concept=_INTC_TOPLINE_CONCEPT, **overrides):
    """INTC's FY2025 flat top-line fact, verbatim from the captured probe
    (concept / window / value) unless a test overrides a field explicitly.
    """
    sample = _probe_flat_sample("INTC", _INTC_TOPLINE_CONCEPT)
    fields = dict(
        concept=concept,
        period_start=sample["period_start"],
        period_end=sample["period_end"],
        value=sample["value"],
        fiscal_year=2025,
        accession=_INTC_FY2025_ACCESSION,
        filed=_INTC_FY2025_AS_OF,
    )
    fields.update(overrides)
    return _flat_topline_fact(**fields)


def _fy2020_topline(accession, *, value=None):
    """One FY2020 flat top-line fact, built from the REAL restatement fixture's
    fact for `accession` — its `filed` / `value` / `period_end` / `fiscal_year`
    are read straight off the capture, never re-typed here. Only the LANE is
    repurposed (the fixture's figures are INTC's CCG segment, read here as the
    company's top line), so every date, accession and figure stays real.

    `value` overrides the captured figure ONLY where a test needs a second,
    deliberately different number for one dedup key (a disagreement probe) —
    such overrides are marked at their call site.
    """
    source = _fixture_fact(accession)
    return _flat_topline_fact(
        concept=_INTC_LEGACY_TOPLINE_CONCEPT,
        period_start=_FY2020_PERIOD_START,
        period_end=source["period_end"],
        value=source["value"] if value is None else value,
        fiscal_year=source["fiscal_year"],
        accession=accession,
        filed=source["filed"],
    )


def _pack(facts, *, company="INTC", source_kind=None):
    """A fact-pack envelope around `facts`, with a dei `fiscal_calendars` entry
    for every accession they carry (`_require_source_form` refuses to emit a
    formless point without one). `source_kind` rides on the envelope only when
    a test declares one — the plan's §Notes envelope provenance contract.
    """
    pack = {
        "company": company,
        "facts": list(facts),
        "fiscal_calendars": {
            fact["accession"]: {
                "fiscal_period_focus": "FY",
                "fiscal_year_end": "--12-26",
                "fiscal_year_focus": str(fact["fiscal_year"]),
            }
            for fact in facts
        },
    }
    if source_kind is not None:
        pack["source_kind"] = source_kind
    return pack


def _mixed_pack(**envelope_kwargs):
    """The real 2-vintage DIMENSIONAL restatement pack PLUS INTC's captured
    flat top-line fact — the Lane B shape that carries BOTH kinds of fact in
    one pack, which is why provenance must be assigned per LANE, not per pack.
    """
    pack = _real_shaped_pack()
    flat = _intc_fy2025_topline()
    pack["facts"].append(flat)
    pack["fiscal_calendars"][flat["accession"]] = {
        "fiscal_period_focus": "FY",
        "fiscal_year_end": "--12-26",
        "fiscal_year_focus": "2025",
    }
    pack.update(envelope_kwargs)
    return pack


def _stored_points(store_dir):
    """Every point durably written under `store_dir`, read straight off disk.
    The series filename embeds a one-way digest of (company, kpi_id), so the
    files are globbed rather than named.
    """
    if not store_dir.exists():
        return []
    points = []
    for path in sorted(store_dir.glob("*.json")):
        points.extend(json.loads(path.read_text(encoding="utf-8"))["points"])
    return points


@pytest.fixture
def isolated_store(tmp_path, monkeypatch):
    """Point `kpi_store` at a per-test tmp dir — the durable
    ~/.local/share store is never touched.
    """
    store_dir = tmp_path / "store"
    monkeypatch.setenv("KPI_STORE_DIR", str(store_dir))
    return store_dir


def test_flat_facts_ingest_as_canonical_total_revenue(ingest_module, isolated_store):
    """A pack mixing dimensional and flat facts appends the FLAT ones under the
    fixed canonical `kpi_id` `total_revenue` — NOT `derive_kpi_id`'s bare-concept
    slug (`revenuefromcontractwithcustomerexcludingassessedtax`), which would
    make the durable series identity hostage to whichever concept string a
    filer happened to tag (memory
    `derived-durable-id-slug-is-a-lossy-one-way-door`). The dimensional lane's
    own id is unaffected.
    """
    result = ingest_module.ingest_pack(_mixed_pack())

    assert "total_revenue" in result["kpi_ids"], (
        f"flat facts must land under the canonical id; got {result['kpi_ids']}"
    )
    assert not any(
        kpi_id.startswith("revenuefromcontractwithcustomer")
        and "__" not in kpi_id
        for kpi_id in result["kpi_ids"]
    ), f"the bare-concept slug must never be minted: {result['kpi_ids']}"

    top_line = [p for p in _stored_points(isolated_store) if p["kpi_id"] == "total_revenue"]
    assert len(top_line) == 1, f"expected one stored top-line point, got {top_line}"
    assert top_line[0]["value"] == _probe_flat_sample("INTC", _INTC_TOPLINE_CONCEPT)["value"]


def test_flat_lane_merges_two_concepts_into_one_series(ingest_module, isolated_store):
    """A filer that SWITCHED tagging across years (`us-gaap:Revenues` in the
    older year, the ASC-606 contract concept in the newer) produces two DISTINCT
    flat signatures that legitimately belong to the ONE `total_revenue` series.
    The arc (d) `claimed_by` collision guard must NOT fire on them — the flat
    lane groups on a single top-line key, not per-concept signature.
    """
    pack = _pack(
        [
            _fy2020_topline(_INTC_FY2020_FIRST_ACCESSION),
            _intc_fy2025_topline(),
        ]
    )

    result = ingest_module.ingest_pack(pack)

    assert result["kpi_ids"] == ["total_revenue"], (
        f"two flat concepts must merge into ONE series; got {result['kpi_ids']}"
    )
    stored = _stored_points(isolated_store)
    assert len(stored) == 2, f"both years must be stored; got {stored}"
    assert {p["kpi_id"] for p in stored} == {"total_revenue"}
    assert {p["period"] for p in stored} == {"2020", "2025"}


def test_flat_lane_keeps_every_vintage_of_one_period(ingest_module, isolated_store):
    """Two vintages of ONE annual period produce TWO points — the flat lane
    routes through the non-collapsing `facts_to_points`, so the restatement the
    store's bitemporal † exists to surface is never erased.
    """
    first = _fixture_fact(_INTC_FY2020_FIRST_ACCESSION)
    restated = _fixture_fact(_INTC_FY2020_RESTATED_ACCESSION)
    pack = _pack(
        [
            _fy2020_topline(_INTC_FY2020_FIRST_ACCESSION),
            _fy2020_topline(_INTC_FY2020_RESTATED_ACCESSION),
        ]
    )

    result = ingest_module.ingest_pack(pack)

    assert result["appended"] == 2, "both vintages must append (no collapse)"
    stored = _stored_points(isolated_store)
    assert sorted(p["value"] for p in stored) == sorted(
        [first["value"], restated["value"]]
    )
    assert {p["as_of"] for p in stored} == {first["filed"], restated["filed"]}
    assert len({first["filed"], restated["filed"]}) == 2, (
        "the fixture's two vintages must carry DIFFERENT filed dates, else this "
        "test cannot distinguish two vintages from one"
    )


def test_ingest_assigns_provenance_per_lane(ingest_module, isolated_store):
    """A Lane B pack carries BOTH kinds of fact, so ONE pack-wide provenance
    label would be factually wrong for half of it. In the SAME ingest call the
    dimensional points keep `xbrl-dimensional` while the flat top-line points
    carry `xbrl-topline` (the envelope declares no `source_kind`).
    """
    ingest_module.ingest_pack(_mixed_pack())

    by_lane = {}
    for point in _stored_points(isolated_store):
        by_lane.setdefault(point["kpi_id"] == "total_revenue", set()).add(
            point["source_kind"]
        )

    assert by_lane[True] == {"xbrl-topline"}, "flat lane must not inherit the dimensional label"
    assert by_lane[False] == {"xbrl-dimensional"}, "dimensional lane's label must be unchanged"


def test_flat_lane_takes_envelope_declared_source_kind(ingest_module, isolated_store):
    """When the pack envelope DECLARES a `source_kind` (Lane A's backfill pack
    declares `xbrl-companyfacts`), the flat top-line points take it — the
    dimensional points still keep `xbrl-dimensional`, since the declaration
    applies to the flat lane only (plan §Notes envelope provenance contract).
    """
    ingest_module.ingest_pack(_mixed_pack(source_kind="xbrl-companyfacts"))

    stored = _stored_points(isolated_store)
    flat_kinds = {p["source_kind"] for p in stored if p["kpi_id"] == "total_revenue"}
    dim_kinds = {p["source_kind"] for p in stored if p["kpi_id"] != "total_revenue"}

    assert flat_kinds == {"xbrl-companyfacts"}
    assert dim_kinds == {"xbrl-dimensional"}


def test_untrusted_source_kind_raises_before_any_write(ingest_module, isolated_store):
    """A pack declaring a `source_kind` OUTSIDE `kpi_gate.TRUSTED_SOURCE_KINDS`
    is rejected loudly BEFORE anything is written — an untrusted kind must never
    ride into the durable store alongside trusted XBRL provenance
    (`kpi_gate.attest_source` would otherwise be handed a poisoned series).
    """
    with pytest.raises(ValueError, match="llm-located"):
        ingest_module.ingest_pack(_mixed_pack(source_kind="llm-located"))

    assert _stored_points(isolated_store) == [], "nothing may be written on rejection"


def test_cross_lane_value_disagreement_raises(ingest_module, isolated_store):
    """SAME dedup key + DIFFERENT value → RAISE, before any append.

    Both lanes read the SAME filing (live-verified: `companyconcept` rows carry
    the same accession/filed as the per-filing parse of that filing), so their
    dedup keys `(company, kpi_id, period, as_of, source_accession)` COINCIDE.
    A value disagreement there means one lane is wrong — and `kpi_store.append`
    would silently keep the FIRST record (`kpi_store.py:321-325`), storing a
    wrong number with no error. This guard pre-empts that.
    """
    captured_value = _probe_flat_sample("INTC", _INTC_TOPLINE_CONCEPT)["value"]
    ingest_module.ingest_pack(_pack([_intc_fy2025_topline()]))
    assert len(_stored_points(isolated_store)) == 1

    # SAME accession / filed / period as the stored point — only the value
    # differs. A deliberate fabrication probe, not a real second observation.
    conflicting = _pack([_intc_fy2025_topline(value=captured_value + 1)])
    with pytest.raises(ValueError, match="disagree"):
        ingest_module.ingest_pack(conflicting)

    stored = _stored_points(isolated_store)
    assert len(stored) == 1, f"the rejected pack must write nothing; got {stored}"
    assert stored[0]["value"] == captured_value


def _rescale_stored_points(store_dir, *, value, scale):
    """Rewrite every stored point's `value`/`scale` in place. Used to express an
    already-stored figure at a DIFFERENT explicit scale — the shape a non-XBRL
    producer already writes into this same store (`kpi_8k_candidates.py:332`
    commits a verbatim cell with `scale=_scale_from_unit(...)`).
    """
    for path in sorted(store_dir.glob("*.json")):
        envelope = json.loads(path.read_text(encoding="utf-8"))
        for point in envelope["points"]:
            point["value"] = value
            point["scale"] = scale
        path.write_text(json.dumps(envelope), encoding="utf-8")


def test_disagreement_compares_on_the_stores_own_scale_semantics(
    ingest_module, isolated_store
):
    """The guard compares through the store's `_canonical_value` (value × the
    explicit per-point `scale`), NOT raw `!=`.

    `scale` is owned by each producer, and a scaled lane already exists in this
    store. Raw comparison would be wrong in BOTH directions, and would also
    disagree with the store's own `history`, which computes its `disagreement`
    flag the canonical way — the guard and the read side must answer the same
    question identically.
    """
    captured_value = _probe_flat_sample("INTC", _INTC_TOPLINE_CONCEPT)["value"]
    pack = _pack([_intc_fy2025_topline()])

    # SAME figure, different representation: (52853, 1e6) == (52853000000, 1).
    # Must NOT raise — a spurious abort on one figure stored at two scales.
    ingest_module.ingest_pack(pack)
    _rescale_stored_points(isolated_store, value=captured_value / 1e6, scale=1e6)
    ingest_module.ingest_pack(pack)
    assert len(_stored_points(isolated_store)) == 1, (
        "same canonical figure at a different scale is not a disagreement"
    )

    # A REAL 10^6 disagreement that raw `!=` would call equal: the stored point
    # keeps the incoming point's digits but at scale 1e6, so the two figures
    # differ by a millionfold. Must RAISE.
    _rescale_stored_points(isolated_store, value=captured_value, scale=1e6)
    with pytest.raises(ValueError, match="disagree"):
        ingest_module.ingest_pack(pack)


def test_disagreement_leaves_the_dimensional_lane_unwritten(
    ingest_module, isolated_store
):
    """The build-then-write split's reason to exist: a top-line rejection must
    also roll back the DIMENSIONAL points of the SAME pack.

    Under the previous append-as-you-go structure the dimensional lane drained
    into the store BEFORE the flat lane was even built, so a flat fact rejected
    at the end of a mixed pack left those dimensional points permanently
    committed to an append-only store — unremovable partial state from a pack
    the driver had refused. Every other guard test here uses a flat-only pack,
    which cannot see that difference; this one is the mixed-pack case where the
    split is load-bearing.
    """
    captured_value = _probe_flat_sample("INTC", _INTC_TOPLINE_CONCEPT)["value"]
    # Seed ONLY the top-line point, so the conflict is discovered on the flat
    # lane of the mixed pack below — after its dimensional points were built.
    ingest_module.ingest_pack(_pack([_intc_fy2025_topline()]))
    baseline = _stored_points(isolated_store)
    assert [p["kpi_id"] for p in baseline] == ["total_revenue"]

    # A MIXED pack: two real dimensional vintages + a flat fact that disagrees
    # with the seeded point on the same dedup key.
    conflicting = _mixed_pack()
    for fact in conflicting["facts"]:
        if not fact["dimensions"]:
            fact["value"] = captured_value + 1
    assert any(fact["dimensions"] for fact in conflicting["facts"]), (
        "this test is only meaningful on a pack that also carries dimensional "
        "facts — they are what the rejection must leave unwritten"
    )

    with pytest.raises(ValueError, match="disagree"):
        ingest_module.ingest_pack(conflicting)

    assert _stored_points(isolated_store) == baseline, (
        "a rejected mixed pack must leave the store byte-identical — its "
        "dimensional points may not survive the flat lane's rejection"
    )


def test_same_period_different_accession_still_appends(ingest_module, isolated_store):
    """SAME period + DIFFERENT accession + DIFFERENT value → APPEND, never raise.

    That is a LEGITIMATE RESTATEMENT and rendering it is the entire point of the
    store's `†`. INTC's real FY2020 pair (first reported in the FY2021 10-K,
    re-presented in the FY2022 10-K) arrives here in two SEPARATE ingest calls —
    the cross-call case the store-aware guard sees — and must produce two
    vintages, not an abort.
    """
    first = _fixture_fact(_INTC_FY2020_FIRST_ACCESSION)
    restated = _fixture_fact(_INTC_FY2020_RESTATED_ACCESSION)
    assert first["value"] != restated["value"], (
        "the fixture's two vintages must genuinely DISAGREE, else this test "
        "cannot prove the guard tolerates a cross-accession disagreement"
    )

    ingest_module.ingest_pack(_pack([_fy2020_topline(_INTC_FY2020_FIRST_ACCESSION)]))
    ingest_module.ingest_pack(_pack([_fy2020_topline(_INTC_FY2020_RESTATED_ACCESSION)]))

    stored = _stored_points(isolated_store)
    assert sorted(p["value"] for p in stored) == sorted(
        [first["value"], restated["value"]]
    ), (
        f"a genuine recast must still append both vintages; got {stored}"
    )
