"""Test Pontoon / GNOME / JLT / NAER / e-Stat / Tokyo / Cabinet ingest -> glossary-en-US--{tgt}.md emit."""
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


def test_naer_csv_dispatches_to_mapped_domains(tmp_path):
    """NAER entries land in the right domain per NAER_CATEGORY_TO_DOMAIN."""
    csv_fixture = tmp_path / "naer.csv"
    csv_fixture.write_text(textwrap.dedent('''\
        英文名稱,中文名稱,學術領域
        algorithm,演算法,電子計算機名詞
        sample,樣本,統計學名詞
        plaintiff,原告,法律名詞
        hypertension,高血壓,醫學名詞
        inflation,通貨膨脹,經濟學名詞
        Aachen,亞琛,外國地名譯名
    '''))
    out_dir = tmp_path / "canonical"
    out_dir.mkdir()
    result = subprocess.run(
        ["python3", str(SCRIPT),
         "--target", "zh-TW",
         "--naer-csv", str(csv_fixture),
         "--out-dir", str(out_dir)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr={result.stderr}"
    content = (out_dir / "glossary-en-US--zh-TW.md").read_text()
    # Domain mappings exercised
    assert "## domain: tech.software" in content
    assert "| algorithm | 演算法 | naer" in content
    assert "## domain: statistics" in content
    assert "| sample | 樣本 | naer" in content
    assert "## domain: legal" in content
    assert "| plaintiff | 原告 | naer" in content
    assert "## domain: medical" in content
    assert "| hypertension | 高血壓 | naer" in content
    assert "## domain: finance" in content
    assert "| inflation | 通貨膨脹 | naer" in content
    # Unknown category -> general
    assert "## domain: general" in content
    assert "| Aachen | 亞琛 | naer" in content


def test_naer_csv_alternate_column_names(tmp_path):
    """NAER parser tolerates alternate header names (en_term/zh_TW_term/category)."""
    csv_fixture = tmp_path / "naer.csv"
    csv_fixture.write_text(textwrap.dedent('''\
        en_term,zh_TW_term,category
        recursion,遞迴,電子計算機名詞
        contract,契約,法律名詞
    '''))
    out_dir = tmp_path / "canonical"
    out_dir.mkdir()
    result = subprocess.run(
        ["python3", str(SCRIPT),
         "--target", "zh-TW",
         "--naer-csv", str(csv_fixture),
         "--out-dir", str(out_dir)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr={result.stderr}"
    content = (out_dir / "glossary-en-US--zh-TW.md").read_text()
    assert "| recursion | 遞迴 | naer" in content
    assert "| contract | 契約 | naer" in content


def test_estat_csv_all_in_statistics_domain(tmp_path):
    """e-Stat entries land in domain: statistics."""
    csv_fixture = tmp_path / "estat.csv"
    csv_fixture.write_text(textwrap.dedent('''\
        English,Japanese
        sample,標本
        standard deviation,標準偏差
        confidence interval,信頼区間
    '''))
    out_dir = tmp_path / "canonical"
    out_dir.mkdir()
    result = subprocess.run(
        ["python3", str(SCRIPT),
         "--target", "ja-JP",
         "--estat-csv", str(csv_fixture),
         "--out-dir", str(out_dir)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr={result.stderr}"
    content = (out_dir / "glossary-en-US--ja-JP.md").read_text()
    assert "## domain: statistics" in content
    assert "| sample | 標本 | e-stat" in content
    assert "| standard deviation | 標準偏差 | e-stat" in content
    assert "| confidence interval | 信頼区間 | e-stat" in content


def test_estat_csv_handles_utf8_bom(tmp_path):
    """e-Stat parser strips UTF-8 BOM via utf-8-sig."""
    csv_fixture = tmp_path / "estat.csv"
    # Write with explicit BOM
    csv_fixture.write_bytes(
        "﻿English,Japanese\nvariance,分散\n".encode("utf-8")
    )
    out_dir = tmp_path / "canonical"
    out_dir.mkdir()
    result = subprocess.run(
        ["python3", str(SCRIPT),
         "--target", "ja-JP",
         "--estat-csv", str(csv_fixture),
         "--out-dir", str(out_dir)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr={result.stderr}"
    content = (out_dir / "glossary-en-US--ja-JP.md").read_text()
    assert "| variance | 分散 | e-stat" in content


def test_tokyo_csv_dispatches_to_mapped_domains(tmp_path):
    """Tokyo entries land in gov when category is 行政/福祉, else general."""
    csv_fixture = tmp_path / "tokyo.csv"
    csv_fixture.write_text(textwrap.dedent('''\
        English,Japanese,カテゴリ
        ward office,区役所,行政
        nursing care,介護,福祉
        evacuation site,避難場所,防災
        hot spring,温泉,観光
        garbage collection,ゴミ収集,生活
    '''))
    out_dir = tmp_path / "canonical"
    out_dir.mkdir()
    result = subprocess.run(
        ["python3", str(SCRIPT),
         "--target", "ja-JP",
         "--tokyo-csv", str(csv_fixture),
         "--out-dir", str(out_dir)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr={result.stderr}"
    content = (out_dir / "glossary-en-US--ja-JP.md").read_text()
    # gov domain: 行政 + 福祉
    assert "## domain: gov" in content
    assert "| ward office | 区役所 | tokyo" in content
    assert "| nursing care | 介護 | tokyo" in content
    # general domain: 防災 + 観光 + 生活
    assert "## domain: general" in content
    assert "| evacuation site | 避難場所 | tokyo" in content
    assert "| hot spring | 温泉 | tokyo" in content
    assert "| garbage collection | ゴミ収集 | tokyo" in content


def test_cabinet_csv_all_in_gov_domain(tmp_path):
    """Cabinet entries land uniformly in domain: gov."""
    csv_fixture = tmp_path / "cabinet.csv"
    csv_fixture.write_text(textwrap.dedent('''\
        Japanese,English
        内閣総理大臣,Prime Minister
        外務省,Ministry of Foreign Affairs
        内閣官房,Cabinet Secretariat
    '''))
    out_dir = tmp_path / "canonical"
    out_dir.mkdir()
    result = subprocess.run(
        ["python3", str(SCRIPT),
         "--target", "ja-JP",
         "--cabinet-csv", str(csv_fixture),
         "--out-dir", str(out_dir)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr={result.stderr}"
    content = (out_dir / "glossary-en-US--ja-JP.md").read_text()
    assert "## domain: gov" in content
    assert "| Prime Minister | 内閣総理大臣 | cabinet" in content
    assert "| Ministry of Foreign Affairs | 外務省 | cabinet" in content
    assert "| Cabinet Secretariat | 内閣官房 | cabinet" in content


def test_cabinet_csv_handles_utf8_bom(tmp_path):
    """Cabinet parser strips UTF-8 BOM via utf-8-sig."""
    csv_fixture = tmp_path / "cabinet.csv"
    csv_fixture.write_bytes(
        "﻿Japanese,English\n法務省,Ministry of Justice\n".encode("utf-8")
    )
    out_dir = tmp_path / "canonical"
    out_dir.mkdir()
    result = subprocess.run(
        ["python3", str(SCRIPT),
         "--target", "ja-JP",
         "--cabinet-csv", str(csv_fixture),
         "--out-dir", str(out_dir)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr={result.stderr}"
    content = (out_dir / "glossary-en-US--ja-JP.md").read_text()
    assert "| Ministry of Justice | 法務省 | cabinet" in content


def test_naer_real_sample_zh_tw(tmp_path):
    """Real bundled NAER sample produces multiple domain sections."""
    real_csv = REPO_ROOT / "translation-toolkit/vendor/naer/academic-terms-zh-TW.csv"
    if not real_csv.exists():
        import pytest
        pytest.skip("Real NAER sample CSV not yet present")

    out_dir = tmp_path / "canonical"
    out_dir.mkdir()
    result = subprocess.run(
        ["python3", str(SCRIPT),
         "--target", "zh-TW",
         "--naer-csv", str(real_csv),
         "--out-dir", str(out_dir)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr={result.stderr}"
    content = (out_dir / "glossary-en-US--zh-TW.md").read_text()
    assert "## domain: tech.software" in content
    assert "## domain: statistics" in content
    assert "## domain: legal" in content
    assert "## domain: medical" in content
    assert "## domain: finance" in content
    assert "naer" in content


def test_estat_real_sample_ja_jp(tmp_path):
    """Real bundled e-Stat sample produces statistics section."""
    real_csv = REPO_ROOT / "translation-toolkit/vendor/e-stat/stat-terms-en-ja.csv"
    if not real_csv.exists():
        import pytest
        pytest.skip("Real e-Stat sample CSV not yet present")
    out_dir = tmp_path / "canonical"
    out_dir.mkdir()
    result = subprocess.run(
        ["python3", str(SCRIPT),
         "--target", "ja-JP",
         "--estat-csv", str(real_csv),
         "--out-dir", str(out_dir)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr={result.stderr}"
    content = (out_dir / "glossary-en-US--ja-JP.md").read_text()
    assert "## domain: statistics" in content
    assert "e-stat" in content


def test_tokyo_real_sample_ja_jp(tmp_path):
    """Real bundled Tokyo sample produces gov + general sections."""
    real_csv = REPO_ROOT / "translation-toolkit/vendor/tokyo/en-ja-translation.csv"
    if not real_csv.exists():
        import pytest
        pytest.skip("Real Tokyo sample CSV not yet present")
    out_dir = tmp_path / "canonical"
    out_dir.mkdir()
    result = subprocess.run(
        ["python3", str(SCRIPT),
         "--target", "ja-JP",
         "--tokyo-csv", str(real_csv),
         "--out-dir", str(out_dir)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr={result.stderr}"
    content = (out_dir / "glossary-en-US--ja-JP.md").read_text()
    assert "## domain: gov" in content
    assert "## domain: general" in content
    assert "tokyo" in content


def test_cabinet_real_sample_ja_jp(tmp_path):
    """Real bundled Cabinet CSV produces a large gov section."""
    real_csv = REPO_ROOT / "translation-toolkit/vendor/cabinet/gov-orgs-en-ja.csv"
    if not real_csv.exists():
        import pytest
        pytest.skip("Real Cabinet CSV not yet present")
    out_dir = tmp_path / "canonical"
    out_dir.mkdir()
    result = subprocess.run(
        ["python3", str(SCRIPT),
         "--target", "ja-JP",
         "--cabinet-csv", str(real_csv),
         "--out-dir", str(out_dir)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr={result.stderr}"
    content = (out_dir / "glossary-en-US--ja-JP.md").read_text()
    assert "## domain: gov" in content
    assert "cabinet" in content
    table_rows = [l for l in content.splitlines()
                  if l.startswith("| ") and "| en-US " not in l and not l.startswith("|--")]
    # Cabinet ships ~3000 entries
    assert len(table_rows) >= 1000, f"expected >=1000 entries, got {len(table_rows)}"


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
