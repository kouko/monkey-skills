"""Adversarial probes for wave-end:1 of
2026-09-05-review-sees-complexity-and-process-cost.

Scope: the delta between the intent-confirmation commit
(subject "docs(loom): intent 2026-09-05-review-sees-complexity-and-process-cost
confirmed") and the tip of this branch at the time this file was written
(subject "chore(loom): dispatch review wave-end:1 -- adversary, blind-runner,
two readers in one record commit"). Commits are located by subject/trailer,
never by a hardcoded sha -- `git log --grep` below is how a clean checkout
finds the same range this file was written against.

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

REVIEW_JSON = REPO / "docs" / "loom" / "2026-09-05-review-sees-complexity-and-process-cost" / "review.json"
TEMPLATE = REPO / "loom-code" / "contract" / "templates" / "review.json"
RUNNER = REPO / "scripts" / "run_package_tests.py"
SHIP_SKILL = REPO / "loom-code" / "skills" / "ship" / "SKILL.md"
BUILD_SKILL = REPO / "loom-code" / "skills" / "build" / "SKILL.md"
CHECKER = REPO / "loom-code" / "scripts" / "loom_checker.py"

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
    out = subprocess.run(
        ["git", "log", "--all", "--format=%H",
         "--grep=^docs(loom): intent 2026-09-05-review-sees-complexity-and-process-cost confirmed$"],
        cwd=str(REPO), capture_output=True, text=True, check=True,
    ).stdout.strip().splitlines()
    assert out, "cannot locate the intent-confirmation commit by subject"
    return out[0]


# ---------------------------------------------------------------------------
# Class 3 (cost schema): the review.json template declares `cost` TWICE
# ---------------------------------------------------------------------------

def test_review_json_template_duplicate_cost_key_shadows_first_value() -> None:
    """The template contract/templates/review.json contains the literal key
    `"cost"` twice as a top-level JSON object member (once near the head with
    `hours_plan_to_pr: 0`, once near the tail -- next to `dispatch` -- with
    `hours_plan_to_pr: null`). JSON object literals with a duplicate key are
    not rejected by Python's `json.loads`; the second occurrence silently
    wins and the first is dead text that no reader or diff tool flags,
    because a textual grep for `"cost"` still finds "it" (there are two).
    This is a real defect in the artifact under review, not a hypothetical:
    it is reproduced here by counting literal occurrences of the top-level
    key in the file text."""
    text = TEMPLATE.read_text(encoding="utf-8")
    # Only count '"cost":' at low indentation (2 spaces), i.e. top-level
    # object members, not any nested key that happens to be named cost.
    top_level_hits = re.findall(r'^\s{2}"cost":', text, re.MULTILINE)
    assert len(top_level_hits) == 1, (
        f"contract/templates/review.json declares the top-level `cost` key "
        f"{len(top_level_hits)} times (expected 1) -- one occurrence is a "
        "dead value silently shadowed by json.loads, invisible to a plain "
        "grep for the key name"
    )


def test_review_json_template_parses_to_the_second_costs_hours_value() -> None:
    """Self-test pinning what the duplicate actually does at parse time: the
    live document resolves to the SECOND `cost` object's `hours_plan_to_pr`
    (null), silently discarding the first object's `hours_plan_to_pr: 0`."""
    doc = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    assert doc["cost"]["hours_plan_to_pr"] is None, (
        "expected the parsed document to keep the LAST cost object's value "
        "(null) -- if this changes, the duplicate-key shadowing behavior "
        "this probe documents has changed shape and needs re-review"
    )


# ---------------------------------------------------------------------------
# Class: forge an artifact the gate trusts -- dispatch[] `started` timestamps
# ---------------------------------------------------------------------------

def test_dispatch_started_timestamp_accepted_even_when_impossible() -> None:
    """`push.reviewer-ne-implementer` (loom_checker.parse_dispatch /
    check_reviewer_ne_implementer) requires every dispatch[] entry to carry a
    non-empty `started` field (DISPATCH_KEYS), but never checks that value
    against git history. A forged review.json whose reviewer 'started'
    (1999) before its implementer 'started' (2099) -- an impossible
    ordering -- is accepted with zero findings. Reproduced by calling the
    actual checker functions, not by reading the code."""
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
        "expected the checker to accept the forged dispatch record (this is "
        "the hole, not the fix): got findings instead, meaning the checker "
        "now validates `started` against something -- re-review this probe"
    )


