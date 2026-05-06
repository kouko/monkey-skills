"""Test verify-drift.py detects byte differences between canonical and functional copies."""
import shutil
import subprocess
from pathlib import Path

DISTRIBUTE_SCRIPT = Path(__file__).resolve().parent.parent / "distribute.py"
VERIFY_SCRIPT = Path(__file__).resolve().parent.parent / "verify-drift.py"


def test_verify_drift_reports_ok_after_distribute(tmp_path):
    plugin_root = tmp_path / "translation-toolkit"
    canonical = plugin_root / "scripts" / "canonical"
    canonical.mkdir(parents=True)
    (canonical / "core-loop.md").write_text("# core")
    (canonical / "glossary-en-US--ja-JP.md").write_text("# glossary")
    for skill in ["translation-i18n", "translation-doc", "translation-creative", "translation-audit"]:
        (plugin_root / skill).mkdir(parents=True)

    shutil.copy(DISTRIBUTE_SCRIPT, plugin_root / "scripts" / "distribute.py")
    shutil.copy(VERIFY_SCRIPT, plugin_root / "scripts" / "verify-drift.py")

    subprocess.run(["python3", "scripts/distribute.py"], cwd=plugin_root, check=True)
    result = subprocess.run(
        ["python3", "scripts/verify-drift.py"], cwd=plugin_root, capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "OK" in result.stdout


def test_verify_drift_detects_modified_functional_copy(tmp_path):
    plugin_root = tmp_path / "translation-toolkit"
    canonical = plugin_root / "scripts" / "canonical"
    canonical.mkdir(parents=True)
    (canonical / "core-loop.md").write_text("# core canonical")
    for skill in ["translation-i18n", "translation-doc", "translation-creative", "translation-audit"]:
        (plugin_root / skill).mkdir(parents=True)

    shutil.copy(DISTRIBUTE_SCRIPT, plugin_root / "scripts" / "distribute.py")
    shutil.copy(VERIFY_SCRIPT, plugin_root / "scripts" / "verify-drift.py")

    subprocess.run(["python3", "scripts/distribute.py"], cwd=plugin_root, check=True)

    # Modify one functional copy
    drifted = plugin_root / "translation-i18n" / "references" / "core-loop.md"
    drifted.write_text("# core MODIFIED")

    result = subprocess.run(
        ["python3", "scripts/verify-drift.py"], cwd=plugin_root, capture_output=True, text=True
    )
    assert result.returncode == 1
    assert "DRIFT" in result.stdout
