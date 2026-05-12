#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest>=7.0"]
# ///
"""Tests for cache_check.py — Phase 1.7 (v0.3.3+) runtime-fetch cache.

Strategy: build temporary cache directory trees, write valid / expired /
malformed entries, verify check_cache returns correct status + reason.
"""

from __future__ import annotations

import datetime as _dt
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
    / "cache_check.py"
)


@pytest.fixture(scope="session")
def cache_check():
    spec = importlib.util.spec_from_file_location("cache_check", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["cache_check"] = module
    spec.loader.exec_module(module)
    return module


def _make_entry(*, type_, key, ttl_days=30, fetched_at=None, **content):
    fetched = fetched_at or _dt.datetime.now()
    expires = fetched + _dt.timedelta(days=ttl_days)
    return {
        "$schema_version": "v0.3.3",
        "type": type_,
        "key": key,
        "fetched_at": fetched.replace(microsecond=0).isoformat(),
        "ttl_days": ttl_days,
        "expires_at": expires.replace(microsecond=0).isoformat(),
        "source_url": "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=247-1",
        "fetch_method": "llm_webfetch",
        "fetch_attempt_count": 1,
        "content": content or {
            "statute": "民法",
            "article": "247-1",
            "title": "民法第二百四十七條之一",
        },
        "verification": {"exists": True, "is_current": True, "deprecated": False, "successor": None},
    }


def _write_cache(cache_dir: Path, type_, key, entry):
    sub_map = {"statute": "statutes", "case": "cases", "function_letter": "function_letters"}
    path = cache_dir / sub_map[type_] / f"{key}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


# --------------------------------------------------------- key normalization


def test_statute_cache_key(cache_check):
    assert cache_check.statute_cache_key("民法", "247-1") == "民法-247-1"
    # whitespace around inputs gets stripped
    assert cache_check.statute_cache_key(" 民法 ", " 247-1 ") == "民法-247-1"


def test_statute_cache_key_strips_path_chars(cache_check):
    # path separators must not leak into the cache filename
    assert "/" not in cache_check.statute_cache_key("民法/施行細則", "1")
    assert "\\" not in cache_check.statute_cache_key("民法", "1\\2")


def test_case_cache_key(cache_check):
    key = cache_check.case_cache_key("最高法院", 105, "台上", 1501)
    assert key == "最高法院-105-台上-1501"


def test_function_letter_cache_key(cache_check):
    key = cache_check.function_letter_cache_key("個人資料保護委員會", "113-0001")
    assert key == "個人資料保護委員會-113-0001"


# --------------------------------------------------------- check_cache


def test_hit_returns_entry(cache_check, tmp_path):
    cache_dir = tmp_path / "cache"
    entry = _make_entry(type_="statute", key="民法-247-1")
    _write_cache(cache_dir, "statute", "民法-247-1", entry)

    result = cache_check.check_cache("statute", key="民法-247-1", cache_dir=cache_dir)
    assert result["status"] == "hit"
    assert result["entry"] == entry
    assert result["path"] is not None


def test_miss_returns_no_entry(cache_check, tmp_path):
    result = cache_check.check_cache("statute", key="民法-247-1", cache_dir=tmp_path / "cache")
    assert result["status"] == "miss"
    assert result["entry"] is None


def test_expired_returns_entry(cache_check, tmp_path):
    cache_dir = tmp_path / "cache"
    # Fetched 60 days ago with 30-day TTL → expired
    past = _dt.datetime.now() - _dt.timedelta(days=60)
    entry = _make_entry(type_="statute", key="民法-247-1", fetched_at=past, ttl_days=30)
    _write_cache(cache_dir, "statute", "民法-247-1", entry)

    result = cache_check.check_cache("statute", key="民法-247-1", cache_dir=cache_dir)
    assert result["status"] == "expired"
    # Even on expired, the entry IS returned (LLM may opt to use stale rather than refetch)
    assert result["entry"] == entry


def test_invalid_json_returns_invalid(cache_check, tmp_path):
    cache_dir = tmp_path / "cache"
    path = cache_dir / "statutes" / "民法-247-1.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not valid json", encoding="utf-8")

    result = cache_check.check_cache("statute", key="民法-247-1", cache_dir=cache_dir)
    assert result["status"] == "invalid"
    assert "JSON decode error" in result["reason"]


def test_missing_required_keys_returns_invalid(cache_check, tmp_path):
    cache_dir = tmp_path / "cache"
    bad = {"type": "statute", "key": "民法-247-1"}  # missing many required
    _write_cache(cache_dir, "statute", "民法-247-1", bad)

    result = cache_check.check_cache("statute", key="民法-247-1", cache_dir=cache_dir)
    assert result["status"] == "invalid"
    assert "missing required keys" in result["reason"]


def test_unrecognised_type_in_entry_invalid(cache_check, tmp_path):
    cache_dir = tmp_path / "cache"
    entry = _make_entry(type_="statute", key="民法-247-1")
    entry["type"] = "magic"
    _write_cache(cache_dir, "statute", "民法-247-1", entry)

    result = cache_check.check_cache("statute", key="民法-247-1", cache_dir=cache_dir)
    assert result["status"] == "invalid"
    assert "invalid type" in result["reason"]


