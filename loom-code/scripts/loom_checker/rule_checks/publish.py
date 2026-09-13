from __future__ import annotations

import re


CONTEXTUAL_PR_HEADINGS = (
    "Context", "Intended outcome", "Scope", "Decisions", "Implementation",
    "Behaviour change", "Verification", "Risks and rollback", "Follow-ups",
)


def validate_contextual_pr_body(body: str) -> str | None:
    """Recompute the structural PR-body floor; semantic truth stays review-owned."""
    sections: list[tuple[str, list[str]]] = []
    outside_fences: list[str] = []
    fence: tuple[str, int] | None = None
    for line in body.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if marker and fence is None:
            token = marker.group(1)
            fence = (token[0], len(token))
            continue
        if marker and fence is not None:
            token, suffix = marker.group(1), marker.group(2)
            if token[0] == fence[0] and len(token) >= fence[1] and not suffix.strip():
                fence = None
            continue
        if fence is not None:
            continue
        outside_fences.append(line)
        heading = re.fullmatch(r"## ([^#\n].*)", line)
        if heading:
            sections.append((heading.group(1), []))
        elif sections:
            sections[-1][1].append(line)

    if [heading for heading, _content in sections] != list(CONTEXTUAL_PR_HEADINGS):
        return (
            "PR body must contain Ship's nine top-level contextual headings "
            "exactly once and in order, with no competing top-level heading"
        )
    for heading, lines in sections:
        content = "\n".join(lines)
        visible = re.sub(r"<!--.*?-->", " ", content, flags=re.DOTALL)
        alphanumeric_count = sum(character.isalnum() for character in visible)
        one_ascii_token = re.fullmatch(r"\s*[A-Za-z]+[.!?:;,-]*\s*", visible) is not None
        template_placeholder = re.fullmatch(r"\s*<[^>\n]+>\s*", visible) is not None
        sentinel = (
            heading == "Follow-ups"
            and re.sub(r"[\W_]+", "", visible).casefold() == "none"
        )
        if (
            (alphanumeric_count < 8 or one_ascii_token or template_placeholder)
            and not sentinel
        ):
            return f"PR body section {heading!r} has no substantive content"
    visible_body = re.sub(
        r"<!--.*?-->", " ", "\n".join(outside_fences), flags=re.DOTALL
    )
    if re.search(
        r"\b(?:private|hidden)(?:\s+or\s+(?:private|hidden))?\s+chain-of-thought\b",
        visible_body,
        flags=re.IGNORECASE,
    ):
        return "PR body must not claim to expose private or hidden chain-of-thought"
    return None
