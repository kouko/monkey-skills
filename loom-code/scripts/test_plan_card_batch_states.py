"""Task Batch Review ledger transitions (plan Task 3)."""

import importlib.util
import multiprocessing
import subprocess
import sys
import time
from pathlib import Path

import pytest


SCRIPT = Path(__file__).with_name("plan_card.py")
REVIEW_SCRIPT = Path(__file__).with_name("review_batch.py")
REVIEW_SPEC = importlib.util.spec_from_file_location("review_batch", REVIEW_SCRIPT)
assert REVIEW_SPEC and REVIEW_SPEC.loader
review_batch = importlib.util.module_from_spec(REVIEW_SPEC)
sys.modules[REVIEW_SPEC.name] = review_batch
REVIEW_SPEC.loader.exec_module(review_batch)
SPEC = importlib.util.spec_from_file_location("plan_card_batch_states", SCRIPT)
plan_card = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = plan_card
SPEC.loader.exec_module(plan_card)

A_SHA = "a" * 40
B_SHA = "b" * 40
I1 = f"implemented({A_SHA})"
I2 = f"implemented({B_SHA})"
D1 = f"done({A_SHA})"
D2 = f"done({B_SHA})"


def _transition_authority(replacements, *, force_reopen_owners=None):
    declaration = review_batch.BatchDeclaration(
        "capability",
        ("Task 1", "Task 2"),
        "Does the capability work?",
        "full",
        "package test suite",
        "capability: fixture; exclusions: none; consumable: yes",
    )
    scope_issuer = review_batch._trusted_scope_issuer(
        issuer="git-scope-resolver",
        source_identity="git:sha1:v1",
        hash_algorithm="sha1",
    )
    members = []
    for number, sha in ((1, A_SHA), (2, B_SHA)):
        files = (review_batch.ReviewedFile(f"src/{number}.py", b"fixture"),)
        members.append(
            review_batch.MemberSnapshot(
                f"Task {number}", f"implemented({sha})", sha,
                (f"src/{number}.py",), files, (f"REQ-{number}",), (),
                (f"accept-{number}",),
                scope_issuer.issue(
                    repository_identity="e" * 64,
                    commit_sha=sha,
                    tree_identity=sha,
                    files=files,
                ),
            )
        )
    members = tuple(members)
    issuer = review_batch._trusted_proof_issuer(
        issuer="sdd:declared-first",
        source_identity="authority:v1",
        source_digest="c" * 64,
    )
    records = tuple(
        review_batch.OwnershipRecord(
            member.task_id, member.owned_requirements,
            member.future_requirements, member.acceptance,
        )
        for member in members
    )
    ownership = issuer.issue_ownership(
        plan_identity="plan:fixture",
        spec_identity="spec:fixture",
        records=records,
        execution_projection=review_batch._issue_execution_projection_from_validated_plan(
            plan_text=_plan({1: I1, 2: I2, 3: "pending"}),
            batch_id="capability",
            plan_identity="plan:fixture",
            spec_identity="spec:fixture",
            records=records,
            issuer="plan-card:validated-schema",
            source_identity="plan:current",
            source_digest="8" * 64,
        ),
    )
    approved = review_batch._approved_safe_resolution(
        declaration_digest=review_batch.text_digest("package test suite"),
        argv=("python3", "-m", "pytest"),
        execution_scope=("src",),
        result="exit=0",
        scanner_receipt_identity="scanner:fixture",
        scanner_input_digest="d" * 64,
    )
    receipt = review_batch._trusted_resolution_issuer(
        issuer="declared-first-resolver",
        source_identity="resolver:v1",
        source_digest="f" * 64,
    ).issue(approved)
    packet = review_batch.materialize_packet(
        declaration, members, ownership, issuer.issue_verification(receipt)
    )
    arms = ("spec-reviewer", "code-quality-reviewer")
    bindings = tuple(
        review_batch.ReviewerArmBinding(
            packet.identity, arm, f"dispatch:{arm}", f"dispatch-proof:{arm}"
        )
        for arm in arms
    )
    reopening = force_reopen_owners is not None or set(replacements) != {1, 2}
    owner = next(iter(replacements)) if reopening else None
    finding_owners = (
        force_reopen_owners
        if force_reopen_owners is not None
        else ((f"Task {owner}",) if owner else ("Task 1",))
    )
    finding = review_batch.BlockingFinding(
        "finding:owner", packet.identity, "spec-reviewer",
        "dispatch:spec-reviewer", "result-proof:spec-reviewer",
        finding_owners, True,
        "owned_requirement", f"REQ-{owner or 1}", f"src/{owner or 1}.py",
        "fatal", "fixture regression",
    )
    results = tuple(
        review_batch.ReviewerTerminalResult(
            packet.identity, arm, f"dispatch:{arm}", f"dispatch-proof:{arm}",
            f"result:{arm}", f"result-proof:{arm}", "completed",
            "NEEDS_REVISION" if reopening and arm == "spec-reviewer" else "PASS",
            (finding,) if reopening and arm == "spec-reviewer" else (),
        )
        for arm in arms
    )
    resolution = review_batch.resolve_aggregate_review(
        packet=packet,
        declared_lane="full",
        expected_arms=arms,
        arm_bindings=bindings,
        terminal_results=results,
    )
    assert resolution.transition_authority is not None
    return resolution.transition_authority


