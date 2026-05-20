# Plan: wiki-ingest ref page TL;DR list + Detailed Extract — part 1 (single-plan scope)

**Source brief**: docs/superpowers/specs/2026-05-20-wiki-ingest-ref-page-tldr-detailed-extract-design.md
**Total tasks**: 3 (≤5 ✓)
**Execution order**: parallel-where-possible (2 waves)
**Plan-document-reviewer verdict**: PASS (2026-05-20 round-1, 14/14 checks)

## Scope of this plan

**Single-plan scope** (no part-2/3 split needed — brief §7 estimates ~111 LOC across 3 atomic tasks). Builds on main `9c10984` (v3.13.0). Adds:

- Section rename: `## Source Excerpt / TL;DR` → `## TL;DR`
- Section format change: prose 2-4 sentences → free-form 3-7 bullets, sentence-fragment style
- New section: `## Detailed Extract` (MAY / advisory)
- Body order: Source → TL;DR → Detailed Extract → Key Contributions
- Version bump v3.13.0 → v3.14.0

**Out of scope** (Phase 2 future PRs):
- `/wiki-relang` bulk re-extract for 468 existing pages
- wiki-lint L15 enforcement on TL;DR / Detailed Extract format
- Source-type-specific templates
- `## Detailed Extract` MUST upgrade

**Migration**: Natural drift only (existing pages stay legacy `## Source Excerpt / TL;DR` until re-ingest).

## Dependency graph

```
T1 (page-format.md rewrite — canonical)      T3 (version bump)
        \                                            /
         ↘                                          ↙
                T2 (SKILL.md STEP 4d mirror — sequential after T1
                    to avoid parallel-dispatch doc-code race per
                    [[parallel-dispatch-doc-code-race]] memory)
```

