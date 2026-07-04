"""Behavioral firing/refusal test harness for the loom-* skill family.

Rebuilds the ad-hoc harness from the 2026-06-24/25 firing/refusal audit
(memory: project_loom_firing_test_router_asymmetry) as versioned,
tested scripts instead of scratchpad throwaways. That audit's method
write-up documented five traps that nearly produced false conclusions
(a sixth was added when the shipped corpora landed, Task F2); each is
named here with the layer that guards against it:

1. **max-turns too tight** — `--max-turns 1` makes orient-first queries
   hit the turn ceiling, which misreads as a trigger-miss. Enforced by
   the `run` mode (Task F1c): a floor of 4 turns, refused below it.
2. **context-less clarify-first != trigger-miss** — a query with no
   context makes the model ask a clarifying question instead of
   routing; that reads as a false miss. Enforced here by
   `validate_corpus`: it WARNS (never fails) on suspiciously short
   queries (< ~15 chars, a heuristic — real self-contained queries are
   almost always longer) so a corpus author can reword before running.
3. **session/rate-limit silently contaminates** — a session-limit or
   error response can produce a whole "miss" verdict that has nothing
   to do with routing. Enforced here by `filter_contaminated`: any
   run-result record whose `result_subtype` signals a true run failure
   (harness_error, unknown subtypes), or whose raw text mentions a
   session limit, is DISCARDED and excluded from grading; the discard
   count is always surfaced, never swallowed. `error_max_turns` is NOT
   contamination — a session that fires a skill and keeps working past
   the turn cap is a success signal, graded normally (F3
   accounting-debt fix; the old success-only filter dropped 6/28
   records that all had useful fires).
4. **grader must separate EXACT / FAMILY and gate OVER correctly** —
   expected=NONE must only penalize a LOOM-family fire (a correct
   non-loom routing is not an over-trigger), and a sibling-skill fire
   in the same loom family must be counted as FAMILY, not folded into
   EXACT. Enforced by the `grade` mode (Task F1b).
5. **real transcripts yield few clean triggers** — corpora must be
   description-derived intent phrasings, seasoned with the few real
   natural triggers, not mined wholesale from transcripts (mostly
   "go/OK" continuations). Enforced by hand-authored corpus files
   (Task F2), validated through `validate_corpus`.
6. **goal-oriented corpus grades routing only; recommendation-surfacing
   requires F3's transcript check on every reuse** — every record in
   `docs/loom/firing-corpus/goal-oriented.jsonl` expects
   `loom-code:using-loom-code`, so fired-skill grading alone CANNOT
   catch a design-side on-ramp regression (deleting brainstorming's
   Axis 0 would not move a single record off EXACT/FAMILY). That
   corpus's real acceptance criterion is whether the design-side
   recommendation SURFACES in the transcript text — an inspection this
   harness does not automate; F3 (and any future reuse of that corpus)
   must read the transcripts, not just the grade table.

This module implements the corpus layer (parsing + contamination
filtering, Task F1a), the grader (Task F1b), and the `run` mode (Task
F1c) that shells out to the live `claude` CLI and merges its output
onto corpus records so `grade_corpus` can consume them directly.

Stdlib only.
"""

import argparse
import json
import subprocess
import sys

_SELF_CONTAINED_MIN_LEN = 15
_REQUIRED_FIELDS = ("query", "expected", "notes")


class CorpusError(Exception):
    """Raised when a corpus line is malformed (fail loud, never guess)."""