def _plan(statuses: dict[int, str]) -> str:
    tasks = []
    for number, dependency, disposition in (
        (1, "none", "batch(capability)"),
        (2, "Task 1 completes first", "batch(capability)"),
        (3, "Task 2 completes first", "individual"),
    ):
        tasks.append(
            f"## Task {number} — task {number}\n\n"
            "- **Description**: fixture\n"
            f"- **Dependencies**: {dependency}\n"
            f"- **Files touched**: src/{number}.py\n"
            f"- **Acceptance**: accept-{number}\n"
            f"- **Brief item covered**: REQ-{number}\n"
            "- **Review-weight**: full\n"
            f"- **Review disposition**: {disposition}\n"
            f"- **Status**: {statuses[number]}\n"
        )
    return (
        "# Plan: fixture\n\n"
        "Goal: exercise Batch ledger transitions.\n"
        "Stage: sdd:wave-1\n\n"
        + "\n".join(tasks)
        + "\n## Review Batches\n\n"
        "### Review Batch: capability\n"
        "- **Members**: Task 1, Task 2\n"
        "- **Verdict question**: Does the capability work?\n"
        "- **Review lane**: full\n"
        "- **Aggregate verification**: package test suite\n"
        "- **Boundary**: capability: fixture; exclusions: none; consumable: yes\n"
    )


def _atomic_update_worker(path, expected, replacements, start, results):
    start.wait()
    try:
        changed = plan_card.atomic_batch_status_update(
            Path(path), "capability", expected, replacements,
            transition_authority=_transition_authority(replacements),
        )
        results.put(("ok", changed))
    except Exception as exc:  # pragma: no cover - surfaced through the queue
        results.put(("error", type(exc).__name__, str(exc)))


def _blocking_atomic_worker(path, expected, entered, release, results):
    def block_before_publish():
        entered.set()
        if not release.wait(5):
            raise RuntimeError("test release timeout")

    try:
        changed = plan_card.atomic_batch_status_update(
            Path(path),
            "capability",
            expected,
            {1: D1, 2: D2},
            transition_authority=_transition_authority({1: D1, 2: D2}),
            before_replace=block_before_publish,
        )
        results.put(("ok", changed))
    except Exception as exc:  # pragma: no cover - surfaced through the queue
        results.put(("error", type(exc).__name__, str(exc)))


