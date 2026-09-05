"""Adversarial probes for wave-end:1 of
2026-09-05-review-sees-complexity-and-process-cost -- retargeted after the
fix round (`fix:wave-end:1`) at HEAD `baf36c70` to assert the CORRECT
invariant for each finding: green on the fixed tree, red on the tree before
that fix round (`e586f195`, the adversary's first probe commit).

Scope: the range from the intent-confirmation commit (subject
"docs(loom): intent 2026-09-05-review-sees-complexity-and-process-cost
confirmed") to HEAD. Commits are located by subject/trailer, never by a
hardcoded sha, except where a test needs to name the specific pre-fix
commit it regresses against (`e586f195`, the adversary's own prior probe
commit, cited by sha because it is this file's own history, not a station
artifact).

Each test is independently re-runnable: `python3 -m pytest
docs/loom/2026-09-05-review-sees-complexity-and-process-cost/evidence/probes/test_abuse_complexity_wave_end.py -q`
from the repo root.
"""
from __future__ import annotations

import importlib.util
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

# Several of the station-text test modules this file loads (via
# _load_module, or "from prose_pin import ...") themselves import the
# shared matcher from loom-code/scripts/prose_pin.py at THEIR module top.
# That import must resolve whether this file runs whole or with `-k`
# selecting only a subset -- the checker re-runs each recorded probe
# command alone at push -- so the path is inserted here, unconditionally,
# rather than inside whichever test happened to need it first.
sys.path.insert(0, str(REPO / "loom-code" / "scripts"))

REVIEW_JSON = REPO / "docs" / "loom" / "2026-09-05-review-sees-complexity-and-process-cost" / "review.json"
TEMPLATE = REPO / "loom-code" / "contract" / "templates" / "review.json"
CODEX_TEMPLATE = REPO / ".codex" / "hooks" / "contract" / "templates" / "review.json"
RUNNER = REPO / "scripts" / "run_package_tests.py"
SHIP_SKILL = REPO / "loom-code" / "skills" / "ship" / "SKILL.md"
BUILD_SKILL = REPO / "loom-code" / "skills" / "build" / "SKILL.md"
CHECKER = REPO / "loom-code" / "scripts" / "loom_checker.py"
PROSE_PIN = REPO / "loom-code" / "scripts" / "prose_pin.py"
MECHANISMS = REPO / "docs" / "loom" / "evidence" / "mechanisms.yaml"

NEGATION_MODULE_PATHS = {
    "review_station": REPO / "loom-code" / "scripts" / "test_review_station_text.py",
    "ship_station": REPO / "loom-code" / "scripts" / "test_ship_station_text.py",
    "lenses_deletion_first": REPO / "loom-code" / "scripts" / "test_lenses_deletion_first.py",
    "prose_pin_rule": REPO / "loom-code" / "scripts" / "test_prose_pin_rule_text.py",
    "build_station": REPO / "loom-code" / "scripts" / "test_build_station_text.py",
}


