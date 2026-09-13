"""Rebuild frozen histories and enforce the cumulative-boundary admission bar."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "docs/skill-dogfood/2026-09-13-cumulative-boundary-reassessment"
CASES = EVIDENCE_DIR / "cases.md"
REPORT = EVIDENCE_DIR / "report.md"
BASELINE_REVISION = "1973ff35c4919e4c40795808240249c7ee40f506"
BASELINE_SHA256 = "e4c249bae4a5badbd15c258fbfe6d4d2d920e9eba58329fa2ee05bfe573c0da4"
CANDIDATE_REVISION = "e2161e2fe6b3bf40d33b8a0c45cb035f77d2d73c"
ALLOWED_CANDIDATE_PATHS = {
    "loom-code/skills/write-plan/SKILL.md",
    "loom-code/skills/write-plan/references/cumulative-boundary-reassessment.md",
}
CANDIDATE_REVISION_PATHS = ALLOWED_CANDIDATE_PATHS | {
    "loom-code/scripts/test_cumulative_boundary_contract.py",
}
ARTIFACT_CARRIERS = {
    "cases": {
        "revision": "4864ea08d96824f74a9b824f39ded1e27b910fd9",
        "path": "docs/skill-dogfood/2026-09-13-cumulative-boundary-reassessment/cases.md",
        "blob": "e97ac10e201da9abd2885e3b6a548effb223eeff",
    },
    "admission_probe": {
        "revision": "4864ea08d96824f74a9b824f39ded1e27b910fd9",
        "path": "loom-code/scripts/test_probes_cumulative_boundary_reassessment.py",
        "blob": "ab40c5061e070d19cad2f3d106d1b4de7c308a42",
    },
    "normalized_report": {
        "revision": "d7e72bb348b8e0092c611992f1bee140ed2f2a6e",
        "path": "docs/skill-dogfood/2026-09-13-cumulative-boundary-reassessment/report.md",
        "blob": "29d9be0261ccc4f9d65fba22ddd0d9cdd2c4febf",
    },
}
MINIMUM_GIT_VERSION = (2, 32)

# Git 2.32 is the harness floor: its official manuals document the config-file
# overrides and numbered environment pairs cleared below. git-init documents
# --initial-branch, --object-format, and --template. See:
# https://git-scm.com/docs/git-config/2.32.0.html#ENVIRONMENT
# https://git-scm.com/docs/git-init/2.32.0.html#_options
# https://git-scm.com/docs/git/2.32.0.html#_environment_variables
_INHERITED_GIT_ENV = {
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_AUTHOR_DATE",
    "GIT_AUTHOR_EMAIL",
    "GIT_AUTHOR_NAME",
    "GIT_COMMON_DIR",
    "GIT_COMMITTER_DATE",
    "GIT_COMMITTER_EMAIL",
    "GIT_COMMITTER_NAME",
    "GIT_CONFIG",
    "GIT_CONFIG_GLOBAL",
    "GIT_CONFIG_NOSYSTEM",
    "GIT_CONFIG_PARAMETERS",
    "GIT_CONFIG_SYSTEM",
    "GIT_DIR",
    "GIT_EXEC_PATH",
    "GIT_EXTERNAL_DIFF",
    "GIT_GRAFT_FILE",
    "GIT_INDEX_FILE",
    "GIT_NAMESPACE",
    "GIT_NO_REPLACE_OBJECTS",
    "GIT_OBJECT_DIRECTORY",
    "GIT_REPLACE_REF_BASE",
    "GIT_SHALLOW_FILE",
    "GIT_TEMPLATE_DIR",
    "GIT_WORK_TREE",
}


def _fenced_json(path: Path, label: str) -> tuple[dict, str]:
    text = path.read_text()
    match = re.search(rf"```json {re.escape(label)}\n(.*?)\n```", text, re.S)
    assert match, f"missing ```json {label}` block in {path}"
    return json.loads(match.group(1)), match.group(1)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _frozen_rubric() -> str:
    match = re.search(
        r"<!-- BEGIN frozen-rubric -->\n(.*?)\n<!-- END frozen-rubric -->",
        CASES.read_text(),
        re.S,
    )
    assert match, "missing frozen rubric markers"
    return match.group(1)


def _sanitized_git_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = os.environ.copy()
    for key in tuple(env):
        if key in _INHERITED_GIT_ENV or re.fullmatch(
            r"GIT_CONFIG_(?:KEY|VALUE)_\d+", key
        ):
            env.pop(key, None)
    if extra:
        env.update(extra)
    env.update(
        {
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_COUNT": "0",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    return env


def _run(repo: Path, *args: str, env: dict[str, str] | None = None) -> str:
    command_env = _sanitized_git_env(env) if args[0] == "git" else env
    completed = subprocess.run(
        [*args],
        cwd=repo,
        env=command_env,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.strip()


def _run_bytes(repo: Path, *args: str) -> bytes:
    completed = subprocess.run(
        [*args],
        cwd=repo,
        env=_sanitized_git_env() if args[0] == "git" else None,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout


def _fixture_git(
    repo: Path, runtime: dict[str, Path], *args: str, env: dict[str, str] | None = None
) -> str:
    # core.hooksPath is the documented override for hooks, and --no-gpg-sign
    # below counteracts commit.gpgSign. See the official Git manuals:
    # https://git-scm.com/docs/git-config/2.32.0.html#Documentation/git-config.txt-corehooksPath
    # https://git-scm.com/docs/git-commit/2.32.0.html#Documentation/git-commit.txt---no-gpg-sign
    return _run(
        repo,
        "git",
        "-c",
        f"core.hooksPath={runtime['hooks']}",
        "-c",
        "commit.gpgSign=false",
        "-c",
        f"init.templateDir={runtime['templates']}",
        *args,
        env=env,
    )


# The fixture command flags are grounded in the Git 2.32 manuals used by the
# replay floor: https://git-scm.com/docs/git-add/2.32.0.html,
# https://git-scm.com/docs/git-commit/2.32.0.html,
# https://git-scm.com/docs/git-rev-parse/2.32.0.html, and
# https://git-scm.com/docs/git-status/2.32.0.html.
def build_fixture(root: Path, case_id: str, case: dict, git_config: dict) -> dict:
    repo = root / case_id
    repo.mkdir()
    runtime = {
        "hooks": root / f".{case_id}-empty-hooks",
        "templates": root / f".{case_id}-empty-templates",
    }
    runtime["hooks"].mkdir()
    runtime["templates"].mkdir()
    _fixture_git(
        repo,
        runtime,
        "init",
        "-q",
        f"--template={runtime['templates']}",
        f"--initial-branch={git_config['branch']}",
        f"--object-format={git_config['object_format']}",
    )
    _fixture_git(repo, runtime, "config", "user.name", git_config["author_name"])
    _fixture_git(repo, runtime, "config", "user.email", git_config["author_email"])

    started = datetime.fromisoformat(git_config["start_time"])
    commits = []
    for index, revision in enumerate(case["commits"]):
        changed_paths = []
        removed_paths = []
        for relative, content in revision["changes"].items():
            target = repo / relative
            if content is None:
                if target.exists():
                    target.unlink()
                removed_paths.append(relative)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content)
                changed_paths.append(relative)
        if changed_paths:
            _fixture_git(repo, runtime, "add", "--", *changed_paths)
        for relative in removed_paths:
            _fixture_git(repo, runtime, "add", "-u", "--", relative)
        timestamp = (started + timedelta(minutes=index)).astimezone(timezone.utc).isoformat()
        env = {
            "GIT_AUTHOR_DATE": timestamp,
            "GIT_COMMITTER_DATE": timestamp,
            "LC_ALL": "C",
            "TZ": "UTC",
        }
        _fixture_git(
            repo,
            runtime,
            "commit",
            "-q",
            "--no-gpg-sign",
            "--no-verify",
            "-m",
            revision["message"],
            env=env,
        )
        commits.append(_fixture_git(repo, runtime, "rev-parse", "HEAD"))

    return {
        "repo": repo,
        "head": _fixture_git(repo, runtime, "rev-parse", "HEAD"),
        "tree": _fixture_git(repo, runtime, "rev-parse", "HEAD^{tree}"),
        "commits": commits,
    }


@pytest.fixture(scope="session")
def fixture_spec() -> tuple[dict, str]:
    return _fenced_json(CASES, "fixture-spec")


def test_fixture_spec_is_complete_and_bounded(fixture_spec):
    spec, _ = fixture_spec
    assert spec["schema"] == 1
    assert spec["git"]["object_format"] == "sha1"
    assert set(spec["cases"]) == {"L1", "L2", "L3", "L4"}
    assert all(2 <= len(case["commits"]) <= 20 for case in spec["cases"].values())
    assert all(case["feature_request"].strip() for case in spec["cases"].values())


def test_git_cli_meets_declared_replay_floor():
    match = re.search(r"(\d+)\.(\d+)", _run(ROOT, "git", "--version"))
    assert match, "git --version did not expose a major.minor version"
    assert tuple(map(int, match.groups())) >= MINIMUM_GIT_VERSION


def test_baseline_contract_matches_frozen_identity():
    # git-show's <revision>:<path> form is documented at:
    # https://git-scm.com/docs/git-show/2.32.0.html
    baseline = _run_bytes(
        ROOT,
        "git",
        "show",
        f"{BASELINE_REVISION}:loom-code/skills/write-plan/SKILL.md",
    )
    assert hashlib.sha256(baseline).hexdigest() == BASELINE_SHA256


@pytest.mark.parametrize("case_id", ["L1", "L2", "L3", "L4"])
def test_real_git_history_matches_frozen_identity(tmp_path, fixture_spec, case_id):
    spec, _ = fixture_spec
    case = spec["cases"][case_id]
    built = build_fixture(tmp_path, case_id, case, spec["git"])
    assert built["head"] == case["expected_head"]
    assert built["tree"] == case["expected_tree"]
    assert len(built["commits"]) == len(set(built["commits"]))
    assert _run(built["repo"], "git", "status", "--porcelain") == ""


@pytest.mark.parametrize("case_id", ["L1", "L2", "L3", "L4"])
def test_fixture_head_unit_tests_pass(tmp_path, fixture_spec, case_id):
    spec, _ = fixture_spec
    built = build_fixture(tmp_path, case_id, spec["cases"][case_id], spec["git"])
    _run(built["repo"], sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q")


def valid_admission_example(spec: dict, fixture_spec_sha256: str) -> dict:
    fixtures = {
        case_id: {"head": case["expected_head"], "tree": case["expected_tree"]}
        for case_id, case in spec["cases"].items()
    }
    candidate = _candidate_repository_snapshot(ROOT, CANDIDATE_REVISION)
    return {
        "status": "ADMITTED",
        "identities": {
            "fixture_spec_sha256": fixture_spec_sha256,
            "rubric_sha256": _sha256_text(_frozen_rubric()),
            "baseline_revision": BASELINE_REVISION,
            "baseline_contract_sha256": BASELINE_SHA256,
            "candidate_revision": CANDIDATE_REVISION,
            "candidate_contract_sha256": candidate["contract_sha256"],
            "candidate_contract_bytes": candidate["contract_bytes"],
            "candidate_reference_sha256": candidate["reference_sha256"],
            "candidate_reference_bytes": candidate["reference_bytes"],
            "candidate_revision_paths": candidate["revision_paths"],
            "candidate_changed_contract_paths": sorted(ALLOWED_CANDIDATE_PATHS),
            "artifact_carriers": {
                name: carrier.copy() for name, carrier in ARTIFACT_CARRIERS.items()
            },
        },
        "fixtures": fixtures,
        "runner_profile": {
            "baseline": {"model": "test-model", "effort": "test-effort"},
            "candidate": {"model": "test-model", "effort": "test-effort"},
        },
        "normalizer_sha256": "3" * 64,
        "normalized_outputs": {
            case_id: {"baseline": "4" * 64, "candidate": "5" * 64}
            for case_id in ("L1", "L2", "L3", "L4")
        },
        "auditors": ["audit-one", "audit-two"],
        "cases": {
            "L1": {"baseline": ["incorrect", "incorrect"], "candidate": ["correct", "correct"]},
            "L2": {"baseline": ["correct", "correct"], "candidate": ["correct", "correct"]},
            "L3": {"baseline": ["insufficient", "insufficient"], "candidate": ["correct", "correct"]},
            "L4": {"baseline": ["correct", "correct"], "candidate": ["correct", "correct"]},
        },
        "reference_loaded": {"L1": True, "L2": False, "L3": True, "L4": False},
        "cost": {
            "baseline": {"elapsed_seconds": 1, "input_tokens": 1, "output_tokens": 1},
            "candidate": {"elapsed_seconds": 1, "input_tokens": 1, "output_tokens": 1},
        },
        "mechanism_delta": 0,
        "real_runs": {
            "L1": {
                "complete": True,
                "focused_tests_pass": True,
                "candidate_surface_clearer_or_smaller": True,
            },
            "L2": {
                "complete": True,
                "focused_tests_pass": True,
                "extraction_performed": False,
            },
        },
        "claims_scope": "frozen-four-case-corpus-only",
    }


def _candidate_repository_snapshot(repo: Path, revision: str) -> dict:
    # --verify with ^{commit} validates object existence and type; diff-tree
    # --name-only recomputes the committed path delta rather than trusting prose.
    # https://git-scm.com/docs/git-rev-parse/2.32.0.html#Documentation/git-rev-parse.txt---verify
    # https://git-scm.com/docs/git-diff-tree/2.32.0.html#Documentation/git-diff-tree.txt---name-only
    resolved = _run(repo, "git", "rev-parse", "--verify", f"{revision}^{{commit}}")
    revision_paths = sorted(
        _run(
            repo,
            "git",
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            f"{resolved}^",
            resolved,
        ).splitlines()
    )
    contract = _run_bytes(
        repo, "git", "show", f"{resolved}:loom-code/skills/write-plan/SKILL.md"
    )
    reference = _run_bytes(
        repo,
        "git",
        "show",
        f"{resolved}:loom-code/skills/write-plan/references/cumulative-boundary-reassessment.md",
    )
    return {
        "revision": resolved,
        "revision_paths": revision_paths,
        "contract_sha256": hashlib.sha256(contract).hexdigest(),
        "contract_bytes": len(contract),
        "reference_sha256": hashlib.sha256(reference).hexdigest(),
        "reference_bytes": len(reference),
    }


def _repository_identity_failures(evidence: dict, repo: Path) -> list[str]:
    identities = evidence.get("identities") or {}
    failures = []
    claimed_revision = identities.get("candidate_revision")
    try:
        candidate = _candidate_repository_snapshot(repo, str(claimed_revision or ""))
    except subprocess.CalledProcessError:
        failures.append("candidate revision object is missing or is not a commit")
        candidate = None
    if claimed_revision != CANDIDATE_REVISION:
        failures.append("candidate revision identity is missing or mismatched")
    if candidate:
        checks = (
            ("candidate_contract_sha256", "contract_sha256", "candidate contract identity"),
            ("candidate_contract_bytes", "contract_bytes", "candidate contract byte count"),
            ("candidate_reference_sha256", "reference_sha256", "candidate reference identity"),
            ("candidate_reference_bytes", "reference_bytes", "candidate reference byte count"),
            ("candidate_revision_paths", "revision_paths", "candidate revision path diff"),
        )
        for claimed_field, actual_field, label in checks:
            if identities.get(claimed_field) != candidate[actual_field]:
                failures.append(f"{label} is missing or mismatched")
        if set(candidate["revision_paths"]) != CANDIDATE_REVISION_PATHS:
            failures.append("candidate revision path diff is outside the frozen scope")

    claimed_carriers = identities.get("artifact_carriers") or {}
    for name, expected in ARTIFACT_CARRIERS.items():
        label = name.replace("_", " ")
        claimed = claimed_carriers.get(name) or {}
        if claimed != expected:
            failures.append(f"{label} carrier is missing or mismatched")
            continue
        try:
            # revision:path resolves only committed blobs; an uncommitted path
            # cannot masquerade as a replayable carrier.
            # https://git-scm.com/docs/gitrevisions/2.32.0.html#Documentation/gitrevisions.txt-emltrevgtltpathgtemegemHEADREADMEem
            observed_blob = _run(
                repo,
                "git",
                "rev-parse",
                "--verify",
                f"{claimed['revision']}:{claimed['path']}",
            )
        except subprocess.CalledProcessError:
            failures.append(f"{label} carrier object is missing")
            continue
        if observed_blob != claimed["blob"]:
            failures.append(f"{label} carrier blob is mismatched")
    return failures


def _static_identity_failures(
    evidence: dict, fixture_spec_sha256: str
) -> list[str]:
    failures = []
    identities = evidence.get("identities") or {}
    if identities.get("fixture_spec_sha256") != fixture_spec_sha256:
        failures.append("fixture specification identity is missing or mismatched")
    if identities.get("rubric_sha256") != _sha256_text(_frozen_rubric()):
        failures.append("rubric identity is missing or mismatched")
    if identities.get("baseline_revision") != BASELINE_REVISION:
        failures.append("baseline revision is missing or mismatched")
    if identities.get("baseline_contract_sha256") != BASELINE_SHA256:
        failures.append("baseline contract identity is missing or mismatched")
    for field in ("candidate_contract_sha256", "candidate_reference_sha256"):
        value = identities.get(field)
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            failures.append(f"{field} is missing or malformed")
    if identities.get("candidate_contract_sha256") == BASELINE_SHA256:
        failures.append("candidate contract is byte-identical to the baseline")
    if set(identities.get("candidate_changed_contract_paths") or []) != ALLOWED_CANDIDATE_PATHS:
        failures.append("candidate contract path identity is incomplete or out of scope")
    return failures


def _fixture_identity_failures(evidence: dict, spec: dict) -> list[str]:
    failures = []
    fixtures = evidence.get("fixtures") or {}
    for case_id, case in spec["cases"].items():
        observed = fixtures.get(case_id) or {}
        if observed.get("head") != case["expected_head"] or observed.get("tree") != case["expected_tree"]:
            failures.append(f"{case_id} fixture identity is missing or mismatched")
    return failures


def _audit_failures(evidence: dict) -> list[str]:
    failures = []
    auditors = evidence.get("auditors") or []
    if len(auditors) != 2 or len(set(auditors)) != 2:
        failures.append("two independent auditor identities are required")
    cases = evidence.get("cases") or {}
    expected = {
        "L1": {"candidate": ["correct", "correct"]},
        "L2": {"candidate": ["correct", "correct"]},
        "L3": {"candidate": ["correct", "correct"]},
        "L4": {"candidate": ["correct", "correct"]},
    }
    for case_id, arms in expected.items():
        for arm, scores in arms.items():
            if (cases.get(case_id) or {}).get(arm) != scores:
                failures.append(f"{case_id} {arm} does not meet the frozen rubric")
    if (cases.get("L1") or {}).get("baseline") not in (
        ["incorrect", "incorrect"],
        ["insufficient", "insufficient"],
    ):
        failures.append("L1 baseline does not meet the frozen non-tie requirement")
    return failures


def _execution_identity_failures(evidence: dict) -> list[str]:
    failures = []
    runner_profile = evidence.get("runner_profile") or {}
    if not runner_profile.get("baseline") or runner_profile.get("baseline") != runner_profile.get("candidate"):
        failures.append("matched runner profile is missing or differs by arm")
    if not re.fullmatch(r"[0-9a-f]{64}", str(evidence.get("normalizer_sha256") or "")):
        failures.append("normalizer identity is missing or malformed")
    normalized_outputs = evidence.get("normalized_outputs") or {}
    for case_id in ("L1", "L2", "L3", "L4"):
        for arm in ("baseline", "candidate"):
            value = (normalized_outputs.get(case_id) or {}).get(arm)
            if not re.fullmatch(r"[0-9a-f]{64}", str(value or "")):
                failures.append(f"{case_id} {arm} normalized output identity is missing")
    return failures


def _cost_and_real_run_failures(evidence: dict) -> list[str]:
    failures = []
    loads = evidence.get("reference_loaded") or {}
    if loads != {"L1": True, "L2": False, "L3": True, "L4": False}:
        failures.append("conditional reference loading does not match the challenge corpus")
    cost = evidence.get("cost") or {}
    for arm in ("baseline", "candidate"):
        values = cost.get(arm) or {}
        if not all(isinstance(values.get(field), (int, float)) and values[field] >= 0
                   for field in ("elapsed_seconds", "input_tokens", "output_tokens")):
            failures.append(f"{arm} cost evidence is missing")
    if evidence.get("mechanism_delta") != 0:
        failures.append("mechanism population did not remain flat")
    real_runs = evidence.get("real_runs") or {}
    l1 = real_runs.get("L1") or {}
    if not (l1.get("complete") and l1.get("focused_tests_pass")
            and l1.get("candidate_surface_clearer_or_smaller")):
        failures.append("L1 real implementation evidence is missing or unmet")
    l2 = real_runs.get("L2") or {}
    if not (l2.get("complete") and l2.get("focused_tests_pass")
            and l2.get("extraction_performed") is False):
        failures.append("L2 real implementation evidence is missing or unmet")
    if evidence.get("claims_scope") != "frozen-four-case-corpus-only":
        failures.append("claims scope exceeds the frozen corpus")
    return failures


def admission_failures(evidence: dict, spec: dict, fixture_spec_sha256: str) -> list[str]:
    failures = []
    if evidence.get("status") != "ADMITTED":
        failures.append("status is not ADMITTED")
    failures.extend(_static_identity_failures(evidence, fixture_spec_sha256))
    failures.extend(_repository_identity_failures(evidence, ROOT))
    failures.extend(_fixture_identity_failures(evidence, spec))
    failures.extend(_audit_failures(evidence))
    failures.extend(_execution_identity_failures(evidence))
    failures.extend(_cost_and_real_run_failures(evidence))
    return failures


def test_admission_oracle_accepts_complete_evidence(fixture_spec):
    spec, raw = fixture_spec
    evidence = valid_admission_example(spec, _sha256_text(raw))
    assert admission_failures(evidence, spec, _sha256_text(raw)) == []


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("l1-tie", "L1 baseline"),
        ("l2-split", "L2 candidate"),
        ("l3-resplit", "L3 candidate"),
        ("l4-noise", "L4 candidate"),
        ("fixture-swap", "L1 fixture identity"),
        ("arm-path", "candidate contract path identity"),
        ("always-load", "conditional reference loading"),
        ("missing-real-run", "L1 real implementation"),
    ],
)
def test_admission_oracle_rejects_false_success(fixture_spec, mutation, expected):
    spec, raw = fixture_spec
    evidence = valid_admission_example(spec, _sha256_text(raw))
    if mutation == "l1-tie":
        evidence["cases"]["L1"]["baseline"] = ["correct", "correct"]
    elif mutation == "l2-split":
        evidence["cases"]["L2"]["candidate"] = ["incorrect", "incorrect"]
    elif mutation == "l3-resplit":
        evidence["cases"]["L3"]["candidate"] = ["incorrect", "incorrect"]
    elif mutation == "l4-noise":
        evidence["cases"]["L4"]["candidate"] = ["incorrect", "incorrect"]
    elif mutation == "fixture-swap":
        evidence["fixtures"]["L1"]["head"] = evidence["fixtures"]["L2"]["head"]
    elif mutation == "arm-path":
        evidence["identities"]["candidate_changed_contract_paths"].append("loom-code/agents/implementer.md")
    elif mutation == "always-load":
        evidence["reference_loaded"]["L2"] = True
    else:
        evidence["real_runs"]["L1"] = None
    assert any(expected in failure for failure in admission_failures(evidence, spec, _sha256_text(raw)))


def test_observed_report_meets_admission_bar(fixture_spec):
    spec, raw = fixture_spec
    evidence, _ = _fenced_json(REPORT, "evidence")
    failures = admission_failures(evidence, spec, _sha256_text(raw))
    assert failures == [
        "status is not ADMITTED",
        "L4 candidate does not meet the frozen rubric",
        "L1 baseline does not meet the frozen non-tie requirement",
        "conditional reference loading does not match the challenge corpus",
        "baseline cost evidence is missing",
        "candidate cost evidence is missing",
    ]


def test_candidate_revision_and_artifact_carriers_are_repository_bound(fixture_spec):
    spec, raw = fixture_spec
    evidence = valid_admission_example(spec, _sha256_text(raw))
    assert _repository_identity_failures(evidence, ROOT) == []


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("fabricated-hash", "candidate contract identity"),
        ("missing-object", "candidate revision object"),
        ("uncommitted-carrier", "normalized report carrier"),
    ],
)
def test_repository_identity_rejects_unverifiable_claims(
    fixture_spec, mutation, expected
):
    spec, raw = fixture_spec
    evidence = valid_admission_example(spec, _sha256_text(raw))
    if mutation == "fabricated-hash":
        evidence["identities"]["candidate_contract_sha256"] = "f" * 64
    elif mutation == "missing-object":
        evidence["identities"]["candidate_revision"] = "0" * 40
    else:
        evidence["identities"]["artifact_carriers"]["normalized_report"] = {
            "revision": "HEAD",
            "path": "docs/skill-dogfood/2026-09-13-cumulative-boundary-reassessment/uncommitted.md",
            "blob": "1" * 40,
        }
    failures = _repository_identity_failures(evidence, ROOT)
    assert any(expected in failure for failure in failures)


def test_refactored_validators_preserve_failure_order(fixture_spec):
    spec, raw = fixture_spec
    evidence = valid_admission_example(spec, _sha256_text(raw))
    evidence["status"] = "NOT_ADMITTED"
    evidence["cases"]["L1"]["baseline"] = ["correct", "correct"]
    evidence["reference_loaded"]["L2"] = True
    expected = [
        "status is not ADMITTED",
        "L1 baseline does not meet the frozen non-tie requirement",
        "conditional reference loading does not match the challenge corpus",
    ]
    assert admission_failures(evidence, spec, _sha256_text(raw)) == expected


def test_fixture_build_ignores_hostile_inherited_git_configuration(
    tmp_path, fixture_spec, monkeypatch
):
    spec, _ = fixture_spec
    sentinel = tmp_path / "hook-fired"
    hostile_hooks = tmp_path / "hostile-hooks"
    hostile_templates = tmp_path / "hostile-templates"
    hostile_hooks.mkdir()
    (hostile_templates / "hooks").mkdir(parents=True)
    hook = f"#!/bin/sh\ntouch '{sentinel}'\n"
    for path in (hostile_hooks / "post-commit", hostile_templates / "hooks/post-commit"):
        path.write_text(hook)
        path.chmod(0o755)
    hostile_config = tmp_path / "hostile.gitconfig"
    hostile_config.write_text(
        "[commit]\n\tgpgSign = true\n"
        f"[core]\n\thooksPath = {hostile_hooks}\n"
        f"[init]\n\ttemplateDir = {hostile_templates}\n"
    )
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(hostile_config))
    monkeypatch.setenv("GIT_CONFIG_SYSTEM", str(hostile_config))
    monkeypatch.setenv("GIT_CONFIG_COUNT", "3")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "commit.gpgSign")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "true")
    monkeypatch.setenv("GIT_CONFIG_KEY_1", "core.hooksPath")
    monkeypatch.setenv("GIT_CONFIG_VALUE_1", str(hostile_hooks))
    monkeypatch.setenv("GIT_CONFIG_KEY_2", "init.templateDir")
    monkeypatch.setenv("GIT_CONFIG_VALUE_2", str(hostile_templates))
    monkeypatch.setenv("GIT_TEMPLATE_DIR", str(hostile_templates))

    fixture_root = tmp_path / "fixtures"
    fixture_root.mkdir()
    built = build_fixture(fixture_root, "L1", spec["cases"]["L1"], spec["git"])

    assert built["head"] == spec["cases"]["L1"]["expected_head"]
    assert not sentinel.exists()
    assert not (built["repo"] / ".git/hooks/post-commit").exists()
