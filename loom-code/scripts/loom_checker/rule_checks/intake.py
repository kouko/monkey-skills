from __future__ import annotations

from loom_checker.helpers import artifact_path
from loom_checker.helpers import git_maybe
from loom_checker.helpers import is_real_date
from loom_checker.helpers import read_text
from loom_checker.intent_state import STATUS
from loom_checker.intent_state import _status_closed_descriptor
from loom_checker.intent_state import _status_closed_info
from loom_checker.intent_state import check_intent_not_reopened
from loom_checker.intent_state import intent_delivery_state
from loom_checker.parsing import LIST_ITEM
from loom_checker.parsing import _squeeze
from loom_checker.parsing import parse_document
from pathlib import Path
import hashlib
import re
import sys


REQ_LINE = re.compile(r"^\s*(?:[-*+]\s+)?REQ-(\d+)\s*(?:—|–|--)\s*(\S.*)$")


ACCEPTANCE_POINTER = re.compile(r"(?:→|->)\s*Acceptance\s*#(\d+)")


def acceptance_count(intent_sections: dict[str, str]) -> int:
    """How many things the user said "done means this" about."""
    body = intent_sections.get("Acceptance", "")
    return sum(1 for line in body.splitlines() if LIST_ITEM.match(line))


def check_req_grammar(manifest, repo: Path, change_id: str, intent_sections):
    """The Requirements grammar the contract manifest declares, recomputed.

    `REQ-<n> — <name>` ids are what a plan task, a finding and a blind-run
    line all point at, so a skipped number, a reused one, or a requirement
    that answers to no Acceptance line breaks addressability everywhere
    downstream (W2 adversary P03). The manifest declared the grammar from
    the start; until now nothing read it."""
    spec_path = artifact_path(manifest, "spec", change_id, repo)
    if not spec_path.is_file():
        return []  # a missing spec is intake.spec-ready's business, not this rule
    _front, sections = parse_document(read_text(spec_path))
    if "Requirements" not in sections:
        return []  # already reported as a schema gap by the spec's own review
    body = sections["Requirements"]

    entries: list[tuple[int, str, str]] = []   # (number, name, block text)
    current: list[str] = []
    for line in body.splitlines():
        match = REQ_LINE.match(line)
        if match:
            entries.append((int(match.group(1)), match.group(2).strip(), ""))
            current = []
        elif entries:
            current.append(line)
        if entries:
            number, name, _ = entries[-1]
            entries[-1] = (number, name, "\n".join(current))

    if not entries:
        return [
            (
                "spec.req-grammar",
                f"{spec_path.relative_to(repo)} has a `## Requirements` section "
                "with no `REQ-<n> — <name>` line in it; the ids are what plan "
                "tasks, findings and the blind-run report point at.",
            )
        ]

    failures = []
    seen: set[int] = set()
    for position, (number, _name, _block) in enumerate(entries, start=1):
        if number in seen:
            failures.append(
                (
                    "spec.req-grammar",
                    f"REQ-{number} appears twice; every requirement id is used "
                    "once, so a finding against one of them is unambiguous.",
                )
            )
        elif number != position:
            failures.append(
                (
                    "spec.req-grammar",
                    f"REQ-{number} is the {position}th requirement; the ids run "
                    f"contiguously from 1, so this one has to be REQ-{position}.",
                )
            )
        seen.add(number)

    total = acceptance_count(intent_sections)
    for number, name, block in entries:
        pointers = [int(value) for value in ACCEPTANCE_POINTER.findall(name + "\n" + block)]
        if not pointers:
            failures.append(
                (
                    "spec.req-grammar",
                    f"REQ-{number} carries no `→ Acceptance #<n>`; a requirement "
                    "that answers to no acceptance line is not something the "
                    "user asked for.",
                )
            )
            continue
        for pointer in pointers:
            if not 1 <= pointer <= total:
                failures.append(
                    (
                        "spec.req-grammar",
                        f"REQ-{number} points at Acceptance #{pointer}, but the "
                        f"intent carries {total} acceptance line(s).",
                    )
                )
    return failures


