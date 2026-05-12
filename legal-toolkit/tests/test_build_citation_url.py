#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest>=7.0"]
# ///
"""Tests for build_citation_url.py — Phase 1.7 (v0.3.3+) URL constructors."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "legal-contract-review"
    / "scripts"
    / "build_citation_url.py"
)


@pytest.fixture(scope="session")
def url_builder():
    spec = importlib.util.spec_from_file_location("build_citation_url", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_citation_url"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def sources(url_builder):
    return url_builder.load_legal_sources()


# --------------------------------------------------------- statute


def test_statute_url_民法(url_builder, sources):
    result = url_builder.build_statute_url("民法", "247-1", sources=sources)
    assert (
        result["url"]
        == "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=247-1"
    )
    assert result["source_host"] == "law.moj.gov.tw"
    assert result["source_metadata"]["pcode"] == "B0000001"
    assert result["verified"] == "templated"


def test_statute_alias_短名稱(url_builder, sources):
    """短名稱 alias '個資法' resolves to '個人資料保護法'."""
    result = url_builder.build_statute_url("個資法", "20-1", sources=sources)
    assert result["source_metadata"]["statute"] == "個人資料保護法"
    assert result["source_metadata"]["alias_short_name"] == "個資法"


def test_statute_alias_勞基法(url_builder, sources):
    result = url_builder.build_statute_url("勞基法", "9-1", sources=sources)
    assert result["source_metadata"]["statute"] == "勞動基準法"


def test_statute_alias_消保法(url_builder, sources):
    result = url_builder.build_statute_url("消保法", "17", sources=sources)
    assert result["source_metadata"]["statute"] == "消費者保護法"


def test_statute_unknown_raises(url_builder, sources):
    with pytest.raises(ValueError, match="not in legal-sources.json registry"):
        url_builder.build_statute_url("假法", "1", sources=sources)


def test_statute_url_whitespace_tolerant(url_builder, sources):
    result = url_builder.build_statute_url(" 民法 ", " 247-1 ", sources=sources)
    assert "pcode=B0000001" in result["url"]
    # article is passed verbatim to template — verify .format() ran
    assert "flno= 247-1 " in result["url"] or "flno=247-1" in result["url"]


# --------------------------------------------------------- case


def test_case_url_最高法院(url_builder, sources):
    result = url_builder.build_case_url("最高法院", 105, "台上", 1501, sources=sources)
    assert "judgment.judicial.gov.tw" in result["url"]
    assert "TPSV,105,台上,1501" in result["url"]
    assert result["source_metadata"]["court_code"] == "TPSV"
    assert result["verified"] == "templated"


def test_case_url_智財法院(url_builder, sources):
    result = url_builder.build_case_url(
        "智慧財產法院", 102, "民營訴", 6, sources=sources
    )
    assert result["source_metadata"]["court_code"] == "IPCV"


def test_case_url_unknown_court_falls_back_to_search(url_builder, sources):
    """Unknown court → fall back to search URL with verified='search-only'."""
    result = url_builder.build_case_url(
        "高雄少年及家事法院", 110, "少訴", 1, sources=sources
    )
    assert result["verified"] == "search-only"
    assert result["url"] == sources["case_sources"]["default"]["search_url"]
    assert "fallback_reason" in result["source_metadata"]


def test_case_year_must_be_int(url_builder, sources):
    """python integer not str; URL formatting will fail visibly if upstream passes str."""
    result = url_builder.build_case_url("最高法院", 105, "台上", 1501, sources=sources)
    assert ",105," in result["url"]


# --------------------------------------------------------- function letter


def test_function_letter_url_PDPC(url_builder, sources):
    result = url_builder.build_function_letter_url(
        "個人資料保護委員會", sources=sources
    )
    assert result["source_host"] == "pdpc.gov.tw"
    assert result["verified"] == "search-only"


def test_function_letter_url_unknown_agency_raises(url_builder, sources):
    with pytest.raises(ValueError, match="not in function_letter_sources registry"):
        url_builder.build_function_letter_url("假機關", sources=sources)


def test_function_letter_includes_fetch_note(url_builder, sources):
    """PDPC entry carries a fetch_note about the 2025-08 jurisdiction migration."""
    result = url_builder.build_function_letter_url(
        "個人資料保護委員會", sources=sources
    )
    assert "2025-08" in result["source_metadata"]["fetch_note"]


# --------------------------------------------------------- legal-sources.json shape


def test_legal_sources_load(url_builder):
    sources = url_builder.load_legal_sources()
    assert "statute_sources" in sources
    assert "case_sources" in sources
    assert "function_letter_sources" in sources
    assert "ttl_defaults" in sources
    assert "fetch_budget_defaults" in sources


def test_statute_sources_contain_canonical_TW_laws(url_builder):
    sources = url_builder.load_legal_sources()
    for required in (
        "民法",
        "個人資料保護法",
        "營業秘密法",
        "公平交易法",
        "著作權法",
        "勞動基準法",
    ):
        assert required in sources["statute_sources"], f"{required} missing"


def test_ttl_defaults_are_positive_ints(url_builder):
    sources = url_builder.load_legal_sources()
    ttl = sources["ttl_defaults"]
    for field in ("statute_days", "case_days", "function_letter_days", "applicability_notes_days"):
        assert isinstance(ttl[field], int)
        assert ttl[field] >= 1


def test_fetch_budget_max_is_positive(url_builder):
    sources = url_builder.load_legal_sources()
    assert sources["fetch_budget_defaults"]["max_unique_citations_per_run"] >= 1


# --------------------------------------------------------- CLI


def test_cli_statute_emits_json(url_builder, capsys):
    rc = url_builder.main(
        ["statute", "--statute", "民法", "--article", "247-1"]
    )
    assert rc == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert "pcode=B0000001" in payload["url"]


def test_cli_case_emits_json(url_builder, capsys):
    rc = url_builder.main(
        [
            "case",
            "--court", "最高法院",
            "--year", "105",
            "--type", "台上",
            "--number", "1501",
        ]
    )
    assert rc == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert "TPSV,105,台上,1501" in payload["url"]


def test_cli_unknown_statute_exits_1(url_builder, capsys):
    rc = url_builder.main(["statute", "--statute", "假法", "--article", "1"])
    assert rc == 1


def test_cli_function_letter_emits_json(url_builder, capsys):
    rc = url_builder.main(["function-letter", "--agency", "公平交易委員會"])
    assert rc == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["source_host"] == "ftc.gov.tw"
