# Seven-Block Recap Schema — Reference Bundle

> **SSOT for `dev-workflow:recap` v0.1**
> This file is the authoritative source for the V1 7-block template and
> the 5 共通核心原則. SKILL.md routes here; do not duplicate content in SKILL.md.
> Source research: `AI Agent Recap 框架研究` (2026-05-25) + `對話接續綜論` (2026-05-25)
> + `2026-05-26-recap-v0.1-brief.md` (5th principle).

---

## 1 — The Seven Blocks

Each block has a one-line WHY. The WHY is sourced from the V1 template in the
Recap research note (§我的 Recap Prompt 模板（V1）) and the Claude Code 9-segment
compaction schema analysis.

### Block ↔ Audience map

This bundle is the SSOT for both L3 (in-session, human warm reader — this skill)
and the future L2 HANDOFF sister skill (cross-session, AI cold reader). Not
every block fires for every reader. SKILL.md routes the L3 subset; future
HANDOFF SKILL.md will route the L2 subset.

| # | Block | L3 (Recap, this skill) | L2 (HANDOFF, future) |
|---|---|---|---|
| 1 | Situation | ✅ render | ✅ render |
| 2 | Background | ✅ render | ✅ render |
| 3 | Assessment | ✅ render | ✅ render |
| 4 | User messages | ❌ **skip** — see Block 4 WHY | ✅ render verbatim |
| 5 | Why-this-question | ✅ render | ❌ skip (no "agent's recent question" in cross-session) |
| 6 | Pending | ✅ render | ✅ render |
| 7 | Synthesis-check | ✅ render | ✅ render (different strength — HANDOFF uses init-prompt synthesis) |

**L3 ships 6 blocks** (1, 2, 3, 5, 6, 7).
**L2 will ship 6 blocks** (1, 2, 3, 4, 6, 7) plus HANDOFF-specific additions per the HANDOFF research v1.1 schema (Interruption Snapshot, Confidence Flags, Do Not Touch, Verification Commands, etc. — those are HANDOFF-only and not in this bundle).

---

## 1.5 — Visual aids (tables / ASCII)

**Rule**: Use tables or ASCII diagrams **only when they compress information** —
not as decoration. The recap exists to be scanned, not admired. A table that
flattens 3 sub-bullets into 3 rows wins; a table with 1 row or a chart for 3
unrelated items adds framing without compressing.

Per-block guidance — added 2026-05-27 after the 3rd dogfood round surfaced
that some blocks (especially Block 3 Assessment, Block 5 Why-this-question,
Block 6 Pending) read meaningfully better with a small table:

| Block | Default form | Upgrade to table / ASCII when… |
|---|---|---|
| 1 Situation | one sentence prose | Never. One sentence cannot be a table. |
| 2 Background | bullet list | Comparing 2+ alternatives → 2-col table (option / why-rejected) |
| 3 Assessment | n/a — **default is table** | Always: 2-col key:value (假設 / 信心 / 卡住) reads cleaner than 3 separate sub-bullets |
| 5 Why-this-question | prose | 2+ options present → option-comparison table (option / cost / benefit) |
| 6 Pending | `- [ ]` checklist | Items carry metadata (priority, blocked-by, owner, due-date) → multi-col table |
| 7 Synthesis-check | one sentence + one question | Never. The whole point is a single direct ask. |

**ASCII diagrams**: useful only when there is real topology — a pipeline /
dependency graph / state machine the human needs to see spatially. Recap
content is usually a flat state snapshot; if you reach for an ASCII diagram,
double-check there is actual structure to visualize, not just a list with
arrows added.

**Anti-pattern**: a 1-row table, a 2-row table whose rows are unrelated, or
an ASCII chart for a 3-item list. These add boxes around text without
reducing parsing cost — net negative for the 60-second-read principle.

---

### Block 1 — Situation

**Prompt instruction**: One sentence — what are we doing right now? Where are we stuck?

**WHY**: Opens with the present moment so the human can orient immediately
before reading any history. Mirrors SBAR's S-block and Claude Code segment 8
("Current work"). Without this, the reader starts in the middle of a story.

---

### Block 2 — Background

**Prompt instruction**: 3–5 bullets covering:
- Key decisions made to get here
- Options that were rejected and why
- Important file names / tools / concepts — **quote directly, do not rewrite**

**WHY**: Captures the reasoning trail so the human does not have to reconstruct
"why did we choose X". Mandatory direct-quote rule stops paraphrase-creep on
technical strings (file paths, error messages, command names). Sourced from
Claude Code compaction prompt: "Directly quote key phrases from the original
text rather than paraphrasing."

---

### Block 3 — Assessment

