"""Test Pontoon / GNOME / JLT ingest -> glossary-en-US--{tgt}.md emit."""
import subprocess
import textwrap
from pathlib import Path

REPO_ROOT = Path("/Users/kouko/GitHub/monkey-skills")
SCRIPT = REPO_ROOT / "translation-toolkit/scripts/build-pairs-from-en.py"


def test_pontoon_ja_tbx_to_pair_file(tmp_path):
    """Given a small fixture TBX, build script produces glossary-en-US--ja-JP.md."""
    fixture = tmp_path / "ja.v2.tbx"
    fixture.write_text(textwrap.dedent('''<?xml version="1.0" encoding="UTF-8"?>
        <martif type="TBX" xml:lang="en">
          <text><body>
            <termEntry id="t1">
              <langSet xml:lang="en"><tig><term>Cancel</term></tig></langSet>
              <langSet xml:lang="ja"><tig><term>キャンセル</term></tig></langSet>
            </termEntry>
            <termEntry id="t2">
              <langSet xml:lang="en"><tig><term>Settings</term></tig></langSet>
              <langSet xml:lang="ja"><tig><term>設定</term></tig></langSet>
            </termEntry>
          </body></text>
        </martif>
    '''))

    out_dir = tmp_path / "canonical"
    out_dir.mkdir()

    result = subprocess.run(
        ["python3", str(SCRIPT),
         "--target", "ja-JP",
         "--pontoon-tbx", str(fixture),
         "--out-dir", str(out_dir)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr={result.stderr}"

    out_file = out_dir / "glossary-en-US--ja-JP.md"
    assert out_file.exists()
    content = out_file.read_text()
    assert "pair: [en-US, ja-JP]" in content
    assert "## domain: ui" in content
    assert "| Cancel | キャンセル" in content
    assert "| Settings | 設定" in content


def test_pontoon_real_tbx_zh_tw(tmp_path):
    """Real Pontoon zh-TW TBX produces ~95 entries with frontmatter intact."""
    real_tbx = REPO_ROOT / "translation-toolkit/vendor/mozilla-pontoon/zh-TW.v2.tbx"
    if not real_tbx.exists():
        # Skip if vendor file not present (CI bootstrap)
        import pytest
        pytest.skip("Real Pontoon TBX not yet downloaded")

    out_dir = tmp_path / "canonical"
    out_dir.mkdir()

    result = subprocess.run(
        ["python3", str(SCRIPT),
         "--target", "zh-TW",
         "--pontoon-tbx", str(real_tbx),
         "--out-dir", str(out_dir)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr={result.stderr}"

    out_file = out_dir / "glossary-en-US--zh-TW.md"
    assert out_file.exists()
    content = out_file.read_text()
    assert "pair: [en-US, zh-TW]" in content
    assert "sources:" in content
    assert "domains_supported:" in content
    # Pontoon zh-TW has 97 entries; allow some slack for filtering
    table_rows = [l for l in content.splitlines()
                  if l.startswith("| ") and "| en-US " not in l and not l.startswith("|--")]
    assert len(table_rows) >= 80, f"expected >=80 entries, got {len(table_rows)}"


def test_gnome_po_parsed_to_ui_domain(tmp_path):
    """GNOME PO entries land in domain: ui."""
    po_fixture = tmp_path / "ja.po"
    po_fixture.write_text(textwrap.dedent('''\
        msgid ""
        msgstr ""
        "Content-Type: text/plain; charset=UTF-8\\n"

        msgid "Cancel"
        msgstr "キャンセル"

        msgid "File"
        msgstr "ファイル"
    '''))
    out_dir = tmp_path / "canonical"
    out_dir.mkdir()
    result = subprocess.run(
        ["python3", str(SCRIPT),
         "--target", "ja-JP",
         "--gnome-po", str(po_fixture),
         "--out-dir", str(out_dir)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr={result.stderr}"
    content = (out_dir / "glossary-en-US--ja-JP.md").read_text()
    assert "## domain: ui" in content
    assert "| File | ファイル | gnome" in content
    assert "| Cancel | キャンセル | gnome" in content


def test_jlt_csv_dispatches_to_legal_or_gov_domain(tmp_path):
    """JLT entries land in domain: gov when ja contains 省/庁/局/府, else legal."""
    csv_fixture = tmp_path / "jlt.csv"
    csv_fixture.write_text(textwrap.dedent('''\
        en_term,ja_term,source_law,notes
        Ministry of Justice,法務省,Establishment Act,
        agreement,契約,Civil Code Article 522,
        Cabinet Office,内閣府,Cabinet Office Establishment Act,
        Civil Code,民法,Civil Code,
    '''))
    out_dir = tmp_path / "canonical"
    out_dir.mkdir()
    result = subprocess.run(
        ["python3", str(SCRIPT),
         "--target", "ja-JP",
         "--jlt-csv", str(csv_fixture),
         "--out-dir", str(out_dir)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr={result.stderr}"
    content = (out_dir / "glossary-en-US--ja-JP.md").read_text()
    # gov domain: org names with 省/庁/局/府
    assert "## domain: gov" in content
    assert "| Ministry of Justice | 法務省" in content
    assert "| Cabinet Office | 内閣府" in content
    # legal domain: everything else
    assert "## domain: legal" in content
    assert "| agreement | 契約" in content
    assert "| Civil Code | 民法" in content


def test_jlt_csv_real_sample_ingest(tmp_path):
    """Real bundled JLT sample produces both gov and legal sections."""
    real_csv = REPO_ROOT / "translation-toolkit/vendor/jlt/standard-bilingual-dictionary.csv"
    if not real_csv.exists():
        import pytest
        pytest.skip("Real JLT sample CSV not yet present")

    out_dir = tmp_path / "canonical"
    out_dir.mkdir()

    result = subprocess.run(
        ["python3", str(SCRIPT),
         "--target", "ja-JP",
         "--jlt-csv", str(real_csv),
         "--out-dir", str(out_dir)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr={result.stderr}"
    content = (out_dir / "glossary-en-US--ja-JP.md").read_text()
    assert "## domain: gov" in content
    assert "## domain: legal" in content
    assert "jlt" in content


def test_gnome_po_real_file_ja(tmp_path):
    """Real GNOME ja.po produces a large `ui` domain section."""
    real_po = REPO_ROOT / "translation-toolkit/vendor/gnome-i18n/ja.po"
    if not real_po.exists():
        import pytest
        pytest.skip("Real GNOME ja.po not yet downloaded")

    out_dir = tmp_path / "canonical"
    out_dir.mkdir()

    result = subprocess.run(
        ["python3", str(SCRIPT),
         "--target", "ja-JP",
         "--gnome-po", str(real_po),
         "--out-dir", str(out_dir)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr={result.stderr}"
    content = (out_dir / "glossary-en-US--ja-JP.md").read_text()
    assert "## domain: ui" in content
    table_rows = [l for l in content.splitlines()
                  if l.startswith("| ") and "| en-US " not in l and not l.startswith("|--")]
    # GNOME ja.po has ~850 non-empty entries
    assert len(table_rows) >= 500, f"expected >=500 entries, got {len(table_rows)}"
