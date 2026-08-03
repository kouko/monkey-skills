# Plan: dbt-wiki knowledge-skill-pack (`pack`) — v1

**Source brief**: docs/code-toolkit/specs/2026-06-03-dbt-wiki-knowledge-skill-pack.md
**Total tasks**: 5
**Critical-path depth**: 3 (≤5 ✓) — T1→T3→T4; T1/T2 are level-1 parallel leaves; T5 (retire to-sql) sits after T2
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-06-03, after round-1 fixes — see Notes)

> **Scope (v1, minimal)**: build the `pack` skill that emits a portable Agent Skill folder (`<project>-analytics/`: SKILL.md + knowledge/ + references/ + examples/) for an agent that BRINGS ITS OWN warehouse-connect tool. dbt-wiki stays warehouse-agnostic (no DB driver; OQ-A locked = read catalog.json + optional external connect, NOT in this v1).
> **Deferred (noted, not v1 tasks)**: catalog.json/connect value_domain enrichment in `init`; gold-example generation; the synthetic `acme-analytics/` demo bundle.
> **Branch**: continue on `feat/dbt-wiki-nl2sql-to-sql` (tip `c3faac5e`) — it already carries the wanted distill enhancements (SCHEMA `value_domain` + compound join-key, distill-metrics ratio-form, distill-entities value_domain). **KEEP those**; this plan REMOVES the `to-sql` shell and ADDS `pack`. (The branch will be re-titled at PR time; rebase onto current origin/main 762106c6 before PR.)
> **Acceptance**: pure spec/markdown (pack is a SKILL.md + reference docs); RED = grep diagnostics. The emitted bundle must be a FLAT Agent Skill (SKILL.md + single-level subfolders) — same Anthropic convention the repo enforces.
> **Governance**: all examples synthetic (acme); zero real customer data in any committed file; explicit `git add <paths>` only (never `-A`).

---

## Task 1 — pack: bundle-format reference (what the emitted skill folder looks like)

