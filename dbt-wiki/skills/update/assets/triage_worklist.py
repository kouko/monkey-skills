# /// script
# requires-python = ">=3.10"
# ///
"""Page-level materiality triage for the redistill work-list.

`rescan` classifies each CHANGED model as "material" (semantically meaningful
evidence change) or "cosmetic" (formatting / whitespace / comment-only). A
knowledge page may derive from several models. This module rolls that per-model
verdict up to a per-page verdict so redistill only spends LLM budget on pages
whose evidence actually changed in meaning.

Rule (OR-aggregation per page): a page is **material** iff ANY uid in
`set(page["derived_from"]) ∩ set(materiality_map)` maps to "material". Otherwise
(all intersecting models cosmetic, OR no intersection at all) the page is
**cosmetic**. Only CHANGED models appear in `materiality_map`; a page whose
derived_from doesn't intersect it saw no model change and is cosmetic by default.

Material pages keep their original domain grouping (now-empty domains drop out).
Cosmetic pages are collected into a single flat list — their domain grouping is
irrelevant once they're skipped. Page dicts are preserved as-is.
"""


def is_material(page, materiality_map):
    """True iff ANY changed model the page derives from is classified material."""
    return any(
        materiality_map.get(uid) == "material"
        for uid in set(page.get("derived_from") or [])
        if uid in materiality_map
    )


def triage(groups, materiality_map):
    """Partition `groups` pages into material (by domain) vs cosmetic (flat).

    `groups`: {domain: [page, ...]} — page is {slug, path, folder, derived_from}.
    `materiality_map`: {uid: "material"|"cosmetic"} — only CHANGED models.
    Returns {"material": {domain: [page, ...]}, "cosmetic": [page, ...]}.
    """
    material = {}
    cosmetic = []
    for domain, pages in groups.items():
        for page in pages:
            if is_material(page, materiality_map):
                material.setdefault(domain, []).append(page)
            else:
                cosmetic.append(page)
    return {"material": material, "cosmetic": cosmetic}
