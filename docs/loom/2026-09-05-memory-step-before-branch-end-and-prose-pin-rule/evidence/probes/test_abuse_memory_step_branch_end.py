"""Branch-end adversarial probes for
2026-09-05-memory-step-before-branch-end-and-prose-pin-rule.

Six attack classes against the wave-2 delta (c2a5a82e..HEAD), one attempt
each, per the branch-end dispatch packet:

1. the two graduated probe files (loom-code/scripts/test_probes_memory_step
   {,_wave_end}.py) diverge from their evidence originals by more than the
   REPO path lines and the one renamed function, or the renamed function
   collides with another test function anywhere in loom-code/scripts/.
2. the new memory entry's frontmatter (name/description/type/origin)
   disagrees with the store's index line, or the store's own mechanical
   integrity checker fails.
3. version stamps disagree across plugin.json x2 / README version row /
   CHANGELOG top heading / .codex/hooks stamps, or the Codex manifest
   sync check disagrees.
4. every commit after the wave-end:1 review-only commit is wave-2 work or
   the memory step, none a post-review fix; stated as a forward
   expectation for what may follow this round, asserted only against
   what is true at HEAD today.
5. the W2-02 commits carry the `Task: W2-02` trailer and review.json
   carries an implementer dispatch entry for W2-02 (fresh_context: false)
   -- checked by commit *order* in the branch's history (a wall-clock
   comparison of the narrative `started` field against real commit
   timestamps is not meaningful here: this branch's real commits are all
   seconds apart while `started` values are spread across a simulated
   workday, so the ordering check is guarded onto git ancestry instead).
6. every SKILL.md changed on the branch stays inside the 4,500-word soft
   cap (Python str.split() on the body after the frontmatter fence); the
   adversary/blind-runner/reviewer agent bodies stay inside AGENT_CAPS.

Every probe is GREEN at HEAD unless a real defect surfaced; a RED probe
is reported as a finding, not silently weakened to pass. Git-ref
comparisons (this file uses one fixed base sha, not a floating branch
ref) skip via pytest.skip when that ref is absent from the local
repository instead of failing on a stale environment.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

# evidence/probes/test_abuse_memory_step_branch_end.py -> parents[5] is the
# repo root (probes -> evidence -> <change-id> -> loom -> docs -> repo root).
REPO = Path(__file__).resolve().parents[5]

WAVE1_REVIEW_ONLY_SHA = "c2a5a82ebf6369dae15e8570925e9d69e551cfb1"

GRADUATED_PAIRS = [
    (
        REPO
        / "docs/loom/2026-09-05-memory-step-before-branch-end-and-prose-pin-rule"
        / "evidence/probes/test_abuse_memory_step.py",
        REPO / "loom-code/scripts/test_probes_memory_step.py",
    ),
    (
        REPO
        / "docs/loom/2026-09-05-memory-step-before-branch-end-and-prose-pin-rule"
        / "evidence/probes/test_abuse_memory_step_wave_end.py",
        REPO / "loom-code/scripts/test_probes_memory_step_wave_end.py",
    ),
]

MEMORY_STORE = REPO / "docs/loom/memory"
MEMORY_ENTRY = MEMORY_STORE / "the-memory-step-belongs-before-the-closing-review-round.md"
MEMORY_README = MEMORY_STORE / "README.md"
INTEGRITY_CHECKER = REPO / "scripts/check_loom_memory_integrity.py"

SYNC_SCRIPT = REPO / "scripts/sync_codex_manifests.py"
CLAUDE_PLUGIN_JSON = REPO / "loom-code/.claude-plugin/plugin.json"
CODEX_PLUGIN_JSON = REPO / "loom-code/.codex-plugin/plugin.json"
README_TOP = REPO / "README.md"
CHANGELOG = REPO / "loom-code/CHANGELOG.md"
CODEX_HOOK_SHIM = REPO / ".codex/hooks/loom-checker"
CODEX_HOOK_PY = REPO / ".codex/hooks/loom_checker.py"

AGENT_CAPS = {"reviewer.md": 1460, "blind-runner.md": 600, "adversary.md": 600}
AGENTS_DIR = REPO / "loom-code/agents"
SKILL_WORD_CAP = 4500

def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout


def _ref_exists(ref: str) -> bool:
    return (
        subprocess.run(
            ["git", "cat-file", "-e", ref], cwd=REPO, capture_output=True
        ).returncode
        == 0
    )


def _skip_if_ref_missing(ref: str) -> None:
    if not _ref_exists(ref):
        pytest.skip(f"ref {ref} is absent from this clone; git-ref comparison skipped")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _body_word_count(path: Path) -> int:
    text = _read(path)
    if text.startswith("---"):
        parts = text.split("---", 2)
        body = parts[2] if len(parts) > 2 else text
    else:
        body = text
    return len(body.split())


def _all_def_test_names(scripts_dir: Path) -> dict[str, list[str]]:
    names: dict[str, list[str]] = {}
    for f in scripts_dir.glob("*.py"):
        for m in re.finditer(r"^def (test_[a-zA-Z0-9_]+)", _read(f), re.M):
            names.setdefault(m.group(1), []).append(f.name)
    return names


# --- class 1: graduated copies vs originals ---------------------------------


def test_memstep_graduatedCopy_matchesOriginalExceptPathLinesAndOneRename():
    """Diff each graduated copy against its evidence original: the only
    permitted differences are the REPO-path derivation lines (comment +
    the `parents[N]` line) and the single renamed function
    (`test_checker_rulecount_pinned` -> `test_memstep_checker_rulecount_pinned`)."""
    for original, graduated in GRADUATED_PAIRS:
        assert original.is_file(), f"missing evidence original: {original}"
        assert graduated.is_file(), f"missing graduated copy: {graduated}"
        orig_lines = _read(original).splitlines()
        grad_lines = _read(graduated).splitlines()
        assert len(orig_lines) == len(grad_lines), (
            f"{graduated.name}: line count diverged from its evidence original "
            "(expected a byte-copy plus path-line edits only)"
        )
        allowed_rename = ("test_checker_rulecount_pinned", "test_memstep_checker_rulecount_pinned")
        for i, (o, g) in enumerate(zip(orig_lines, grad_lines)):
            if o == g:
                continue
            is_path_line = "parents[" in o or "parents[" in g
            is_rename = allowed_rename[0] in o and allowed_rename[1] in g
            assert is_path_line or is_rename, (
                f"{graduated.name}:{i + 1}: unexpected divergence from its "
                f"evidence original beyond path lines / the one rename\n"
                f"  original:  {o!r}\n  graduated: {g!r}"
            )


def test_memstep_renamedFunction_noCollisionAcrossLoomCodeScripts():
    """The renamed function test_memstep_checker_rulecount_pinned must be
    unique across every test_*.py file under loom-code/scripts/ -- a
    collision would silently shadow one of the two tests under pytest's
    module-qualified but human-grep-driven review conventions."""
    scripts_dir = REPO / "loom-code/scripts"
    names = _all_def_test_names(scripts_dir)
    hits = names.get("test_memstep_checker_rulecount_pinned", [])
    assert len(hits) == 1, (
        "expected the renamed function to appear in exactly one file, "
        f"found it in: {hits}"
    )


# --- class 2: memory entry frontmatter vs index, integrity checker ---------


def _parse_frontmatter(path: Path) -> dict[str, str]:
    text = _read(path)
    assert text.startswith("---\n"), f"{path.name}: no frontmatter fence"
    _, fm, _ = text.split("---", 2)
    out: dict[str, str] = {}
    for line in fm.strip("\n").splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            out[key.strip()] = val.strip()
    return out


def test_memstep_memoryEntry_frontmatterFieldsAllPresent():
    """The new store entry must declare all four fields the ship-station
    contract requires: name, description, type, origin."""
    assert MEMORY_ENTRY.is_file(), f"missing memory entry: {MEMORY_ENTRY}"
    fm = _parse_frontmatter(MEMORY_ENTRY)
    for field in ("name", "description", "type", "origin"):
        assert field in fm and fm[field], f"frontmatter missing or empty field: {field}"
    assert fm["name"] == MEMORY_ENTRY.stem, (
        "frontmatter name must equal the filename (minus .md), "
        f"got name={fm['name']!r} filename={MEMORY_ENTRY.stem!r}"
    )


def test_memstep_memoryEntry_indexLineMatchesFrontmatterDescription():
    """README.md's index line for this entry must carry the file's
    filename as the link target and the frontmatter description
    byte-identical after stripping -- this repo's own integrity checker
    (invariants c/d) enforces exactly this."""
    fm = _parse_frontmatter(MEMORY_ENTRY)
    index_text = _read(MEMORY_README)
    pattern = re.compile(
        r"\[" + re.escape(fm["name"]) + r"\]\(" + re.escape(MEMORY_ENTRY.name) + r"\) — (.+)"
    )
    match = pattern.search(index_text)
    assert match, f"no index line found in README.md for {fm['name']}"
    assert match.group(1).strip() == fm["description"].strip(), (
        "index-line description diverges from frontmatter description"
    )


def test_memstep_integrityChecker_exitsZeroOnCleanStore():
    """scripts/check_loom_memory_integrity.py mechanizes the store's five
    §Index invariants (README.md docstring a-e); it must exit 0 at HEAD."""
    assert INTEGRITY_CHECKER.is_file(), f"missing checker: {INTEGRITY_CHECKER}"
    result = subprocess.run(
        [sys.executable, str(INTEGRITY_CHECKER), "--store", str(MEMORY_STORE)],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"memory-store integrity check failed:\n{result.stdout}\n{result.stderr}"
    )


# --- class 3: version stamps ------------------------------------------------


def test_memstep_versionStamps_agreeEverywhereAndSyncCheckPasses():
    """plugin.json x2, README's version row, CHANGELOG's top heading and
    the two .codex/hooks stamp lines must all name the same version, and
    the Codex-manifest sync script must confirm it in --check mode."""
    claude_json = _read(CLAUDE_PLUGIN_JSON)
    codex_json = _read(CODEX_PLUGIN_JSON)
    m1 = re.search(r'"version":\s*"([^"]+)"', claude_json)
    m2 = re.search(r'"version":\s*"([^"]+)"', codex_json)
    assert m1 and m2, "could not find a version field in one of the plugin.json files"
    version = m1.group(1)
    assert m2.group(1) == version, "the two plugin.json files disagree on version"

    readme = _read(README_TOP)
    assert f"| {version} |" in readme, (
        f"README.md's loom-code version row does not name {version}"
    )

    changelog_top = _read(CHANGELOG).splitlines()[7] if len(_read(CHANGELOG).splitlines()) > 7 else ""
    changelog_head = "\n".join(_read(CHANGELOG).splitlines()[:15])
    assert f"[{version}]" in changelog_head, (
        f"CHANGELOG.md's top heading does not name [{version}] in its first lines"
    )

    for hook_file in (CODEX_HOOK_SHIM, CODEX_HOOK_PY):
        assert version in _read(hook_file).splitlines()[1], (
            f"{hook_file.name}'s stamp line does not name {version}"
        )

    result = subprocess.run(
        [sys.executable, str(SYNC_SCRIPT), "--check", "loom-code"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"sync_codex_manifests.py --check loom-code failed:\n{result.stdout}\n{result.stderr}"
    )


# --- class 4: commit provenance since the wave-1 review-only commit --------


def test_memstep_commitsSinceReviewOnly_areWave2OrMemoryNeverPostReviewFix():
    """Every commit strictly after the wave-end:1 review-only commit
    (c2a5a82e) must be wave-2 implementation work, the memory step, or a
    dispatch record -- never a fix issued because a completed review
    round found something wrong (this branch's whole point is that such
    fixes should not exist post-review). This asserts only what is true
    at HEAD today: it does NOT claim anything about commits that land
    after *this* round finishes -- the expectation for those is that only
    a review-only commit and the single close commit may follow, and
    that expectation is stated here, not asserted, because it has not
    happened yet."""
    _skip_if_ref_missing(WAVE1_REVIEW_ONLY_SHA)
    subjects = _git(
        "log", f"{WAVE1_REVIEW_ONLY_SHA}..HEAD", "--format=%s"
    ).strip("\n").splitlines()
    assert subjects, "expected at least one commit after the wave-1 review-only commit"
    forbidden_markers = ("fix:", "NEEDS_REVISION", "post-review fix", "re-fix")
    for subject in subjects:
        lowered = subject.lower()
        assert not any(marker.lower() in lowered for marker in forbidden_markers), (
            f"commit subject reads like a post-review fix, not wave-2/memory work: {subject!r}"
        )


# --- class 5: W2-02 trailer + dispatch-before-work -------------------------


def _commits_by_grep(pattern: str) -> list[str]:
    """Newest-first list of commit shas on the current branch whose full
    message matches `pattern` (a `git log --grep` pattern)."""
    out = _git("log", "--format=%H", f"--grep={pattern}").strip("\n")
    return out.splitlines() if out else []


def test_memstep_w2_02Dispatch_precedesWork():
    """Both W2-02 work commits (found by trailer, not by hard-coded sha --
    a hard-coded sha goes stale the moment the branch is rewritten) must
    carry `Task: W2-02`. review.json must carry an implementer dispatch
    entry for W2-02 with fresh_context: false. The dispatch-record-
    before-work claim is checked by git ANCESTRY, not by comparing the
    narrative `started` timestamp against real commit clocks (this
    branch's real commits land seconds apart while `started` values are
    spread across a simulated workday, so a literal wall-clock comparison
    is not meaningful and is skipped here -- this is the guard). The
    dispatch commit (found by its subject, "dispatch W2-02") must be an
    ancestor of the earliest work commit."""
    work_shas = _commits_by_grep("^Task: W2-02")
    assert work_shas, "no commit on this branch carries the Task: W2-02 trailer"
    for sha in work_shas:
        message = _git("log", "-1", "--format=%B", sha)
        assert "Task: W2-02" in message, f"commit {sha} is missing the Task: W2-02 trailer"
    earliest_work_sha = work_shas[-1]  # git log lists newest first

    review_json = REPO / "docs/loom/2026-09-05-memory-step-before-branch-end-and-prose-pin-rule/review.json"
    text = _read(review_json)
    assert '"task": "W2-02"' in text, "review.json has no W2-02 dispatch entry"
    # the W2-02 dispatch block must declare fresh_context: false (self-dispatch)
    idx = text.index('"task": "W2-02"')
    window = text[max(0, idx - 400) : idx + 400]
    assert '"fresh_context": false' in window, (
        "the W2-02 dispatch entry does not declare fresh_context: false nearby"
    )

    dispatch_shas = _commits_by_grep("dispatch W2-02")
    assert dispatch_shas, "no commit on this branch has a subject naming 'dispatch W2-02'"
    dispatch_sha = dispatch_shas[-1]  # earliest such commit, same convention

    dispatch_before_work = (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", dispatch_sha, earliest_work_sha],
            cwd=REPO,
        ).returncode
        == 0
    )
    assert dispatch_before_work, (
        "dispatch-record-before-work ordering violated: the dispatch commit "
        f"{dispatch_sha} is not an ancestor of the earliest work commit "
        f"{earliest_work_sha} -- the memory-step work was committed before "
        "its own dispatch record"
    )


# --- class 6: word caps ------------------------------------------------------


def test_memstep_changedSkillFiles_stayWithinFourThousandFiveHundredWordCap():
    """Every SKILL.md the branch touches (build, ship, write-plan) must
    stay at or under the 4,500-word soft cap, counted the way this
    repo's own probes count it (Python str.split() on the body after the
    frontmatter fence)."""
    _skip_if_ref_missing("e895fbb3")
    changed = _git("diff", "--name-only", "e895fbb3..HEAD").splitlines()
    skill_files = [REPO / p for p in changed if p.endswith("SKILL.md")]
    assert skill_files, "expected at least one changed SKILL.md on this branch"
    for f in skill_files:
        assert f.is_file(), f"changed path no longer exists: {f}"
        count = _body_word_count(f)
        assert count <= SKILL_WORD_CAP, (
            f"{f.relative_to(REPO)}: {count} words exceeds the {SKILL_WORD_CAP}-word cap"
        )


def test_memstep_agentFiles_stayWithinAgentCaps():
    """adversary.md, blind-runner.md and reviewer.md must each stay within
    their AGENT_CAPS word limit; adversary.md changed on this branch."""
    for name, cap in AGENT_CAPS.items():
        path = AGENTS_DIR / name
        if not path.is_file():
            continue
        count = _body_word_count(path)
        assert count <= cap, f"{name}: {count} words exceeds its AGENT_CAPS limit of {cap}"
