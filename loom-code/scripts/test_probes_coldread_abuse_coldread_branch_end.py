"""Branch-end adversary pass for `2026-09-04-adversary-three-way-
attribution-measured`, wave 2 delta.

Wave 1's code (`loom-code/scripts/coldread_role_split.py`) was already
attacked across three rounds — see `test_abuse_coldread_wave1.py`,
`test_abuse_coldread_wave1_fix.py`, `test_abuse_coldread_runner.py`,
`test_abuse_coldread_run_status.py`, `test_abuse_coldread_scoring.py`
in this directory. This file does not repeat those cases. It attacks
the *evidence* wave 2 committed: does every number in `baselines.md`
and the intent's `## Measurement record` actually recompute from the
raw `run-<i>.txt` bodies via the shipped `parse_response`/`score`
functions, do the committed hashes match the committed bytes they
claim to hash, is the "systematic" list mechanical rather than
transcribed, are the nine graduated probe copies byte-identical to
their evidence originals, and was the mechanically-decided arm (B —
leave the wording alone) actually taken.

Every case here is run against the real committed evidence at HEAD;
none of them mutate anything.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest


def _find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "docs" / "loom").is_dir() and (candidate / "loom-code").is_dir():
            return candidate
    raise RuntimeError(f"could not locate repo root above {start}")


REPO_ROOT = _find_repo_root(Path(__file__).parent)
CID = "2026-09-04-adversary-three-way-attribution-measured"
EVIDENCE_DIR = REPO_ROOT / "docs" / "loom" / CID / "evidence"
PROBES_DIR = EVIDENCE_DIR / "probes"
SCRIPTS_DIR = REPO_ROOT / "loom-code" / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))
import coldread_role_split as m  # noqa: E402

FIXTURE = json.loads((EVIDENCE_DIR / "fixture-coldread-8.json").read_text(encoding="utf-8"))

_BASELINE_DIRS = [
    "baseline-precap-adversary",
    "baseline-precap-reviewer",
    "baseline-current-adversary",
    "baseline-current-reviewer",
]


def _load_summary(dirname: str) -> dict:
    return json.loads((EVIDENCE_DIR / dirname / "summary.json").read_text(encoding="utf-8"))


def _read_run_bodies(dirname: str, n: int) -> list[str]:
    bodies = []
    for i in range(1, n + 1):
        text = (EVIDENCE_DIR / dirname / f"run-{i}.txt").read_text(encoding="utf-8")
        _, _, body = text.partition("\n\n")
        bodies.append(body)
    return bodies


def _run_headers(dirname: str, n: int) -> list[dict]:
    headers = []
    for i in range(1, n + 1):
        text = (EVIDENCE_DIR / dirname / f"run-{i}.txt").read_text(encoding="utf-8")
        header, _, _ = text.partition("\n\n")
        fields = {}
        for line in header.splitlines():
            if line.startswith("# status:"):
                fields["status"] = line.split(":", 1)[1].strip()
            elif line.startswith("# model:"):
                fields["model"] = line.split(":", 1)[1].strip()
            elif line.startswith("# prompt-sha256:"):
                fields["prompt_sha256"] = line.split(":", 1)[1].strip()
        headers.append(fields)
    return headers


@pytest.mark.parametrize("dirname", _BASELINE_DIRS)
def test_summary_json_wrong_recomputed_from_raw_run_bodies_matches(dirname: str) -> None:
    """A `summary.json` that claims a score without the raw transcripts
    backing it up is a report that asserts nothing. This recomputes
    `own_not_own_correct`, `three_way_correct`, `systematic`, `n`, and
    every per-item `wrong`/`dominant_wrong` cell directly from the
    committed `run-<i>.txt` bodies via the shipped `parse_response`/
    `score` functions (never by re-reading the summary's own numbers)
    and asserts the committed `summary.json` agrees exactly."""
    summary = _load_summary(dirname)
    bodies = _read_run_bodies(dirname, summary["attempted_runs"])
    recomputed = m.score(bodies, FIXTURE, summary["role"])

    assert recomputed["n"] == summary["n"]
    assert recomputed["own_not_own_correct"] == summary["own_not_own_correct"]
    assert recomputed["three_way_correct"] == summary["three_way_correct"]
    assert recomputed["systematic"] == summary["systematic"]
    for item_n_str, claimed_item in summary["items"].items():
        recomputed_item = recomputed["items"][item_n_str]
        assert recomputed_item["wrong"] == claimed_item["wrong"], (
            f"{dirname} item {item_n_str}: wrong recomputed={recomputed_item['wrong']} "
            f"claimed={claimed_item['wrong']}"
        )
        assert recomputed_item["dominant_wrong"] == claimed_item["dominant_wrong"]
        assert recomputed_item["counts"] == claimed_item["counts"]


@pytest.mark.parametrize("dirname", _BASELINE_DIRS)
def test_systematic_list_matches_50pct_same_wrong_label_50pct_n3_rule(dirname: str) -> None:
    """The intent's stated rule for "systematic" is: an item wrong in
    >=50% of scored runs, with the same wrong label in >=50% of scored
    runs, and n >= 3. This recomputes the rule directly from each
    summary's own per-item `counts`/`wrong` fields (never trusting the
    `systematic` list itself) and checks it against the committed list —
    catching a systematic list that was hand-edited rather than
    produced by the scorer."""
    summary = _load_summary(dirname)
    n = summary["n"]
    expected_systematic = []
    for item_n_str in sorted(summary["items"], key=int):
        info = summary["items"][item_n_str]
        if n < 3:
            continue
        wrong_rate = info["wrong"] / n
        dominant = info["dominant_wrong"]
        if dominant is None:
            continue
        dominant_rate = info["counts"].get(dominant, 0) / n
        if wrong_rate >= 0.5 and dominant_rate >= 0.5:
            expected_systematic.append(int(item_n_str))
    assert expected_systematic == summary["systematic"], (
        f"{dirname}: rule recomputes systematic={expected_systematic}, "
        f"summary claims {summary['systematic']}"
    )


def test_precap_contract_copies_byte_identical_to_git_history_4ab5224d() -> None:
    """`contract-precap-adversary.md` and `contract-precap-reviewer.md`
    are supposed to be `git show 4ab5224d:loom-code/agents/<x>.md`
    verbatim, not a retyped or re-wrapped copy. This diffs the committed
    file bytes against a fresh `git show` of that commit.

    Grounding for the `git show <commit>:<path>` form relied on below:
    git-show(1) (https://git-scm.com/docs/git-show), "git show <object>"
    section — an <object> may be a `<rev>:<path>` blob reference, whose
    grammar is defined in gitrevisions(7)
    (https://git-scm.com/docs/gitrevisions), `<rev>:<path>` — and the
    fact this probe relies on: a `<commit>:<path>` argument to `git show`
    prints that path's blob contents as they existed at that commit,
    with no other output mixed in."""
    for role, filename in (("adversary", "contract-precap-adversary.md"), ("reviewer", "contract-precap-reviewer.md")):
        committed = (EVIDENCE_DIR / filename).read_bytes()
        historical = subprocess.run(
            ["git", "show", f"4ab5224d:loom-code/agents/{role}.md"],
            cwd=REPO_ROOT, capture_output=True, check=True,
        ).stdout
        assert committed == historical, f"{filename} differs from git show 4ab5224d:loom-code/agents/{role}.md"


@pytest.mark.parametrize("dirname", _BASELINE_DIRS)
def test_run_headers_carry_status_ok_model_sonnet_and_correct_prompt_hash(dirname: str) -> None:
    """Every `run-<i>.txt` in a committed baseline must be a real,
    completed, scored observation: `# status: ok`, `# model: sonnet`,
    and `# prompt-sha256` equal to sha256 of `build_prompt(contract_text,
    fixture, role)` recomputed right now from the committed contract
    file the summary names — not merely equal to whatever the header
    itself already says."""
    summary = _load_summary(dirname)
    role = summary["role"]
    # The "current" baselines were run on the agent files as of loom-code
    # 1.4.0 (db7d44f9); 1.5.0 edited those files afterwards, so the text
    # to recompute against is the committed measured snapshot, not the
    # live file the summary's `contract.path` names.
    if dirname.startswith("baseline-current-"):
        contract_path = EVIDENCE_DIR / f"contract-measured-{role}.md"
    else:
        contract_path = REPO_ROOT / summary["contract"]["path"]
    contract_text = contract_path.read_text(encoding="utf-8")
    assert hashlib.sha256(contract_path.read_bytes()).hexdigest() == summary["contract"]["sha256"], (
        f"{dirname}: the summary's contract hash is not the hash of {contract_path.name}"
    )
    expected_prompt = m.build_prompt(contract_text, FIXTURE, role)
    expected_hash = hashlib.sha256(expected_prompt.encode("utf-8")).hexdigest()

    headers = _run_headers(dirname, summary["attempted_runs"])
    for i, fields in enumerate(headers, start=1):
        assert fields.get("status") == "ok", f"{dirname} run-{i}: status={fields.get('status')!r}"
        assert fields.get("model") == "sonnet", f"{dirname} run-{i}: model={fields.get('model')!r}"
        assert fields.get("prompt_sha256") == expected_hash, (
            f"{dirname} run-{i}: prompt-sha256={fields.get('prompt_sha256')!r} "
            f"recomputed={expected_hash!r}"
        )


def test_graduated_probe_copies_byte_identical_to_evidence_originals() -> None:
    """The nine `loom-code/scripts/test_probes_coldread_*.py` files are
    supposed to be graduated copies of the nine `evidence/probes/
    test_*.py` files, with at most their path-referencing lines
    differing (the plan says the fixture-verbatim check is "rewritten
    to read the fixture and the prior list by repo-relative path"; the
    others should carry over untouched). This diffs each pair and
    reports which, if any, are not byte-identical."""
    graduated_dir = SCRIPTS_DIR
    graduated = sorted(graduated_dir.glob("test_probes_coldread_*.py"))
    assert graduated, "no graduated test_probes_coldread_*.py files found"

    non_identical = []
    checked = 0
    for graduated_path in graduated:
        stem = graduated_path.stem  # e.g. test_probes_coldread_abuse_coldread_wave1
        suffix = stem[len("test_probes_coldread_"):]
        original_path = PROBES_DIR / f"test_{suffix}.py"
        if not original_path.is_file():
            continue
        checked += 1
        if graduated_path.read_bytes() != original_path.read_bytes():
            non_identical.append((graduated_path.name, original_path.name))

    assert checked >= 1, "no graduated/original pairs matched by name; naming scheme may have drifted"
    assert non_identical == [], f"graduated copies differ from their evidence originals: {non_identical}"


def test_readme_paragraph_numbers_agree_with_current_adversary_summary() -> None:
    """`docs/loom/README.md`'s three-way-attribution paragraph quotes
    "80/80" (pre-cap) and "79/80" (current, post-cap) for the adversary
    contract. This checks both numbers against the committed
    `baseline-precap-adversary` and `baseline-current-adversary`
    summaries' `three_way_correct`/`three_way_total`."""
    readme = (REPO_ROOT / "docs" / "loom" / "README.md").read_text(encoding="utf-8")
    precap = _load_summary("baseline-precap-adversary")
    current = _load_summary("baseline-current-adversary")

    precap_fraction = f"{precap['three_way_correct']}/{precap['three_way_total']}"
    current_fraction = f"{current['three_way_correct']}/{current['three_way_total']}"

    assert precap_fraction in readme, f"README does not contain the pre-cap fraction {precap_fraction!r}"
    assert current_fraction in readme, f"README does not contain the current fraction {current_fraction!r}"
    assert precap["systematic"] == [], "README claims no systematic item pre-cap, but summary disagrees"
    assert current["systematic"] == [], "README claims no systematic item current, but summary disagrees"


def _positioning_paragraph(text: str) -> str:
    """The `You own ...` paragraph of an agent contract: the blank-line
    delimited block whose first line starts with `You own`."""
    for block in text.split("\n\n"):
        if block.lstrip().startswith("You own"):
            return block.strip()
    raise AssertionError("no `You own` paragraph found")


def test_arm_b_taken_adversary_positioning_paragraph_unchanged_since_measurement() -> None:
    """The intent's `## Measurement record` concludes arm B (leave the
    wording alone) because `baseline-current-adversary`'s `systematic`
    list is empty. This checks the mechanical precondition for arm B —
    `systematic == []` — and, independently, that the positioning
    paragraph of `loom-code/agents/adversary.md` at HEAD is identical to
    the paragraph in `contract-measured-adversary.md`, the text the
    baseline was run on (the agent file at db7d44f9). The whole file is
    not compared: loom-code 1.5.0 edited two sentences elsewhere in the
    contract after the measurement, and arm B only promises that the
    attribution wording was left alone."""
    summary = _load_summary("baseline-current-adversary")
    assert summary["systematic"] == [], "arm B's mechanical precondition (systematic == []) does not hold"

    current = (REPO_ROOT / "loom-code" / "agents" / "adversary.md").read_text(encoding="utf-8")
    measured = (EVIDENCE_DIR / "contract-measured-adversary.md").read_text(encoding="utf-8")
    assert _positioning_paragraph(current) == _positioning_paragraph(measured), (
        "the adversary positioning paragraph changed after the measurement despite arm B"
    )


def test_memory_step_store_integrity_check_exits_zero() -> None:
    """The plan's W2-memory task originally named its own verification
    test as `python3 loom-code/scripts/loom_checker.py memory` — that
    sub-command does not exist (`--list-rules`, `intent`, `intake`,
    `push`, `standing`, `contract` are the only ones) and the command
    exited 2 ("unknown sub-command"), never 0. The plan line was
    corrected at branch-end to name the real memory-store checker,
    `python3 scripts/check_loom_memory_integrity.py --check` at repo
    root. This probe runs the corrected command from the repo root
    (resolved from `__file__`, not the process cwd) and asserts it
    exits 0 against the committed memory store — the positive case the
    original probe never carried."""
    result = subprocess.run(
        [sys.executable, "scripts/check_loom_memory_integrity.py", "--check"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        f"expected the corrected memory-store checker to pass with exit 0, "
        f"got {result.returncode}: {result.stdout}{result.stderr}"
    )

    # Negative control, clearly labelled: the plan's ORIGINAL (now-corrected)
    # command still does not exist and still exits 2 — kept as a witness
    # that the fix in the plan, not a change to loom_checker.py itself, is
    # what closed this finding.
    stale_command = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "loom_checker.py"), "memory"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert stale_command.returncode == 2, (
        "negative control: the plan's original 'loom_checker.py memory' command "
        f"was expected to still exit 2 (unknown sub-command), got {stale_command.returncode}"
    )