def test_this_changes_own_reviewjson_started_timestamps_postdate_their_commits() -> None:
    """The dispatch[] entries this very change wrote for W1-01..W1-05 record
    `started: 2026-09-06T10:30:00+08:00` -- a full calendar day AFTER the
    commit that carries `Task: W1-01` (2026-09-05, per `git log --format=%ci`
    on the range from the intent-confirmation commit). A dispatch record
    whose `started` field postdates the work it claims to have started is
    not evidence of ordering; it is exactly the unchecked field the
    previous probe shows the gate never verifies. This is read from THIS
    branch's own real review.json, not a synthetic example."""
    assert REVIEW_JSON.is_file(), f"{REVIEW_JSON} does not exist on this branch"
    doc = json.loads(REVIEW_JSON.read_text(encoding="utf-8"))
    started_for_w1_01 = next(
        (e["started"] for e in doc.get("dispatch", [])
         if e.get("task") == "W1-01" and e.get("role") == "implementer"),
        None,
    )
    assert started_for_w1_01 is not None, "no W1-01 implementer dispatch entry found"

    commit_iso = subprocess.run(
        ["git", "log", "--format=%cI", "--grep=^Task: W1-01$",
         f"{_confirm_intent_sha()}..HEAD"],
        cwd=str(REPO), capture_output=True, text=True, check=True,
    ).stdout.strip().splitlines()
    assert commit_iso, "no commit on this range carries 'Task: W1-01'"
    commit_time = commit_iso[0]

    # ISO-8601 strings with the same UTC-offset format sort lexically the
    # same as chronologically for this repo's timestamps (both +08:00).
    assert started_for_w1_01 > commit_time, (
        f"expected to reproduce the anomaly (started {started_for_w1_01!r} "
        f"after commit {commit_time!r}); if this now sorts the other way, "
        "the anomaly this probe documents has been fixed -- re-review "
        "whether it still needs recording as a finding"
    )


# ---------------------------------------------------------------------------
# Class 1 (prose pins): the shared negation regex has a hole -- "cannot",
# "without", "nothing" evade it in all five modules that copy it verbatim.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("module_name", sorted(NEGATION_MODULE_PATHS))
def test_shared_negation_matcher_misses_cannot_without_nothing(module_name: str) -> None:
    """`_NEGATION_RE = re.compile(r"\\b(?:not|never|no)\\b|n't", re.IGNORECASE)`
    is copy-pasted verbatim into five test modules that each pin a sentence
    of prose. None of the five catch "cannot" (word-boundary "not" never
    appears -- "cannot" has no boundary before "not"), "without", or
    "nothing" as negation. A hostile rewrite using any of those three words
    passes `_has_negation() == False`, i.e. is accepted as 'affirmative'."""
    path = NEGATION_MODULE_PATHS[module_name]
    mod = _load_module(module_name, path)
    has_negation = getattr(mod, "_has_negation")
    for hostile_sentence in (
        "This cannot be undone once committed.",
        "It is done without exception, always.",
        "Nothing changes the outcome here.",
    ):
        assert has_negation(hostile_sentence) is False, (
            f"{module_name}._has_negation unexpectedly caught a negation "
            f"word in {hostile_sentence!r} -- the hole this probe documents "
            "may have been closed; re-review"
        )


def test_hostile_rewrite_of_build_stations_pinned_sentence_still_matches() -> None:
    """End-to-end version of the negation-matcher hole against a REAL pinned
    sentence: `test_build_station_text.py`'s
    `test_dispatch_record_commits_once_per_wave_not_per_record` requires a
    sentence naming "appended once", "committed once" and "first dispatch"
    with no negation. A sentence using "cannot" to state the exact OPPOSITE
    of the rule -- implementer records CANNOT be appended/committed as
    described -- still satisfies that test's own filter, because "cannot"
    evades `_has_negation`. If this sentence replaced the real one in
    build/SKILL.md, the pinned test would keep passing while the prose it
    pins says the opposite thing."""
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
    assert hits, (
        "expected the hostile negated-via-'cannot' rewrite to still match "
        "the pinned-sentence filter (that is the hole); if it no longer "
        "matches, the negation matcher used by test_build_station_text.py "
        "has been hardened -- re-review whether the shared regex changed"
    )


# ---------------------------------------------------------------------------
# Class 6: ship's §4 pre-push checklist claims to mirror CI "command for
# command" -- the doc-citations line does not reproduce the CI invocation.
# ---------------------------------------------------------------------------

