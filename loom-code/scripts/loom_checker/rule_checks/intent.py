from __future__ import annotations

from loom_checker.artifact_types import _artifact_type_for
from loom_checker.helpers import REOPEN_TRUNK_CANDIDATES
from loom_checker.helpers import UsageError
from loom_checker.helpers import changed_paths
from loom_checker.helpers import git_maybe
from loom_checker.helpers import git_text
from loom_checker.helpers import glob_to_regex
from loom_checker.helpers import interface_surfaces
from loom_checker.helpers import read_text
from loom_checker.parsing import _squeeze
from pathlib import Path
import re
import sys


def check_intent_schema(manifest, front, sections) -> list[tuple[str, str]]:
    """Every required field/section from the manifest, recomputed."""
    failures = []
    for field in manifest["artifacts"]["intent"]["fields"]:
        if not field.get("required"):
            continue
        name, kind = field["name"], field["kind"]
        holder = front if kind == "frontmatter" else sections
        value = holder.get(name, "").strip()
        if not value:
            failures.append(
                ("intent.schema", f"required {kind} `{name}` is missing or empty.")
            )
            continue
        allowed = field.get("values")
        if allowed and value not in allowed:
            failures.append(
                ("intent.schema", f"`{name}: {value}` is not one of {allowed}.")
            )
    return failures


MAP_ORIGINATOR = re.compile(r"^map:\s*(\S+)$")


def check_map_exists(repo: Path, front) -> list[tuple[str, str]]:
    """A `map:` id names a Map that exists.

    `start_delivery.py` writes both sides at once, but an intent written or
    edited by hand carries free text, and a dangling id points the reader at
    a Map that is not there while the change looks map-originated (W3
    adversary P13). Both spellings of the same claim are resolved: the
    `map:` field and an `originator: map:<id>`."""
    failures = []
    claims: list[tuple[str, str]] = []
    map_id = front.get("map", "").strip()
    if map_id:
        claims.append(("map", map_id))
    originator = front.get("originator", "").strip()
    if (match := MAP_ORIGINATOR.match(originator)):
        claims.append(("originator", match.group(1)))
    for field, value in claims:
        if not (repo / "docs" / "loom" / "maps" / value / "MAP.md").is_file():
            failures.append((
                "intent.schema",
                f"`{field}: {'map:' if field == 'originator' else ''}{value}` names a "
                f"Map that does not exist: no docs/loom/maps/{value}/MAP.md. An intent "
                "cannot originate in a Map that is not there.",
            ))
    return failures


IDENTIFIER_PATTERNS = [
    (
        re.compile(
            r"(?<![\w./-])[\w.-]+\.(?:py|sh|bash|zsh|js|jsx|ts|tsx|json|ya?ml|toml|md"
            r"|rb|go|rs|java|c|h|cpp|sql|css|html)(?![\w/])"
        ),
        "a file or script name",
    ),
    (re.compile(r"(?<![\w./-])[\w.-]+/[\w./-]+"), "a file path"),
    (re.compile(r"\b\w+\(\s*\)"), "a function call"),
    (re.compile(r"\b[a-z][a-z0-9]*_[a-z0-9_]+\b"), "a snake_case identifier"),
    (re.compile(r"\b[a-z][a-z0-9]*[A-Z][A-Za-z0-9]*\b"), "a camelCase identifier"),
]


CONSUMER_PRODUCT_NAMES = re.compile(
    r"\b(?:iPhone|iPadOS|iPad|iOS|macOS|eBay|iCloud|iMac|tvOS|watchOS)\b"
)


