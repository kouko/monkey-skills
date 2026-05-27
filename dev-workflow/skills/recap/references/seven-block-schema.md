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

### Block 4 — User messages (compressed for L3 reader)

**Prompt instruction**: For each user turn in this session, produce one line:
- A short plain-language summary of the turn's intent (≤15 words)
- Plus a verbatim quote of any **spec-critical phrase** in that turn — file
  paths, error messages, exact tool/command/file names, named constraints
  (numbers / dates / hard limits), or any sentence whose paraphrase would
  change the meaning

If the turn contained no spec-critical phrase, the one-line intent alone is
enough. If the user explicitly asks "show me my original messages" (or any
language-equivalent), produce the full verbatim list instead. Default is
compressed.

**WHY**: This block has different value at L3 (in-session, human warm reader)
vs L2 (cross-session, AI cold reader). The full verbatim list — inherited from
Anthropic's compaction prompt rule "Preserve all user messages that are not
tool results" — is correct for L2 because the next agent has no other source
of user intent. At L3 the reader is the user themselves; the verbatim list
they already remember dilutes the recap (violates principle 5, plain-language /
60-second read). The compressed form preserves the anti-drift goal — spec-
critical phrases stay verbatim so paraphrase-creep cannot erase file paths /
constraints — while collapsing routine user turns to one-line intent so the
recap stays scannable. The opt-in escape hatch ("show me originals") restores
full verbatim when the user actually needs it.

---

### Block 5 — Why-this-question

**Prompt instruction**: Explain the agent's most recent question:
- What is the agent asking?
- Why does the agent need to know this (what breaks if the user skips it)?
- What options does the user have, and what are the trade-offs?

**WHY**: This block is Recap-specific — it does not appear in HANDOFF or the
9-segment compaction schema. It exists because the most common mid-session
confusion point is: "I don't understand why the agent just asked that." Without
this block, the human may answer the question without understanding the stakes.
Sourced from the L3 Recap design in the Continuation Stack 4-layer model.

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

### all-user-messages

**Definition**: Block 4 preserves the **full set** of user-stated intent across
the session. The shape of preservation depends on the reader:
- **L3 (in-session, human reader — this skill's default)**: one-line intent per
  user turn + verbatim quote of any spec-critical phrase in that turn (file
  paths, error messages, named constraints, numbers, exact tool / command
  names). User can request full verbatim with phrases like "show me my original
  messages."
- **L2 (cross-session HANDOFF, AI reader — future sister skill)**: every user
  turn verbatim, no exceptions. The cold AI reader has no other source of user
  intent.

The non-negotiable: no LLM filtering of which intents to keep. Every user turn
is represented (compressed or verbatim); none is dropped as "unimportant."

**WHY**: The user's intent is ground truth — that part of Anthropic's
compaction prompt ("Preserve all user messages that are not tool results")
holds across both readers. What changes between L3 and L2 is the
*representation*, not the *coverage*: a warm human reader who lived through the
session has their own memory of routine turns, so verbatim dump is noise; a
cold AI reader has nothing, so verbatim is the only signal. Spec-critical
phrases stay verbatim in both forms because paraphrase-creep on file paths /
constraints is the failure mode this principle exists to prevent. (This L3 vs
L2 distinction was added 2026-05-27 after pre-merge dogfood showed the original
"every turn verbatim" rule was inherited from the L2-audience compaction prompt
and didn't fit L3's human-reader cost / benefit.)

**Failure mode (intent dropped)**: User said "also keep the old endpoint alive
for 30 days." Agent compresses this turn to "user asked about endpoint" without
the 30-day constraint quoted verbatim. The new agent in the next session
deletes the old endpoint on day 3.

**Failure mode (verbatim noise at L3)**: User session has 30 routine turns
("go", "好", "next", "fix that", "merge"). Agent dumps all 30 verbatim into a
block that the user has to scroll past to reach block 5 — violates
plain-language (principle 5) and structured-schema's scan-in-30-seconds value.

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

Current assumption: the directory structure is correct and pytest can discover the test.
Confidence: high — ran `ls` to verify paths.
Blocked on: nothing; the test runs and fails cleanly (expected RED state).

### User messages (compressed — L3 form)

1. Dispatched implementer for T1 with full SDD task spec. Spec-critical quote:
   `dev-workflow/skills/recap/references/seven-block-schema.md` (target path);
   `pytest ...::test_all_seven_blocks_and_five_principles_present -v` (RED
   acceptance command).

*(Single-turn session — only the dispatch prompt. If user later asks "show me
the full original message," produce the verbatim text. Default stays
compressed.)*

### Why-this-question

There is no pending question; this is a recap of a completed step. If there
were a question — e.g., "should I use H2 or H3 for the block headings?" — the
answer matters because the test regex matches `^#{2,3}`, so both work, and the
choice affects how the document renders in a preview.

### Pending

- [ ] Write `seven-block-schema.md` bundle (GREEN step)
- [ ] Commit GREEN
- [ ] Return implementer output to orchestrator

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

Hypothesis: path resolution is nominal. Confidence: sufficient.
Concern: no outstanding impediments identified at this juncture.

> **jargon-creep**: "path resolution is nominal", "no outstanding impediments
> at this juncture" — the plain version is "paths are correct, nothing is
> blocking us."

### User messages

The user dispatched the implementer with standard SDD task parameters, including
resource paths and acceptance criteria. The user's primary directive involved
TDD compliance and conventional commit discipline.

> **all-user-messages violation (intent dropped)**: even in the L3-compressed
> form, principle 3 requires every user turn to be represented AND any
> spec-critical phrase to be quoted verbatim. This summary drops the actual
> file paths (`dev-workflow/skills/recap/references/seven-block-schema.md`),
> the RED test command, and the commit format constraint. The compressed form
> would still say "Dispatched T1 implementer. Spec-critical quote: `<path>`,
> `<command>`" — losing those quotes is the failure mode this principle
> prevents.
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
