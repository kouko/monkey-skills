"""Content-hash-bound critic-verdict CLI (§4c Fix-4 of
docs/loom/audits/2026-07-18-agent-loop-convergence-audit.md).

Binds a critic's PASS_WITH_NOTES / NEEDS_REVISION verdict to the exact
bytes of the artifact files it reviewed, so a downstream consumer
(spec-expansion's ui-flows intake, writing-plans' change-folder intake)
can trust "the critic ran and approved THIS content" rather than a
stale free-floating verdict string.

Verdict file (input to `mint`, `--verdict-file <path>`): tolerant
line-regex text carrying a `verdict:` line whose value is
PASS_WITH_NOTES or NEEDS_REVISION — bare PASS is not an allowed token
for a critic verdict (a critic panel always leaves notes or blocks;
see monkey-skills/CLAUDE.md Agent Behavioral Rules).

Verdict JSON (output of `mint`, `<change-folder>/<critic>-verdict.json`
— `--critic` is a required argument on both `mint` and `validate`,
naming the file so multiple critics reviewing the same change-folder
never clobber each other's verdict):
    {"schema": 1, "verdict": "PASS_WITH_NOTES"|"NEEDS_REVISION",
     "files": [...], "sha256": "<hex>", "written_at": "<iso8601>"}
`sha256` is over the concatenated bytes of `--files`, resolved
relative to `--change-folder` (or used as-is if absolute), in the
order given. Overwrite-in-place: a second `mint` for the same critic
replaces its file (atomic tmp+os.replace), latest wins — round
history stays in the critic's prose Round summary, not here.

`mint` exit codes: 0 written (either verdict value — NEEDS_REVISION
still mints, unlike loom-code's gate-markers where NEEDS_REVISION
mints nothing; a consumer must be able to distinguish "ran and
blocked" from "never ran"); 2 change-folder not found; 4 schema-invalid
verdict text (missing/disallowed token) or an unreadable/undecodable
covered file.

`validate` exit codes: 0 fresh PASS_WITH_NOTES; 2 no verdict file
(critic never ran); 3 fresh NEEDS_REVISION; 4 stale hash (covered
files changed since mint), a `--files` list that diverges from the
list recorded at mint time, or an unreadable/unparseable verdict
file. Freshness is checked before verdict value: a stale
PASS_WITH_NOTES is untrustworthy, so hash mismatch always wins over
verdict value.

Stdlib only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_VERDICTS = {"PASS_WITH_NOTES", "NEEDS_REVISION"}


def verdict_filename(critic: str) -> str:
    """Per-critic verdict filename: `<critic>-verdict.json` (§4c point 1
    — one file per critic per change-folder so co-resident critics
    (e.g. design-critic, completeness-critic) never overwrite each
    other's verdict)."""
    return f"{critic}-verdict.json"


# Same horizontal-whitespace-after-colon caution as loom_gate_markers.py:
# \s* under re.M spans the newline and would wrongly capture the next
# line as the value of an empty key.
_VERDICT_RE = re.compile(r"^\s*verdict:[^\S\n]*([A-Z_]+)[^\S\n]*$", re.M)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_critic_verdict_text(text: str) -> tuple[str | None, list[str]]:
    """Validate a critic verdict text's `verdict:` line.

    Returns (verdict_value, problems); `verdict_value` is None unless a
    well-formed line with an allowed value was found. `problems` is
    empty iff the text is schema-valid.
    """
    problems: list[str] = []
    m = _VERDICT_RE.search(text)
    if not m:
        problems.append("verdict: missing")
        return None, problems
    if m.group(1) not in ALLOWED_VERDICTS:
        problems.append(
            f"verdict: invalid value {m.group(1)!r} "
            f"(allowed: {', '.join(sorted(ALLOWED_VERDICTS))})"
        )
        return None, problems
    return m.group(1), problems


def _resolve(change_folder: Path, file_str: str) -> Path:
    p = Path(file_str)
    return p if p.is_absolute() else change_folder / p


def _covered_bytes(change_folder: Path, files: list[str]) -> bytes | None:
    """Concatenated bytes of `files` (order preserved); None if any is
    unreadable."""
    chunks = []
    for f in files:
        try:
            chunks.append(_resolve(change_folder, f).read_bytes())
        except OSError:
            return None
    return b"".join(chunks)


def _parse_files(files_arg: str) -> list[str]:
    return [f.strip() for f in files_arg.split(",") if f.strip()]


def _write_verdict_json(change_folder: Path, critic: str, payload: dict) -> Path:
    """Atomically write `payload` as JSON to
    `<change-folder>/<critic>-verdict.json`."""
    filename = verdict_filename(critic)
    path = change_folder / filename
    fd, tmp = tempfile.mkstemp(dir=str(change_folder), prefix=filename, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return path


def _cmd_mint(args: argparse.Namespace) -> int:
    change_folder = Path(args.change_folder)
    if not change_folder.is_dir():
        print(
            f"mint-critic-verdict: change-folder not found: {change_folder}",
            file=sys.stderr,
        )
        return 2

    try:
        text = Path(args.verdict_file).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"mint-critic-verdict: cannot read verdict file: {exc}", file=sys.stderr)
        return 4

    verdict, problems = validate_critic_verdict_text(text)
    if problems:
        print(
            "mint-critic-verdict: verdict text failed schema validation; "
            "no verdict file written:",
            file=sys.stderr,
        )
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 4

    files = _parse_files(args.files)
    covered = _covered_bytes(change_folder, files)
    if covered is None:
        print(
            f"mint-critic-verdict: cannot read one or more covered files: {files}",
            file=sys.stderr,
        )
        return 4

    payload = {
        "schema": 1,
        "verdict": verdict,
        "files": files,
        "sha256": hashlib.sha256(covered).hexdigest(),
        "written_at": _now_iso(),
    }
    path = _write_verdict_json(change_folder, args.critic, payload)
    print(path)
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    change_folder = Path(args.change_folder)
    verdict_path = change_folder / verdict_filename(args.critic)
    if not verdict_path.is_file():
        print(
            f"mint-critic-verdict: no verdict file at {verdict_path} — "
            "critic never ran.",
            file=sys.stderr,
        )
        return 2

    try:
        data = json.loads(verdict_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(
            f"mint-critic-verdict: cannot read/parse verdict file: {exc}",
            file=sys.stderr,
        )
        return 4

    files = _parse_files(args.files)
    recorded_files = data.get("files")
    if files != recorded_files:
        print(
            "mint-critic-verdict: --files list diverges from the files "
            "list recorded at mint — refusing to validate.\n"
            f"  caller --files: {files}\n"
            f"  recorded files: {recorded_files}",
            file=sys.stderr,
        )
        return 4

    covered = _covered_bytes(change_folder, files)
    if covered is None:
        print(
            "mint-critic-verdict: cannot read one or more covered files "
            f"for validation: {files}",
            file=sys.stderr,
        )
        return 4

    digest = hashlib.sha256(covered).hexdigest()
    if digest != data.get("sha256"):
        print(
            "mint-critic-verdict: covered files changed since mint — "
            "verdict is STALE.",
            file=sys.stderr,
        )
        return 4

    verdict = data.get("verdict")
    if verdict == "NEEDS_REVISION":
        print(
            "mint-critic-verdict: fresh verdict is NEEDS_REVISION — blocked.",
            file=sys.stderr,
        )
        return 3
    if verdict == "PASS_WITH_NOTES":
        print(str(verdict_path))
        return 0

    print(
        f"mint-critic-verdict: unexpected/invalid verdict value in "
        f"verdict file: {verdict!r}",
        file=sys.stderr,
    )
    return 4


def main(argv: list[str] | None = None) -> int:
    """CLI entry: `mint --change-folder <path> --critic <name>
    --verdict-file <path> --files <comma-list>` / `validate
    --change-folder <path> --critic <name> --files <comma-list>`."""
    parser = argparse.ArgumentParser(
        description="Mint/validate a content-hash-bound critic verdict file"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    mint = subparsers.add_parser("mint")
    mint.add_argument("--change-folder", required=True)
    mint.add_argument("--critic", required=True)
    mint.add_argument("--verdict-file", required=True)
    mint.add_argument("--files", required=True)
    mint.set_defaults(func=_cmd_mint)

    validate = subparsers.add_parser("validate")
    validate.add_argument("--change-folder", required=True)
    validate.add_argument("--critic", required=True)
    validate.add_argument("--files", required=True)
    validate.set_defaults(func=_cmd_validate)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