FENCE = re.compile(r"^\s*(?:```|~~~)")


HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


ARROW = re.compile(r"\u2192|->")


VISIBLE = re.compile(r"[^\W_]", re.UNICODE)


MIN_VISIBLE_PER_SIDE = 4


LINE_MARKER = re.compile(r"^\s*(?:>|#{1,6}|[-*+]|\d+[.)])\s*")


EMPHASIS = str.maketrans("", "", "*_~`")


def strip_markup(line: str) -> str:
    """One line, minus the markdown that decorates it: leading quote /
    heading / list markers, table pipes, emphasis characters."""
    text = line.replace("|", " ")
    while True:
        stripped = LINE_MARKER.sub("", text, count=1)
        if stripped == text:
            break
        text = stripped
    return text.translate(EMPHASIS).strip()


def visible_count(text: str) -> int:
    """Characters that carry content -- letters and digits in any script.
    Counted as CHARACTERS, not words: CJK writes a whole flow with no
    spaces in it."""
    return len(VISIBLE.findall(text))


def prose_lines(body: str) -> list[str]:
    """The body minus fenced code blocks and HTML comments."""
    kept, inside_fence = [], False
    for line in HTML_COMMENT.sub(" ", body).splitlines():
        if FENCE.match(line):
            inside_fence = not inside_fence
            continue
        if inside_fence:
            continue
        if line.startswith(("    ", "\t")):
            # Indented code block (CommonMark): the same semantic class as a
            # fence, so it is not prose either.
            continue
        kept.append(line)
    return kept


def flow_lines(body: str) -> list[str]:
    """`<operation> -> <reaction>` lines: what decision point 2 reads back."""
    found = []
    for line in prose_lines(body):
        text = strip_markup(line)
        arrow = ARROW.search(text)
        if not arrow:
            continue
        left, right = text[:arrow.start()], text[arrow.end():]
        if (visible_count(left) >= MIN_VISIBLE_PER_SIDE
                and visible_count(right) >= MIN_VISIBLE_PER_SIDE):
            found.append(text)
    return found


def check_ui_flows_recompute(manifest, repo: Path, change_id: str, touched: list[str]):
    """`## UI flows: N/A` is a claim; the diff is the fact.

    `intent.needs-design-recompute` only ever ran on the `no` branch, so a
    `needs-design: yes` change could answer "no interface" in its spec while
    editing the CLI and a `.tsx` file, leaving decision point (2) with
    nothing to read back (W2 adversary P06)."""
    if not touched:
        return []
    spec_path = artifact_path(manifest, "spec", change_id, repo)
    if not spec_path.is_file():
        return []  # intake.spec-pass reports the missing spec
    _front, sections = parse_document(read_text(spec_path))
    body = sections.get("UI flows", "")
    if flow_lines(body):
        return []
    shown = _squeeze(body)[:40] or "(empty)"
    return [
        (
            "spec.ui-flows-recompute",
            f"{spec_path.relative_to(repo)} carries no `<operation> -> "
            f"<reaction>` line under `## UI flows` (it says {shown!r}) while "
            f"the diff touches a declared interface surface: "
            f"{', '.join(touched[:5])}. A flow line is prose -- not inside a "
            "``` fence or an HTML comment -- carrying an arrow with at least "
            f"{MIN_VISIBLE_PER_SIDE} visible characters on each side, e.g. "
            "`todo add --due 2026-09-10 'buy milk' -> the todo is stored with "
            "its due date`. That is a shape check only: whether the flow is "
            "true, complete or worth reading is the reviewer's judgement, not "
            "this rule's. Write one per operation; that section IS decision "
            "point 2.",
        )
    ]


CONFIRMED_BEHAVIOR_GRAMMAR = re.compile(
    r"^(\d{4}-\d{2}-\d{2})(?:\s+@([0-9a-f]{7,40}))?$"
)


CONFIRMED_BEHAVIOR_LINE = re.compile(rb"^confirmed-behavior:.*\n?", re.MULTILINE)


