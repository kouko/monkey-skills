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
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

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


_HOSTS = ("claude", "codex")
_OUTCOME_SCORE = {"EXACT": 3, "FAMILY": 2, "MISS": 1, "OVER": 0}


@dataclass(frozen=True)
class HostInvocation:
    """One root-specific host run, kept injectable for offline tests."""

    host: str
    root_label: str
    plugin_root: Path
    record: dict
    replicate: int
    argv: tuple[str, ...]
    codex_home: Path | None
    environment: dict[str, str]


def run_host(invocation: HostInvocation) -> str:
    """Execute one host invocation; callers can replace this in unit tests."""
    env = {**os.environ, **invocation.environment}
    if invocation.host == "codex":
        _prepare_codex_root(invocation, env)
    proc = subprocess.run(
        invocation.argv, capture_output=True, text=True, check=False, env=env
    )
    if proc.returncode:
        raise RuntimeError(
            f"{invocation.host} host exited with status {proc.returncode}"
        )
    return proc.stdout + proc.stderr


def _plugin_tree_fingerprint(root: Path) -> str:
    """Hash one regular, symlink-free plugin tree for cache identity."""
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Codex plugin root must be a regular directory")
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda item: str(item.relative_to(root))):
        relative = str(path.relative_to(root))
        if path.is_symlink():
            raise ValueError(f"Codex plugin root contains symlink: {relative}")
        if path.is_dir():
            payload = b""
            kind = "D"
        elif path.is_file():
            payload = path.read_bytes()
            kind = "F"
        else:
            raise ValueError(f"Codex plugin root contains special file: {relative}")
        entry = json.dumps(
            [
                kind, relative, path.stat().st_mode & 0o111,
                hashlib.sha256(payload).hexdigest(),
            ],
            ensure_ascii=False, separators=(",", ":"),
        ).encode()
        digest.update(len(entry).to_bytes(8, "big"))
        digest.update(entry)
    return digest.hexdigest()


def _prepare_codex_root(invocation: HostInvocation, env: dict[str, str]) -> None:
    """Install one source root into its own disposable Codex home."""
    if invocation.codex_home is None:
        raise ValueError("Codex invocation requires an isolated CODEX_HOME")
    lexical_home = Path(os.path.abspath(os.fspath(invocation.codex_home)))
    if invocation.codex_home.is_symlink() or lexical_home != invocation.codex_home.resolve():
        raise ValueError("Codex home must not contain a symlink alias")
    plugin_fingerprint = _plugin_tree_fingerprint(invocation.plugin_root)
    manifest = invocation.plugin_root / ".codex-plugin" / "plugin.json"
    try:
        plugin_name = json.loads(manifest.read_text(encoding="utf-8"))["name"]
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        raise ValueError("Codex plugin root must contain a named .codex-plugin manifest") from exc
    if (
        not isinstance(plugin_name, str)
        or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", plugin_name) is None
    ):
        raise ValueError("Codex plugin root manifest name has an invalid identifier")
    marketplace = invocation.codex_home / "marketplace"
    if marketplace.is_symlink():
        raise ValueError("Codex marketplace must not be a symlink")
    marker = invocation.codex_home / ".loom-harness-prepared"
    if marker.is_symlink():
        raise ValueError("Codex preparation marker must not be a symlink")
    marker_payload = {
        "plugin_fingerprint": plugin_fingerprint,
        "plugin_name": plugin_name,
        "root_label": invocation.root_label,
    }
    target = marketplace / plugin_name
    try:
        installed_matches = (
            not target.is_symlink()
            and _plugin_tree_fingerprint(target) == plugin_fingerprint
        )
        prepared = (
            json.loads(marker.read_text(encoding="utf-8")) == marker_payload
            and installed_matches
        )
    except (OSError, json.JSONDecodeError):
        prepared = False
    except ValueError:
        prepared = False
    if not prepared:
        invocation.codex_home.mkdir(parents=True, exist_ok=True)
        if marketplace.exists():
            shutil.rmtree(marketplace)
        if target.parent.resolve() != marketplace.resolve():
            raise ValueError("Codex plugin manifest name escapes marketplace")
        shutil.copytree(invocation.plugin_root, target)
        manifest_dir = marketplace / ".claude-plugin"
        manifest_dir.mkdir()
        marketplace_name = f"loom-harness-{invocation.root_label}"
        (manifest_dir / "marketplace.json").write_text(
            json.dumps({
                "name": marketplace_name,
                "owner": {"name": "loom-harness"},
                "plugins": [{"name": plugin_name, "source": f"./{plugin_name}/"}],
            }),
            encoding="utf-8",
        )
        for command in (
            ("codex", "plugin", "marketplace", "add", str(marketplace)),
            ("codex", "plugin", "add", f"{plugin_name}@{marketplace_name}"),
        ):
            result = subprocess.run(command, capture_output=True, text=True, check=False, env=env)
            if result.returncode:
                raise RuntimeError("Codex plugin installation failed for comparison root")
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".loom-harness-prepared.", dir=invocation.codex_home
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                stream.write(json.dumps(marker_payload, sort_keys=True) + "\n")
            os.replace(temporary, marker)
        finally:
            temporary.unlink(missing_ok=True)


