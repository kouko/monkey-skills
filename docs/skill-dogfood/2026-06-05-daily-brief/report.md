# Dogfood report — `daily-brief` (v0.2.0 regression / Task 14)

> Behavioral regression dogfood of the WORKING-TREE daily-brief after the
> v0.2.0 hardening (G1–G4 + dogfood fixes H1/M1/M2/L2). Findings are
> ADVISORY. Gate for the release tasks (T15/T16): **no new Critical/High vs
> the 2026-06-04 baseline**.

## Metadata

| Field | Value |
|---|---|
| Skill path | `briefing-toolkit/skills/daily-brief/` (branch `daily-brief-playbook-hardening`) |
| Skill version | `0.1.0` at test time → bumping to `0.2.0` (T16, gated on this report) |
| Date | 2026-06-05 |
| Passes run | activation (Probe A) · executor+2 blind auditors (Probe B) · cold-reader (Probe C) |
| Model pinned | subagents: `claude-sonnet-4-6`; activation harness: `claude` CLI 2.1.163 |
| Activation fidelity | **approximate** — real-harness blocked in nested env (same as 06-04 I1); triggering description untouched this branch → no re-eval needed |

## Severity summary

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 2 (FINDING-001 fixed this run; FINDING-002 advisory) |
| **Total** | 2 |

**Regression gate: PASS.** The 06-04 baseline had **High ×1 (H1)** + **Medium ×2 (M1, M2)** + **Low ×2 (L1, L2)**. This run confirms **all of H1/M1/M2/L1/L2 fixed and holding**, and the four new behaviors **G1–G4 execute correctly end-to-end**. No new Critical/High introduced. The only new items are two Low nits, one already fixed in-run.

---

## Positive validation (the v0.2.0 changes, behaviorally confirmed)

Probe B executor ran triage → continuity-diff → output on a fixture engineered to force each new behavior (5-ready Gate, Asana 1→17 count swing with dated items, Notion as-of cache, Drive placeholder link, GH merged, an explicit prior-brief generation time). Both blind auditors judged the produced artifacts with no knowledge of how they were made.

| Change | Expected behavior | Executor result | Auditor confirmation |
|---|---|---|---|
| **G1** 5th-state | item date ≥ prior-brief-time → 🆕 真新發生; < → ⚠️ 昨日未涵蓋 | ASANA-3001 (06-05 08:00) → 🆕 真新發生; ASANA-2001–2015 (May) → ⚠️ 昨日未涵蓋 | both auditors: continuity states correct, genuinely-new vs missed-yesterday distinguished |
| **G2** as-of degrade | cached re-verify → 推論 + caveat | NOTION-pageA (as-of 2026-06-04T18:00) → 🔄 **推論** + "重驗資料非即時 (as-of …)" | auditor #2: "no cached item presented as confirmed live fact" |
| **G3** zero-fold | stale backlog one-row-per-item in MD+CSV | 15 stale items each its own row; CSV 22 rows, every unique_id populated | both auditors: complete table fully expanded, MD↔CSV parity 22=22 |
| **G4** counts+swing | per-platform counts + swing flag | coverage line `Gmail(2)/Notion(1)/Asana(17)/Drive(1)/GitHub(1)`; "⚠️ Asana 17 vs 昨日 1" note | auditor #1: counts + swing surfaced, not hidden |
| **H1** ready-only dispatch | dispatch only ✅ platforms | dispatched **5** (not 7); Slack/Calendar → blind spots | trajectory Q6 |
| **M1** placeholder link | non-URL token → ⚠️無直連 | Drive `htmlLink` token → `⚠️無直連`, unique_id kept | auditor #1 D1 PASS, auditor #2 check-3 PASS |
| **M2** PDB | expanded on first prose use | (doc-level; cold-reader confirmed expansion present) | — |
| **L2** jargon | 高槓桿決策 defined, source_book gone | cold-reader did NOT flag either as undefined | Probe C Q7 |

---

## Findings

### FINDING-001: continuity state-count label lagged the new 5th state — FIXED in-run