- **Wave 1 (parallel)**: T1 + T3 — different files, no shared symbols, both `Independent: true`
- **Wave 2 (sequential)**: T2 — depends on T1 (mirrors canonical spec; race risk if parallel because T2 needs T1's exact sub-heading vocabulary)

---

## Task 1 — Rewrite page-format.md §Reference page body structure (canonical spec)

- **Description**: Edit `obsidian/skills/wiki-ingest/references/page-format.md` §Reference page body structure (lines 45-87 per recon). Apply 4 changes per design brief §2-§4: (a) Rename `## Source Excerpt / TL;DR` → `## TL;DR`; (b) Reshape from "2-4 sentence neutral description" → "free-form 3-7 bullets, sentence-fragment style, no nested sub-bullets"; (c) Add new `## Detailed Extract` MAY section spec — sub-heading vocabulary (Key Claims / Examples / Notable Quotes / Cross-references / Methodology / Caveats; free-form, LLM picks 2-4 per source; source-proportional length, no hard cap); (d) Update body section order to Source → TL;DR → Detailed Extract → Key Contributions. Preserve existing `## Source` wikilink format warning block (v3.12.0 L14-related). Update worked examples in the spec to show new format (one thin source, one substantive source).
- **Module**: `obsidian/skills/wiki-ingest/references/page-format.md`
- **Files touched**: `obsidian/skills/wiki-ingest/references/page-format.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-ref-page-extract/obsidian/skills/wiki-ingest/references/page-format.md (current state — §Reference page body structure at line 45+)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-ref-page-extract/docs/superpowers/specs/2026-05-20-wiki-ingest-ref-page-tldr-detailed-extract-design.md (§2 TL;DR + §3 Detailed Extract + §4 body order + worked examples)
- **Acceptance**:
  - **RED**:
    - `grep -c 'Source Excerpt' obsidian/skills/wiki-ingest/references/page-format.md` returns ≥ 1 (old name still present)
    - `grep -c '## Detailed Extract' obsidian/skills/wiki-ingest/references/page-format.md` returns 0
    - `grep -c '2.4 sentence' obsidian/skills/wiki-ingest/references/page-format.md` returns ≥ 1 (old wording still present)
  - **GREEN**:
    - `grep -c 'Source Excerpt' obsidian/skills/wiki-ingest/references/page-format.md` returns 0 (old name removed)
    - `grep -c '## TL;DR' obsidian/skills/wiki-ingest/references/page-format.md` returns ≥ 1
    - `grep -c '## Detailed Extract' obsidian/skills/wiki-ingest/references/page-format.md` returns ≥ 1
    - `grep -ciE '3.7 bullets|sentence.fragment' obsidian/skills/wiki-ingest/references/page-format.md` returns ≥ 1 (new TL;DR format documented)
    - `grep -ciE 'MAY|advisory|strongly encouraged' obsidian/skills/wiki-ingest/references/page-format.md` returns ≥ 1 (Detailed Extract severity documented)
    - `grep -ciE 'Key Claims|Notable Quotes|Methodology' obsidian/skills/wiki-ingest/references/page-format.md` returns ≥ 2 (sub-heading vocabulary present)
    - Existing `## Source` wikilink warning block preserved (`grep -c 'bare basename' obsidian/skills/wiki-ingest/references/page-format.md` ≥ 1)
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: §2 TL;DR new format; §3 Detailed Extract new section; §4 body order; §5 row 1 (page-format.md rewrite)

## Task 2 — Update wiki-ingest/SKILL.md STEP 4d (in-flight template mirror)

- **Description**: Edit `obsidian/skills/wiki-ingest/SKILL.md` STEP 4d (currently shows the ref-page template inline; see `### 4d. Create/update reference page` block). Mirror T1's canonical spec changes: (a) Replace `## Source Excerpt / TL;DR\n2–4 sentence neutral description...` block with `## TL;DR\n- bullet 1\n- bullet 2\n...` (free 3-7 bullets); (b) Add `## Detailed Extract` block with placeholder sub-headings (`### Key Claims` etc.) marked as "include when source has substance worth preserving — see references/page-format.md §Reference page body structure for full spec"; (c) Reorder body sections to Source → TL;DR → Detailed Extract → Key Contributions; (d) Preserve `## Source` wikilink warning callout (the long `> [!warning]` block about basename format — that stays verbatim). Don't touch other STEP 4 sub-sections (4a / 4b / 4c / 4e / 4f / 4g).
- **Module**: `obsidian/skills/wiki-ingest/SKILL.md`
- **Files touched**: `obsidian/skills/wiki-ingest/SKILL.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-ref-page-extract/obsidian/skills/wiki-ingest/SKILL.md (current STEP 4d block)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-ref-page-extract/obsidian/skills/wiki-ingest/references/page-format.md (T1 output — for canonical sub-heading vocabulary + worked example wording to mirror)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-ref-page-extract/docs/superpowers/specs/2026-05-20-wiki-ingest-ref-page-tldr-detailed-extract-design.md (§2-§4)
- **Acceptance**:
  - **RED**:
    - `grep -c 'Source Excerpt' obsidian/skills/wiki-ingest/SKILL.md` returns ≥ 1 (old name in STEP 4d template)
    - `grep -c '## Detailed Extract' obsidian/skills/wiki-ingest/SKILL.md` returns 0
    - `grep -c '2.4 sentence' obsidian/skills/wiki-ingest/SKILL.md` returns ≥ 1
  - **GREEN**:
    - `grep -c 'Source Excerpt' obsidian/skills/wiki-ingest/SKILL.md` returns 0
    - `grep -c '## TL;DR' obsidian/skills/wiki-ingest/SKILL.md` returns ≥ 1 (template)
    - `grep -c '## Detailed Extract' obsidian/skills/wiki-ingest/SKILL.md` returns ≥ 1 (template placeholder + description)
    - `grep -ciE 'bare basename' obsidian/skills/wiki-ingest/SKILL.md` ≥ 1 (existing `## Source` wikilink warning callout preserved verbatim)
    - `grep -cE '^### 4' obsidian/skills/wiki-ingest/SKILL.md` unchanged at 7 (4a/4b/4c/4d/4e/4f/4g — no accidental sub-section addition/removal)
    - `.claude/hooks/validate-skill-folder-structure.sh` passes (auto-fires on Edit)
- **Dependencies**: Task 1 completes first
- **Independent**: false (sequential after T1; mirror task — would race against T1's commit if parallel-dispatched per [[parallel-dispatch-doc-code-race]])
- **Brief item covered**: §5 row 2 (SKILL.md STEP 4d mirror); §4 body order; §2/§3 (consistent template with canonical spec)

## Task 3 — Version bump v3.13.0 → v3.14.0 + marketplace sync

- **Description**: Bump `obsidian/.claude-plugin/plugin.json` `version` field from `3.13.0` → `3.14.0` (minor bump per brief §8 — body schema change, backward compatible). Verify `scripts/check-marketplace-description-sync.py` exits 0 (no drift; marketplace.json description should already match).
- **Module**: `obsidian/.claude-plugin/plugin.json`
- **Files touched**: `obsidian/.claude-plugin/plugin.json` (marketplace.json only touched if drift exists)
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-ref-page-extract/obsidian/.claude-plugin/plugin.json (current 3.13.0)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-ref-page-extract/.claude-plugin/marketplace.json (sync target — touch only if drift)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-ref-page-extract/scripts/check-marketplace-description-sync.py (CI enforcer)
- **Acceptance**:
  - **RED**: `jq -r .version obsidian/.claude-plugin/plugin.json` returns `3.13.0`
  - **GREEN**:
    - `jq -r .version obsidian/.claude-plugin/plugin.json` returns `3.14.0`
    - `python3 scripts/check-marketplace-description-sync.py` exits 0 (no drift)
- **Dependencies**: none
- **Independent**: true (parallel with T1 — different file; no shared state)
- **Brief item covered**: §5 row 3 (version bump); §8 PR naming (v3.14.0 minor bump)

---

## Notes

- **Wave 1 parallel**: T1 + T3 dispatchable in one assistant message via `dispatching-parallel-agents` (both `Independent: true`, disjoint `Files touched`: `page-format.md` vs `plugin.json`).
- **Wave 2 sequential**: T2 mirrors T1's canonical decisions (sub-heading vocabulary, exact wording). Sequencing eliminates parallel-dispatch doc-code race ([[parallel-dispatch-doc-code-race]]) — T2 reads T1's committed page-format.md to ensure consistency.
- **No pytest in this plan** — pure markdown spec change (page-format.md + SKILL.md) + JSON version bump; no script-side change. Format compliance is Claude-prose-enforced per [[cc-ll-pytest-infeasibility]]; manual verification post-merge via dogfood (re-ingest 1 sample source).
- **No wiki-lint changes** — L14 (`## Source` wikilink) unchanged; no L15 added for TL;DR / Detailed Extract format (Phase 2 if dogfood demands).
- **Migration**: existing 468 ref pages stay legacy; natural drift on source modify triggers re-ingest with new spec. Matches v3.10.0 / v3.11.0 / v3.12.0 migration pattern. No backfill in MVP scope.

## Out of scope (for Phase 2 future PRs)

| Brief item | Deferred to |
|---|---|
| `/wiki-relang`-style bulk re-extract for 468 existing pages | Phase 2 (triggered if dogfood demand emerges) |
| wiki-lint L15 enforcement on `## TL;DR` / `## Detailed Extract` format | Phase 2 (if dogfood shows ingest skipping sections) |
| Source-type-specific templates (`source_type` frontmatter) | Phase 2 (YAGNI for MVP) |
| `## Detailed Extract` MUST upgrade | Phase 2 conditional on dogfood |
| Density-floor lint (LLM judges LLM) | Phase 2 conditional |
| pytest CC-style fixtures for ref page format | Out of scope (infeasible — see [[cc-ll-pytest-infeasibility]]) |
| Post-merge LLM-behavior dogfood (re-ingest sample source on real vault) | Manual user action post-merge |
| PR title / body composition + finishing-a-branch close-out | finishing-a-branch phase |

## Open questions surfaced (track to finishing-a-branch / post-merge)

1. **`## Detailed Extract` sub-heading vocabulary canonical list size** (brief Open Q1) — implementer T1 decides: ship all 6 suggested sub-headings OR shorter starter set (3-4). Surface in T1 self_review for reviewer to weigh.
2. **Detailed Extract length soft cap** (brief Open Q2) — defer to dogfood; if Extracts blow past 2000 words consistently, add Phase 2 guidance.
3. **Old pages with `## Source Excerpt / TL;DR` heading** (brief Open Q3) — wiki-query Tier 2 reads full body so no special handling needed; verify in T2 self_review that no heading-specific extraction logic exists in wiki-query / wiki-cross-linker that would break on mixed-heading vault.
