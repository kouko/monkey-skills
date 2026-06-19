---
name: brief-before-asking
description: |
  Deliver a 6-block briefing (Mental Model → Situation → Why-fork → Options → My take → Open ends) before asking a complex engineering decision. Use proactively before non-trivial fork questions, or reactively on '看不懂' / 'in plain English' / 'ELI5'.
---

# Brief Before Asking

## Purpose

When an agent needs to involve the user in a **complex engineering decision**, the failure mode is rarely "agent said too little" or "agent said too much." It's almost always **"agent started at the wrong abstraction level."**

The agent defaults to implementation-level detail with embedded jargon. The user needs to start from system-level understanding with business semantics. Without a bridge, no amount of detail will land.

**brief-before-asking** enforces a 6-block briefing structure where **Mental Model leads** — the plain-English scaffolding that lets all subsequent technical content land.

## Three Trigger Modes

### Mode A — Proactive
**Triggered by**: Agent self-detects "I'm about to ask user about a non-trivial decision."

**Output**: Full 6-block briefing → ends with specific request.

**Mini-example** — index decision briefing (compressed):

> **Mental Model**: Our orders-list page is slow because the database scans every row instead of jumping to recent pending ones.
> **Situation**: `OrderRepository.findRecentPending` (orders.ts:142) p95 = 12s in prod; orders table 4.2M rows; only PK index; EXPLAIN shows Seq Scan.
> **Why-this-fork**: Deploy window tomorrow; index choice constrains 2 mirror tables we'll add Q2.
> **Options**: **A.** composite `(status, created_at DESC)` — 320 MB storage / read p95 → <100 ms / two-way door. **B.** cursor pagination on `created_at` — query rewrite ~40 lines / 0 storage / one-way door (API contract change).
> **My take**: Lean **A**. (1) Deploy pressure favors low-blast-radius; (2) read-heavy access pattern stable 6+ months per usage logs; (3) 320 MB storage cost is negligible vs API contract churn. **But if** the orders-list endpoint is being deprecated Q3 anyway, B's one-way-door cost vanishes — switch to B.
> **Open ends**: Q3 deprecation timeline confirmed? Dev DB storage ceiling? Your call on contract-stability vs storage trade-off.

### Mode B — Reactive on Question
**Triggered by user phrases** indicating they didn't understand the *question*:
- 「我不懂」「看不懂」「不理解」「什麼意思」「你在問什麼」
- 「沒頭沒尾」「資訊太少」「給我完整脈絡」
- "I don't understand" / "what?" / "clarify"

> Note: ambiguous phrases like "more context" / 「補充一下」default to **Mode C** (see Mode Detection Heuristics) — Mode C pauses, so it's the safer fallback when prior agent turn was a long explanation.

**Output**:
1. Bridge: 「回到我剛才問的『X』，補完整脈絡：」
2. Full 6-block briefing
3. **Re-ask the original question in specific, briefing-grounded form** (not the original ambiguous version)

### Mode C — Reactive on Explanation
**Triggered by user phrases** indicating they didn't follow the *explanation* (lost in jargon, missing prerequisites):
- 「我跟不上」「我跟丟了」「太多術語」「這些 term 不熟」
- 「能不能簡單講」「降低 level」「先講系統哪一塊」「我需要 mental model」
- 「我不知道你在說什麼」
- "I'm lost" / "back up" / "ELI5" / "in plain English" / "too much jargon" / "where in the system are we"

**Output (different from Mode B)**:
1. Bridge: 「讓我退一步，先建立 mental model。」
2. **Only** the Mental Model block + define jargon from prior turn
3. **Pause** and ask user where to drill: "A. technical details / B. options + my take / C. expand a specific term"
4. After user picks, continue with that block only

> **Why Mode C pauses**: The user already drowned in jargon once. Dumping 6 more blocks just drowns them again, even reordered. The fix is to land Mental Model first, then let the user pick the drill direction.

> **First Mode C of session — optional load**: `references/EXAMPLES.md` §Saga/Outbox demo shows a worked Mode C output (Mental Model + glossary + drill menu). Skip if you've already produced one this session.

## The 6-Block Briefing Structure

```
Mental Model     1-2 sentences plain-English: where in system + why it matters (NO jargon)
Situation        Technical state: code refs, metrics, investigation done
Why-this-fork    Trigger condition + constraint + what happens if not asked
Options          2-4 real options with depth (concrete diffs, not abstract pros/cons)
My take          Lean (A/B/C) + reasoning chain ≥3 steps + conditional reversal
Open ends        What I don't know / what would flip my answer / what needs your value call
```

### Block 1 — Mental Model (highest priority)

The block everyone wants to skip. The block that makes everything else land.

