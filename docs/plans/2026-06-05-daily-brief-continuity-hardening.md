# Plan: daily-brief continuity & zero-omission hardening (v0.2.0)

Source brief: embedded below (discovery was interactive — day-2 dogfood run on installed 0.1.0 + alignment with user). Corroborating artifact: `docs/skill-dogfood/2026-06-04-daily-brief/report.md`.
Target repo: monkey-skills (repo root), branch `daily-brief-playbook-hardening`.
Touch surface: markdown only — `briefing-toolkit/skills/daily-brief/{SKILL.md, references/*.md}`, `briefing-toolkit/CHANGELOG.md`, `briefing-toolkit/.claude-plugin/plugin.json`. **No code.**
Total tasks: 19 (uncapped; width OK) — T13 split into 13a–13d per Check-4 (one module/task)
Critical-path depth: 4 (≤5) — content edits (≤2) → regression (3) → release fan-out (4)
Execution order: parallel-where-possible (across files); same-file tasks serialize at dispatch but carry no semantic dependency
Plan-document-reviewer verdict: PASS (2026-06-05, round 2 / 14 checks; round 1 NEEDS_REVISION on Check 4 / Task 13, fixed by per-file split)
Regression gate: `dev-workflow:dogfood-skill-testing` must show no new Critical/High before release tasks run.

---

## Embedded brief

**Problem.** Running daily-brief a 2nd day (against installed **0.1.0**, not the hardened dev branch) surfaced gaps that survive even the dev branch's hardening:
- The continuity diff cannot tell a *genuinely new event* from an *item yesterday's fan-out missed* — both look like "today has an ID yesterday's CSV lacks" → both get `🆕`. The dev branch's new Asana `modified_at` fallback makes this worse short-term (collection methodology changed between days → a flood of old items appear as `🆕`).
- "Live re-verify" (a §5 hard rule) was silently defeated when the Notion API returned an `as-of`-cached snapshot — no degradation path exists (unlike Slack thread-read failure, which already has one).
- The zero-omission complete table has no sanctioned behavior for a large stale backlog; consolidating (what the operator did on day 2) drops JOIN keys and breaks next-day continuity for those items.
- Collection-volume swings (Asana 1→42 between days) are completely invisible — the coverage statement only records ✅/⚠️/❌, not counts.

Plus 4 pre-existing dogfood findings (06-04 report) still unshipped: H1, M1, M2, L2.

**Smallest end state.** The four gaps (G1–G4) closed in the reference docs + the four dogfood findings (H1/M1/M2/L2) fixed, regression-checked via dogfood, CHANGELOG updated, version bumped 0.1.0 → 0.2.0.

**Decisions (aligned with user).**
- G3: complete table is **strictly zero-fold in BOTH MD and CSV** — one item = one row, never grouped / footnote-summarized; every JOIN key preserved. Operator's day-2 consolidation is the anti-pattern to codify against.
- G1: 5th-state discrimination keyed on item created/due/event date vs prior-brief generation time.
- G4 is G1's enabler (makes collection swings visible).
- Markdown-only; no code; dogfood is the regression harness.

**Out of scope.** Any code/MCP changes; the already-shipped dev-branch hardening (✅-rarity expectation, focus "today-evidence" qualifier, Asana `modified_at`, Drive `viewedByMeTime`, Slack `after:` unreliability, GitHub global-search, thread-read degradation, window-edge items) — confirmed present, not re-touched. Scheduling/delivery layer. Triggering description (untouched → no activation re-eval needed).

---

## Task 1 — G1: 5th-state discrimination in continuity-diff
- Description: In `prioritization-framework.md` §5b, after the 4-state table add a discrimination rule: when an item is "today-present, absent from yesterday's CSV", branch on the item's own created/due/event date vs the prior-brief generation timestamp — `≥ prior brief time → 🆕 真新發生`; `< prior brief time → ⚠️ 昨日未涵蓋 (疑似漏收/方法變更)`, NOT 🆕. Add a WHY tying it to "my blind spot ≠ a new world event".
- Module: `briefing-toolkit/skills/daily-brief/references/prioritization-framework.md`
- Files touched: briefing-toolkit/skills/daily-brief/references/prioritization-framework.md
- Context paths:
  - briefing-toolkit/skills/daily-brief/references/prioritization-framework.md (§5b four-state table)
