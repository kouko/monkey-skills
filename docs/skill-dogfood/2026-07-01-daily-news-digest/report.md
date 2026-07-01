# Dogfood report — `daily-news-digest`

> **Findings are ADVISORY.** Dogfood discovers + points; it does NOT apply edits.
> The main agent decides and makes the change. The user is the final calibrator —
> read the surfaced raw outputs (appendix), then drive fixes by talking to the main agent.

## Metadata

| Field | Value |
|---|---|
| Skill path | `/Users/kouko/GitHub/monkey-skills/obsidian/skills/daily-news-digest/` |
| Cache path | `/Users/kouko/.claude/plugins/cache/monkey-skills/obsidian/3.15.0/skills/daily-news-digest/` |
| Skill version | `3.15.0` |
| Date | `2026-07-01` |
| Passes run | `activation (blind) · executor+auditor (informed) · cold-reader (blind)` |
| Model pinned | `claude-sonnet-4-5` (all subagents) |
| Activation fidelity | `approximate (injection fallback — no live CLI sandbox)` |

## Severity summary

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 2 |
| Medium | 2 |
| Low | 1 |
| **Total** | **5** |

> Probe B (executor + auditor) verdict: **PASS_WITH_NOTES** — no new SKILL.md defects surfaced. Three execution advisories noted in §E (Story E single-source hedging, SK Hynix cross-link, frontmatter escape valve). These are output-quality notes for the executor, not structural skill defects.

---

## Findings

### ~~FINDING-001~~: `cot_mermaid.py` calling pattern — **FALSE POSITIVE**

> The Probe C prompt passed to the cold-reader contained `[cot_mermaid.py examples omitted for brevity]` — a truncation introduced **by the probe author**, not present in the actual SKILL.md. The real SKILL.md has complete bash examples for both `type:"chain"` and `type:"web"` calls in §STEP 6 (lines 322–351). No defect.

- **Severity**: ~~`Critical`~~ → retracted
- **Category**: `Progressive-disclosure`
- **Pass**: `blind` (cold-reader)
- **Probe prompt**: "Read this SKILL.md as a first-time user. What is the ONE thing that would most likely cause two different agents to produce wildly different outputs?"
- **Expected**: Calling pattern for `cot_mermaid.py` is documented so every agent produces consistent COT diagrams
- **Actual**: STEP 6 contains `[cot_mermaid.py examples omitted for brevity]`. The concrete CLI calling pattern — arguments, JSON schema, stdout format — is invisible at the point of use.
- **Transcript evidence**: *"The COT diagram rendering via `cot_mermaid.py` — specifically, the '[omitted for brevity]' calling pattern. Two agents would diverge here in the most visible, structural way: one guesses flags from the subagent contract JSON shape; another hand-writes the Mermaid `style` lines anyway (violating a hard rule); a third skips COT diagrams entirely. The COT diagram is described as 'the heart of the skill' and appears in every story, every knowledge callout, and the day-level overview."*
- **Root cause**: SKILL.md inlines example bash blocks for cot_mermaid.py in STEP 6 — but the blocks were stripped with a brevity comment when the SKILL.md was edited. The script itself is in `$SKILL_DIR/scripts/` but the calling convention exists only in the bash examples that are now gone.
- **Why static review missed it**: `skill-judge` reads the SKILL.md and sees a working JSON schema in the subagent return contract. It can't detect that the *consuming* step (STEP 6 rendering) has no concrete interface — both appear in the same document.
- **Location**: `SKILL.md:§STEP 6` — the line `[cot_mermaid.py examples omitted for brevity]`
- **Suggested fix direction**: Restore the concrete bash examples that were originally in STEP 6 (they existed in the previous version per session history). The examples should cover both `type:"chain"` (per-story `flowchart LR`) and `type:"web"` (day-level `flowchart TD`) calls, with the JSON input structure and expected stdout shown.
- **Repro**: Fresh subagent with SKILL.md only (no scripts) → ask to execute STEP 6 for a 3-story digest → observe whether agent hand-writes `style` lines or uses the script.

---

### FINDING-002: `digest-format.md` fully external — STEP 6 unexecutable cold