- **Severity**: Low
- **Category**: Cold-start / Convention-violation
- **Pass**: blind (cold-reader) + corroborated by Wave-2 spec/quality review and both auditors' adjacent notes
- **Probe prompt**: Probe C Q3 — "how many distinct continuity states are there… is the relationship between the four-state table and any additional state(s) clear?"
- **Expected**: a first-time reader can tell the section enumerates a 4-base + 1-refinement structure without being misled by the heading.
- **Actual**: the `§5b` heading read "四狀態" while the body defined a fifth state (⚠️ 昨日未涵蓋); SKILL.md's workflow summary still carried the **pre-rename** label "🆕 新發生" (vs the reference's canonical "🆕 真新發生"). Cold-reader: *"The section is titled 四狀態 but contains five states… the heading actively mislabels it."*
- **Transcript evidence**: Probe C — *"The actual state count is five, not four. The heading of the overall section is called 四狀態, which is inconsistent with the body."*
- **Root cause**: T1 added the 5th state + relabeled 🆕→真新發生 in the reference, but the "四狀態" headings (§0 freedom-map, §5b heading), SKILL.md's workflow summary (old label), the SKILL.md reference description ("4 狀態"), and the brief-templates pointer were not in T1's scope and stayed stale.
- **Why static review missed it**: each occurrence is individually grammatical; the contradiction only appears when a reader cross-references the heading against the body's state list.
- **Location**: `SKILL.md:72`, `SKILL.md:97`, `references/prioritization-framework.md:18`, `:273`, `references/brief-templates.md:26`, `:148`.
- **Suggested fix direction**: acknowledge "+ 第五狀態" at every state-count reference; canonicalize 🆕 真新發生.
- **STATUS**: **FIXED this run** — commit `6f01da6` (6 edits across the 3 files; grep confirms 0 remaining "🆕 新發生", every "四狀態" reference now carries "+ 第五狀態" or the explicit 5-item list). The executor applied the 5-state logic correctly *despite* the stale heading (it read the reference body), so this was a clarity defect, not a logic defect.
- **Repro**: re-run Probe C, ask Q3; or `grep -rn "四狀態\|🆕 新發生" SKILL.md references/`.

### FINDING-002: curated brief's `自上次以來` backlog summary uses ambiguous range notation

- **Severity**: Low
- **Category**: Output-quality
- **Pass**: blind (both Probe B auditors)
- **Probe prompt**: Probe B — judge the produced 晨報.md against the zero-omission + dual-product contract.
- **Expected**: the curated brief may summarize a large backlog (it is the 狠取捨 product) provided the complete table stays zero-fold and JOIN keys are preserved.
- **Actual**: the brief's `📈 自上次以來` line reads `⚠️ 昨日未涵蓋（15 筆 Asana backlog 補收…）：ASANA-2001～2015。詳見完整事項表。` — the `2001～2015` range implies a contiguous block, but ASANA-2005 is broken out separately (a `中`-priority due-06-09 item), so the range is imprecise.
- **Transcript evidence**: auditor #1 — *"the range notation '～2015' implies continuity but 2005 breaks the narrative grouping… a labeling imprecision."* Auditor #2 logged the same as a Check-4 note, **mitigated by the explicit redirect** to the complete table.
- **Root cause**: the §4 zero-fold rule governs the **complete table** (which the executor correctly kept one-row-per-item, 22=22, all JOIN keys present); the brief's continuity section has no guidance on *how* to summarize a backlog cleanly when summarizing is permitted.
- **Why static review missed it**: the complete table passes every structural check (row count, unique IDs); the imprecision lives only in the curated narrative line.
- **Location**: `references/brief-templates.md` §3 (📈 自上次以來 template) — the curated-brief continuity render, NOT the complete-table rule.
- **Suggested fix direction** (advisory, NOT applied): optionally add one line to the §3 template — when summarizing a backlog in the brief, count + link to the complete table but avoid implying a contiguous ID range (e.g. "N 筆 backlog 補收，逐筆見完整表" without a `X～Y` range). **Not blocking**: this is intended dual-product curation; the complete table is zero-fold and continuity-safe (next-day JOIN intact). Logged as residue per the plan's T14 GREEN clause.
- **Repro**: re-run Probe B executor on `/tmp/dogfood-0605-fixture/`, inspect 晨報.md `📈` section.

---

## Non-findings (explicitly discounted)

