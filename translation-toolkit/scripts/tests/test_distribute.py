"""Test distribute.py byte-copies canonical/* to each skill's correct subfolder."""
import shutil
import subprocess
from pathlib import Path

REPO_SCRIPT = Path(__file__).resolve().parent.parent / "distribute.py"


def test_distribute_routes_files_to_correct_subfolders(tmp_path):
    plugin_root = tmp_path / "translation-toolkit"
    canonical = plugin_root / "scripts" / "canonical"
    canonical.mkdir(parents=True)
    (canonical / "core-loop.md").write_text("# core loop")
    (canonical / "glossary-en-US--ja-JP.md").write_text("# glossary")
    (canonical / "jlreq-summary.md").write_text("# jlreq")
    (canonical / "nict-en-ja-zh.md").write_text("# nict")
    (canonical / "manual-entries-ja-JP--zh-TW.md").write_text("# manual")  # NOT distributed

    for skill in ["translation-i18n", "translation-doc", "translation-creative", "translation-audit"]:
        (plugin_root / skill).mkdir(parents=True)

    shutil.copy(REPO_SCRIPT, plugin_root / "scripts" / "distribute.py")

    result = subprocess.run(
        ["python3", "scripts/distribute.py"], cwd=plugin_root, capture_output=True, text=True
    )
    assert result.returncode == 0, f"stdout={result.stdout!r} stderr={result.stderr!r}"

    for skill in ["translation-i18n", "translation-doc", "translation-creative", "translation-audit"]:
        assert (plugin_root / skill / "references" / "core-loop.md").read_text() == "# core loop"
        assert (plugin_root / skill / "glossary" / "glossary-en-US--ja-JP.md").read_text() == "# glossary"
        assert (plugin_root / skill / "typography" / "jlreq-summary.md").read_text() == "# jlreq"
        assert (plugin_root / skill / "corpus" / "nict-en-ja-zh.md").read_text() == "# nict"
        # manual-entries should NOT be distributed
        for sub in ["references", "glossary", "typography", "corpus"]:
            assert not (plugin_root / skill / sub / "manual-entries-ja-JP--zh-TW.md").exists()


def test_distribute_unrouted_warns(tmp_path, capsys):
    plugin_root = tmp_path / "translation-toolkit"
    canonical = plugin_root / "scripts" / "canonical"
    canonical.mkdir(parents=True)
    (canonical / "unknown.md").write_text("# unknown")
    for skill in ["translation-i18n", "translation-doc", "translation-creative", "translation-audit"]:
        (plugin_root / skill).mkdir(parents=True)
    shutil.copy(REPO_SCRIPT, plugin_root / "scripts" / "distribute.py")
    result = subprocess.run(
        ["python3", "scripts/distribute.py"], cwd=plugin_root, capture_output=True, text=True
    )
    assert "WARN" in result.stdout
    assert "unknown.md" in result.stdout