def text_after_heading(path: Path, heading: str) -> str:
    """Return the text of `path` from `heading` up to (not including) the
    next top-level `## ` heading -- so a search for a fenced code block
    only sees the block that actually sits under that heading, not an
    earlier fence elsewhere in the file."""
    text = path.read_text(encoding="utf-8")
    start = text.index(heading)
    rest = text[start + len(heading):]
    cut = re.search(r"\n## ", rest)
    return rest[: cut.start()] if cut else rest


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(f"_adv_probe_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _confirm_intent_sha() -> str:
    """Locate the intent-confirmation commit by subject. That commit lived
    only on 2026-09-05-review-sees-complexity-and-process-cost's own local
    development branch and was squash-merged (PR #794, loom-code 1.5.0,
    merge commit 43e32034) -- it is absent from every other clone's
    history, including CI on main. Callers that depend on it skip rather
    than fail when it is not found, following the precedent in
    test_probes_positioning.py / test_probes_positioning_branch_end.py
    (pytest.skip when a probe's host precondition is absent)."""
    out = subprocess.run(
        ["git", "log", "--all", "--format=%H",
         "--grep=^docs(loom): intent 2026-09-05-review-sees-complexity-and-process-cost confirmed$"],
        cwd=str(REPO), capture_output=True, text=True, check=True,
    ).stdout.strip().splitlines()
    if not out:
        pytest.skip(
            "intent-confirmation commit for "
            "2026-09-05-review-sees-complexity-and-process-cost is not in "
            "this clone's history (it lived on the change's local branch "
            "and was squash-merged); this probe replays that change's own "
            "dispatch history and has nothing to read here"
        )
    return out[0]


# ---------------------------------------------------------------------------
# Fixed: the review.json template (and its Codex mirror) declare `cost`
# exactly once each; before the fix round they carried it twice
# (fixed by commit 0dc680c1, "one cost block in the review.json template").
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("template_path", [TEMPLATE, CODEX_TEMPLATE], ids=["loom-code", "codex-mirror"])
def test_review_json_template_declares_cost_exactly_once(template_path: Path) -> None:
    """FIXED (0dc680c1): both `contract/templates/review.json` and its Codex
    mirror under `.codex/hooks/contract/templates/review.json` carry the
    top-level `"cost"` key exactly once. Before the fix, the loom-code
    template carried it twice (a dead `hours_plan_to_pr: 0` block silently
    shadowed by json.loads picking the second occurrence) -- the adversary's
    prior probe commit (e586f195) has this test asserting the same
    invariant and failing on that earlier tree."""
    assert template_path.is_file(), f"{template_path} does not exist"
    text = template_path.read_text(encoding="utf-8")
    top_level_hits = re.findall(r'^\s{2}"cost":', text, re.MULTILINE)
    assert len(top_level_hits) == 1, (
        f"{template_path.relative_to(REPO)} declares the top-level `cost` "
        f"key {len(top_level_hits)} times (expected exactly 1)"
    )


def test_review_json_template_cost_block_parses_to_declared_shape() -> None:
    """FIXED (0dc680c1): with the duplicate gone, the template's single
    `cost` object parses to the declared null-hours shape (nothing shadows
    it anymore)."""
    doc = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    assert doc["cost"] == {
        "rounds": 0, "dispatches": 0, "cap_changes": [], "hours_plan_to_pr": None,
    }


# ---------------------------------------------------------------------------
# Fixed: `artifact:review.cost` is registered in the mechanisms ledger, with
# a working eval -- fixed alongside the duplicate-key fix (0dc680c1) and its
# CHANGELOG budget-exception line (0274d550).
# ---------------------------------------------------------------------------

def test_mechanisms_yaml_registers_artifact_review_cost() -> None:
    """FIXED (0dc680c1 + 0274d550): `docs/loom/evidence/mechanisms.yaml`
    registers `artifact:review.cost` in the `contract` class, with an
    `eval:` that names a real, collectible pytest node id. Before the fix
    round this id was absent -- the `cost` field the review.json template
    carries had no mechanism-population entry at all."""
    assert MECHANISMS.is_file()
    text = MECHANISMS.read_text(encoding="utf-8")
    m = re.search(
        r'-\s*\{id:\s*"artifact:review\.cost",\s*class:\s*(\S+),\s*eval:\s*"([^"]+)"',
        text,
    )
    assert m, "docs/loom/evidence/mechanisms.yaml has no artifact:review.cost entry"
    assert m.group(1).rstrip(",") == "contract", (
        f"artifact:review.cost is class {m.group(1)!r}, expected contract"
    )
    eval_ref = m.group(2)
    assert "::" in eval_ref, f"eval {eval_ref!r} does not name a test node id"
    node_path, node_name = eval_ref.split("::", 1)
    node_file = REPO / node_path
    assert node_file.is_file(), f"eval target {node_path} does not exist"
    collected = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", eval_ref],
        cwd=str(REPO), capture_output=True, text=True,
    )
    assert collected.returncode == 0 and node_name in collected.stdout, (
        f"eval {eval_ref!r} does not collect: {collected.stdout}{collected.stderr}"
    )


# ---------------------------------------------------------------------------
# Fixed: dispatch[] `started` timestamps now precede the first commit
# carrying each task's `Task:` trailer (0dc680c1 / 639180ea, "dispatch
# started timestamps corrected to their record commits").
# ---------------------------------------------------------------------------

