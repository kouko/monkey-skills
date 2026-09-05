"""Adversarial probes for the branch-end (closing) round of
2026-09-05-review-sees-complexity-and-process-cost.

Scope: the delta from reviewed_sha `1eeaf6a8447dd8412cff8e38a94960fca4acc19b`
(wave-end:1 PASS) to HEAD -- the `--then` separator rename across the
runner/tests/KICKOFF/CHANGELOG, the wave-end probe file's own fixes, its
graduated copy under `loom-code/scripts/`, a memory entry + README index
line, and `review.json`.

Commits are located by subject or trailer, never by a hardcoded sha.

Each test is independently re-runnable:
`python3 -m pytest docs/loom/2026-09-05-review-sees-complexity-and-process-cost/evidence/probes/test_abuse_complexity_branch_end.py -q`
from the repo root.
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

# The station-text and matcher modules this file may load import each
# other from loom-code/scripts/ at their own module top -- put it on
# sys.path unconditionally, the same discipline the wave-end probe file
# uses, so a `-k <group>` selection that skips the test which first
# needed the path still resolves imports for every other test.
sys.path.insert(0, str(REPO / "loom-code" / "scripts"))

EVIDENCE_PROBE = (
    REPO / "docs" / "loom" / "2026-09-05-review-sees-complexity-and-process-cost"
    / "evidence" / "probes" / "test_abuse_complexity_wave_end.py"
)
GRADUATED_PROBE = REPO / "loom-code" / "scripts" / "test_probes_complexity_wave_end.py"
REVIEW_JSON = (
    REPO / "docs" / "loom" / "2026-09-05-review-sees-complexity-and-process-cost"
    / "review.json"
)
KICKOFF = REPO / "docs" / "loom" / "KICKOFF-DEFAULTS.md"
MEMORY_README = REPO / "docs" / "loom" / "memory" / "README.md"
MEMORY_ENTRY = (
    REPO / "docs" / "loom" / "memory"
    / "one-record-commit-per-wave-and-per-round-keeps-the-record-honest-and-the-log-short.md"
)
RUNNER = REPO / "scripts" / "run_package_tests.py"
SHIP_SKILL = REPO / "loom-code" / "skills" / "ship" / "SKILL.md"
BUILD_SKILL = REPO / "loom-code" / "skills" / "build" / "SKILL.md"
REVIEWER_MD = REPO / "loom-code" / "agents" / "reviewer.md"
ADVERSARY_MD = REPO / "loom-code" / "agents" / "adversary.md"
REVIEW_SKILL = REPO / "loom-code" / "skills" / "review" / "SKILL.md"


def _confirm_intent_sha() -> str:
    out = subprocess.run(
        ["git", "log", "--all", "--format=%H",
         "--grep=^docs(loom): intent 2026-09-05-review-sees-complexity-and-process-cost confirmed$"],
        cwd=str(REPO), capture_output=True, text=True, check=True,
    ).stdout.strip().splitlines()
    assert out, "cannot locate the intent-confirmation commit by subject"
    return out[0]


def _body_of(text: str) -> str:
    match = re.match(r"^---\n.*?\n---\n", text, re.DOTALL)
    return text[match.end():] if match else text


def _text_after_heading(path: Path, heading: str) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.index(heading)
    rest = text[start + len(heading):]
    cut = re.search(r"\n## ", rest)
    return rest[: cut.start()] if cut else rest


# ---------------------------------------------------------------------------
# Class 1: the graduated copy of the wave-end probe file.
# ---------------------------------------------------------------------------

def test_graduated_probe_copy_matches_evidence_original_byte_for_byte() -> None:
    """The graduated copy under loom-code/scripts/ must be byte-identical to
    the evidence original -- both locate the repo via `git rev-parse
    --show-toplevel` at their own module top, so no absolute path line
    differs between the two copies."""
    assert EVIDENCE_PROBE.is_file()
    assert GRADUATED_PROBE.is_file()
    assert EVIDENCE_PROBE.read_bytes() == GRADUATED_PROBE.read_bytes(), (
        "the graduated copy has drifted from the evidence original it was "
        "supposed to be a byte copy of"
    )


def test_graduated_probe_test_names_do_not_collide_with_the_rest_of_loomcode_scripts() -> None:
    """No `test_*` function name defined in the graduated copy also appears
    as a top-level function in any OTHER file under loom-code/scripts/ --
    a collision would make `-k <name>` ambiguous across the package-tests
    session."""
    graduated_names = set(
        re.findall(r"^def (test_[a-zA-Z0-9_]+)", GRADUATED_PROBE.read_text(encoding="utf-8"), re.MULTILINE)
    )
    assert graduated_names, "no test_* functions found in the graduated copy"
    collisions: dict[str, list[str]] = {}
    for path in (REPO / "loom-code" / "scripts").glob("*.py"):
        if path == GRADUATED_PROBE:
            continue
        names = set(re.findall(r"^def (test_[a-zA-Z0-9_]+)", path.read_text(encoding="utf-8"), re.MULTILINE))
        for hit in names & graduated_names:
            collisions.setdefault(hit, []).append(str(path.relative_to(REPO)))
    assert collisions == {}, f"graduated test names collide elsewhere: {collisions}"


def test_graduated_probe_copy_passes_when_run_alone() -> None:
    """The graduated copy is claimed to be a stable regression file that
    passes on its own. Run it alone in a fresh subprocess and require a
    clean exit -- this is the adversary's own re-run, not a claim taken on
    trust."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(GRADUATED_PROBE), "-q"],
        cwd=str(REPO), capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        "the graduated copy does NOT pass when run alone on this tree "
        f"(exit {result.returncode}); see the accompanying finding -- the "
        "held dispatch-commit-count test bakes in a round-specific bound "
        f"that the branch-end round's own dispatch commit now exceeds:\n"
        f"{result.stdout[-4000:]}"
    )