def test_unparseable_expires_at_invalid(cache_check, tmp_path):
    cache_dir = tmp_path / "cache"
    entry = _make_entry(type_="statute", key="民法-247-1")
    entry["expires_at"] = "not-a-date"
    _write_cache(cache_dir, "statute", "民法-247-1", entry)

    result = cache_check.check_cache("statute", key="民法-247-1", cache_dir=cache_dir)
    assert result["status"] == "invalid"


def test_ttl_days_zero_invalid(cache_check, tmp_path):
    cache_dir = tmp_path / "cache"
    entry = _make_entry(type_="statute", key="民法-247-1")
    entry["ttl_days"] = 0
    _write_cache(cache_dir, "statute", "民法-247-1", entry)

    result = cache_check.check_cache("statute", key="民法-247-1", cache_dir=cache_dir)
    assert result["status"] == "invalid"


def test_just_expired_at_boundary(cache_check, tmp_path):
    cache_dir = tmp_path / "cache"
    # Set expires_at to be 1 second in the past; pin "now" to a deterministic value
    pinned_now = _dt.datetime(2026, 5, 12, 12, 0, 0)
    just_past = pinned_now - _dt.timedelta(seconds=1)
    entry = _make_entry(type_="statute", key="民法-247-1")
    entry["expires_at"] = just_past.replace(microsecond=0).isoformat()
    _write_cache(cache_dir, "statute", "民法-247-1", entry)

    result = cache_check.check_cache("statute", key="民法-247-1", cache_dir=cache_dir, now=pinned_now)
    assert result["status"] == "expired"


def test_just_before_expiry_is_hit(cache_check, tmp_path):
    cache_dir = tmp_path / "cache"
    pinned_now = _dt.datetime(2026, 5, 12, 12, 0, 0)
    just_future = pinned_now + _dt.timedelta(seconds=1)
    entry = _make_entry(type_="statute", key="民法-247-1")
    entry["expires_at"] = just_future.replace(microsecond=0).isoformat()
    _write_cache(cache_dir, "statute", "民法-247-1", entry)

    result = cache_check.check_cache("statute", key="民法-247-1", cache_dir=cache_dir, now=pinned_now)
    assert result["status"] == "hit"


# --------------------------------------------------------- case / function-letter parity


def test_case_cache_hit(cache_check, tmp_path):
    cache_dir = tmp_path / "cache"
    entry = _make_entry(type_="case", key="最高法院-105-台上-1501")
    entry["content"] = {"court": "最高法院", "year": 105, "case_type": "台上", "number": 1501}
    _write_cache(cache_dir, "case", "最高法院-105-台上-1501", entry)

    result = cache_check.check_cache("case", key="最高法院-105-台上-1501", cache_dir=cache_dir)
    assert result["status"] == "hit"


def test_function_letter_cache_hit(cache_check, tmp_path):
    cache_dir = tmp_path / "cache"
    entry = _make_entry(type_="function_letter", key="個人資料保護委員會-113-0001")
    entry["content"] = {"agency": "個人資料保護委員會", "letter_id": "113-0001"}
    _write_cache(cache_dir, "function_letter", "個人資料保護委員會-113-0001", entry)

    result = cache_check.check_cache(
        "function_letter", key="個人資料保護委員會-113-0001", cache_dir=cache_dir
    )
    assert result["status"] == "hit"


# --------------------------------------------------------- defaults


def test_default_cache_dir(cache_check):
    expected = Path.cwd() / ".legal-toolkit" / "cache"
    assert cache_check.default_cache_dir() == expected


def test_unsupported_entry_type_raises(cache_check):
    with pytest.raises(ValueError):
        cache_check.cache_path_for(Path("/tmp"), "magic", "key")


# --------------------------------------------------------- CLI


def test_cli_miss_exits_1(cache_check, tmp_path, capsys, monkeypatch):
    rc = cache_check.main(
        [
            "--cache-dir", str(tmp_path / "cache"),
            "statute",
            "--statute", "民法",
            "--article", "247-1",
        ]
    )
    assert rc == 1
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["status"] == "miss"


def test_cli_hit_exits_0(cache_check, tmp_path, capsys):
    cache_dir = tmp_path / "cache"
    entry = _make_entry(type_="statute", key="民法-247-1")
    _write_cache(cache_dir, "statute", "民法-247-1", entry)

    rc = cache_check.main(
        [
            "--cache-dir", str(cache_dir),
            "statute",
            "--statute", "民法",
            "--article", "247-1",
        ]
    )
    assert rc == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["status"] == "hit"
    assert payload["entry"]["key"] == "民法-247-1"


def test_cli_expired_exits_2(cache_check, tmp_path, capsys):
    cache_dir = tmp_path / "cache"
    past = _dt.datetime.now() - _dt.timedelta(days=60)
    entry = _make_entry(type_="statute", key="民法-247-1", fetched_at=past, ttl_days=30)
    _write_cache(cache_dir, "statute", "民法-247-1", entry)

    rc = cache_check.main(
        [
            "--cache-dir", str(cache_dir),
            "statute",
            "--statute", "民法",
            "--article", "247-1",
        ]
    )
    assert rc == 2


def test_cli_invalid_exits_3(cache_check, tmp_path, capsys):
    cache_dir = tmp_path / "cache"
    path = cache_dir / "statutes" / "民法-247-1.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("not json", encoding="utf-8")

    rc = cache_check.main(
        [
            "--cache-dir", str(cache_dir),
            "statute",
            "--statute", "民法",
            "--article", "247-1",
        ]
    )
    assert rc == 3
