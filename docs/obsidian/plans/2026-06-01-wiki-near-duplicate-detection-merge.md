# Plan: obsidian wiki near-duplicate detection (ingest + lint) + LLM auto-merge (wiki-merge)

Source brief: docs/obsidian/specs/2026-06-01-wiki-near-duplicate-detection-merge.md (Decision REVISED v2)
Total tasks: 9 (uncapped; wide-shallow by design)
Critical-path depth: 4 (≤5) — longest chain T1 → T3 → T4/T5 → T9
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (14/14, 0 gaps, 2026-06-01 reshape v2)

Nature: prose-only (SKILL.md + reference markdown). No pytest — acceptance = grep/Read diagnostics. Skill-folder hook applies (flat subfolders only).

Locked design (brief v2):
- Detection (shared method) has TWO homes: wiki-ingest STEP 4c (prevent-new, HIGH-confidence prompt) + wiki-lint L15 (sweep-existing, read-only). Method = string/alias blocking → LLM-as-judge + self-reported confidence (HIGH/MID/LOW). No embedding, no vector DB.
- Merge = new wiki-merge skill (writes). Human gates the TRIGGER; LLM auto-EXECUTES (draft + apply + archive + verify + log + iterate). Safety invariants inline in SKILL.md (no heavy survivorship reference).
- archive convention = `wiki/_archive/<date>/`.
- Cross-skill duplication: detection method appears in wiki-ingest/references/near-duplicate-detection.md (full) AND inline in lint-checks.md L15 (all-pairs framing). Per repo skill-independence convention — duplicated, kept consistent (like L12's inline heuristic).

Parallel waves:
- Wave 1 (Independent): T1 (detection reference), T6 (wiki-merge skeleton) — disjoint new files.
- Wave 2: T2 (←T1, ingest SKILL.md), T3 (←T1, lint-checks.md), T7 (←T6, merge SKILL.md) — disjoint.
- Wave 3: T4 (←T3, lint SKILL.md), T5 (←T3, lint-checks.md), T8 (←T7, merge SKILL.md) — disjoint.
- Wave 4: T9 (←T2,T4,T5,T8).

---

## Task 1 — near-duplicate detection method reference
- Description: Write new reference defining the shared detection method: (a) normalization rules (lowercase, strip hyphens, drop trailing qualifier tokens e.g. `-MAB`), (b) string/alias blocking via Levenshtein + Jaro-Winkler on normalized `title`+`aliases`+slug to produce candidate pairs, (c) LLM-as-judge confirm step (input: both pages' title+summary+key-facts; output: same/different + reason + self-reported confidence HIGH/MID/LOW), (d) explicit "no embedding / no vector DB — obsidian-native string+LLM only" note. This reference is owned by wiki-ingest; lint's L15 restates it inline.
- Module: obsidian/skills/wiki-ingest
- Files touched: obsidian/skills/wiki-ingest/references/near-duplicate-detection.md
- Context paths:
  - obsidian/skills/wiki-lint/references/lint-checks.md (L07 Levenshtein-instruction style; L12 inline-heuristic precedent)
  - obsidian/skills/wiki-ingest/references/page-format.md (aliases, title fields)
  - docs/obsidian/specs/2026-06-01-wiki-near-duplicate-detection-merge.md
- Acceptance:
  - RED: `test -f obsidian/skills/wiki-ingest/references/near-duplicate-detection.md` → absent.
  - GREEN: file present with 4 sections (Normalization / Blocking / LLM-judge+confidence / obsidian-native note); confidence tiers HIGH/MID/LOW defined.
- Dependencies: none
- Independent: true
- Brief item covered: "偵測（共用一套 prose method）… string/alias blocking → LLM-as-judge … 自報信賴度 HIGH/MID/LOW（非 embedding）"

## Task 2 — wiki-ingest STEP 4c detection extension (prevent-new)
- Description: Extend wiki-ingest SKILL.md STEP 4c: after the existing exact-name uniqueness check, run near-duplicate detection per near-duplicate-detection.md against existing pages. On a HIGH-confidence near-duplicate, prompt the user "近重複 — 這像是 [existing page] 的不同命名,要用 /wiki-merge 合併嗎?" and let the user decide (do NOT auto-merge, do NOT block the page). Below HIGH confidence: stay silent (preserve STEP 4c restraint — only prompt on real candidates).
- Module: obsidian/skills/wiki-ingest
- Files touched: obsidian/skills/wiki-ingest/SKILL.md
- Context paths:
  - obsidian/skills/wiki-ingest/SKILL.md (STEP 4c at lines 165-179)
  - obsidian/skills/wiki-ingest/references/near-duplicate-detection.md (T1 output)
- Acceptance:
  - RED: `grep -i 'near-duplicate\|wiki-merge' obsidian/skills/wiki-ingest/SKILL.md` → absent in STEP 4c.
  - GREEN: STEP 4c runs near-dup detection, prompts only on HIGH confidence, routes user to /wiki-merge, never auto-merges/blocks.
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "wiki-ingest STEP 4c 擴充(防新)… 只在 HIGH 信賴度才提示 … 人決定是否觸發"

## Task 3 — wiki-lint L15 entry (sweep-existing)
- Description: Add `### L15 — Near-duplicate pages` to lint-checks.md (Semantic section): all-pairs read-only sweep restating the detection method inline (normalize → string/alias block → LLM-judge), severity=warning, output = candidate pairs + confidence + "run /wiki-merge to consolidate"; add an L15 row to the "Action recommendations per check" table and an L15 line in the output-format example.
- Module: obsidian/skills/wiki-lint
- Files touched: obsidian/skills/wiki-lint/references/lint-checks.md
- Context paths:
  - obsidian/skills/wiki-lint/references/lint-checks.md (L12 inline-heuristic + L13 pattern; action table; output format)
  - obsidian/skills/wiki-ingest/references/near-duplicate-detection.md (T1 — keep method consistent)
- Acceptance:
  - RED: `grep '### L15' obsidian/skills/wiki-lint/references/lint-checks.md` → empty.
  - GREEN: L15 section (all-pairs sweep, inline method, warning) + action-table row + output-format line present; points to /wiki-merge.
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "wiki-lint L15(掃舊)— 唯讀稽核,all-pairs 掃既有頁 … 補既存重複盲區"

## Task 4 — wiki-lint SKILL.md count 14→15
- Description: Update wiki-lint/SKILL.md: "14 health checks"→15 (description frontmatter + "Run the 14 checks"); add L15 to STEP 2 bullet list; add L15 (warning) to the severity line.
- Module: obsidian/skills/wiki-lint
- Files touched: obsidian/skills/wiki-lint/SKILL.md
- Context paths:
  - obsidian/skills/wiki-lint/SKILL.md (lines 3, 8, 26-50)
- Acceptance:
  - RED: `grep '14' obsidian/skills/wiki-lint/SKILL.md` still shows 14-check phrasing; no L15.
  - GREEN: SKILL.md says "15 …checks", L15 in bullet list + severity line.
- Dependencies: Task 3 completes first
- Independent: true
- Brief item covered: "wiki-lint L15(掃舊)" — count reflects the new check

## Task 5 — L06 cross-reference to L15
- Description: In lint-checks.md L06 (Orphan pages), add one sentence: before treating a page as orphan, check it is not an L15 near-duplicate candidate (so the L06→cross-linker recommendation doesn't entrench a duplicate). Do not change L06's detection logic.
- Module: obsidian/skills/wiki-lint
- Files touched: obsidian/skills/wiki-lint/references/lint-checks.md
- Context paths:
  - obsidian/skills/wiki-lint/references/lint-checks.md (L06 at lines 51-54)
- Acceptance:
  - RED: L06 entry has no mention of L15 / near-duplicate.
  - GREEN: L06 entry includes the "check L15 first" cross-reference sentence.
- Dependencies: Task 3 completes first
- Independent: false  # shares lint-checks.md with Task 3
- Brief item covered: "L06「orphan→cross-linker」… 加交叉提示"

## Task 6 — wiki-merge SKILL.md skeleton
- Description: Create new skill wiki-merge: SKILL.md frontmatter (name: wiki-merge; description with zh-TW/ja/en triggers 「合併重複頁」「merge duplicate pages」「重複ページ統合」 + disambiguation: user-triggered after wiki-ingest/wiki-lint flags a near-dup; NOT wiki-ingest (add) / NOT cross-linker (link)); overview; pre-condition block (wiki/ exists; takes a candidate page pair as input).
- Module: obsidian/skills/wiki-merge
- Files touched: obsidian/skills/wiki-merge/SKILL.md
- Context paths:
  - obsidian/skills/wiki-ingest/SKILL.md (frontmatter + pre-condition style)
  - docs/obsidian/specs/2026-06-01-wiki-near-duplicate-detection-merge.md
- Acceptance:
  - RED: `test -f obsidian/skills/wiki-merge/SKILL.md` → absent.
  - GREEN: valid frontmatter (name/description + triggers + disambiguation) + overview + pre-condition (candidate pair input).
- Dependencies: none
- Independent: true
- Brief item covered: "wiki-merge(新 skill,寫入)… 人觸發後 LLM 自動執行"

## Task 7 — wiki-merge LLM auto-execute procedure
- Description: Add the auto-merge procedure to wiki-merge/SKILL.md: Step A LLM re-confirms the pair is the same entity (abort if not); Step B pick canonical (more inbound links / higher sources_count / older); Step C LLM drafts consolidated content (`## Summary` fuller wins, `## Key Facts` union, `## Sources` union, `sources_count` max); Step D apply to canonical page. This is LLM-automatic (no manual labor) once the user has triggered.
- Module: obsidian/skills/wiki-merge
- Files touched: obsidian/skills/wiki-merge/SKILL.md
- Context paths:
  - obsidian/skills/wiki-ingest/references/page-format.md (section + frontmatter inventory)
  - obsidian/skills/wiki-ingest/references/near-duplicate-detection.md (same-entity judge)
- Acceptance:
  - RED: `grep -i 'consolidat\|canonical' obsidian/skills/wiki-merge/SKILL.md` → absent (no procedure yet).
  - GREEN: Steps A–D present; LLM re-confirm + canonical-pick + LLM-draft union + apply.
- Dependencies: Task 6 completes first
- Independent: false  # same file as Task 6
- Brief item covered: "LLM 自動執行 … LLM 再確認同一實體 → 起草整合 Summary/Key Facts → 套用"

## Task 8 — wiki-merge safety invariants (reversible auto-merge)
- Description: Add to wiki-merge/SKILL.md the safety invariants that make auto-execution safe: `## User Notes` always union-preserved; self-verify after draft (LLM checks no facts lost / no contradiction silently dropped → if fail, abort + flag to user); archive absorbed page to `wiki/_archive/<date>/` (reversible, never hard-delete); absorbed slug → canonical `aliases:`; repoint inbound wikilinks + note to re-run /wiki-cross-linker; idempotent (no-op if already merged); append `wiki/log.md`; NEVER/ALWAYS block (NEVER hard-delete / NEVER drop User Notes / NEVER merge on failed self-verify; ALWAYS archive + log). Scope = the triggered pair only (single responsibility); a third duplicate is left to the existing detection homes (ingest prevent-new / lint sweep-old) — NO transitive cascade inside one merge.
- Module: obsidian/skills/wiki-merge
- Files touched: obsidian/skills/wiki-merge/SKILL.md
- Context paths:
  - obsidian/skills/wiki-ingest/references/delta-tracking.md (manifest wiki_pages, audit-trail precedent)
  - obsidian/skills/wiki-cross-linker/SKILL.md (re-run note)
- Acceptance:
  - RED: `grep -E '_archive|self-verify|User Notes|NEVER' obsidian/skills/wiki-merge/SKILL.md` → absent.
  - GREEN: User-Notes-union + self-verify + archive + slug→aliases + wikilink repoint + idempotent + log + NEVER/ALWAYS all present; NO transitive-cascade logic (single-pair scope stated).
- Dependencies: Task 7 completes first
- Independent: false  # same file as Tasks 6, 7
- Brief item covered: "安全閘 … User Notes 永遠聯集 … archive 不 hard-delete(可逆)… self-verify … 寫 log"

## Task 9 — version bump + CHANGELOG + README
- Description: Bump obsidian plugin.json minor version; add CHANGELOG entry (near-dup detection in wiki-ingest + wiki-lint L15 + new wiki-merge skill); update README.md (+ README.zh-TW.md, README.ja.md) skills table — add wiki-merge row, note wiki-ingest near-dup prompt, fix stale wiki-lint "11-check"→"15-check"; add wiki-merge to the README directory tree.
- Module: obsidian (plugin root)
- Files touched: obsidian/.claude-plugin/plugin.json, obsidian/CHANGELOG.md, obsidian/README.md, obsidian/README.zh-TW.md, obsidian/README.ja.md
- Context paths:
  - obsidian/.claude-plugin/plugin.json
  - obsidian/CHANGELOG.md
  - obsidian/README.md (lines 83-86, 191-194)
- Acceptance:
  - RED: CHANGELOG has no near-dup/wiki-merge entry; README says "11-check"; no wiki-merge row.
  - GREEN: version bumped; CHANGELOG entry present; README skills table lists wiki-merge + "15-check" + ingest near-dup note; tree updated.
- Dependencies: Tasks 2, 4, 5, 8 complete first
- Independent: false
- Brief item covered: Decision section (whole-change shipping: detection two homes + wiki-merge)

## Notes
- All tasks prose/markdown; "RED test" = grep/Read diagnostic (wiki-ingest/wiki-lint/wiki-merge are LLM-executed prose skills; only wiki-query has pytest).
- Skill-folder hook: wiki-merge/ single-level — compliant.
- Independent:true set = {T1, T2, T3, T4, T6}; files pairwise disjoint (near-duplicate-detection.md / ingest SKILL.md / lint-checks.md / lint SKILL.md / merge SKILL.md). T5/T7/T8 are false (same-file sequential chains). Check 14 satisfied.
- Cross-skill method duplication (T1 reference vs T3 inline) is intentional per repo skill-independence convention; keep consistent if either changes.
- Post-PASS amendment (2026-06-01): removed "transitive iterate" from T8 per complexity-critique (gold-plating from batch-KG systems; single-pair scope is correct). Removal-only, schema/DAG/required-fields unchanged — re-review skipped per writing-plans §Amending a PASS plan.
