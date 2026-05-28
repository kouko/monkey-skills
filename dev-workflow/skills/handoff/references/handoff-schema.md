# Ten-Block HANDOFF Schema — Reference Bundle

> **SSOT for `dev-workflow:handoff` v0.1**
> This file is the authoritative source for the V1 10-block template and
> the 5 共通核心原則. SKILL.md routes here; do not duplicate content in SKILL.md.
>
> **Audience note**: This bundle is L2 (cross-session, AI cold reader).
> Its sister skill is L3 (in-session, human warm reader): `dev-workflow:recap-state`.
> Each skill ships its own self-contained bundle — no file sharing, no cross-imports.
> Per Anthropic skill-independence convention (`CLAUDE.md §Skill Structure`):
> "每個 skill 是自包含目錄".
>
> **L2 vs L3 audience distinction**:
> - L3 Recap reader: human, warm context (session still alive), 60-second scan
> - L2 HANDOFF reader: cold AI agent, zero context (new session / new tool), needs
>   maximum verbatim content + precise identifiers + runnable verification commands

---

## 1 — Block ↔ Audience Map

This bundle is the SSOT for L2 (HANDOFF — cross-session, AI cold reader).
The L3 sister is `dev-workflow:recap-state` with its own separate bundle.
Do NOT cross-link, import, or reference the recap bundle from this file.

| # | Block name | L2 HANDOFF | Note |
|---|---|---|---|
| 1 | Frontmatter | ✅ required | Machine-parseable state snapshot |
| 2 | Situation | ✅ required | What we are doing right now |
| 3 | Background | ✅ required | Decisions + rejected paths + critical paths (verbatim) |
| 4 | All user messages | ✅ required | Verbatim — L2 audience has no other source of user intent |
| 5 | Recent decisions | ✅ required | Why-we-chose-X-over-Y with full WHY |
| 6 | Pending | ✅ required | Tasks not yet done |
| 7 | Critical files | ✅ required | Path + why-it-matters + recently-modified |
| 8 | Do Not Touch | ✅ required | Explicit guardrails — cold AI must not "fix" constrained code |
| 9 | Verification | ✅ required | Runnable shell assertions before cold AI continues |
| 10 | Confidence | ✅ required | Per-block ✅⚠️❓ — cold AI must not treat guesses as ground truth |

**Why L2 keeps all 10**: The cold AI reader has zero prior context.
Every block that Recap drops at L3 (because the human remembers it) must
be present at L2 because the cold AI does not.

---

## 2 — The Ten Blocks

Each block has: prompt instruction (what the agent MUST author at prepare-time)
+ WHY (sourced from research v1.1).

---

### Block 1 — Frontmatter

**Prompt instruction**: Author YAML frontmatter at the very top of the file.
Required fields:

```yaml
---
handoff_id: HANDOFF-<NNN>
created: <ISO-8601 timestamp with timezone>
trigger_type: voluntary  # voluntary | forced
project: <repo or project name>
chain:
  continues_from: <previous HANDOFF filename or null>
git:
  branch: <output of git rev-parse --abbrev-ref HEAD>
  head: <output of git rev-parse HEAD>
  dirty: <list of uncommitted files from git status --short, or []>
tools:
  claude_code: <output of claude --version>
---
```