- Acceptance:
  - RED: grep of §5b returns no `昨日未涵蓋` / no 5th-state branch (current state).
  - GREEN: §5b contains the date-vs-prior-brief-time branch and the `⚠️ 昨日未涵蓋` state with a WHY; a cold-reader can decide 🆕 vs 昨日未涵蓋 for a 40-item Asana swing.
- Dependencies: none (corroborates T4's swing flag but does not require it — cross-ref only)
- Independent: false  # same file as T4/T5/T12; not parallel-dispatchable
- Brief item covered: "G1 … 把『真🆕新發生』與『⚠️昨日未涵蓋』分開"

## Task 2 — G1: render the new state in the brief template
- Description: In `brief-templates.md` §3 (📈 自上次以來 template), add a render line for `⚠️ 昨日未涵蓋` so the 📈 section presents it distinctly from `🆕`, mirroring T1's logic exactly (same label, same meaning).
- Module: `briefing-toolkit/skills/daily-brief/references/brief-templates.md`
- Files touched: briefing-toolkit/skills/daily-brief/references/brief-templates.md
- Context paths:
  - briefing-toolkit/skills/daily-brief/references/brief-templates.md (§3 📈 template block)
  - briefing-toolkit/skills/daily-brief/references/prioritization-framework.md (§5b — must match T1 label)
- Acceptance:
  - RED: §3 template has only 🆕/⏳/✅/🔄 lines, no 昨日未涵蓋.
  - GREEN: §3 template includes a `⚠️ 昨日未涵蓋` example line consistent with T1's wording.
- Dependencies: Task 1 completes first (doc-mirrors-doc: render must match the §5b label)
- Independent: false
- Brief item covered: "G1 … 把『真🆕新發生』與『⚠️昨日未涵蓋』分開"

## Task 3 — G4: per-platform counts in coverage statement
- Description: In `brief-templates.md` §2 (資料源涵蓋聲明), extend the ✅/⚠️/❌ block to record per-platform returned item counts (e.g. `Asana ✅(42 筆)`). Update the §2 template and the example.
- Module: `briefing-toolkit/skills/daily-brief/references/brief-templates.md`
- Files touched: briefing-toolkit/skills/daily-brief/references/brief-templates.md
- Context paths:
  - briefing-toolkit/skills/daily-brief/references/brief-templates.md (§2 coverage block)
- Acceptance:
  - RED: §2 coverage block has no per-platform count field.
  - GREEN: §2 template + example show per-platform counts.
- Dependencies: none
- Independent: false  # same file as T2/T7/T8/T11
- Brief item covered: "G4 … 附每平台本次回傳筆數"

## Task 4 — G4: continuity-load count comparison + swing flag
- Description: In `prioritization-framework.md` §5a (continuity-load), add a step: compare each platform's today-count to yesterday's CSV-derived count; on a material swing, emit a brief-level note ("X 收集量較昨日大幅變動,🆕 可能含昨日漏收") that feeds T1's discrimination. Define "material swing" qualitatively (order-of-magnitude / >Nx), not a hardcoded number.
- Module: `briefing-toolkit/skills/daily-brief/references/prioritization-framework.md`
- Files touched: briefing-toolkit/skills/daily-brief/references/prioritization-framework.md
- Context paths:
  - briefing-toolkit/skills/daily-brief/references/prioritization-framework.md (§5a continuity-load)
  - briefing-toolkit/skills/daily-brief/references/brief-templates.md (§2 — count field defined by T3)
- Acceptance:
  - RED: §5a has no count-comparison / swing-flag step.
  - GREEN: §5a instructs count comparison + swing note; references the §2 count field.
- Dependencies: Task 3 completes first (cross-file semantic dep: consumes the §2 count field)
- Independent: false
- Brief item covered: "G4 … 對照昨日筆數,某平台筆數劇變就在簡報標"

## Task 5 — G2: stale/cached re-verify degradation rule
- Description: In `prioritization-framework.md` §5 hard-rule (live re-verify), add a degradation clause mirroring §3's thread-read-failure rule: if re-verify data carries an `as-of`/cache timestamp earlier than today, the item's continuity confidence drops to `推論` and a caveat "重驗資料非即時 (as-of X)" is required. Add WHY (a defeated live-check is a blind spot, not fact).
- Module: `briefing-toolkit/skills/daily-brief/references/prioritization-framework.md`
- Files touched: briefing-toolkit/skills/daily-brief/references/prioritization-framework.md
- Context paths:
  - briefing-toolkit/skills/daily-brief/references/prioritization-framework.md (§5 hard rule, §3 degradation analog)
- Acceptance:
  - RED: §5 has no stale/cached degradation path.
  - GREEN: §5 contains the as-of degradation clause → 推論 + required caveat.
- Dependencies: none
- Independent: false  # same file
- Brief item covered: "G2 … live 重驗讀到陳舊/快取資料時降為推論並標 caveat"

## Task 6 — G2: Notion fetch must check returned timestamp
- Description: In `platform-search-playbook.md` §4.3 (Notion), add a knowhow bullet: `notion-fetch` may return a cached/as-of snapshot; the agent must check the returned last-edited/as-of timestamp and, if it predates today during a continuity re-verify, flag per §5 (T5). Cross-reference §5.
- Module: `briefing-toolkit/skills/daily-brief/references/platform-search-playbook.md`
- Files touched: briefing-toolkit/skills/daily-brief/references/platform-search-playbook.md
- Context paths:
  - briefing-toolkit/skills/daily-brief/references/platform-search-playbook.md (§4.3 Notion knowhow)
- Acceptance:
  - RED: §4.3 has no fetch-timestamp / cache-staleness bullet.
  - GREEN: §4.3 instructs checking the fetch timestamp + cross-refs the §5 degradation rule.
- Dependencies: none (cross-refs T5 but is independently readable)
- Independent: false  # same file as T9
- Brief item covered: "G2 … Notion fetch 要檢查回傳時間戳"

## Task 7 — G3: strict zero-fold rule + anti-pattern
- Description: In `brief-templates.md` §4 (完整表) and §5 (CSV), state the hard rule: the complete table is **strictly one-row-per-item in BOTH MD and CSV — never grouped, never footnote-summarized, every JOIN key preserved**. Add an anti-pattern entry "群組陳舊 backlog 為摘要列 → 丟失 JOIN key、斷延續鏈" with the day-2 consolidation as the example. Clarify the dual-product split (brief = curated/狠取捨; complete table = zero-omission safety net).
- Module: `briefing-toolkit/skills/daily-brief/references/brief-templates.md`
- Files touched: briefing-toolkit/skills/daily-brief/references/brief-templates.md
- Context paths:
  - briefing-toolkit/skills/daily-brief/references/brief-templates.md (§4 complete-table, §5 CSV)
- Acceptance:
  - RED: §4/§5 do not forbid grouping/folding; no anti-pattern entry.
  - GREEN: §4/§5 contain the strict zero-fold rule (MD + CSV) and the grouping anti-pattern.
- Dependencies: none
- Independent: false  # same file
- Brief item covered: "G3 … 完整表 MD 與 CSV 都嚴格零折疊 … 群組陳舊 backlog 寫成反模式"

## Task 8 — M1: placeholder / non-URL link → ⚠️無直連
- Description: In `brief-templates.md` (§無直連 rule), extend it: a returned link value that is not an `http(s)` URL (placeholder / unresolved token / empty) must be treated as `⚠️無直連`, not rendered clickable. Mirror into the shared Sanity-check reference if cross-linked.
- Module: `briefing-toolkit/skills/daily-brief/references/brief-templates.md`
- Files touched: briefing-toolkit/skills/daily-brief/references/brief-templates.md
- Context paths:
  - briefing-toolkit/skills/daily-brief/references/brief-templates.md (§無直連 rule)
  - docs/skill-dogfood/2026-06-04-daily-brief/report.md (M1)
- Acceptance:
  - RED: §無直連 only covers "no link", not "malformed/placeholder link".
  - GREEN: §無直連 requires non-`http(s)` values be marked ⚠️無直連.
- Dependencies: none
- Independent: false  # same file
- Brief item covered: "dogfood … M1(非 URL/placeholder 連結要標⚠️無直連)"

## Task 9 — H1: fix "發 7 個 Agent" vs ready-only Gate contradiction
- Description: In `platform-search-playbook.md` §1, replace every "一次發出 7 個 Agent" phrasing with "一次發出**全部 ✅就緒平台**的 Agent(最多 7,可更少)" so the dispatch count never contradicts the Gate result.
- Module: `briefing-toolkit/skills/daily-brief/references/platform-search-playbook.md`
- Files touched: briefing-toolkit/skills/daily-brief/references/platform-search-playbook.md
- Context paths:
  - briefing-toolkit/skills/daily-brief/references/platform-search-playbook.md (§1)
  - docs/skill-dogfood/2026-06-04-daily-brief/report.md (H1)
- Acceptance:
  - RED: §1 still hardcodes "7 個 Agent" unconditionally.
  - GREEN: §1 phrases dispatch as "全部 ✅就緒平台 (最多 7)"; no unconditional "發 7" remains.
- Dependencies: none
- Independent: false  # same file as T6
- Brief item covered: "dogfood … H1(『發 7 個 Agent』與 Gate 矛盾)"

## Task 10 — M2a: expand "PDB" in SKILL.md
- Description: In `SKILL.md`, on the first use of "PDB" write "PDB(President's Daily Brief)"; the `pdb` tag stays but the prose acronym is expanded once.
- Module: `briefing-toolkit/skills/daily-brief/SKILL.md`
- Files touched: briefing-toolkit/skills/daily-brief/SKILL.md
- Context paths:
  - briefing-toolkit/skills/daily-brief/SKILL.md (first "PDB" occurrence)
- Acceptance:
  - RED: "PDB" appears in SKILL.md prose without expansion.
  - GREEN: first prose use reads "PDB(President's Daily Brief)".
- Dependencies: none
- Independent: true
- Brief item covered: "dogfood … M2(PDB 首次出現展開)"

## Task 11 — M2b: expand "PDB" in brief-templates.md
- Description: In `brief-templates.md`, on the first use of "PDB" write "PDB(President's Daily Brief)".
- Module: `briefing-toolkit/skills/daily-brief/references/brief-templates.md`
- Files touched: briefing-toolkit/skills/daily-brief/references/brief-templates.md
- Context paths:
  - briefing-toolkit/skills/daily-brief/references/brief-templates.md (first "PDB" occurrence)
- Acceptance:
  - RED: "PDB" unexpanded in brief-templates.md.
  - GREEN: first prose use expanded.
- Dependencies: none
- Independent: false  # same file
- Brief item covered: "dogfood … M2(PDB 首次出現展開)"

## Task 12 — L2a: define 高槓桿決策 with an example
- Description: In `prioritization-framework.md` §2, add a one-line definition + concrete example of "高槓桿決策" at its first use as a focus gate.
- Module: `briefing-toolkit/skills/daily-brief/references/prioritization-framework.md`
- Files touched: briefing-toolkit/skills/daily-brief/references/prioritization-framework.md
- Context paths:
  - briefing-toolkit/skills/daily-brief/references/prioritization-framework.md (§2 focus gates)
- Acceptance:
  - RED: "高槓桿決策" used without definition.
  - GREEN: one-line definition + example present at first use.
- Dependencies: none
- Independent: false  # same file
- Brief item covered: "dogfood … L2(高槓桿決策一行定義+例)"

> **L2b jargon purge split per-file (Check-4 fix, round 1):** one task per file so each `Module` names exactly one path. Same per-file grep RED/GREEN. (T13a also closes the SKILL.md dispatch overlap with T10.)

## Task 13a — L2b: purge dev-internal jargon from SKILL.md
- Description: Remove/replace "source skill" / "source_book" and similar development-internal terms from user-facing prose in `SKILL.md`.
- Module: `briefing-toolkit/skills/daily-brief/SKILL.md`
- Files touched: briefing-toolkit/skills/daily-brief/SKILL.md
- Context paths:
  - docs/skill-dogfood/2026-06-04-daily-brief/report.md (L2)
- Acceptance:
  - RED: `grep -n "source_book\|source skill" briefing-toolkit/skills/daily-brief/SKILL.md` returns user-facing matches.
  - GREEN: same grep returns 0 user-facing matches.
- Dependencies: Task 10 completes first (shared file SKILL.md — serialize after the PDB edit)
- Independent: false
- Brief item covered: "dogfood … L2(移除 source skill/source_book 等開發術語)"

## Task 13b — L2b: purge dev-internal jargon from prioritization-framework.md
- Description: Remove/replace "source skill" / "source_book" and similar dev-internal terms from user-facing prose in `prioritization-framework.md`.
- Module: `briefing-toolkit/skills/daily-brief/references/prioritization-framework.md`
- Files touched: briefing-toolkit/skills/daily-brief/references/prioritization-framework.md
- Context paths:
  - docs/skill-dogfood/2026-06-04-daily-brief/report.md (L2)
- Acceptance:
  - RED: `grep -n "source_book\|source skill" .../prioritization-framework.md` returns user-facing matches.
  - GREEN: same grep returns 0 user-facing matches.
- Dependencies: none (same file as T1/T4/T5/T12 — serializes at dispatch, not a semantic dep)
- Independent: false
- Brief item covered: "dogfood … L2(移除 source skill/source_book 等開發術語)"

## Task 13c — L2b: purge dev-internal jargon from platform-search-playbook.md
- Description: Remove/replace "source skill" / "source_book" and similar dev-internal terms from user-facing prose in `platform-search-playbook.md`.
- Module: `briefing-toolkit/skills/daily-brief/references/platform-search-playbook.md`
- Files touched: briefing-toolkit/skills/daily-brief/references/platform-search-playbook.md
- Context paths:
  - docs/skill-dogfood/2026-06-04-daily-brief/report.md (L2)
- Acceptance:
  - RED: `grep -n "source_book\|source skill" .../platform-search-playbook.md` returns user-facing matches.
  - GREEN: same grep returns 0 user-facing matches.
- Dependencies: none (same file as T6/T9 — serializes at dispatch)
- Independent: false
- Brief item covered: "dogfood … L2(移除 source skill/source_book 等開發術語)"

## Task 13d — L2b: purge dev-internal jargon from brief-templates.md
- Description: Remove/replace "source skill" / "source_book" and similar dev-internal terms from user-facing prose in `brief-templates.md`.
- Module: `briefing-toolkit/skills/daily-brief/references/brief-templates.md`
- Files touched: briefing-toolkit/skills/daily-brief/references/brief-templates.md
- Context paths:
  - docs/skill-dogfood/2026-06-04-daily-brief/report.md (L2)
- Acceptance:
  - RED: `grep -n "source_book\|source skill" .../brief-templates.md` returns user-facing matches.
  - GREEN: same grep returns 0 user-facing matches.
- Dependencies: none (same file as T2/T3/T7/T8/T11 — serializes at dispatch)
- Independent: false
- Brief item covered: "dogfood … L2(移除 source skill/source_book 等開發術語)"

## Task 14 — Regression: dogfood-skill-testing run
- Description: Run `dev-workflow:dogfood-skill-testing` against the modified working-tree daily-brief (Probes A/B/C). Capture report under `docs/skill-dogfood/2026-06-05-daily-brief/`. Verify the new G1–G4 behaviors are executable + the H1/M1/M2/L2 fixes hold, with no new Critical/High.
- Module: regression (no skill-file edit)
- Files touched: docs/skill-dogfood/2026-06-05-daily-brief/report.md
- Context paths:
  - briefing-toolkit/skills/daily-brief/ (modified tree)
  - docs/skill-dogfood/2026-06-04-daily-brief/report.md (prior baseline)
- Acceptance:
  - RED: no 2026-06-05 dogfood report exists.
  - GREEN: report exists; no new Critical/High; G1–G4 + H1/M1/M2/L2 behaviorally confirmed (or any residue logged as a follow-up task).
- Dependencies: Tasks 1,2,3,4,5,6,7,8,9,10,11,12,13a,13b,13c,13d complete first
- Independent: false
- Brief item covered: "回歸測試用 dev-workflow:dogfood-skill-testing"

## Task 15 — Release: CHANGELOG 0.2.0 entry
- Description: Add a `## [0.2.0] — 2026-06-05` entry to `briefing-toolkit/CHANGELOG.md` documenting G1–G4 + H1/M1/M2/L2 under Added/Changed/Fixed.
- Module: `briefing-toolkit/CHANGELOG.md`
- Files touched: briefing-toolkit/CHANGELOG.md
- Context paths:
  - briefing-toolkit/CHANGELOG.md (existing 0.1.0 entry format)
- Acceptance:
  - RED: CHANGELOG top entry is 0.1.0.
  - GREEN: 0.2.0 entry present, lists the 8 changes.
- Dependencies: Task 14 completes first (don't document a release that failed regression)
- Independent: true  # disjoint file from Task 16
- Brief item covered: "更新 CHANGELOG"

## Task 16 — Release: version bump 0.1.0 → 0.2.0
- Description: Bump the version field in `briefing-toolkit/.claude-plugin/plugin.json` to 0.2.0.
- Module: `briefing-toolkit/.claude-plugin/plugin.json`
- Files touched: briefing-toolkit/.claude-plugin/plugin.json
- Context paths:
  - briefing-toolkit/.claude-plugin/plugin.json
- Acceptance:
  - RED: version is 0.1.0.
  - GREEN: version is 0.2.0.
- Dependencies: Task 14 completes first
- Independent: true  # disjoint file from Task 15
- Brief item covered: "bump 0.1.0→0.2.0"

---

## Notes

- **Depth computation**: critical-path depth counts only **semantic** `Dependencies` chains. Same-file tasks (e.g. the five brief-templates.md edits T2/T3/T7/T8/T11) are `Independent: false` to block parallel dispatch (edit-conflict avoidance) but most carry `Dependencies: none` — they serialize at dispatch without extending the dependency chain. Longest semantic chain: T3→T4→T14→T15/T16 = depth 4 (≤5).
- **Parallel-dispatch reality**: only T10 (SKILL.md), T15 (CHANGELOG), T16 (plugin.json) are truly `Independent: true` (disjoint files, no semantic dep). The three reference files each form a serialized within-file group; SDD dispatches one implementer per file-group sequentially, file-groups across each other in parallel.
- **TDD-iron-law mapping for prose**: "RED test" = a grep/cold-read assertion that the target rule is absent now; "GREEN" = rule present + behaviorally confirmed by the Task 14 dogfood probe. The dogfood run is the package-level verification (`verification-before-completion` analog) for a docs-only skill.
- **Already-shipped, do-not-touch**: dev-branch hardening enumerated in the brief's Out of scope — confirmed present in the working tree on 2026-06-05; this plan does not re-edit those sections.
- **Order**: G4(T3)→G1(T1,T2 + T4) → G2(T5,T6) → G3(T7) → dogfood-fixes(T8,T9,T10,T11,T12) → jargon-purge(T13a–13d, per file, after each file's content edits) → regression(T14) → release(T15,T16). Within a file, edits batch into one implementer pass.
- **T13 split (round-1 reviewer fix)**: the single multi-file jargon purge became per-file children 13a–13d so each `Module` is one path; 13a depends on T10 (shared SKILL.md), the rest serialize within their file group. Max semantic depth unchanged (4).
