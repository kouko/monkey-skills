"""Branch-end attacks for the single-owner local push gate.

Every fixture mutates only a temporary Git repository.  The six catalogue
classes are executable here, with additional absent-command and dependency
failure boundaries.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    bootstrap_root = next(
        p for p in Path(__file__).resolve().parents
        if (p / "requirements-package-tests.lock").is_file()
    )
    os.execvp(
        "uv",
        ["uv", "run", "--isolated", "--with-requirements",
         str(bootstrap_root / "requirements-package-tests.lock"),
         "python", "-m", "pytest", __file__, "-q", "--tb=line"],
    )


ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "loom-code" / "scripts" / "loom_checker.py").exists()
)
sys.path.insert(0, str(ROOT / "loom-code" / "scripts"))
import test_loom_checker_push as fixture
import test_single_owner_push_gate as permanent


def repository(tmp_path: Path, package: str = "python3 -c pass") -> tuple[Path, dict]:
    """Build a valid reviewed fixture with a replaceable package command."""
    repo = fixture.build_repo(tmp_path, package_tests=package)
    reviewed = fixture.git(repo, "rev-parse", "HEAD^")
    body = fixture.review_body(reviewed)
    body["probes"][0]["command"] = package
    fixture.recommit_review(repo, body)
    return repo, body


def observed(repo: Path) -> tuple[subprocess.CompletedProcess[str], str]:
    """Run the real push checker and retain its observable result."""
    result = fixture.run_checker("push", cwd=repo)
    detail = f"rc={result.returncode}\nstdout={result.stdout}\nstderr={result.stderr}"
    return result, detail


def affirmative_sentence(text: str, literal: str) -> bool:
    """Require an affirmative un-negated sentence that governs a literal."""
    normalized = re.sub(r"\s+", " ", text)
    negation = re.compile(r"\b(?:no|not|never|without|cannot|neither|nor)\b|n't", re.I)
    affirmative = re.compile(r"\b(?:is|owns|blocks|requires|runs|executes|issues)\b", re.I)
    for sentence in re.split(r"(?<=[.!?])\s+", normalized):
        position = sentence.find(literal)
        if position >= 0 and not negation.search(sentence) and affirmative.search(sentence[:position]):
            return True
    return False


def test_gate_forged_held(tmp_path: Path) -> None:
    """A forged recorded pass cannot replace an observed package failure."""
    repo, body = repository(tmp_path, "python3 -c 1/0")
    assert body["probes"][0]["result"] == "pass"
    result, detail = observed(repo)
    assert result.returncode != 0, detail
    assert "push.probes-package-tests" in result.stderr, detail


def test_gate_edited_held(tmp_path: Path) -> None:
    """Editing the recorded command cannot bypass repository command resolution."""
    repo, body = repository(tmp_path)
    body["probes"][0]["command"] = "python3 -c 'print(\"forged\")'"
    fixture.recommit_review(repo, body)
    result, detail = observed(repo)
    assert result.returncode != 0, detail
    assert "is not this repo's test command" in result.stderr, detail


def test_gate_stale_held(tmp_path: Path) -> None:
    """A genuine probe SHA from the pre-change commit is refused as stale."""
    repo, body = repository(tmp_path)
    body["probes"][0]["sha"] = fixture.git(repo, "rev-parse", "main")
    fixture.recommit_review(repo, body)
    result, detail = observed(repo)
    assert result.returncode != 0, detail
    assert "not the reviewed content" in result.stderr, detail


def test_hook_crossrepo_held(tmp_path: Path) -> None:
    """An absolute git -C push is checked in its selected repository."""
    selected = tmp_path / "selected"
    selected.mkdir()
    repo, _ = repository(selected)
    unrelated = tmp_path / "caller"
    unrelated.mkdir()
    head = fixture.git(repo, "rev-parse", "HEAD")
    payload = {
        "cwd": str(unrelated),
        "tool_input": {"command": permanent.immutable_push_command(repo, head, external=True)},
    }
    result = subprocess.run(
        [sys.executable, str(fixture.CHECKER), "push", "--hook"],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=unrelated,
    )
    assert result.returncode == 0, f"rc={result.returncode}\n{result.stdout}{result.stderr}"
    assert "package-tests `python3 -c pass`" in result.stdout
    assert not list(unrelated.iterdir())


def test_ship_selfexempt_held() -> None:
    """The one-line-diff temptation still meets affirmative hook ownership text."""
    assert affirmative_sentence("The hook owns the package suite.", "package suite")
    assert not affirmative_sentence("The hook does not own the package suite.", "package suite")
    assert not affirmative_sentence("Never run the package suite.", "package suite")
    ship = (ROOT / "loom-code" / "skills" / "ship" / "SKILL.md").read_text(encoding="utf-8")
    assert affirmative_sentence(ship, "sole owner")
    assert affirmative_sentence(ship, "Ship")


def test_gate_concurrent_reproduced(tmp_path: Path) -> None:
    """Fail closed when a mutable source could publish a delayed child commit."""
    result = permanent.delayed_network_replay(tmp_path, immutable=False)
    assert result["hook_rc"] == 2 and result["published"] is None, result


def test_gate_immutable_pinsreviewed(tmp_path: Path) -> None:
    """An actual local push remains pinned despite a post-hook child commit."""
    result = permanent.delayed_network_replay(tmp_path, immutable=True)
    assert result["hook_rc"] == 0, result
    assert result["published"] == result["before"], result
    assert result["published"] != result["after"], result


def test_gate_absent_held(tmp_path: Path) -> None:
    """An absent package declaration and marker cannot silently skip execution."""
    repo, _ = repository(tmp_path)
    fixture.git(repo, "reset", "--hard", "HEAD^")
    kickoff = repo / "docs" / "loom" / "KICKOFF-DEFAULTS.md"
    kickoff.unlink()
    fixture.git(repo, "add", "-A")
    fixture.git(repo, "commit", "--amend", "-q", "--no-edit")
    reviewed = fixture.git(repo, "rev-parse", "HEAD")
    fixture.write_review(repo, fixture.review_body(reviewed))
    fixture.git(repo, "add", fixture.REVIEW)
    fixture.git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")
    result, detail = observed(repo)
    assert result.returncode != 0, detail
    assert "declares no package-test command" in result.stderr, detail


def test_gate_missingexe_held(tmp_path: Path) -> None:
    """A declared command whose executable is missing blocks the push."""
    repo, _ = repository(tmp_path, "missing-program-branch-end-adversary")
    result, detail = observed(repo)
    assert result.returncode != 0, detail
    assert "names no program on PATH" in result.stderr, detail
