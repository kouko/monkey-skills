# Dogfood report — daily-news-digest multi-viewpoint (多空對照/分歧點) behavior

- Date: 2026-07-08 (re-run: 2026-07-10, see §Re-run below)
- Target: `obsidian/skills/daily-news-digest/` @ branch feat/digest-multiview-synthesis (original run: commit 929bb294 — a pre-squash object, not reachable from any branch after the squash into baaf7fda; the re-run below anchors to 109b3866, on-branch)
- Scope: the NEW multi-view block behavior only (STEP 4 cluster-by-debate, STEP 6 block, digest-format §房規, arc-tracking 機構觀點). Probe A (activation harness) SKIPPED — the change does not touch the skill's `description`/triggering.
- Probes run: B (executor+cold-reader firewall, ×2 input classes: fire / over-fire), C (blind cold-reader).

## Severity summary

| Severity | Count | Categories |
|---|---|---|
| Critical | 0 | — |
| High | 0 | — |
| Medium | 2 | Output-quality / Cold-start |
| Low | 3 | Jargon-leak / Cold-start / Convention |

**Behavioral verdict: PASS on both dimensions** (fires on real debate; does NOT over-fire on complementary cluster). Findings below are clarity/robustness, not behavioral failures — both real executor runs navigated the ambiguity correctly.

## Behavioral results

- **B-1 Fire-when-expected** (2026-07-04 correction debate, 3 sources): PASS. One debate-cluster; 多空對照 table with mandatory 分歧點 row that flags "非五五對稱 / Grantham = 高調少數" (false-balance guard working); zero 漏引 (all 3 in Source Index); arc 機構觀點 觀點交鋒 rows with 立場 tags; book-routing rule applied (美股大盤 central).
- **B-2 Do-not-over-fire** (2026-07-04 Kaldellis Roman-history series, 3 complementary clips): PASS. NO 多空對照 block produced; correctly triaged to knowledge tier, rendered a prose 整合分析, and explicitly cited the "complementary angles = integration, not a debate → do NOT force a block" rule. The post-remediation "整合分析 stays prose unless a real debate" clause held.

## Findings

### F1 — Medium — Output-quality/Convention — the exactly-2 三行式 form has no worked example
- Location: `references/digest-format.md` §多空對照/分歧點 房規 (Form by stance count) + Output-template block.
- Probe C (blind cold-reader): "The `正方/反方/分歧點` three-row form is never shown. The template only draws the ≥3-stance table … given no example of what the 正方/反方 rows look like — do they still carry a 誰 column and 論據? I'd have to guess the column layout."
- Why static review missed it: the ≥3 table example exists and reads complete; the missing 2-row example is an absence, not a contradiction.
- Suggested fix: add a minimal `正方/反方/分歧點` worked example beside the ≥3 table (state whether it keeps 誰/論據 columns).

### F2 — Medium — Cold-start — the core "stance vs complementary angle" judgment has no worked positive+negative example pair
- Location: `references/digest-format.md` §Does a source count as a stance + `SKILL.md` STEP 6 point 2.
- Probe C: every genuine ambiguity "collapses to the single undefined judgment at the core — materially-differing stance vs complementary angle — which the spec labels a judgment call but gives no worked positive/negative example pair inside these sections." Two named borderline classes:
  1. **Same direction, different reason** — two bulls agreeing on the verdict but disagreeing on why: one 多 slot (integration) or two stances?
  2. **Implied lean from a different-facet source** — "supply is tightening" implicitly leans bullish; does an implied directional lean count as a stance, or only an explicit verdict? Overlaps the 中性 "flags fragility" definition.
- Why static review missed it: the rule is internally consistent; the gap is calibration (no example), invisible without a reader hitting a borderline input.
- Note: both executor runs resolved their (non-borderline) inputs correctly, so this is robustness for the ambiguous tail, not a live failure.
- Suggested fix: add a 2-line worked pair — one fires (opposing verdicts on one question), one does NOT (same-direction/different-reason OR different-facet lens → integration).

### F3 — Low — Jargon-leak — three names for one concept
- Location: `references/digest-format.md` (多空對照/分歧點 = spec; 市場分歧 = news-rendered header; 整合分析 = knowledge-rendered).
- Probe C + the earlier code-review both flagged: "can't immediately tell if these are three things or one thing wearing three labels." Suggested fix: one line mapping the three names (spec / news instance / knowledge instance).

### F4 — Low — Cold-start — `<stem>` undefined within these standalone sections
- Probe C: reading only these sections, "I would not know what a 'stem' is or how to obtain one" (it's the collector manifest `wikilink` field, defined elsewhere). In a full skill run the context is present; standalone it's opaque. Suggested fix: one-word pointer, or accept (defined in STEP 6.1 / Hard rules).

### F5 — Low — Convention — 論據 vs 核心論據 label drift; exactly-1-stance-after-filtering edge unstated
- Trivial: header says 核心論據, row spec says 論據. And if filtering drops the stance count below 2, no explicit "then no block" branch (inferable). Suggested fix: align the label; optionally one line for the <2 case.

## Raw outputs

Executor transcripts (fire / over-fire) and the cold-reader Q&A are in this session's subagent results (2026-07-08). Both executor artifacts reproduced verbatim in the session log; behavioral PASS is evidenced by the fire-case block presence + over-fire-case block absence, each with the executor's cited governing rule.

## Re-run — 2026-07-10 @ commit 109b3866 (post-CHK-SKL-010-trim remediation)

Why: whole-branch review found (a) the original PASS anchored a pre-squash commit while the shipped text carried ~90 lines of post-dogfood remediation, and (b) the unified exactly-2-stance form (F1's fix) had never been behaviorally exercised — B-1 had 3 stances. The review remediation also trimmed SKILL.md STEP 6 to a pointer at digest-format §多空對照/分歧點 (CHK-SKL-010), which itself warranted re-testing the over-fire guard through the pointer.

Probes (same method: blind executor, synthetic 2-source clusters, no mention of the multi-view feature in the dispatch):

- **B-3 Fire, exactly 2 stances** (2026-07-09 synthetic: 高盛「健康回檔逢低買」 vs GMO「泡沫破裂減持」): **PASS.** Executor followed the trimmed STEP 6 pointer, read the 房規 before emitting, and produced the unified 3-column table in the exactly-2 form — 2 stance rows (canonical enum 多/空) + mandatory 分歧點 row. False-balance guard executed (named 高盛 = sell-side mainstream vs GMO = self-acknowledged long-term bear — not a 50/50 split), using only in-cluster context. Zero 漏引 (both sources in 來源索引). Explicitly cited the "Fires (2 stances)" calibration case (F2's fix working).
- **B-4 Do-not-over-fire via the pointer** (2026-07-09 synthetic: 台積電 CoWoS 供應鏈盤點 + 法說前瞻, complementary facets): **PASS.** Executor read the 房規 via the pointer, applied the stance-counting test, classified both sources as complementary/no-verdict → NO block; noted the complementarity in-narrative instead. Zero 漏引.

**Re-run verdict: PASS on both dimensions at the shipped text** (fire in the exactly-2 form; no over-fire through the trimmed pointer). F1/F2/F3 fixes observed working in-run; F5 label drift (論據 → 核心論據) remediated in the same commit. Probe fixtures + raw executor outputs: session subagent results 2026-07-10.
