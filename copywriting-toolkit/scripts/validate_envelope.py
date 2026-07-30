"""Fail-loud validator for the copywriting-toolkit handoff envelope.

Usage: validate_envelope.py <envelope.json> [--prev <prev.json>]

Run at every file-borne stage boundary (see CLAUDE.md §Handoff Envelope).
Proceed only on exit 0; any non-zero exit means STOP and surface — never
hand-repair the envelope silently.

Check classes, in evaluation order (all violations for every class are
reported to stderr, one `validate_envelope: ...` line each; the exit code
is the FIRST failing class in this order):

  2  usage / I/O — file missing, unreadable, not a JSON object, phase-enum
     source (.claude-plugin/envelope.schema.json) unreadable
  3  schema — mandatory fields incl. express_mode_used / audit_trail[] /
     retries{bounce_round, revise_round_count, total_retries}; phase must
     be in the schema enum; audit_trail entries carry at/event/skill with
     event in the schema enum. The audit alt-entry minimal shape
     (CLAUDE.md §External Caller Guide, detected by
     phase == "phase-audit-entry") may omit express_mode_used /
     audit_trail / retries but MUST carry a non-empty external_copy.
  4  counters — retries identity total_retries == bounce_round +
     revise_round_count (always); with --prev, each counter is monotonic
     (never decreases — resets are how stall-loops hide)
  5  immutable fields (--prev only) — express_mode_used, voice_quadrant,
     tone_notes.register_signal_applied.named_master_fit_warning, and
     every brief.* key present in prev must survive unchanged (additive
     brief keys are fine). A sanctioned user-override brief edit will
     trip this check by design: fail loud, let the operator confirm.
  6  audit_trail append-only (--prev only) — prev's entries must be a
     verbatim prefix of the current trail
  7  manual-PASS ban — gate_verdict PASS / PASS_WITH_NOTES is valid ONLY
     when audit_trail carries an evaluator-written `gate-verdict` entry
     whose detail names the SAME verdict (exact-token match: a
     PASS_WITH_NOTES entry never legitimizes a bare PASS)
  8  round-2 structural duty — an envelope with revise_round_count > 0
     entering a re-gate (phase-7-ethics / phase-8-form) must carry a
     non-empty prior_findings block (Gate Convergence Vocabulary round-2
     duty, enforced structurally per plan Open Q3)

Enum SSOT: phase + audit event enums, plus the gate_verdict / ethics_verdict
/ form_verdict enums, are read from .claude-plugin/envelope.schema.json next
to this plugin — no hardcoded copy to drift. Stdlib only.

Known-permissive check: retries.* counters are validated as non-negative
integers only (schema also declares maxima 3/2/4) — the router re-checks
those maxima itself for its own HALT decision, so this validator leaves
them unenforced here rather than duplicating that authority.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parent.parent / ".claude-plugin" / "envelope.schema.json"

ALT_ENTRY_PHASE = "phase-audit-entry"
REGATE_PHASES = {"phase-7-ethics", "phase-8-form"}
PASSING_VERDICTS = {"PASS", "PASS_WITH_NOTES"}
VERDICT_FIELDS = ("gate_verdict", "ethics_verdict", "form_verdict")
EVALUATOR_SKILL = "copywriter-evaluator"
COUNTERS = ("bounce_round", "revise_round_count", "total_retries")
IMMUTABLE_PATHS = (
    "express_mode_used",
    "voice_quadrant",
    "tone_notes.register_signal_applied.named_master_fit_warning",
)

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_SCHEMA = 3
EXIT_COUNTERS = 4
EXIT_IMMUTABLE = 5
EXIT_APPEND_ONLY = 6
EXIT_MANUAL_PASS = 7
EXIT_ROUND2 = 8


def _fail_usage(message: str) -> "NoReturn":  # noqa: F821 — py<3.11 friendly
    print(f"validate_envelope: {message}", file=sys.stderr)
    raise SystemExit(EXIT_USAGE)


def _load_json_object(path: Path, label: str) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        _fail_usage(f"{label} unreadable: {exc}")
    except json.JSONDecodeError as exc:
        _fail_usage(f"{label} is not valid JSON: {exc}")
    if not isinstance(data, dict):
        _fail_usage(f"{label} must be a JSON object, got {type(data).__name__}")
    return data


def _schema_enums() -> tuple[list, list, dict[str, list]]:
    schema = _load_json_object(SCHEMA_PATH, f"envelope schema {SCHEMA_PATH}")
    try:
        phases = schema["properties"]["phase"]["enum"]
        events = schema["properties"]["audit_trail"]["items"]["properties"]["event"]["enum"]
        verdict_enums = {
            field: schema["properties"][field]["enum"] for field in VERDICT_FIELDS
        }
    except (KeyError, TypeError) as exc:
        _fail_usage(f"envelope schema missing expected enum: {exc}")
    return phases, events, verdict_enums


def _dig(obj, dotted: str):
    """Resolve a dotted path; returns (found: bool, value)."""
    node = obj
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return False, None
        node = node[part]
    return True, node


def check_schema(
    env: dict, phases: list, events: list, verdict_enums: dict[str, list]
) -> list[str]:
    problems = []
    phase = env.get("phase")
    if not isinstance(phase, str) or phase not in phases:
        problems.append(f"phase must be one of the schema enum values, got {phase!r}")
        return problems  # phase drives every shape decision below

    if phase == ALT_ENTRY_PHASE:
        external_copy = env.get("external_copy")
        if not isinstance(external_copy, str) or not external_copy.strip():
            problems.append("alt-entry envelope requires non-empty external_copy (full text)")
        # express_mode_used / audit_trail / retries omissible here; if present
        # they still get the type checks below.
    else:
        if "express_mode_used" not in env:
            problems.append("mandatory field express_mode_used missing")
        if "audit_trail" not in env:
            problems.append("mandatory field audit_trail missing")
        if "retries" not in env:
            problems.append("mandatory field retries missing")

    if "express_mode_used" in env and not isinstance(env["express_mode_used"], bool):
        problems.append("express_mode_used must be a boolean")

    trail = env.get("audit_trail")
    if trail is not None:
        if not isinstance(trail, list):
            problems.append("audit_trail must be an array")
        else:
            for i, entry in enumerate(trail):
                if not isinstance(entry, dict):
                    problems.append(f"audit_trail[{i}] must be an object")
                    continue
                for key in ("at", "event", "skill"):
                    if not isinstance(entry.get(key), str) or not entry.get(key):
                        problems.append(f"audit_trail[{i}].{key} missing or not a string")
                if isinstance(entry.get("event"), str) and entry["event"] not in events:
                    problems.append(f"audit_trail[{i}].event {entry['event']!r} not in schema enum")

    retries = env.get("retries")
    if retries is not None:
        if not isinstance(retries, dict):
            problems.append("retries must be an object")
        else:
            for counter in COUNTERS:
                value = retries.get(counter)
                if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                    problems.append(f"retries.{counter} missing or not a non-negative integer")

    for field in VERDICT_FIELDS:
        value = env.get(field)
        if value is not None and value not in verdict_enums.get(field, []):
            problems.append(f"{field} must be one of the schema enum values, got {value!r}")
    return problems


def check_counters(env: dict, prev: dict | None) -> list[str]:
    problems = []
    retries = env.get("retries")
    if not isinstance(retries, dict):
        return problems  # schema check already reported the shape problem
    values = {c: retries.get(c) for c in COUNTERS}
    if all(isinstance(v, int) for v in values.values()):
        expected = values["bounce_round"] + values["revise_round_count"]
        if values["total_retries"] != expected:
            problems.append(
                "retries.total_retries must equal bounce_round + revise_round_count "
                f"({values['bounce_round']} + {values['revise_round_count']} = {expected}, "
                f"got {values['total_retries']})"
            )
    if prev is not None:
        prev_retries = prev.get("retries") or {}
        for counter in COUNTERS:
            before = prev_retries.get(counter, 0) if isinstance(prev_retries, dict) else 0
            after = values.get(counter)
            if isinstance(before, int) and isinstance(after, int) and after < before:
                problems.append(
                    f"retries.{counter} decreased ({before} -> {after}); counters are monotonic"
                )
    return problems


def check_immutable(env: dict, prev: dict) -> list[str]:
    problems = []
    for dotted in IMMUTABLE_PATHS:
        found, prev_value = _dig(prev, dotted)
        if not found:
            continue
        curr_found, curr_value = _dig(env, dotted)
        if not curr_found:
            problems.append(f"immutable field {dotted} dropped (present in --prev)")
        elif curr_value != prev_value:
            problems.append(
                f"immutable field {dotted} mutated ({prev_value!r} -> {curr_value!r})"
            )
    prev_brief = prev.get("brief")
    curr_brief = env.get("brief")
    if isinstance(prev_brief, dict):
        for key, prev_value in prev_brief.items():
            if not isinstance(curr_brief, dict) or key not in curr_brief:
                problems.append(f"immutable field brief.{key} dropped (present in --prev)")
            elif curr_brief[key] != prev_value:
                problems.append(
                    f"immutable field brief.{key} mutated ({prev_value!r} -> {curr_brief[key]!r})"
                )
    return problems


def check_append_only(env: dict, prev: dict) -> list[str]:
    prev_trail = prev.get("audit_trail")
    curr_trail = env.get("audit_trail")
    if not isinstance(prev_trail, list) or not isinstance(curr_trail, list):
        return []
    if curr_trail[: len(prev_trail)] != prev_trail:
        return [
            "audit_trail is append-only: --prev entries must be a verbatim prefix "
            f"of the current trail (prev has {len(prev_trail)} entries)"
        ]
    return []


MANUAL_PASS_FIELDS = ("gate_verdict", "ethics_verdict", "form_verdict")


def check_manual_pass(env: dict) -> list[str]:
    # All three verdict fields carry the same PASS tokens and each can
    # unlock a downstream phase (form-check gates Phase-8 entry on
    # ethics_verdict), so the ban covers all of them, not just
    # gate_verdict.
    problems = []
    trail = env.get("audit_trail")
    for field in MANUAL_PASS_FIELDS:
        verdict = env.get(field)
        if verdict not in PASSING_VERDICTS:
            continue
        token = re.compile(rf"\b{re.escape(verdict)}\b")
        matched = False
        if isinstance(trail, list):
            for entry in trail:
                if (
                    isinstance(entry, dict)
                    and entry.get("event") == "gate-verdict"
                    and entry.get("skill") == EVALUATOR_SKILL
                    and isinstance(entry.get("detail"), str)
                    and token.search(entry["detail"])
                ):
                    matched = True
                    break
        if not matched:
            problems.append(
                f"{field} {verdict!r} has no matching evaluator-written gate-verdict "
                "audit_trail entry — manual PASS is banned (CLAUDE.md §What NOT to do)"
            )
    return problems


def check_round2(env: dict) -> list[str]:
    if env.get("phase") not in REGATE_PHASES:
        return []
    retries = env.get("retries")
    revise = retries.get("revise_round_count") if isinstance(retries, dict) else None
    if not isinstance(revise, int) or revise <= 0:
        return []
    findings = env.get("prior_findings")
    non_empty = (
        (isinstance(findings, (list, dict)) and len(findings) > 0)
        or (isinstance(findings, str) and findings.strip())
    )
    if not non_empty:
        return [
            "round-2 duty: revise_round_count > 0 entering a re-gate requires a "
            "non-empty prior_findings block (prior round's findings, verbatim)"
        ]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("envelope", help="envelope JSON file to validate")
    parser.add_argument("--prev", help="previous stage-boundary envelope JSON file")
    args = parser.parse_args(argv)

    env = _load_json_object(Path(args.envelope), f"envelope {args.envelope}")
    prev = _load_json_object(Path(args.prev), f"--prev {args.prev}") if args.prev else None
    phases, events, verdict_enums = _schema_enums()

    classes: list[tuple[int, list[str]]] = [
        (EXIT_SCHEMA, check_schema(env, phases, events, verdict_enums)),
        (EXIT_COUNTERS, check_counters(env, prev)),
        (EXIT_IMMUTABLE, check_immutable(env, prev) if prev is not None else []),
        (EXIT_APPEND_ONLY, check_append_only(env, prev) if prev is not None else []),
        (EXIT_MANUAL_PASS, check_manual_pass(env)),
        (EXIT_ROUND2, check_round2(env)),
    ]

    exit_code = EXIT_OK
    for code, problems in classes:
        for problem in problems:
            print(f"validate_envelope: {problem}", file=sys.stderr)
        if problems and exit_code == EXIT_OK:
            exit_code = code
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