- **"All underlying data is fabricated" (Probe B auditor #2, verdict SERIOUS-ISSUES)** — this is the **test fixture**, not skill behavior. The executor faithfully rendered the recorded fixture (`threadX`, `acme/app`, sequential Asana IDs) and invented nothing beyond it. The dogfood method treats the blind auditor's verdict as a draft; the human calibrator discounts a fixture-fidelity complaint. **Not a skill defect.**
- **`github.com/acme/app` not marked 無直連 while Drive was** (auditor #2 informational) — correct skill behavior: M1 flags **non-URL tokens**, not syntactically-valid-but-fake URLs. The GH link is a well-formed `https://` URL; the Drive value was the literal token `htmlLink`. The skill cannot (and should not) verify URL liveness. **Not a defect.**
- **Pre-existing jargon** (deferred tools / InputValidationError / AskUserQuestion / GID / 台帳 / fan-out / continuity-load·diff) flagged undefined by the cold-reader — all present in the 0.1.0 baseline, **out of scope** for this branch (not part of G1–G4 or H1/M1/M2/L2). Carry-forward note, not a regression.
- **Probe A real-harness "did not fire"** — nested-harness fidelity failure (the obvious should-fire query also returned no-fire), identical to baseline I1; not a trigger-miss. Triggering description untouched this branch.

---

## Raw outputs appendix

### A. Activation runs (Probe A)

| # | Query | should_fire | Run 1 | Verdict |
|---|---|---|---|---|
| 1 | `daily brief please 幫我做今天的晨報` | true | did not fire | harness-blocked (not FN) |
| 2 | `幫我做這一季的績效自評盤點` | false | did not fire | TN (vacuous — harness blocked) |

Real-harness blocked in nested env (obvious-fire also no-fired → fidelity failure, not skill behavior). Description byte-identical to the 0.1.0 baseline that scored TPR≈1.0 / TNR≈1.0 via the approximate fallback; no re-eval warranted.

### B. Cold-reader audit (Probe C) — key verbatim

- Q3 (continuity states): *"The actual state count is five, not four… the section title 四狀態 is a misnomer."* → FINDING-001 (now fixed).
- Q5 (zero-fold): *"If you had 40 stale backlog items… list all 40 as individual rows… no exception for age, staleness, or volume."* → G3 understood correctly.
- Q6 (as-of): *"信心只能掛『推論』… caveat 標『重驗資料非即時 (as-of X)』… rule is clear."* → G2 understood.
- Q7 (jargon): 高槓桿決策 and source_book **not** in the undefined-terms list → L2 fix holds.

### C. Executor artifacts (Probe B) — excerpts

晨報.md coverage + continuity (verbatim head):
```
> ✅ 已涵蓋：Gmail✅(2 筆) / Notion✅(1 筆) / Asana✅(17 筆) / Google Drive✅(1 筆) / GitHub✅(1 筆)
> ⚠️ 受阻：Slack — 連上但被 AI-eligibility 標籤封鎖
> ❌ 未連：Google Calendar — MCP 未連線
> ⚠️ Asana 收集量大幅變動：今日 17 筆 vs 昨日 1 筆（方法改為 modified_at 篩選）。🆕 可能含昨日漏收。
...
- 🔄 狀態變化（推論）：NOTION-pageA … （快取 as-of 2026-06-04T18:00+08:00，非即時；實際狀態需自行確認）
- 🆕 真新發生：ASANA-3001 … （今日 08:00 建立）
- ⚠️ 昨日未涵蓋（15 筆 Asana backlog 補收，建立日均早於 2026-06-04 09:00）：ASANA-2001～2015。詳見完整事項表。
```
完整事項.csv: 1 header + 22 data rows, zero-fold; DRIVE-fileZ link cell = `⚠️無直連` (unique_id `DRIVE-fileZ` kept); NOTION-pageA 信心 = `推論`; ASANA-2001–2015 each its own row.

### D. Executor trajectory (Probe B) — summary
Per-item states: ASANA-1001 ⏳(3d); GH-PR-482 ✅(merged); NOTION-pageA 🔄/推論; GMAIL-threadX ⏳(2d). 17 Asana = 1 carried (1001) + 1 🆕 真新發生 (3001, 06-05 ≥ 06-04 09:00) + 15 ⚠️ 昨日未涵蓋 (May/early-June < 06-04 09:00). Dispatch = 5 ready agents. (Executor crashed once on a transient socket error; the re-run completed cleanly — infra, not skill.)

### E. Auditor judgments (Probe B) — draft verdicts
- Auditor #1 (domain-expert): **PASS_WITH_MINOR** — 8/8 contract dimensions PASS; 1 Low nit (FINDING-002 range notation) + a suggestion to self-declare the complete-table row count.
- Auditor #2 (data-integrity): MD↔CSV parity ✅, unique-IDs ✅, link integrity ✅, stale-data honesty ✅, continuity correctness ✅, coverage ✅; "SERIOUS" verdict driven solely by **fixture** fabrication (discounted, see Non-findings) + the FINDING-002 brief summary.

## Verdict

**No new Critical/High vs the 06-04 baseline → regression gate PASS.** H1/M1/M2/L1/L2 fixed and holding; G1–G4 behaviorally confirmed end-to-end by an informed executor + two blind auditors. One Low labeling residue (FINDING-001) was fixed in-run (`6f01da6`); one Low advisory (FINDING-002) is logged, non-blocking. Release tasks T15 (CHANGELOG) and T16 (version bump 0.1.0→0.2.0) are cleared to proceed.