**WHY** (research v1.1 §Schema v1.1 frontmatter): Machine-parseable fields let
the cold AI agent run automated staleness checks and chain traversal without
parsing prose. `trigger_type` distinguishes voluntary ("work is done, resume
tomorrow") from forced ("context pressure") — schema emphasis differs.
`chain.continues_from` enables multi-handoff history traversal up to 3 levels.
`git.head` is the ground-truth state anchor: if the new session finds a
different HEAD, it surfaces the divergence before proceeding.

---

### Block 2 — Situation

**Prompt instruction**: One sentence — what are we doing right now?
What is the exact state of the work at this moment?

**WHY** (research v1.1 §Current State Snapshot, softaworks §Current State Summary):
Opens with the present moment so the cold AI can orient before reading any
history. The cold reader has zero warm context; without this anchor it is
reading a story whose chapter-marker is missing.

---

### Block 3 — Background

**Prompt instruction**: 3–7 bullets covering:
- Key decisions made to reach this point
- Options that were rejected and WHY (exact reason, not paraphrase)
- Critical file paths and tool names — **quote directly, do not rewrite**

**WHY** (research v1.1 §Recent Decisions, softaworks §Important Context):
Captures the reasoning trail so the cold AI does not re-litigate rejected paths.
Direct-quote rule stops paraphrase-creep on technical identifiers.
The cold reader who does not know WHY we chose X will choose Y by default.

---

### Block 4 — All User Messages

**Prompt instruction**: List every message the user sent in this session,
verbatim. No filtering. No paraphrasing. No selection of "important" ones.
Format: numbered list, one message per item.

**WHY** (research v1.1 §All User Messages, synthesis research §原則 3):
The cold AI reader has no other source of user intent.
"You cannot let LLM decide which user messages are unimportant — user intent
is ground truth." (synthesis research §共通核心 原則 3).
At L3 (Recap), the user reads their own turns and this block is redundant.
At L2, the cold AI is starting from zero — every verbatim user message is
the ONLY record of constraints the user stated.

**Failure mode (skip this block at L2)**: User said "also keep the old
endpoint alive for 30 days." The HANDOFF agent dropped this turn as minor.
The cold AI in the next session deleted the old endpoint on day 3.

---

### Block 5 — Recent Decisions

**Prompt instruction**: For each significant decision made in this session,
write a three-part entry:
```
**Decision**: <exact statement of what was decided>
**WHY**: <verbatim reason — quote the user's words or the actual rationale>
**Rejected alternative**: <what was considered and discarded, and why>
```

**WHY** (research v1.1 §Recent Decisions, Don't Sleep On AI §Section 4):
Decisions without WHY are half-useful: the cold AI sees the conclusion but
not the constraint that produced it. Without the rejected alternative, the cold
AI will re-evaluate and possibly re-choose it. This is the "re-litigated
decisions" failure mode: the new agent picks an approach already rejected
because it has no record of the rejection.

---

### Block 6 — Pending

**Prompt instruction**: A checklist of tasks not yet completed.
Mark items with priority (P1 / P2 / P3) and any blocking dependency.

```
- [ ] [P1] <task> — <short context if needed>
- [ ] [P2] <task> — blocked by <X>
```

**WHY** (research v1.1 §Pending Work, softaworks §Pending Work):
Gives the cold AI a fast scan of what is left. Without an explicit pending
list the cold AI starts work based on its interpretation of Situation — which
may omit half of what was actually queued.

---

### Block 7 — Critical Files

**Prompt instruction**: A table of files the next session must know about.

| File path | Why it matters | Recently modified |
|---|---|---|
| `<exact path>` | <one sentence> | <yes/no — and what changed> |

**WHY** (research v1.1 §Critical Files, softaworks §Critical Files):
The cold AI does not know which files are load-bearing for the current work.
Without this block it either reads every file (slow) or reads the wrong ones
(wrong-state assumptions). Exact paths are required — paraphrases ("the config
file") do not resolve to filesystem locations.

---

### Block 8 — Do Not Touch

**Prompt instruction**: Explicit list of code, files, or conventions the cold AI
MUST NOT modify or "improve" without explicit user permission. Include the reason.

```
- `<path or convention>` — <reason this is constrained>
```

**WHY** (research v1.1 §Do Not Touch, Don't Sleep On AI §Section 7):
Cold-start AI agents see code smells and want to "fix" them.
"Must explicitly forbid" (research v1.1 §5 獨有段). Without this block, the
cold AI performs unauthorized refactoring of constrained code, breaking
external contracts the previous session already knew about.

Example from research:
```
- `src/legacy/billing.ts` — looks like code smell but has contract constraint, can touch after 2026-07
- naming convention `snake_case` in db layer, `camelCase` in JS layer — intentional, not inconsistency
```

---

### Block 9 — Verification Commands

**Prompt instruction**: List every shell command the new session MUST run and
the expected output (or expected pattern). Format:

```
- `<command>` — expected: <exact output or pattern>
```

If any command output does not match expected: **stop and ask the user**.
Do not proceed on mismatched state.

**WHY** (research v1.1 §Verification Commands, softaworks RESUME MODE step 4):
HANDOFF is written at time T; the new session runs at time T+N. Anything
could have changed. Verification commands provide a runnable integrity check —
the same discipline as distributed systems warm-start integrity checks.
Without this block, the cold AI proceeds on stale assumptions and acts on a
state that no longer exists.

Example from research:
```
- `git log --oneline -5` — expected: commit abc123 at top
- `pytest -k test_auth --no-header -q` — expected: 2 failed, 14 passed
- `cat docs/decisions/ADR-007.md | head -3` — expected: `# ADR-007: Use PostgreSQL`
```

---

### Block 10 — Confidence Flags

**Prompt instruction**: A table rating each block's information quality.

| Block | Confidence | Reason |
|---|---|---|
| 1 Frontmatter | ✅ | Git commands run at write time — ground truth |
| 2 Situation | ✅ | Direct observation from this session |
| 3 Background | ✅/⚠️ | ✅ if directly observed; ⚠️ if partly inferred |
| 4 User messages | ✅ | Verbatim — no inference |
| 5 Recent decisions | ✅/⚠️ | ✅ if directly observed; ⚠️ if reconstructed from memory |
| 6 Pending | ⚠️ | Agent's best read — verify with user if uncertain |
| 7 Critical files | ✅ | Confirmed by ls / git log |
| 8 Do Not Touch | ✅/❓ | ✅ if stated explicitly; ❓ if inferred from context |
| 9 Verification | ✅ | Commands are syntactically runnable (verified before writing) |
| 10 Confidence | ✅ | Meta-block — always rated by the agent authoring it |

**WHY** (research v1.1 §Confidence Flags, Don't Sleep On AI §Section 8):
"New AI has no conversation cache to judge which items are ground truth vs
guesses. Without confidence flags it treats everything as equally reliable."
(research v1.1 §1 Confidence Flags). Cold readers must not silently act on
❓-rated items — they must ask.

---

## 3 — The Five 共通核心原則

These 5 principles are the normative contract behind the 10 blocks.
Each has: name, one-line definition, one-line WHY, one short failure-mode example.

The first 4 are sourced from `AI Agent 對話接續綜論` §共通核心：四大原則.
The 5th (`technical-precision`) is L2-specific, added per the handoff v0.1 brief
(mirror-flip of recap's L3-specific `plain-language`).

---

### structured-schema

**Definition**: Use the fixed 10-block structure every time — no free-form summary.

**WHY**: The cold AI reader must find each piece of information in a predictable
location. A HANDOFF without fixed blocks forces the reader to search for
the verification commands, potentially missing them and proceeding on stale state.

**Failure mode**: Agent produces a narrative "here's what we were doing"
paragraph. The cold AI reads it, feels oriented, and starts working — then hits
a wrong-state assumption because Block 9 (Verification) was omitted.

---

### quote-not-paraphrase

**Definition**: On blocks 3 (Background), 4 (User messages), and 5 (Recent
decisions), reproduce original strings exactly — file paths, error messages,
command names, and user turns are quoted verbatim.

**WHY**: Every LLM pass introduces drift. "the auth module" becomes "session
management" across two summaries. Forcing direct quotes stops drift at the
source. Sourced from Anthropic's compaction prompt rule: "Directly quote key
phrases from the original text rather than paraphrasing."

**Failure mode**: Block 3 says "we decided to restructure the config."
The actual user constraint was "kill `config/base.py` and split into
`config/db.py` + `config/app.py` before the Monday deploy."
The paraphrase drops both the specific file names and the time constraint.

---

### all-user-messages

**Definition**: Block 4 lists every user turn verbatim — no LLM filtering.
The cold AI reader has no other source of user intent.

**WHY**: The user's intent is ground truth. "You cannot let LLM decide which
user messages are unimportant" (synthesis research §原則 3). At L3 (Recap),
the reader is the user themselves who lived through the session — verbatim dump
adds no signal. At L2 (HANDOFF), the cold reader has zero prior context; every
user message is the only record of constraints the user ever stated.

**Failure mode (L2)**: User said "also keep the old endpoint alive for 30 days."
HANDOFF agent filtered this turn as "minor clarification." The cold AI in the
next session deleted the old endpoint on day 3, breaking 6 client integrations.

---

### synthesis-check

**Definition**: The resume-mode SKILL.md instruction always ends with a directed
question asking the agent to summarize its understanding and wait for user
confirmation before continuing.

**WHY**: Sourced from I-PASS's Synthesis by receiver. Without a forced pause,
the cold AI resumes from its own assumption of alignment. The user's "yes" costs
3 seconds; the misalignment correction costs 30 minutes and a rollback.

**Failure mode**: Cold AI reads the HANDOFF, runs Verification, then immediately
begins writing code. User was planning to clarify one constraint first.
Agent wrote 200 lines based on the wrong assumption.

---

### technical-precision

**Definition**: HANDOFF output uses exact identifiers, full file paths, complete
error messages, precise command names. The reader is a cold AI agent (a tool),
not a human; precision is the value, plain-language softening adds ambiguity.
Acronyms expanded only when unambiguous.

**WHY**: Mirror-flip of recap's L3-specific `plain-language` principle
(audience-inheritance lesson). Recap is written for a human who needs 60-second
readability over completeness. HANDOFF is written for a cold AI that needs exact
state reconstruction — a vague description of a file path causes wrong-path
assumptions; an over-simplified description of an error causes the cold reader
to miss the critical detail that makes the error actionable.

**Failure mode (plain-language-creep — L2-specific anti-pattern)**: HANDOFF
Block 9 says: "Run the test suite to check things are working."
The cold AI runs `pytest` with no flags and 3 unrelated test failures from
unfinished work cause it to stop. The correct command was
`pytest dev-workflow/skills/handoff/scripts/ -v --tb=short`.
Plain-language softening ("run the test suite") removed the scope constraint
that made the command safe to execute.

---

## 4 — Good Example

A clean HANDOFF from an imaginary cross-session ship: implementing a Python
helper utility. Demonstrates all 10 blocks and all 5 principles.

---

```yaml
---
handoff_id: HANDOFF-007
created: 2026-05-28T22:15:00+08:00
trigger_type: voluntary
project: monkey-skills
chain:
  continues_from: HANDOFF-006.md
git:
  branch: feat/handoff-v0.1
  head: 7b09c92a4e1f83d0b2c5e9a1234567890abcdef0
  dirty: []
tools:
  claude_code: 2.1.14
---
```

### Situation

Implementing `dev-workflow:handoff` v0.1 skill. T1 (schema bundle RED test) and
T1 bundle commit are done. About to begin T2 (SKILL.md authoring). Branch:
`feat/handoff-v0.1` at commit `7b09c92a`.

### Background

- Decided to use pure prompt-template pattern (no Python scripts at v0.1) —
  agent uses native Bash/Write/Read tools; rejected Python scripts because
  recap v0.1 proved the pattern sufficient (0-LOC sister skill)
- Rejected splitting prepare/resume into two separate skills — one skill with
  two modes is simpler and matches softaworks CREATE MODE / RESUME MODE pattern
- Bundle path: `dev-workflow/skills/handoff/references/handoff-schema.md`
- Test path: `dev-workflow/skills/handoff/scripts/test_handoff_schema.py`
- Quote from plan: "RED: `PYTHONDONTWRITEBYTECODE=1 pytest dev-workflow/skills/handoff/scripts/test_handoff_schema.py::test_all_ten_blocks_and_five_principles_present -v` fails initially"

### All User Messages

1. "You are the SDD implementer for Task 1 of the HANDOFF v0.1 plan. Work under TDD iron law: RED test first, then GREEN bundle file, verify."
2. "Working directory: `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/explore-handoff-v0.1`"
3. "After GREEN, commit immediately — do not pause on git-memory-trailer reasoning"

### Recent Decisions

**Decision**: Ship 10 blocks (trim research v1.1's 14-block schema)
**WHY**: Smallest end state — covers cold-start needs without heavy sections
(How to Think / Architecture / Patterns / Interruption Snapshot) that need
dogfood evidence to prove they pull weight (same discipline as recap v0.1)
**Rejected alternative**: Full 14-block schema — over-engineering at v0.1;
forces agent to author sections that add no value for voluntary handoff

**Decision**: `technical-precision` as the 5th L2-specific principle
**WHY**: Mirror-flip of recap's `plain-language` — HANDOFF reader is a cold AI
tool, not a human; precision wins over readability
**Rejected alternative**: Keeping `plain-language` — wrong audience; an AI
reader is confused by vague descriptions, not helped by them

### Pending

- [ ] [P1] T2: Author `dev-workflow/skills/handoff/SKILL.md`
- [ ] [P2] T3: Tri-language READMEs (EN/JA/zh-TW)
- [ ] [P3] T4: Plugin manifest bump `dev-workflow` 2.10.0 → 2.11.0 + `handoff` keyword
- [ ] [P3] T4: Add `handoff` to `dev-workflow/.claude-plugin/plugin.json` keywords array

### Critical Files

| File path | Why it matters | Recently modified |
|---|---|---|
| `dev-workflow/skills/handoff/references/handoff-schema.md` | SSOT for 10-block schema — SKILL.md routes here | Yes — just created (T1 GREEN) |
| `dev-workflow/skills/handoff/scripts/test_handoff_schema.py` | Structural gate test for bundle | Yes — created in T1 RED commit `7b09c92a` |
| `dev-workflow/.claude-plugin/plugin.json` | Plugin manifest — needs version bump in T4 | No — untouched until T4 |

### Do Not Touch

- `dev-workflow/skills/handoff/` — only files in this directory may be edited;
  sister skills are READ-ONLY structural references per Anthropic skill-independence
- `dev-workflow/.claude-plugin/plugin.json` version until T4 — premature bump
  before T3 ships would create a misleading version that doesn't match content

### Verification Commands

- `git log --oneline -3` — expected: `7b09c92a` at or near top (T1 RED commit)
- `PYTHONDONTWRITEBYTECODE=1 pytest dev-workflow/skills/handoff/scripts/test_handoff_schema.py -v` — expected: 1 passed
- `ls dev-workflow/skills/handoff/references/` — expected: `handoff-schema.md` listed
- `cat dev-workflow/.claude-plugin/plugin.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['version'])"` — expected: `2.10.0`

### Confidence Flags

| Block | Confidence | Reason |
|---|---|---|
| 1 Frontmatter | ✅ | git commands run at write time |
| 2 Situation | ✅ | direct observation this session |
| 3 Background | ✅ | decisions directly made in this session |
| 4 User messages | ✅ | verbatim from dispatch prompt |
| 5 Recent decisions | ✅ | decisions made in this session, not inferred |
| 6 Pending | ⚠️ | based on plan tasks; T4 order may shift |
| 7 Critical files | ✅ | confirmed by ls + git log |
| 8 Do Not Touch | ✅ | explicit constraints from brief |
| 9 Verification | ✅ | commands tested before writing |
| 10 Confidence | ✅ | meta-block |

---

## 5 — Bad Example

The same scenario as the Good Example above, poorly executed.
Demonstrates **paraphrase-creep** + **plain-language-creep** + missing Verification commands.

---

```yaml
---
handoff_id: HANDOFF-007
created: 2026-05-28T22:15:00+08:00
trigger_type: voluntary
project: monkey-skills
---
```

> **structured-schema violation**: Missing `chain`, `git`, and `tools` fields.
> The cold AI cannot check whether the repo state matches — wrong-state
> assumption failure mode is now possible.

### Situation

Working on the handoff skill implementation. Made good progress today.

> **plain-language-creep**: "made good progress" is vague reassurance for a
> human reader, not state information for a cold AI. The cold AI needs:
> which task, which commit, which branch, what is left. Plain-language softening
> removed all three load-bearing identifiers.

### Background

- Chose to keep things simple without extra scripts
- Decided the fifth principle should be about accuracy for AI readers
- Files are in the right place

> **paraphrase-creep**: "keep things simple without extra scripts" paraphrases
> "pure prompt-template pattern (no Python scripts at v0.1) — agent uses native
> Bash/Write/Read tools." The actual constraint (Bash/Write/Read tools are the
> execution surface) is gone. "Files are in the right place" — which files?
> Which paths? The cold AI cannot act on this.
> **plain-language-creep**: "about accuracy for AI readers" over-simplifies
> `technical-precision` (exact identifiers, full file paths, complete error
> messages, precise command names). The cold AI cannot infer from "about
> accuracy" what style choices the principle mandates.

### All User Messages

The user gave instructions about TDD and commit discipline.

> **all-user-messages violation**: Block 4 must list every user turn verbatim.
> A paraphrase summary of user messages defeats the entire purpose of this block.
> "The user gave instructions about TDD" — the cold AI cannot recover the actual
> constraints (working directory, specific test command, no-trailer instruction)
> from this summary.

### Recent Decisions

We decided to trim the schema to 10 blocks to keep things manageable.

> **quote-not-paraphrase violation + plain-language-creep**: Missing the
> three-part format (Decision / WHY / Rejected alternative). The cold AI sees
> a conclusion but not why 10 was chosen over 14, not what the rejected
> alternative was, and not what "manageable" means in terms of the actual
> deferred blocks. Next session may re-evaluate adding the heavy sections.

### Pending

- Continue with the remaining tasks
- Do the README work
- Update the plugin file

> **plain-language-creep + technical-precision violation**: "remaining tasks"
> — which tasks? "README work" — which READMEs, which format, blocked by what?
> "Update the plugin file" — which file path, what change, what version bump?
> The cold AI cannot derive a concrete action plan from these descriptions.

### Critical Files

The main skill files and the test files are important.

> **technical-precision violation**: No paths, no "why it matters", no
> "recently modified" column. "The main skill files" does not resolve to a
> filesystem location. The cold AI will read the wrong files or ask the user
> to enumerate them — defeating the block's entire purpose.

### Do Not Touch

Be careful with the recap skill files.

> **technical-precision violation**: "be careful" is not a guardrail.
> The cold AI needs an exact path and an exact reason. "Be careful with the
> recap skill files" — careful how? The cold AI might still edit them,
> thinking "careful = read first, then edit."

*(Block 9 — Verification Commands: MISSING)*

> **structured-schema violation**: Omitting Block 9 entirely means the cold AI
> proceeds without verifying repo state. This is the highest-severity omission:
> the cold AI may act on a stale HANDOFF and modify files that have already
> changed since the handoff was written.

### Confidence Flags

Everything looks good, I'm fairly confident about most things.

> **structured-schema violation**: "Everything looks good" is not a per-block
> confidence table. The cold AI cannot identify which sections are ❓-rated
> and which are ✅. The prose obscures that Block 5 (Recent decisions) was
> partially reconstructed from memory (warranting ⚠️).
