# Dogfood Report — daily-brief (modified)

- **Skill-under-test**: `briefing-toolkit/skills/daily-brief/` (working tree, branch `daily-brief-playbook-hardening`, commit 53ebce8)
- **Date**: 2026-06-04
- **Focus**: behavioral test of the MODIFIED version (5-cell template, Worked Examples, shared Sanity-check, live-discovery rule, window-edge, thread-degrade, supplementary signals)
- **Probes**: A (activation), B (executor + blind auditor), C (cold-reader)

## Severity summary

| Severity | Count | Findings |
|---|---|---|
| Critical | 0 | — |
| High | 1 | H1 playbook §1 hardcodes "7 個 Agent" vs ready-only Gate |
| Medium | 2 | M1 placeholder link presented as clickable (無直連 check gap); M2 "PDB" undefined |
| Low | 2 | L1 focus "卡住別人" over-claimable w/o today-evidence; L2 jargon leak (高槓桿決策 / source_book) |
| Info | 1 | I1 Probe A real-harness blocked → triggering validated via approximate fallback only |

**Positive validation**: every MODIFIED section (Worked Examples, Sanity-check, live-discovery總則, 窗緣, thread-降級, supplementary signals) was judged clear + executable by the cold-reader, correctly applied by the executor, and confirmed by the blind auditor. The edits pass the behavioral dogfood.

---

## Probe A — Activation