def test_dispatch_started_timestamp_accepted_when_impossible_still_documents_gap() -> None:
    """Unfixed by design, and stated as a note rather than a finding per the
    coordinator: `push.reviewer-ne-implementer` (loom_checker.parse_dispatch
    / check_reviewer_ne_implementer) still only checks that `started` is
    non-empty -- it never cross-checks the value against git. A forged
    review.json with an impossible ordering (reviewer 'started' in 1999,
    implementer 'started' in 2099) is still accepted with zero findings.
    Kept here as a live record of that gap, not a regression: the fix round
    corrected the RECORD's own timestamps (next test), and left the checker
    unchanged, out of this change's scope (no checker rule added)."""
    sys.path.insert(0, str(CHECKER.parent))
    import loom_checker as lc  # noqa: E402

    forged = {
        "dispatch": [
            {"task": "W1-01", "role": "implementer", "agent_id": "a1",
             "model": "sonnet", "started": "2099-01-01T00:00:00+08:00"},
            {"task": "wave-end:1", "role": "adversary", "agent_id": "a2",
             "model": "sonnet", "started": "1999-01-01T00:00:00+08:00"},
        ],
        "verdicts": [],
    }
    implementers, reviewers, err = lc.parse_dispatch(forged)
    assert err is None
    findings = lc.check_reviewer_ne_implementer(forged, implementers, reviewers, err)
    assert findings == [], (
        "expected the checker to still accept the forged dispatch record "
        "(this remains an accepted, out-of-scope gap, not a regression)"
    )


def test_every_w1_implementer_started_precedes_its_first_task_commit() -> None:
    """FIXED (639180ea): every W1-01..W1-05 implementer dispatch entry's
    `started` timestamp now precedes (or equals the record-commit instant
    immediately before) the first commit carrying that task's `Task:`
    trailer. Before the fix, all five carried `started:
    2026-09-06T10:30:00+08:00` -- a full calendar day AFTER their own
    `Task:` commits (2026-09-05). Bound to this change's own branch
    history via `_confirm_intent_sha()`: skips (not fails) on any clone
    that lacks that branch's squash-merged intent-confirmation commit."""
    assert REVIEW_JSON.is_file(), f"{REVIEW_JSON} does not exist on this branch"
    doc = json.loads(REVIEW_JSON.read_text(encoding="utf-8"))
    confirm_sha = _confirm_intent_sha()
    checked = 0
    for task in ("W1-01", "W1-02", "W1-03", "W1-04", "W1-05"):
        started = next(
            (e["started"] for e in doc.get("dispatch", [])
             if e.get("task") == task and e.get("role") == "implementer"),
            None,
        )
        assert started is not None, f"no {task} implementer dispatch entry found"

        commit_iso = subprocess.run(
            ["git", "log", "--format=%cI", f"--grep=^Task: {task}$",
             f"{confirm_sha}..HEAD"],
            cwd=str(REPO), capture_output=True, text=True, check=True,
        ).stdout.strip().splitlines()
        assert commit_iso, f"no commit on this range carries 'Task: {task}'"
        # git log lists newest first; the FIRST commit carrying the trailer
        # is the last line here.
        first_commit_time = commit_iso[-1]

        assert started <= first_commit_time, (
            f"{task}: started {started!r} does not precede its first "
            f"Task-trailer commit {first_commit_time!r}"
        )
        checked += 1
    assert checked == 5


# ---------------------------------------------------------------------------
# Fixed: the shared negation matcher (loom-code/scripts/prose_pin.py) now
# catches "cannot"/"without"/"neither"/"nobody"/"nor" (54c675c9);
# "none"/"nothing" deliberately excluded per the coordinator (used as
# quantifiers in two pinned affirmative sentences).
# ---------------------------------------------------------------------------

