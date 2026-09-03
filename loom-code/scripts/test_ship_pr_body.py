"""W1-04 — the ship station's SKILL.md is executable, and its PR body survives the merge.

Two families of assertion:

1. The PR body template the station tells the agent to write must still
   satisfy the post-merge carrier check that runs on every push to `main`
   (`.github/workflows/memory-verify-merged.yml`, which shells out to
   `loom-workflow/skills/git-memory/scripts/memory-grep.sh --verify-merged`).
   The template is rendered into a real commit message in a throwaway git
   repository and the real script is run against it — a regex copied into
   this file would drift from the workflow the moment either side moved.

2. The same executability floor the other stations carry: named checker
   rules exist, cited paths exist, prose gates are registered mechanisms,
   deleted vocabulary stays deleted, and the body is short enough that the
   cold reader of REQ-9 reaches the end.
"""
from __future__ import annotations

import ast
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO / "loom-code" / "skills" / "ship"
SKILL = SKILL_DIR / "SKILL.md"
CHECKER = REPO / "loom-code" / "scripts" / "loom_checker.py"
CONTRACT = REPO / "loom-code" / "contract"
MECHANISMS = REPO / "docs" / "loom" / "evidence" / "mechanisms.yaml"
MEMORY_GREP = REPO / "loom-workflow" / "skills" / "git-memory" / "scripts" / "memory-grep.sh"
WORKFLOW = REPO / ".github" / "workflows" / "memory-verify-merged.yml"

WORD_CAP = 3500
DESCRIPTION_CAP = 400

PR_BODY_ANCHOR = "<!-- pr-body-template -->"
FENCE_RE = re.compile(r"^```")
GATE_RE = re.compile(r"<!--\s*gate:\s*([A-Za-z0-9._-]+)\s*-->")
REFERENCE_RE = re.compile(r"references/([A-Za-z0-9._-]+\.md)")
TEMPLATE_RE = re.compile(r"contract/templates/([A-Za-z0-9._-]+)")
RULE_RE = re.compile(
    r"\b(?:intent|intake|push|standing|contract)\.(?!md\b|json\b|ya?ml\b|py\b)"
    r"[a-z][a-z0-9-]*\b"
)
SUBCOMMAND_RE = re.compile(r"loom_checker\.py\s+(--list-rules|[a-z][a-z-]*)")

COMMIT_TYPES = {"feat", "fix", "test", "docs", "chore", "refactor"}

# concept-model §10 deleted these outright, plus the machinery this station
# inherited from `finishing-a-development-branch` and must not carry over.
# `batch` / `batches` are still forbidden in the old "batch review" sense —
# except the "nit batch" / "nit-batch" phrase, the small-change-lane
# mechanism (2026-09-03) that bunches nit-severity findings into one
# pre-push commit; that is a different, currently-live concept and the
# negative lookbehind exempts only that exact phrase.
DELETED_VOCABULARY = (
    r"\bmarker\b",
    r"\bmarkers\b",
    r"\bwaiver\b",
    r"\bwaivers\b",
    r"\bmint\b",
    r"\bminted\b",
    r"(?<!nit )(?<!nit-)\bbatch\b",
    r"(?<!nit )(?<!nit-)\bbatches\b",
    r"progress card",
    r"\bbacklog\b",
    r"archive_change_folder",
    r"Approved-by",
    r"observed fan-outs",
)


@pytest.fixture(scope="module")
def skill_text() -> str:
    assert SKILL.is_file(), f"{SKILL.relative_to(REPO)} does not exist."
    return SKILL.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def skill_body(skill_text: str) -> str:
    match = re.match(r"^---\n.*?\n---\n", skill_text, re.DOTALL)
    return skill_text[match.end() :] if match else skill_text


def skill_markdown() -> list[Path]:
    return sorted(p for p in SKILL_DIR.rglob("*.md"))