# ---------------------------------------------------------------------------
# Class 2: the memory entry and its README index line.
# ---------------------------------------------------------------------------

def test_memory_entry_frontmatter_description_equals_its_readme_index_line() -> None:
    """The memory entry's frontmatter `description` field must equal the
    prose that follows its title in the README index line, exactly --
    a second, drifted copy of the same sentence is a maintenance trap."""
    assert MEMORY_ENTRY.is_file()
    front = MEMORY_ENTRY.read_text(encoding="utf-8")
    m = re.search(r"^description:\s*(.+)$", front, re.MULTILINE)
    assert m, "no description: line in the memory entry's frontmatter"
    description = m.group(1).strip()

    slug = MEMORY_ENTRY.stem
    readme = MEMORY_README.read_text(encoding="utf-8")
    line_match = re.search(
        rf"^\[{re.escape(slug)}\]\({re.escape(slug)}\.md\) — (.+)$",
        readme, re.MULTILINE,
    )
    assert line_match, f"no README index line found for {slug}"
    readme_text = line_match.group(1).strip()

    assert description == readme_text, (
        "frontmatter description and README index line have drifted apart:\n"
        f"frontmatter: {description!r}\n"
        f"readme:      {readme_text!r}"
    )


def test_memory_integrity_checker_exits_zero() -> None:
    """The repo's own integrity checker must accept the new entry and its
    README line."""
    result = subprocess.run(
        [sys.executable, "scripts/check_loom_memory_integrity.py"],
        cwd=str(REPO), capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        f"check_loom_memory_integrity.py failed: {result.stdout}{result.stderr}"
    )


def test_memory_entry_related_links_all_resolve_to_existing_entries() -> None:
    """Every `[[wikilink]]` in the entry's `Related:` line names a memory
    file that actually exists under docs/loom/memory/ -- a dangling
    reference in a freshly-written entry is a common self-inflicted wound."""
    text = MEMORY_ENTRY.read_text(encoding="utf-8")
    m = re.search(r"^Related:\s*(.+)$", text, re.MULTILINE | re.DOTALL)
    assert m, "no Related: line found in the memory entry"
    names = re.findall(r"\[\[([^\]]+)\]\]", m.group(1))
    assert names, "Related: line names no [[wikilinks]]"
    missing = [n for n in names if not (MEMORY_README.parent / f"{n}.md").is_file()]
    assert missing == [], f"Related: names entries that do not exist: {missing}"


