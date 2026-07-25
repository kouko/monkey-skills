"""Regenerate `kpi_id_identity_probe_2026-07-25.json` — the live grounding
capture behind the §Probe evidence numbers in
`docs/loom/specs/2026-07-25-kpi-id-injective-identity.md`.

WHAT IT ANSWERS. `derive_kpi_id` (`kpi_xbrl_ingest.py`) mints the durable
`kpi_id` for every dimensional KPI point from a lossy slug of the fact's
XBRL signature. Two claims about that loss cannot be settled from in-repo
fixtures — they are claims about the SHAPE of real filers' XBRL tagging:
(1) how often does dropping the `ConsolidationItemsAxis` qualifier collide
two genuinely different amounts into one id, and does the same abort happen
across a broad filer sample, not just the two filers (XOM, JPM) found by
hand; (2) how often does one filer spell one XBRL element two different
ways (typically split along the 10-Q/10-K boundary), and is folding those
spellings together safe (does it ever also fold two GENUINELY distinct
signatures)? This script replays `ingest_pack`'s selector+claim loop against
each fetched filer, with no store write, so "would this pack abort today?"
is measured, not guessed. Two different sourcing choices apply to the two
halves of that replay, and each is deliberate: SELECTOR BUILDING
(`_signature_key`, `_consumer_consolidation`) stays imported live from
`kpi_xbrl_ingest` — this arc leaves both untouched (its brief scopes
`_fact_matches`/`_signature_key` semantics out), so importing them keeps
selector-building faithful to production as it evolves. KPI-ID DERIVATION
for the "current"/"today" half is a FROZEN vendored copy,
`_legacy_kpi_id` (below), reproducing `derive_kpi_id` exactly as it stood
at the pre-arc baseline commit `90374e63` — never the live import — because
this same arc's Tasks 1-3 edit `derive_kpi_id` in the working tree; a
"current baseline" that tracked the live function would silently stop
meaning "today's damage" and start scoring the arc's own in-flight fix
against itself. See `_legacy_kpi_id`'s docstring for why. It also scores
the PROPOSED C'
identity (readable prefix incl. a non-default consolidation member, plus a
12-hex digest of the CASE-FOLDED consumer identity tuple) against the same
corpus. Only COUNTS are captured — collision counts by kind, co-occurrence
(do colliding claimants share a filing, or are they disjoint across
filings), the observed `ConsolidationItemsAxis` member domain, and the
proposed scheme's fold/collision counts. No financial values, no per-fact
values, ever land in the output.

A data probe answers "does this shape exist", never "does the pipeline
survive" (`docs/loom/memory/a-data-probe-is-not-a-pipeline-dogfood.md`) —
the pipeline claim needed its own live dogfood at close-out, separate from
this capture.

NETWORK. Hits `data.sec.gov` live, via `pack.py --pack kpi-quarterly`
subprocesses (SEC fair-access: sequential, one filer at a time); NOT part
of the offline suite (it is not a `test_*` module and pytest never collects
it). Re-run by hand when the probe evidence is questioned:

    python3 investing-toolkit/tests/data/fixtures/\\
      capture_kpi_id_identity_probe.py > \\
      investing-toolkit/tests/data/fixtures/\\
      kpi_id_identity_probe_2026-07-25.json

Each filer's fetched pack is cached under `_CACHE_DIR` (a fixed temp
location) and re-fetch is skipped when a cached pack already exists — same
fair-access posture as the sibling probe script's fetch loop. Delete the
cache directory to force a full re-fetch.

FILER SAMPLE, and why each is in it: 47 US filers spanning the sectors
where `ConsolidationItemsAxis` reconciliation tables and multi-spelling
segment tags are both common — energy majors (XOM CVX COP PSX), money-
center banks (JPM BAC WFC C GS MS), tech/consumer megacaps (AAPL MSFT
GOOGL AMZN META NVDA INTC AMD IBM ORCL CRM QCOM TXN), retail (WMT COST TGT
HD LOW MCD NKE), consumer staples/healthcare (KO PEP PG JNJ PFE MRK UNH),
and industrials/autos/telecom (CAT BA GE HON F GM TSLA T VZ DIS). The
sample is broad-by-sector, not curated to reproduce a known bug — XOM and
JPM (found by hand, motivating this arc) sit inside it rather than being
the whole of it, so the measured 23/47 abort rate is evidence about
US-filer XBRL tagging in general, not about two known-bad filers.

This script mirrors `capture_companyconcept_form_domain.py`'s structure
(module docstring stating WHAT IT ANSWERS / NETWORK / FILER SAMPLE, single
runnable file, JSON to stdout) but differs in one respect that precedent
does not need: `kpi-quarterly` packs come from a CLI (`pack.py`), not a
single HTTP GET, so fetching here is a `pack.py` subprocess per ticker
rather than a direct `urllib` call.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

_HERE = Path(__file__).resolve()
_REPO_ROOT = _HERE.parents[4]
_DATA_MARKETS_SCRIPTS = _REPO_ROOT / "investing-toolkit" / "skills" / "data-markets" / "scripts"
_ANALYSIS_KPI_SCRIPTS = _REPO_ROOT / "investing-toolkit" / "skills" / "analysis-kpi" / "scripts"
sys.path.insert(0, str(_ANALYSIS_KPI_SCRIPTS))
import kpi_xbrl_ingest as ing  # noqa: E402

_CACHE_DIR = Path(tempfile.gettempdir()) / "kpi_id_identity_probe_packs"

TICKERS = [
    "XOM", "CVX", "COP", "PSX",
    "JPM", "BAC", "WFC", "C", "GS", "MS",
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "INTC", "AMD", "IBM",
    "ORCL", "CRM", "QCOM", "TXN",
    "WMT", "COST", "TGT", "HD", "LOW", "MCD", "NKE",
    "KO", "PEP", "PG", "JNJ", "PFE", "MRK", "UNH",
    "CAT", "BA", "GE", "HON", "F", "GM", "TSLA", "T", "VZ", "DIS",
]


# --- FROZEN legacy derivation (pre-arc baseline, commit `90374e63`) --------
# This block is a HISTORICAL RECORD of what the OLD kpi_id scheme did to the
# corpus, not a live view of `kpi_xbrl_ingest.derive_kpi_id`. It must never
# be pointed back at that import, and never "kept in sync" with it — see
# `_legacy_kpi_id`'s docstring for why syncing would silently break this
# script's own regenerate command.
_LEGACY_CONSOLIDATION_AXIS_LOCAL = "consolidationitems"


def _legacy_local_name(qname) -> str:
    """Frozen copy of `derive_kpi_id`'s `_local_name` helper as it stood at
    commit `90374e63`. See `_legacy_kpi_id`."""
    return str(qname).split(":")[-1]


def _legacy_strip_axis_member_suffix(name: str) -> str:
    """Frozen copy of `derive_kpi_id`'s `_strip_axis_member_suffix` helper
    as it stood at commit `90374e63`. See `_legacy_kpi_id`."""
    for suffix in ("Axis", "Member"):
        if name.endswith(suffix) and len(name) > len(suffix):
            return name[: -len(suffix)]
    return name


def _legacy_slug_token(qname) -> str:
    """Frozen copy of `derive_kpi_id`'s `_slug_token` helper as it stood at
    commit `90374e63`. See `_legacy_kpi_id`."""
    return _legacy_strip_axis_member_suffix(_legacy_local_name(qname)).lower()


def _legacy_kpi_id(concept, dimensions) -> str:
    """FROZEN reproduction of `derive_kpi_id` exactly as it behaved at the
    pre-arc baseline commit `90374e63` — before Task 1 added the optional
    `consolidation` parameter, and before Task 2's further edit to that same
    function. Deliberately NOT wired to the live `kpi_xbrl_ingest.
    derive_kpi_id` import.

    Why frozen rather than imported: this script exists to answer "how much
    damage does the CURRENT/shipped scheme do to real filers today", and
    "today" has to mean a fixed point in history, not whatever `derive_kpi_id`
    happens to read as on the branch that is actively rewriting it. The live
    function already carries Task 1's edit in the working tree (a new third
    param that happens to default to a no-op today, so the SAME 2-arg call
    this script makes still reproduces pre-arc behavior by coincidence, not
    by design) and will carry Task 2's further edit once that task lands —
    at which point the same 2-arg call would silently start folding
    case-drift collisions inside what this script reports as the "before"
    baseline, and a fresh-checkout re-run would stop reproducing today's
    committed numbers (23 aborting filers, 149 collisions) with no error
    raised. Freezing the derivation here instead means this script's own
    regenerate command keeps reproducing those numbers after this arc
    merges, with no checkout gymnastics.

    Verified against `git show 90374e63:investing-toolkit/skills/
    analysis-kpi/scripts/kpi_xbrl_ingest.py`'s `derive_kpi_id` +
    `_slug_token` + `_local_name` + `_strip_axis_member_suffix` — see
    `_capture.legacy_derivation_vintage` in this script's output for the
    commit a reader can diff against.
    """
    parts = []
    for axis in sorted(dimensions):
        axis_token = _legacy_slug_token(axis)
        if axis_token == _LEGACY_CONSOLIDATION_AXIS_LOCAL:
            continue  # reconciliation qualifier, not a breakdown axis
        member_token = _legacy_slug_token(dimensions[axis])
        parts.append(f"{axis_token}-{member_token}")
    concept_token = _legacy_slug_token(concept)
    if not parts:
        return concept_token
    return concept_token + "__" + "__".join(parts)


def _fetch_pack(ticker: str) -> Path:
    """Fetch one filer's `kpi-quarterly` pack via `pack.py`, caching under
    `_CACHE_DIR` so a re-run of this script (or a prior run's cache) never
    re-hits SEC for a ticker it already has."""
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = _CACHE_DIR / f"{ticker}.json"
    if out_path.exists() and out_path.stat().st_size > 0:
        return out_path
    result = subprocess.run(
        [
            "uv", "run", "--quiet",
            "--with", "requests==2.33.1", "--with", "edgartools==5.42.0",
            "pack.py", "--ticker", ticker, "--pack", "kpi-quarterly",
        ],
        cwd=str(_DATA_MARKETS_SCRIPTS),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=120,
    )
    out_path.write_text(result.stdout)
    return out_path


# --- the PROPOSED C' derivation (candidate scored against the corpus) ------
def _proposed_kpi_id(concept, dimensions, consolidation):
    """Readable prefix + 12-hex digest of the CASE-FOLDED consumer identity
    tuple — the C' mechanism (brief §Chosen mechanism). The prefix is built
    from the FROZEN `_legacy_kpi_id` (pre-arc baseline, commit `90374e63`),
    never the live `derive_kpi_id` import — same reason as `_analyze`'s
    "current" half: Tasks 1-3 are editing `derive_kpi_id` on this same arc,
    so a live call here would score the proposed scheme's prefix against a
    moving target instead of the fixed baseline this probe is measuring
    delta from. `_consumer_consolidation` stays live-imported — this arc
    does not touch it."""
    prefix = _legacy_kpi_id(concept, dimensions)
    norm = ing._consumer_consolidation(consolidation)
    if norm != "OperatingSegmentsMember":
        prefix += "__" + ing._slug_token(norm)
    ident = "\x00".join(
        [
            str(concept).casefold(),
            "|".join(
                f"{axis.casefold()}={str(member).casefold()}"
                for axis, member in sorted(dimensions.items())
            ),
            str(norm).casefold(),
        ]
    )
    return f"{prefix}__{hashlib.sha1(ident.encode('utf-8')).hexdigest()[:12]}"


def _casefold_ident(concept, dimensions, norm):
    return (
        str(concept).casefold(),
        tuple(
            sorted(
                (str(axis).casefold(), str(member).casefold())
                for axis, member in dimensions.items()
            )
        ),
        str(norm).casefold(),
    )


def _classify(keys):
    """Why did these signature keys collide under the CURRENT scheme?
    Two shapes were measured: a `ConsolidationItemsAxis`-only difference
    (one concept, one dimensions tuple, two consolidation members), and a
    CASE-drift difference — the concept OR a dimension member spelled two
    ways. The member-side branch below is the fix over the scratchpad
    probe's classifier: `dims` there is the whole sorted-items tuple per
    key, so a member spelled two ways changes THAT tuple, not just the
    concept, and fell through to an unlabelled "other" bucket for 10 of the
    47-filer corpus's 21 case-drift collisions. Comparing the CASE-FOLDED
    dims tuples catches those.
    """
    concepts = {k[0] for k in keys}
    dims = {k[1] for k in keys}
    consol = {k[2] for k in keys}
    if len(concepts) == 1 and len(dims) == 1 and len(consol) > 1:
        return "consolidation-axis"
    if len(concepts) == 1 and len(dims) > 1:
        casefolded_dims = {
            tuple(sorted((str(axis).casefold(), str(member).casefold()) for axis, member in d))
            for d in dims
        }
        if len(casefolded_dims) == 1:
            return "case-drift"  # member spelling drift, e.g. DataCenterMember vs DatacenterMember
    if len(concepts) > 1:
        locals_ = {str(c).split(":")[-1] for c in concepts}
        prefixes = {str(c).rsplit(":", 1)[0] if ":" in str(c) else "" for c in concepts}
        if len(locals_) > 1 and len({name.casefold() for name in locals_}) == 1:
            return "case-drift" if len(prefixes) == 1 else "case-drift+namespace"
        if len(locals_) == 1 and len(prefixes) > 1:
            return "cross-namespace"
        return "other-slug-collision"
    return "other"


def _analyze(pack_path: Path):
    pack = json.loads(pack_path.read_text())
    ticker = pack.get("ticker") or pack_path.stem
    facts = pack.get("facts") or []
    if not facts:
        return {"ticker": ticker, "error": pack.get("_status", {}).get("status", "no facts")}

    selectors = {}
    by_key = defaultdict(list)
    for fact in facts:
        dimensions = fact.get("dimensions") or {}
        if not dimensions:
            continue  # top-line lane: fixed literal id, out of scope for this probe
        key = ing._signature_key(fact.get("concept"), dimensions, fact.get("consolidation"))
        selectors.setdefault(key, {"concept": fact.get("concept"), "dimensions": dimensions})
        by_key[key].append(fact)

    # "today's damage": the FROZEN pre-arc derivation (`_legacy_kpi_id`), not
    # the live `derive_kpi_id` import — see `_legacy_kpi_id`'s docstring.
    current = defaultdict(list)
    for key, match in selectors.items():
        current[_legacy_kpi_id(match["concept"], match["dimensions"])].append(key)
    collisions = {kid: keys for kid, keys in current.items() if len(keys) > 1}

    # silent mislabel: no collision, but the sole claimant carries a
    # non-default consolidation member and the id reads as the default view
    mislabeled = [
        (kid, keys[0][2])
        for kid, keys in current.items()
        if len(keys) == 1 and keys[0][2] != "OperatingSegmentsMember"
    ]

    proposed = defaultdict(list)
    for key, match in selectors.items():
        proposed[_proposed_kpi_id(match["concept"], match["dimensions"], key[2])].append(key)

    n_intended_folds = 0
    n_unintended_merges = 0
    for kid, keys in proposed.items():
        if len(keys) <= 1:
            continue
        idents = {
            _casefold_ident(selectors[k]["concept"], selectors[k]["dimensions"], k[2])
            for k in keys
        }
        if len(idents) == 1:
            n_intended_folds += 1  # every claimant is case-insensitively the same signature
        else:
            n_unintended_merges += 1  # genuinely distinct signatures shared one proposed id

    def co_occurs(keys):
        accessions = {k: {f.get("accession") for f in by_key[k]} for k in keys}
        shared = set.intersection(*accessions.values()) if len(accessions) > 1 else set()
        return bool(shared)

    return {
        "ticker": ticker,
        "n_facts": len(facts),
        "n_selectors": len(selectors),
        "consolidation_members": dict(
            Counter(ing._consumer_consolidation(f.get("consolidation")) for f in facts)
        ),
        "current_aborts": bool(collisions),
        "current_collisions_by_kind": dict(Counter(_classify(keys) for keys in collisions.values())),
        "n_collisions_co_occurring_in_one_filing": sum(
            1 for keys in collisions.values() if co_occurs(keys)
        ),
        "n_collisions_disjoint_across_filings": sum(
            1 for keys in collisions.values() if not co_occurs(keys)
        ),
        "n_silently_mislabeled_ids": len(mislabeled),
        "proposed_n_ids": len(proposed),
        "n_intended_folds": n_intended_folds,
        "n_unintended_merges": n_unintended_merges,
    }


def main():
    pack_paths = [_fetch_pack(ticker) for ticker in TICKERS]
    results = []
    for path in pack_paths:
        try:
            results.append(_analyze(path))
        except Exception as exc:  # a probe never hides a failure
            results.append({"ticker": path.stem, "error": f"{type(exc).__name__}: {exc}"})
    ok = [r for r in results if "error" not in r]

    summary = {
        "n_filers_analyzed": len(ok),
        "n_filers_errored": len(results) - len(ok),
        "n_filers_aborting_today": sum(1 for r in ok if r["current_aborts"]),
        "filers_aborting_today": sorted(r["ticker"] for r in ok if r["current_aborts"]),
        "collision_kinds": dict(
            sum((Counter(r["current_collisions_by_kind"]) for r in ok), Counter())
        ),
        "n_collisions_co_occurring_in_one_filing": sum(
            r["n_collisions_co_occurring_in_one_filing"] for r in ok
        ),
        "n_collisions_disjoint_across_filings": sum(
            r["n_collisions_disjoint_across_filings"] for r in ok
        ),
        "n_filers_with_silent_mislabel": sum(1 for r in ok if r["n_silently_mislabeled_ids"]),
        "total_silently_mislabeled_ids": sum(r["n_silently_mislabeled_ids"] for r in ok),
        "consolidation_member_domain": dict(
            sum((Counter(r["consolidation_members"]) for r in ok), Counter())
        ),
        "total_facts": sum(r["n_facts"] for r in ok),
        "total_selectors": sum(r["n_selectors"] for r in ok),
        "proposed_total_distinct_ids": sum(r["proposed_n_ids"] for r in ok),
        "n_intended_folds": sum(r["n_intended_folds"] for r in ok),
        "proposed_total_collisions": sum(r["n_unintended_merges"] for r in ok),
    }
    doc = {
        "_capture": {
            "what": (
                "Replay of ingest_pack's selector+claim loop over 47 US "
                "filers' kpi-quarterly packs, no store write, scoring both "
                "the CURRENT scheme (collisions, kinds, silent mislabels) "
                "and the PROPOSED C' identity (case-folded digest) on the "
                "same corpus. Grounds "
                "docs/loom/specs/2026-07-25-kpi-id-injective-identity.md "
                "§Probe evidence. Selector building (_signature_key, "
                "_consumer_consolidation) is imported live from "
                "kpi_xbrl_ingest — this arc leaves it untouched. KPI-id "
                "derivation for the CURRENT scheme is a frozen vendored "
                "copy (see legacy_derivation_vintage below and "
                "_legacy_kpi_id's docstring), not the live derive_kpi_id "
                "import, because this same arc's Tasks 1-3 edit that "
                "function."
            ),
            "endpoint": "pack.py --pack kpi-quarterly (data.sec.gov, per ticker)",
            "captured_at": "2026-07-25",
            "legacy_derivation_vintage": (
                "90374e63 — the pre-arc baseline commit `_legacy_kpi_id` "
                "reproduces exactly. Diff `_legacy_kpi_id` in this script "
                "against `git show 90374e63:investing-toolkit/skills/"
                "analysis-kpi/scripts/kpi_xbrl_ingest.py`'s derive_kpi_id "
                "to re-verify the freeze."
            ),
            "filer_sample_rationale": (
                "47 US filers across energy, banking, tech/consumer, retail, "
                "staples/healthcare, and industrials/autos/telecom — broad by "
                "sector, not curated to reproduce a known bug; see module "
                "docstring FILER SAMPLE."
            ),
            "regenerate": "investing-toolkit/tests/data/fixtures/capture_kpi_id_identity_probe.py",
            "note": (
                "Counts only. No financial values and no per-fact values are "
                "captured here — only collision counts, kinds, co-occurrence, "
                "and the observed ConsolidationItemsAxis member domain."
            ),
        },
        "_summary": summary,
        "per_filer": results,
    }
    print(json.dumps(doc, indent=1))


if __name__ == "__main__":
    main()