- **Description**: Write `pack/references/bundle-format.md` specifying the OUTPUT structure `pack` emits — a flat Agent Skill folder `<project>-analytics/` containing: `SKILL.md` (entry), `knowledge/` (frozen distilled entities/metrics/concepts + column-cards + relationships incl. compound join-keys + value_domain), `references/` (generation guidance — produced by Task 2), `examples/` (gold few-shot; may be empty in v1), and a **snapshot-annotation block** (in the bundle's SKILL.md frontmatter or a `PROVENANCE.md`): source `manifest_sha` + build date + a "this is a snapshot — re-run `pack` to refresh" note. State the flat-skill constraint (single-level subfolders, no nesting), the portability (drop into `~/.claude/skills/` or any Skills-compatible agent), and that the bundle carries knowledge read on-demand (unbounded). Synthetic examples only.
- **Module**: `dbt-wiki/skills/pack/references/bundle-format.md`
- **Files touched**: `dbt-wiki/skills/pack/references/bundle-format.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-06-03-dbt-wiki-knowledge-skill-pack.md`
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/assets/SCHEMA.md` (the `.dbt-wiki/` knowledge page types that get frozen into `knowledge/`)
- **Acceptance**:
  - **RED**: `test -f dbt-wiki/skills/pack/references/bundle-format.md` fails.
  - **GREEN**: file specifies the `<project>-analytics/` flat-skill output structure (SKILL.md + knowledge/ + references/ + examples/ + snapshot-annotation block with manifest_sha/build-date/rebuild note), the flat-skill constraint, portability, and on-demand knowledge loading.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "交付物 = packager：把 `.dbt-wiki/` 蒸餾知識 → 自包含「知識 skill」bundle (Agent Skill / SKILL.md 形式)" + bundle 內容 item 1 (frozen knowledge) + item 5 "快照註記（來源 manifest_sha + build 日期 + rebuild 指引）" (Smallest End State).

## Task 2 — pack: generation-guidance reference (port A's guardrails)

- **Description**: Write `pack/references/generation-guidance.md` — the SQL-generation guidance that gets copied into each emitted bundle's `references/`, **ported from the to-sql work's semantic guardrails** (aggregate-level SUM/SUM; compound-grain-key joins / no fan-out; value-grounding via value_domain; source disambiguation; temporal CURRENT_DATE / forward-dated caveat) PLUS schema-linking (business term → entity field). Reframe them as **guidance for a warehouse-connected agent**: "generate SQL grounded in this knowledge → **execute via your own warehouse tool** → iterate"; static parse/manifest-existence is an optional pre-check, real validation = execution. Synthetic examples only.
- **Module**: `dbt-wiki/skills/pack/references/generation-guidance.md`
- **Files touched**: `dbt-wiki/skills/pack/references/generation-guidance.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/to-sql/references/prompt-assembly.md` (SOURCE: §1 schema-linking + §4e-§4h guardrails to port/reframe)
  - `/Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-06-03-dbt-wiki-knowledge-skill-pack.md`
- **Acceptance**:
  - **RED**: `test -f dbt-wiki/skills/pack/references/generation-guidance.md` fails.
  - **GREEN**: file carries the 5 guardrail classes (aggregate / grain-fan-out / value-grounding / source / temporal) + schema-linking, reframed as "generate → execute via your warehouse tool → iterate" (not never-execute); static check noted as optional pre-check.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "生成指引（不是執行器）：把先前 A 的語意護欄改寫成『給連倉 agent 的 SQL 生成指引』" (Smallest End State item 2) + Axis 5 "A 的護欄改寫進 bundle 的生成指引".

## Task 3 — pack: emitted-bundle SKILL.md template

- **Description**: Write `pack/assets/bundle-skill-template.md` — the template for the GENERATED bundle's `SKILL.md`: frontmatter (`name: <project>-analytics`, a description scoping it as "ground + generate SQL for <project>'s data; use your own warehouse tool to execute"; trigger phrases) + a **tool-agnostic** body procedure: ① read `knowledge/` for grounding/schema-linking ② generate SQL per `references/generation-guidance.md` ③ **execute via the agent's own warehouse-connect tool** (name none specifically; e.g. "an MCP/CLI that runs SQL") ④ inspect results + iterate. Must reference `knowledge/`, `references/`, `examples/` by relative path and obey flat-skill. Match the bundle-format (Task 1).
- **Module**: `dbt-wiki/skills/pack/assets/bundle-skill-template.md`
- **Files touched**: `dbt-wiki/skills/pack/assets/bundle-skill-template.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/pack/references/bundle-format.md` (Task 1 — structure to match)
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/pack/references/generation-guidance.md` (Task 2 — the guidance the template points the agent at)
- **Acceptance**:
  - **RED**: `test -f dbt-wiki/skills/pack/assets/bundle-skill-template.md` fails.
  - **GREEN**: template has valid frontmatter + the 4-step tool-agnostic procedure (ground → generate → execute-via-your-tool → iterate), references knowledge/references/examples by relative path, flat-skill compliant.
- **Dependencies**: Tasks 1, 2 complete first
- **Independent**: false  # references the bundle-format (T1) + guidance (T2) it must align to
- **Brief item covered**: "SKILL.md（消費契約）：指示 agent ①讀知識 grounding ②生 SQL ③用你的連倉工具執行 ④迭代。工具無關" (Smallest End State item 4).

## Task 4 — pack: SKILL.md (the packager procedure)

- **Description**: Write `pack/SKILL.md` — the packager skill (run by the owner). Procedure: ① locate `.dbt-wiki/` ② create `<project>-analytics/` flat skill folder ③ copy/freeze the knowledge layer into `knowledge/` ④ copy `references/generation-guidance.md` into the bundle's `references/` ⑤ instantiate the bundle's `SKILL.md` from `assets/bundle-skill-template.md` (fill project name/description) ⑥ (examples/ empty in v1, slot reserved) ⑦ **write the snapshot annotation** (source `manifest_sha` from `.dbt-wiki/log.md` + build date + "snapshot — re-run `pack` to refresh") into the bundle per `bundle-format.md` ⑧ verify the emitted folder is a flat valid skill. Frontmatter (`name: pack`, description: "package the dbt-wiki knowledge base into a portable, warehouse-tool-agnostic analytics skill"). State governance: real bundles land in the user's private repo; never commit real ones. References bundle-format + template + generation-guidance by relative path.
- **Module**: `dbt-wiki/skills/pack/SKILL.md`
- **Files touched**: `dbt-wiki/skills/pack/SKILL.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/pack/references/bundle-format.md` (T1)
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/pack/assets/bundle-skill-template.md` (T3)
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/query/SKILL.md` (sibling skill — frontmatter/register + WIKI_DIR locate logic to mirror)
- **Acceptance**:
  - **RED**: `test -f dbt-wiki/skills/pack/SKILL.md` fails; `grep -l "name: pack"` empty.
  - **GREEN**: SKILL.md has frontmatter (name: pack + description) + the 8-step packager procedure (locate → create folder → freeze knowledge → copy guidance → instantiate template → examples slot → **write snapshot annotation** → verify flat); references bundle-format.md, bundle-skill-template.md, generation-guidance.md by relative path; governance note present.
- **Dependencies**: Tasks 1, 2, 3 complete first
- **Independent**: false  # orchestrator; ties together T1/T2/T3 outputs
- **Brief item covered**: "Decision：建 packager，把 `.dbt-wiki/` 蒸餾知識封裝成可攜「知識 skill」bundle" (Decision) + bundle 內容 item 5 snapshot 註記寫入步驟 (Smallest End State).

## Task 5 — Retire the to-sql shell; salvage the validator into pack

- **Description**: Remove the standalone `to-sql` skill shell now that its guidance lives in `pack/references/generation-guidance.md` (Task 2): delete `skills/to-sql/SKILL.md`, `skills/to-sql/references/retrieval.md`, `skills/to-sql/references/prompt-assembly.md`. **Salvage** the static validator: move `skills/to-sql/assets/validate_sql.py` + `validate_sql_test.py` → `skills/pack/assets/` (the bundle's optional static pre-check). Confirm nothing else references `skills/to-sql/` (grep). Update the dbt-wiki README Skills table: remove the `to-sql` row, add a `pack` row.
- **Module**: `dbt-wiki/skills/to-sql/` (the shell being retired; salvage move + README edits reflected in Files touched only)
- **Files touched**: `dbt-wiki/skills/to-sql/` (deleted), `dbt-wiki/skills/pack/assets/validate_sql.py`, `dbt-wiki/skills/pack/assets/validate_sql_test.py`, `dbt-wiki/README.md`, `dbt-wiki/README.ja.md`, `dbt-wiki/README.zh-TW.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/to-sql/assets/validate_sql.py` (to move)
  - `/Users/kouko/GitHub/monkey-skills/dbt-wiki/README.md` (Skills table — swap to-sql→pack)
- **Acceptance**:
  - **RED**: `test -d dbt-wiki/skills/to-sql && echo present` (still present); `grep -rl "to-sql" dbt-wiki/README.md` matches.
  - **GREEN**: `skills/to-sql/` gone; `skills/pack/assets/validate_sql_test.py` runs green (moved validator intact, `PYTHONDONTWRITEBYTECODE=1 python3 …` all pass); no tracked file references `skills/to-sql/` (grep clean); README Skills tables (×3) show `pack` not `to-sql`.
- **Dependencies**: Task 2 completes first  # guidance must be ported before deleting the source shell
- **Independent**: false  # depends on T2 (port before delete)
- **Brief item covered**: "A（永不連倉的獨立 to-sql skill）退場，好東西併入 bundle … validate_sql.py 降為可選 pre-check" (Axis 5).

## Notes

- **Round-1 reviewer fixes (NEEDS_REVISION → PASS)**: plan-document-reviewer flagged 2 gaps, both closed exactly per its suggested_fix: (Check 4) T5 `Module` named two modules → now single `dbt-wiki/skills/to-sql/`, salvage/README reflected in Files-touched only; (Check 8) brief Smallest-End-State item 5 (snapshot annotation: manifest_sha + build date + rebuild note) was unmapped → added to T1 (bundle-format spec + GREEN) and T4 (packager step ⑦ + GREEN), Brief-item-covered updated on both. Mechanical/targeted closures; verdict flipped to PASS without a 2nd reviewer round.
- **Dependency shape**: Level-1 leaves **T1 ∥ T2** (disjoint files in pack/references/, no semantic dep) → both `Independent: true`. **T3** deps T1+T2 (aligns to both). **T4** deps T1+T2+T3 (orchestrator). **T5** deps T2 (port guidance before deleting the to-sql shell). Critical path = T1→T3→T4 = **depth 3**.
- **Branch reality**: work continues on `feat/dbt-wiki-nl2sql-to-sql` (keeps the distill enhancements already there: SCHEMA value_domain + compound join-key, distill-metrics ratio-form, distill-entities value_domain — these ARE the rich knowledge the bundle freezes). The `to-sql` shell (added on this branch) is removed by T5. Rebase onto current origin/main (762106c6) before PR.
- **Deferred (OQ-D + enrichment, separate increments)**: `init` catalog.json/connect value_domain enrichment (OQ-A mechanism); gold-example generation into `examples/`; the synthetic `acme-analytics/` demo bundle (note: a demo bundle is itself a skill folder — must live OUTSIDE `skills/` to avoid skill-in-skill nesting, e.g. `dbt-wiki/examples/acme-analytics/`; decide at that increment).
- **Finish-time (not plan tasks)**: version bump (2.3.0 → 2.4.0 or per the eventual merge state) + CHANGELOG; whole-branch review; verification (moved validator test green + folder-structure hook clean).
- **Flat-skill guard**: both `skills/pack/` AND every emitted `<project>-analytics/` bundle must be flat (single-level subfolders). The packager (T4) verifies its output; reviewers check `skills/pack/`.