**Real-harness: BLOCKED (Info I1).** `claude -p --output-format stream-json` in the nested environment produced an empty/unparseable stream — every query returned NO-FIRE, including unambiguous ones ("daily brief please", "幫我做今天的晨報"). All-zero-including-obvious-fire = harness fidelity failure, NOT a skill trigger-miss (per this skill's own floor-not-ceiling rule; meta-note: the failure pattern is exactly what the daily-brief Sanity-check we just added is designed to catch — "active source returns 0 → suspect the harness"). Diagnostic confirmed: no `system`/`assistant` events emitted.

**Fallback (synthetic menu, `fidelity:approximate`):** distractor set = performance-evidence-audit / obsidian-daily / handoff / gws-gmail-send / recap-state.
- should-fire → daily-brief: **6/6** (TPR ≈ 1.0)
- should-NOT wrongly → daily-brief: **0/5** (TNR ≈ 1.0)
- At-risk near-miss to watch: SN5 "我這週有哪些待回覆的訊息漏掉了(過去一週回顧)" — shares 待回覆 trigger but is past-axis; routed correctly to performance-evidence-audit. The time-axis boundary is the thinnest line (cold-reader independently flagged the same).

> Triggering not changed by this branch (description untouched), so approximate confidence is acceptable; re-run real-harness in a non-nested shell for a definitive read.

---

## Probe B — Executor + blind auditor

Executor ran triage→continuity→output on a minimal real fixture (8 fan-out items incl. a GitHub↔Slack same-source echo, an overdue task, a window-edge item), forced first-run cold-start, wrote 3 artifacts to `/tmp/dogfood-brief-out/`. Blind auditor judged artifacts with no production context.

**Executor behavior (all correct):** dynamic focus by threshold not top-N (4 items, not padded); same-source echo (GitHub#88 + Slack bot repost) converged to ONE row, kept ⚠️ not inflated to ✅; window-edge 績效面談 06-19 included as "(窗緣)"; first-run → "首份簡報,無對照", no fabricated diff; CSV unique-id populated on all rows; MD/CSV parity 9=9.

**Auditor verdict: PASS overall**, 2 real defects:

### M1 — placeholder link presented as clickable [Medium · Output-quality/Gate · pass:informed]
- **Probe**: executor output rows 4 & 6 (Calendar) render `[↗](htmlLink)` — `htmlLink` is an unresolved token, not a URL; CSV 連結 field = literal `htmlLink`.
- **Expected**: contract says items without a usable deep-link must be marked "⚠️ 無直連", not shown as clickable.
- **Root cause**: the 無直連 rule + Sanity-check cover "0 results" and "no link", but nothing tells the agent "a returned link that is a placeholder/non-URL token must be treated as 無直連". (Partly fixture-induced — fixture used `<htmlLink>` placeholder — but a robust skill should catch a malformed link.)
- **Why static review missed it**: row counts and "has a link cell" both look PASS; only rendering the link reveals it's a token.
- **Location**: `references/brief-templates.md` (§無直連 rule) + `references/prioritization-framework.md` §共用 Sanity-check.
- **Suggested fix**: extend Sanity-check / 無直連 rule — "連結必須是 http(s) URL;若值是 placeholder/空/未解析 token → 標 ⚠️無直連".

### L1 — focus "會卡住別人" over-claimable without today-evidence [Low · Output-quality · pass:informed]
- **Probe**: focus ③ GitHub#88 (review-requested, open, **no deadline**) promoted to 今日焦點 on "別人下一步等我" with no evidence it blocks *today*.
- **Root cause**: §2 focus gate "會卡住別人" has no "today/now" qualifier → an open-ended review request can be promoted as focus (mild padding).
- **Location**: `references/prioritization-framework.md` §2 動態焦點門檻.
- **Suggested fix**: qualify "卡住別人" → require evidence it blocks someone *now/today* (explicit ask / deadline); otherwise route to 進行中專案, not 焦點.

---

## Probe C — Cold-reader (zero-context)

### H1 — playbook §1 hardcodes "一次發出 7 個 Agent" vs ready-only Gate [High · Convention/Contradiction · pass:informed]
- **Probe**: §1 repeatedly says "一次發出 **7** 個 Agent 呼叫並行"; three lines later "只有 ✅就緒 的平台才發 agent。⚠️受阻/❌未連 的平台不發 agent". A literal reader dispatches 7 even when Gate passed only 5.
- **Why static review missed it**: both statements are individually correct; the conflict only appears when executing.
- **Location**: `references/platform-search-playbook.md` §1.
- **Suggested fix**: replace "一次發出 7 個 Agent" → "一次發出**全部 ✅就緒平台**的 Agent(最多 7,可更少)".

### M2 — "PDB" never expanded [Medium · Jargon-leak · pass:informed]
- Load-bearing acronym ("PDB 風格 6 段", tag `pdb`) never spelled out; the President's Daily Brief link is implicit only.
- **Location**: `SKILL.md` + `references/brief-templates.md` (first use).
- **Suggested fix**: "PDB(President's Daily Brief)" on first use.

### L2 — dev-internal concepts leak into user-facing text [Low · Jargon-leak · pass:informed]
- "高槓桿決策" used as a focus gate but never defined/exemplified; "source skill" / "source_book" (development concept) appears in reference prose.
- **Suggested fix**: one-line define 高槓桿決策 with an example; drop "source skill/source_book" from user-facing reference.

### Positive (cold-reader, on the MODIFIED content)
- Worked Examples: "clear and copyable", "照抄這個形狀" unambiguous; nit — Drive example uses `<file-id>`/`<htmlLink>` placeholders (relates to M1).
- 共用 Sanity-check: "executable as written", clear WHY.
- live-探索 總則: "the clearest meta-rule in the docs"; precedence over negative notes understood.
- 窗緣 + thread-降級: both "clear and operational", cross-referenced consistently.

### Note (downgraded)
Cold-reader flagged "not self-contained — output step needs brief-templates.md". This is partly a probe artifact (that file was not in the cold-reader's reading set); it IS bundled. Real residue: SKILL.md alone doesn't restate the output contract — acceptable progressive disclosure, but the 狠取捨 vs 零省略 resolution lives only in the reference, so a SKILL.md-only reader could misexecute. Minor.

---

## Raw outputs (appendix)
- Probe A real-harness: `probeA-results.txt` (all NO-FIRE — harness-blocked, not a finding).
- Probe A fallback: SF 6/6 → daily-brief; SN 0/5 misrouted.
- Probe B artifacts: `/tmp/dogfood-brief-out/2026-06-10_{晨報.md,完整事項.md,完整事項.csv}`.
- Probe B auditor: PASS overall; defects M1, L1.
- Probe C: cold-reader transcript (findings H1, M1-nit, M2, L2 + positive validation).

## Verdict
No Critical/blocking defects. The **modifications themselves are sound and behaviorally validated**. The findings are mostly **pre-existing** issues the dogfood surfaced (H1 the "7" contradiction is the one worth fixing now) plus one **new-adjacent gap** (M1 malformed-link handling — a natural extension of the Sanity-check we added). Floor-not-ceiling: NO pass stamped for Probe A (real-harness was blocked; only approximate triggering data exists).