def test_batch_ledger_transition_matrix(tmp_path):
    # @req: REQ-103
    # @req: REQ-104
    # @req: REQ-108
    implemented = {1: I1, 2: I2}
    assert plan_card._classify(implemented[1]) == "implemented"
    changed, _, _ = plan_card.set_status(
        _plan({1: "claimed(@main)", 2: "pending", 3: "pending"}),
        1,
        implemented[1],
    )
    assert f"- **Status**: {I1}" in changed

    assert plan_card.dependency_is_ready(implemented[1], "capability", "capability")
    assert not plan_card.dependency_is_ready(
        implemented[1], "capability", None
    )
    assert plan_card.dependency_is_ready(D1, "capability", None)
    assert not plan_card.dependency_is_ready("claimed(@main)", "capability", "capability")
    assert not plan_card.dependency_is_ready(implemented[1], None, None)
    for malformed in (
        "implemented(stale",
        "implemented()",
        "implemented(a b)",
        "implemented((abc))",
        "done(a111111)junk",
    ):
        assert not plan_card.dependency_is_ready(
            malformed, "capability", "capability"
        )

    plan_path = tmp_path / "plan.md"
    original = _plan({**implemented, 3: "pending"})
    plan_path.write_text(original, encoding="utf-8")

    finalized = plan_card.atomic_batch_status_update(
        plan_path,
        "capability",
        implemented,
        {1: D1, 2: D2},
        transition_authority=_transition_authority({1: D1, 2: D2}),
    )
    assert finalized is True
    assert f"- **Status**: {D1}" in plan_path.read_text(encoding="utf-8")
    assert f"- **Status**: {D2}" in plan_path.read_text(encoding="utf-8")

    before_retry = plan_path.read_bytes()
    assert plan_card.atomic_batch_status_update(
        plan_path,
        "capability",
        implemented,
        {1: D1, 2: D2},
        transition_authority=_transition_authority({1: D1, 2: D2}),
    )
    assert plan_path.read_bytes() == before_retry

    plan_path.write_text(original, encoding="utf-8")
    assert not plan_card.atomic_batch_status_update(
        plan_path,
        "capability",
        {1: "implemented(stale)", 2: implemented[2]},
        {1: "done(stale)", 2: D2},
        transition_authority=_transition_authority({1: D1, 2: D2}),
    )
    assert plan_path.read_text(encoding="utf-8") == original

    assert plan_card.atomic_batch_status_update(
        plan_path,
        "capability",
        implemented,
        {2: "pending"},
        transition_authority=_transition_authority({2: "pending"}),
    )
    reopened = plan_path.read_text(encoding="utf-8")
    assert f"- **Status**: {I1}" in reopened
    assert "- **Status**: pending" in reopened

    plan_path.write_text(original, encoding="utf-8")
    assert not plan_card.atomic_batch_status_update(
            plan_path,
            "capability",
            implemented,
            {3: "pending"},
            transition_authority=object(),
        )
    assert plan_path.read_text(encoding="utf-8") == original

    def interrupt():
        raise RuntimeError("injected interruption")

    with pytest.raises(RuntimeError, match="injected interruption"):
        plan_card.atomic_batch_status_update(
            plan_path,
            "capability",
            implemented,
            {1: D1, 2: D2},
            transition_authority=_transition_authority({1: D1, 2: D2}),
            before_replace=interrupt,
        )
    assert plan_path.read_text(encoding="utf-8") == original

    invalid = original.replace("- **Members**: Task 1, Task 2", "- **Members**: Task 1")
    plan_path.write_text(invalid, encoding="utf-8")
    assert not plan_card.atomic_batch_status_update(
            plan_path,
            "capability",
            implemented,
            {1: D1, 2: D2},
            transition_authority=_transition_authority({1: D1, 2: D2}),
        )
    assert plan_path.read_text(encoding="utf-8") == invalid

    plan_path.write_text(original, encoding="utf-8")
    for malformed in (
        "implemented(stale",
        "implemented()",
        "implemented(a b)",
        "implemented((abc))",
    ):
        malformed_snapshot = {**implemented, 1: malformed}
        assert not plan_card.atomic_batch_status_update(
                plan_path,
                "capability",
                malformed_snapshot,
                {1: "pending"},
                transition_authority=_transition_authority({1: "pending"}),
            )
        assert plan_path.read_text(encoding="utf-8") == original