def test_prose_pin_module_exists_and_is_the_single_source() -> None:
    """FIXED (54c675c9): `loom-code/scripts/prose_pin.py` exists and exports
    `NEGATION_RE`/`has_negation`; the five station-text test modules import
    `NEGATION_RE` from it rather than each carrying a private literal."""
    assert PROSE_PIN.is_file()
    mod = _load_module("prose_pin_module", PROSE_PIN)
    assert hasattr(mod, "NEGATION_RE")
    assert hasattr(mod, "has_negation")
    for name, path in NEGATION_MODULE_PATHS.items():
        text = path.read_text(encoding="utf-8")
        assert "from prose_pin import" in text, (
            f"{name} ({path.relative_to(REPO)}) does not import the shared "
            "prose_pin matcher"
        )


@pytest.mark.parametrize("module_name", sorted(NEGATION_MODULE_PATHS))
def test_shared_negation_matcher_now_catches_cannot_and_without(module_name: str) -> None:
    """FIXED (54c675c9): all five station-text modules now reject "cannot"
    and "without" as negation -- previously (e586f195's probe) all five
    returned False (no negation detected) for both words."""
    path = NEGATION_MODULE_PATHS[module_name]
    mod = _load_module(module_name, path)
    has_negation = getattr(mod, "_has_negation")
    for negated_word_sentence in (
        "This cannot be undone once committed.",
        "It is done without exception, always.",
    ):
        assert has_negation(negated_word_sentence) is True, (
            f"{module_name}._has_negation still misses a negation word in "
            f"{negated_word_sentence!r}"
        )


def test_shared_negation_matcher_deliberately_still_permits_none_and_nothing() -> None:
    """Documents the coordinator's explicit design choice, not a hole: `none`
    and `nothing` stay OUT of the widened matcher because two pinned
    affirmative sentences use them as quantifiers ("a reader who raised
    none keeps its previous PASS"; "that one intent line, nothing more").
    Widening to catch them would break those two legitimate pins, so this
    probe pins the deliberate exclusion rather than treating it as a
    finding."""
    mod = _load_module("prose_pin_module", PROSE_PIN)
    for still_permitted in (
        "A reader who raised none keeps its previous PASS.",
        "That one intent line, nothing more.",
    ):
        assert mod.has_negation(still_permitted) is False, (
            f"expected {still_permitted!r} to still read as negation-free "
            "(none/nothing are deliberately excluded quantifier words)"
        )


def test_hostile_rewrite_of_build_stations_pinned_sentence_now_rejected() -> None:
    """FIXED (54c675c9): the end-to-end hostile rewrite of build/SKILL.md's
    real pinned sentence ("appended once"/"committed once"/"first
    dispatch") using "cannot" to state the OPPOSITE of the rule no longer
    matches the pinned-sentence filter -- e586f195's probe showed it did,
    before the shared matcher widened."""
    mod = _load_module("build_station", NEGATION_MODULE_PATHS["build_station"])
    hostile_paragraph = (
        "This wave sadly cannot have its implementer records appended once "
        "and committed once before the wave first dispatch, contrary to "
        "the old per-task behaviour."
    )
    sentences = mod._flat_sentences(hostile_paragraph)
    hits = [
        s for s in sentences
        if "appended once" in s.lower()
        and "committed once" in s.lower()
        and "first dispatch" in s.lower()
        and not mod._has_negation(s)
    ]
    assert hits == [], (
        f"expected the hostile 'cannot' rewrite to be rejected now that the "
        f"shared matcher catches it; still matched: {hits}"
    )


def test_build_stations_real_pinned_sentence_still_accepted() -> None:
    """Regression guard alongside the previous test: the widened matcher
    must still accept the REAL (non-hostile) pinned sentence in
    build/SKILL.md -- a wider negation regex that also ate legitimate
    affirmative text would trade one hole for another."""
    sys.path.insert(0, str(REPO / "loom-code" / "scripts"))
    from prose_pin import has_negation  # noqa: E402
    mod = _load_module("build_station", NEGATION_MODULE_PATHS["build_station"])
    paragraph = mod._perwave_commit_paragraph()
    flat = " ".join(paragraph.split())
    hits = [
        s for s in mod._flat_sentences(flat)
        if "appended once" in s.lower()
        and "committed once" in s.lower()
        and "first dispatch" in s.lower()
        and not has_negation(s)
    ]
    assert hits, (
        "the real (non-hostile) pinned sentence in build/SKILL.md §3 no "
        "longer matches its own test's filter after the matcher widened"
    )


