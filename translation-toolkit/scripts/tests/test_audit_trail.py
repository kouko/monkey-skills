"""Tests for scripts/lib/audit_trail.py — AuditTrailBuilder.

Covers Task C5 of translation-toolkit v0.1.0 plan (lines 1424-1512).
Spec: ``scripts/canonical/audit-trail-spec.md``.
"""
from __future__ import annotations

import sys
from pathlib import Path

# tests/ -> scripts/ -> translation-toolkit/ -> repo root
SCRIPTS_DIR = Path(__file__).resolve().parent.parent

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.audit_trail import AuditTrailBuilder  # noqa: E402


# --------------------------------------------------------------------------- #
# full record                                                                  #
# --------------------------------------------------------------------------- #


def test_audit_trail_full_record():
    """Audit trail JSON contains all spec fields with correct shape."""
    builder = AuditTrailBuilder()
    builder.set_intake(
        mode="faithful", register="neutral", strategy="domestication",
        source_locale="en-US", target_locale="ja-JP", domain="ui",
        intent="UI strings for Settings screen",
        inferred={"mode": False, "register": True},
    )
    builder.add_glossary_resolution(
        term="Cancel", tier="L2", source="pontoon",
        value="キャンセル", audit_path="direct",
    )
    builder.add_chunk(
        index=0, draft="...", reflect={"accuracy": []}, improve="キャンセル",
    )
    builder.add_gate_verdict("M1", "PASS", None)
    builder.add_gate_verdict("M2", "PASS", None)
    out = builder.build()
    assert out["intake"]["mode"] == "faithful"
    assert out["intake"]["inferred"]["register"] is True
    assert out["glossary_resolution"][0]["audit_path"] == "direct"
    assert out["gate_verdicts"]["M1"]["verdict"] == "PASS"
    assert out["version"] == "0.1.0"
    assert "timestamp" in out


# --------------------------------------------------------------------------- #
# unicode-safe serialization                                                   #
# --------------------------------------------------------------------------- #


def test_audit_trail_to_json_unicode_safe():
    """to_json() serializes Japanese/Chinese characters without escaping."""
    builder = AuditTrailBuilder()
    builder.set_intake(
        mode="faithful", register="neutral", strategy="domestication",
        source_locale="en-US", target_locale="ja-JP", domain="ui",
    )
    builder.add_chunk(
        index=0, draft="Cancel", reflect={"accuracy": []}, improve="キャンセル",
    )
    json_str = builder.to_json()
    assert "キャンセル" in json_str  # unescaped
    # If JA chars were ASCII-escaped, "キ" (U+30AD) would render as "キ".
    assert "\\u30ad" not in json_str.lower()


# --------------------------------------------------------------------------- #
# sources-used dedup                                                           #
# --------------------------------------------------------------------------- #


def test_audit_trail_dedup_sources_used():
    """add_source_used deduplicates within a category."""
    builder = AuditTrailBuilder()
    builder.add_source_used("glossary", "pontoon")
    builder.add_source_used("glossary", "pontoon")
    builder.add_source_used("glossary", "gnome")
    builder.add_source_used("websearch", "wikipedia.org")
    out = builder.build()
    assert out["sources_used"]["glossary"] == ["pontoon", "gnome"]
    assert out["sources_used"]["websearch"] == ["wikipedia.org"]


# --------------------------------------------------------------------------- #
# chunk ordering                                                               #
# --------------------------------------------------------------------------- #


def test_audit_trail_multiple_chunks_preserve_order():
    """Chunks preserve insertion order."""
    builder = AuditTrailBuilder()
    for i in range(3):
        builder.add_chunk(index=i, draft=f"d{i}", reflect={}, improve=f"i{i}")
    out = builder.build()
    assert [c["index"] for c in out["chunks"]] == [0, 1, 2]


# --------------------------------------------------------------------------- #
# warnings                                                                     #
# --------------------------------------------------------------------------- #


def test_audit_trail_warnings():
    builder = AuditTrailBuilder()
    builder.add_warning("Glossary tier L2 missed for 5 terms")
    builder.add_warning("Web search rate-limited; 3 fallbacks to LLM")
    out = builder.build()
    assert len(out["warnings"]) == 2


# --------------------------------------------------------------------------- #
# empty builder skeleton                                                       #
# --------------------------------------------------------------------------- #


def test_audit_trail_empty_builder_has_default_shape():
    """A bare AuditTrailBuilder still produces a valid skeleton with all top-level keys."""
    out = AuditTrailBuilder().build()
    expected_keys = {
        "version", "timestamp", "intake", "glossary_resolution",
        "chunks", "gate_verdicts", "untranslatables", "sources_used", "warnings",
    }
    assert set(out.keys()) == expected_keys
    assert out["intake"] == {}
    assert out["chunks"] == []


# --------------------------------------------------------------------------- #
# gate verdict with details                                                    #
# --------------------------------------------------------------------------- #


def test_audit_trail_gate_verdict_with_details():
    """add_gate_verdict propagates diff + details to the JSON."""
    builder = AuditTrailBuilder()
    builder.add_gate_verdict(
        "M1", "FAIL", "missing: ['⟦P:02⟧']", {"missing": ["⟦P:02⟧"]},
    )
    out = builder.build()
    assert out["gate_verdicts"]["M1"]["verdict"] == "FAIL"
    assert out["gate_verdicts"]["M1"]["details"]["missing"] == ["⟦P:02⟧"]


# --------------------------------------------------------------------------- #
# inferred_value capture (auto-inference vs user override)                     #
# --------------------------------------------------------------------------- #


def test_audit_trail_inferred_value_records_under_intake():
    builder = AuditTrailBuilder()
    builder.set_intake(
        mode="faithful", register="neutral", strategy="domestication",
        source_locale="en-US", target_locale="ja-JP", domain="ui",
    )
    builder.add_inferred_value("register", "neutral")
    out = builder.build()
    assert out["intake"]["inferred_values"]["register"] == "neutral"


# --------------------------------------------------------------------------- #
# chunk optional source                                                        #
# --------------------------------------------------------------------------- #


def test_audit_trail_chunk_optional_source():
    builder = AuditTrailBuilder()
    builder.add_chunk(index=0, draft="d", reflect={}, improve="i", source="orig")
    out = builder.build()
    assert out["chunks"][0]["source"] == "orig"


# --------------------------------------------------------------------------- #
# untranslatable target_rendering                                              #
# --------------------------------------------------------------------------- #


def test_audit_trail_untranslatable_target_rendering():
    builder = AuditTrailBuilder()
    builder.add_untranslatable(
        source_phrase="御朱印", decision="borrow",
        alternatives=["temple stamp"],
        target_rendering="御朱印 (a temple stamp)",
    )
    out = builder.build()
    assert out["untranslatables"][0]["target_rendering"] == "御朱印 (a temple stamp)"