def test_reopen_of_every_member_is_validated_as_reopen_not_finalize(tmp_path):
    # A reopen whose owner union is the whole membership (every member's
    # replacement is "pending") must still be validated against a reopen
    # authority, not misclassified as a finalize by
    # set(replacements) == member_set (station-prose live failure).
    implemented = {1: I1, 2: I2}
    plan_path = tmp_path / "plan.md"
    original = _plan({**implemented, 3: "pending"})
    plan_path.write_text(original, encoding="utf-8")

    full_reopen = {1: "pending", 2: "pending"}
    changed = plan_card.atomic_batch_status_update(
        plan_path,
        "capability",
        implemented,
        full_reopen,
        transition_authority=_transition_authority(
            full_reopen, force_reopen_owners=("Task 1", "Task 2")
        ),
    )
    assert changed is True
    text = plan_path.read_text(encoding="utf-8")
    assert text.count("- **Status**: pending") == 3


def test_locked_reader_releases_descriptor_after_invalid_utf8(tmp_path):
    plan_path = tmp_path / "plan.md"
    plan_path.write_bytes(b"\xff\xfe")

    with pytest.raises(UnicodeDecodeError):
        plan_card.atomic_batch_status_update(
            plan_path,
            "capability",
            {1: I1, 2: I2},
            {1: "pending"},
            transition_authority=_transition_authority({1: "pending"}),
        )

    expected = {1: I1, 2: I2}
    plan_path.write_text(_plan({**expected, 3: "pending"}), encoding="utf-8")
    context = multiprocessing.get_context("spawn")
    start = context.Event()
    results = context.Queue()
    process = context.Process(
        target=_atomic_update_worker,
        args=(plan_path, expected, {1: "pending"}, start, results),
    )
    process.start()
    start.set()
    process.join(5)
    if process.is_alive():
        process.terminate()
        process.join()
        pytest.fail("a leaked descriptor kept the plan lock held")
    assert process.exitcode == 0
    assert results.get(timeout=1) == ("ok", True)


def test_two_process_batch_cas_has_one_atomic_winner(tmp_path):
    expected = {1: I1, 2: I2}
    plan_path = tmp_path / "plan.md"
    plan_path.write_text(_plan({**expected, 3: "pending"}), encoding="utf-8")
    context = multiprocessing.get_context("spawn")
    start = context.Event()
    results = context.Queue()
    processes = [
        context.Process(
            target=_atomic_update_worker,
            args=(
                plan_path,
                expected,
                replacements,
                start,
                results,
            ),
        )
        for replacements in (
            {1: D1, 2: D2},
            {2: "pending"},
        )
    ]
    for process in processes:
        process.start()
    start.set()
    for process in processes:
        process.join(5)
        if process.is_alive():
            process.terminate()
            process.join()
            pytest.fail("competing Batch CAS did not terminate")
        assert process.exitcode == 0

    outcomes = [results.get(timeout=1), results.get(timeout=1)]
    assert sorted(outcomes) == [("ok", False), ("ok", True)]
    final = plan_path.read_text(encoding="utf-8")
    states = plan_card._task_statuses(final)
    assert (states[1], states[2]) in {
        (D1, D2),
        (I1, "pending"),
    }


def test_external_replace_before_cas_publish_is_stale_and_preserved(tmp_path):
    """Best-effort detection for a non-participating direct filesystem writer."""
    expected = {1: I1, 2: I2}
    plan_path = tmp_path / "plan.md"
    original = _plan({**expected, 3: "pending"})
    external = original.replace("Stage: sdd:wave-1", "Stage: external-writer")
    plan_path.write_text(original, encoding="utf-8")

    def replace_from_external_actor():
        external_path = tmp_path / "external.md"
        external_path.write_text(external, encoding="utf-8")
        external_path.replace(plan_path)

    changed = plan_card.atomic_batch_status_update(
        plan_path,
        "capability",
        expected,
        {1: D1, 2: D2},
        transition_authority=_transition_authority({1: D1, 2: D2}),
        before_replace=replace_from_external_actor,
    )

    assert changed is False
    assert plan_path.read_text(encoding="utf-8") == external
    assert list(tmp_path.glob(f".{plan_path.name}.*.tmp")) == []


