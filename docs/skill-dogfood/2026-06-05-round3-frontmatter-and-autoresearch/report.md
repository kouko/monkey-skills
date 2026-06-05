# Dogfood Report (Round 3) — frontmatter-link precision + wiki-auto-research

- Date: 2026-06-05
- Targets: `obsidian/skills/wiki-ingest` gate (frontmatter axis) + `obsidian/skills/wiki-auto-research` (first dogfood of this skill)
- Axes (predict-then-execute): (A) gate precision on **frontmatter** wikilinks; (B) wiki-auto-research end-to-end output (the `[[new-concept]]`→non-link reframe).

## Severity summary

| Severity | Count | Finding |
|---|---|---|
| 🟡 Medium-Low | 1 | H1 — gate flags frontmatter danglers but the body-oriented downgrade remedy breaks YAML there |
| ✅ Behavioral PASS | 1 | wiki-auto-research emits the new concept as non-link; zero dangling links in the note |

## H1 🟡 Medium-Low — frontmatter dangling wikilinks flagged, but the SKILL.md remedy is body-specific

- Category: Workflow-drift (remedy-context-mismatch)
- pass: informed (script execution)
- Location: `obsidian/skills/wiki-ingest/scripts/check-wikilink-targets.py` (the extractor scans the whole document, incl. the frontmatter block — `_FRONTMATTER_RE` is used only to harvest aliases, not to exclude frontmatter from the unresolved scan) + `obsidian/skills/wiki-ingest/SKILL.md:213` (downgrade remedy `[[X]]`→`**X**`)
- Prediction (written first): the gate scans frontmatter, so a `contributes_to: ["[[missing]]"]` / `source_pages: ["[[missing]]"]` entry whose target doesn't resolve gets flagged — and the downgrade remedy (`[[X]]`→`**X**`) makes no sense inside a YAML list field.
- Actual: confirmed. A reference page with `contributes_to: ["[[exploration-exploitation]]", "[[missing-concept]]"]` and `source_pages: ["[[also-missing]]"]` → the gate prints `missing-concept` and `also-missing` (exit 1). Applying SKILL.md:213 literally would rewrite the YAML to `contributes_to: ["[[exploration-exploitation]]", "**missing-concept**"]` — a bold-text string in a wikilink-list field, which Obsidian does not treat as a link and which violates the field's "list of wikilinks" contract.
- Nuance (honest): flagging a frontmatter dangler is arguably **correct** — Obsidian resolves frontmatter wikilinks too, so a missing target there is a real dangling link. The defect is only the **remedy**: SKILL.md's downgrade instruction is written for body Connections and produces broken YAML if mechanically applied to a frontmatter hit. In normal wiki-ingest operation this rarely fires (`contributes_to` points to the concept page created in the same ingest → resolves; `source_pages` point to existing pages → resolve), so trigger frequency is low — hence Medium-Low.
- Why static / earlier rounds missed it: R1 ran the gate only on the concept page (body Connections); R2 swept embeds. No probe placed a dangling wikilink in frontmatter until this round's predict-then-execute.
- Suggested fix (pick one):
  1. **Scope the gate to the body** (strip the frontmatter block before the unresolved scan, the same way `_strip_exempt_regions` already blanks code/`## Source`). Rationale: the downgrade remedy is body-only, and frontmatter link fields (`contributes_to`/`source_pages`) carry a by-construction-resolvable contract; a genuine dangler there is a metadata bug, not the click-to-create phantom-note problem this gate targets. Cleanest + matches the remedy's scope.
  2. **Keep scanning frontmatter, but make the remedy frontmatter-aware** in SKILL.md:213 — a frontmatter hit is fixed by correcting the target or removing the list entry, NOT by bold-ifying. Adds a caveat sentence; keeps the broader catch.
- My lean: option 1 (strip frontmatter) — it aligns the gate's scope with its remedy and removes a foot-gun, at the cost of not catching the rare frontmatter dangler (which would surface anyway as an Obsidian unresolved-link in the graph).

## Behavioral PASS — wiki-auto-research (first dogfood)

A blind executor given the full SKILL.md + `research-note-format.md`, asked to produce a research note that references two existing source pages AND concludes a brand-new concept ("posterior sampling") deserves a not-yet-existing page:
- Wrote the new concept as inline code `` `posterior-sampling` `` (NON-link), citing research-note-format.md:71 verbatim ("written as plain text / inline code, NOT a `[[wikilink]]`, because the page does not exist yet").
- Wrote `source_pages` as `[[Thompson-Sampling]]` / `[[exploration-exploitation]]` (exist by construction), citing the frontmatter spec comment.
- **Zero dangling wikilinks** in the produced note (frontmatter or body) — exactly the format's intended outcome. The R1/T6 `[[new-concept]]`→non-link reframe works end-to-end.
- (Scenario limitation, not a defect: the executor used placeholder `example.org` citations rather than live WebSearch results.)

## Verdict

Round 3 found **one Medium-Low remedy-mismatch** (frontmatter danglers flagged but the body-oriented downgrade remedy breaks YAML there — a narrow, low-trigger foot-gun) and **validated wiki-auto-research end-to-end** (the non-link reframe holds). Signal is diminishing relative to R2's High embed bug — the big precision foot-gun is fixed; H1 is a smaller, scope-alignment issue. Advisory — main agent applies on user approval.
