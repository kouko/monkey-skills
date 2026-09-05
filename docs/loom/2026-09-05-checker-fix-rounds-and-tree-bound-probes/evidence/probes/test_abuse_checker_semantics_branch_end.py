"""Branch-end adversarial probes for
2026-09-05-checker-fix-rounds-and-tree-bound-probes -- six attack classes,
one attempt each, against the delta closing this branch. Every case is
self-contained (no import from the wave-end/W0 probe files, no shared
sandbox helper) so it stands as an independent second opinion rather than
re-running the same fixture under a new name.

REPO is resolved via `git rev-parse --show-toplevel`, never a hardcoded
`parents[n]` walk, so the file keeps working if it is ever moved. Any
comparison against a git ref (a trunk, a tag) is skipped rather than
failed when that ref does not resolve in the sandbox it was run from.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
)
CHECKER = REPO / "loom-code" / "scripts" / "loom_checker.py"
SHIP_SKILL_MD = REPO / "loom-code" / "skills" / "ship" / "SKILL.md"
REVIEW_SKILL_MD = REPO / "loom-code" / "skills" / "review" / "SKILL.md"
MEMORY_DIR = REPO / "docs" / "loom" / "memory"
MEMORY_ENTRY = MEMORY_DIR / "a-gate-that-binds-records-to-commit-ids-taxes-every-bookkeeping-commit.md"
MEMORY_README = MEMORY_DIR / "README.md"
GRAD_A = REPO / "loom-code" / "scripts" / "test_probes_checker_semantics.py"
GRAD_B = REPO / "loom-code" / "scripts" / "test_probes_checker_semantics_wave_end.py"
ORIG_A = REPO / "docs" / "loom" / "2026-09-05-checker-fix-rounds-and-tree-bound-probes" / "evidence" / "probes" / "test_abuse_checker_semantics.py"
ORIG_B = REPO / "docs" / "loom" / "2026-09-05-checker-fix-rounds-and-tree-bound-probes" / "evidence" / "probes" / "test_abuse_checker_semantics_wave_end.py"
PLUGIN_MANIFESTS = [
    REPO / "loom-code" / ".claude-plugin" / "plugin.json",
    REPO / "loom-code" / ".codex-plugin" / "plugin.json",
]
README = REPO / "README.md"
CHANGELOG = REPO / "loom-code" / "CHANGELOG.md"
CODEX_MIRROR = REPO / ".codex" / "hooks" / "loom_checker.py"
SYNC_SCRIPT = REPO / "scripts" / "sync_codex_manifests.py"


def _git(*args: str, cwd: Path = REPO) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(cwd), *args], capture_output=True, text=True
    )


def _ref_exists(ref: str) -> bool:
    return _git("rev-parse", "--verify", ref).returncode == 0


def _flat_sentences(text: str) -> list[str]:
    flat = " ".join(text.split())
    return [p for p in re.split(r"(?<=[.!?])\s+", flat) if p.strip()]


# ----------------------------------------------------------------------------
# class 1 -- ship SKILL.md sS6: closing commit shape, and the PR-body order
# ----------------------------------------------------------------------------


def _sandbox_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git("init", "-q", "-b", "main", cwd=repo)
    _git("config", "user.email", "t@example.com", cwd=repo)
    _git("config", "user.name", "T", cwd=repo)
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    _git("add", "seed.txt", cwd=repo)
    _git("commit", "-q", "-m", "seed", cwd=repo)
    _git("checkout", "-q", "-b", "work", cwd=repo)
    kickoff = repo / "docs/loom/KICKOFF-DEFAULTS.md"
    kickoff.parent.mkdir(parents=True, exist_ok=True)
    kickoff.write_text(
        "# Kickoff Defaults\n\n- package-tests: python3 -c pass — probe fixture (2026-09-05)\n",
        encoding="utf-8",
    )
    return repo


def _seed_intent_and_code(repo: Path, change: str) -> str:
    intent = repo / f"docs/loom/intent/{change}.md"
    intent.parent.mkdir(parents=True, exist_ok=True)
    intent.write_text(f"# {change}\nstatus: confirmed 2026-09-01\n\n## Problem\nx\n", encoding="utf-8")
    _git("add", "-A", cwd=repo)
    _git("commit", "-q", "-m", "feat: seed intent\n\nTask: T1", cwd=repo)
    return _git("rev-parse", "HEAD", cwd=repo).stdout.strip()


def _closing_commit_body(code_sha: str) -> dict:
    dispatch = [
        {"task": "T1", "role": "implementer", "agent_id": "impl-1", "model": "m",
         "started": "2026-09-05T09:00:00Z", "fresh_context": True},
        {"task": "T1", "role": "reviewer", "agent_id": "rev-a", "model": "m",
         "started": "2026-09-05T09:10:00Z", "fresh_context": True},
        {"task": "T1", "role": "reviewer", "agent_id": "rev-b", "model": "m",
         "started": "2026-09-05T09:11:00Z", "fresh_context": True},
    ]
    return {
        "reviewed_sha": code_sha,
        "scope": "branch-end",
        "vendors": ["anthropic"],
        "verdicts": [
            {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 1, "verdict": "PASS", "dimension_scores": {}, "sha": code_sha, "findings": []},
            {"reviewer": "rev-b", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 1, "verdict": "PASS", "dimension_scores": {}, "sha": code_sha, "findings": []},
        ],
        "probes": [
            {"kind": "package-tests", "command": "python3 -c pass", "sha": code_sha,
             "result": "pass", "artifact": ""},
        ],
        "open_findings": [],
        "dispatch": dispatch,
    }


def test_ship_close_commit_option_a_shape_push_exits_zero(tmp_path: Path) -> None:
    """Attack (class 1a): try the exact option-A closing-commit shape ship's
    S6 prescribes -- review.json plus the intent's `status:` line alone,
    flipped to `closed <date> — branch <name>` -- through the REAL `push`
    subcommand end to end (not the internal check function). Expected GREEN:
    a reader following S6 verbatim is not blocked."""
    change = "zzz-branch-end-close-probe-a"
    repo = _sandbox_repo(tmp_path)
    code_sha = _seed_intent_and_code(repo, change)
    review_rel = f"docs/loom/{change}/review.json"
    intent_rel = f"docs/loom/intent/{change}.md"

    review_path = repo / review_rel
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(json.dumps(_closing_commit_body(code_sha), indent=1), encoding="utf-8")

    intent_path = repo / intent_rel
    text = intent_path.read_text(encoding="utf-8")
    intent_path.write_text(
        text.replace("status: confirmed 2026-09-01", "status: closed 2026-09-06 — branch probe-branch"),
        encoding="utf-8",
    )

    _git("add", review_rel, intent_rel, cwd=repo)
    _git("commit", "-q", "-m", "chore(loom): checkpoint review — branch-end PASS", cwd=repo)

    result = subprocess.run(
        [sys.executable, str(CHECKER), "push"], capture_output=True, text=True, cwd=str(repo)
    )
    assert result.returncode == 0, result.stderr


def test_ship_close_commit_with_unrelated_second_file_blocks(tmp_path: Path) -> None:
    """Attack (class 1b): can ship's S6 be read as allowing ANY other file to
    ride along in the closing commit, not only the intent's status line? Add
    a plainly unrelated third file (a stray code change) to the same commit
    and confirm the real `push` subcommand still blocks on
    `push.review-only-head` -- a hostile reading of S6 ("the close line
    rides in the commit" taken to license "so does anything else") must
    still fail."""
    change = "zzz-branch-end-close-probe-b"
    repo = _sandbox_repo(tmp_path)
    code_sha = _seed_intent_and_code(repo, change)
    review_rel = f"docs/loom/{change}/review.json"
    intent_rel = f"docs/loom/intent/{change}.md"
    stray_rel = "src/unrelated_change.py"

    review_path = repo / review_rel
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(json.dumps(_closing_commit_body(code_sha), indent=1), encoding="utf-8")

    intent_path = repo / intent_rel
    text = intent_path.read_text(encoding="utf-8")
    intent_path.write_text(
        text.replace("status: confirmed 2026-09-01", "status: closed 2026-09-06 — branch probe-branch"),
        encoding="utf-8",
    )

    stray_path = repo / stray_rel
    stray_path.parent.mkdir(parents=True, exist_ok=True)
    stray_path.write_text("print('sneaked in')\n", encoding="utf-8")

    _git("add", review_rel, intent_rel, stray_rel, cwd=repo)
    _git("commit", "-q", "-m", "chore(loom): checkpoint review + a stray file", cwd=repo)

    result = subprocess.run(
        [sys.executable, str(CHECKER), "push"], capture_output=True, text=True, cwd=str(repo)
    )
    assert result.returncode == 1
    blocked = {
        line.split(":", 1)[0].removeprefix("BLOCK ").strip()
        for line in result.stderr.splitlines() if line.startswith("BLOCK ")
    }
    assert "push.review-only-head" in blocked, result.stderr


def test_ship_pr_body_template_memory_is_last_block_after_closing_log() -> None:
    """Attack (class 1c): re-derive, independently of test_ship_pr_body.py
    and test_ship_station_text.py, that the PR-body template keeps
    `## Closing log` before `## Memory`, and that `## Memory` (with the raw
    trailer footer) is the LAST heading in the template -- so a reader who
    reorders sections cannot push the trailer footer out of last place
    without this failing too."""
    text = SHIP_SKILL_MD.read_text(encoding="utf-8")
    start = text.index("<!-- pr-body-template -->")
    end = text.index("<!-- /gate -->", start)
    template = text[start:end]
    headings = re.findall(r"^## .+$", template, re.M)
    assert headings, "no headings found in the pr-body-template block"
    assert headings[-1].strip() == "## Memory", (
        f"expected '## Memory' to be the last heading in the PR body template, got {headings!r}"
    )
    closing_idx = template.index("## Closing log")
    memory_idx = template.index("## Memory")
    assert closing_idx < memory_idx


# ----------------------------------------------------------------------------
# class 2 -- review SKILL.md sS7/sS8a: the fix-round anchor safety condition
# ----------------------------------------------------------------------------


def test_review_fix_round_anchor_condition_survives_semicolon_split() -> None:
    """Attack (class 2): a reader skimming S8a might stop at the first
    semicolon ("... resumes the reader(s) who raised the still-open
    findings;") and miss the anchor-scoped safety net that follows. Confirm
    the anchor condition ("otherwise it is resumed too") sits in the SAME
    sentence as the reader-who-raised-none clause, so even a semicolon-only
    reading of the clause that follows the split still carries the escape
    hatch -- a reader cannot quote "keeps its previous PASS standing"
    without also quoting the "otherwise ... resumed too" that qualifies it.
    RESULT: this attack failed to break anything -- the text is already one
    atomic sentence end to end."""
    text = REVIEW_SKILL_MD.read_text(encoding="utf-8")
    start = text.index("## 8a. Fix rounds")
    section = text[start:]
    sentences = _flat_sentences(section)
    target = [
        s for s in sentences
        if "resumes the reader" in s.lower() and "still-open findings" in s.lower()
    ]
    assert target, "no sentence in S8a resumes-the-reader clause found"
    sentence = target[0]
    # a hostile reader stopping at the first semicolon:
    after_semicolon = sentence.split(";", 1)[1] if ";" in sentence else sentence
    assert "keeps its previous pass standing" in after_semicolon.lower()
    assert "otherwise it is resumed too" in after_semicolon.lower(), (
        "the anchor safety condition is NOT in the same clause as the "
        "reader-who-raised-none exemption -- a reader could stop reading "
        "before the escape hatch"
    )
    assert "push.verdicts-ge-2" in sentence.lower()


def test_review_round_numbers_continue_sentence_names_branch_end_example() -> None:
    """Attack (class 2, second attempt): could S7's round-numbering sentence
    be read as applying only to wave-end-to-wave-end continuity, leaving a
    branch-end round free to restart numbering? Confirm the worked example
    explicitly names a branch-end round (round 4 after wave-end rounds
    1-3), closing that reading. RESULT: failed to break anything."""
    text = REVIEW_SKILL_MD.read_text(encoding="utf-8")
    start = text.index("## 7. Write the record")
    end = text.index("Every finding `text`, review note")
    section = text[start:end]
    sentences = _flat_sentences(section)
    hits = [
        s for s in sentences
        if "continue" in s.lower() and "branch-end" in s.lower() and "round 4" in s.lower()
    ]
    assert hits, "no sentence in S7 ties round continuity to a branch-end example"


# ----------------------------------------------------------------------------
# class 3 -- graduated probe copies, name collisions, memory index agreement
# ----------------------------------------------------------------------------


def _strip_path_lines(text: str) -> str:
    """Drop lines that merely restate the file's own repo-relative path (a
    provenance/header comment), so the byte comparison below isn't defeated
    by the one line the memory step is explicitly allowed to change."""
    lines = text.splitlines()
    return "\n".join(
        line for line in lines
        if "evidence/probes/test_abuse_checker_semantics" not in line
        and "loom-code/scripts/test_probes_checker_semantics" not in line
        and "parents[2]" not in line
        and "parents[5]" not in line
    )


def test_graduated_copy_a_equals_original_apart_from_path_lines() -> None:
    orig = _strip_path_lines(ORIG_A.read_text(encoding="utf-8"))
    grad = _strip_path_lines(GRAD_A.read_text(encoding="utf-8"))
    assert orig == grad, "test_probes_checker_semantics.py drifted from its evidence original beyond the path line"


def test_graduated_copy_b_equals_original_apart_from_path_lines() -> None:
    orig = _strip_path_lines(ORIG_B.read_text(encoding="utf-8"))
    grad = _strip_path_lines(GRAD_B.read_text(encoding="utf-8"))
    assert orig == grad, "test_probes_checker_semantics_wave_end.py drifted from its evidence original beyond the path line"


def _test_function_names(path: Path) -> list[str]:
    import ast
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [
        node.name for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    ]


def test_no_graduated_function_name_collides_with_any_other_test_in_repo() -> None:
    """Attack (class 3): build/SKILL.md's own memory-step rule says a shared
    test-function name with a DIFFERENT body is a name collision that must
    be renamed, not left as a duplicate. Both graduated files in this
    branch's closing wave were committed together
    (3ddecb05), so neither was "an existing test there" when the other
    graduated -- confirm no such same-commit collision slipped through."""
    all_names: dict[str, list[str]] = {}
    for path in (REPO / "loom-code" / "scripts").glob("test_*.py"):
        for name in _test_function_names(path):
            all_names.setdefault(name, []).append(str(path.relative_to(REPO)))
    collisions_among_graduated = {
        name: files for name, files in all_names.items()
        if len(files) > 1 and any(
            str(GRAD_A.relative_to(REPO)) in files or str(GRAD_B.relative_to(REPO)) in files
            for _ in [None]
        )
    }
    assert not collisions_among_graduated, (
        f"graduated probe file(s) share a test-function name with another "
        f"file in the same test package: {collisions_among_graduated!r} -- "
        "per build/SKILL.md's own rule this is a name collision, not a "
        "duplicate, and the later copy should have been renamed"
    )


def test_memory_entry_frontmatter_description_matches_readme_index_line() -> None:
    text = MEMORY_ENTRY.read_text(encoding="utf-8")
    front = text.split("---\n", 2)[1]
    desc_match = re.search(r"^description: (.+)$", front, re.M)
    assert desc_match, "memory entry has no `description:` frontmatter line"
    description = desc_match.group(1).strip()

    readme = MEMORY_README.read_text(encoding="utf-8")
    slug = "a-gate-that-binds-records-to-commit-ids-taxes-every-bookkeeping-commit"
    index_line = next(
        (line for line in readme.splitlines() if slug in line), None
    )
    assert index_line, f"README.md carries no index line for {slug}"
    # the README line is `[slug](slug.md) — <description>`
    assert " — " in index_line, index_line
    readme_description = index_line.split(" — ", 1)[1].strip()
    assert readme_description == description, (
        f"README index description disagrees with the entry's own frontmatter:\n"
        f"  entry:  {description!r}\n  readme: {readme_description!r}"
    )


def test_memory_integrity_check_script_exits_zero() -> None:
    script = REPO / "scripts" / "check_loom_memory_integrity.py"
    result = subprocess.run(
        [sys.executable, str(script)], capture_output=True, text=True, cwd=str(REPO)
    )
    assert result.returncode == 0, result.stdout + result.stderr


# ----------------------------------------------------------------------------
# class 4 -- version stamps agree; codex mirror byte-identical
# ----------------------------------------------------------------------------


def test_version_stamps_agree_everywhere() -> None:
    versions = {}
    for manifest in PLUGIN_MANIFESTS:
        versions[str(manifest.relative_to(REPO))] = json.loads(
            manifest.read_text(encoding="utf-8")
        )["version"]

    readme_text = README.read_text(encoding="utf-8")
    readme_row = next(
        (line for line in readme_text.splitlines() if "loom-code" in line and "|" in line),
        None,
    )
    assert readme_row, "README.md carries no loom-code table row"
    readme_version = [cell.strip() for cell in readme_row.split("|")][2]
    versions["README.md"] = readme_version

    changelog_top = next(
        (line for line in CHANGELOG.read_text(encoding="utf-8").splitlines() if line.startswith("## [")),
        None,
    )
    assert changelog_top, "CHANGELOG.md has no `## [x.y.z]` heading"
    changelog_version = changelog_top.split("[", 1)[1].split("]", 1)[0]
    versions["CHANGELOG.md (top)"] = changelog_version

    for path in (REPO / ".codex" / "hooks" / "loom-checker", CODEX_MIRROR):
        stamp_line = next(
            (line for line in path.read_text(encoding="utf-8").splitlines() if "loom-checker" in line and line.lstrip().startswith("#")),
            None,
        )
        assert stamp_line, f"{path} carries no `# loom-checker <version>` stamp line"
        versions[str(path.relative_to(REPO))] = stamp_line.split("loom-checker", 1)[1].strip()

    distinct = set(versions.values())
    assert len(distinct) == 1, f"version stamps disagree: {versions!r}"


def test_sync_codex_manifests_check_exits_zero() -> None:
    result = subprocess.run(
        [sys.executable, str(SYNC_SCRIPT), "--check", "loom-code"],
        capture_output=True, text=True, cwd=str(REPO),
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_codex_mirror_byte_identical_to_checker_masking_stamp_lines() -> None:
    """Independent re-derivation of test_codex_mirror_matches_checker.py's
    check: the mirror INSERTS one version-stamp comment line
    (`# loom-checker <version>`) right after the shebang, rather than
    replacing an existing line -- so the correct comparison drops that one
    inserted line from the mirror and requires the rest to be
    byte-identical to the source, not a same-length line-for-line mask."""
    stamp_re = re.compile(r"^#\s*loom-checker\s+\S+\s*$")
    checker_lines = (REPO / "loom-code" / "scripts" / "loom_checker.py").read_text(
        encoding="utf-8"
    ).splitlines()
    mirror_lines = CODEX_MIRROR.read_text(encoding="utf-8").splitlines()

    assert len(mirror_lines) == len(checker_lines) + 1, (
        f"mirror has {len(mirror_lines)} lines, source has {len(checker_lines)}; "
        "expected exactly one extra (the inserted stamp line)"
    )
    at = 1 if checker_lines and checker_lines[0].startswith("#!") else 0
    assert stamp_re.match(mirror_lines[at]), (
        f"expected an inserted `# loom-checker <version>` stamp line at index {at}, "
        f"got {mirror_lines[at]!r}"
    )
    rebuilt = mirror_lines[:at] + mirror_lines[at + 1:]
    assert rebuilt == checker_lines, (
        "the Codex mirror diverges from the source once the stamp line is removed"
    )


# ----------------------------------------------------------------------------
# class 5 -- dogfood: the branch's own checker on an option-A closing commit
# ----------------------------------------------------------------------------


def test_checker_dogfood_option_a_second_time_with_new_change_id(tmp_path: Path) -> None:
    """A second, independent dogfood run under a fresh change id (distinct
    from the class-1 sandbox above), confirming the branch's checker exits
    0 on the option-A shape reliably rather than as a one-off fixture
    artefact."""
    change = "zzz-branch-end-dogfood-c"
    repo = _sandbox_repo(tmp_path)
    code_sha = _seed_intent_and_code(repo, change)
    review_rel = f"docs/loom/{change}/review.json"
    intent_rel = f"docs/loom/intent/{change}.md"

    review_path = repo / review_rel
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(json.dumps(_closing_commit_body(code_sha), indent=1), encoding="utf-8")

    intent_path = repo / intent_rel
    text = intent_path.read_text(encoding="utf-8")
    intent_path.write_text(
        text.replace("status: confirmed 2026-09-01", "status: closed 2026-09-06 — branch dogfood-c"),
        encoding="utf-8",
    )

    _git("add", review_rel, intent_rel, cwd=repo)
    _git("commit", "-q", "-m", "chore(loom): checkpoint review — branch-end PASS", cwd=repo)

    result = subprocess.run(
        [sys.executable, str(CHECKER), "push"], capture_output=True, text=True, cwd=str(repo)
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.skipif(not _ref_exists("HEAD"), reason="no HEAD to resolve in this tree")
def test_checker_list_rules_still_27_lines_at_head() -> None:
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--list-rules"],
        capture_output=True, text=True, cwd=str(REPO),
    )
    assert result.returncode == 0, result.stderr
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) == 27, f"--list-rules emitted {len(lines)} lines, expected 27"


# ----------------------------------------------------------------------------
# class 6 -- word cap on every changed SKILL.md in this delta
# ----------------------------------------------------------------------------


def _body_word_count(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    body = re.sub(r"^---.*?---\n", "", text, count=1, flags=re.S)
    return len(body.split())


def test_changed_skill_md_files_stay_under_word_cap() -> None:
    """The delta since the last passing checkpoint touches review/SKILL.md
    and ship/SKILL.md; each body (frontmatter stripped) must stay <= 4,500
    words per CLAUDE.md's SKILL.md cap."""
    for path in (REVIEW_SKILL_MD, SHIP_SKILL_MD):
        count = _body_word_count(path)
        assert count <= 4500, f"{path.relative_to(REPO)} is {count} words, over the 4,500 cap"