def blob_sha(data: bytes) -> str:
    """`git hash-object` without shelling out -- the same value git stores."""
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def spec_identity(spec_path: Path) -> str:
    """The one blob sha both freshness rules compare against: the spec WITHOUT
    its `confirmed-behavior:` line.

    Two reasons it is not simply `git hash-object spec.md`. The confirmation
    line names this value, so hashing the whole file would make it a hash of
    itself; and decision point 2 writes that line AFTER the reviewers read the
    text, so a whole-file hash would make every confirmation invalidate the
    review that preceded it."""
    return blob_sha(CONFIRMED_BEHAVIOR_LINE.sub(b"", spec_path.read_bytes(), count=1))


def recompute_command(relative: str) -> str:
    return (
        "recompute it with `git hash-object <(grep -v '^confirmed-behavior:' "
        f"{relative})`"
    )


def sha_agrees(recorded: str, current: str) -> bool:
    """Either abbreviation is a prefix of the other; git shortens freely."""
    recorded, current = recorded.strip().lower(), current.strip().lower()
    return bool(recorded) and (current.startswith(recorded) or recorded.startswith(current))


TASK_LINE = re.compile(
    r"^(?:[-*+]\s+)?\*\*(?P<id>[A-Za-z0-9][A-Za-z0-9._-]*)[^*]*\*\*(?P<rest>.*)$"
)


TASK_ACCEPTANCE = re.compile(r"(?:^|\s)acceptance:\s*(.*?)\s*$", re.IGNORECASE)


VALID_ACCEPTANCE_REFS = re.compile(r"[0-9]{1,9}(?:\s*,\s*[0-9]{1,9})*")


TEST_CASE = re.compile(
    r"(?:^|[.;]\s*)A(?P<number>\d+)\s+positive:\s*(?P<positive>[^;]+?)\s*;\s*"
    r"(?P<kind>negative|boundary):\s*(?P<opposite>.+?)"
    r"(?=\s*(?:[.;]\s*A\d+\s+positive:|$))",
    re.IGNORECASE,
)


def check_test_case_pairs(
    manifest, repo: Path, change_id: str, intent_sections: dict[str, str]
) -> list[tuple[str, str]]:
    """A new plan owns every Acceptance line and pairs both sides of its tests.

    Plans authored before this contract remain byte-compatible when their
    first committed form used the old task grammar. A new plan cannot
    self-exempt later by deleting its ownership markers or charter line."""
    plan_path = artifact_path(manifest, "plan", change_id, repo)
    if not plan_path.is_file():
        return []
    plan_text = read_text(plan_path)
    _front, plan_sections = parse_document(plan_text)
    task_dag = plan_sections.get("Task DAG", "")
    headers = [
        match
        for raw_line in task_dag.splitlines()
        if (match := TASK_LINE.match(raw_line.strip()))
    ]
    relative_plan = plan_path.relative_to(repo).as_posix()
    first_commit_log = git_maybe(
        repo, "log", "--diff-filter=A", "--reverse", "--format=%H", "HEAD", "--", relative_plan
    )
    first_commit = first_commit_log.splitlines()[0] if first_commit_log else None
    if first_commit:
        original_plan = git_maybe(repo, "show", f"{first_commit}:{relative_plan}")
        if original_plan is not None:
            _original_front, original_sections = parse_document(original_plan)
            original_headers = [
                match
                for raw_line in original_sections.get("Task DAG", "").splitlines()
                if (match := TASK_LINE.match(raw_line.strip()))
            ]
            if original_headers and not any(
                TASK_ACCEPTANCE.search(match.group("rest"))
                for match in original_headers
            ):
                return []

    failures: list[tuple[str, str]] = []
    if not headers:
        failures.append(
            ("intake.test-case-pair", "a newly authored plan requires at least one task.")
        )
    acceptance_numbers = {
        int(match.group(1))
        for raw_line in intent_sections.get("Acceptance", "").splitlines()
        if (match := re.match(r"^\s*(\d+)[.)]\s+\S", raw_line))
    }
    if intent_sections.get("Open questions", "").strip() != "- none":
        failures.append(
            (
                "intake.test-case-pair",
                "a newly authored plan requires intent Open questions to be exactly `- none`.",
            )
        )

    fields = _parse_plan_task_fields(task_dag)
    owned: set[int] = set()
    for header in headers:
        task_id = header.group("id")
        if MEMORY_TASK_ID.match(task_id):
            continue
        marker = TASK_ACCEPTANCE.search(header.group("rest"))
        if marker is None:
            failures.append(
                ("intake.test-case-pair", f"{task_id} carries no `acceptance: <numbers>` marker.")
            )
            continue
        raw_marker = marker.group(1).strip()
        if not VALID_ACCEPTANCE_REFS.fullmatch(raw_marker):
            failures.append(
                (
                    "intake.test-case-pair",
                    f"{task_id} carries malformed Acceptance references.",
                )
            )
            continue
        raw_references = [value.strip() for value in raw_marker.split(",")]
        references = [int(value) for value in raw_references]
        nonexistent = sorted(set(references) - acceptance_numbers)
        if nonexistent:
            failures.append(
                (
                    "intake.test-case-pair",
                    f"{task_id} references nonexistent Acceptance lines: "
                    f"{', '.join(map(str, nonexistent))}.",
                )
            )
        owned.update(set(references) & acceptance_numbers)
        cases = {
            int(match.group("number")): match
            for match in TEST_CASE.finditer(str(fields.get(task_id, {}).get("Test") or ""))
            if any(ch.isalnum() for ch in match.group("positive"))
            and any(ch.isalnum() for ch in match.group("opposite"))
        }
        missing_cases = sorted(set(references) - set(cases))
        if missing_cases:
            failures.append(
                (
                    "intake.test-case-pair",
                    f"{task_id} lacks a non-empty positive plus negative or boundary pair for "
                    f"Acceptance: {', '.join(map(str, missing_cases))}.",
                )
            )

    uncovered = sorted(acceptance_numbers - owned)
    if uncovered:
        failures.append(
            (
                "intake.test-case-pair",
                "intent Acceptance lines are owned by no task: "
                f"{', '.join(map(str, uncovered))}.",
            )
        )
    return failures