def test_set_status_refuses_done_for_declared_batch_member(tmp_path):
    """A task declared `batch(capability)` cannot have its `done(<sha>)`
    hand-set through `--set-status` — apply-result is the only writer,
    so crash recovery can trust a `done` it finds (plan Task 5). The
    refusal prints on stdout with the same `plan_card: FAIL —` prefix
    every other failure uses (Decision Log DL-1)."""
    plan_path = tmp_path / "plan.md"
    original = _plan({1: I1, 2: I2, 3: "pending"})
    plan_path.write_text(original, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(plan_path), "--set-status", f"T1={D1}"],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0, result.stdout + result.stderr
    assert plan_path.read_text(encoding="utf-8") == original
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "capability" in result.stdout, result.stdout
    assert "apply-result" in result.stdout, result.stdout


def test_set_status_refuses_done_when_disposition_missing_but_batches_declared(
    tmp_path,
):
    """A task with no `- Review disposition:` line is schema-invalid
    when the plan declares `## Review Batches` — refuse a `done(<sha>)`
    write rather than risk a hidden batch member (fail-closed, plan
    Task 5 review round 1 finding 3)."""
    plan_path = tmp_path / "plan.md"
    original = (
        "# Plan: fixture\n\n"
        "Goal: exercise missing-disposition fail-closed.\n"
        "Stage: sdd:wave-1\n\n"
        "## Task 1 — task 1\n\n"
        "- **Description**: fixture\n"
        "- **Dependencies**: none\n"
        "- **Files touched**: src/1.py\n"
        "- **Acceptance**: accept-1\n"
        "- **Brief item covered**: REQ-1\n"
        "- **Review-weight**: full\n"
        f"- **Status**: {I1}\n"
        "\n## Review Batches\n\n"
        "### Review Batch: capability\n"
        "- **Members**: Task 1\n"
        "- **Verdict question**: Does the capability work?\n"
        "- **Review lane**: full\n"
        "- **Aggregate verification**: package test suite\n"
        "- **Boundary**: capability: fixture; exclusions: none; consumable: yes\n"
    )
    plan_path.write_text(original, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(plan_path), "--set-status", f"T1={D1}"],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0, result.stdout + result.stderr
    assert plan_path.read_text(encoding="utf-8") == original


def test_set_status_refuses_done_when_disposition_is_malformed(tmp_path):
    """A `- Review disposition:` value that does not fullmatch the
    oracle's disposition grammar (e.g. trailing junk) is schema-invalid
    — refuse a `done(<sha>)` write rather than let a malformed
    disposition through the guard undetected."""
    plan_path = tmp_path / "plan.md"
    original = (
        "# Plan: fixture\n\n"
        "Goal: exercise malformed-disposition fail-closed.\n"
        "Stage: sdd:wave-1\n\n"
        "## Task 1 — task 1\n\n"
        "- **Description**: fixture\n"
        "- **Dependencies**: none\n"
        "- **Files touched**: src/1.py\n"
        "- **Acceptance**: accept-1\n"
        "- **Brief item covered**: REQ-1\n"
        "- **Review-weight**: full\n"
        "- **Review disposition**: batch(capability) (paused)\n"
        f"- **Status**: {I1}\n"
        "\n## Review Batches\n\n"
        "### Review Batch: capability\n"
        "- **Members**: Task 1\n"
        "- **Verdict question**: Does the capability work?\n"
        "- **Review lane**: full\n"
        "- **Aggregate verification**: package test suite\n"
        "- **Boundary**: capability: fixture; exclusions: none; consumable: yes\n"
    )
    plan_path.write_text(original, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(plan_path), "--set-status", f"T1={D1}"],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert plan_path.read_text(encoding="utf-8") == original