**Prompt instruction**: Three sub-items:
- Current assumption the agent is operating under
- Confidence level (high / medium / low)
- What the agent does not know or is blocked on

**WHY**: Makes the agent's internal model visible to the human. Without this
block, the human cannot tell whether the agent's next question is well-founded
or based on a wrong assumption. Sourced from SBAR's A-block and I-PASS
contingency planning.

---

### Block 4 — User messages (L2-only — skipped at L3)

**Prompt instruction (L2 only — for the future HANDOFF sister skill)**: List
every message the user sent in this session, verbatim. No filtering. No
paraphrasing. No selection of "important" ones.

**At L3 (this skill): skip Block 4 entirely.** Renumber the rendered output to
6 blocks. Spec-critical user phrases (file paths, error messages, named
constraints) belong in Block 2 (Background) via the quote-not-paraphrase
principle — that's where the anti-drift discipline lives at L3.

**WHY**: This block has different value at L3 (in-session, human warm reader)
vs L2 (cross-session, AI cold reader). The full verbatim list — inherited from
Anthropic's compaction prompt rule "Preserve all user messages that are not
tool results" — is correct for L2 because the next agent has no other source
of user intent. At L3 the reader is the user themselves; they already remember
their own turns, so the block adds no signal and dilutes the recap by pushing
Block 5 (Why-this-question) below the fold. Two rounds of pre-merge dogfood
(2026-05-27, this PR's own session) confirmed the block was not worth the
space — even after compressing to one-line-intent + spec-critical-quotes (the
intermediate v0.1 design from commit `0d6244d0`), the user reported "沒有太大
必要" / "still not worth it". Final v0.1 design: drop at L3, keep for L2,
route spec-critical anti-drift duty to Block 2's quote-not-paraphrase rule.

---

### Block 5 — Why-this-question (L3-only)

**Prompt instruction**: Explain the agent's most recent question:
- What is the agent asking?
- Why does the agent need to know this (what breaks if the user skips it)?
- What options does the user have, and what are the trade-offs?

**WHY**: This block is L3-specific — it does not appear in HANDOFF (L2) or the
9-segment compaction schema. It exists because the most common mid-session
confusion point is: "I don't understand why the agent just asked that." Without
this block, the human may answer the question without understanding the stakes.
Sourced from the L3 Recap design in the Continuation Stack 4-layer model. L2
HANDOFF skips this block because there is no "agent's recent question" in a
cross-session cold-start context — the cold AI reader is starting fresh, not
answering a pending question.

---

### Block 6 — Pending

**Prompt instruction**: A checklist of tasks not yet completed.

**WHY**: Corresponds to Claude Code compaction segment 7 ("Pending tasks") and
I-PASS's A (Action list). Gives the human a fast scan of what is left so the
Synthesis-check question in block 7 has concrete content to confirm or redirect.

---

### Block 7 — Synthesis-check

**Prompt instruction**: State in one sentence the direction the agent expects
the user to confirm. Then ask the user to confirm or redirect before continuing.

Example format:
> "My read is that we're about to do X. Does that match your intent,
> or would you like to redirect?"

**WHY**: Sourced from I-PASS's S ("Synthesis by receiver") — the one element
that SBAR lacks. Forcing a read-back catches the failure mode where the agent
believed it communicated clearly but the user had a different mental model.
Without this block the agent continues and the mismatch only surfaces 3 turns
later. This is a **soft gate**: the agent waits for user confirmation before
proceeding, but any "yes / 對 / go / continue / 繼続" counts as confirmation.

---

## 2 — The Five 共通核心原則

These 5 principles are the normative contract behind the 7 blocks.
Each has: name, one-line definition, one-line WHY, one short failure-mode example.

The first 4 are sourced from the synthesis research note §共通核心：四大原則.
The 5th is skill-specific, added 2026-05-26 per the brief amendment.

---

### structured-schema

**Definition**: Use the fixed 7-block structure every time — no free-form summary.

**WHY**: Consistency is the user-visible value. A reader who has seen the schema
twice can scan it in 30 seconds because they know where each piece of information
lives ("expected location" principle from information design).

**Failure mode**: Agent produces a "quick summary" paragraph instead of the
7 blocks. User has to hunt for the assessment and misses that the pending
list changed.

---

### quote-not-paraphrase

**Definition**: On blocks 2 (Background) and 4 (User messages), reproduce the
original strings exactly — file paths, error messages, command names, and user
turns are quoted verbatim.

**WHY**: Every LLM pass introduces small drift. "auth module" becomes "the
authentication layer" becomes "session management" across three summaries.
Forcing direct quotes stops that drift at the source. Sourced from Anthropic's
compaction prompt rule: "Directly quote key phrases from the original text
rather than paraphrasing."

**Failure mode**: Block 2 says "we decided to restructure the config file."
The actual user phrase was "kill `config/base.py` and split into
`config/db.py` + `config/app.py`." The paraphrase drops the specific file names
that the next session needs.

---

### all-user-messages (L2-only principle)

**Definition**: At L2 (cross-session HANDOFF, AI cold reader): Block 4 lists
every user turn verbatim — no LLM filtering. The cold AI reader has no other
source of user intent.

**At L3 (this skill): the principle is dormant.** Block 4 is skipped entirely.
Spec-critical user phrases (file paths, error messages, named constraints, exact
tool / command names) are preserved by principle 2 (`quote-not-paraphrase`)
inside Block 2 (Background) — that's where the anti-drift duty lives at L3. If
the user explicitly wants a verbatim listing of their messages at L3, they ask
outside the recap schema; the recap stays focused on the 6 blocks the L3 reader
actually scans.

**WHY**: The user's intent is ground truth — that part of Anthropic's
compaction prompt ("Preserve all user messages that are not tool results")
holds for L2 because the next agent has no other source. At L3 the reader is
the user themselves who lived through the session — verbatim dump is signal-
zero noise. Two rounds of pre-merge dogfood (this PR's session, 2026-05-27)
confirmed the principle fired at L3 only because of L2-prompt inheritance, not
because of L3 reader cost / benefit. v0.1 ships with the principle reduced to
L2-only at L3-rendering time, while the anchor `all-user-messages` stays in the
bundle as the canonical SSOT for the future HANDOFF sister skill.

**Failure mode (L2)**: User said "also keep the old endpoint alive for 30
days." HANDOFF agent drops this turn as "minor." The new agent in the next
session deletes the old endpoint on day 3.

**Failure mode (L3 — what this v0.1 ships to prevent)**: Block 4 at L3 dumps
17 verbatim user turns (mostly routine "go" / "好" / "next" confirmations) +
2 substantive direction-setting turns. The human reader has to scroll past
the 17 to find the 2. Plain-language principle (#5) violated by structural
verbosity even if every line is technically plain.

---

### synthesis-check

**Definition**: Block 7 always ends with a directed question asking the user to
confirm the next-step direction before the agent continues.

**WHY**: Sourced from I-PASS's Synthesis by receiver — the one design element
SBAR lacks that has the most impact. Without a forced pause, the agent resumes
from its own assumption of alignment. The user's "yes" costs 2 seconds; the
misalignment correction costs 20 minutes.

**Failure mode**: Agent delivers the 6-block recap and immediately says "OK,
I'll proceed with option A." User was going to say option B. The agent has
already started writing 200 lines of option A code.

---

### plain-language

**Definition**: Recap output uses plain everyday language so the human can read
themselves back into state in under 60 seconds without parsing jargon. Only use
a technical term if the user introduced it first in the session (mirrors
quote-not-paraphrase on the agent's own vocabulary). Acronyms expanded on first
mention. Short sentences over long. One fact per bullet.

*(Text of this principle is quoted verbatim from the 2026-05-26 brief,
Smallest End State criterion #5. This is the skill-specific 5th principle,
added to the 4 共通核心原則 from the synthesis research.)*

**WHY**: Recap is written for a human who is already cognitively loaded from
the work they just did. An agent that explains the situation in its own
preferred vocabulary (tool names, architectural jargon, acronyms) forces the
human to do translation work at the moment they can least afford it. The recap
exists to remove load, not add it. Aligns with kouko's global preference:
"Plain language over jargon unless I introduce the term first."

**Failure mode (paraphrase-creep + jargon-creep)**: See §3 Bad Example below.

---

## 3 — Good Example

The following is a clean recap from a real SDD session (implementing a Python
test for a skill bundle). It demonstrates all 5 principles.

---

### Situation

We are writing the RED test for `seven-block-schema.md` in the `recap` skill.
The test file exists and fails because the bundle file does not exist yet.

### Background

- Decided to put the test in `dev-workflow/skills/recap/scripts/` (flat per CLAUDE.md rule)
- Rejected putting the test at plugin root — that would need a subfolder which the hook blocks
- Bundle path: `dev-workflow/skills/recap/references/seven-block-schema.md`
- Quote from plan: "RED: `pytest ...::test_all_seven_blocks_and_five_principles_present -v` fails initially because file does not exist"

### Assessment

| | |
|---|---|
| **假設** | directory structure is correct and pytest can discover the test |
| **信心** | high — ran `ls` to verify paths |
| **卡住** | nothing; the test runs and fails cleanly (expected RED state) |

*(2-col key:value table per §1.5 — Assessment defaults to this form; reads
cleaner than 3 separate sub-bullets.)*

### ~~User messages~~ (skipped at L3 — see Block ↔ Audience map)

*(L3 render skips Block 4 entirely. Spec-critical phrases from user turns
appear in Block 2 (Background) above via quote-not-paraphrase. This skip is
itself part of the good example — demonstrates principle 5 plain-language by
removing a structurally noisy block that adds no signal for the L3 reader. At
L2 HANDOFF this block fires verbatim — that example will ship with the
HANDOFF sister skill.)*

### Why-this-question

There is no pending question; this is a recap of a completed step.

**If a real question with multiple options existed** — e.g., "H2 or H3 for
block headings?" — per §1.5 the option-comparison reads better as a table:

| Option | Pro | Con |
|---|---|---|
| H2 (`##`) | matches top-level convention in bundles | larger visual jump from H1 |
| H3 (`###`) | tighter under bundle's H2 sections | regex still matches via `^#{2,3}` |

Prose is fine when there is one option or a clear narrative; reach for the
table when the human is comparing alternatives.

### Pending

- [ ] Write `seven-block-schema.md` bundle (GREEN step)
- [ ] Commit GREEN
- [ ] Return implementer output to orchestrator

*(Simple checklist — no per-item metadata, so the `- [ ]` form wins. If items
carried priority / blocked-by / owner, per §1.5 a multi-col table would fit.)*

### Synthesis-check

My read: the RED test is done and committed; the next step is to write the
bundle file. Does that match your intent, or would you like to redirect?

---

## 4 — Bad Example

The following is a **bad** recap of the same session. It violates
paraphrase-creep (principle 2) and jargon-creep (principle 5). Annotations
mark each problem.

---

### Situation

We are engaged in test-driven development activities pursuant to the
implementation of a schema-validation artifact for the in-session recap skill
within the dev-workflow plugin ecosystem.

> **jargon-creep**: "test-driven development activities", "schema-validation
> artifact", "dev-workflow plugin ecosystem" — the human does not need any of
> these terms to understand "we are writing a test for a reference file."
> Replace with one plain sentence.

### Background

- The project conventions mandate flat subfolder topology for skill directories
- The implementer elected the `scripts/` subfolder for test collocation
- The bundle artifact will be materialized at the references layer

> **paraphrase-creep**: "mandate flat subfolder topology" is a paraphrase of
> "subfolder 內不可再嵌 subfolder" (the actual CLAUDE.md rule). "materialized
> at the references layer" paraphrases "create the file at
> `references/seven-block-schema.md`." The actual path is gone.
> **jargon-creep**: "elected", "collocation", "artifact", "materialized",
> "references layer" — none of these were in the user's messages.

### Assessment

| Field |
|---|
| Hypothesis: path resolution is nominal. Confidence: sufficient. Concern: no outstanding impediments identified at this juncture. |

> **decorative-table (§1.5 anti-pattern)**: a 1-row, 1-column table is just a
> box around prose. It adds parsing cost (the reader has to recognize the
> table structure) without compressing anything. Correct form is the 2-col
> key:value table — see Good Example Block 3.
> **jargon-creep (principle 5)**: "path resolution is nominal", "no
> outstanding impediments at this juncture" — the plain version is "paths are
> correct, nothing is blocking us."

### User messages

The user dispatched the implementer with standard SDD task parameters, including
resource paths and acceptance criteria. The user's primary directive involved
TDD compliance and conventional commit discipline.

> **structured-schema violation (block 4 should not appear at L3)**: per the
> Block ↔ Audience map, Block 4 is L2-only. A bad L3 recap that includes
> Block 4 at all — even a good-looking one — violates the schema for L3.
> Correct fix at L3: delete Block 4 entirely and rely on Block 2 to carry any
> spec-critical user phrases via quote-not-paraphrase.
> **jargon-creep (principle 5)**: "dispatched", "SDD task parameters", "TDD
> compliance", "conventional commit discipline" — these are agent-introduced
> terms. Plain version: "asked me to write the failing test for the bundle file."

### Why-this-question

No pending agent interrogatives at this time.

> **jargon-creep**: "agent interrogatives" = "questions." Use plain language.

### Pending

- [ ] GREEN implementation phase execution
- [ ] Artifact persistence via VCS commit operation

> **jargon-creep**: "GREEN implementation phase execution" = "write the bundle
> file." "Artifact persistence via VCS commit operation" = "commit to git."

### Synthesis-check

Confirm alignment on trajectory and authorize continuation of workflow.

> **jargon-creep**: the plain version is "Does this match your plan — should I
> write the bundle file next?" The bad version makes the user parse two
> nominalized phrases ("confirm alignment", "authorize continuation") before
> understanding the question.