# ---------------------------------------------------------------------------
# Class 3: KICKOFF's package-tests value as the installed checker parses it.
# ---------------------------------------------------------------------------

def _load_installed_checker():
    cache_root = Path.home() / ".claude" / "plugins" / "cache" / "monkey-skills" / "loom-code"
    versions = sorted(
        (p for p in cache_root.glob("*") if p.is_dir() and (p / "scripts" / "loom_checker.py").is_file()),
        key=lambda p: p.name,
    )
    assert versions, f"no installed loom_checker.py found under {cache_root}"
    checker_path = versions[-1] / "scripts" / "loom_checker.py"
    sys.path.insert(0, str(checker_path.parent))
    import importlib
    if "loom_checker" in sys.modules:
        importlib.reload(sys.modules["loom_checker"])
        return sys.modules["loom_checker"], checker_path
    import loom_checker as lc  # noqa
    return lc, checker_path


def test_kickoff_package_tests_value_as_installed_checker_parses_it_matches_grammar() -> None:
    """The installed checker's `kickoff_defaults()` parses KICKOFF's
    `package-tests` line to a value that carries the `--then` group
    separator and contains no bare ` -- ` (which the checker's own value
    grammar reads as the note separator)."""
    lc, checker_path = _load_installed_checker()
    defaults = lc.kickoff_defaults(REPO)
    value = defaults.get("package-tests")
    assert value, f"kickoff_defaults() returned no package-tests key (checker: {checker_path})"
    assert "--then" in value, f"parsed value lacks '--then': {value!r}"
    assert " -- " not in value, f"parsed value still contains a bare ' -- ' separator: {value!r}"


def test_kickoff_package_tests_value_run_verbatim_exits_zero() -> None:
    """The exact value the installed checker parses out of KICKOFF must
    itself exit 0 when run verbatim -- this is the slow probe (~1 min)."""
    lc, _ = _load_installed_checker()
    value = lc.kickoff_defaults(REPO).get("package-tests")
    assert value
    result = subprocess.run(value, cwd=str(REPO), shell=True, capture_output=True, text=True)
    assert result.returncode == 0, (
        f"KICKOFF's own recorded package-tests command exits {result.returncode}, "
        f"not 0, when run verbatim on this tree:\n{result.stdout[-4000:]}\n{result.stderr[-2000:]}"
    )


def test_review_json_recorded_package_tests_probe_still_reproduces() -> None:
    """The `package-tests` probe command already RECORDED in this change's
    own review.json (from the wave-end:1 round, before the `--then` rename)
    must still reproduce its recorded `pass` result on the current tree.
    The recorded command still uses the retired bare `--` separator, which
    the renamed runner no longer treats as a group boundary -- it now folds
    both path groups into one pytest invocation that collects zero tests
    (`no tests ran`, pytest exit 5) instead of running the suite it once
    ran; a stale recorded probe is not evidence that reruns."""
    doc = json.loads(REVIEW_JSON.read_text(encoding="utf-8"))
    recorded = next(
        (p for p in doc.get("probes", []) if p.get("kind") == "package-tests"),
        None,
    )
    assert recorded is not None, "no package-tests probe recorded in review.json"
    command = recorded["command"]
    result = subprocess.run(command, cwd=str(REPO), shell=True, capture_output=True, text=True)
    ran_something = "no tests ran" not in result.stdout.lower()
    assert result.returncode == 0 and ran_something, (
        f"the recorded package-tests command {command!r} does not reproduce "
        f"a real passing run (exit {result.returncode}, ran_something="
        f"{ran_something}); stdout tail: {result.stdout[-500:]!r}"
    )


# ---------------------------------------------------------------------------
# Class 4: runner edge cases after the `--then` rename.
# ---------------------------------------------------------------------------

def _runner_module():
    import importlib
    sys.path.insert(0, str(RUNNER.parent))
    if "run_package_tests" in sys.modules:
        importlib.reload(sys.modules["run_package_tests"])
        return sys.modules["run_package_tests"]
    return importlib.import_module("run_package_tests")