def host_argv_for_root(
    host: str,
    plugin_root: Path,
    record: dict,
    *,
    max_turns: int,
    working_directory: Path,
    claude_model: str | None = None,
    codex_model: str | None = None,
) -> tuple[str, ...]:
    """Build the host-specific argv for one explicitly named plugin root.

    Claude accepts a source plugin directory directly. Codex loads plugins
    from its configured installation, so the root stays in the invocation
    provenance rather than being passed as Claude's unsupported flag.
    """
    root = Path(plugin_root).resolve()
    if host == "claude":
        argv = (
            "claude", "-p", record["query"], "--max-turns", str(max_turns),
            "--allowedTools", "Skill", "--output-format", "stream-json",
            "--verbose", "--plugin-dir", str(root),
        )
        return argv if claude_model is None else argv + ("--model", claude_model)
    if host == "codex":
        argv = (
            "codex", "exec", "--ephemeral",
            "--ignore-rules", "--sandbox", "workspace-write",
            "--skip-git-repo-check", "-C", str(Path(working_directory).resolve()),
            "--json", record["query"],
        )
        return argv if codex_model is None else argv[:-1] + ("--model", codex_model, argv[-1])
    raise ValueError(f"unsupported host: {host}")


def _host_events(transcript: str) -> list[dict]:
    events, _ = _parse_stream_json_lines(transcript)
    return events


def _normalize_observable(host: str, transcript: str) -> dict:
    """Keep only structured host observations; deliberately omit prose."""
    events = _host_events(transcript)
    if host == "claude":
        fired = _extract_fired_skill(events)
        subtype, _ = _extract_result(events)
        tool_sequence = tuple(
            block.get("name")
            for event in events if event.get("type") == "assistant"
            for block in event.get("message", {}).get("content", [])
            if block.get("type") == "tool_use" and isinstance(block.get("name"), str)
        )
        return {"fired": fired, "result_subtype": subtype, "tool_sequence": tool_sequence}

    commands = []
    fired = None
    tokens = None
    for event in events:
        item = event.get("item")
        if event.get("type") == "item.completed" and isinstance(item, dict):
            if item.get("type") == "command_execution" and isinstance(item.get("command"), str):
                command = item["command"]
                commands.append(command)
                parts = command.split(maxsplit=1)
                if fired is None and len(parts) == 2 and parts[0] == "skill":
                    fired = parts[1]
                if fired is None:
                    match = re.search(
                        r"/(loom-[^/\s]+)/[^/\s]+/skills/([^/\s]+)/SKILL\.md",
                        command,
                    )
                    if match:
                        fired = f"{match.group(1)}:{match.group(2)}"
        usage = event.get("usage")
        if isinstance(usage, dict):
            tokens = dict(usage)
    completed = any(event.get("type") == "turn.completed" for event in events)
    return {
        "fired": fired,
        "result_subtype": "completed" if completed else "",
        "tool_sequence": tuple(commands),
        "tokens": tokens,
    }


def _comparison_verdict(pairs: list[tuple[dict, dict]]) -> str:
    """Require two identical observable changes before assigning direction."""
    gradeable = {"success", "error_max_turns", "completed"}
    if any(
        run["observable"].get("result_subtype") not in gradeable
        for pair in pairs for run in pair
    ):
        return "INCONCLUSIVE"
    differences: dict[tuple[str, str], list[tuple[dict, dict]]] = {}
    for baseline, candidate in pairs:
        before_observable = {
            key: value for key, value in baseline["observable"].items()
            if key != "tokens"
        }
        after_observable = {
            key: value for key, value in candidate["observable"].items()
            if key != "tokens"
        }
        before = json.dumps(before_observable, sort_keys=True, default=list)
        after = json.dumps(after_observable, sort_keys=True, default=list)
        if before != after:
            differences.setdefault((before, after), []).append((baseline, candidate))
    if not differences:
        return "PASS"
    if len(differences) != 1:
        return "INCONCLUSIVE"
    matching = max(differences.values(), key=len)
    if len(matching) < 2:
        return "INCONCLUSIVE"
    before = grade_record({"expected": matching[0][0]["expected"], **matching[0][0]["observable"]})
    after = grade_record({"expected": matching[0][1]["expected"], **matching[0][1]["observable"]})
    if _OUTCOME_SCORE[after] < _OUTCOME_SCORE[before]:
        return "REGRESSION"
    if _OUTCOME_SCORE[after] > _OUTCOME_SCORE[before]:
        return "IMPROVEMENT"
    return "INCONCLUSIVE"


