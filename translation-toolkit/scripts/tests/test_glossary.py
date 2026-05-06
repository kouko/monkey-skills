"""Tests for scripts/lib/glossary.py — parser + EN-pivot fallback lookup.

Covers Task C1 of translation-toolkit v0.1.0 plan (lines 1018-1102):
  1. test_lookup_direct_pair_hit
  2. test_lookup_via_en_pivot
  3. test_lookup_misses
  4. test_lookup_with_domain_filter
  5. test_lookup_pair_filename_alphabetical
  6. test_lookup_reverse_direction_via_direct
  7. test_parse_pair_file_handles_meta_section
  8. test_parse_pair_file_real_canonical_files
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

# tests/ -> scripts/ -> translation-toolkit/ -> repo root
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = SCRIPTS_DIR.parent.parent
CANONICAL_DIR = SCRIPTS_DIR / "canonical"

# Make `scripts/` importable so `from lib.glossary import ...` works
# (mirrors how other test files reference scripts via subprocess; here we
# import directly because lookup is a library function, not a CLI).
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.glossary import lookup, parse_pair_file  # noqa: E402


# -------------------- fixtures --------------------

def _write_pair_file(
    path: Path,
    lang_a: str,
    lang_b: str,
    domain_to_rows: dict[str, list[tuple[str, str]]],
    *,
    include_meta: bool = False,
) -> None:
    """Write a minimal valid pair file at `path`.

    domain_to_rows: {domain_name: [(lang_a_term, lang_b_term), ...]}.
    """
    lines: list[str] = []
    lines.append("---")
    lines.append(f"pair: [{lang_a}, {lang_b}]")
    lines.append("version: 0.1.0")
    lines.append("sources: [test]")
    lines.append(f"domains_supported: [{', '.join(domain_to_rows.keys())}]")
    lines.append("---")
    lines.append("")
    lines.append(f"# Glossary {lang_a} ↔ {lang_b}")
    lines.append("")
    if include_meta:
        lines.append("## meta")
        lines.append("")
        lines.append("(typography rules)")
        lines.append("")
    for domain, rows in domain_to_rows.items():
        lines.append(f"## domain: {domain}")
        lines.append("")
        lines.append(f"| {lang_a} | {lang_b} | source | notes |")
        lines.append("|---|---|---|---|")
        for a_term, b_term in rows:
            lines.append(f"| {a_term} | {b_term} | test | — |")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


# -------------------- 1. direct hit --------------------

def test_lookup_direct_pair_hit(tmp_path):
    _write_pair_file(
        tmp_path / "glossary-ja-JP--zh-TW.md",
        "ja-JP", "zh-TW",
        {"general": [("図書館", "圖書館")]},
    )
    result = lookup(tmp_path, "ja-JP", "zh-TW", "図書館")
    assert result is not None
    assert result["target_term"] == "圖書館"
    assert result["audit_path"] == "direct"


# -------------------- 2. EN-pivot fallback --------------------

def test_lookup_via_en_pivot(tmp_path):
    _write_pair_file(
        tmp_path / "glossary-en-US--ja-JP.md",
        "en-US", "ja-JP",
        {"ui": [("Cancel", "キャンセル")]},
    )
    _write_pair_file(
        tmp_path / "glossary-en-US--zh-TW.md",
        "en-US", "zh-TW",
        {"ui": [("Cancel", "取消")]},
    )
    # Note: deliberately NO direct ja-JP--zh-TW.md
    result = lookup(tmp_path, "ja-JP", "zh-TW", "キャンセル")
    assert result is not None
    assert result["target_term"] == "取消"
    assert result["audit_path"] == "pivot.en-US (via 'Cancel')"


def test_lookup_via_en_pivot_when_direct_file_exists_but_misses(tmp_path):
    """Direct pair file exists but doesn't contain term → fall back to pivot."""
    _write_pair_file(
        tmp_path / "glossary-ja-JP--zh-TW.md",
        "ja-JP", "zh-TW",
        {"general": [("図書館", "圖書館")]},  # different term
    )
    _write_pair_file(
        tmp_path / "glossary-en-US--ja-JP.md",
        "en-US", "ja-JP",
        {"ui": [("Cancel", "キャンセル")]},
    )
    _write_pair_file(
        tmp_path / "glossary-en-US--zh-TW.md",
        "en-US", "zh-TW",
        {"ui": [("Cancel", "取消")]},
    )
    result = lookup(tmp_path, "ja-JP", "zh-TW", "キャンセル")
    assert result is not None
    assert result["target_term"] == "取消"
    assert result["audit_path"] == "pivot.en-US (via 'Cancel')"


# -------------------- 3. miss --------------------

def test_lookup_misses(tmp_path):
    # Empty glossary dir
    result = lookup(tmp_path, "ja-JP", "zh-TW", "存在しない単語")
    assert result is None


def test_lookup_misses_term_not_in_files(tmp_path):
    _write_pair_file(
        tmp_path / "glossary-ja-JP--zh-TW.md",
        "ja-JP", "zh-TW",
        {"general": [("図書館", "圖書館")]},
    )
    result = lookup(tmp_path, "ja-JP", "zh-TW", "未掲載")
    assert result is None


# -------------------- 4. domain filter --------------------

