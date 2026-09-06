"""Independent W0-02 abuse cases; execute from any checkout of this probe.

Run: uv run --isolated --with pytest --with pyyaml python -m pytest
     loom-code/scripts/test_single_owner_push_gate.py -q

All mutations are confined to newly created temporary Git repositories.
Source checks are static contracts, not claims of a blind agent run.
"""
from __future__ import annotations

import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "loom-code/scripts/loom_checker.py").exists())
sys.path.insert(0, str(ROOT / "loom-code/scripts"))
import test_loom_checker_push as fixture


def repository(tmp_path: Path, *, package="python3 -c pass", scripts=None):
    """Commit attack payloads before the reviewed revision is selected."""
    repo = fixture.build_repo(tmp_path, package_tests=package)
    fixture.git(repo, "reset", "--soft", "HEAD^")
    for relative, content in (scripts or {}).items():
        (repo / relative).write_text(content, encoding="utf-8")
    fixture.git(repo, "add", "-A")
    fixture.git(repo, "commit", "--amend", "--no-edit", "-q")
    reviewed = fixture.git(repo, "rev-parse", "HEAD")
    body = fixture.review_body(reviewed)
    body["probes"][0]["command"] = package
    fixture.write_review(repo, body)
    fixture.git(repo, "add", fixture.REVIEW)
    fixture.git(repo, "commit", "-q", "-m", "chore: checkpoint")
    assert not fixture.git(repo, "status", "--porcelain")
    return repo, reviewed, body


TRACKED = "from pathlib import Path\nPath('a.py').write_text('value = 999\\n')\n"
HEADMOVE = "import subprocess\nsubprocess.run(['git', 'commit', '--allow-empty', '-qm', 'moved'], check=True)\n"
UNTRACKED = "from pathlib import Path\nPath('unexpected.txt').write_text('new\\n')\n"
STAGED = TRACKED + "import subprocess\nsubprocess.run(['git', 'add', 'a.py'], check=True)\n"
WRITER = (
    "import subprocess, sys\n"
    "writer = subprocess.Popen([sys.executable, '-c', "
    "\"from pathlib import Path; Path('a.py').write_text('writer\\\\n')\"])\n"
    "assert writer.wait() == 0\n"
)


def observed(repo):
    """Retain real gate output on assertion failure, without local paths."""
    result = fixture.run_checker("push", cwd=repo)
    return result, f"rc={result.returncode}\n{result.stdout}{result.stderr}"


def test_hook_selectedrepomutation_rejected(tmp_path):
    """The intercepted absolute -C target owns the state snapshot, not cwd."""
    repo, _, _ = repository(tmp_path, package="python3 evidence/package.py", scripts={"evidence/package.py": HEADMOVE})
    unrelated = tmp_path / "unrelated"
    unrelated.mkdir()
    before = fixture.git(repo, "rev-parse", "HEAD")
    payload = {"cwd": str(unrelated), "tool_input": {"command": f"git -C {shlex.quote(str(repo))} push origin work"}}
    result = subprocess.run([sys.executable, str(fixture.CHECKER), "push", "--hook"], input=json.dumps(payload), capture_output=True, text=True, cwd=unrelated)
    assert fixture.git(repo, "rev-parse", "HEAD") != before, "attack did not move target HEAD"
    assert not list(unrelated.iterdir()), "wrong repository was modified"
    assert result.returncode == 2, f"hook rc={result.returncode}\n{result.stdout}{result.stderr}"


def test_push_packageheadmove_rejected(tmp_path):
    """A successful suite may advance HEAD while leaving porcelain empty."""
    repo, _, _ = repository(tmp_path, package="python3 evidence/package.py", scripts={"evidence/package.py": HEADMOVE})
    before = fixture.git(repo, "rev-parse", "HEAD")
    result, detail = observed(repo)
    assert before != fixture.git(repo, "rev-parse", "HEAD"), "attack did not move HEAD"
    assert not fixture.git(repo, "status", "--porcelain")
    assert result.returncode != 0, detail


@pytest.mark.parametrize("payload", [TRACKED, STAGED, UNTRACKED, HEADMOVE, WRITER], ids=["tracked", "staged", "untracked", "head", "writer-process"])
def test_push_lastadversarymutation_rejected(tmp_path, payload):
    """The final adversarial process cannot mutate after all prechecks pass."""
    repo, _, _ = repository(tmp_path, scripts={"evidence/abuse_hostile.py": payload})
    before = fixture.git(repo, "rev-parse", "HEAD")
    result, detail = observed(repo)
    assert fixture.git(repo, "status", "--porcelain") or before != fixture.git(repo, "rev-parse", "HEAD"), "attack did not mutate"
    assert result.returncode != 0, detail