PLAN_FIELD_CAP_TEST = 40


PLAN_FIELD_CAP_RISK = 40


PLAN_FIELD_CAP_FILES = 8


PLAN_FIELD_CAP_RISKS_ITEM = 40


PLAN_FIELD_CAP_CSE_BULLET = 30


TASK_FIELD_LINE = re.compile(r"^-\s*(Files|Test|Risk):\s*(.*)$")


NUMBERED_ITEM = re.compile(r"^\d+\.\s+(\S.*)$")


BULLET_ITEM = re.compile(r"^-\s+(\S.*)$")


def _split_respecting_backticks(text: str) -> list[str]:
    """Comma-split `text`, except a comma sitting inside a `backtick span`
    never splits -- a generated fixture path legitimately containing a
    comma must still count as one Files entry (W1-01 adversary pin)."""
    entries: list[str] = []
    current: list[str] = []
    in_backtick = False
    for ch in text:
        if ch == "`":
            in_backtick = not in_backtick
            current.append(ch)
        elif ch == "," and not in_backtick:
            entries.append("".join(current))
            current = []
        else:
            current.append(ch)
    entries.append("".join(current))
    return [entry.strip() for entry in entries if entry.strip()]


def _parse_plan_task_fields(task_dag_text: str) -> dict[str, dict[str, str | None]]:
    """One dict per task id, `{"Files": ..., "Test": ..., "Risk": ...}`,
    values `None` when the task's block carries no such line at all --
    distinct from an empty value, which the task did write."""
    tasks: dict[str, dict[str, str | None]] = {}
    current_id: str | None = None
    for raw_line in task_dag_text.splitlines():
        line = raw_line.strip()
        header = TASK_LINE.match(line)
        if header:
            current_id = header.group("id")
            tasks[current_id] = {"Files": None, "Test": None, "Risk": None}
            continue
        if current_id is None:
            continue
        field_match = TASK_FIELD_LINE.match(line)
        if field_match:
            tasks[current_id][field_match.group(1)] = field_match.group(2)
    return tasks


