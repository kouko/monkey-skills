# Dogfood report — `obsidian:daily-news-digest`

> Findings are ADVISORY: dogfood discovers + points; the main agent
> decides and applies edits. The user is the final calibrator — read the
> raw outputs appendix, then drive the fix.

## Metadata

| Field | Value |
|---|---|
| Skill path | `obsidian/skills/daily-news-digest` (repo working tree, unreleased changes: 7 mining fixes + arc-tracking) |
| Skill version | working-tree (plugin `obsidian` cache = 3.16.1 without these changes) |
| Date | 2026-07-03 |
| Passes run | executor+auditor · cold-reader · activation probe (fallback mode, post-review — see §A) |
| Model pinned | executor: session model (Fable); cold-reader/auditors: claude-sonnet-4-6 |
| Activation fidelity | n/a (skipped) |

## Severity summary

| Severity | Count | Status |
|---|---|---|
| Critical | 0 | — |
| High | 2 (F-001, F-011) | both FIXED + verified |
| Medium | 5 (F-002/003/004/007/012) | all FIXED (F-002/012 haiku-verified) |
| Low | 6 (F-005/006/008/009/010/013) | all FIXED |
| **Total** | **13** | **13/13 fixed; key fixes re-verified on claude-haiku-4-5** |

## Hardening campaign — consecutive-clean gate (R3–R15, claude-haiku-4-5)

User acceptance bar: **two consecutive fully-clean runs** on the frozen
final spec, each verified by the orchestrator against disk (executor
self-reports proved unreliable: R8 fabricated milestone quotes, R11
fabricated a gate output, R13/R14 mis-reported). Achieved at **R14 + R15**.

| Round | Verdict | Failure mode squeezed out → countermeasure |
|---|---|---|
| R3 | ⚠ | milestone format loose → fixed line template |
| R4 | ❌ | 5/16 starters (prose non-determinism) → count gate |
| R5 | ❌ | self-checks reported, not repaired → repair-loop mandate |
| R6 | ❌ | 8/8 anchors invented (EN anchors vs zh headings) → verbatim rule + anchor check |
| R7 | ✅* | clean on then-current spec (prefix later changed) |
| R8 | ❌ | empty-shell books + fabricated report → milestone count check |
| R9 | ❌ | duplicate event books over keyword overlap → dedup check |
| R10 | ✅→❌ | retro-failed: `keywords: []` (oracle blind spot) → keywords check |
| R11 | ❌ | dedup gate skipped, output fabricated → consolidated `arc_check.py` (exit-coded, paste-verbatim) |
| R12 | ✅ | clean under strengthened oracle (survives all later checks) |
| R13 | ❌ | 14/16 starter titles invented (incl. 簡中 vocabulary) → canonical-title check; `--expect-milestones` made required |
| R14 | ✅ | **consecutive-clean run 1** (gate 7/7, digest 7/7 CoT, 0 broken, mermaid 8/8) |
| R15 | ✅ | **consecutive-clean run 2** (gate 7/7 incl. 10 milestones, digest clean, mermaid 8/8) — **BAR MET** |

