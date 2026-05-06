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
    # Unrouted files are warn-only (NOT a non-zero exit) — distribute.py is
    # informational; verify-drift.py is the strict CI gate. Lock the intent.
    assert result.returncode == 0
    assert "WARN" in result.stdout
    assert "unknown.md" in result.stdout


def test_distribute_flattens_prompts_to_references(tmp_path):
    """prompts/<name>.md must land at <skill>/references/prompt-<name>.md (flattened)."""
    plugin_root = tmp_path / "translation-toolkit"
    canonical = plugin_root / "scripts" / "canonical"
    prompts_dir = canonical / "prompts"
    prompts_dir.mkdir(parents=True)
    (prompts_dir / "draft.md").write_text("WRITER prompt body")
    (prompts_dir / "reflect-4d.md").write_text("CRITIC 4D body")
    (prompts_dir / "reflect-5d.md").write_text("CRITIC 5D body")
    (prompts_dir / "improve.md").write_text("REVISER body")

    for skill in ["translation-i18n", "translation-doc", "translation-creative", "translation-audit"]:
        (plugin_root / skill).mkdir(parents=True)

    shutil.copy(REPO_SCRIPT, plugin_root / "scripts" / "distribute.py")

    result = subprocess.run(
        ["python3", "scripts/distribute.py"], cwd=plugin_root, capture_output=True, text=True
    )
    assert result.returncode == 0, f"stdout={result.stdout!r} stderr={result.stderr!r}"

    for skill in ["translation-i18n", "translation-doc", "translation-creative", "translation-audit"]:
        refs = plugin_root / skill / "references"
        # Flattened: prompt-<name>.md, NOT prompts/<name>.md
        assert (refs / "prompt-draft.md").read_text() == "WRITER prompt body"
        assert (refs / "prompt-reflect-4d.md").read_text() == "CRITIC 4D body"
        assert (refs / "prompt-reflect-5d.md").read_text() == "CRITIC 5D body"
        assert (refs / "prompt-improve.md").read_text() == "REVISER body"
        # No nested prompts/ subfolder may appear under any skill subfolder.
        assert not (refs / "prompts").exists()
        assert not (plugin_root / skill / "prompts").exists()


def test_distribute_excludes_prompts_from_other_routings(tmp_path):
    """prompts/foo.md must NOT be misrouted to typography/, corpus/, or glossary/."""
    plugin_root = tmp_path / "translation-toolkit"
    canonical = plugin_root / "scripts" / "canonical"
    prompts_dir = canonical / "prompts"
    prompts_dir.mkdir(parents=True)
    (prompts_dir / "draft.md").write_text("WRITER")

    for skill in ["translation-i18n", "translation-doc", "translation-creative", "translation-audit"]:
        (plugin_root / skill).mkdir(parents=True)

    shutil.copy(REPO_SCRIPT, plugin_root / "scripts" / "distribute.py")
    subprocess.run(["python3", "scripts/distribute.py"], cwd=plugin_root, check=True)

    for skill in ["translation-i18n", "translation-doc", "translation-creative", "translation-audit"]:
        # The flattened file lives only under references/.
        assert (plugin_root / skill / "references" / "prompt-draft.md").exists()
        # Must not leak into other top-level subfolders.
        for sub in ["typography", "corpus", "glossary"]:
            assert not (plugin_root / skill / sub / "prompt-draft.md").exists()
            assert not (plugin_root / skill / sub / "draft.md").exists()
        # Must not preserve the nested prompts/ layout under any subfolder.
        for sub in ["references", "typography", "corpus", "glossary"]:
            assert not (plugin_root / skill / sub / "prompts").exists()


def test_distribute_unknown_nested_subdir_is_unrouted(tmp_path):
    """Files under canonical/<unknown-subdir>/ must NOT auto-distribute."""
    plugin_root = tmp_path / "translation-toolkit"
    canonical = plugin_root / "scripts" / "canonical"
    (canonical / "scratch").mkdir(parents=True)
    (canonical / "scratch" / "foo.md").write_text("# scratch")
    for skill in ["translation-i18n", "translation-doc", "translation-creative", "translation-audit"]:
        (plugin_root / skill).mkdir(parents=True)
    shutil.copy(REPO_SCRIPT, plugin_root / "scripts" / "distribute.py")
    result = subprocess.run(
        ["python3", "scripts/distribute.py"], cwd=plugin_root, capture_output=True, text=True
    )
    assert "WARN" in result.stdout
    assert "scratch/foo.md" in result.stdout
    for skill in ["translation-i18n", "translation-doc", "translation-creative", "translation-audit"]:
        for sub in ["references", "typography", "corpus", "glossary"]:
            assert not (plugin_root / skill / sub / "foo.md").exists()