def compare_hosts(
    records: list[dict],
    baseline_root: Path,
    candidate_root: Path,
    *,
    replicates: int = 2,
    raw_dir: Path,
    runner,
    max_turns: int = _MAX_TURNS_FLOOR,
    working_directory: Path | None = None,
    claude_model: str | None = None,
    codex_model: str | None = None,
) -> dict:
    """Run baseline and candidate roots through both hosts and compare facts.

    ``runner`` receives a :class:`HostInvocation` and returns raw JSONL. This
    preserves transcript evidence while making unit tests and future live
    adapters share the same comparison logic.
    """
    if replicates < 2:
        raise ValueError("comparison requires at least two replicates")
    roots = (("baseline", Path(baseline_root).resolve()), ("candidate", Path(candidate_root).resolve()))
    raw_directory = Path(raw_dir).resolve()
    raw_directory.mkdir(parents=True, exist_ok=True)
    cwd = Path.cwd() if working_directory is None else Path(working_directory)
    runs = []
    for record_index, record in enumerate(records):
        for host in _HOSTS:
            for root_label, plugin_root in roots:
                for replicate in range(replicates):
                    invocation = HostInvocation(
                        host, root_label, plugin_root, record, replicate,
                        host_argv_for_root(
                            host, plugin_root, record, max_turns=max_turns,
                            working_directory=cwd, claude_model=claude_model,
                            codex_model=codex_model,
                        ),
                        raw_directory / f"codex-home-{root_label}" if host == "codex" else None,
                        {"CODEX_HOME": str(raw_directory / f"codex-home-{root_label}")} if host == "codex" else {},
                    )
                    transcript = runner(invocation)
                    raw_path = raw_directory / f"{record_index}-{host}-{root_label}-{replicate}.jsonl"
                    raw_path.write_text(transcript, encoding="utf-8")
                    runs.append({
                        **record,
                        "record_index": record_index,
                        "host": host,
                        "root_label": root_label,
                        "plugin_root": str(plugin_root),
                        "replicate": replicate,
                        "model": claude_model if host == "claude" else codex_model,
                        "argv": invocation.argv,
                        "raw_transcript_path": str(raw_path),
                        "observable": _normalize_observable(host, transcript),
                    })
    comparisons = []
    for record_index, record in enumerate(records):
        for host in _HOSTS:
            pairs = []
            for replicate in range(replicates):
                matching = [
                    run for run in runs
                    if run["host"] == host
                    and run["replicate"] == replicate
                    and run["record_index"] == record_index
                ]
                pairs.append((next(run for run in matching if run["root_label"] == "baseline"), next(run for run in matching if run["root_label"] == "candidate")))
            comparisons.append({"record_index": record_index, "host": host, "verdict": _comparison_verdict(pairs)})
    return {"runs": runs, "comparisons": comparisons}


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


def _cmd_compare(args: argparse.Namespace) -> None:
    with open(args.corpus, encoding="utf-8") as f:
        records = parse_corpus(f.read())
    result = compare_hosts(
        records,
        args.baseline,
        args.candidate,
        replicates=args.replicates,
        raw_dir=args.raw_dir,
        runner=run_host,
        max_turns=args.max_turns,
        working_directory=args.working_directory,
        claude_model=args.claude_model,
        codex_model=args.codex_model,
    )
    output = json.dumps(result, ensure_ascii=False, default=list)
    if args.out:
        args.out.write_text(output + "\n", encoding="utf-8")
    print(output)


def main(argv: list[str] | None = None) -> None:
    """CLI entry for Claude-only run/grade and dual-host comparison."""
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

    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("--corpus", required=True)
    compare_parser.add_argument("--baseline", required=True, type=Path)
    compare_parser.add_argument("--candidate", required=True, type=Path)
    compare_parser.add_argument("--raw-dir", required=True, type=Path)
    compare_parser.add_argument("--out", type=Path)
    compare_parser.add_argument("--replicates", type=int, default=2)
    compare_parser.add_argument("--max-turns", type=int, default=_MAX_TURNS_FLOOR)
    compare_parser.add_argument("--working-directory", type=Path, default=Path.cwd())
    compare_parser.add_argument("--claude-model")
    compare_parser.add_argument("--codex-model")
    compare_parser.set_defaults(func=_cmd_compare)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