def test_ship_checklist_doc_citations_line_is_not_the_ci_command() -> None:
    """ship/SKILL.md §4 says the checklist "mirrors
    `.github/workflows/loom-code-ci.yml`'s jobs, command for command, so a
    red line here is red there too." The CI job pipes a filtered
    `git ls-files` list through `xargs` into `check_doc_citations.py`; the
    checklist's line is the bare `python3 loom-code/scripts/check_doc_citations.py`
    with a trailing comment pointing at the workflow step, and no actual
    file arguments. These are not the same command."""
    section = text_after_heading(SHIP_SKILL, "## 4. Push")
    checklist_block = section.split("```", 2)[1]
    doc_citation_lines = [
        line for line in checklist_block.splitlines()
        if "check_doc_citations.py" in line
    ]
    assert doc_citation_lines, "no check_doc_citations.py line in ship's §4 checklist"
    line = doc_citation_lines[0]
    assert "git ls-files" not in line and "xargs" not in line, (
        "the checklist line does not carry the file-selection pipeline the "
        "CI job actually runs"
    )


def test_ship_checklist_doc_citations_line_run_verbatim_exits_nonzero() -> None:
    """Reproduced: copying the checklist's printed line and running it
    verbatim (stripped of its trailing `#` comment, as a user would type it)
    exits 2 (argparse usage error) regardless of the repository's actual
    citation health -- it can never reflect "red there too" because it
    never runs the check at all."""
    section = text_after_heading(SHIP_SKILL, "## 4. Push")
    checklist_block = section.split("```", 2)[1]
    line = next(
        line for line in checklist_block.splitlines()
        if "check_doc_citations.py" in line
    )
    command = line.split("#", 1)[0].strip()
    result = subprocess.run(
        command.split(), cwd=str(REPO), capture_output=True, text=True,
    )
    assert result.returncode != 0, (
        f"expected the bare checklist line {command!r} to fail with a "
        f"usage error regardless of repo health; got exit "
        f"{result.returncode} -- re-review whether the script's default "
        "argument handling changed"
    )


def test_ci_workflow_doc_citations_step_does_pass_on_this_tree() -> None:
    """Control case: the ACTUAL CI command (with its file-selection
    pipeline) exits 0 on this tree, confirming the checklist's failure mode
    above is specific to the checklist's line, not to the repo's citation
    health."""
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
# Class 4: scripts/run_package_tests.py -- empty/absent argv, `--`-only argv
# ---------------------------------------------------------------------------

def test_runner_empty_argv_exits_zero_having_run_nothing() -> None:
    """Empty and absent input: invoking the runner with NO arguments exits
    0 -- success -- while running zero pytest sessions. A truncated or
    mistyped KICKOFF-DEFAULTS command (e.g. a shell-quoting accident that
    drops every path argument) would silently "pass" the package-tests
    probe rather than failing loudly."""
    result = subprocess.run(
        [sys.executable, str(RUNNER)], cwd=str(REPO), capture_output=True, text=True,
    )
    assert result.returncode == 0, "expected the boundary case to reproduce as exit 0"
    assert result.stdout.strip() == "" and result.stderr.strip() == "", (
        "expected no pytest output at all, confirming zero sessions ran"
    )


def test_runner_dashdash_only_argv_exits_zero_having_run_nothing() -> None:
    """Boundary one step past empty: an argv consisting only of `--` (every
    group empty after splitting) also exits 0 with no session run -- the
    same silent-success hole as the fully empty case, reached a different
    way."""
    result = subprocess.run(
        [sys.executable, str(RUNNER), "--"], cwd=str(REPO), capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "" and result.stderr.strip() == ""


def test_runner_failing_first_group_shortcircuits_second_group() -> None:
    """Wrong call order / failure of a dependency, combined: when the first
    `--`-separated group fails, the runner returns immediately -- the
    second group's pytest session never runs at all (not merely its result
    being masked). Held: this matches the module's own docstring claim
    ("Two sessions, one exit code") rather than breaking it, but it means a
    red loom-code group hides whether the loom-design group would ALSO have
    been red or green -- recorded as a finding, not a break, since the
    runner never claimed to run both regardless of failure."""
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
             "--", str(good), "-q", "-p", "no:cacheprovider"],
            cwd=str(REPO), capture_output=True, text=True,
        )
        assert result.returncode != 0
        assert not marker.exists(), (
            "expected the second group to NOT have run after the first "
            "group failed -- if it now runs, the runner's short-circuit "
            "behaviour has changed and this finding is stale"
        )


# ---------------------------------------------------------------------------
# Class 1 (prose pins): gate-block reordering in review/SKILL.md keeps both
# <!-- gate: ... --> ... <!-- /gate --> pairs intact with their original ids.
# Held: attempted, did not break.
# ---------------------------------------------------------------------------

