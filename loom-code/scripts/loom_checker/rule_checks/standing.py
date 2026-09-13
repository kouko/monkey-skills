from __future__ import annotations

from loom_checker.helpers import is_real_date
from loom_checker.helpers import kickoff_defaults, read_text
from pathlib import Path
import re


def check_standing_silence(repo: Path) -> bool:
    return kickoff_defaults(repo).get("standing-docs", "").strip() == "waived"


def check_standing_warn(principles, design, waived: bool, err) -> None:
    missing = [name for name, path in (("PRINCIPLES.md", principles), ("DESIGN.md", design)) if path is None]
    if missing and not waived:
        for line in STANDING_WARN:
            err.write(line.format(missing=" or ".join(missing)) + "\n")


def check_second_vendor(repo: Path) -> list[tuple[str, str]]:
    if kickoff_defaults(repo).get("second-vendor", "").strip() == "none":
        return [(
            "standing.second-vendor-valid",
            "`second-vendor: none` was removed; replace it with "
            "`second-vendor: suggest` for non-blocking, opt-in behavior.",
        )]
    return []


def check_product_principles(repo: Path, front, principles) -> list[tuple[str, str]]:
    if front.get("kind", "").strip() != "product":
        return []
    if principles is None:
        return [(
            "standing.product-principles-reject",
            "kind: product but this repo has no PRINCIPLES.md; "
            "a waiver silences the WARN only, never this rejection.",
        )]
    reason = unratified_reason(read_text(principles))
    if reason:
        return [(
            "standing.product-principles-reject",
            f"{principles.relative_to(repo)} {reason}, so it was never ratified.",
        )]
    return []


STANDING_WARN = (
    "WARN: this repo has no {missing} yet.",
    "WARN: without it, the review station cannot check any change for consistency "
    "against what this product is supposed to be.",
    "WARN: say the word and I will write one; to stop seeing this, record "
    "`standing-docs: waived — <reason> (<date>)` in docs/loom/KICKOFF-DEFAULTS.md.",
)


RATIFIED_BY_ANY = re.compile(r"^ratified-by:.*$", re.MULTILINE)


RATIFIED_BY = re.compile(r"^ratified-by:\s*\S.+\s(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)


NON_NEGOTIABLES = re.compile(r"^##\s+non-negotiables\b", re.IGNORECASE)


LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+\S")


LIST_MARKER = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")


PUNCTUATION = re.compile(r"[^\w\s]+")


MIN_WORDS_PER_ITEM = 3


MIN_NON_NEGOTIABLES = 3


def normalise_item(line: str) -> str:
    body = LIST_MARKER.sub("", line)
    return " ".join(PUNCTUATION.sub(" ", body.lower()).split())


def substantive_non_negotiables(body: str) -> list[str]:
    """The normalised items that actually say something, de-duplicated.

    An item under three words is a slogan, not a commitment, and two items
    that normalise to the same string are one item typed twice -- counting
    raw lines let `it must be fast` three times ratify a constitution
    (W2 adversary P04)."""
    seen: set[str] = set()
    kept: list[str] = []
    for line in body.splitlines():
        if not LIST_ITEM.match(line):
            continue
        item = normalise_item(line)
        if len(item.split()) < MIN_WORDS_PER_ITEM or item in seen:
            continue
        seen.add(item)
        kept.append(item)
    return kept


def unratified_reason(text: str) -> str | None:
    """Ratified is two things, not one (concept-model §8): the signature
    line AND a Non-negotiables section with something in it. A signature over
    an empty document ratifies nothing, so the section is counted here."""
    match = RATIFIED_BY.search(text)
    if not match:
        if RATIFIED_BY_ANY.search(text):
            return (
                "carries a `ratified-by:` line that is not a signature; the "
                "grammar is `ratified-by: <name> <YYYY-MM-DD>` (a name, one "
                "space, an ISO date) -- a placeholder ratifies nothing"
            )
        return "carries no `ratified-by: <name> <date>` line"
    if not is_real_date(match.group(1)):
        return (
            f"names {match.group(1)!r} on its `ratified-by:` line, which is "
            "not a real date"
        )
    body, inside = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = bool(NON_NEGOTIABLES.match(line))
            continue
        if inside:
            body.append(line)
    items = len(substantive_non_negotiables("\n".join(body)))
    if items < MIN_NON_NEGOTIABLES:
        return (
            "has no `## Non-negotiables` section carrying at least "
            f"{MIN_NON_NEGOTIABLES} list items that are each at least "
            f"{MIN_WORDS_PER_ITEM} words long and distinct from one another "
            f"(found {items})"
        )
    return None


def find_standing_doc(repo: Path, name: str) -> Path | None:
    """Repo root first, then docs/loom/ -- both are in use in the wild."""
    for candidate in (repo / name, repo / "docs" / "loom" / name):
        if candidate.is_file():
            return candidate
    return None
