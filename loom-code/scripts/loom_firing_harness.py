"""Behavioral firing/refusal test harness for the loom-* skill family.

Rebuilds the ad-hoc harness from the 2026-06-24/25 firing/refusal audit
(memory: project_loom_firing_test_router_asymmetry) as versioned,
tested scripts instead of scratchpad throwaways. That audit's method
write-up documented five traps that nearly produced false conclusions;
each is named here with the layer that guards against it:

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
   run-result record whose `result_subtype` signals an error, or whose
   raw text mentions a session limit, is DISCARDED and excluded from
   grading; the discard count is always surfaced, never swallowed.
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

This module currently implements the corpus layer only (parsing +
contamination filtering, Task F1a). `grade` (F1b) and `run` (F1c) modes
land in follow-up tasks; records are kept as plain dicts throughout so
those modes can consume this layer's output directly.

Stdlib only.
"""

import json

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


def _is_contaminated(record: dict) -> bool:
    subtype = str(record.get("result_subtype", ""))
    text = str(record.get("text", ""))
    if subtype != "success":
        return True
    if "session limit" in text.lower():
        return True
    return False


def filter_contaminated(run_results: list[dict]) -> tuple[list[dict], int]:
    """Contamination filter (trap #3): discard error/session-limit records.

    A record is discarded if its `result_subtype` is anything other
    than "success", or if its `text` mentions a session limit
    (case-insensitive) — either signals the run itself failed, not
    that routing failed. Returns `(kept_records, discarded_count)`;
    the count must always be surfaced by callers, never swallowed.
    """
    kept = [r for r in run_results if not _is_contaminated(r)]
    discarded_count = len(run_results) - len(kept)
    return kept, discarded_count