def test_push_firstadversarymutation_rejected(tmp_path):
    """Batch validation must not hide a mutation made by the first process."""
    repo, _, _ = repository(tmp_path, scripts={"evidence/abuse_empty.py": TRACKED})
    result, detail = observed(repo)
    assert fixture.git(repo, "status", "--porcelain"), "attack did not mutate"
    assert result.returncode != 0, detail


def test_push_packagetrackedmutation_rejected(tmp_path):
    """Existing later adversarial prechecks already catch this simple case."""
    repo, _, _ = repository(tmp_path, package="python3 evidence/package.py", scripts={"evidence/package.py": TRACKED})
    result, detail = observed(repo)
    assert fixture.git(repo, "status", "--porcelain")
    assert result.returncode != 0, detail


def test_push_unchangedrepeat_released(tmp_path):
    """An unchanged checkpoint can pass repeatedly without consuming a receipt."""
    repo, _, _ = repository(tmp_path)
    before = fixture.git(repo, "rev-parse", "HEAD")
    for _ in range(2):
        result, detail = observed(repo)
        assert result.returncode == 0, detail
    assert fixture.git(repo, "rev-parse", "HEAD") == before
    assert not fixture.git(repo, "status", "--porcelain")


@pytest.mark.parametrize("attack", ["forged-result", "edited-command", "stale-sha", "dirty-input", "missing-program", "malformed-command"])
def test_push_existingguard_preserved(tmp_path, attack):
    """Mutation hardening must retain command, freshness, and cleanliness guards."""
    package = "missing-program-for-w002" if attack == "missing-program" else "python3 -c pass"
    if attack == "malformed-command":
        package = "python3 -c '"
    repo, _, body = repository(tmp_path, package=package)
    if attack == "forged-result":
        repo2 = tmp_path / "second"
        repo2.mkdir()
        repo, _, body = repository(repo2, package="python3 -c 1/0")
        assert body["probes"][0]["result"] == "pass"
    elif attack == "edited-command":
        body["probes"][0]["command"] = "python3 -c 'print(123)'"
        fixture.recommit_review(repo, body)
    elif attack == "stale-sha":
        body["probes"][0]["sha"] = fixture.git(repo, "rev-parse", "main")
        fixture.recommit_review(repo, body)
    elif attack == "dirty-input":
        (repo / "a.py").write_text("unreviewed\n", encoding="utf-8")
    result, detail = observed(repo)
    assert result.returncode != 0, detail


def affirmative(text, literal):
    """Require an affirmative verb before a literal in the same sentence."""
    normalized = re.sub(r"\s+", " ", text)
    for sentence in re.split(r"(?<=[.!?])\s+", normalized):
        position = sentence.find(literal)
        if position < 0 or re.search(r"\b(?:no|not|never|without|cannot|neither|nor)\b|n't", sentence, re.I):
            continue
        if re.search(r"\b(?:run|runs|execute|executes|preserve|retain|keep)\b", sentence[:position], re.I):
            return True
    return False


def test_text_affirmativeoracle_rejectsnegation():
    """Validate the sentence oracle with a positive and a negated example."""
    assert affirmative("Run the integration tests.", "integration tests")
    assert not affirmative("Do not run the integration tests.", "integration tests")
    assert not affirmative("Run nothing. The integration tests exist.", "integration tests")


def test_build_prereviewsuite_absent():
    """A Build instruction cannot invoke the duplicate suite before review."""
    text = (ROOT / "loom-code/skills/build/SKILL.md").read_text()
    section = text.split("## 6.", 1)[1].split("## 6.5", 1)[0]
    assert not affirmative(section, "before the branch-end review"), "Build still executes the complete suite before review"
    assert not affirmative(section, "fully integrated tree"), "Build still executes the complete suite before review"
    assert affirmative(text, "integration tests"), "integration verification was weakened"


def test_ship_presuitescript_absent():
    """Ship must drop the suite command while retaining deterministic checks."""
    text = (ROOT / "loom-code/skills/ship/SKILL.md").read_text()
    section = text.split("## 4. Push", 1)[1].split("## 5.", 1)[0]
    assert not re.search(r"^python3 -m pytest\b", section, re.M), "Ship still runs the package suite before its hook"
    for command in (
        "python3 scripts/check_plugin_boundaries.py loom-code",
        "python3 scripts/check_plugin_boundaries.py loom-design",
        "python3 scripts/sync_codex_manifests.py --check --all",
        "python3 loom-code/scripts/check_mechanisms.py --baseline origin/main",
        "python3 loom-code/scripts/check_mechanisms.py --measure",
        "python3 loom-code/scripts/check_contract_citations.py",
        "python3 loom-code/scripts/check-skill-crossrefs.py",
    ):
        assert command in section, f"existing deterministic check removed: {command}"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q", "--tb=short"]))