def _plan_numbered_items(text: str) -> list[str]:
    items = []
    for raw_line in text.splitlines():
        match = NUMBERED_ITEM.match(raw_line.strip())
        if match:
            items.append(match.group(1))
    return items


def _plan_bullets(text: str) -> list[str]:
    items = []
    for raw_line in text.splitlines():
        match = BULLET_ITEM.match(raw_line.strip())
        if match:
            items.append(match.group(1))
    return items


def check_plan_field_caps(plan_text: str) -> list[tuple[str, str]]:
    """Recomputed per-field caps on a charter-stamped plan (W1-01).

    Skipped entirely -- no output at all -- when the plan's frontmatter
    carries no `charter:` key; presence is the stamp, not any particular
    value, so grandfathering is by template, not by date (concept-model
    §5, plan Risk #1)."""
    front, sections = parse_document(plan_text)
    if "charter" not in front:
        return []

    failures: list[tuple[str, str]] = []

    tasks = _parse_plan_task_fields(sections.get("Task DAG", ""))
    for task_id, fields in tasks.items():
        for field, cap in (("Files", PLAN_FIELD_CAP_FILES), ("Test", PLAN_FIELD_CAP_TEST), ("Risk", PLAN_FIELD_CAP_RISK)):
            value = fields.get(field)
            if value is None:
                failures.append(("plan.field-caps", f"{task_id}.{field} missing"))
                continue
            if field == "Files":
                entries = _split_respecting_backticks(value)
                if len(entries) > cap:
                    failures.append((
                        "plan.field-caps",
                        f"{task_id}.Files {len(entries)} entries, cap {cap}",
                    ))
            else:
                words = len(value.split())
                if words > cap:
                    failures.append((
                        "plan.field-caps",
                        f"{task_id}.{field} {words} words, cap {cap}",
                    ))

    for index, item in enumerate(_plan_numbered_items(sections.get("Risks", "")), start=1):
        words = len(item.split())
        if words > PLAN_FIELD_CAP_RISKS_ITEM:
            failures.append((
                "plan.field-caps",
                f"Risks#{index} {words} words, cap {PLAN_FIELD_CAP_RISKS_ITEM}",
            ))

    cse = sections.get("Current State Evidence", "")
    for index, item in enumerate(_plan_bullets(cse), start=1):
        words = len(item.split())
        if words > PLAN_FIELD_CAP_CSE_BULLET:
            failures.append((
                "plan.field-caps",
                f"Current State Evidence#{index} {words} words, cap {PLAN_FIELD_CAP_CSE_BULLET}",
            ))

    return failures


def check_plan_field_caps_at(manifest, repo: Path, change_id: str) -> list[tuple[str, str]]:
    """Same rule, applied to a change's own `plan.md` when it exists -- the
    shape `check_after_task_budget` uses, reused at intake and push."""
    plan_path = artifact_path(manifest, "plan", change_id, repo)
    if not plan_path.is_file():
        return []
    return check_plan_field_caps(read_text(plan_path))


MEMORY_TASK_ID = re.compile(r"^W\d+-memory$", re.IGNORECASE)


PRE_BUILD_REVIEW = re.compile(
    r"^(required|not-required)\s*(?:—|–|--)\s*(\S.*)$", re.IGNORECASE
)


def check_spec_ready(manifest, repo: Path, change_id: str) -> list[tuple[str, str]]:
    """Require the spec and its explicit risk decision, without a review ledger."""
    spec_path = artifact_path(manifest, "spec", change_id, repo)
    if not spec_path.is_file():
        return [("intake.spec-ready", f"needs-design: yes but no spec at {spec_path.relative_to(repo)}.")]
    spec_front, _ = parse_document(read_text(spec_path))
    declaration = spec_front.get("pre-build-review", "").strip()
    if not declaration or PRE_BUILD_REVIEW.fullmatch(declaration) is None:
        return [(
            "intake.spec-ready",
            "`pre-build-review` must be `required|not-required — <reason>`.",
        )]
    return []


