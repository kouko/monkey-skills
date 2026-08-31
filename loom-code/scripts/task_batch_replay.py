#!/usr/bin/env python3
"""Compare individual and Task Batch Review on one authorized replay corpus.

The command consumes only three explicitly named local JSON files.  It never
discovers sessions, plans, repositories, or other paths.  The corpus contains
identifiers and measurement oracles, not source content; both result files
must bind to its exact canonical digest before any comparison is made.

Exit 0 proves the cost claim (review dispatches fell; rounds and reopens are
reported, never compared); the safety checks run only over evidence
``observe`` does not yet collect, so they cannot fire on the sanctioned path.  Exit 1 is a valid FAIL comparison, and exit 2
means an input could not be read or validate.

``observe`` derives a ``task-batch-replay-result/v2`` file from the dispatch
log ``review_context.py`` appends per reviewer fan-out and from the dispatch
receipts ``batch_review_cli.py`` writes, so the review counts are observed,
never typed.  ``--summary`` prints the one-line count instead of writing.
``compare`` reads only those observed v2 files: a ``task-batch-replay-result/v1``
file (the hand-typed pilot shape) or any file whose ``provenance`` is not
``"observed"`` is refused by name.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any


def _load(name: str, filename: str):
    """Load a sibling script module without cwd or sys.path coupling."""
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


review_context = _load("review_context_for_task_batch_replay", "review_context.py")

CORPUS_SCHEMA = "task-batch-replay-corpus/v1"
RESULT_SCHEMA = "task-batch-replay-result/v1"
RESULT_SCHEMA_V2 = "task-batch-replay-result/v2"
REPORT_SCHEMA = "task-batch-replay-report/v1"
OBSERVED_PROVENANCE = "observed"
SUMMARY_NO_LOG = "observed reviewer fan-outs: N/A — no dispatch log"

_DISPATCH_LOG_KEYS = {"schema", "recorded_at", "branch", "reviewed_sha", "plugin_version"}

_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")

_CORPUS_KEYS = {"schema", "authorization", "cases"}
_AUTHORIZATION_KEYS = {"authorized", "source"}
_CORPUS_CASE_KEYS = {
    "case_id",
    "task_ids",
    "requirements",
    "known_defects",
    "required_package_gates",
    "expected_candidate_path",
    "expected_fallback_causes",
}
_RESULT_KEYS_V2 = {"schema", "provenance", "corpus_identity", "branch", "cases"}
_RESULT_CASE_KEYS = {
    "case_id",
    "review_dispatches",
    "review_rounds",
    "fallback_causes",
    "false_scope_expansions",
    "detected_known_defects",
    "elapsed_work_ms",
    "maximum_aggregate_diff_bytes",
    "requirement_to_tests",
    "package_gates",
}
_RESULT_CASE_KEYS_V2 = _RESULT_CASE_KEYS | {"batch_reopens"}


class ReplayInputError(ValueError):
    """A replay input is unreadable, ambiguous, or outside the closed schema."""


def _fail(context: str, detail: str) -> None:
    raise ReplayInputError(f"{context}: {detail}")


def _object(value: object, keys: set[str], context: str) -> dict[str, Any]:
    if type(value) is not dict:
        _fail(context, "expected an object")
    if not all(type(key) is str for key in value):
        _fail(context, "object keys must be strings")
    actual = set(value)
    if actual != keys:
        missing = sorted(keys - actual)
        extra = sorted(actual - keys)
        _fail(context, f"closed schema mismatch; missing={missing}, extra={extra}")
    return value


def _identifier(value: object, context: str) -> str:
    if type(value) is not str or _IDENTIFIER.fullmatch(value) is None:
        _fail(context, "expected a non-secret identifier")
    return value


def _identifier_list(
    value: object, context: str, *, nonempty: bool = False
) -> list[str]:
    if type(value) is not list or (nonempty and not value):
        _fail(context, "expected an identifier list")
    items = [_identifier(item, f"{context}[{index}]") for index, item in enumerate(value)]
    if len(set(items)) != len(items):
        _fail(context, "duplicate identifiers are not allowed")
    return items


def _count(value: object, context: str) -> int:
    if type(value) is not int or value < 0:
        _fail(context, "expected a non-negative integer")
    return value


def _choice(value: object, choices: set[str], context: str) -> str:
    if type(value) is not str or value not in choices:
        _fail(context, f"expected one of {sorted(choices)}")
    return value


def _review_measurement(case: dict[str, Any], context: str) -> None:
    dispatches = case["review_dispatches"]
    rounds = case["review_rounds"]
    if (dispatches == 0) != (rounds == 0) or rounds > dispatches:
        _fail(
            context,
            "review measurement requires zero dispatches with zero rounds, "
            "or at least one dispatch per positive round",
        )


def _validate_corpus(corpus: object) -> list[dict[str, Any]]:
    root = _object(corpus, _CORPUS_KEYS, "corpus")
    _choice(root["schema"], {CORPUS_SCHEMA}, "corpus.schema")
    authorization = _object(
        root["authorization"], _AUTHORIZATION_KEYS, "corpus.authorization"
    )
    if type(authorization["authorized"]) is not bool or not authorization["authorized"]:
        _fail("corpus.authorization.authorized", "explicit authorization is required")
    _identifier(authorization["source"], "corpus.authorization.source")
    if type(root["cases"]) is not list or not root["cases"]:
        _fail("corpus.cases", "at least one authorized case is required")

    cases: list[dict[str, Any]] = []
    case_ids: list[str] = []
    for index, raw_case in enumerate(root["cases"]):
        context = f"corpus.cases[{index}]"
        case = _object(raw_case, _CORPUS_CASE_KEYS, context)
        case_id = _identifier(case["case_id"], f"{context}.case_id")
        case_ids.append(case_id)
        _identifier_list(case["task_ids"], f"{context}.task_ids", nonempty=True)
        _identifier_list(case["requirements"], f"{context}.requirements", nonempty=True)
        _identifier_list(case["known_defects"], f"{context}.known_defects")
        _identifier_list(
            case["required_package_gates"],
            f"{context}.required_package_gates",
            nonempty=True,
        )
        path = _choice(
            case["expected_candidate_path"],
            {"eligible_batch", "individual_fallback"},
            f"{context}.expected_candidate_path",
        )
        causes = _identifier_list(
            case["expected_fallback_causes"],
            f"{context}.expected_fallback_causes",
        )
        if path == "eligible_batch" and causes:
            _fail(context, "an eligible Batch cannot require a fallback cause")
        if path == "individual_fallback" and not causes:
            _fail(context, "individual fallback requires at least one oracle cause")
        cases.append(case)
    if len(set(case_ids)) != len(case_ids):
        _fail("corpus.cases", "duplicate case IDs are not allowed")
    return cases


def corpus_identity(corpus: object) -> str:
    """Return the canonical identity of one validated authorized corpus."""
    _validate_corpus(corpus)
    encoded = json.dumps(
        corpus, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _validate_result_case(
    case: dict[str, Any],
    oracle: dict[str, Any],
    *,
    context: str,
    expected_mode: str,
) -> None:
    """Validate one result row against its authorized corpus oracle."""
    for field in (
        "review_dispatches",
        "review_rounds",
        "batch_reopens",
        "elapsed_work_ms",
        "maximum_aggregate_diff_bytes",
    ):
        _count(case[field], f"{context}.{field}")
    _review_measurement(case, context)
    fallback_causes = _identifier_list(
        case["fallback_causes"], f"{context}.fallback_causes"
    )
    _identifier_list(
        case["false_scope_expansions"], f"{context}.false_scope_expansions"
    )
    detected = _identifier_list(
        case["detected_known_defects"], f"{context}.detected_known_defects"
    )
    unknown_defects = sorted(set(detected) - set(oracle["known_defects"]))
    if unknown_defects:
        _fail(context, f"detected defects are outside the corpus oracle: {unknown_defects}")

    trace = case["requirement_to_tests"]
    if type(trace) is not dict:
        _fail(f"{context}.requirement_to_tests", "expected an object")
    if not all(type(key) is str for key in trace):
        _fail(f"{context}.requirement_to_tests", "object keys must be strings")
    if list(trace) != oracle["requirements"]:
        _fail(
            f"{context}.requirement_to_tests",
            "requirement keys and order must exactly match the corpus oracle",
        )
    for requirement, tests in trace.items():
        _identifier(requirement, f"{context}.requirement_to_tests key")
        _identifier_list(tests, f"{context}.requirement_to_tests.{requirement}")

    gates = case["package_gates"]
    if type(gates) is not dict:
        _fail(f"{context}.package_gates", "expected an object")
    if not all(type(key) is str for key in gates):
        _fail(f"{context}.package_gates", "object keys must be strings")
    # `observe` writes no gate verdicts (it measures only review counts), so an
    # empty object means "unmeasured"; anything else must match the oracle.
    if gates and list(gates) != oracle["required_package_gates"]:
        _fail(
            f"{context}.package_gates",
            "gate keys and order must exactly match the corpus oracle",
        )
    for gate_id, verdict in gates.items():
        _identifier(gate_id, f"{context}.package_gates key")
        _choice(verdict, {"PASS", "FAIL"}, f"{context}.package_gates.{gate_id}")

    if expected_mode == "individual" and (
        case["review_dispatches"] == 0 or case["review_rounds"] == 0
    ):
        _fail(context, "baseline requires positive review evidence")
    if expected_mode == "batch":
        path = oracle["expected_candidate_path"]
        if case["review_dispatches"] == 0 or case["review_rounds"] == 0:
            _fail(context, f"{path} requires positive review evidence")
        if path == "eligible_batch":
            if fallback_causes:
                _fail(context, "eligible Batch evidence cannot contain fallback causes")
        elif fallback_causes != oracle["expected_fallback_causes"]:
            _fail(
                context,
                "individual fallback causes must exactly match the corpus oracle",
            )


def _refuse_unobserved(result: object, label: str) -> None:
    """Refuse any result that is not an `observe`-written v2 file, by name.

    Checked before the closed-schema comparison so a declared v1 pilot file
    (or a v2 file with edited provenance) is refused on `schema` /
    `provenance` rather than on a generic key mismatch.
    """
    if type(result) is not dict:
        _fail(label, "expected an object")
    schema = result.get("schema", "<missing>")
    if schema != RESULT_SCHEMA_V2:
        _fail(
            f"{label}.schema",
            f"refused {schema!r} (the declared shape is {RESULT_SCHEMA!r}); "
            f"compare accepts only {RESULT_SCHEMA_V2!r} results written by "
            f"observe (provenance {OBSERVED_PROVENANCE!r})",
        )
    provenance = result.get("provenance", "<missing>")
    if provenance != OBSERVED_PROVENANCE:
        _fail(
            f"{label}.provenance",
            f"refused {provenance!r}; compare accepts only provenance "
            f"{OBSERVED_PROVENANCE!r} results written by observe",
        )


def _validate_result(
    result: object,
    *,
    label: str,
    expected_mode: str,
    identity: str,
    corpus_cases: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    _refuse_unobserved(result, label)
    root = _object(result, _RESULT_KEYS_V2, label)
    if type(root["branch"]) is not str or not root["branch"]:
        _fail(f"{label}.branch", "expected a non-empty branch name")
    if type(root["corpus_identity"]) is not str or _DIGEST.fullmatch(
        root["corpus_identity"]
    ) is None:
        _fail(f"{label}.corpus_identity", "expected a SHA-256 identity")
    if root["corpus_identity"] != identity:
        _fail(f"{label}.corpus_identity", "corpus identity does not match input")
    if type(root["cases"]) is not list:
        _fail(f"{label}.cases", "expected a list")

    result_cases = [
        _object(raw_case, _RESULT_CASE_KEYS_V2, f"{label}.cases[{index}]")
        for index, raw_case in enumerate(root["cases"])
    ]
    expected_case_ids = [case["case_id"] for case in corpus_cases]
    actual_case_ids = [
        _identifier(case["case_id"], f"{label}.cases[{index}].case_id")
        for index, case in enumerate(result_cases)
    ]
    if actual_case_ids != expected_case_ids:
        _fail(
            f"{label}.cases",
            "case IDs and order must exactly match the authorized corpus",
        )

    cases: list[dict[str, Any]] = []
    for index, (case, oracle) in enumerate(zip(result_cases, corpus_cases)):
        context = f"{label}.cases[{index}]"
        _validate_result_case(
            case, oracle, context=context, expected_mode=expected_mode
        )
        cases.append(case)
    return cases


def _metrics(
    cases: list[dict[str, Any]], corpus_cases: list[dict[str, Any]]
) -> dict[str, Any]:
    fallback = Counter(
        cause for case in cases for cause in case["fallback_causes"]
    )
    escaped: list[str] = []
    false_scope: list[str] = []
    trace_by_case: dict[str, dict[str, list[str]]] = {}
    package_gates: dict[str, dict[str, str]] = {}
    covered = 0
    total = 0
    for case, oracle in zip(cases, corpus_cases):
        case_id = case["case_id"]
        escaped.extend(
            f"{case_id}:{defect}"
            for defect in oracle["known_defects"]
            if defect not in case["detected_known_defects"]
        )
        false_scope.extend(
            f"{case_id}:{scope}" for scope in case["false_scope_expansions"]
        )
        trace_by_case[case_id] = case["requirement_to_tests"]
        total += len(oracle["requirements"])
        covered += sum(bool(case["requirement_to_tests"][req]) for req in oracle["requirements"])
        package_gates[case_id] = case["package_gates"]
    return {
        "review_dispatches": sum(case["review_dispatches"] for case in cases),
        "review_rounds": sum(case["review_rounds"] for case in cases),
        "fallback_causes": dict(sorted(fallback.items())),
        "false_scope_expansion": false_scope,
        "escaped_known_defects": escaped,
        "elapsed_work_ms": sum(case["elapsed_work_ms"] for case in cases),
        "maximum_aggregate_diff_bytes": max(
            case["maximum_aggregate_diff_bytes"] for case in cases
        ),
        "requirement_to_test_traceability": {
            "covered_requirements": covered,
            "total_requirements": total,
            "by_case": trace_by_case,
        },
        "package_gates": package_gates,
    }


def _covered_requirements(case: dict[str, Any]) -> set[str]:
    return {
        requirement
        for requirement, tests in case["requirement_to_tests"].items()
        if tests
    }


def _cost_attribution(
    corpus_cases: list[dict[str, Any]],
    baseline_cases: list[dict[str, Any]],
    candidate_cases: list[dict[str, Any]],
) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for path in ("eligible_batch", "individual_fallback"):
        indexes = [
            index
            for index, case in enumerate(corpus_cases)
            if case["expected_candidate_path"] == path
        ]
        baseline_dispatches = sum(
            baseline_cases[index]["review_dispatches"] for index in indexes
        )
        candidate_dispatches = sum(
            candidate_cases[index]["review_dispatches"] for index in indexes
        )
        result[path] = {
            "baseline_review_dispatches": baseline_dispatches,
            "candidate_review_dispatches": candidate_dispatches,
            "saved_review_dispatches": baseline_dispatches - candidate_dispatches,
        }
    return result


def compare(corpus: object, baseline: object, candidate: object) -> dict[str, Any]:
    """Return a deterministic evidence report for one valid comparison."""
    corpus_cases = _validate_corpus(corpus)
    identity = corpus_identity(corpus)
    baseline_cases = _validate_result(
        baseline,
        label="baseline",
        expected_mode="individual",
        identity=identity,
        corpus_cases=corpus_cases,
    )
    candidate_cases = _validate_result(
        candidate,
        label="candidate",
        expected_mode="batch",
        identity=identity,
        corpus_cases=corpus_cases,
    )

    for index, (oracle, before, after) in enumerate(
        zip(corpus_cases, baseline_cases, candidate_cases)
    ):
        if oracle["expected_candidate_path"] != "individual_fallback":
            continue
        if (
            after["review_dispatches"] != before["review_dispatches"]
            or after["review_rounds"] != before["review_rounds"]
        ):
            _fail(
                f"candidate.cases[{index}]",
                "fallback review cost must exactly match baseline individual "
                "review dispatches and rounds",
            )

    baseline_metrics = _metrics(baseline_cases, corpus_cases)
    candidate_metrics = _metrics(candidate_cases, corpus_cases)
    cost_attribution = _cost_attribution(
        corpus_cases, baseline_cases, candidate_cases
    )
    safety: list[str] = []
    for oracle, before, after in zip(corpus_cases, baseline_cases, candidate_cases):
        case_id = oracle["case_id"]
        before_escaped = set(oracle["known_defects"]) - set(
            before["detected_known_defects"]
        )
        after_escaped = set(oracle["known_defects"]) - set(
            after["detected_known_defects"]
        )
        safety.extend(
            f"escaped_known_defect:{case_id}:{defect}"
            for defect in sorted(after_escaped - before_escaped)
        )
        safety.extend(
            f"traceability_regression:{case_id}:{requirement}"
            for requirement in sorted(
                _covered_requirements(before) - _covered_requirements(after)
            )
        )
        safety.extend(
            f"false_scope_expansion:{case_id}:{scope}"
            for scope in sorted(
                set(after["false_scope_expansions"])
                - set(before["false_scope_expansions"])
            )
        )
        for gate_id in oracle["required_package_gates"]:
            # An unmeasured gate (empty object from observe) is neither PASS
            # nor FAIL; only a recorded verdict can regress.
            if before["package_gates"].get(gate_id, "PASS") == "FAIL":
                safety.append(f"baseline_package_gate_failure:{case_id}:{gate_id}")
            if after["package_gates"].get(gate_id, "PASS") == "FAIL":
                safety.append(f"package_gate_failure:{case_id}:{gate_id}")
        if oracle["expected_candidate_path"] == "individual_fallback":
            missing = set(oracle["expected_fallback_causes"]) - set(
                after["fallback_causes"]
            )
            safety.extend(
                f"missing_expected_fallback:{case_id}:{cause}"
                for cause in sorted(missing)
            )

    cost = []
    if candidate_metrics["review_dispatches"] >= baseline_metrics["review_dispatches"]:
        cost.append("no_review_dispatch_reduction")
    if cost_attribution["eligible_batch"]["saved_review_dispatches"] <= 0:
        cost.append("no_eligible_batch_dispatch_reduction")
    verdict = "PASS" if not safety and not cost else "FAIL"
    return {
        "schema": REPORT_SCHEMA,
        "verdict": verdict,
        "corpus_identity": identity,
        "case_ids": [case["case_id"] for case in corpus_cases],
        "baseline": baseline_metrics,
        "candidate": candidate_metrics,
        "cost_attribution": cost_attribution,
        "safety_regressions": safety,
        "cost_regressions": cost,
    }


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ReplayInputError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def _read_json(path: Path, label: str) -> object:
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ReplayInputError(f"{label}: cannot read {path}: {exc}") from exc
    try:
        return json.loads(raw, object_pairs_hook=_unique_json_object)
    except ReplayInputError as exc:
        raise ReplayInputError(f"{label}: {exc}") from exc
    except (json.JSONDecodeError, RecursionError) as exc:
        raise ReplayInputError(f"{label}: invalid JSON: {exc}") from exc


def read_dispatch_log(path: Path) -> list[dict[str, Any]]:
    """Return every ``review-dispatch-log/v1`` line of ``path``, validated.

    The only reader of the dispatch log in this module: a malformed line
    refuses, naming its 1-based line number.
    """
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ReplayInputError(f"dispatch log: cannot read {path}: {exc}") from exc
    entries: list[dict[str, Any]] = []
    for number, line in enumerate(raw.splitlines(), start=1):
        context = f"dispatch log line {number}"
        try:
            entry = json.loads(line, object_pairs_hook=_unique_json_object)
        except ReplayInputError as exc:
            raise ReplayInputError(f"{context}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise ReplayInputError(f"{context}: invalid JSON: {exc}") from exc
        _object(entry, _DISPATCH_LOG_KEYS, context)
        _choice(entry["schema"], {review_context.DISPATCH_LOG_SCHEMA}, f"{context}.schema")
        for key in ("recorded_at", "branch", "plugin_version"):
            if type(entry[key]) is not str or not entry[key]:
                _fail(f"{context}.{key}", "expected a non-empty string")
        if type(entry["reviewed_sha"]) is not str or (
            review_context.SHA_PATTERN.fullmatch(entry["reviewed_sha"]) is None
        ):
            _fail(f"{context}.reviewed_sha", "expected a 40-hex commit sha")
        entries.append(entry)
    return entries


def _count_reopens(receipts_dir: Path | None) -> int:
    """Count receipts under ``receipts_dir`` whose applied action was reopen."""
    if receipts_dir is None:
        return 0
    if not receipts_dir.is_dir():
        _fail("receipts", f"{receipts_dir} is not a directory")
    reopens = 0
    for receipt_path in sorted(receipts_dir.glob("*.json")):
        receipt = _read_json(receipt_path, f"receipt {receipt_path.name}")
        if type(receipt) is not dict:
            _fail(f"receipt {receipt_path.name}", "expected an object")
        if receipt.get("applied_action") == "reopen":
            reopens += 1
    return reopens


def _observed_counts(
    log: Path, branch: str, receipts_dir: Path | None
) -> dict[str, int]:
    matching = [entry for entry in read_dispatch_log(log) if entry["branch"] == branch]
    return {
        "review_dispatches": len(matching),
        "review_rounds": len({entry["reviewed_sha"] for entry in matching}),
        "batch_reopens": _count_reopens(receipts_dir),
    }


def _summary_line(counts: dict[str, int], reopens_measured: bool) -> str:
    # Without `--receipts` nobody counted reopens; the relayed line must not
    # read as a measured zero (the v2 file still carries 0 by schema).
    reopens = counts["batch_reopens"] if reopens_measured else "unmeasured"
    return (
        f"observed reviewer fan-outs: {counts['review_dispatches']} "
        f"(rounds {counts['review_rounds']}, batch reopens {reopens})"
    )


def observe(corpus: object, branch: str, counts: dict[str, int]) -> dict[str, Any]:
    """Return the v2 result binding observed counts to the corpus's one case."""
    cases = _validate_corpus(corpus)
    if len(cases) != 1:
        _fail("corpus.cases", "observe attributes counts to exactly one case")
    (oracle,) = cases
    # Only the review counts are observed; every other v1 case field stays at
    # its empty value rather than carrying a number nobody measured.
    case = {
        "case_id": oracle["case_id"],
        **counts,
        "fallback_causes": [],
        "false_scope_expansions": [],
        "detected_known_defects": [],
        "elapsed_work_ms": 0,
        "maximum_aggregate_diff_bytes": 0,
        "requirement_to_tests": {req: [] for req in oracle["requirements"]},
        "package_gates": {},
    }
    return {
        "schema": RESULT_SCHEMA_V2,
        "provenance": OBSERVED_PROVENANCE,
        "corpus_identity": corpus_identity(corpus),
        "branch": branch,
        "cases": [case],
    }


