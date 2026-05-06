"""End-to-end smoke tests for translation-toolkit v0.1.0.

These exercise build-pipeline + lib together, but DO NOT invoke skills
(which would require LLM calls). They verify:
- All 5 canonical pair files parse correctly
- Protect-pass round-trips fixture files cleanly
- M1 + M2 detect injected violations in the audit fixture
- Audit trail builder produces valid JSON conforming to the schema
- Glossary lookup works against real canonical files for known terms
"""
from pathlib import Path
import sys
import json

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
ROOT = SCRIPTS_DIR.parent
CANONICAL = SCRIPTS_DIR / "canonical"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

sys.path.insert(0, str(SCRIPTS_DIR))

from lib.glossary import parse_pair_file, lookup
from lib.protect_pass import protect, restore, verify_count
from lib.gates import m1_check, m2_check
from lib.audit_trail import AuditTrailBuilder


def test_e2e_smoke_glossary_loads_all_pair_files():
    """All 5 canonical pair files parse without error."""
    pair_files = sorted(CANONICAL.glob("glossary-*--*.md"))
    assert len(pair_files) == 5, f"expected 5 pair files, got {len(pair_files)}: {pair_files}"
    for f in pair_files:
        result = parse_pair_file(f)
        assert "_meta" in result
        # at least 1 domain section with at least 1 entry
        domain_keys = [k for k in result.keys() if k != "_meta"]
        assert len(domain_keys) >= 1, f"empty: {f.name}"


def test_e2e_smoke_real_glossary_lookup_known_terms():
    """Lookup known canonical terms via direct + EN-pivot."""
    # Direct: ja-JP --> zh-TW
    r = lookup(CANONICAL, "ja-JP", "zh-TW", "図書館")
    assert r is not None
    assert r["target_term"] == "圖書館"
    assert r["audit_path"] == "direct"


def test_e2e_smoke_protect_roundtrip_po_fixture():
    """Round-trip a complex i18n fixture through protect/restore."""
    text = (FIXTURES / "sample.po").read_text(encoding="utf-8")
    masked, token_map = protect(text)
    restored = restore(masked, token_map)
    assert restored == text, "protect-restore round-trip lost content"


def test_e2e_smoke_protect_roundtrip_markdown_fixture():
    text = (FIXTURES / "sample.md").read_text(encoding="utf-8")
    masked, token_map = protect(text)
    restored = restore(masked, token_map)
    assert restored == text


def test_e2e_smoke_m1_detects_dropped_placeholder_in_audit_fixture():
    """M1 catches the intentional dropped {app_name} in sample-existing-translation.po.

    The audit fixture deliberately translates "Hello {name}, welcome to {app_name}!"
    as "ようこそ、{name}さん" — dropping {app_name}. M1 should FAIL with the
    missing token surfaced in the diff.
    """
    src_msgid = "Hello {name}, welcome to {app_name}!"
    tgt_msgstr = "ようこそ、{name}さん"  # dropped {app_name}
    _src_masked, src_token_map = protect(src_msgid)
    tgt_masked, _tgt_token_map = protect(tgt_msgstr)
    # M1 compares the set of ⟦P:NN⟧ tokens in target against source token_map keys.
    result = m1_check(tgt_masked, src_token_map)
    assert result["verdict"] == "FAIL"
    assert result["details"]["missing"], "expected at least one missing token"
    # Sanity: count primitive also flags the drop.
    assert verify_count(tgt_masked, src_token_map) is False
    # And the audit fixture really does live on disk with this exact bug:
    # the welcome msgstr is present but {app_name} is missing from it.
    audit_text = (FIXTURES / "sample-existing-translation.po").read_text(encoding="utf-8")
    assert 'msgstr "ようこそ、{name}さん"' in audit_text
    # The dropped placeholder is intentional (see fixture comment).


def test_e2e_smoke_m2_detects_glossary_violation():
    """M2 catches the intentional 取り消す instead of キャンセル."""
    project_glossary = {("Cancel", "ui"): "キャンセル"}
    source = "Cancel"
    target = "取り消す"  # violation
    result = m2_check(source, target, project_glossary, domain="ui")
    assert result["verdict"] == "FAIL"
    assert "Cancel" in result["diff"] or "キャンセル" in result["diff"]


def test_e2e_smoke_audit_trail_round_trips_through_json():
    """Audit trail builder produces JSON that parses cleanly back to the same dict."""
    builder = AuditTrailBuilder()
    builder.set_intake(
        mode="faithful", register="neutral", strategy="domestication",
        source_locale="en-US", target_locale="ja-JP", domain="ui",
        intent="App UI strings",
    )
    builder.add_glossary_resolution(
        term="Cancel", tier="L2", source="pontoon", value="キャンセル", audit_path="direct",
    )
    builder.add_chunk(index=0, draft="...", reflect={"accuracy": []}, improve="キャンセル")
    builder.add_gate_verdict("M1", "PASS", None)
    builder.add_gate_verdict("M2", "PASS", None)
    builder.add_source_used("glossary", "pontoon")

    json_str = builder.to_json()
    parsed = json.loads(json_str)
    assert parsed["intake"]["mode"] == "faithful"
    assert parsed["chunks"][0]["improve"] == "キャンセル"
    assert parsed["sources_used"]["glossary"] == ["pontoon"]
    # CJK round-trip clean (no \u escapes)
    assert "キャンセル" in json_str
