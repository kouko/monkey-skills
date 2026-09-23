# Dogfood report — `obsidian-research`

> Advisory fix dossier. Findings localize defects and name an edit class;
> the main agent decides and applies. Raw outputs are in this directory.

## Metadata

| Field | Value |
|---|---|
| Skill path | `obsidian/skills/obsidian-research/` (PR #848, commit 96f81dade) |
| Skill version | obsidian plugin 3.21.0 |
| Date | 2026-09-24 |
| Passes run | activation (real harness) · executor + 2 blind auditors · cold-reader |
| Model pinned | `claude-opus-5-5[1m]` for activation and executor (headless `claude -p`, CLI 2.1.281); auditors `opus`; cold-reader `sonnet` |
| Activation fidelity | real-harness sandbox (`--setting-sources project`; user plugins excluded) |

## Severity summary

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 0 |
| Medium | 2 |
| Low | 4 |
| **Total** | 6 |

Headline results:

- **Triggering**: should-fire 40/40 (20 queries × 2 runs, zh-TW / ja / en); should-NOT 12/12, each routed to the intended sibling or to nothing. With the account's claude.ai connectors present (38 MCP tools incl. Claude Docs), should-fire 20/20.
- **Parallel path (previously untested)**: the headless main session dispatched 5 angle subagents in one message, then 4 refutation subagents (17 claim groups, 2–3 claims each as allowed). The refutation pass caught an outdated Yano estimate and two sampling caveats. Note written in the conversation language (zh-TW), Japanese-primary sources (38 ja / 1 en), vault heading style followed, TOC 12/12 targets valid, citations [1]–[39] match a 39-entry source list.
- **Blind auditors**: GOOD (run 1) / ACCEPTABLE (run 2). No fabricated source. Both independently found the same secondary-claim errors (FINDING-001).
- **Cost**: one note ≈ US$6.33; all 9 subagents inherited the session model.

## Findings

### FINDING-001 — Secondary numbers are never checked against their cited source

- **Severity / category**: Medium · Output-quality (valid-but-wrong)
- **Pass**: informed executor → blind auditors (2/2 runs agree)
- **Probe**: 「幫我研究一下日本推し活經濟的市場規模和消費特徵，寫成研究筆記放進 vault」
- **Expected**: every number in the note says what its cited source says.
- **Actual**: three non-key numbers are wrong or unsupported — Intage 73.0% is the share of people in their 60s *unaffected* by prices, written as the share feeling *more* pressure (inverted); "50s spend ¥99k" cited to Bloomberg [36] but absent there (it comes from a MIC survey via another outlet); "推し疲れ 33%–70%" has no source for 70%.
- **Evidence**: auditor 1 — "L144：Intage 的 73.0% 是「60 多歲回答完全沒受物價影響」的比例…意思也變成相反"; auditor 2 — "Intage … **寫錯**… intage.co.jp/news/6144/"; both flag L112 and L220.
- **Root cause**: Step 4 only verifies claims "the conclusion depends on" (8–10); Step 5 has no rule that each remaining number must match its cited source. Errors enter when the writer merges subagent summaries.
- **Why static review missed it**: checkpoint 5 only requires that claims *carry* a citation — every wrong number here does.
- **Location**: `SKILL.md` Step 4 / Step 5 checkpoint 5.
- **Suggested fix**: add a final citation pass to Step 5 — every figure and quoted claim is checked against the passage its `[n]` points to (can be one subagent over the finished note); a figure with no matching passage is fixed, re-sourced, or removed.

### FINDING-002 — Confidence labels ignore sponsor interest and sample quality

- **Severity / category**: Medium · Output-quality
- **Pass**: blind auditor run 2 (run 1 raised the same point for one row)
- **Actual**: "High" on surveys the note itself calls commercially interested online samples (推し活総研, Paidy) and on a row whose sample size is "unknown" (NRI).
- **Evidence**: auditor 2 — "推し活總研 B、C 標「高」，但第十節自己承認它是有商業利益的網路樣本"; auditor 1 — "B 是有商業利益的網路自填樣本，標「高」偏樂觀".
- **Root cause**: Step 4's High = "two independent sources + survived refutation"; nothing caps confidence for a conflicted sponsor, non-random sample, or undisclosed method.
- **Location**: `SKILL.md` Step 4 item 3.
- **Suggested fix**: add one line — a source whose sponsor benefits from the result, or with a non-random / undisclosed sample, caps the claim at Medium unless an independent source agrees.

### FINDING-003 — Summary length drifts

- **Severity / category**: Low · Workflow-drift
- **Actual**: summary paragraph has 4 sentences (limit 2–3). Auditor 2 PARTIAL, auditor 1 PASS.
- **Location**: `SKILL.md` Step 5 checkpoint 2. **Suggested fix**: none required; watch across more runs.

### FINDING-004 — Source-list entries with two URLs

- **Severity / category**: Low · Convention-violation
- **Actual**: entries [1] and [36] each hold two URLs (original + mirror).
- **Location**: `SKILL.md` Step 5 checkpoint 9. **Suggested fix**: state "one URL per entry; a mirror or syndicated copy may follow after `; mirror:`".

### FINDING-005 — Subagent model unspecified; every subagent inherits the session model

- **Severity / category**: Low · Output-quality (cost)
- **Actual**: all 9 subagents ran on the inherited Opus model; one note ≈ US$6.33.
- **Location**: `SKILL.md` Step 3 / Step 4. **Suggested fix**: optional — name a cheaper tier for per-angle search subagents where the host supports it, keep refutation on the default. Leave unchanged if cost is acceptable.

### FINDING-006 — Cold-reader gaps

- **Severity / category**: Low · Cold-start / Jargon-leak
- **Pass**: blind cold-reader
- **Evidence**: "angle：全篇使用但無明確定義"; "Step 5 …若 `research/` 是空的（第一篇筆記）沒有 fallback"; "vault convention：未定義"; "topic's own dimensions：未定義".
- **Location**: `SKILL.md` Steps 1, 2, 5. **Suggested fix**: define "angle" (one sub-question researched separately); give a default heading style when `research/` is empty; point "vault convention" at the vault's CLAUDE.md when it defines frontmatter; one example of "topic dimensions".

## Observations (not defects)

- Queries that say only "research X" without a note or vault ("研究一下 Tailwind CSS v5 有什麼新功能") routed to `domain-teams:research-team` 6/6. This matches the description's "into a note / vault" scope; widening it is a product decision.
- English sources were thin for a Japan-market topic (1 of 39). The note stated this in its limitations, as the skill requires.
- Sandbox caveat: with `--restricted`, project skills did not load and the model created a Claude Docs document instead. That was a harness artifact, not a routing defect; the corrected sandbox is recorded above.
- Meta-dogfood bias: the skill was written in the same session that ran this dogfood; blind auditors and the cold-reader are the mitigation.

## Raw outputs

- `trigger-corpus.tsv`, `trigger-results.tsv` (29 queries × 2 runs), `trigger-results-with-connectors.tsv` (20 should-fire × 1 run)
- `executor-note.md` — the note the executor produced
- Executor trajectory: 9 `Agent` dispatches (5 angle: market size, consumer profile, industry structure, risks, trends; 4 verify: market-size, consumer-behaviour, industry/outlook, risk claims), 62 WebSearch, 65 WebFetch across subagents

## Applied after this report

Fixed in the follow-up commit on PR #848: FINDING-001 (final citation pass in Step 5 checkpoint 5), FINDING-002 (confidence capped at Medium when the publisher or funder benefits, or the sample is non-random / undisclosed), FINDING-004 (one URL per source entry), FINDING-006 (angle defined, empty `research/` fallback, frontmatter pointer to the vault's CLAUDE.md, an example of topic dimensions). FINDING-003 and FINDING-005 left unchanged by decision.

A complexity check (critique, complexity mode) bundled deletions with these fixes: `frameworks.md` merged its separate skeleton list and purpose-based tool table into the question-type table and dropped a provenance paragraph and a duplicated pre-mortem line; SKILL.md dropped the "8–15 sources" guidance, which both real runs exceeded (30 and 39). Skill files went from 251 lines / 2,849 words to 225 lines / 2,649 words. Two independent readers (Claude sonnet, Codex gpt-5.6-sol) checked the revision; their three remaining points were fixed.