def parse_corpus(raw: str) -> list[dict]:
    """Parse a JSONL corpus: one record per non-empty line.

    Each record must be a JSON object with `query` (str), `expected`
    (str — a "<plugin:skill>" id or the literal "NONE"), and `notes`
    (str). Raises `CorpusError` on any line that isn't valid JSON or is
    missing a required field — never silently skips or guesses.
    """
    records = []
    for lineno, line in enumerate(raw.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CorpusError(f"corpus line {lineno}: invalid JSON: {exc}") from exc
        if not isinstance(record, dict):
            raise CorpusError(f"corpus line {lineno}: expected a JSON object")
        missing = [f for f in _REQUIRED_FIELDS if f not in record]
        if missing:
            raise CorpusError(
                f"corpus line {lineno}: missing required field(s): {missing}"
            )
        records.append(record)
    return records


def validate_corpus(records: list[dict]) -> list[str]:
    """Self-containedness check (trap #2): warn, never fail.

    Returns one warning string per record whose `query` is shorter
    than `_SELF_CONTAINED_MIN_LEN` chars — a heuristic proxy for
    "lacks enough context to avoid a clarify-first response." Callers
    decide what to do with warnings; this never raises.
    """
    warnings = []
    for record in records:
        query = record.get("query", "")
        if len(query) < _SELF_CONTAINED_MIN_LEN:
            warnings.append(
                f"query too short (< {_SELF_CONTAINED_MIN_LEN} chars), "
                f"may not be self-contained: {query!r}"
            )
    return warnings


# Subtypes that carry a valid routing signal — rationale in the module
# docstring, trap #3.
_GRADEABLE_SUBTYPES = frozenset({"success", "error_max_turns"})


def _is_contaminated(record: dict) -> bool:
    subtype = str(record.get("result_subtype", ""))
    text = str(record.get("text", ""))
    if subtype not in _GRADEABLE_SUBTYPES:
        return True
    if "session limit" in text.lower():
        return True
    return False


def filter_contaminated(run_results: list[dict]) -> tuple[list[dict], int]:
    """Contamination filter (trap #3): discard true run failures only.

    A record is discarded if its `result_subtype` is outside
    `_GRADEABLE_SUBTYPES` (harness_error, unknown/absent subtypes), or
    if its `text` mentions a session limit (case-insensitive) — either
    signals the run itself failed, not that routing failed.
    "error_max_turns" records are KEPT and graded normally (see module
    docstring, trap #3). Returns `(kept_records, discarded_count)`;
    the count must always be surfaced by callers, never swallowed.
    """
    kept = [r for r in run_results if not _is_contaminated(r)]
    discarded_count = len(run_results) - len(kept)
    return kept, discarded_count


def _family(skill_id: str) -> str:
    """Plugin prefix before ':' (the loom-family grouping key)."""
    return skill_id.split(":", 1)[0]


def _is_loom_skill(skill_id) -> bool:
    """A fired skill counts as loom-family iff its prefix starts with 'loom'."""
    if not skill_id:
        return False
    return _family(skill_id).startswith("loom")


def grade_record(record: dict) -> str:
    """Grade one merged corpus+run record (trap #4).

    `record["expected"]` is a "<plugin:skill>" id or the literal
    "NONE" (from the corpus); `record["fired"]` is the skill id the
    run captured, or None/falsy if nothing fired.

    Returns one of:
    - "EXACT" — fired == expected, OR expected is "NONE" and no
      loom-family skill fired (a non-loom fire, or nothing firing, is
      the CORRECT outcome for expected=NONE — trap #4's grader rule:
      it must never be scored as an over-trigger).
    - "FAMILY" — fired is a DIFFERENT skill than expected, but shares
      its plugin prefix (same loom family) — counted separately from
      EXACT, never folded in.
    - "MISS" — expected named a skill, and nothing fired, or a skill
      fired that is neither an exact nor a same-family match.
    - "OVER" — expected is "NONE", but a loom-family skill fired
      anyway.
    """
    expected = record["expected"]
    fired = record.get("fired")

    if expected == "NONE":
        if _is_loom_skill(fired):
            return "OVER"
        return "EXACT"

    if fired == expected:
        return "EXACT"
    if _is_loom_skill(fired) and _family(fired) == _family(expected):
        return "FAMILY"
    return "MISS"


def grade_corpus(
    records: list[dict], discarded_count: int = 0, unparsed_lines: int = 0
) -> dict:
    """Per-corpus aggregate: a count per verdict class.

    `discarded_count` passes through the contamination filter's count
    (Task F1a) and `unparsed_lines` passes through the caller's sum of
    per-record skipped-noise counts (over ALL records, including
    discarded ones — their noise still happened), so both are always
    surfaced alongside the grade, never computed or swallowed here.
    """
    counts = {"EXACT": 0, "FAMILY": 0, "MISS": 0, "OVER": 0}
    for record in records:
        counts[grade_record(record)] += 1
    counts["discarded"] = discarded_count
    counts["unparsed_lines"] = unparsed_lines
    return counts


_MAX_TURNS_FLOOR = 4


class MaxTurnsBelowFloorError(Exception):
    """Raised when --max-turns is set below the floor (trap #1).

    A too-tight turn ceiling makes orient-first queries hit the turn
    ceiling, which misreads as a trigger-miss (see module docstring,
    trap #1). Refused before any subprocess call is made.
    """


def _extract_fired_skill(stream_events: list[dict]):
    """First `Skill` tool_use `.input.skill` across the transcript.

    Chronologically FIRST, not "first loom-relevant": grading cares
    about the model's initial routing decision, so a later exploratory
    dispatch (loom or not) must not overwrite that signal.
    """
    for event in stream_events:
        if event.get("type") != "assistant":
            continue
        for block in event.get("message", {}).get("content", []):
            if block.get("type") == "tool_use" and block.get("name") == "Skill":
                return block.get("input", {}).get("skill")
    return None


def _extract_result(stream_events: list[dict]) -> tuple[str, str]:
    """(subtype, text) from the terminal `result` event, or ("", "") if absent."""
    for event in stream_events:
        if event.get("type") == "result":
            return event.get("subtype", ""), event.get("result", "")
    return "", ""


def _parse_stream_json_lines(stdout: str) -> tuple[list[dict], int]:
    """Parse stream-json lines tolerantly: skip non-JSON noise, count it.

    Verbose CLI output can interleave banners/noise lines that aren't
    JSON at all. Crashing the whole record on one such line would be
    worse than skipping it — but the skip must never be silent, so the
    count of skipped lines is returned alongside the parsed events for
    the caller to surface as `unparsed_lines`.
    """
    events = []
    unparsed = 0
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            unparsed += 1
    return events, unparsed


def run_one(record: dict, claude_bin: str = "claude", max_turns: int = 4) -> dict:
    """Shell out to `claude -p` for one corpus record; merge run results.

    Runs `claude -p "<query>" --max-turns <N> --allowedTools Skill
    --output-format stream-json --verbose` as a list-form subprocess
    (no shell=True), tolerantly parses the stream-json lines (skipping
    non-JSON noise, counting it into `unparsed_lines` — never silent),
    and merges `fired` (the captured skill id or None), `result_subtype`,
    `text`, and `unparsed_lines` onto a copy of `record` — the field
    contract `grade_record` and `_is_contaminated` read.

    Raises `MaxTurnsBelowFloorError` if `max_turns` < 4 (trap #1).
    """
    if max_turns < _MAX_TURNS_FLOOR:
        raise MaxTurnsBelowFloorError(
            f"--max-turns {max_turns} is below the floor of "
            f"{_MAX_TURNS_FLOOR} (trap #1: too-tight turns misread "
            "orient-first queries as trigger-misses)"
        )
    argv = [
        claude_bin,
        "-p",
        record["query"],
        "--max-turns",
        str(max_turns),
        "--allowedTools",
        "Skill",
        "--output-format",
        "stream-json",
        "--verbose",
    ]
    proc = subprocess.run(argv, capture_output=True, text=True, check=False)
    events, unparsed_lines = _parse_stream_json_lines(proc.stdout)
    fired = _extract_fired_skill(events)
    subtype, text = _extract_result(events)
    return {
        **record,
        "fired": fired,
        "result_subtype": subtype,
        "text": text,
        "unparsed_lines": unparsed_lines,
    }


def run_corpus(
    records: list[dict], claude_bin: str = "claude", max_turns: int = 4
) -> list[dict]:
    """Run every corpus record through `run_one`; isolate per-record failures.

    A misconfigured `max_turns` (below the floor) still fails the whole
    batch fast and loud — that's a batch-level config error, not a
    per-record runtime failure. But if an individual record's subprocess
    call or parsing raises, that record is captured as
    `{"result_subtype": "harness_error", "text": <error>}` instead of
    aborting the rest of the batch (trap #3's sibling: a flaky single
    call should not lose every other record's signal). The contamination
    filter (`filter_contaminated`) then discards `harness_error` records
    downstream, same as any other non-gradeable subtype.
    """
    if max_turns < _MAX_TURNS_FLOOR:
        raise MaxTurnsBelowFloorError(
            f"--max-turns {max_turns} is below the floor of "
            f"{_MAX_TURNS_FLOOR} (trap #1: too-tight turns misread "
            "orient-first queries as trigger-misses)"
        )
    results = []
    for record in records:
        try:
            results.append(run_one(record, claude_bin=claude_bin, max_turns=max_turns))
        except Exception as exc:  # noqa: BLE001 - isolate any per-record failure
            results.append({**record, "fired": None, "result_subtype": "harness_error", "text": str(exc)})
    return results


def _cmd_run(args: argparse.Namespace) -> None:
    with open(args.corpus, encoding="utf-8") as f:
        records = parse_corpus(f.read())
    results = run_corpus(records, max_turns=args.max_turns)
    output = "\n".join(json.dumps(r, ensure_ascii=False) for r in results) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(output)
    else:
        sys.stdout.write(output)


def _cmd_grade(args: argparse.Namespace) -> None:
    with open(args.in_path, encoding="utf-8") as f:
        raw_records = [json.loads(line) for line in f if line.strip()]
    kept, discarded_count = filter_contaminated(raw_records)
    unparsed_total = sum(int(r.get("unparsed_lines") or 0) for r in raw_records)
    counts = grade_corpus(
        kept, discarded_count=discarded_count, unparsed_lines=unparsed_total
    )
    for key in ("EXACT", "FAMILY", "MISS", "OVER", "discarded", "unparsed_lines"):
        print(f"{key}: {counts[key]}")


def main(argv: list[str] | None = None) -> None:
    """CLI entry: `run --corpus <path> [--max-turns N] [--out <path>]` or
    `grade --in <path>`."""
    parser = argparse.ArgumentParser(description="loom-* firing/refusal harness")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--corpus", required=True)
    run_parser.add_argument("--max-turns", type=int, default=_MAX_TURNS_FLOOR)
    run_parser.add_argument("--out")
    run_parser.set_defaults(func=_cmd_run)

    grade_parser = subparsers.add_parser("grade")
    grade_parser.add_argument("--in", dest="in_path", required=True)
    grade_parser.set_defaults(func=_cmd_grade)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
