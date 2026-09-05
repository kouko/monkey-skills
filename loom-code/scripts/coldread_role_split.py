"""Scoring core and CLI runner for the cold-read role-split measurement.

Parses one cold-read answer transcript into a per-item label map and
scores N such transcripts against a fixture's expected-owner map. The
label vocabulary is exactly four tokens: "mine" (the reader's own
contract owns this finding), "other" (the counterpart role owns it),
"implementer" (a positive RED belongs to the implementer), and
"unparsed" (the line for that item did not match the pinned answer
format and is never counted as correct).

Usage: python3 coldread_role_split.py --contract <path> --fixture <path>
    --role reviewer|adversary --runs 10 --out <dir> [--model sonnet]
    [--timeout 180] [--claude-bin claude] [--resume]
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter

_LABEL_TOKENS = ("mine", "other", "implementer")

# Matches an optional leading markdown bullet/bold marker, an item number,
# one of `.` `)` `:` as the number/label separator, then the label token
# (tolerating a trailing possessive and markdown emphasis around it).
_LINE_RE = re.compile(
    r"""^\s*
    (?:[\*\-]\s*)*          # optional markdown bullet noise
    \**\s*
    (?P<n>\d+)
    \s*[.\):]
    \s*
    (?:[\*\-]\s*)*
    (?P<label>mine|other|implementer)
    (?:'s|’s)?
    \**
    """,
    re.IGNORECASE | re.VERBOSE,
)

_ROLE_OTHER = {"reviewer": "adversary", "adversary": "reviewer"}


def parse_response(text: str, n_items: int) -> dict[int, str]:
    """Parse one cold-read answer transcript into {1..n_items: label}.

    Every key from 1 to n_items is always present. A line is recognized
    when, after optional whitespace and markdown noise, it starts with
    `<n>.`, `<n>)`, or `<n>:` followed by one of the three label tokens
    (case-insensitive, tolerating a trailing possessive and surrounding
    `**`). Anything else for that item is "unparsed". A duplicate item
    number keeps the first occurrence. Item numbers outside 1..n_items
    are ignored.
    """
    result: dict[int, str] = {n: "unparsed" for n in range(1, n_items + 1)}
    if n_items <= 0:
        return {}

    for line in text.splitlines():
        match = _LINE_RE.match(line)
        if not match:
            continue
        n = int(match.group("n"))
        if n < 1 or n > n_items:
            continue
        if result.get(n) != "unparsed":
            continue
        result[n] = match.group("label").lower()

    return result


def _expected_label(expected_owner: str, role: str) -> str:
    if expected_owner == role:
        return "mine"
    if expected_owner == "implementer":
        return "implementer"
    return "other"


def _validate_fixture_items(items: list) -> None:
    """Require the fixture's item `n` values to be exactly `1..len(items)`
    (contiguous, no gaps or duplicates). A gap silently mis-scores every
    item numbered beyond `len(items)` as always wrong/unparsed regardless
    of what the transcript says, so this is checked eagerly rather than
    left to `dict` lookups to fail quietly."""
    n_items = len(items)
    actual = sorted(item["n"] for item in items)
    expected = list(range(1, n_items + 1))
    if actual != expected:
        raise ValueError(
            f"fixture item numbers must be exactly 1..{n_items} (contiguous, no gaps or "
            f"duplicates); got {actual}"
        )


def score(responses: list[str], fixture: dict, role: str) -> dict:
    """Score N cold-read answer transcripts against `fixture` for `role`.

    `role` must be "reviewer" or "adversary" (ValueError otherwise).
    `fixture` must carry an "items" list of {n, expected} (KeyError
    otherwise). Item `n` values must be exactly 1..len(items)
    (`ValueError` otherwise — see `_validate_fixture_items`). "unparsed"
    is never counted as correct in either tally.
    """
    if role not in _ROLE_OTHER:
        raise ValueError(f"unknown role: {role!r}")

    items = fixture["items"]
    _validate_fixture_items(items)
    n_items = len(items)
    expected_by_n = {item["n"]: _expected_label(item["expected"], role) for item in items}

    n = len(responses)
    parsed = [parse_response(r, n_items) for r in responses]

    items_out: dict[str, dict] = {}
    own_not_own_correct = 0
    three_way_correct = 0

    for item_n, expected in expected_by_n.items():
        counts: Counter = Counter()
        wrong = 0
        for labels in parsed:
            label = labels.get(item_n, "unparsed")
            counts[label] += 1
            if label == expected:
                three_way_correct += 1
            else:
                wrong += 1

            expected_is_mine = expected == "mine"
            label_is_mine = label == "mine"
            if label != "unparsed" and expected_is_mine == label_is_mine:
                own_not_own_correct += 1

        dominant_wrong = None
        dominant_wrong_count = 0
        for label, count in counts.items():
            if label == expected:
                continue
            if count > dominant_wrong_count:
                dominant_wrong = label
                dominant_wrong_count = count

        items_out[str(item_n)] = {
            "expected": expected,
            "counts": dict(counts),
            "wrong": wrong,
            "dominant_wrong": dominant_wrong,
        }

    systematic = []
    for item_n in sorted(expected_by_n):
        info = items_out[str(item_n)]
        if n == 0:
            continue
        wrong_rate = info["wrong"] / n
        dominant_wrong = info["dominant_wrong"]
        if dominant_wrong is None:
            continue
        dominant_count = info["counts"].get(dominant_wrong, 0)
        dominant_rate = dominant_count / n
        if wrong_rate >= 0.5 and dominant_rate >= 0.5:
            systematic.append(item_n)

    total_runs_times_items = n * n_items

    return {
        "n": n,
        "role": role,
        "items": items_out,
        "own_not_own_correct": own_not_own_correct,
        "own_not_own_total": total_runs_times_items,
        "three_way_correct": three_way_correct,
        "three_way_total": total_runs_times_items,
        "systematic": systematic,
    }


# ---------------------------------------------------------------------------
# CLI runner: build the cold-read prompt, call `claude -p` N times, score.
# ---------------------------------------------------------------------------

_ANSWER_INSTRUCTION = (
    "Answer with (a) one sentence stating your own boundary versus the "
    "other verification role named in the contract above, then (b) "
    "exactly one line per finding above in the form "
    "`<n>. mine|other|implementer — <reason>`, where `mine` means this "
    "finding is yours to raise under the contract above, `other` means it "
    "belongs to the other verification role the contract names as not "
    "yours, and `implementer` means it belongs to whoever wrote the code."
)


def build_prompt(contract_text: str, fixture: dict, role: str) -> str:
    """Build the cold-read prompt: contract verbatim, items verbatim, then
    the pinned answer-format instruction. Never uses `str.format`/`%` on
    caller-supplied text, and never mentions expected owners or role names
    beyond what `contract_text` itself carries."""
    del role  # instruction text is role-agnostic; role decides scoring only
    lines = [contract_text, "", "Findings:"]
    for i, item in enumerate(fixture["items"], start=1):
        lines.append(str(i) + ". " + item["text"])
    lines.append("")
    lines.append(_ANSWER_INSTRUCTION)
    return "\n".join(lines)


def run_once(claude_bin: str, model: str, prompt: str, timeout: int) -> tuple[list[str], str, int]:
    """Run one `claude -p` call. Lets `subprocess.TimeoutExpired` propagate.
    On a non-zero return code, stdout and stderr are concatenated and still
    returned rather than raising.

    The prompt is sent on `stdin` (`subprocess.run(..., input=prompt)`),
    never as an argv element: a real contract's YAML frontmatter starts
    with `---`, which `claude`'s option parser rejects as an unknown
    option when the prompt is positional. Grounded in the captured
    `claude -p --help` output at
    docs/loom/2026-09-04-adversary-three-way-attribution-measured/evidence/claude-p-help-2026-09-05.txt,
    which this invocation relies on for three facts: the prompt is read
    from stdin when none is given positionally, `--model` and
    `--output-format text` are supported flags, and no `--seed` flag
    exists."""
    argv = [claude_bin, "-p", "--model", model, "--output-format", "text"]
    completed = subprocess.run(
        argv, input=prompt, capture_output=True, text=True, timeout=timeout
    )
    if completed.returncode != 0:
        return argv, (completed.stdout or "") + (completed.stderr or ""), completed.returncode
    return argv, completed.stdout, completed.returncode


def _command_line(argv: list[str], prompt_hash: str) -> str:
    """The `# command:` header line: the argv actually passed to
    `subprocess.run` (the prompt is never one of its elements — see
    `run_once`), annotated with how the prompt was delivered and its
    hash so a reader can verify it without the prompt being printed."""
    return "# command: " + " ".join(argv) + f"  (prompt on stdin, sha256 {prompt_hash})"


def _write_run_file(
    path,
    argv: list[str],
    prompt: str,
    contract_arg: str,
    contract_hash: str,
    fixture_arg: str,
    fixture_hash: str,
    i: int,
    n: int,
    model: str,
    body: str,
) -> None:
    prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    header_lines = [
        _command_line(argv, prompt_hash),
        f"# contract: {contract_arg} sha256 {contract_hash}",
        f"# fixture: {fixture_arg} sha256 {fixture_hash}",
        f"# run: {i} of {n}",
        f"# model: {model}",
        f"# timestamp: {datetime.datetime.now().astimezone().isoformat()}",
        f"# prompt-sha256: {prompt_hash}",
    ]
    path.write_text("\n".join(header_lines) + "\n\n" + body, encoding="utf-8")


def _parse_run_header(text: str) -> dict:
    """Parse the header block (everything before the first blank line) of
    a `run-<i>.txt` transcript into {"contract_hash", "fixture_hash",
    "prompt_sha256", "run_i", "run_n", "model"}. A field absent from the
    header is simply omitted from the result — never guessed or
    defaulted — so a caller comparing against an expected value treats a
    missing field as a mismatch."""
    header = text.split("\n\n", 1)[0]
    fields: dict = {}
    for line in header.splitlines():
        if line.startswith("# contract:"):
            match = re.search(r"sha256\s+(\S+)", line)
            if match:
                fields["contract_hash"] = match.group(1)
        elif line.startswith("# fixture:"):
            match = re.search(r"sha256\s+(\S+)", line)
            if match:
                fields["fixture_hash"] = match.group(1)
        elif line.startswith("# prompt-sha256:"):
            fields["prompt_sha256"] = line.split(":", 1)[1].strip()
        elif line.startswith("# run:"):
            match = re.match(r"#\s*run:\s*(\d+)\s+of\s+(\d+)", line)
            if match:
                fields["run_i"] = int(match.group(1))
                fields["run_n"] = int(match.group(2))
        elif line.startswith("# model:"):
            fields["model"] = line.split(":", 1)[1].strip()
    return fields


def _resume_mismatch(
    fields: dict,
    run_path,
    i: int,
    n: int,
    model: str,
    contract_hash: str,
    fixture_hash: str,
    prompt_hash: str,
) -> str | None:
    """Compare a resumed run's parsed header `fields` against the current
    invocation. Returns an `error:` message naming the mismatching field
    and the offending file, or None when every field matches."""
    checks = [
        ("contract", fields.get("contract_hash"), contract_hash),
        ("fixture", fields.get("fixture_hash"), fixture_hash),
        ("prompt-sha256", fields.get("prompt_sha256"), prompt_hash),
        ("model", fields.get("model"), model),
    ]
    for name, actual, expected in checks:
        if actual != expected:
            return (
                f"error: resumed run {run_path} has mismatching {name} "
                f"(expected {expected!r}, got {actual!r})"
            )
    if fields.get("run_n") != n:
        return (
            f"error: resumed run {run_path} has mismatching run count N "
            f"(expected {n}, got {fields.get('run_n')!r})"
        )
    if fields.get("run_i") != i:
        return (
            f"error: resumed run {run_path} has mismatching run index "
            f"(expected {i}, got {fields.get('run_i')!r})"
        )
    return None


def main(argv: list[str] | None = None) -> int:
    from pathlib import Path

    cli_argv = list(argv) if argv is not None else sys.argv[1:]

    parser = argparse.ArgumentParser(description="Cold-read role-split runner")
    parser.add_argument("--contract", required=True)
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--role", required=True, choices=["reviewer", "adversary"])
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--out", required=True)
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument(
        "--claude-bin", default=os.environ.get("COLDREAD_CLAUDE_BIN", "claude")
    )
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args(cli_argv)

    if args.runs < 1:
        print(f"error: --runs must be >= 1, got {args.runs}", file=sys.stderr)
        return 2

    claude_bin = shutil.which(args.claude_bin)
    if claude_bin is None:
        print(f"error: claude binary not found on PATH: {args.claude_bin!r}", file=sys.stderr)
        return 2

    out_dir = Path(args.out)
    if out_dir.exists() and not out_dir.is_dir():
        print(f"error: --out is an existing file, not a directory: {out_dir}", file=sys.stderr)
        return 2

    existing_runs = sorted(out_dir.glob("run-*.txt")) if out_dir.exists() else []
    if existing_runs and not args.resume:
        print(
            f"error: {out_dir} already contains run files "
            f"(e.g. {existing_runs[0].name}); pass --resume to continue",
            file=sys.stderr,
        )
        return 2

    contract_path = Path(args.contract)
    fixture_path = Path(args.fixture)
    if not contract_path.is_file():
        print(f"error: --contract file not found: {contract_path}", file=sys.stderr)
        return 2
    if not fixture_path.is_file():
        print(f"error: --fixture file not found: {fixture_path}", file=sys.stderr)
        return 2

    out_dir.mkdir(parents=True, exist_ok=True)

    contract_bytes = contract_path.read_bytes()
    fixture_bytes = fixture_path.read_bytes()
    contract_hash = hashlib.sha256(contract_bytes).hexdigest()
    fixture_hash = hashlib.sha256(fixture_bytes).hexdigest()
    contract_text = contract_bytes.decode("utf-8")
    fixture = json.loads(fixture_bytes.decode("utf-8"))
    try:
        _validate_fixture_items(fixture["items"])
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    prompt = build_prompt(contract_text, fixture, args.role)
    prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    n = args.runs
    responses: list[str] = []
    runs_summary: list[dict] = []

    for i in range(1, n + 1):
        run_path = out_dir / f"run-{i}.txt"

        if args.resume and run_path.exists():
            text = run_path.read_text(encoding="utf-8")
            header_fields = _parse_run_header(text)
            mismatch = _resume_mismatch(
                header_fields, run_path, i, n, args.model, contract_hash, fixture_hash, prompt_hash
            )
            if mismatch:
                print(mismatch, file=sys.stderr)
                return 2
            body = text.split("\n\n", 1)[1] if "\n\n" in text else ""
            responses.append(body)
            runs_summary.append(
                {"i": i, "file": run_path.name, "status": "resumed", "returncode": None}
            )
            continue

        call_argv = [claude_bin, "-p", "--model", args.model, "--output-format", "text"]
        returncode = None
        try:
            _, raw_body, returncode = run_once(claude_bin, args.model, prompt, args.timeout)
            if returncode == 0:
                status = "ok"
                body = raw_body
            else:
                status = "error"
                body = f"# error: exit {returncode}\n" + raw_body
        except subprocess.TimeoutExpired:
            body = f"# error: timeout after {args.timeout}s"
            status = "timeout"

        _write_run_file(
            run_path,
            call_argv,
            prompt,
            args.contract,
            contract_hash,
            args.fixture,
            fixture_hash,
            i,
            n,
            args.model,
            body,
        )
        responses.append(body)
        runs_summary.append(
            {"i": i, "file": run_path.name, "status": status, "returncode": returncode}
        )

    result = score(responses, fixture, args.role)
    failed_runs = sum(1 for run in runs_summary if run["status"] != "ok")

    command_template = _command_line(
        [claude_bin, "-p", "--model", args.model, "--output-format", "text"],
        hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
    )

    summary = {
        "argv": cli_argv,
        "command_template": command_template,
        "n": n,
        "model": args.model,
        "seed": None,
        "seed_note": "claude -p exposes no seed flag",
        "contract": {"path": args.contract, "sha256": contract_hash},
        "fixture": {"path": args.fixture, "sha256": fixture_hash},
        "contract_delivery": "inline",
        "failed_runs": failed_runs,
        "role": args.role,
        "runs": runs_summary,
        **result,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