def test_split_groups_bare_dashdash_inside_a_group_passed_through_not_a_separator() -> None:
    """A bare `--` sitting inside a group's argv is an ordinary token
    forwarded to pytest, not a group-splitting separator: only the literal
    token `--then` splits groups now."""
    mod = _runner_module()
    groups = mod.split_groups(["a/", "-q", "--", "-p", "no:cacheprovider", "--then", "b/"])
    assert groups == [["a/", "-q", "--", "-p", "no:cacheprovider"], ["b/"]], groups


def test_split_groups_trailing_dashthen_yields_no_empty_group() -> None:
    """A trailing `--then` with nothing after it produces no empty trailing
    group -- split_groups filters empty groups out."""
    mod = _runner_module()
    groups = mod.split_groups(["a/", "-q", "--then"])
    assert groups == [["a/", "-q"]], groups
    assert [] not in groups


def test_runner_failing_first_group_returns_that_groups_exit_code() -> None:
    """When the first `--then`-separated group's pytest session fails with
    a specific nonzero exit code, the runner propagates that same code
    (not some other nonzero value, and not the second group's code) and the
    second group never runs."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        bad = tmp_path / "bad"; bad.mkdir()
        (bad / "test_bad.py").write_text("def test_bad():\n    assert False\n")
        good = tmp_path / "good"; good.mkdir()
        (good / "test_good.py").write_text(
            "import pathlib\n"
            "def test_good():\n"
            f"    pathlib.Path({str(tmp_path / 'RAN')!r}).write_text('yes')\n"
            "    assert True\n"
        )
        first_group_alone = subprocess.run(
            [sys.executable, str(RUNNER), str(bad), "-q", "-p", "no:cacheprovider"],
            cwd=str(REPO), capture_output=True, text=True,
        )
        combined = subprocess.run(
            [sys.executable, str(RUNNER),
             str(bad), "-q", "-p", "no:cacheprovider",
             "--then", str(good), "-q", "-p", "no:cacheprovider"],
            cwd=str(REPO), capture_output=True, text=True,
        )
        assert combined.returncode == first_group_alone.returncode
        assert combined.returncode != 0
        assert not (tmp_path / "RAN").exists()


# ---------------------------------------------------------------------------
# Class 5: dispatch batching at branch end.
# ---------------------------------------------------------------------------

def test_dispatch_subject_commit_count_bound_by_waves_plus_verdict_rounds() -> None:
    """Acceptance 6's bound recomputed AT BRANCH END, not frozen at an
    earlier round: `chore(loom): dispatch` commits <= waves so far (2: W1,
    W2) + verdict rounds so far (3: wave-end:1 rounds 1-3). The branch-end
    round's own dispatch commit is the one being counted by this very
    invocation, so it is included in `waves so far`/`rounds so far` neither
    -- it is the subject of the count, not a round already closed."""
    confirm_sha = _confirm_intent_sha()
    subjects = subprocess.run(
        ["git", "log", "--format=%s", f"{confirm_sha}..HEAD"],
        cwd=str(REPO), capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    dispatch_commits = [s for s in subjects if s.startswith("chore(loom): dispatch")]
    waves_so_far = 2
    verdict_rounds_so_far = 3
    bound = waves_so_far + verdict_rounds_so_far
    assert len(dispatch_commits) == 5, dispatch_commits
    assert len(dispatch_commits) <= bound, (
        f"{len(dispatch_commits)} dispatch-subject commits exceed the bound "
        f"{bound}: {dispatch_commits}"
    )


def test_every_dispatch_started_precedes_its_first_task_or_round_commit() -> None:
    """Every dispatch[] entry's `started` timestamp precedes the first
    commit that could plausibly follow from it -- for an implementer, its
    first `Task:` trailer commit; for a round role (adversary, blind-runner,
    reviewer), any commit at or after the record commit that carries it.
    Regression guard for the timestamp bug the wave-end round's own
    adversary caught and fixed (639180ea)."""
    doc = json.loads(REVIEW_JSON.read_text(encoding="utf-8"))
    confirm_sha = _confirm_intent_sha()
    checked = 0
    for entry in doc.get("dispatch", []):
        task = entry.get("task", "")
        started = entry.get("started")
        if not task or not started:
            continue
        m = re.match(r"^(W\d+-\d+)", task)
        if not m:
            continue
        task_id = m.group(1)
        commit_iso = subprocess.run(
            ["git", "log", "--format=%cI", f"--grep=^Task: {task_id}$",
             f"{confirm_sha}..HEAD"],
            cwd=str(REPO), capture_output=True, text=True, check=True,
        ).stdout.strip().splitlines()
        if not commit_iso:
            continue
        first_commit_time = commit_iso[-1]
        assert started <= first_commit_time, (
            f"{task}: started {started!r} does not precede its first "
            f"Task-trailer commit {first_commit_time!r}"
        )
        checked += 1
    assert checked >= 5, f"expected at least the 5 W1 tasks checked, got {checked}"


# ---------------------------------------------------------------------------
# Class 6: ship's §4 pre-push checklist run verbatim.
# ---------------------------------------------------------------------------

def _checklist_commands() -> list[str]:
    section = _text_after_heading(SHIP_SKILL, "## 4. Push")
    block = section.split("```", 2)[1]
    return [line for line in block.splitlines() if line.strip()]


@pytest.mark.parametrize("index", range(9))
def test_ship_checklist_command_exits_zero_on_this_tree(index: int) -> None:
    """Every fenced command of ship's §4 pre-push checklist, run verbatim
    from the repo root, must exit 0 on this tree -- the mechanisms baseline
    line resolves `origin/main` directly since the flag itself accepts a
    ref name (no substitution needed)."""
    commands = _checklist_commands()
    assert len(commands) == 9, f"expected 9 checklist lines, found {len(commands)}: {commands}"
    command = commands[index]
    result = subprocess.run(command, cwd=str(REPO), shell=True, capture_output=True, text=True)
    assert result.returncode == 0, (
        f"checklist line {index} ({command!r}) exited {result.returncode} "
        f"on this tree:\n{result.stdout[-3000:]}\n{result.stderr[-1000:]}"
    )


def test_ship_checklist_doc_citations_line_is_the_pipeline_form() -> None:
    """The checklist's doc-citations line is the full `git ls-files | grep |
    xargs` pipeline, matching CI's own command, not a bare invocation."""
    commands = _checklist_commands()
    line = next(c for c in commands if "check_doc_citations.py" in c)
    assert "git ls-files" in line and "xargs" in line, line


# ---------------------------------------------------------------------------
# Class 7: word caps on the touched station files.
# ---------------------------------------------------------------------------

def test_word_caps_hold_for_every_station_file_touched_this_change() -> None:
    """adversary.md sits at exactly 600 words (its hard cap); reviewer.md,
    review/SKILL.md and ship/SKILL.md sit at or under their caps
    (1460/4500/3500); build/SKILL.md sits under its 3750 whole-file cap.
    Body word counts exclude YAML frontmatter, the same method
    test_reviewer_agent_single_contract.py uses."""
    reviewer_words = len(_body_of(REVIEWER_MD.read_text(encoding="utf-8")).split())
    adversary_words = len(_body_of(ADVERSARY_MD.read_text(encoding="utf-8")).split())
    review_skill_words = len(_body_of(REVIEW_SKILL.read_text(encoding="utf-8")).split())
    ship_skill_words = len(_body_of(SHIP_SKILL.read_text(encoding="utf-8")).split())
    build_skill_words = len(BUILD_SKILL.read_text(encoding="utf-8").split())

    assert adversary_words == 600, adversary_words
    assert reviewer_words <= 1460, reviewer_words
    assert review_skill_words <= 4500, review_skill_words
    assert ship_skill_words <= 3500, ship_skill_words
    assert build_skill_words <= 3750, build_skill_words


if __name__ == "__main__":  # pragma: no cover
    sys.exit(pytest.main([__file__, "-q"]))