def test_set_status_refuses_done_when_batch_omits_task(tmp_path):
    """A task's disposition names a batch whose `**Members**` list does
    not include it — schema-invalid, refuse a `done(<sha>)` write
    rather than trust a disposition the batch itself disagrees with."""
    plan_path = tmp_path / "plan.md"
    original = (
        "# Plan: fixture\n\n"
        "Goal: exercise batch/disposition mismatch fail-closed.\n"
        "Stage: sdd:wave-1\n\n"
        "## Task 1 — task 1\n\n"
        "- **Description**: fixture\n"
        "- **Dependencies**: none\n"
        "- **Files touched**: src/1.py\n"
        "- **Acceptance**: accept-1\n"
        "- **Brief item covered**: REQ-1\n"
        "- **Review-weight**: full\n"
        "- **Review disposition**: batch(capability)\n"
        f"- **Status**: {I1}\n\n"
        "## Task 2 — task 2\n\n"
        "- **Description**: fixture\n"
        "- **Dependencies**: none\n"
        "- **Files touched**: src/2.py\n"
        "- **Acceptance**: accept-2\n"
        "- **Brief item covered**: REQ-2\n"
        "- **Review-weight**: full\n"
        "- **Review disposition**: batch(capability)\n"
        f"- **Status**: {I2}\n"
        "\n## Review Batches\n\n"
        "### Review Batch: capability\n"
        "- **Members**: Task 2\n"
        "- **Verdict question**: Does the capability work?\n"
        "- **Review lane**: full\n"
        "- **Aggregate verification**: package test suite\n"
        "- **Boundary**: capability: fixture; exclusions: none; consumable: yes\n"
    )
    plan_path.write_text(original, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(plan_path), "--set-status", f"T1={D1}"],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert plan_path.read_text(encoding="utf-8") == original


def test_set_status_refuses_done_when_disposition_duplicated(tmp_path):
    """Two `- Review disposition:` lines on the same task — the first
    `individual`, the second `batch(capability)` — is schema-invalid.
    `_bullet_value` (single-first-match) would otherwise see only the
    `individual` line and let a `done(<sha>)` write through a hidden
    batch member (whole-branch review finding, arm A)."""
    plan_path = tmp_path / "plan.md"
    original = (
        "# Plan: fixture\n\n"
        "Goal: exercise duplicate-disposition fail-closed.\n"
        "Stage: sdd:wave-1\n\n"
        "## Task 1 — task 1\n\n"
        "- **Description**: fixture\n"
        "- **Dependencies**: none\n"
        "- **Files touched**: src/1.py\n"
        "- **Acceptance**: accept-1\n"
        "- **Brief item covered**: REQ-1\n"
        "- **Review-weight**: full\n"
        "- **Review disposition**: individual\n"
        "- **Review disposition**: batch(capability)\n"
        f"- **Status**: {I1}\n"
        "\n## Review Batches\n\n"
        "### Review Batch: capability\n"
        "- **Members**: Task 1\n"
        "- **Verdict question**: Does the capability work?\n"
        "- **Review lane**: full\n"
        "- **Aggregate verification**: package test suite\n"
        "- **Boundary**: capability: fixture; exclusions: none; consumable: yes\n"
    )
    plan_path.write_text(original, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(plan_path), "--set-status", f"T1={D1}"],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert plan_path.read_text(encoding="utf-8") == original