# ---------------------------------------------------------------------------
# Fixed: ship's §4 doc-citations checklist line now carries the full
# `git ls-files | grep | xargs` pipeline (2e0491c8).
# ---------------------------------------------------------------------------

def test_ship_checklist_doc_citations_line_carries_the_ci_pipeline() -> None:
    """FIXED (2e0491c8): the checklist line for doc-citations now IS the
    full `git ls-files '*.md' | grep -E ... | xargs python3
    loom-code/scripts/check_doc_citations.py` pipeline, matching the CI
    job's actual command rather than a bare invocation with a comment."""
    section = text_after_heading(SHIP_SKILL, "## 4. Push")
    checklist_block = section.split("```", 2)[1]
    doc_citation_lines = [
        line for line in checklist_block.splitlines()
        if "check_doc_citations.py" in line
    ]
    assert doc_citation_lines, "no check_doc_citations.py line in ship's §4 checklist"
    line = doc_citation_lines[0]
    assert "git ls-files" in line and "xargs" in line, (
        f"checklist line still lacks the CI file-selection pipeline: {line!r}"
    )


def test_ship_checklist_doc_citations_line_run_verbatim_exits_zero() -> None:
    """FIXED (2e0491c8): copying the checklist's printed line and running it
    verbatim now exits 0 on this tree -- before the fix it always exited 2
    (a bare invocation with no file arguments), regardless of repo health."""
    section = text_after_heading(SHIP_SKILL, "## 4. Push")
    checklist_block = section.split("```", 2)[1]
    line = next(
        line for line in checklist_block.splitlines()
        if "check_doc_citations.py" in line
    )
    result = subprocess.run(
        line, cwd=str(REPO), shell=True, capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        f"expected the checklist's own printed pipeline to exit 0; got "
        f"{result.returncode}: stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_ci_workflow_doc_citations_step_still_passes_on_this_tree() -> None:
    """Control case, unchanged: the ACTUAL CI command exits 0 on this tree
    (confirms the previous test's green is not a repo-health accident)."""
    result = subprocess.run(
        "git ls-files '*.md' | grep -E "
        r"'^(docs/loom/[^/]+\.md|docs/loom/intent/|loom-(code|design|workflow)/(skills|agents|references|contract)/)' "
        "| xargs python3 loom-code/scripts/check_doc_citations.py",
        cwd=str(REPO), shell=True, capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        f"the real CI doc-citations command failed on this tree (exit "
        f"{result.returncode}); stdout={result.stdout!r} stderr={result.stderr!r}"
    )


# ---------------------------------------------------------------------------
# Fixed: scripts/run_package_tests.py refuses zero groups with exit 2
# (0dc680c1).
# ---------------------------------------------------------------------------

def test_runner_empty_argv_exits_nonzero_refusing_zero_groups() -> None:
    """FIXED (0dc680c1): invoking the runner with NO arguments now exits 2
    with a stderr message -- before the fix it silently exited 0 having
    run zero pytest sessions."""
    result = subprocess.run(
        [sys.executable, str(RUNNER)], cwd=str(REPO), capture_output=True, text=True,
    )
    assert result.returncode == 2, (
        f"expected exit 2 refusing zero groups; got {result.returncode}"
    )
    assert result.stderr.strip(), "expected a stderr message explaining the refusal"


def test_runner_thenonly_argv_exits_nonzero_refusing_zero_groups() -> None:
    """FIXED (0dc680c1, retargeted for 43d8eb88's `--then` separator): an
    argv of only `--then` (every group empty after splitting) also now
    exits 2 -- the same silent-success hole (test_runner_empty_argv...)
    reached a different way, closed the same way. The separator itself
    changed from a bare `--` to `--then` (43d8eb88) because `--` collides
    with KICKOFF's ` -- ` note-separator grammar; this test names the
    current separator token, not the retired one."""
    result = subprocess.run(
        [sys.executable, str(RUNNER), "--then"], cwd=str(REPO), capture_output=True, text=True,
    )
    assert result.returncode == 2
    assert result.stderr.strip()


def test_runner_bare_dashdash_no_longer_a_group_separator() -> None:
    """Regression guard for the separator change (43d8eb88): a bare `--` is
    now an ordinary token passed through to pytest as part of the current
    group, not a group-splitting separator -- `split_groups` must return
    exactly one group containing it, not split on it."""
    sys.path.insert(0, str(REPO / "scripts"))
    import importlib
    if "run_package_tests" in sys.modules:
        importlib.reload(sys.modules["run_package_tests"])
        runner_mod = sys.modules["run_package_tests"]
    else:
        runner_mod = importlib.import_module("run_package_tests")
    groups = runner_mod.split_groups(["a/", "-q", "--", "-p", "no:cacheprovider"])
    assert groups == [["a/", "-q", "--", "-p", "no:cacheprovider"]], (
        f"expected a bare '--' to stay inside one group, got {groups}"
    )


def test_runner_still_runs_a_real_nonempty_group_and_exits_zero() -> None:
    """Regression guard: the zero-groups refusal must not have broken the
    ordinary one-group case."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "test_ok.py").write_text("def test_ok():\n    assert True\n")
        result = subprocess.run(
            [sys.executable, str(RUNNER), str(tmp_path), "-q", "-p", "no:cacheprovider"],
            cwd=str(REPO), capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr


def test_runner_failing_first_group_shortcircuits_second_group() -> None:
    """Unchanged (not part of this fix round, per the coordinator): when the
    first `--then`-separated group fails, the runner returns immediately --
    the second group's pytest session never runs. Kept as a live record,
    not a regression: the runner's own docstring never claimed otherwise.
    Retargeted for 43d8eb88's separator: uses `--then` where this test
    previously used a bare `--`, which is no longer a group separator."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        bad = tmp_path / "bad"; bad.mkdir()
        (bad / "test_bad.py").write_text("def test_bad():\n    assert False\n")
        good = tmp_path / "good"; good.mkdir()
        (good / "test_good.py").write_text(
            "import pathlib\n"
            "def test_good():\n"
            f"    pathlib.Path({str(tmp_path / 'SECOND_GROUP_RAN')!r}).write_text('yes')\n"
            "    assert True\n"
        )
        marker = tmp_path / "SECOND_GROUP_RAN"
        result = subprocess.run(
            [sys.executable, str(RUNNER),
             str(bad), "-q", "-p", "no:cacheprovider",
             "--then", str(good), "-q", "-p", "no:cacheprovider"],
            cwd=str(REPO), capture_output=True, text=True,
        )
        assert result.returncode != 0
        assert not marker.exists(), (
            "expected the second group to NOT have run after the first "
            "group failed"
        )


# ---------------------------------------------------------------------------
# Held (unchanged, no break found): gate-block reordering, word caps,
# dispatch commit-count bound.
# ---------------------------------------------------------------------------

def test_review_skill_gate_blocks_remain_paired_and_named_after_reorder() -> None:
    """Held: both `<!-- gate: ... -->` / `<!-- /gate -->` pairs the file
    declares are still balanced, and the two ids the W1-02 §2 reorder
    touched are each still present exactly once."""
    text = (REPO / "loom-code" / "skills" / "review" / "SKILL.md").read_text(encoding="utf-8")
    opens = re.findall(r"<!--\s*gate:\s*([A-Za-z0-9._-]+)\s*-->", text)
    closes = len(re.findall(r"<!--\s*/gate\s*-->", text))
    assert len(opens) == closes
    for gate_id in ("review.two-fresh-reviewers", "review.reviewer-not-implementer"):
        assert opens.count(gate_id) == 1


def _body_of(text: str) -> str:
    match = re.match(r"^---\n.*?\n---\n", text, re.DOTALL)
    return text[match.end():] if match else text


def test_word_caps_hold_for_every_touched_station_file() -> None:
    """Held: reviewer.md 1460, adversary.md exactly 600, review/SKILL.md
    4500, ship/SKILL.md 3500, build/SKILL.md whole-file 3750 -- all within
    cap on this tree."""
    reviewer_md = REPO / "loom-code" / "agents" / "reviewer.md"
    adversary_md = REPO / "loom-code" / "agents" / "adversary.md"
    review_skill = REPO / "loom-code" / "skills" / "review" / "SKILL.md"

    reviewer_words = len(_body_of(reviewer_md.read_text(encoding="utf-8")).split())
    adversary_words = len(_body_of(adversary_md.read_text(encoding="utf-8")).split())
    review_skill_words = len(_body_of(review_skill.read_text(encoding="utf-8")).split())
    ship_skill_words = len(_body_of(SHIP_SKILL.read_text(encoding="utf-8")).split())
    build_skill_words = len(BUILD_SKILL.read_text(encoding="utf-8").split())

    assert reviewer_words <= 1460
    assert adversary_words == 600
    assert review_skill_words <= 4500
    assert ship_skill_words <= 3500
    assert build_skill_words <= 3750


def _distinct_wave_ids(confirm_sha: str) -> set[str]:
    """Every distinct `W<n>` prefix carried by a `Task:` trailer on this
    branch -- the wave count, recomputed from git rather than frozen at
    whatever wave existed when a probe was last written."""
    body = subprocess.run(
        ["git", "log", "--format=%B", f"{confirm_sha}..HEAD"],
        cwd=str(REPO), capture_output=True, text=True, check=True,
    ).stdout
    return set(re.findall(r"^Task: (W\d+)-", body, re.MULTILINE))


def _verdict_rounds_so_far(review_json_path: Path) -> int:
    """The count of verdict rounds so far: the highest `round` among
    review.json's real verdict entries (the schema's own template entry,
    with its literal `<agent id>`/pipe-joined placeholder scope, is not a
    real entry and is excluded), plus one more when a `dispatch[]` entry
    names a checkpoint scope (`branch-end`, or `wave-end:<n>`) that no
    verdict entry has scored yet -- the round that dispatch just opened."""
    doc = json.loads(review_json_path.read_text(encoding="utf-8"))
    real_verdicts = [
        v for v in doc.get("verdicts", [])
        if isinstance(v.get("round"), int)
        and "|" not in str(v.get("scope", ""))
        and "<" not in str(v.get("reviewer", ""))
    ]
    max_round = max((v["round"] for v in real_verdicts), default=0)
    verdicted_scopes = {v.get("scope") for v in real_verdicts}
    checkpoint_scopes = {
        entry["task"] for entry in doc.get("dispatch", [])
        if entry.get("task") == "branch-end" or re.fullmatch(r"wave-end:\d+", entry.get("task", ""))
    }
    opened_without_verdict = any(scope not in verdicted_scopes for scope in checkpoint_scopes)
    return max_round + (1 if opened_without_verdict else 0)


def test_dispatch_commit_count_within_waves_plus_rounds_bound() -> None:
    """Held: Acceptance 6's bound (dispatch-subject commits <= waves so far
    + review rounds so far), recomputed from git and review.json at
    whatever round this actually runs in -- never a number frozen at the
    round this test was written in, which the very next round would
    outgrow. Bound to this change's own branch history via
    `_confirm_intent_sha()`: skips (not fails) on any clone that lacks
    that branch's squash-merged intent-confirmation commit."""
    confirm_sha = _confirm_intent_sha()
    subjects = subprocess.run(
        ["git", "log", "--format=%s", f"{confirm_sha}..HEAD"],
        cwd=str(REPO), capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    dispatch_commits = [s for s in subjects if s.startswith("chore(loom): dispatch")]
    waves_so_far = len(_distinct_wave_ids(confirm_sha))
    rounds_so_far = _verdict_rounds_so_far(REVIEW_JSON)
    bound = waves_so_far + rounds_so_far
    assert len(dispatch_commits) <= bound, (
        f"{len(dispatch_commits)} dispatch-subject commits exceed the bound "
        f"{bound} ({waves_so_far} waves + {rounds_so_far} rounds): {dispatch_commits}"
    )


if __name__ == "__main__":  # pragma: no cover
    sys.exit(pytest.main([__file__, "-q"]))
