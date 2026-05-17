# Plan: wiki-ingest language policy — part 1 (commit 1 scope)

**Source brief**: docs/superpowers/specs/2026-05-18-wiki-ingest-language-policy-design.md
**Total tasks**: 4 (≤5 ✓)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-05-18 round-1, 14/14 checks)

## Scope of this plan

**Commit 1 only** per brief §7. Builds on v3.10.0 main `4e00610` (PR #307 MERGED). Adds the core language-policy infrastructure to wiki-ingest + page-format.md split + wiki-setup config template. SSOT distribute.py / verify-drift.py / 4 functional copies / wiki-lint new rule deferred to part-2; pytest CC-LL fixtures + dogfood deferred to part-3.

**Commit 1 deliverables**:
- New `obsidian/skills/wiki-ingest/references/language-policy.md` (1-mechanism + decision tree + preserve-terms protocol + worked example)
- `obsidian/skills/wiki-ingest/SKILL.md` patches: pre-flight reads 3 new config fields / lazy-load table adds language-policy.md / STEP 4c adds language resolution step
- `obsidian/skills/wiki-ingest/references/page-format.md` split: Filename rules + Body language sections + aliases conditional MUST schema
- `obsidian/skills/wiki-setup/SKILL.md` config template extension: 3 new optional fields

**Out of part-1 scope** (deferred):
- distribute.py + verify-drift.py + 4 functional copies + CI verify-drift step → part-2
- wiki-lint new rule (slug ≠ body language → aliases required) → part-2
- pytest CC-LL-01..05 + dogfood on kouko-obsidian-vault → part-3
- Version bump v3.10.0 → v3.11.0 → part-3 (finishing-a-branch phase)

## Dependency graph

```
T1 (language-policy.md)     T3 (page-format.md split)     T4 (wiki-setup template)
        \                                                              /
         ↘                                                            ↙
          T2 (wiki-ingest/SKILL.md — references T1 in lazy-load table)
```

- Wave 1 (parallel): T1, T3, T4 — all independent, different files, no shared symbols
- Wave 2 (sequential): T2 — depends on T1 (lazy-load table references new language-policy.md; sequencing avoids parallel-dispatch doc-code race per [[parallel-dispatch-doc-code-race]] memory)

---

## Task 1 — Create language-policy.md (new lazy-load reference)

- **Description**: Create `obsidian/skills/wiki-ingest/references/language-policy.md` per brief §2 + §3 + §4. Single-mechanism + decision-tree spec: ~120 lines markdown structured as: (1) Purpose — explain LANGUAGE_POLICY=enabled vs unset semantics; (2) Decision tree spec — path-based / tag-based rules with mandatory fallback to PRIMARY_LANGUAGE; (3) preserve-terms protocol — file format, grouping, ASCII vs CJK matching rules; (4) aliases conditional MUST — when slug language ≠ body language; (5) Slug vs body language strict decoupling (slug authority = page-format.md, body authority = this file); (6) Worked example — kouko-style multi-language vault tree (folder-based: investing/→zh-TW, JP-design clusters → PRIMARY+ja-term preserve, research/coding → en). Style matches sibling references (delta-tracking.md / category-routing.md / batching-policy.md).
- **Module**: `obsidian/skills/wiki-ingest/references/language-policy.md`
- **Files touched**: `obsidian/skills/wiki-ingest/references/language-policy.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-language-policy/docs/superpowers/specs/2026-05-18-wiki-ingest-language-policy-design.md (§2 mechanism, §3 config, §4 frontmatter aliases)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-language-policy/obsidian/skills/wiki-ingest/references/delta-tracking.md (sibling style reference)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-language-policy/obsidian/skills/wiki-ingest/references/batching-policy.md (sibling style — v3.10.0 8-section structure to mirror)
  - /Users/kouko/kouko-obsidian-vault/research/2026-05-18 wiki-ingest 語言策略優化設計研究.md (upstream design note — Layer B outline)
- **Acceptance**:
  - **RED**: `ls obsidian/skills/wiki-ingest/references/language-policy.md` returns "No such file"
  - **GREEN**: file exists; `grep -cE '^## ' obsidian/skills/wiki-ingest/references/language-policy.md` returns ≥ 6 (six top-level sections); `grep -c 'PRIMARY_LANGUAGE\|LANGUAGE_POLICY\|PRESERVE_TERMS' obsidian/skills/wiki-ingest/references/language-policy.md` ≥ 3; `grep -ciE 'aliases.*MUST\|conditional MUST' obsidian/skills/wiki-ingest/references/language-policy.md` ≥ 1 (aliases rule documented)
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: §2 Mechanism (1-mechanism binary switch + decision tree); §4 aliases conditional MUST (rule definition); §5 skill-list row 2 (language-policy.md new reference)

## Task 2 — Patch wiki-ingest/SKILL.md (pre-flight + lazy-load table + STEP 4c)

- **Description**: Edit `obsidian/skills/wiki-ingest/SKILL.md` (current v3.10.0 head) three sections per brief §3 + §5: (a) **Pre-flight** — extend the `.obsidian-wiki.config` config-read paragraph to list `OBSIDIAN_WIKI_PRIMARY_LANGUAGE`, `OBSIDIAN_WIKI_LANGUAGE_POLICY`, `OBSIDIAN_WIKI_PRESERVE_TERMS_FILE` as optional fields alongside existing `OBSIDIAN_WIKI_BATCH_ORDER`; (b) **Lazy-load reference table** — add row `references/language-policy.md | Before STEP 4c — only when LANGUAGE_POLICY=enabled`; (c) **STEP 4c (For each target wiki page)** — insert a 3-4 line "Language resolution" paragraph at the top of the section: "If `OBSIDIAN_WIKI_LANGUAGE_POLICY=enabled`, load `references/language-policy.md`; resolve body language per the decision tree. Slug remains ASCII per page-format.md. If `OBSIDIAN_WIKI_PRESERVE_TERMS_FILE` is set, load it and treat listed terms as no-translate." Don't refactor surrounding STEP 4c content.
- **Module**: `obsidian/skills/wiki-ingest/SKILL.md`
- **Files touched**: `obsidian/skills/wiki-ingest/SKILL.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-language-policy/obsidian/skills/wiki-ingest/SKILL.md (v3.10.0 current state; pre-flight ~lines 10-15, lazy-load table ~21-26, STEP 4c "For each target wiki page" inside STEP 4 per-source loop)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-language-policy/obsidian/skills/wiki-ingest/references/language-policy.md (T1 output — confirm filename for lazy-load table reference)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-language-policy/docs/superpowers/specs/2026-05-18-wiki-ingest-language-policy-design.md (§3 config, §5 skill list row 1)
- **Acceptance**:
  - **RED**:
    - `grep -c 'OBSIDIAN_WIKI_PRIMARY_LANGUAGE' obsidian/skills/wiki-ingest/SKILL.md` returns 0
    - `grep -c 'OBSIDIAN_WIKI_LANGUAGE_POLICY' obsidian/skills/wiki-ingest/SKILL.md` returns 0
    - `grep -c 'language-policy.md' obsidian/skills/wiki-ingest/SKILL.md` returns 0
  - **GREEN**:
    - `grep -c 'OBSIDIAN_WIKI_PRIMARY_LANGUAGE' obsidian/skills/wiki-ingest/SKILL.md` ≥ 1 (pre-flight)
    - `grep -c 'OBSIDIAN_WIKI_LANGUAGE_POLICY' obsidian/skills/wiki-ingest/SKILL.md` ≥ 1 (pre-flight)
    - `grep -c 'language-policy.md' obsidian/skills/wiki-ingest/SKILL.md` ≥ 2 (lazy-load table + STEP 4c reference)
    - `grep -cE '^## STEP' obsidian/skills/wiki-ingest/SKILL.md` unchanged at 6 (no accidental STEP renumber)
    - `.claude/hooks/validate-skill-folder-structure.sh` passes
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: §3 Config schema (pre-flight reads 3 new fields); §5 skill-list row 1 (SKILL.md patches); §2 (STEP 4c invokes language-policy.md decision tree)

## Task 3 — Split page-format.md (filename / body language) + aliases conditional MUST schema

- **Description**: Edit `obsidian/skills/wiki-ingest/references/page-format.md` per brief §4 + §5 row 3. Two concrete changes: (a) **Split existing content into two top-level sections**: `## Filename rules (authority: page-format.md)` containing existing filename / uniqueness rules; `## Body language (authority: language-policy.md when loaded)` containing default-legacy-behavior note + pointer to `references/language-policy.md` for when LANGUAGE_POLICY=enabled + slug-body-decoupling rule + summary-language rule. (b) **Frontmatter schema update** — change the "Frontmatter (8 fields, all required)" header / table to "Frontmatter (8 required + 1 conditional)" and add `aliases` as a 9th conditional MUST entry with rule: "Required when slug language ≠ body language (e.g. ASCII slug + zh-TW body). Optional otherwise. Lint-enforced by wiki-lint." Don't remove the existing "Other skills... reference their own copies" line at top — keep but the file should still be the canonical source (the "do not cross-link" rule stays).
- **Module**: `obsidian/skills/wiki-ingest/references/page-format.md`
- **Files touched**: `obsidian/skills/wiki-ingest/references/page-format.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-language-policy/obsidian/skills/wiki-ingest/references/page-format.md (current state — header lines 1-3, frontmatter table lines 5-17)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-language-policy/docs/superpowers/specs/2026-05-18-wiki-ingest-language-policy-design.md (§4 frontmatter schema, §5 row 3)
- **Acceptance**:
  - **RED**:
    - `grep -cE '^## Filename rules' obsidian/skills/wiki-ingest/references/page-format.md` returns 0
    - `grep -cE '^## Body language' obsidian/skills/wiki-ingest/references/page-format.md` returns 0
    - `grep -c 'aliases' obsidian/skills/wiki-ingest/references/page-format.md` returns 0
  - **GREEN**:
    - `grep -cE '^## Filename rules' obsidian/skills/wiki-ingest/references/page-format.md` returns 1
    - `grep -cE '^## Body language' obsidian/skills/wiki-ingest/references/page-format.md` returns 1
    - `grep -c 'aliases' obsidian/skills/wiki-ingest/references/page-format.md` ≥ 2 (schema entry + rule description)
    - `grep -ciE 'conditional MUST\|when slug language' obsidian/skills/wiki-ingest/references/page-format.md` ≥ 1 (conditional rule documented)
    - Existing 8 required fields (title / type / domain / status / updated / tags / sources_count / summary) still present (`grep -c '^| \`title\`' page-format.md` ≥ 1 etc.)
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: §4 frontmatter schema (aliases conditional MUST); §5 skill-list row 3 (page-format.md split + aliases)

## Task 4 — Extend wiki-setup/SKILL.md config template

- **Description**: Edit `obsidian/skills/wiki-setup/SKILL.md` — locate the `.obsidian-wiki.config` template block (per v3.10.0 PR #307 already contains `OBSIDIAN_WIKI_BATCH_ORDER`). Append 3 new lines with comment blocks for `OBSIDIAN_WIKI_PRIMARY_LANGUAGE`, `OBSIDIAN_WIKI_LANGUAGE_POLICY`, `OBSIDIAN_WIKI_PRESERVE_TERMS_FILE`. Match existing template comment style (2-line description above each KEY=value line). All three are optional; default unset = legacy. Per brief §3 wording.
- **Module**: `obsidian/skills/wiki-setup/SKILL.md`
- **Files touched**: `obsidian/skills/wiki-setup/SKILL.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-language-policy/obsidian/skills/wiki-setup/SKILL.md (current state — find template block containing OBSIDIAN_WIKI_BATCH_ORDER from PR #307)
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-language-policy/docs/superpowers/specs/2026-05-18-wiki-ingest-language-policy-design.md (§3 exact wording for 3 fields)
- **Acceptance**:
  - **RED**: `grep -c 'OBSIDIAN_WIKI_PRIMARY_LANGUAGE' obsidian/skills/wiki-setup/SKILL.md` returns 0; same for LANGUAGE_POLICY and PRESERVE_TERMS_FILE
  - **GREEN**:
    - `grep -c 'OBSIDIAN_WIKI_PRIMARY_LANGUAGE=' obsidian/skills/wiki-setup/SKILL.md` returns 1
    - `grep -c 'OBSIDIAN_WIKI_LANGUAGE_POLICY=' obsidian/skills/wiki-setup/SKILL.md` returns 1
    - `grep -c 'OBSIDIAN_WIKI_PRESERVE_TERMS_FILE=' obsidian/skills/wiki-setup/SKILL.md` returns 1
    - Existing `OBSIDIAN_WIKI_BATCH_ORDER=oldest-first` still present (no accidental removal)
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: §3 Config schema (template synced); §5 skill-list row 4 (wiki-setup template)

---

## Notes

- **Wave 1 parallel dispatch eligible**: T1 + T3 + T4 all marked `Independent: true` with disjoint `Files touched`. `dispatching-parallel-agents` MAY dispatch all 3 implementers in one assistant message. SDD sequential fallback always safe.
- **T2 must sequence after T1** to avoid parallel-dispatch doc-code race ([[parallel-dispatch-doc-code-race]] memory): T2 references language-policy.md in lazy-load table; if dispatched parallel, T2 might write the reference before T1 lands the actual file. Even though grep diagnostic catches the case, sequencing eliminates the race upfront.
- **No pytest in part-1**: language-policy.md is markdown spec; SKILL.md / page-format.md / wiki-setup are also markdown. No Python implementation lands here — pytest CC-LL fixtures wait for part-3 (when wiki-lint rule + dogfood infrastructure all align).
- This plan covers **commit 1 only** of the brief's 3-commit plan (§7). part-2 will cover distribute.py + verify-drift.py + 4 functional copies + wiki-lint new rule; part-3 will cover pytest CC-LL fixtures + dogfood + version bump.

## Out of scope (for part-2 / part-3 plans)

| Brief item | Deferred to |
|---|---|
| `obsidian/scripts/distribute.py` + `verify-drift.py` | part-2 |
| 4 functional copies of language-policy.md to sibling skills | part-2 |
| `.github/workflows/test-obsidian.yml` verify-drift step | part-2 |
| `obsidian/skills/wiki-lint/SKILL.md` new lint rule (slug ≠ body lang → aliases required) | part-2 |
| pytest `test_language_policy.py` CC-LL-01..05 | part-3 |
| Dogfood on `~/kouko-obsidian-vault` | part-3 |
| Version bump `obsidian/.claude-plugin/plugin.json` 3.10.0 → 3.11.0 | part-3 |
| PR title / body composition | finishing-a-branch phase |

## Open questions surfaced (track to part-2 / part-3)

1. **language-policy.md "generic vs kouko-style" decision tree** (brief Open Q1) — T1 implementer to decide: generic tree (just fallback + 1-2 generic example rows) + Examples section showing kouko-style customizations OR ship kouko-style tree as default. Recommend generic for portability; surface in T1 self_review for reviewer to weigh.
2. **lazy-load table convention check** (T2) — the table per v3.10.0 lists 4 references (delta-tracking / category-routing / page-format / batching-policy). T2 adds language-policy.md as 5th. The "Before STEP NM" convention from v3.10.0 should be honored (e.g. category-routing = Before STEP 4b, page-format = Before STEP 4c). language-policy.md fires Before STEP 4c (per design §5). Verify in T2.
3. **page-format.md "do not cross-link" header** (T3) — header line 3 says other skills reference their own copies. After this PR introduces distribute.py for language-policy.md, the page-format.md header may also want a similar update (mention distribute.py? or just for language-policy.md scope?). Out of part-1 scope; revisit in part-2 when distribute.py lands.
