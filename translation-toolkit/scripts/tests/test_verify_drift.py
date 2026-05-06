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


def test_verify_drift_detects_modified_prompt_functional_copy(tmp_path):
    """Drift detection must follow the prompts/<name>.md -> prompt-<name>.md flattening."""
    plugin_root = tmp_path / "translation-toolkit"
    canonical = plugin_root / "scripts" / "canonical"
    prompts_dir = canonical / "prompts"
    prompts_dir.mkdir(parents=True)
    (prompts_dir / "draft.md").write_text("WRITER prompt v1")

    for skill in ["translation-i18n", "translation-doc", "translation-creative", "translation-audit"]:
        (plugin_root / skill).mkdir(parents=True)

    shutil.copy(DISTRIBUTE_SCRIPT, plugin_root / "scripts" / "distribute.py")
    shutil.copy(VERIFY_SCRIPT, plugin_root / "scripts" / "verify-drift.py")

    subprocess.run(["python3", "scripts/distribute.py"], cwd=plugin_root, check=True)

    # Sanity: clean state passes.
    ok = subprocess.run(
        ["python3", "scripts/verify-drift.py"], cwd=plugin_root, capture_output=True, text=True
    )
    assert ok.returncode == 0, ok.stdout

    # Now mutate one functional copy at the FLATTENED path.
    drifted = plugin_root / "translation-i18n" / "references" / "prompt-draft.md"
    assert drifted.exists(), "expected flattened prompt-draft.md to exist"
    drifted.write_text("WRITER prompt MUTATED")

    result = subprocess.run(
        ["python3", "scripts/verify-drift.py"], cwd=plugin_root, capture_output=True, text=True
    )
    assert result.returncode == 1
    assert "DRIFT" in result.stdout
    assert "prompt-draft.md" in result.stdout
    # And the canonical-side path in the message uses the canonical-relative path.
    assert "prompts/draft.md" in result.stdout