def test_review_skill_gate_blocks_remain_paired_and_named_after_reorder() -> None:
    """W1-02 moved the `review.reviewer-not-implementer` gate block's prose
    (splitting the old single block into an ungated sentence plus a
    narrower gated remainder). Held: both `<!-- gate: ... -->` /
    `<!-- /gate -->` pairs the file declares are still balanced and the two
    ids this delta touches (`review.two-fresh-reviewers`,
    `review.reviewer-not-implementer`) are both still present exactly
    once each."""
    text = (REPO / "loom-code" / "skills" / "review" / "SKILL.md").read_text(encoding="utf-8")
    opens = re.findall(r"<!--\s*gate:\s*([A-Za-z0-9._-]+)\s*-->", text)
    closes = len(re.findall(r"<!--\s*/gate\s*-->", text))
    assert len(opens) == closes, (
        f"{len(opens)} gate-open markers vs {closes} gate-close markers -- "
        "reordering left an orphaned gate block"
    )
    for gate_id in ("review.two-fresh-reviewers", "review.reviewer-not-implementer"):
        assert opens.count(gate_id) == 1, (
            f"gate id {gate_id!r} appears {opens.count(gate_id)} times "
            "(expected exactly 1) after the §2 reorder"
        )


# ---------------------------------------------------------------------------
# Class 2 (word caps): measure every touched file's cap the same way the
# pinned test measures it, and confirm adversary.md's reported "exactly 600"
# claim. Held: attempted, all within cap.
# ---------------------------------------------------------------------------

def _body_of(text: str) -> str:
    match = re.match(r"^---\n.*?\n---\n", text, re.DOTALL)
    return text[match.end():] if match else text


def test_word_caps_hold_for_every_touched_station_file() -> None:
    """Held: independently recomputes every cap named in the plan/scope
    (reviewer.md 1460, adversary.md 600, review/SKILL.md 4500,
    ship/SKILL.md 3500) using the same body-extraction rule
    `test_reviewer_agent_single_contract.py` uses (strip a leading YAML
    frontmatter block, then count words), plus build/SKILL.md's own
    soft-cap test (whole file, 3750). None of the five is over cap on this
    tree; adversary.md is confirmed at exactly 600."""
    reviewer_md = REPO / "loom-code" / "agents" / "reviewer.md"
    adversary_md = REPO / "loom-code" / "agents" / "adversary.md"
    review_skill = REPO / "loom-code" / "skills" / "review" / "SKILL.md"
    ship_skill = SHIP_SKILL
    build_skill = BUILD_SKILL

    reviewer_words = len(_body_of(reviewer_md.read_text(encoding="utf-8")).split())
    adversary_words = len(_body_of(adversary_md.read_text(encoding="utf-8")).split())
    review_skill_words = len(_body_of(review_skill.read_text(encoding="utf-8")).split())
    ship_skill_words = len(_body_of(ship_skill.read_text(encoding="utf-8")).split())
    build_skill_words = len(build_skill.read_text(encoding="utf-8").split())

    assert reviewer_words <= 1460, f"reviewer.md body is {reviewer_words} words"
    assert adversary_words == 600, (
        f"adversary.md body is {adversary_words} words, expected exactly 600 "
        "as reported in the scope"
    )
    assert review_skill_words <= 4500, f"review/SKILL.md body is {review_skill_words} words"
    assert ship_skill_words <= 3500, f"ship/SKILL.md body is {ship_skill_words} words"
    assert build_skill_words <= 3750, f"build/SKILL.md whole file is {build_skill_words} words"


# ---------------------------------------------------------------------------
# Class 5: dispatch-batching claim -- commit count bound from Acceptance 6.
# Held: attempted, the bound currently holds at wave-end:1.
# ---------------------------------------------------------------------------

def test_dispatch_commit_count_within_waves_plus_rounds_bound() -> None:
    """Held: Acceptance 6 says the number of `chore(loom): dispatch`-subject
    commits on the branch must stay <= (waves so far) + (review rounds so
    far). At wave-end:1 there are 2 waves (W1, W2/fix-wave) and 1 review
    round (wave-end:1 round 1) so far, bound = 3; counts the actual
    dispatch-subject commits on the range and confirms it does not exceed
    that bound."""
    subjects = subprocess.run(
        ["git", "log", "--format=%s", f"{_confirm_intent_sha()}..HEAD"],
        cwd=str(REPO), capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    dispatch_commits = [s for s in subjects if s.startswith("chore(loom): dispatch")]
    waves_so_far = 2  # W1 wave, W2/fix-wave wave (per plan.md's Task DAG)
    rounds_so_far = 1  # wave-end:1, round 1
    bound = waves_so_far + rounds_so_far
    assert len(dispatch_commits) <= bound, (
        f"{len(dispatch_commits)} dispatch-subject commits exceed the bound "
        f"{bound} (2 waves + 1 round) -- the per-wave/per-round batching "
        f"claim is violated: {dispatch_commits}"
    )


if __name__ == "__main__":  # pragma: no cover
    sys.exit(pytest.main([__file__, "-q"]))