def test_lookup_with_domain_filter(tmp_path):
    _write_pair_file(
        tmp_path / "glossary-ja-JP--zh-TW.md",
        "ja-JP", "zh-TW",
        {
            "general": [("ボタン", "按鈕(general)")],
            "ui":      [("ボタン", "按鈕(ui)")],
        },
    )
    # No filter → any match (deterministic by section order — general first).
    result_any = lookup(tmp_path, "ja-JP", "zh-TW", "ボタン")
    assert result_any is not None
    assert result_any["target_term"] in {"按鈕(general)", "按鈕(ui)"}

    # Domain-filtered → only the ui entry.
    result_ui = lookup(tmp_path, "ja-JP", "zh-TW", "ボタン", domain="ui")
    assert result_ui is not None
    assert result_ui["target_term"] == "按鈕(ui)"

    # Filter on a domain not present → None (no fallback to other domains).
    result_missing = lookup(
        tmp_path, "ja-JP", "zh-TW", "ボタン", domain="tech.crypto"
    )
    assert result_missing is None


# -------------------- 5. filename alphabetical --------------------

def test_lookup_pair_filename_alphabetical(tmp_path):
    """Pair filename must be sorted alphabetically: glossary-ja-JP--zh-TW.md."""
    # Write the alphabetical filename.
    _write_pair_file(
        tmp_path / "glossary-ja-JP--zh-TW.md",
        "ja-JP", "zh-TW",
        {"general": [("図書館", "圖書館")]},
    )
    # Lookup with reversed source/target args still finds the file.
    result = lookup(tmp_path, "zh-TW", "ja-JP", "圖書館")
    assert result is not None
    assert result["target_term"] == "図書館"
    assert result["audit_path"] == "direct"

    # And the WRONG-order filename is NOT consulted: write only the wrong-order
    # name with a contradictory mapping; lookup must NOT see it.
    wrong_name = tmp_path / "glossary-zh-TW--ja-JP.md"
    _write_pair_file(
        wrong_name, "zh-TW", "ja-JP",
        {"general": [("圖書館_wrong", "図書館_wrong")]},
    )
    # Term "圖書館_wrong" lives only in wrong-order file; lookup should miss.
    result_wrong = lookup(tmp_path, "ja-JP", "zh-TW", "図書館_wrong")
    assert result_wrong is None


# -------------------- 6. reverse direction via direct --------------------

def test_lookup_reverse_direction_via_direct(tmp_path):
    """Pair file [en-US, ja-JP] supports lookup in either direction."""
    _write_pair_file(
        tmp_path / "glossary-en-US--ja-JP.md",
        "en-US", "ja-JP",
        {"ui": [("Cancel", "キャンセル")]},
    )
    # Forward: en→ja
    fwd = lookup(tmp_path, "en-US", "ja-JP", "Cancel")
    assert fwd is not None
    assert fwd["target_term"] == "キャンセル"
    assert fwd["audit_path"] == "direct"

    # Reverse: ja→en
    rev = lookup(tmp_path, "ja-JP", "en-US", "キャンセル")
    assert rev is not None
    assert rev["target_term"] == "Cancel"
    assert rev["audit_path"] == "direct"


# -------------------- 7. meta section handling --------------------

def test_parse_pair_file_handles_meta_section(tmp_path):
    """A `## meta` section must NOT be treated as a domain; parser must not crash."""
    p = tmp_path / "glossary-en-US--ja-JP.md"
    _write_pair_file(
        p, "en-US", "ja-JP",
        {"general": [("hello", "こんにちは")]},
        include_meta=True,
    )
    parsed = parse_pair_file(p)
    # _meta key carries pair lang order
    assert "_meta" in parsed
    assert parsed["_meta"]["pair"] == ["en-US", "ja-JP"]
    # Domain present
    assert "general" in parsed
    # `meta` is NOT a domain
    assert "meta" not in parsed
    # Entry parsed
    assert any(
        e["lang_a_term"] == "hello" and e["lang_b_term"] == "こんにちは"
        for e in parsed["general"]
    )


# -------------------- 8. real canonical files --------------------

def test_parse_pair_file_real_canonical_files():
    pair_files = sorted(CANONICAL_DIR.glob("glossary-*--*.md"))
    assert len(pair_files) == 5, (
        f"expected 5 canonical pair files, got {len(pair_files)}: "
        f"{[p.name for p in pair_files]}"
    )
    for pf in pair_files:
        parsed = parse_pair_file(pf)
        assert "_meta" in parsed, f"{pf.name}: missing _meta"
        assert isinstance(parsed["_meta"]["pair"], list), (
            f"{pf.name}: _meta.pair not a list"
        )
        assert len(parsed["_meta"]["pair"]) == 2, (
            f"{pf.name}: _meta.pair must have exactly 2 elements"
        )
        # At least 1 domain with at least 1 entry.
        domain_keys = [k for k in parsed.keys() if k != "_meta"]
        assert len(domain_keys) >= 1, f"{pf.name}: no domain sections"
        total_entries = sum(len(parsed[d]) for d in domain_keys)
        assert total_entries >= 1, f"{pf.name}: no entries across any domain"


# -------------------- file-not-found semantics --------------------

def test_lookup_returns_none_when_pair_file_missing(tmp_path):
    """File not found is a miss, not an exception."""
    # tmp_path is empty — no files at all
    assert lookup(tmp_path, "en-US", "ja-JP", "Cancel") is None


# -------------------- malformed frontmatter --------------------

def test_parse_pair_file_raises_on_malformed_frontmatter(tmp_path):
    """Missing/garbled frontmatter must raise ValueError, not silently parse."""
    bad = tmp_path / "glossary-en-US--ja-JP.md"
    bad.write_text(textwrap.dedent("""
        # No frontmatter at all
        ## domain: general
        | en-US | ja-JP | source | notes |
        |---|---|---|---|
        | hi | こん | test | — |
    """).strip(), encoding="utf-8")
    with pytest.raises(ValueError):
        parse_pair_file(bad)
