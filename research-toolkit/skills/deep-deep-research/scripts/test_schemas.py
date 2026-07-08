"""Tests for the flat schemas.py — shape assertions + CLI behavior.

Ported from deep-research/tests/test_schemas.py with flat imports
(`from schemas import ...`), plus CLI tests for the new
`python schemas.py {scope|search|extract|verdict|report}` entrypoint.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent


def test_scope_schema_shape():
    from schemas import SCOPE_SCHEMA

    angles_prop = SCOPE_SCHEMA["properties"]["angles"]
    assert angles_prop["minItems"] == 3
    assert angles_prop["maxItems"] == 6
    assert set(SCOPE_SCHEMA["required"]) == {"question", "angles", "summary"}


def test_verdict_schema_required():
    from schemas import VERDICT_SCHEMA

    assert "refuted" in VERDICT_SCHEMA["required"]
    assert "evidence" in VERDICT_SCHEMA["required"]
    assert "confidence" in VERDICT_SCHEMA["required"]


def test_constants():
    from schemas import (
        MAX_FETCH,
        MAX_VERIFY_CLAIMS,
        REFUTATIONS_REQUIRED,
        VOTES_PER_CLAIM,
    )

    assert VOTES_PER_CLAIM == 3
    assert REFUTATIONS_REQUIRED == 2
    assert MAX_FETCH == 15
    assert MAX_VERIFY_CLAIMS == 25


def test_search_schema_shape():
    from schemas import SEARCH_SCHEMA

    results_prop = SEARCH_SCHEMA["properties"]["results"]
    assert results_prop["maxItems"] == 6
    assert set(results_prop["items"]["required"]) == {"url", "title", "relevance"}
    assert SEARCH_SCHEMA["required"] == ["results"]


def test_extract_schema_shape():
    from schemas import EXTRACT_SCHEMA

    claims_prop = EXTRACT_SCHEMA["properties"]["claims"]
    assert claims_prop["maxItems"] == 5
    assert set(claims_prop["items"]["required"]) == {"claim", "quote", "importance"}
    sq = EXTRACT_SCHEMA["properties"]["sourceQuality"]
    assert set(sq["enum"]) == {"primary", "secondary", "blog", "forum", "unreliable"}


def test_extract_schema_supports_claim_type_and_held_by():
    from schemas import EXTRACT_SCHEMA, ExtractedClaim

    claim_props = EXTRACT_SCHEMA["properties"]["claims"]["items"]["properties"]
    assert set(claim_props["claimType"]["enum"]) == {"fact", "opinion"}
    assert claim_props["heldBy"]["type"] == "string"
    # claimType is NOT required — backward-compat: an extraction response
    # that omits it must not fail schema validation.
    required = EXTRACT_SCHEMA["properties"]["claims"]["items"]["required"]
    assert "claimType" not in required

    ec = ExtractedClaim(claim="c", quote="q", importance="central")
    assert ec.claim_type == "fact"
    assert ec.held_by is None


def test_report_schema_shape():
    from schemas import REPORT_SCHEMA

    assert set(REPORT_SCHEMA["required"]) == {"summary", "findings", "caveats"}
    finding_req = set(REPORT_SCHEMA["properties"]["findings"]["items"]["required"])
    assert finding_req == {"claim", "confidence", "sources", "evidence"}


def test_dataclasses_importable():
    from schemas import (
        Angle,
        ExtractedClaim,
        Finding,
        Report,
        SearchResult,
        Verdict,
    )

    a = Angle(label="test", query="test query")
    assert a.rationale is None

    sr = SearchResult(url="http://x.com", title="X", relevance="high")
    assert sr.snippet is None

    ec = ExtractedClaim(claim="c", quote="q", importance="central",
                        source_url="http://x.com", source_quality="primary")
    assert ec.importance == "central"

    v = Verdict(refuted=False, evidence="e", confidence="high")
    assert v.counter_source is None

    f = Finding(claim="c", confidence="high", sources=["http://x.com"], evidence="e")
    assert f.vote is None

    r = Report(summary="s", findings=[], caveats="none")
    assert r.open_questions == []


# ---------------------------------------------------------------------------
# CLI: python schemas.py {scope|search|extract|verdict|report}
# ---------------------------------------------------------------------------


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "schemas.py"), *args],
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
    )


def test_cli_verdict_prints_schema():
    proc = _run_cli("verdict")
    assert proc.returncode == 0
    parsed = json.loads(proc.stdout)
    assert set(parsed["required"]) >= {"refuted", "evidence", "confidence"}


def test_cli_scope_prints_schema():
    proc = _run_cli("scope")
    assert proc.returncode == 0
    parsed = json.loads(proc.stdout)
    assert parsed["properties"]["angles"]["minItems"] == 3


def test_cli_unknown_name_fails_loud():
    proc = _run_cli("bogus")
    assert proc.returncode == 1
    assert proc.stdout.strip() == ""
    assert "bogus" in proc.stderr