- **Severity**: `High`
- **Category**: `Cold-start`
- **Pass**: `blind` (cold-reader)
- **Probe prompt**: "Walk through STEP 0 and STEP 6. Are the instructions executable as written, or are there gaps that would make you guess or improvise?"
- **Expected**: STEP 6 is self-contained (or the external file's contents are reproduced inline / in a bundled reference)
- **Actual**: STEP 6 opens with **"READ `references/digest-format.md` first"** — output template, link-presentation rules, and Mermaid house style all live there. The file is not bundled in the skill's `references/` folder; it is a vault file the skill assumes exists.
- **Transcript evidence**: *"`references/digest-format.md` contents — STEP 6 says 'READ this first' but it's not reproduced in the SKILL.md. Without it, the output template, link-presentation rules, and Mermaid house style are unknown. I'd be improvising the format."*
- **Root cause**: The digest format spec was externalised to the vault intentionally (it's shared between the skill and the user's manual reference), but no fallback is specified for a cold run where the file doesn't exist or the agent hasn't read it.
- **Why static review missed it**: A static reader sees "READ references/digest-format.md" as a valid instruction — the file path exists in the vault. A cold-start runner who doesn't have vault context can't execute this instruction at all, which a static read doesn't simulate.
- **Location**: `SKILL.md:§STEP 6`, first sentence
- **Suggested fix direction**: Add a fallback sentence: *"If the file is missing or unreadable, fall back to the format described in §Hard rules + the COT colour scheme in §STEP 4."* Alternatively, inline a compact template skeleton directly in STEP 6 so the skill is self-executing without the external file.
- **Repro**: Cold-start executor subagent (vault path unknown, no file context) → attempt STEP 6 → observe whether agent asks for the file, invents a format, or stalls.

---

### FINDING-003: SKILL_DIR resolution undefined at cold start

- **Severity**: `High`
- **Category**: `Cold-start`
- **Pass**: `blind` (cold-reader)
- **Probe prompt**: "Walk through STEP 0. Are the instructions executable as written?"
- **Expected**: STEP 0 either describes a fallback for `SKILL_DIR` when the runtime header is absent, or the header is reliably injected.
- **Actual**: STEP 0 says resolve SKILL_DIR from "the skill metadata header injected by the runtime." The cold-reader sees no such header in the provided SKILL.md. Without SKILL_DIR, every script call (`collect_sources.py`, `collect_history.py`, `cot_mermaid.py`, `validate.sh`) fails.
- **Transcript evidence**: *"Resolve the skill base directory — it appears as 'Base directory for this skill:' in the skill metadata header injected by the runtime. I see no such header in what was provided. I'd have to search for it or ask. Without it, SKILL_DIR is undefined and every subsequent script call fails. This is a real blocker requiring improvisation (e.g., searching for the scripts manually with `find`)."*
- **Root cause**: The skill relies on the Claude Code plugin runtime to inject a `Base directory for this skill:` header — when the plugin is installed, this header appears. A cold-start executor (not running through the installed plugin) doesn't receive it. The skill has no fallback for this path.
- **Why static review missed it**: Static reviewers see "the runtime injects the path" as sufficient — they read the skill as it will be when installed. A dogfood executor not using the installed plugin reveals the cold-start breakage.
- **Location**: `SKILL.md:§STEP 0`, bullet 2
- **Suggested fix direction**: Add a find-based fallback: *"If the metadata header is absent (cold-start / direct invocation), locate the scripts with: `SKILL_DIR=$(find ~/.claude/plugins -path '*/daily-news-digest/scripts' -type d | head -1 | xargs dirname)`"* — this covers the most common cold-start scenario without breaking the hot path.
- **Repro**: Executor subagent without the plugin runtime (pass SKILL.md body only, no metadata header) → STEP 0 → observe whether agent stalls or improvises with `find`.

---

### FINDING-004: "anchored-open taxonomy" phrase undefined

- **Severity**: `Medium`
- **Category**: `Jargon-leak`
- **Pass**: `blind` (cold-reader)
- **Probe prompt**: "List every term or acronym that was NOT defined in the SKILL.md and that a first-time user might not know."
- **Expected**: The taxonomy design decision is self-explaining: fixed anchors you pick from, with an escape valve for new headings.
- **Actual**: The phrase "anchored-open taxonomy" appears twice (STEP 3 and STEP 5) as the name of the selection system. The concept is inferrable from the table + escape-valve instruction, but the term itself is jargon coined for this skill — not industry-standard, not defined anywhere in the document.
- **Transcript evidence**: *"'anchored-open taxonomy' — the phrase appears without definition — it means 'use these anchors but you can add new ones,' which is inferrable but not stated."*
- **Root cause**: The term was introduced during a design discussion (this session) and written into the SKILL.md as if it were a known term of art. It's a useful compound label but needs a one-line gloss on first use.
- **Why static review missed it**: A static reader who co-designed the taxonomy knows what it means. A fresh reader infers it but may still be uncertain about the rules (when to use the escape valve? what docs go in `notes`?).
- **Location**: `SKILL.md:§STEP 3` and `§STEP 5`, first paragraph
- **Suggested fix direction**: On first occurrence (STEP 3), add an inline gloss: *"**anchored-open**: pick from the fixed list below; only create a new heading if nothing fits, and document the reason in `notes`."*
- **Repro**: Cold-reader prompt as above → question 4 (undefined terms) → check if "anchored-open" appears in the list.

---

### FINDING-005: COT abbreviation never spelled out

- **Severity**: `Medium`
- **Category**: `Jargon-leak`
- **Pass**: `blind` (cold-reader)
- **Probe prompt**: Same as FINDING-004
- **Expected**: "COT" expanded on first use (e.g., "Chain-of-Thought (COT) mini-diagram")
- **Actual**: The skill uses "COT mini-diagram," "CoT 小圖," "COT completeness," and "COT diagram" throughout — but the abbreviation is never defined. A reader who doesn't know "Chain of Thought" as an LLM concept won't know what the diagram is supposed to represent conceptually.
- **Transcript evidence**: *"COT (Chain of Thought) diagram — the skill uses 'COT mini-diagram' throughout; the abbreviation is never spelled out."*
- **Root cause**: Author familiarity bias — COT is obvious to an LLM-fluent author but not defined for a general vault user.
- **Why static review missed it**: Static review checks whether the diagram is described mechanically (it is: `flowchart LR`, bullet nodes, colours). It doesn't check whether the *concept name* is defined.
- **Location**: `SKILL.md:§STEP 4`, first mention of "COT mini-diagram"
- **Suggested fix direction**: Add `(COT = Chain-of-Thought)` inline at first mention in STEP 4.
- **Repro**: Cold-reader → question 4 → check for "COT" in undefined terms list.

---

### FINDING-006: Trigger vocabulary gap — "summarize what I consumed today"

- **Severity**: `Low`
- **Category**: `Trigger-miss` (instability risk, not a hard miss)
- **Pass**: `blind` (activation probe)
- **Probe prompt**: `"summarize what I consumed today into the vault"` (Query 9 in the activation corpus)
- **Expected**: Routes to `daily-news-digest` in both runs
- **Actual**: Run 1 routed correctly; Run 2 routed to `obsidian-tldr`. One-in-two routing instability, not a hard miss.
- **Transcript evidence**: *"Run 2 drifted to obsidian-tldr ('save … to vault'); ambiguity arises because 'summarize … into the vault' strongly overlaps with obsidian-tldr's description ('save … to the vault'). Without the word 'news', 'digest', or a time-sensitive/evergreen framing, one routing pass treats this as a session-save request rather than a digest-compilation request."*
- **Root cause**: The description's trigger vocabulary is: `'整理今天的新聞'`, `'每日新聞'`, `'daily news digest'`, `'round up a day's content'`. "Summarize what I consumed" doesn't contain any of these tokens, and "into the vault" matches obsidian-tldr's phrasing more closely than any digest trigger.
- **Why static review missed it**: Trigger coverage is a distribution problem — a static reader checks whether examples exist, not whether they cover the *paraphrases* a real user would reach for.
- **Location**: `SKILL.md:frontmatter description`, trigger phrase list
- **Suggested fix direction**: Add one more trigger example to the description's use-for list: `'summarize what I consumed/read today'` (English) and `'整理今日看過的內容'` (Traditional Chinese). This anchors the "consume + vault" phrasing to the digest rather than to tldr.
- **Repro**: Injection-fallback activation probe → run query 9 (`"summarize what I consumed today into the vault"`) × 4 → check split ratio.

---

## Raw outputs appendix

### A. Activation runs (blind pass)

Fidelity: **approximate** (injection fallback — synthetic skill menu, not live CLI sandbox).

| # | Query | should_trigger | Run 1 | Run 2 | Verdict |
|---|---|---|---|---|---|
| 1 | `整理今天的新聞` | true | daily-news-digest | daily-news-digest | TP |
| 2 | `幫我做今天的每日新聞` | true | daily-news-digest | daily-news-digest | TP |
| 3 | `create today's daily news digest` | true | daily-news-digest | daily-news-digest | TP |
| 4 | `round up today's content from references/ into a digest` | true | daily-news-digest | daily-news-digest | TP |
| 5 | `今天的新聞整理一下，分成時效新聞和知識觀點` | true | daily-news-digest | daily-news-digest | TP |
| 6 | `今日のニュースダイジェストを作って` | true | daily-news-digest | daily-news-digest | TP |
| 7 | `compile what I read and watched today into a news note` | true | daily-news-digest | daily-news-digest | TP |
| 8 | `幫我跑 daily-news 2026-07-01` | true | daily-news-digest | daily-news-digest | TP |
| 9 | `summarize what I consumed today into the vault` | true | daily-news-digest | obsidian-tldr | TP (unstable) |
| 10 | `I want to process today's notes into time-sensitive and evergreen buckets` | true | daily-news-digest | daily-news-digest | TP |
| 11 | `start my day and check what's on my plate today` | false | obsidian-daily | obsidian-daily | TN |
| 12 | `save this conversation summary to my vault` | false | obsidian-tldr | obsidian-tldr | TN |
| 13 | `ingest today's references/ notes into the wiki knowledge graph` | false | wiki-ingest | wiki-ingest | TN |
| 14 | `create a new markdown note with proper frontmatter` | false | obsidian-markdown | obsidian-markdown | TN |
| 15 | `process and summarize the PDFs in this folder` | false | obsidian-file-intel | obsidian-file-intel | TN |

- **True-positive (fire when should) rate**: 10/10 across majority vote (9 clean TP, 1 unstable)
- **True-negative (silent when should-not) rate**: 5/5

---

### B. Cold-reader audit (blind pass)

Full verbatim response from a fresh zero-context subagent reading only the SKILL.md body:

```
## Fixed Question Set — Answers

### 1. Self-Contained?

No, not fully. I could execute ~80% end-to-end, but would need to ask about or resolve:

- `references/digest-format.md` contents — STEP 6 says "READ this first" but it's not
  reproduced in the SKILL.md. Without it, the output template, link-presentation rules,
  and Mermaid house style are unknown. I'd be improvising the format.
- `$SKILL_DIR/scripts/cot_mermaid.py` interface — The skill says "feed it node content JSON"
  and "Concrete calling pattern: [omitted for brevity]." That omission is a real gap; I don't
  know the exact CLI syntax or JSON schema to pass.
- `$SKILL_DIR/scripts/validate.sh` — Referenced in the hard rules but never described. What
  does it validate exactly, what does it output, and how do I act on failures?
- The skill metadata header / `SKILL_DIR` resolution — STEP 0 says the base directory
  "appears as 'Base directory for this skill:' in the skill metadata header injected by the
  runtime." I see no such header in what was provided. I'd have to search for it or ask.

### 2. Trigger confidence — Two Uncertain Requests

A. "幫我整理今天的研究筆記" ("Help me organize today's research notes")
Unsure because: the skill explicitly handles references/ (consumed external content), and
triages research/ folder items only into a Research Appendix (links only). A user asking to
"organize research notes" might want a skill that focuses on their own analysis, not one that
treats it as a footnote.

B. "做一個本週的新聞總結" ("Make a weekly news summary")
Unsure because: the skill is scoped to exactly one day (news/YYYY-MM-DD) and STEP 1 collects
by a single date. A weekly request has no obvious mapping — the skill could be fired 7 times,
or it might be the wrong tool entirely.

### 3. STEP 0 and STEP 1 Executability

STEP 0 — gaps:
- Working directory is unspecified (assumed vault root).
- "Resolve the skill base directory" depends on a runtime-injected metadata header that isn't
  present in the provided SKILL.md. Without it, SKILL_DIR is undefined and every subsequent
  script call fails. Real blocker requiring improvisation (e.g., find).

STEP 1 — executable with one gap:
The command `python3 "$SKILL_DIR/scripts/collect_sources.py" <YYYY-MM-DD> .` is clear.
Second positional arg (`.`) = vault root, reasonable assumption. Output schema is described
adequately. Executable as written once SKILL_DIR is known.

### 4. Undefined Terms

wikilink / stem — Obsidian-specific syntax; "stem" = filename without extension
frontmatter — YAML block at top of Markdown; Obsidian convention
callout ([!note], [!warning]) — Obsidian-specific styled blockquote
news/ folder — not mentioned in vault structure; existence assumed
collect_sources.py output schema — fields named but full JSON shape not shown
collect_history.py --since / --until — date format implied not stated
cot_mermaid.py JSON input schema — shown in subagent contract but CLI omitted
validate.sh — mentioned in hard rules, never described
digest-format.md — required read at STEP 6 but contents entirely external
anchored-open taxonomy — undefined phrase, inferrable but not stated
COT (Chain of Thought) diagram — abbreviation never spelled out
subagent / Agent/Task calls — assumes Claude Code multi-agent familiarity
counts.candidates — field from collector output, source only implied

### 5. Biggest Single Ambiguity

The COT diagram rendering via cot_mermaid.py — specifically, the "[omitted for brevity]"
calling pattern. The skill calls cot_mermaid.py for every diagram (day-level overview, every
story mini-diagram, every knowledge-tier mini-diagram), states "don't hand-write the style
lines," but the concrete calling pattern is omitted. Two agents diverge here most visibly:

- One guesses CLI flags from the subagent contract JSON shape
- Another hand-writes style lines anyway (violating a hard rule), producing inconsistent colours
- A third skips COT diagrams entirely

The COT diagram is "the heart of the skill" and appears in every section — this ambiguity
propagates into every section of every output.
```

---

### C. Executor artifacts (informed pass)

Executor ran STEP 0–3.5 in full and reported a synthesis *plan* for STEPs 4–6 (stopped before writing the actual digest per probe instructions). Date: 2026-07-01. Input: real vault.

**Collection**

```
22 candidates: references/ai (6), references/design (5), references/finance (6),
references/business (1), references/dev (2), references/misc (2), references/tech (1)
```

**Triage** (all 22 rows, summary)

```
10 × Time-Sensitive News
11 × Knowledge & Perspectives
 0 × Research Appendix
 1 × drop (Irish Beekeeping documentary)
```

**Story clusters** (7 stories, 4 categories)

```
🤖 AI・科技
  A — Anthropic Claude Sonnet 5 上市：性價比爭議  (#1,#4,#5 — 3 conflicting sources)
  B — Google Gemini Omni Flash API 正式開放       (#3)

📈 金融市場・總經
  C — 美股 Q2 收官強勁：半導體創史上最佳季報      (#17,#18)
  D — 聯準會鷹派警告：今年或升息三次             (#15)
  E — AI 巨頭 IPO 潮：半導體資本循環新動能       (#19 — single Korean-language source)

⚖️ 政策・法規
  F — 日本派遣業暗黑卡特爾：FTC 調查與勞動改革   (#16)

🌍 國際・地緣政治
  G — 沙烏地 MBS 的財富外交：PIF 投資與政治回報  (#20)
```

**Event Arc sweep table** (all 7 rows, no blanks)

```
A — No   (one-off launch)
B — No   (one-off API launch)
C — Yes  (April correction → Computex surge → June 5 blow-up → Q2 record; ran collect_history)
D — Yes  (Warsh Jun 1 hawkish pivot → 82% hike prob → Sintra Jul 1; ran collect_history)
E — Yes  (SpaceX IPO done → OpenAI/Anthropic next → HBM/semiconductor cycle; ran collect_history)
F — No   (FTC regulatory action, today's news only)
G — No   (FRONTLINE documentary, historical synthesis)

Red-flag check: all 3 Financial Markets & Macro stories marked Yes ✅
```

**Knowledge tier plan** (4 sub-categories)

```
AI・開發・工具: promote #14 (eval pipeline), synthesis #2+#8+#13, one-liner #6
設計・創意:    promote #11 (Waymo legibility), synthesis #9+#10, one-liner #12
商業・策略:    one-liner #7 (Equinox)
歷史・思想:    NEW escape-valve heading; #22 (Byzantine/Lex Fridman);
               to be documented in frontmatter notes
```

---

### D. Executor trajectory (informed pass)

Key ambiguities and improvisation decisions documented by the executor:

```
1. SKILL_DIR cold-start: no runtime header injected → resolved from task briefing path.
   In normal plugin operation the header is injected automatically. Documented explicitly.

2. Triage call #19 (Korean IPO/semiconductor thesis): borderline K&P vs News.
   Kept as News: "OpenAI/Anthropic IPOs are upcoming catalysts" = dated forward-looking
   news hook with specific companies named. Filed under 📈 (capital cycle lens, not model
   capability). Confidence: medium.

3. Triage call #20 (MBS/FRONTLINE): lowest confidence in News bucket.
   Historical documentary but Kushner/Mnuchin active in 2026 policy gives freshness.
   Could defensibly be K&P. Kept as News at low confidence; noted for double-check.

4. Event Arc for Story D: "Fed Warsh TOMORROW" is an upcoming event, not a progression.
   Correctly flagged arc on the *rate/policy trajectory* (Warsh Jun 1 hawkish pivot →
   bond repricing → 82% hike prob → Sintra Jul 1), per SKILL.md's rule distinguishing
   "upcoming single datapoint" from "backdrop arc."

5. Knowledge tier new heading "歷史・思想" (Byzantine/Lex Fridman):
   Fits none of the 5 Knowledge anchor concepts. Applied escape valve, planned
   frontmatter notes entry per taxonomy rules.
```

---

### E. Auditor judgment (informed pass)

Blind auditor received the executor's trajectory (sections C+D above) with no context about the skill. Verdict: **PASS_WITH_NOTES**

```
### Procedural Completeness

STEP 0: ✅ complete — digest check done, SKILL_DIR ambiguity transparently noted
STEP 1: ✅ complete — 22 candidates, 8 folders, all listed
STEP 2: ✅ complete — all 22 rows triaged with reasoning
STEP 3: ✅ complete — 7 stories, 4 categories
STEP 3.5: ✅ complete — all 7 rows filled, no blanks
Red-flag check (📈 "No" on volatile day): ⚠️ partial — C/D/E all correctly flagged Yes;
  arc narrative for E leans on single Korean source alone, thin evidence
STEP 4 synthesis plan: ✅ complete — all 7 stories addressed; COT chains named
STEP 5 K&P plan: ⚠️ partial — ≥1 promoted item per sub-category met; dev/AI tutorial
  split slightly compressed (#2 Gemini how-to + #6 Softr into same bucket)
Improvisation documented: ✅ complete — 5 notes, including hardest triage calls

### Domain Correctness

- Story A (Sonnet 5): ✅ correct cluster, three conflicting angles handled
- Story C (Q2 equities): ✅ correct, SK Hynix IPO as catalyst valid
- Story D (Fed/Warsh): ✅ correct arc call, Sintra as next milestone accurate
- Story E (AI IPO → semiconductor): ✅ arc call justified by SpaceX precedent; BUT
  single-source basis means this reads as "one analyst's thesis," not confirmed market
  event. Synthesis paragraph should hedge conditional vs confirmed.
- Stories F, G: ✅ arc-skip defensible, single-source clean stories
- SK Hynix US IPO: noted as catalyst for Story C, but also overlaps with Story E's
  HBM/semiconductor cycle thesis. Consider cross-link or brief footnote in C.

### Skill Contract Compliance

- Anchor taxonomy (6 fixed headings): ✅ all 4 used categories are from the list
- 4–7 stories: ✅ (7)
- Escape valve in frontmatter: ⚠️ planned but not yet written (planning output,
  not final digest — flag for executor when writing the actual file)
- No references/ edits: ✅

### Actionable notes for executor

1. Story E: hedge synthesis as analyst hypothesis, not confirmed trend ("if OpenAI/
   Anthropic IPOs materialize, the thesis is... " rather than stating the arc as fact)
2. SK Hynix IPO: add a cross-link or footnote connecting Story C's IPO catalyst to
   Story E's semiconductor capital cycle narrative
3. When writing final digest: add escape-valve explanation to frontmatter notes field
   for "歷史・思想" sub-category
```