def test_set_status_allows_implemented_for_declared_batch_member(tmp_path):
    """`implemented(<sha>)` on a declared batch member still succeeds —
    only `done(<sha>)` is a batch member's exclusive apply-result write
    (plan Task 5 review round 1 finding 4)."""
    plan_path = tmp_path / "plan.md"
    plan_path.write_text(
        _plan({1: "pending", 2: I2, 3: "pending"}), encoding="utf-8"
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(plan_path), "--set-status", f"T1={I1}"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert f"- **Status**: {I1}" in plan_path.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("cli_args", "assertion"),
    [
        (("--set-stage", "review:done"), "Stage: review:done"),
        (("--set-status", "T3=blocked"), "- **Status**: blocked"),
    ],
)
def test_cli_writer_waits_for_batch_publish_and_rereads_current_plan(
    tmp_path, cli_args, assertion
):
    expected = {1: I1, 2: I2}
    plan_path = tmp_path / "plan.md"
    plan_path.write_text(_plan({**expected, 3: "pending"}), encoding="utf-8")
    context = multiprocessing.get_context("spawn")
    entered = context.Event()
    release = context.Event()
    results = context.Queue()
    batch_writer = context.Process(
        target=_blocking_atomic_worker,
        args=(plan_path, expected, entered, release, results),
    )
    batch_writer.start()
    assert entered.wait(5), "Batch writer never reached its locked publish seam"

    cli_writer = subprocess.Popen(
        [sys.executable, str(SCRIPT), str(plan_path), *cli_args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    time.sleep(0.2)
    assert cli_writer.poll() is None, "CLI writer did not wait for directory lock"

    release.set()
    batch_writer.join(5)
    stdout, stderr = cli_writer.communicate(timeout=5)
    assert batch_writer.exitcode == 0
    assert results.get(timeout=1) == ("ok", True)
    assert cli_writer.returncode == 0, stdout + stderr
    final = plan_path.read_text(encoding="utf-8")
    assert f"- **Status**: {D1}" in final
    assert f"- **Status**: {D2}" in final
    assert assertion in final
    assert sorted(path.name for path in tmp_path.iterdir()) == ["plan.md"]


def _standalone_plan_card_copy(tmp_path):
    """Copy plan_card.py alone (no check_review_batches.py sibling) into
    an isolated directory — the standalone use this repo's plan-card
    shim/standalone convention documents (CLAUDE.md Contract Citations
    exempts loom-scaffolded standalone copies)."""
    standalone_dir = tmp_path / "standalone"
    standalone_dir.mkdir()
    standalone_script = standalone_dir / "plan_card.py"
    standalone_script.write_text(SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
    return standalone_script


def test_set_status_done_on_batch_free_plan_does_not_need_oracle(tmp_path):
    """A plan with no `## Review Batches` section must never reach the
    oracle call (plan Task 5 invariant) — even when `plan_card.py` is
    copied standalone without its sibling `check_review_batches.py`.
    Before the fix, `_batch_member_done_refusal` loaded the oracle
    unconditionally and crashed with an uncaught FileNotFoundError."""
    standalone_script = _standalone_plan_card_copy(tmp_path)
    plan_path = tmp_path / "plan.md"
    original = (
        "# Plan: fixture\n\n"
        "Goal: exercise batch-free standalone plan_card.py.\n"
        "Stage: sdd:wave-1\n\n"
        "## Task 1 — task 1\n\n"
        "- **Description**: fixture\n"
        "- **Dependencies**: none\n"
        "- **Files touched**: src/1.py\n"
        "- **Acceptance**: accept-1\n"
        "- **Brief item covered**: REQ-1\n"
        "- **Review-weight**: full\n"
        f"- **Status**: {I1}\n"
    )
    plan_path.write_text(original, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(standalone_script), str(plan_path), "--set-status", f"T1={D1}"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert f"- **Status**: {D1}" in plan_path.read_text(encoding="utf-8")


def test_set_status_done_refuses_when_oracle_missing_but_batches_declared(tmp_path):
    """A plan declaring `## Review Batches` DOES need the oracle; when the
    standalone copy is missing its sibling `check_review_batches.py`, the
    guard must fail closed with a `plan_card: FAIL —` message rather than
    crash uncaught and rather than silently allow the write."""
    standalone_script = _standalone_plan_card_copy(tmp_path)
    plan_path = tmp_path / "plan.md"
    original = (
        "# Plan: fixture\n\n"
        "Goal: exercise batch-declared standalone plan_card.py.\n"
        "Stage: sdd:wave-1\n\n"
        "## Task 1 — task 1\n\n"
        "- **Description**: fixture\n"
        "- **Dependencies**: none\n"
        "- **Files touched**: src/1.py\n"
        "- **Acceptance**: accept-1\n"
        "- **Brief item covered**: REQ-1\n"
        "- **Review-weight**: full\n"
        f"- **Status**: {I1}\n"
        "\n## Review Batches\n\n"
        "### Review Batch: capability\n"
        "- **Members**: Task 1\n"
        "- **Verdict question**: Does the capability work?\n"
        "- **Review lane**: full\n"
        "- **Aggregate verification**: package test suite\n"
        "- **Boundary**: capability: fixture; exclusions: none; consumable: yes\n"
    )
    plan_path.write_text(original, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(standalone_script), str(plan_path), "--set-status", f"T1={D1}"],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert plan_path.read_text(encoding="utf-8") == original
