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
| High | 1 (FINDING-007, round 2) |
| Medium | 2 |
| Low | 4 |
| **Total** | 7 |

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
- Run 1: `run1-executor-note.md`, `run1-executor-trajectory.md`, `run1-reviews.md` (two blind auditors + cold reader)
- Codex audit of the PR after round 1: `codex-audit.md`
- Run 2: `run2-executor-note.md`, `run2-executor-trajectory.md`, `run2-reviews.md`
- Citation-check trial on run 2: `run2-citation-check-prompt.md`, `run2-citation-check-log.md` (137 items), `run2-citation-check-trajectory.md`

## Applied after this report

Fixed in the follow-up commit on PR #848: FINDING-001 (final citation pass in Step 5 checkpoint 5), FINDING-002 (confidence capped at Medium when the publisher or funder benefits, or the sample is non-random / undisclosed), FINDING-004 (one URL per source entry), FINDING-006 (angle defined, empty `research/` fallback, frontmatter pointer to the vault's CLAUDE.md, an example of topic dimensions). FINDING-003 and FINDING-005 left unchanged by decision.

A complexity check (critique, complexity mode) bundled deletions with these fixes: `frameworks.md` merged its separate skeleton list and purpose-based tool table into the question-type table and dropped a provenance paragraph and a duplicated pre-mortem line; SKILL.md dropped the "8–15 sources" guidance, which both real runs exceeded (30 and 39). Skill files went from 251 lines / 2,849 words to 225 lines / 2,649 words. Two independent readers (Claude sonnet, Codex gpt-5.6-sol) checked the revision; their three remaining points were fixed.

## Round 2 — Codex audit, rerun, and a structural citation check

**Codex audit** (`gpt-5.6-sol`, high reasoning, read-only; `codex-audit.md`): NEEDS_REVISION. Accepted and fixed: user-named languages now add to English + Japanese instead of replacing them; vault root found by walking up to `.obsidian/`; frontmatter follows the vault's CLAUDE.md convention when it has one; Yin attribution removed from the case-study skeleton; Hofstede limited to cross-national averages; Kano/JTBD dropped from the comparison row; KJ steps completed; the example cut to fragments; missing raw evidence added (this directory). Not applicable: its pytest and `gh` failures came from its read-only, offline sandbox.

**Run 2** (skill after those fixes; `run2-*`): Taiwan Japanese-era railways with Korean sources added, started from the vault's `research/` subfolder. Vault root found; languages 26 zh-TW / 18 ko / 6 ja / 2 en; 5 angle + 3 verify subagents; no empty chapters; US$10.81. Both blind auditors: ACCEPTABLE.

### FINDING-007 — The prose "check every figure before saving" was skipped, and the note claimed it was done

- **Severity / category**: High · Gate-bypass
- **Evidence**: the run-2 trajectory shows the main session wrote the note immediately after the verify subagents returned — no further subagent, no source fetch — while the note's method section says every figure and citation was checked. Auditor A: 3 of 19 secondary items not in the cited source, 1 causal claim contradicted by its own source; auditor B: "partly" credible.
- **Root cause**: the rule was optional ("one subagent can do this pass") and left no artifact, so skipping it was invisible.
- **Industry practice** (EN + JP web research): attribution is enforced structurally — generation bound to quoted spans (Anthropic Citations API, Gemini grounding), a separate checker role working from the writer's source material (New Yorker fact-checking; newspaper 校閲 → デスク double check), and tiered checking where a cheap pass covers everything and only failures get the expensive check (SAFE; NLI gatekeepers; a Japanese three-stage citation check). Same-model self-verification shares blind spots. Paper figures were gathered by a research subagent and not individually re-verified.

**Citation-check trial** (`run2-citation-check-*`): one Sonnet agent, given the run-2 note and a packet of the 8 subagent reports, checked 137 items: 122 passed on text alone, 13 escalated to the cited page (20 fetches), 15 final failures. It caught 3 of the 4 errors auditor A found (Daejeon population, 鹽水港 head office, 鴨綠江 bridge year) and missed the fire-as-cause claim because it checked the date only. Cost US$1.52 (~14% of the note), 6 minutes. Its 11 additional findings were not independently re-checked.

