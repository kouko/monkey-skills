#!/usr/bin/env python3
"""Verdict CLI for the wiki-update mechanical fix loop (T2, brief
docs/loom/specs/2026-07-23-wiki-update-maintenance-loop.md Decision 2).

ORIGIN NOTE (bounded duplication, disclosed): adapted from
``loom-product-principles/scripts/improve_loop_verdict.py`` — same
exit-code-verdict skeleton (MalformedInputError, pure verdict
functions, ``_cmd_*`` wrappers, silent accept path) — but the input
surface is fully swapped: this CLI consumes ``wiki_lint_check.py``
JSONL round files (violation records + conservation counters +
summary), not replay-matrix row-sets. Extraction to a shared skeleton
is parked in docs/loom/BACKLOG.md with a Rule-of-Three re-trigger
(plan Notes, docs/loom/plans/2026-07-23-wiki-update-loop.md).

INPUT FORMAT: every round argument is a path to one
``wiki_lint_check.py`` JSONL output file. Each line is a JSON object
whose ``type`` is one of:

  {"type": "violation", "check_id", "severity", "file", "line", "detail"}
  {"type": "counters", "file", "words", "links", "headings"}
  {"type": "summary", "files", "violations", "errors", "warnings", "by_check"}

``check_id`` values OUTSIDE the SSOT check list — notably ``PARSE``
(error-lane: unreadable file / frontmatter defect) — COUNT as
violations; the verdicts below never filter by check id. A round file
must contain exactly one summary record whose ``violations`` count
equals the number of violation records present (truncation guard);
any other shape — missing file, invalid JSON line, non-object line,
unknown ``type``, duplicate/absent summary, count mismatch — is
malformed input.

Exit codes are GLOBALLY DISTINCT across verbs so the loop engine
(``wiki_fix_loop.js``, T3) can pass them through unambiguously:

  0  ok — win / within budget / continue / not stuck / no breach
  1  ``compare``: no-win (candidate violation count not lower)
  2  malformed input (any verb), or a named file does not exist
  3  ``plateau``: stop — K consecutive rounds without improvement
  4  ``budget``: stop — round cap (or token cap) exhausted
  5  ``stuck``: same failure fingerprint — sha256 over the sorted
     (check_id, file) pair set — for --strikes consecutive rounds,
     UNLESS the violation total strictly declined across that window
     (converging on one violation class is progress, not stuckness)
  6  ``stuck``: no-new-info round — the latest round's violation
     records are exactly the previous round's (nothing changed)
  7  ``stuck``: regression — latest violation count ROSE vs previous
  8  ``ratchet``: breach — a conservation counter aggregate (words /
     links / headings summed across files) net-decreased with no
     ``--justification`` file supplied

``stuck`` precedence when several conditions hold at once:
regression (7) > fingerprint strikes (5) > no-new-info (6).

Verbs:
  compare  --baseline R.jsonl --candidate R.jsonl     round N-1 vs N
  plateau  --rounds R.jsonl ... [--k 3]               K-round brake
  budget   --round N --max-rounds M
           [--spent-tokens T --max-tokens TM]         hard caps
  stuck    --rounds R.jsonl ... [--strikes 3]         3 stuck kinds
  ratchet  --baseline R.jsonl --candidate R.jsonl
           [--justification PATH]                     conservation

Verdict paths are zero-LLM by design: never printing on the ok path,
stderr one-liners on stop paths. Stdlib only (plugin
self-containment).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_NO_WIN = 1
EXIT_MALFORMED = 2
EXIT_PLATEAU = 3
EXIT_BUDGET = 4
EXIT_STUCK_FINGERPRINT = 5
EXIT_STUCK_NO_NEW_INFO = 6
EXIT_STUCK_REGRESSION = 7
EXIT_RATCHET_BREACH = 8

COUNTER_KEYS = ("words", "links", "headings")


class MalformedInputError(ValueError):
    """Raised for any input that fails the round-file contract above."""


# ---------------------------------------------------------------- loading

def load_round(path: str) -> dict:
    """Read one wiki_lint_check.py JSONL round file. Returns
    ``{"violations": [...], "counters": [...], "summary": {...}}``.
    Raises MalformedInputError on a missing file, an invalid or
    non-object JSON line, an unknown record type, a duplicate or
    missing summary record, or a summary whose ``violations`` count
    does not match the violation records present (truncation guard)."""
    file_path = Path(path)
    if not file_path.is_file():
        raise MalformedInputError(f"file not found: {path}")
    violations, counters, summary = [], [], None
    for lineno, line in enumerate(
            file_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise MalformedInputError(
                f"invalid JSON on {path}:{lineno}: {exc}") from exc
        if not isinstance(record, dict):
            raise MalformedInputError(
                f"non-object JSONL record on {path}:{lineno}")
        rtype = record.get("type")
        if rtype == "violation":
            if not isinstance(record.get("check_id"), str) \
                    or not isinstance(record.get("file"), str):
                raise MalformedInputError(
                    f"violation record missing str 'check_id'/'file' on "
                    f"{path}:{lineno}: {record!r}")
            violations.append(record)
        elif rtype == "counters":
            counters.append(record)
        elif rtype == "summary":
            if summary is not None:
                raise MalformedInputError(
                    f"duplicate summary record on {path}:{lineno}")
            summary = record
        else:
            raise MalformedInputError(
                f"unknown record type {rtype!r} on {path}:{lineno}")
    if summary is None:
        raise MalformedInputError(f"no summary record in {path} (truncated?)")
    if summary.get("violations") != len(violations):
        raise MalformedInputError(
            f"summary violations={summary.get('violations')!r} but "
            f"{len(violations)} violation records present in {path} "
            "(truncated?)")
    return {"violations": violations, "counters": counters,
            "summary": summary}


def violation_count(round_data: dict) -> int:
    return len(round_data["violations"])


def fingerprint(round_data: dict) -> str:
    """sha256 hexdigest over the sorted set of (check_id, file) pairs —
    the round's failure signature (counts/details/lines excluded)."""
    pairs = sorted({(v.get("check_id"), v.get("file"))
                    for v in round_data["violations"]})
    canonical = json.dumps(pairs, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _violation_multiset(round_data: dict) -> list:
    return sorted(json.dumps(v, sort_keys=True, ensure_ascii=False)
                  for v in round_data["violations"])


def counter_totals(round_data: dict) -> dict:
    """Aggregate conservation counters across files: {key: total}."""
    totals = dict.fromkeys(COUNTER_KEYS, 0)
    for record in round_data["counters"]:
        for key in COUNTER_KEYS:
            value = record.get(key)
            if type(value) is not int:  # bool is an int subclass — reject it
                raise MalformedInputError(
                    f"counters record missing int {key!r}: {record!r}")
            totals[key] += value
    return totals


# ---------------------------------------------------------------- verdicts

def compare_verdict(baseline: dict, candidate: dict) -> int:
    """Win iff the candidate round has strictly fewer violations."""
    if violation_count(candidate) < violation_count(baseline):
        return EXIT_OK
    return EXIT_NO_WIN


def plateau_verdict(rounds: list, k: int) -> int:
    """Stop iff the last k round transitions ALL failed to improve
    (violation count never decreased). Fewer than k transitions in the
    history always continues."""
    if k < 1:
        raise MalformedInputError("--k must be >= 1")
    counts = [violation_count(r) for r in rounds]
    if len(counts) < k + 1:
        return EXIT_OK
    recent = counts[-(k + 1):]
    improved = any(recent[i] < recent[i - 1] for i in range(1, len(recent)))
    return EXIT_OK if improved else EXIT_PLATEAU


def budget_verdict(rounds_completed: int, max_rounds: int,
                   spent_tokens: int | None,
                   max_tokens: int | None) -> int:
    """Stop when rounds completed reach --max-rounds, or (when both
    token args are given) spent tokens exceed --max-tokens."""
    if rounds_completed < 0 or max_rounds <= 0:
        raise MalformedInputError(
            "--round must be >= 0 and --max-rounds must be > 0")
    if (spent_tokens is None) != (max_tokens is None):
        raise MalformedInputError(
            "--spent-tokens and --max-tokens must be given together")
    if rounds_completed >= max_rounds:
        return EXIT_BUDGET
    if spent_tokens is not None and spent_tokens > max_tokens:
        return EXIT_BUDGET
    return EXIT_OK


def stuck_verdict(rounds: list, strikes: int) -> int:
    """Three stuck kinds, checked in precedence order:
    regression (7) > fingerprint strikes (5) > no-new-info (6).
    Fewer than 2 rounds of history is never stuck. A shared fingerprint
    is NOT a strike while the violation total is strictly declining
    across the strike window — converging on one violation class
    (e.g. 5 -> 3 -> 1 broken links) is progress, not stuckness."""
    if strikes < 1:
        raise MalformedInputError("--strikes must be >= 1")
    if len(rounds) < 2:
        return EXIT_OK
    if violation_count(rounds[-1]) > violation_count(rounds[-2]):
        return EXIT_STUCK_REGRESSION
    if len(rounds) >= strikes:
        window = rounds[-strikes:]
        prints = [fingerprint(r) for r in window]
        converging = violation_count(window[0]) > violation_count(window[-1])
        if len(set(prints)) == 1 and not converging:
            return EXIT_STUCK_FINGERPRINT
    if _violation_multiset(rounds[-1]) == _violation_multiset(rounds[-2]):
        return EXIT_STUCK_NO_NEW_INFO
    return EXIT_OK


def ratchet_verdict(baseline: dict, candidate: dict,
                    justification: str | None) -> int:
    """Breach iff any conservation aggregate (words/links/headings,
    summed across files) net-decreases and no justification file is
    supplied. A supplied --justification path MUST exist (else
    malformed)."""
    if justification is not None and not Path(justification).is_file():
        raise MalformedInputError(
            f"justification file not found: {justification}")
    base_totals = counter_totals(baseline)
    cand_totals = counter_totals(candidate)
    decreased = sorted(k for k in COUNTER_KEYS
                       if cand_totals[k] < base_totals[k])
    if decreased and justification is None:
        return EXIT_RATCHET_BREACH
    return EXIT_OK


# ---------------------------------------------------------------- commands

def _cmd_compare(args) -> int:
    try:
        baseline = load_round(args.baseline)
        candidate = load_round(args.candidate)
    except MalformedInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_MALFORMED
    code = compare_verdict(baseline, candidate)
    if code:
        print(f"no-win: candidate violations {violation_count(candidate)} "
              f">= baseline {violation_count(baseline)}", file=sys.stderr)
    return code


def _cmd_plateau(args) -> int:
    try:
        rounds = [load_round(p) for p in args.rounds]
        code = plateau_verdict(rounds, args.k)
    except MalformedInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_MALFORMED
    if code:
        print(f"plateau: last {args.k} rounds never improved — stop",
              file=sys.stderr)
    return code


def _cmd_budget(args) -> int:
    try:
        code = budget_verdict(args.round, args.max_rounds,
                              args.spent_tokens, args.max_tokens)
    except MalformedInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_MALFORMED
    if code:
        print(f"budget: exhausted (round {args.round}/{args.max_rounds}"
              + (f", tokens {args.spent_tokens}/{args.max_tokens}"
                 if args.spent_tokens is not None else "")
              + ") — stop", file=sys.stderr)
    return code


def _cmd_stuck(args) -> int:
    try:
        rounds = [load_round(p) for p in args.rounds]
        code = stuck_verdict(rounds, args.strikes)
    except MalformedInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_MALFORMED
    if code == EXIT_STUCK_REGRESSION:
        print(f"stuck: regression — violations rose "
              f"{violation_count(rounds[-2])} -> "
              f"{violation_count(rounds[-1])}", file=sys.stderr)
    elif code == EXIT_STUCK_FINGERPRINT:
        print(f"stuck: same failure fingerprint "
              f"{fingerprint(rounds[-1])[:12]}… for {args.strikes} "
              "consecutive rounds", file=sys.stderr)
    elif code == EXIT_STUCK_NO_NEW_INFO:
        print("stuck: no-new-info round — violation records identical "
              "to previous round", file=sys.stderr)
    return code


def _cmd_ratchet(args) -> int:
    try:
        baseline = load_round(args.baseline)
        candidate = load_round(args.candidate)
        code = ratchet_verdict(baseline, candidate, args.justification)
    except MalformedInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_MALFORMED
    if code:
        base_totals = counter_totals(baseline)
        cand_totals = counter_totals(candidate)
        drops = ", ".join(f"{k} {base_totals[k]}->{cand_totals[k]}"
                          for k in COUNTER_KEYS
                          if cand_totals[k] < base_totals[k])
        print(f"ratchet breach: net decrease without justification "
              f"({drops})", file=sys.stderr)
    return code


# ---------------------------------------------------------------- parser

def _add_compare_parser(subparsers) -> None:
    p = subparsers.add_parser(
        "compare",
        help="round N vs N-1: win iff candidate has strictly fewer violations")
    p.add_argument("--baseline", required=True, metavar="PATH",
                   help="round N-1 wiki_lint_check JSONL file")
    p.add_argument("--candidate", required=True, metavar="PATH",
                   help="round N wiki_lint_check JSONL file")
    p.epilog = "Exit codes: 0 win, 1 no-win, 2 malformed input."
    p.set_defaults(func=_cmd_compare)


def _add_plateau_parser(subparsers) -> None:
    p = subparsers.add_parser(
        "plateau",
        help="stop after K consecutive rounds without improvement")
    p.add_argument("--rounds", nargs="+", required=True, metavar="PATH",
                   help="round JSONL files in chronological order")
    p.add_argument("--k", type=int, default=3, metavar="K",
                   help="consecutive no-improvement rounds to stop (default 3)")
    p.epilog = "Exit codes: 0 continue, 3 plateau stop, 2 malformed input."
    p.set_defaults(func=_cmd_plateau)


def _add_budget_parser(subparsers) -> None:
    p = subparsers.add_parser(
        "budget", help="stop on round cap (and optional token cap)")
    p.add_argument("--round", type=int, required=True, metavar="N",
                   help="rounds completed so far")
    p.add_argument("--max-rounds", type=int, required=True, metavar="M",
                   help="round hard cap; stop when completed >= cap")
    p.add_argument("--spent-tokens", type=int, default=None, metavar="T",
                   help="tokens spent so far (requires --max-tokens)")
    p.add_argument("--max-tokens", type=int, default=None, metavar="TM",
                   help="token hard cap (requires --spent-tokens)")
    p.epilog = "Exit codes: 0 within budget, 4 budget stop, 2 malformed input."
    p.set_defaults(func=_cmd_budget)


def _add_stuck_parser(subparsers) -> None:
    p = subparsers.add_parser(
        "stuck",
        help="three stuck kinds: regression / same-fingerprint / no-new-info")
    p.add_argument("--rounds", nargs="+", required=True, metavar="PATH",
                   help="round JSONL files in chronological order")
    p.add_argument("--strikes", type=int, default=3, metavar="S",
                   help="consecutive same-fingerprint rounds to stop (default 3)")
    p.epilog = ("Exit codes: 0 not stuck, 5 fingerprint strikes, "
                "6 no-new-info, 7 regression, 2 malformed input. "
                "Precedence: 7 > 5 > 6.")
    p.set_defaults(func=_cmd_stuck)


def _add_ratchet_parser(subparsers) -> None:
    p = subparsers.add_parser(
        "ratchet",
        help="conservation counters may not net-decrease without a "
             "justification file")
    p.add_argument("--baseline", required=True, metavar="PATH",
                   help="round N-1 wiki_lint_check JSONL file")
    p.add_argument("--candidate", required=True, metavar="PATH",
                   help="round N wiki_lint_check JSONL file")
    p.add_argument("--justification", default=None, metavar="PATH",
                   help="flagged justification file sanctioning a decrease")
    p.epilog = "Exit codes: 0 no breach, 8 ratchet breach, 2 malformed input."
    p.set_defaults(func=_cmd_ratchet)


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verdict CLI for the wiki-update fix loop: 'compare' "
                    "judges one round (fewer violations = win); 'plateau', "
                    "'budget', 'stuck' are the brakes; 'ratchet' guards the "
                    "conservation counters. Exit codes are globally "
                    "distinct — see module docstring.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    _add_compare_parser(subparsers)
    _add_plateau_parser(subparsers)
    _add_budget_parser(subparsers)
    _add_stuck_parser(subparsers)
    _add_ratchet_parser(subparsers)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