DATE_LIKE_FRACTION = re.compile(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b")


def mask_allowed_tokens(problem: str) -> str:
    for pattern in (CONSUMER_PRODUCT_NAMES, DATE_LIKE_FRACTION):
        problem = pattern.sub(lambda match: " " * len(match.group(0)), problem)
    return problem


def check_product_no_identifiers(front, sections) -> list[tuple[str, str]]:
    """A product Problem is written for the person with the problem: it may
    not name the code that will change (concept-model §2b)."""
    if front.get("kind", "").strip() != "product":
        return []
    problem = mask_allowed_tokens(sections.get("Problem", ""))
    failures = []
    for pattern, what in IDENTIFIER_PATTERNS:
        match = pattern.search(problem)
        if match:
            failures.append(
                (
                    "intent.product-no-identifiers",
                    f"the Problem section of a product intent names {what}: "
                    f"{match.group(0)!r}.",
                )
            )
    return failures


NEEDS_DESIGN_GRAMMAR = re.compile(r"^(yes|no)\s*(?:—|–|--)\s*(\S.*)$")


FRONTMATTER_DECISION = ("status:", "needs-design:")


def deciding_commit(
    repo: Path, relative: str, prefixes: tuple[str, ...] = FRONTMATTER_DECISION
) -> str | None:
    """The newest commit that CHANGED the intent's `status:` or
    `needs-design:` line -- the one that decided something. `prefixes`
    generalizes this to another frontmatter line with the same discipline
    (the `lane:` switch line reuses it below) without touching the
    needs-design/status callers, which keep the default.

    Reading the newest touching commit instead made every later edit to the
    intent body (a new open question, an evidence path) owe the needs-design
    line, which is not what concept-model §2b asks for: the line belongs on
    the commit that writes or changes the decision (W2 re-review NF-4)."""
    for sha in git_text(repo, "log", "--format=%H", "--", relative).splitlines():
        if not sha.strip():
            continue
        if _decides_in_frontmatter(repo, sha, relative, prefixes=prefixes):
            return sha
    return None


HUNK_HEADER = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def frontmatter_end(text: str) -> int:
    """The 1-based line number where the front matter stops: the first `## `
    heading. Everything at or after it is body -- an example `status:` line
    inside a fence decides nothing."""
    for number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("## "):
            return number
    return len(text.splitlines()) + 1


def _decides_in_frontmatter(
    repo: Path, sha: str, relative: str, prefixes: tuple[str, ...] = FRONTMATTER_DECISION
) -> bool:
    """Did this commit change a `status:`/`needs-design:` line (or another
    `prefixes` line) that lived in the intent's FRONT MATTER? A quoted or
    fenced copy in the body is an example, not a decision (W2 re-review)."""
    diff = git_text(repo, "show", "--format=", "--unified=0", sha, "--", relative)
    after = frontmatter_end(git_maybe(repo, "show", f"{sha}:{relative}") or "")
    before = frontmatter_end(git_maybe(repo, "show", f"{sha}^:{relative}") or "")
    old_line = new_line = 0
    for line in diff.splitlines():
        if (header := HUNK_HEADER.match(line)):
            old_line, new_line = int(header.group(1)), int(header.group(2))
            continue
        if line[:3] in ("+++", "---"):
            continue
        marker, body = line[:1], line[1:]
        if marker == "+":
            decisive = body.lstrip().startswith(prefixes) and new_line < after
            new_line += 1
        elif marker == "-":
            decisive = body.lstrip().startswith(prefixes) and old_line < before
            old_line += 1
        else:
            old_line += 1
            new_line += 1
            continue
        if decisive:
            return True
    return False


SQUASH_SUBJECT = re.compile(r" \(#\d+\)\s*$")


def _squash_note(repo: Path, relative: str, sha: str) -> str | None:
    """Does `sha` have the SHAPE of a GitHub "Squash and merge" commit on
    the trunk? Three conditions, all git topology or subject shape -- never
    message text, so a hand-written subject that merely LOOKS like a squash
    cannot forge the exception (W0-01 adversary: the fake-`(#1)`-off-main
    case):

    1. single parent -- the squash button makes a plain commit, not a
       2-parent merge (a real `--no-ff` merge already passes today by a
       different path and is untouched by this function);
    2. the subject ends ` (#<n>)` -- exactly what GitHub writes;
    3. `sha` is on the trunk's first-parent chain (REOPEN_TRUNK_CANDIDATES
       -- the same four names `branch_base()` resolves against, minus
       `@{upstream}` for the reason documented at that constant: a
       branch's own upstream must never stand in as "the trunk" here).
       This is checked by literal MEMBERSHIP in
       `git rev-list --first-parent <candidate>`, not by
       `merge-base --is-ancestor` -- ancestry alone proves `sha` is
       *reachable* from the candidate, which a hand-written, single-parent
       `... (#<n>)` commit on a side branch also is once that branch is
       merged into the candidate with a real (`--no-ff`) merge commit; it
       is reachable but never walked by a first-parent traversal, since a
       first-parent walk steps over the merge commit straight to the
       candidate's OWN previous first parent and never descends into the
       merged-in branch. The membership walk is O(history) in the worst
       case (it lists the candidate's entire first-parent chain to check
       one sha) -- cheap in practice because the trunk's first-parent
       chain is short relative to full history including side branches.

    These three are all this function can verify offline: it has no way to
    ask GitHub whether `sha` really came from a "Squash and merge" click,
    or whether the source branch's HEAD really carried the needs-design
    line -- PR provenance is not fetchable from a local clone. The note
    says exactly that, and states the shape-match as shape, not as a
    verified squash. What is actually relied on is that the line was
    already checked, verbatim, on the branch commit BEFORE it could reach
    the trunk -- by this same rule running as the push gate on that
    branch -- so the line is assumed carried forward, not re-derived here.

    Residual: a commit hand-written with this exact shape (single parent,
    `... (#<n>)` subject) and pushed straight to the trunk without going
    through a reviewed branch -- bypassing the push gate that would have
    checked the line -- is accepted by this exception too. That path is
    governed by branch protection (who may push directly to the trunk),
    not by this rule; this rule only recognizes the shape, it cannot tell
    a real squash-merge from a direct push that mimics it.

    Returns the printable note when all three shape conditions hold, else
    None -- the note itself is the evidence for "why did it say that"
    (concept-model §2b), not a bare pass.
    """
    parents = git_maybe(repo, "log", "-1", "--format=%P", sha)
    if parents is None or len(parents.split()) != 1:
        return None
    subject = git_maybe(repo, "log", "-1", "--format=%s", sha)
    if subject is None or not SQUASH_SUBJECT.search(subject):
        return None
    for candidate in REOPEN_TRUNK_CANDIDATES:
        if git_maybe(repo, "rev-parse", "--verify", f"{candidate}^{{commit}}") is None:
            continue
        first_parent_chain = git_maybe(repo, "rev-list", "--first-parent", candidate)
        if first_parent_chain is None or sha not in first_parent_chain.split():
            continue
        return (
            f"intent.needs-design-reason: commit {sha[:7]} ({relative}) has the "
            f"shape of a GitHub squash on {candidate}'s first-parent chain "
            f"(single parent, subject {subject!r}); PR provenance is not "
            "verifiable offline, so this is not a confirmed squash -- the "
            "needs-design line is assumed carried by the branch that the push "
            "gate checked before this commit reached the trunk."
        )
    return None


def check_needs_design_reason(
    front, commit_msg: Path | None, repo: Path, path: Path, out=sys.stdout
):
    """`needs-design` carries a reason, and the intent's commit message
    repeats the line verbatim (concept-model §2b). With no `--commit-msg`
    (the post-commit and station calls) the message is that of the last commit
    that TOUCHED THIS INTENT, not HEAD's -- reading HEAD made the rule pass or
    fail on whatever happened to be committed last, so one unrelated commit
    after the intent broke it and one unrelated commit carrying the line
    could satisfy it (W2 re-review F5). The check is never skipped for want
    of a flag."""
    raw = front.get("needs-design", "").strip()
    if not raw:
        return [], None
    match = NEEDS_DESIGN_GRAMMAR.match(raw)
    if not match:
        return (
            [
                (
                    "intent.needs-design-reason",
                    f"`needs-design: {raw}` does not match `yes | no — <reason>`.",
                )
            ],
            raw.split()[0] if raw.split() else None,
        )
    verdict = match.group(1)
    sha, relative = None, None
    if commit_msg is not None:
        if not commit_msg.is_file():
            raise UsageError(f"no commit message file at {commit_msg}")
        message, source = read_text(commit_msg), str(commit_msg)
    else:
        relative = path.resolve().relative_to(repo.resolve()).as_posix()
        sha = deciding_commit(repo, relative)
        if sha is None:
            message, source = "", f"{relative} (no commit has decided it yet)"
        else:
            message = git_text(repo, "show", "-s", "--format=%B", sha)
            source = f"commit {sha[:7]}, which last changed status/needs-design"
    line = f"needs-design: {raw}"
    if _squeeze(line) not in _squeeze(message):
        # `--commit-msg` names an exact message to check and is never the
        # station's own recompute (deciding_commit() ran, if at all, only in
        # the else branch above) -- the squash exception only ever applies
        # to a commit this function itself found via git topology.
        if sha is not None and relative is not None:
            note = _squash_note(repo, relative, sha)
            if note is not None:
                out.write(note + "\n")
                return [], verdict
        return (
            [
                (
                    "intent.needs-design-reason",
                    f"the commit message ({source}) does not carry the line `{line}`.",
                )
            ],
            verdict,
        )
    return [], verdict


LANE_LINE_PREFIX = ("lane:",)


LANE_GRAMMAR = re.compile(
    r"^(?P<name>express|gate-only|full)\s*(?:—|–|--)\s*"
    r"(?:"
    r"declared\s+(?P<declared_date>\d{4}-\d{2}-\d{2})\s+by\s+(?P<declared_by>[^,]+?)"
    r"|"
    r"switched\s+(?P<date>\d{4}-\d{2}-\d{2})\s+by\s+(?P<by>[^,]+?)\s*,\s*from\s+"
    r"(?P<unit>wave|round)\s+(?P<n>\d+)"
    r")"
    r"\s*$"
)


def check_lane_schema(front) -> list[tuple[str, str]]:
    """`lane:` is optional, but when present it must carry dated user
    attribution -- the declared suffix `— declared <YYYY-MM-DD> by <name>`
    or the switch suffix `— switched <YYYY-MM-DD> by <name>, from <wave
    <n>|round <n>>`, both WITH `by <name>` -- a bare `lane: express` (no
    suffix at all), or a suffix that omits who wrote it, is unrecoverable
    and blocks here rather than being silently accepted as a plain
    declaration."""
    raw = front.get("lane", "").strip()
    if not raw or LANE_GRAMMAR.match(raw):
        return []
    return [
        (
            "intent.schema",
            f"`lane: {raw}` does not match the declared grammar `express | "
            "gate-only | full — declared <YYYY-MM-DD> by <name>` or the switch "
            "grammar `<name> — switched <YYYY-MM-DD> by <name>, from <wave "
            "<n>|round <n>>` -- a bare lane name with no dated attribution is "
            "not a legal value.",
        )
    ]


def check_lane_reason(
    front, commit_msg: Path | None, repo: Path, path: Path, out=sys.stdout
) -> list[tuple[str, str]]:
    """The `lane:` line, declared or switched, must appear verbatim in the
    message of the commit that last changed it -- the same discipline
    `check_needs_design_reason` applies to `status:`/`needs-design:`,
    reused here (`deciding_commit`/`_decides_in_frontmatter` take a
    `prefixes` argument for exactly this) since only the user may write
    this line and its provenance matters the same way."""
    raw = front.get("lane", "").strip()
    if not raw:
        return []
    sha = relative = None
    if commit_msg is not None:
        if not commit_msg.is_file():
            raise UsageError(f"no commit message file at {commit_msg}")
        message, source = read_text(commit_msg), str(commit_msg)
    else:
        relative = path.resolve().relative_to(repo.resolve()).as_posix()
        sha = deciding_commit(repo, relative, prefixes=LANE_LINE_PREFIX)
        if sha is None:
            message, source = "", f"{relative} (no commit has decided it yet)"
        else:
            message = git_text(repo, "show", "-s", "--format=%B", sha)
            source = f"commit {sha[:7]}, which last changed lane"
    line = f"lane: {raw}"
    if _squeeze(line) not in _squeeze(message):
        if sha is not None and relative is not None:
            note = _squash_note(repo, relative, sha)
            if note is not None:
                out.write(note + "\n")
                return []
        return [
            (
                "intent.needs-design-reason",
                f"the commit message ({source}) does not carry the line `{line}`.",
            )
        ]
    return []


TEMPLATES_GLOB = "**/templates/**"


def touched_interface_surfaces(repo: Path, manifest, out) -> list[str]:
    """The changed paths that land on a declared interface surface, and a
    printed line saying which globs were used -- the answer to "why did it
    say that" is never a mystery. Both `intent.needs-design-recompute` and
    `intent.kind-recompute` read this one recomputation.

    Only the `**/templates/**` glob match is narrowed by artifact type: it
    also matches an agent-filled `.md` template that no user ever reads, so
    a match against THIS glob alone counts only when `_artifact_type_for`
    types the path `code` -- an `.md`/`.jinja` template stays excluded, a
    `.tsx`/`.py` one still counts. A match against any OTHER glob -- the
    manifest default (`**/cli/**`, `**/api/**`, `**/commands/**`,
    `**/*.tsx`) or one a repo added via KICKOFF-DEFAULTS -- counts
    regardless of type: a CLI help `.md` under `**/cli/**` is a user
    surface exactly as much as a `.py` one is. This does not let an agent
    narrow the surface, because `artifact-types` in KICKOFF-DEFAULTS is
    reserved (the checker never reads it, per the manifest note); the type
    mapping is the contract's own `artifact_types:` table, fixed regardless
    of what a repo declares."""
    globs, source = interface_surfaces(repo, manifest)
    matchers = [(pattern, glob_to_regex(pattern)) for pattern in globs]
    touched = sorted(
        path
        for path in changed_paths(repo)
        if any(
            matcher.match(path)
            and (
                pattern != TEMPLATES_GLOB
                or _artifact_type_for(manifest, path) == "code"
            )
            for pattern, matcher in matchers
        )
    )
    out.write(
        f"interface-surfaces ({source}): {', '.join(globs)} "
        f"(non-code paths under {TEMPLATES_GLOB} excluded)\n"
    )
    return touched


def check_needs_design_recompute(touched: list[str]) -> list[tuple[str, str]]:
    """`needs-design: no` is a claim; the diff is the fact."""
    if not touched:
        return []
    return [
        (
            "intent.needs-design-recompute",
            "`needs-design: no` but the diff touches a declared interface "
            f"surface: {', '.join(touched[:5])}.",
        )
    ]


def check_kind_recompute(touched: list[str]) -> list[tuple[str, str]]:
    """`kind:` is a claim too, and it is the one that switches off all three
    product rules at once -- the PRINCIPLES.md rejection, the plain-words
    Problem, and decision point (2) (W2 adversary P05). `needs-design` is
    already recomputed against the interface globs; the same recomputation
    answers `kind:`, so an `engineering` label over a diff that edits what
    the user reads or types is refused.

    Note what is NOT here: a declared `needs-design: yes` on its own does not
    make a change product. Reason (b) of concept-model §2b -- many states or
    objects and no spec -- is a legitimate engineering reason to write a
    spec, and §4 gives engineering a needs-design: yes path that simply
    skips decision point (2). Only the diff says "user surface"."""
    if not touched:
        return []
    return [
        (
            "intent.kind-recompute",
            "`kind: engineering` but the diff touches a user surface: "
            f"{', '.join(touched[:5])}. Either `kind: product` (which brings "
            "the ratified PRINCIPLES.md, the plain-words Problem and decision "
            "point 2 with it), or keep the change off the declared interface "
            "surfaces -- docs/loom/KICKOFF-DEFAULTS.md `interface-surfaces` "
            "can only ADD globs, never remove one.",
        )
    ]