**Fix applied**: a required Step 6 — a separate subagent checks every figure, date, attribution, causal claim and quote against the saved source packet (text first, cited page only on failure; causal claims need the stated cause), returns a table, and the note's method section copies its counts; without subagents the note must say "self-checked". Also: works by one author or organization count as one source for independence. Two readers (Claude sonnet, Codex) checked the wording; their points (packet timing, writing fixes back to the saved note, a stale step reference, the scope of the same-author rule) were fixed.

**Residual risk**: Step 6 is still an instruction, not an enforced gate. It is harder to skip than before (a named required step with a table the note and chat report must quote) but an agent can still ignore it.

## Round 3 — in-vault triggering and a final end-to-end run

**In-vault triggering** (owner's decision: inside an Obsidian vault, any research request should use this skill and produce a note). The description now says so. Test (`trigger-*-vault-vs-plain.tsv`): the same 9 queries × 2 runs in a sandbox vault (`.obsidian/` plus a CLAUDE.md saying it is a vault) and in a plain project. Plain research requests without the word "note": vault 12/12 → obsidian-research, plain project 12/12 → research-team. Quick factual question, single-claim check, wiki-gap scan: same sibling (or none) in both. Regression of the original 29-query corpus with the new description (`trigger-results-regression.tsv`): should-fire 40/40, should-not 12/12, ambiguous 6/6 → research-team in the non-vault sandbox — unchanged. Caveat: the vault signal the router sees is the vault's CLAUDE.md and the path; a vault whose CLAUDE.md never mentions Obsidian may not be recognised.

**Run 3** (`run3-*`; final skill; prompt without the word "note", from a vault): the note was written; 5 angle + 4 refute subagents; the source packet was written to 8 files outside the vault before writing; **Step 6 ran** as a separate subagent the main session put on Sonnet; the method section reports its counts (~110 items, 0 mismatches). US$8.20. en 47 / ja 10.

Blind auditors: GOOD / ACCEPTABLE. Every secondary figure they checked (20+ and ~15) was in its cited source — the wrong-source class from runs 1–2 did not recur. Both found the same remaining class, **paraphrase drift**: "more than 32GB" written as "32GB or more", a cherry-picked benchmark setting, an AI-generated estimate counted as a measurement (and its High confidence), "only mlx-lm can fine-tune" from an unchecked alternative, and a comparison table mixing conditions.

**Fix applied**: Step 6 tier 1 also checks that qualifiers and the source's type are kept; Step 4 says an estimate or AI-generated article is not a measurement and that "only / does not exist" needs a source; Step 5 checkpoint 4 requires comparison rows to share conditions or state the difference in the header. Not re-run end to end after these three sentences, by decision: the remaining errors are subtle and visible in use.

**Final readers** (Claude sonnet, Codex gpt-5.6-sol) on these changes: both flagged over-broad in-vault triggering (a chat-only request, "look into why the build fails") and an unclassifiable "source type" rule. Fixed: the description now excludes chat-only / no-note requests and debugging or code work; research subagents record how each source got its figure (measured / reported / vendor claim / estimate or model output / not stated) so the checker compares against the packet instead of guessing; an estimate, model output, or unstated method cannot raise a claim above Low on its own; "only / does not exist" claims join the Step 6 checklist; comparison-table conditions are defined (hardware, version, configuration, method). Trigger tests re-run on the final description: vault vs plain 11 queries × 2 — plain research 12/12 vault / 12/12 research-team outside, chat-only and debugging requests do not trigger in either; regression 40/40, 12/12, ambiguous 6/6 → research-team. (A first regression attempt hit the account's session limit for queries 20–29; those runs were discarded and the whole corpus re-run, 0 limit hits.)