**Depth requirements**:
- 1–2 sentences, **no jargon**, **no code refs**
- Must answer:
  1. "Where in the system are we?" (locate on user's mental map, in business semantics)
  2. "Why does this matter from the user's perspective?" (business consequence, not implementation framing)
- If any **potentially unfamiliar term** is used: either define inline in 1 sentence, OR end the block with a flag list: "If any of these are unfamiliar, ask: [saga, outbox, offset commit]"

**Forbidden in Mental Model**:
- ❌ Code refs (those belong in Situation)
- ❌ Quantitative metrics (those belong in Situation)
- ❌ Undefined or unflagged jargon
- ❌ Abstract framings like "we have an issue" with no grounding
- ❌ Using service names or pattern names as if they were explanations

**Contrast**:

❌ Bad Mental Model:
> "OrderService has a race condition under high concurrency and needs idempotency."
> (Three jargon terms, zero plain English, no system location.)

✅ Good Mental Model:
> "This is the async 'deduct inventory after checkout' flow: once an order is written, a message is sent to InventoryService to deduct stock. Problem: the same message sometimes gets processed twice, causing the same order to deduct stock twice (oversells)."
> (Business semantics, no jargon, consequence is graspable.)

### Block 2 — Situation

**Depth requirements**:
- ≥1 **code ref** (filename:lineno or function name)
- ≥1 **quantitative metric** (if truly unmeasured, say "not measured")
- What **investigation** the agent performed

**Forbidden**: "looks complex" / "seems slow" / "doesn't feel right"

### Block 3 — Why this is a fork

**Depth requirements**:
- **Trigger condition** — why ask now (not last week, not next week)
- **Constraint** — what makes this a fork (not something agent can decide alone)
- **What happens if not asked** — cost of agent deciding unilaterally

**Forbidden**: "want to confirm with you" / "I think we should change something"

### Block 4 — Options

**Each option requires**:
1. **Concrete approach** (at code-review level of specificity)
2. **Quantitative impact** (files affected, lines, perf numbers, storage, cost)
3. **Trade-off** (the real cost — not just upside)
4. **Reversibility** (two-way door vs one-way door)
5. **Downstream implications** (effect on other systems, teams, processes)

- **Minimum 2, maximum 4** options
- **Equal-depth treatment** — banned: A in 5 lines, B in 1 line (fake balance)
- **Forbidden**: abstract adjectives like "simpler" / "modern" / "industry standard" / "best practice"

### Block 5 — My take

**Required**:
- **Explicit lean** (A / B / C) — never "either works" or "up to you"
- **Reasoning chain** ≥3 causal steps
- **Conditional reversal** — "but if X condition holds, I'd switch to Y"

**Forbidden**:
- ❌ "I have no preference" (agent read the code; pretending neutrality is a lie)
- ❌ "Both are good"
- ❌ "Up to you" / "your call" (offloading thinking)
- ❌ "I think A is good, OK to go with A?" (this is asking permission, not stating a lean)

### Block 6 — Open ends

**Three categories**:
1. **Context the agent lacks** (info the user holds)
2. **Future conditions that would flip the answer** (e.g., "if read pattern changes in 6 months")
3. **Value judgments needing the user** (e.g., "you prefer latency or storage?")

**Forbidden**:
- ❌ "Need more context" (vague — be specific)
- ❌ Fake open ends (questions agent could answer itself)
- ❌ "Above is for reference only" (disclaimer fluff)

## Anti-Patterns (cross-block / cross-mode)

Per-block forbidden items live in each block's section above. The patterns below are failure modes that span blocks or modes:

- ❌ **Skipping Mental Model and jumping straight to Situation** — kills the abstraction bridge (most fatal)
- ❌ Zero-context yes/no: "Should we proceed?" / "OK?" — no block carries the load
- ❌ Conclusion-first with no reasoning: "I recommend Redis, OK?" — collapses 6 blocks into 1 ask
- ❌ Multiple forks bundled into one briefing — one fork per briefing
- ❌ **Mode C trigger but agent dumps full 6 blocks instead of pausing** — re-drowns the user

## When NOT to Use

- **Trivial decisions** (private-code naming, formatting, log level, ≤5 lines, reversible, no public-API surface change) → just do it, note the choice
- **Pure factual queries** ("what is X") → just answer
- Already in cross-team architecture review mode → escalate to a heavier consulting-style framework (Minto SCQA / formal RFC; see `references/DESIGN.md` for escalation criteria)

## Escape Hatches

- User says **"just decide" / "skip briefing" / "don't ask"** → trivial-ize, do it, note the choice in commit/response
- User says **"too long" / "shorter"** → keep all 6 blocks but compress each; never drop Mental Model
- User says **"expand C" / "more detail on B"** → deepen the named block in-place
- User says **"give me the full analysis" / "go heavy"** → escalate to heavyweight cross-team review framework (Minto SCQA / RFC); see `references/DESIGN.md`

## Mode Detection Heuristics

When deciding between Mode B and Mode C:

| Signal | Mode |
|--------|------|
| User asks what the **question** means | B |
| User asks what the **explanation** means | C |
| User says "什麼意思" right after agent's short question | B |
| User says "跟不上" / "太多術語" after agent's long explanation | C |
| User says ambiguous "more context" / 「補充」after agent's **long explanation** | C |
| User says ambiguous "more context" / 「補充」after agent's **short question** | B |
| Agent just delivered ≥3 sentences of dense technical content + user signals confusion | C |
| Agent's previous turn was a short ambiguous question + user signals confusion | B |
| Still ambiguous after checking prior turn → default to **C** (safer; Mode C pauses) | C |

## See Also

### Runtime references (conditional load)

- **`references/EXAMPLES.md`** — concrete bad-vs-good examples for race conditions, query/index decisions, saga/outbox.
  - **CONDITIONAL load** on first Mode C invocation per session (worked Mode C output format).
  - **CONDITIONAL load** when debugging anti-pattern catches (jargon-in-MM / fake-neutrality / unbalanced-options).

### Author-only — do NOT load at runtime

- **`references/DESIGN.md`** — design rationale + 4-iteration history. Load only when redesigning this skill.
- **`references/IMPLEMENTATION-CHECKLIST.md`** — author phase checklist. Load only when working on this skill itself.

### Sibling skills

- **`dev-workflow:complexity-critique`** — one-shot deletion-first gate (orthogonal — critique not briefing)
- **`skill-dev-toolkit:skill-creator-advance`** — iterate this skill via test prompts
- **`superpowers:brainstorming`** — task-start ideation (brief-before-asking is for task-progress decisions)

## Core Mindset

> **Briefing depth = decision speed.** The value is the abstraction bridge (Mental Model) plus the depth rules that force agent to surface what it already knows — not structure for its own sake.