def checker_subcommands() -> set[str]:
    tree = ast.parse(CHECKER.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if "COMMANDS" in targets and isinstance(node.value, ast.Dict):
                return {k.value for k in node.value.keys if isinstance(k, ast.Constant)}
    raise AssertionError("loom_checker.py declares no COMMANDS mapping.")


def checker_rule_ids() -> set[str]:
    """The rule population, read from the checker's own RULES table."""
    tree = ast.parse(CHECKER.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", "") == "RULES":
            value = node.value
        elif isinstance(node, ast.Assign) and any(
            getattr(t, "id", "") == "RULES" for t in node.targets
        ):
            value = node.value
        else:
            continue
        return {
            element.elts[0].value
            for element in value.elts
            if isinstance(element, ast.Tuple) and isinstance(element.elts[0], ast.Constant)
        }
    raise AssertionError("loom_checker.py declares no RULES table.")


def pr_body_template(text: str) -> str:
    """The fenced block right after the PR-body anchor comment."""
    assert PR_BODY_ANCHOR in text, (
        f"SKILL.md carries no {PR_BODY_ANCHOR} anchor, so the PR body template "
        "cannot be located and cannot be checked against the merge workflow."
    )
    tail = text.split(PR_BODY_ANCHOR, 1)[1].splitlines()
    opened = False
    collected: list[str] = []
    for line in tail:
        if FENCE_RE.match(line.strip()):
            if opened:
                return "\n".join(collected)
            opened = True
            continue
        if opened:
            collected.append(line)
    raise AssertionError("the PR-body anchor is not followed by a closed fenced block.")


INLINE_GREP_RE = re.compile(r"git log -1 --format=%B[^\n]*\|\s*grep -E '(\^\([A-Za-z|]+\)):'")


def inline_footer_grep_pattern(skill_text: str) -> str:
    """The regex the station's step-6 fallback greps the squash commit with."""
    match = INLINE_GREP_RE.search(skill_text)
    assert match, (
        "the ship station no longer carries an inline `git log | grep` fallback "
        "for the post-merge carrier check; a loom-code-only install would have "
        "no carrier check at all."
    )
    return match.group(1)


# --- family 1: the body survives the post-merge carrier check ----------------


@pytest.mark.skipif(
    not WORKFLOW.is_file(),
    reason="the post-merge workflow is repo-local, not part of the plugin",
)
def test_workflow_still_runs_verify_merged():
    """If the workflow stops calling this script, family 1 is checking nothing."""
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "--verify-merged" in text and "memory-grep.sh" in text, (
        f"{WORKFLOW.relative_to(REPO)} no longer runs memory-grep.sh "
        "--verify-merged; this test's premise is stale."
    )


def test_pr_body_template_ends_with_the_raw_trailer_footer(skill_text):
    body = pr_body_template(skill_text)
    lines = [line for line in body.splitlines() if line.strip()]
    assert lines, "the PR body template is empty."
    assert any(re.match(r"^## Memory\s*$", line) for line in body.splitlines()), (
        "the PR body template has no `## Memory` heading — the merge workflow "
        "greps for exactly that line."
    )
    assert re.match(r"^(Decision|Learning|Gotcha):", lines[-1]), (
        f"the PR body template's last non-empty line is {lines[-1]!r}; it must be "
        "a raw Decision:/Learning:/Gotcha: trailer, because a trailer block "
        "followed by any other line stops being the message's footer."
    )


@pytest.mark.skipif(shutil.which("git") is None, reason="git is required")
@pytest.mark.skipif(
    not MEMORY_GREP.is_file(),
    reason="loom-workflow is a separate plugin and need not be installed here",
)
def test_pr_body_template_passes_the_real_verify_merged(skill_text, tmp_path):
    """Render the template into a squash-shaped commit and run the real script."""
    message = "feat(loom-code): example change (#123)\n\n" + pr_body_template(skill_text) + "\n"

    work = tmp_path / "repo"
    work.mkdir()
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@example.com",
    }
    subprocess.run(["git", "init", "-q"], cwd=work, check=True, env=env)
    message_file = tmp_path / "message.txt"
    message_file.write_text(message, encoding="utf-8")
    subprocess.run(
        ["git", "commit", "-q", "--allow-empty", "-F", str(message_file)],
        cwd=work,
        check=True,
        env=env,
    )

    result = subprocess.run(
        ["bash", str(MEMORY_GREP), "--verify-merged", "HEAD", f"--repo={work}"],
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode == 3:
        pytest.skip(f"memory-grep dependency missing: {result.stderr.strip()}")
    assert result.returncode == 0, (
        "the PR body template does not survive the post-merge carrier check "
        f"(exit {result.returncode}): {result.stdout}{result.stderr}"
    )


# --- family 2: the station file is followable as written ---------------------


def test_skill_dir_is_flat():
    assert SKILL.is_file()
    nested = [
        p for p in SKILL_DIR.iterdir()
        if p.is_dir() and any(child.is_dir() for child in p.iterdir())
    ]
    assert not nested, f"skill sub-folders must not nest: {nested}"


def test_frontmatter_name_and_description(skill_text):
    match = re.match(r"^---\n(.*?)\n---\n", skill_text, re.DOTALL)
    assert match, "SKILL.md has no frontmatter."
    front = yaml.safe_load(match.group(1))
    assert front["name"] == "ship"
    description = " ".join(str(front["description"]).split())
    assert len(description) <= DESCRIPTION_CAP, (
        f"description is {len(description)} chars; the host truncates past "
        f"{DESCRIPTION_CAP}."
    )


def test_summary_table_covers_every_station(skill_text):
    manifest = yaml.safe_load((CONTRACT / "manifest.yaml").read_text(encoding="utf-8"))
    stations = [s["name"] for s in manifest["stations"]]
    rows = [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in skill_text.splitlines()
        if line.strip().startswith("|") and line.strip().endswith("|")
    ]
    header_index = None
    for index, row in enumerate(rows):
        header = " ".join(row).lower()
        if all(c in header for c in ("artifact", "who decides", "checker", "checkpoint")):
            header_index = index
            break
    assert header_index is not None, (
        "SKILL.md carries no station summary table with the four answer columns."
    )
    following = " ".join(" ".join(row) for row in rows[header_index + 1 :])
    for station in stations:
        assert station in following, (
            f"the summary table has no row for station {station!r}; REQ-9 wants "
            "the whole station order in the one file the cold reader holds."
        )


def test_every_checker_subcommand_exists(skill_text):
    known = checker_subcommands() | {"--list-rules"}
    used = set(SUBCOMMAND_RE.findall(skill_text))
    assert used, "SKILL.md names no loom_checker.py sub-command at all."
    unknown = sorted(used - known)
    assert not unknown, f"unknown checker sub-commands: {unknown}; known {sorted(known)}."


def test_every_named_rule_id_exists(skill_text):
    known = checker_rule_ids()
    used = set(RULE_RE.findall(skill_text))
    assert used, "SKILL.md names no checker rule; the push gate is the point of it."
    unknown = sorted(used - known)
    assert not unknown, (
        f"SKILL.md names checker rules that do not exist: {unknown}; the checker "
        f"has {sorted(known)}."
    )


def test_referenced_paths_exist(skill_text):
    for name in sorted(set(REFERENCE_RE.findall(skill_text))):
        assert (SKILL_DIR / "references" / name).is_file(), (
            f"SKILL.md cites references/{name}, which does not exist."
        )
    for name in sorted(set(TEMPLATE_RE.findall(skill_text))):
        assert (CONTRACT / "templates" / name).is_file(), (
            f"SKILL.md cites contract/templates/{name}, which does not exist."
        )


def test_gate_markers_are_registered_mechanisms():
    registered = {
        str(entry["id"]): entry
        for entry in yaml.safe_load(MECHANISMS.read_text(encoding="utf-8"))["mechanisms"]
    }
    found: set[str] = set()
    for path in skill_markdown():
        found |= set(GATE_RE.findall(path.read_text(encoding="utf-8")))
    assert found, (
        "ship marks no prose gate; the two rules it enforces in prose — no push "
        "before acceptance, and the PR body carries the trailer footer — are "
        "gates and must be marked."
    )
    for gate_id in sorted(found):
        assert gate_id.startswith("ship."), (
            f"gate id {gate_id!r} must be namespaced `ship.<id>`."
        )
        assert gate_id in registered, (
            f"gate {gate_id!r} is not registered in {MECHANISMS.relative_to(REPO)} "
            "— an unregistered gate raises the mechanism baseline silently."
        )
        assert registered[gate_id]["class"] == "prose-gate", (
            f"gate {gate_id!r} is registered as class "
            f"{registered[gate_id]['class']!r}."
        )
        assert str(registered[gate_id].get("eval", "")).strip(), (
            f"gate {gate_id!r} carries no eval:."
        )


@pytest.mark.parametrize("pattern", DELETED_VOCABULARY)
def test_no_deleted_vocabulary(pattern):
    offenders = []
    for path in skill_markdown():
        if re.search(pattern, path.read_text(encoding="utf-8"), re.IGNORECASE):
            offenders.append(path.relative_to(REPO).as_posix())
    assert not offenders, (
        f"{pattern} names machinery this redesign deleted; found in {offenders}."
    )


def test_commit_type_whitelist_matches_ci(skill_body):
    flat = " ".join(skill_body.split())
    match = re.search(r"type whitelist(.*?)nothing else passes", flat)
    assert match, (
        "SKILL.md states no commit-type whitelist; the CI type check has bitten "
        "this repo eleven times and the station writes commits."
    )
    named = set(re.findall(r"`([a-z]+)`", match.group(1)))
    assert named == COMMIT_TYPES, (
        f"the stated commit types {sorted(named)} differ from the CI whitelist "
        f"{sorted(COMMIT_TYPES)}."
    )


def test_body_word_count(skill_body):
    words = len(skill_body.split())
    assert words <= WORD_CAP, f"SKILL.md body is {words} words (cap {WORD_CAP})."


@pytest.mark.skipif(shutil.which("git") is None, reason="git is required")
def test_pr_body_template_passes_the_stations_own_inline_grep(skill_text, tmp_path):
    """The station's fallback check must find the footer without loom-workflow.

    Step 6 tells the agent to run an inline `git log | grep` when the sibling
    plugin is absent. That grep is the only carrier check a loom-code-only
    install has, so it is run here for real against a squash-shaped commit
    built from the station's own template.
    """
    pattern = inline_footer_grep_pattern(skill_text)
    message = "feat(loom-code): example change (#123)\n\n" + pr_body_template(skill_text) + "\n"

    work = tmp_path / "repo"
    work.mkdir()
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@example.com",
    }
    subprocess.run(["git", "init", "-q"], cwd=work, check=True, env=env)
    message_file = tmp_path / "message.txt"
    message_file.write_text(message, encoding="utf-8")
    subprocess.run(
        ["git", "commit", "-q", "--allow-empty", "-F", str(message_file)],
        cwd=work,
        check=True,
        env=env,
    )

    body = subprocess.run(
        ["git", "log", "-1", "--format=%B", "HEAD"],
        cwd=work,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    ).stdout
    matched = [line for line in body.splitlines() if re.match(pattern, line)]
    assert matched, (
        f"the station's own fallback grep {pattern!r} finds no trailer footer in "
        "a commit built from its PR-body template."
    )
