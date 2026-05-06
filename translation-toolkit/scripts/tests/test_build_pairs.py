"""Test Pontoon TBX -> glossary-en-US--{tgt}.md emit."""
import subprocess
from pathlib import Path
import textwrap

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