def _run_observe(args: argparse.Namespace) -> int:
    if args.summary:
        if not args.log.exists():
            print(SUMMARY_NO_LOG)
            return 0
        counts = _observed_counts(args.log, args.branch, args.receipts)
        print(_summary_line(counts, args.receipts is not None))
        return 0
    if args.corpus is None or args.out is None:
        _fail("observe", "--corpus and --out are required without --summary")
    result = observe(
        _read_json(args.corpus, "corpus"),
        args.branch,
        _observed_counts(args.log, args.branch, args.receipts),
    )
    args.out.write_text(
        json.dumps(result, ensure_ascii=True, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


def _run_compare(args: argparse.Namespace) -> int:
    report = compare(
        _read_json(args.corpus, "corpus"),
        _read_json(args.baseline, "baseline"),
        _read_json(args.candidate, "candidate"),
    )
    print(json.dumps(report, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return 0 if report["verdict"] == "PASS" else 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    compare_parser = subparsers.add_parser(
        "compare", help="compare two result files on one authorized corpus"
    )
    compare_parser.add_argument("--corpus", type=Path, required=True)
    compare_parser.add_argument("--baseline", type=Path, required=True)
    compare_parser.add_argument("--candidate", type=Path, required=True)
    observe_parser = subparsers.add_parser(
        "observe", help="derive an observed v2 result file from the dispatch log"
    )
    observe_parser.add_argument("--log", type=Path, required=True)
    observe_parser.add_argument("--branch", required=True)
    observe_parser.add_argument("--corpus", type=Path)
    observe_parser.add_argument("--out", type=Path)
    observe_parser.add_argument("--receipts", type=Path)
    observe_parser.add_argument(
        "--summary",
        action="store_true",
        help="print the one-line count instead of writing a result file",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "observe":
            return _run_observe(args)
        return _run_compare(args)
    except (ReplayInputError, OSError) as exc:
        # OSError: an observe path (log / receipts / --out) the OS refused;
        # fail loud at the CLI boundary rather than tracebacking.
        print(f"task-batch-replay: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