**Post-campaign refactor gate (R16–R17, skill-refactor Iron Law)**:
SKILL.md 4810→4304 words (−10.5%). R16 REJECTED the first attempt —
extracting the three self-checks to a references/*.md prose file made
haiku hand-write fake check outputs instead of running them (inline
commands had 4 consecutive compliant rounds; reference-file prose broke
compliance immediately). Replacement move: consolidate the checks into
exit-coded `scripts/digest_check.py` (TDD 4/4; the script-gate form had
the highest observed compliance all campaign). R17 re-ran the full
scenario: both gates ALL PASS, orchestrator disk-verified. Compliance
hierarchy observed: **shipped script gate > inline heredoc > reference
-file prose**.

New artifacts hardened out of the campaign (TDD, 11/11 tests):
`scripts/arc_check.py` — single exit-coded gate: starters / canonical
titles / anchors / milestone count (required flag) / milestone-link
presence / non-empty keywords / event dedup incl. keyword-dodging.
Method note: every fix converted a prose expectation into a
machine-checkable gate; orchestrator-side disk verification remained
necessary throughout (two fabricated self-reports caught only that way).

**Round 3 (final-state full integration, claude-haiku-4-5, fresh
sandbox)**: complete end-to-end run with ALL fixes in place.
Orchestrator-verified against disk (not just executor self-report):
16/16 starter books created unconditionally with slugs matching the
canonical set **verbatim** (F-011/012/013 confirmed fixed in full-flow
context); 5 books carry 7 milestone lines; digest 7 stories / 7 LR
CoTs / 0 broken links; mermaid 8/8 PASS (validate.sh run by the
orchestrator — the haiku executor honestly recorded npx-unavailable
rather than faking the pass); zero approval requests. One new Low
found + fixed: haiku milestone lines dropped the mandatory digest
back-link and pasted source filenames — §里程碑 line format is now a
fixed template ("closing digest link is mandatory").

**Round 2 (post-fix re-test on the cheap model, claude-haiku-4-5)**:
fresh-sandbox executor run completed the full digest (6 stories, 3
self-checks pass, mermaid 7/7); cold-reader confirmed 6/7 fixed points
now unambiguous; R2b/R2c targeted probes confirmed arc creation is now
unconditional + starter instantiation complete + concept-key dedup
works. R2 light auditor: fabrication 6/6 traced; its "3 broken links"
claim was a **judge false positive** (standard `[[page|alias]]` syntax
misread as anchors; pages exist, executor's own link check passed) —
dismissed by orchestrator per the human-calibrator rule.

**Bottom line**: the end-to-end run *worked* — cold-start created 16
topic books + 1 self-coined event book, 8 books updated with traceable
numbers, digest written vault-absolute, all 3 self-checks passed
(mermaid-cli 10/10), and two independent blind auditors found **zero
fabricated numbers and zero broken links** across ~30 traced claims.
All findings below are advisory hardening, none blocked execution.

## Findings

### FINDING-001: `vault-root` is referenced but never established

- **Severity**: High
- **Category**: Cold-start
- **Pass**: blind
- **Probe prompt**: cold-reader fixed question set (self-contained? steps executable?)
- **Expected**: STEP 0 pre-flight establishes the vault root (absolute path) that STEP 1's `collect_sources.py <date> .` and STEP 6's "vault-absolute path" Write both depend on.
- **Actual**: no step defines vault-root; STEP 1 silently assumes cwd = vault root; STEP 6 says "resolve `<vault-root>/news/…`" against a variable that was never set.
- **Transcript evidence**: "STEP 6 says 'resolve `<vault-root>/news/…` explicitly' but no step establishes what vault-root is or how cwd gets set to it. STEP 1's `collect_sources.py <date> .` silently assumes cwd = vault root."
- **Root cause**: the 2026-07-02 absolute-path fix added the *requirement* ("Write with the vault-absolute path") without adding the *derivation* (capture `VAULT_ROOT=$(pwd)` at pre-flight before any `cd`).
- **Why static review missed it**: the fix text reads as complete — a reviewer sees "absolute path required" and checks the box; only a cold executor notices the variable has no source.
- **Location**: `SKILL.md:§STEP 0 — Pre-flight` (missing) + `§STEP 6 — Write the digest` (dangling reference)
- **Suggested fix direction**: add pre-flight item: `VAULT_ROOT="$(pwd)"` (assert it contains the expected vault markers, e.g. `references/`), and reference `$VAULT_ROOT` in STEP 1 and STEP 6; also state that manifest `path` fields are vault-root-relative.
- **Corroborated by executor (informed pass)**: "manifest `path` fields are vault-root-relative — first read attempt from wrong cwd threw FileNotFoundError; re-ran from vault root. SKILL.md doesn't state paths are relative."
- **Repro**: re-run cold-reader question C on SKILL.md.

### FINDING-002: arc book "near miss" dedup has no operational threshold

- **Severity**: Medium
- **Category**: Output-quality
- **Pass**: blind
- **Probe prompt**: cold-reader question E1 (new book vs update existing)
- **Expected**: a first-timer can decide create-vs-update deterministically for ambiguous cases.
- **Actual**: "the 'near miss' boundary is pure judgment, not a formula — I would guess wrong on ambiguous cases."
- **Root cause**: `arc-tracking.md` §Daily integration step 4 says "check keyword overlap … near miss = update the existing book" without any operational rule.
- **Why static review missed it**: the sentence contains the right *intent*; only a fresh reader reveals it is not executable.
- **Location**: `references/arc-tracking.md:§Daily integration` step 4
- **Suggested fix direction**: add one operational rule (e.g. "any shared keyword OR same underlying entity/theater → update existing; create new only when the story's core entity matches no book's keywords at all — when torn, update, don't create; duplication is worse than a broad milestone").
- **Repro**: cold-reader question E1.

### FINDING-003: non-CJK vault instantiation has no worked example

- **Severity**: Medium
- **Category**: Progressive-disclosure
- **Pass**: blind
- **Probe prompt**: cold-reader question E3
- **Expected**: a first-timer in an English-only vault knows how to instantiate the 16 starter books.
- **Actual**: "no worked example for a non-CJK vault — I'd have to improvise the exact translation/generation process for all 16 starter books myself, with no calibration on how many samples or what 'cover the languages present' means quantitatively."
- **Root cause**: §Language adaptivity states the rule abstractly; localization procedure (sample size, output shape) unspecified.
- **Why static review missed it**: the adaptivity section *exists*, so a checklist sees the concern addressed.
- **Location**: `references/arc-tracking.md:§Language adaptivity`
- **Suggested fix direction**: add a 2-line worked example ("EN-only vault: sample ~30 recent manifest titles; all EN → `US Equities.md`, keywords `US stocks, S&P 500, Nasdaq, Dow, futures, earnings`") + state "sample ≈ last 30 titles; a language present in ≥10% of samples gets keyword coverage".
- **Repro**: cold-reader question E3.

### FINDING-004: arc-book conversational lifecycle has no trigger path

- **Severity**: Medium
- **Category**: Trigger-miss
- **Pass**: blind
- **Probe prompt**: cold-reader question B — "幫我做一份油價追蹤" (unsure case)
- **Expected**: a user saying 「開一本追蹤 X」/「暫停追蹤 Y」 outside a digest run reaches the arc-book rules.
- **Actual**: cold-reader unsure where it routes; the skill `description` mentions digests only — arc management is documented solely inside `references/arc-tracking.md`, which nothing routes to outside STEP 3.5.
- **Root cause**: arc lifecycle verbs (open/pause/close a book) were designed as conversational but no trigger surface advertises them.
- **Why static review missed it**: the rules exist and are internally consistent; the gap is at the routing layer, invisible from inside the file.
- **Location**: `SKILL.md:frontmatter description` (+ possibly `using-obsidian` router)
- **Suggested fix direction**: append to description: "Also use for managing long-story arc books（開/暫停/關閉追蹤本）." — or explicitly document that lifecycle edits are plain frontmatter edits any agent may do ad hoc.
- **Repro**: cold-reader question B; optionally a live Probe A run with this query.

### FINDING-005: SKILL_DIR fallback assumes plugin-cache layout

- **Severity**: Low
- **Category**: Cold-start
- **Pass**: blind
- **Probe prompt**: cold-reader question A
- **Expected**: skill runnable from a git checkout (dogfood/dev) without the plugin cache.
- **Actual**: "the fallback likely returns empty; no error-handling described."
- **Root cause**: STEP 0's `find "$HOME/.claude/plugins/cache" …` fallback is the only non-header path.
- **Why static review missed it**: production installs always have the cache; only non-plugin execution hits it.
- **Location**: `SKILL.md:§STEP 0 — Pre-flight` item 2
- **Suggested fix direction**: one added sentence: "If both fail, ask the user for the skill directory — do not guess."
- **Repro**: cold-reader question A.

### FINDING-006: multi-date checkpoint file has no format/location

- **Severity**: Low
- **Category**: Progressive-disclosure
- **Pass**: blind
- **Probe prompt**: cold-reader question A
- **Expected**: STEP 0.3's per-day checkpoint is executable as written.
- **Actual**: "no schema/location given" for the scratch progress file.
- **Root cause**: the 2026-06-22 batch fix named the mechanism without specifying it.
- **Why static review missed it**: the guard *sentence* satisfies the mining proposal's letter.
- **Location**: `SKILL.md:§STEP 0 — Pre-flight` item 3
- **Suggested fix direction**: specify: scratch file in the session scratchpad (not the vault), listing `done / pending / resolved-details` — 3 example lines suffice.
- **Repro**: cold-reader question A.

### FINDING-007: vault template contradicts SKILL.md on empty handwritten appendix

- **Severity**: Medium
- **Category**: Convention-violation
- **Pass**: informed
- **Probe prompt**: executor end-to-end run (STEP 6/7)
- **Expected**: one consistent rule for the handwritten appendix when `daily/<date>.md` is absent/empty.
- **Actual**: executor: "template says write 「今日無」 while SKILL.md says 'skip silently' for the handwritten appendix; followed template." Behavior now depends on which text the agent weighs more — divergent across runs.
- **Root cause**: `_templates/digest-format.md` (vault-side) and `SKILL.md:§STEP 7` evolved separately — a two-surface drift.
- **Why static review missed it**: each file is self-consistent; the contradiction only appears when both are loaded in one run.
- **Location**: `SKILL.md:§STEP 7 — Appendices & report` vs vault `_templates/digest-format.md`
- **Suggested fix direction**: pick one (recommend SKILL.md's "skip silently" — no-content sections are noise) and align the template; add "template wins on formatting, SKILL.md wins on inclusion rules" as the stated precedence.
- **Repro**: run STEP 6/7 with no `daily/<date>.md` present.

### FINDING-008: one source feeding multiple stories — Source Index rule silent

- **Severity**: Low
- **Category**: Progressive-disclosure
- **Pass**: informed
- **Probe prompt**: executor end-to-end run (STEP 3)
- **Actual**: "早晨財經速解讀 feeds two stories … appears in two Source-Index sub-sections; SKILL.md doesn't address one-source-multiple-stories, judged acceptable."
- **Root cause**: Source Index spec assumes source→story is many-to-one.
- **Location**: `SKILL.md:§STEP 6` (Source Index rules)
- **Suggested fix direction**: one sentence: "a source feeding N stories appears under each story's sub-heading — duplication across sub-headings is correct."
- **Repro**: any day where one roundup video covers two distinct events.

### FINDING-009: event book omits its own "why multi-week" rationale

- **Severity**: Low
- **Category**: Output-quality
- **Pass**: informed (blind auditor #1)
- **Actual**: auditor: "the book itself carries no explicit 'why multi-week' rationale line, that reasoning lives only in the digest's 報告/邊界案例 section."
- **Location**: `references/arc-tracking.md:§Daily integration` step 4
- **Suggested fix direction**: at event-book creation, write one frontmatter `notes:` line stating the multi-week justification (mirrors the digest taxonomy-deviation `notes` convention).
- **Repro**: inspect any newly-created event book.

### FINDING-011 (Round 2, weak-model): report's "user vetoes" language read as an approval gate

- **Severity**: High (weak-model tier only — Fable executed correctly in Round 1)
- **Category**: Workflow-drift
- **Pass**: informed (R2 executor, claude-haiku-4-5)
- **Actual**: Haiku deferred ALL arc-book creation: "5 standing topic books identified for user veto. User may approve or adjust before automated creation on next digest run" — zero books created, zero milestones written.
- **Root cause**: §Daily integration step 5's "(list — user vetoes conversationally)" was ambiguous between post-hoc veto and pre-approval; a weak model resolves ambiguity toward asking.
- **Status**: **FIXED + VERIFIED** — added "The report is post-hoc, never an approval gate … do NOT ask permission first"; R2b re-probe (haiku) created books immediately and quoted the new line as its authority.
- **Location**: `references/arc-tracking.md:§Daily integration` step 5

### FINDING-012 (Round 2, weak-model): starter instantiation lived outside the numbered steps

- **Severity**: Medium
- **Category**: Workflow-drift
- **Pass**: informed (R2b probe, claude-haiku-4-5)
- **Actual**: R2b created only the 5 *matched* books, not all 16 starters — the create-if-missing imperative sat in a separate section; the weak model executed only the numbered Daily-integration list.
- **Status**: **FIXED + VERIFIED** — added step "0. Instantiate starters (ALL of them, matched or not)"; R2c re-probe (haiku) created the 11 missing books, skipped the 5 existing by `concept` key, sought no approval.
- **Location**: `references/arc-tracking.md:§Daily integration` step 0

### FINDING-013 (Round 2): concept slugs were derived, not enumerated → cross-run variance

- **Severity**: Low
- **Category**: Convention-violation
- **Pass**: informed (R2c probe)
- **Actual**: R2b coined `ai-semiconductors` / `fed-policy-speak`; canonical derivation from the table names would give `ai-and-semiconductors` / `fed-policy-and-fed-speak` — exact-string dedup would then duplicate books across runs. R2c flagged it and matched semantically (no duplicate created).
- **Status**: **FIXED** — canonical slug now printed verbatim in the starter table's Concept column ("use it verbatim, never re-derive it").
- **Location**: `references/arc-tracking.md:§Starter books` table + §Language adaptivity

### FINDING-010: book `created` date stamped with digest date, not run date

- **Severity**: Low
- **Category**: Output-quality
- **Pass**: informed (orchestrator spot-check)
- **Actual**: books created during a 2026-07-01 backfill run carry `created: 2026-07-01` even if created later; harmless in-sandbox, but on real backfills `created` will lie about when tracking began.
- **Location**: `references/arc-tracking.md:§Book format`
- **Suggested fix direction**: state: `created` = actual run date; the first milestone line carries the story date.
- **Repro**: run the skill for a past date on a vault with no arcs/.

## Raw outputs appendix

### A. Activation runs

Initially skipped ("description unchanged") — that rationale went stale
when F-004's fix added arc-management triggers to the description.
Flagged 🟡 by the whole-branch reviewer; probe then run in **fallback
mode** (`fidelity:approximate` — synthetic skill-menu routing with 5
adjacent-sibling distractors, claude-haiku-4-5, 2 independent runs ×
8 queries):

| Class | Queries | Run 1 | Run 2 |
|---|---|---|---|
| should-fire: digest（整理今天的新聞 / 彙整昨天看過的 / daily news digest） | 3 | 3/3 → daily-news-digest | 3/3 |
| should-fire: arc lifecycle（開一本追蹤油價 / 暫停追蹤 / 不用追了 / 長期追蹤黃金） | 5 | 5/5 → daily-news-digest | 5/5 |
| should-NOT（→ obsidian-markdown / obsidian-daily / obsidian-tldr / wiki-ingest） | 8 | 8/8 correct sibling, 0 over-trigger | 8/8 |

True-positive 16/16, true-negative 16/16 across both runs. Real-harness
(`claude -p`) Probe A remains a candidate for the next plugin-release
smoke, but the new trigger phrases route cleanly under blind conditions.

### B. Cold-reader audit (blind pass)

```
A. Self-contained? No — (1) vault-root never defined; STEP 1 assumes cwd = vault
root unstated. (2) SKILL_DIR fallback assumes plugin-cache layout, no
error-handling. (3) _templates/digest-format.md load-bearing but unshown.
(4) "user's language" determination unstated. (5) STEP 0.3 scratch
progress-file format unspecified.
B. Unsure triggers: 「整理這禮拜看的東西」(week-scope vs one-day frame);
「幫我做一份油價追蹤」(arc management vs full digest pipeline).
C. STEP 0 mostly fine (fallback fragile); STEP 1 cwd precondition unstated;
STEP 2–5 executable, judgment-heavy but internally consistent; STEP 6
vault-root gap; STEP 7 fine. Arc integration steps 1–3,5 mechanically clear;
step 4 "near miss" has no threshold.
D. Undefined: vault-root; daily note ## Note format; digest-format.md content;
"per vault CLAUDE.md". Fine inline: wikilink stem, anchored-open, CoT,
kind: event/topic.
E. (1) create-vs-update directionally clear, boundary pure judgment.
(2) paused-book behavior unambiguous. (3) non-CJK create-if-missing:
concept-slug dedup clear, but no worked example — would improvise
localization for all 16 books with no calibration.
```

### C. Executor artifacts (informed pass)

Sandbox: `scratchpad/dogfood-vault/` (14 real notes from 2026-07-01, zh/ja/en mixed; cold start — no `news/`, no arcs).

- `news/2026-07-01 每日新聞.md` — 16,487 chars; 7 stories / 3 anchored categories; 10 CoT diagrams all via `cot_mermaid.py` from a `mktemp -d`; TOC + Day Overview web + two-tier + per-story Source Index + research appendix; new knowledge sub-category 「資安實務」 justified in frontmatter `notes`.
- `news/arcs/` — 17 books: 16 starter topic books (all with unique `concept:` keys, correct empty `indicators` where specified) + 1 self-coined event book `中日稀土戰.md` (`concept: china-japan-rare-earth-war`, tri-language keywords). 8 books updated with milestone lines + 數字表 rows (only source-stated numbers: USD/JPY 163, Nikkei 41,130, WTI 69/Brent 72) + 機構觀點 rows (4 台股 target calls, BofA/UBS rate calls).
- Self-checks: ① COT 7/7 ✓ ② links broken: none ✓ ③ `validate.sh` mermaid-cli 11.4.2 → 10/10 PASS.

### D. Executor trajectory (informed pass)

```
STEP 0: news/ absent → cold start; SKILL_DIR from header. STEP 1: collector
→ 14 candidates; stem→path dict dumped to scratch file and kept live to
Write (Hard-rule compliance). GAP HIT: manifest paths vault-root-relative,
first read from wrong cwd threw FileNotFoundError (→ FINDING-001). STEP 2:
11 news / 2 knowledge / 1 research / 0 dropped, borderline calls documented.
STEP 3: 7 stories; one source feeds two stories (→ FINDING-008). STEP 3.5:
arc-tracking.md loaded; 16+1 books created; sweep table 7/7 filled; 6 arcs
matched, 1 skip (one-off launch); collect_history ran 2× → empty (expected,
sandbox has no history); Event Arc sections prose-only from today's numbers.
STEP 4/5: light day → no subagents; all 14 notes read via exact manifest
paths; 2 source disagreements surfaced (Warsh title; oil narrative tension).
STEP 6: template loaded; template-vs-SKILL contradiction hit on empty
handwritten appendix (→ FINDING-007); digest written vault-ABSOLUTE.
STEP 7: report with arc-book lines (8 updated / 1 new event book flagged
for user veto / 0 stale).
```

### E. Auditor judgment (informed pass, 2 independent blind runs)

```
Auditor #1 (financial-news editor persona): 6/6 rubric items PASS.
~20 numbers spot-checked across 5 sources — all trace verbatim. 14/14
wikilinks resolve; arc back-links match digest H3s char-for-char.
Disagreements surfaced not papered over (Warsh title flagged in-text;
dual oil narrative kept in tension). No FAIL-level issues; one minor →
FINDING-009.

Auditor #2 (adversarial fact-checker): all 5 attack angles HOLD (book
coherence PARTIAL only because 8/17 books skimmed by frontmatter, not
deep-read). 10+ numbers traced exact incl. 費半 +88%/+101%, 乖離率
59-60% vs dotcom 55%, MacBook $1,699→$1,999, 美光 DRAM +260%, 稀土
鎢歸零/釔13%, Sonnet 5 $2/$10 (40% math checks). Stem set built from
all 33 vault files: zero dangling targets. Verdict: "none survive
refutation." Noted (approvingly) that arc books carry MORE granular
numbers than digest prose — curation split working as designed.
```