def check_confirmed_behavior(
    manifest, repo: Path, change_id: str, err=sys.stderr
) -> list[tuple[str, str]]:
    """Decision point ② leaves exactly one trace: the spec's
    `confirmed-behavior:` line (concept-model §2c).

    The line names the text the user was shown -- `<date> @<spec-blob-sha7>`,
    where the sha is `git hash-object` over the spec WITHOUT this line (the
    file as it stood the moment before the agent wrote the confirmation, so
    the value is not a hash of itself). Rewrite the spec afterwards and the
    confirmation is about a behaviour nobody agreed to (W2 adversary P02)."""
    spec_path = artifact_path(manifest, "spec", change_id, repo)
    if not spec_path.is_file():
        return []  # already reported by intake.spec-pass
    front, _ = parse_document(read_text(spec_path))
    raw = front.get("confirmed-behavior", "").strip()
    if not raw:
        return [
            (
                "intake.confirmed-behavior",
                "kind: product but the spec has no "
                "`confirmed-behavior: <date> @<spec-blob-sha7>` line; "
                "decision point ② has not happened.",
            )
        ]
    current = spec_identity(spec_path)
    relative = spec_path.relative_to(repo).as_posix()
    match = CONFIRMED_BEHAVIOR_GRAMMAR.match(raw)
    if not match or not match.group(2):
        return [
            (
                "intake.confirmed-behavior",
                f"`confirmed-behavior: {raw}` does not match "
                f"`<date> @<spec-blob-sha7>`; the sha names the text the user "
                f"was actually shown ({current[:7]} for {relative} as it "
                f"stands) -- {recompute_command(relative)}.",
            )
        ]
    if not is_real_date(match.group(1)):
        return [
            (
                "intake.confirmed-behavior",
                f"`confirmed-behavior: {raw}` names {match.group(1)!r}, which "
                "is not a real date.",
            )
        ]
    recorded = match.group(2)
    if not sha_agrees(recorded, current):
        return [
            (
                "intake.confirmed-behavior",
                f"the user confirmed spec @{recorded}, but {relative} is now "
                f"@{current[:7]} -- the "
                "visible behaviour changed after decision point ②; show it "
                "again and rewrite the line.",
            )
        ]
    return []


def check_confirmed(manifest, repo: Path, change_id: str, station: str) -> list[tuple[str, str]]:
    intent_path = artifact_path(manifest, 'intent', change_id, repo)
    if not intent_path.is_file():
        return [('intake.confirmed', f'no intent file at {intent_path.relative_to(repo)}.')]
    front, sections = parse_document(read_text(intent_path))
    status = front.get('status', '').strip()
    match = STATUS.fullmatch(status)
    confirmed_date = match.group(1) if match else None
    closed_info = _status_closed_info(match) if match else None
    if closed_info is not None:
        closed_date, kind, identifier = closed_info
        descriptor = _status_closed_descriptor(kind, identifier)
        if not is_real_date(closed_date):
            return [('intake.confirmed', f'`status: closed {closed_date} — {descriptor}` names something that is not a real date.')]
        return [('intake.confirmed', f'{station} accepts only `status: confirmed <date>`; this change is closed ({descriptor}) and closed intents are not reopened; start a new intent.')]
    reopen_failure = check_intent_not_reopened(repo, intent_path, change_id)
    if reopen_failure is not None:
        return [reopen_failure]
    if confirmed_date is None:
        shown = status or 'absent (= open)'
        return [('intake.confirmed', f'{station} accepts only `status: confirmed <date>`; status is {shown}.')]
    if not is_real_date(confirmed_date):
        return [('intake.confirmed', f'`status: confirmed {confirmed_date}` names something that is not a real date.')]
    delivery_state, delivery_detail = intent_delivery_state(repo, change_id, manifest=manifest)
    if delivery_state == 'delivered':
        return [('intake.confirmed', f'{change_id} is delivered on {delivery_detail}; start a new intent')]
    if delivery_state == 'closed':
        return [('intake.confirmed', f'{change_id} was closed ({delivery_detail}) and closed intents are not reopened; start a new intent')]
    if delivery_state == 'indeterminate':
        return [('intake.confirmed', f'{change_id} delivery is indeterminate: {delivery_detail}; refresh the selected remote-default ref before intake')]
    return []
