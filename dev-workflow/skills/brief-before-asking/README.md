# Brief Before Asking

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> A 6-block structured briefing the agent delivers **before** (or in
> direct response to) any non-trivial engineering decision question.
> Mental Model leads — a plain-English abstraction bridge that lands
> before any code reference or metric. The user can then read,
> push back, or confirm in seconds instead of reverse-engineering
> the agent's question from scratch.

A proactively-triggered **agent-side skill**: when Claude is about
to ask the user about a complex engineering decision (race
condition, perf bottleneck, refactor direction, tech selection, bug
root cause), this skill enforces a 6-block briefing structure
instead of letting Claude default to either zero-context yes/no
("OK to proceed?") or jargon-first technical dump. Also fires
reactively when the user signals confusion about a question
(Mode B) or about an explanation (Mode C).

This README is for humans reading the skill on GitHub. The
operational file Claude actually loads is [`SKILL.md`](SKILL.md).

---

## Why does this skill exist?

The recurring failure mode is **not** "agent said too little" or
"agent said too much." It is almost always **agent started at the
wrong abstraction level**. Claude defaults to implementation-level
detail with embedded jargon. The user needs to start from
system-level understanding in business semantics. Without a bridge,
no amount of detail will land — adding more detail only widens the
gap.

The current 6-block + 3-mode design landed after **4 iterations**.
Each prior iteration corrected a different failure mode but missed
the abstraction-bridge problem. See
[`references/DESIGN.md`](references/DESIGN.md) for the full
narrative. The short version:

| Iteration | What was tried | Why it failed |
|---|---|---|
| **1** | Stack SCQA + MECE + LLM-bias defense + human-bias alert (8 procedural steps) | Ceremony dominated value. ~1500 tokens of structural overhead before reaching content. "Framework stack" felt rigorous; produced ritual. |
| **2** | 5-field "Minimum Viable Question" (Where / Fork / Options / Default / Escape) + 4-tier stakes calibration | Misread the actual pain. Designed for high-frequency low-stakes forks. Real pain is genuinely complex forks with no clean default. |
| **3** | 5-block briefing (Situation / Why-this-fork / Options / My take / Open ends) with strict depth rules | Started at the wrong abstraction level. Situation block required code refs and metrics, but those land only if the user already knows where in the system those refs live. |
| **4** (current) | 6 blocks with **Mental Model** leading + 3 trigger modes (Proactive / Reactive-on-Question / Reactive-on-Explanation) | Mental Model addresses the abstraction-level mismatch directly. Depth rules from iteration 3 preserved for blocks 2-6. Mode C closes the "long explanation but still confused" failure that iterations 1-3 all missed. |

The core insight, late-arriving: **abstraction-level matching
beats word count**. A 2-sentence Mental Model in plain English
unblocks 200 lines of technical detail. Without it, the 200 lines
just deepen the confusion.

---

## How does it work?

### The 3 trigger modes

| Mode | Trigger | Output shape |
|---|---|---|
| **A — Proactive** | Agent self-detects "I'm about to ask user about a non-trivial decision" | Full 6-block briefing → ends with specific request |
| **B — Reactive on Question** | User signals they didn't understand the *question* (「我不懂」「沒頭沒尾」"clarify") | Bridge → full 6-block briefing → **re-ask the original question in specific, briefing-grounded form** |
| **C — Reactive on Explanation** | User signals they didn't follow the *explanation* (「跟不上」「太多術語」"ELI5" "in plain English") | Bridge → **only** the Mental Model block + define jargon from prior turn → **pause** and ask user where to drill |

Mode C is structurally different from Mode B. The user already
drowned in jargon once — dumping 6 more blocks just drowns them
again, even reordered. The fix is to land Mental Model first,
then let the user pick the drill direction.

### The 6 blocks

```
Mental Model     1-2 sentences plain-English: where in system + why it matters (NO jargon)
Situation        Technical state: code refs, metrics, investigation done
Why-this-fork    Trigger condition + constraint + what happens if not asked
Options          2-4 real options with depth (concrete diffs, not abstract pros/cons)
My take          Lean (A/B/C) + reasoning chain ≥3 steps + conditional reversal
Open ends        What I don't know / what would flip my answer / what needs your value call
```

Each block has its own depth requirements and forbidden patterns.
The full ruleset lives in [`SKILL.md`](SKILL.md); the short version:

- **Mental Model** — no code refs, no metrics, no undefined jargon. Must answer "where in the system are we?" in business semantics and "why does this matter from the user's perspective?". Inline-define or flag any term the user might not know.
- **Situation** — ≥1 code ref (filename:lineno), ≥1 quantitative metric, what investigation was done. Banned: "looks complex" / "seems slow".
- **Why-this-fork** — trigger (why ask now), constraint (what makes this a fork agent can't decide alone), cost if not asked.
- **Options** — minimum 2, maximum 4, equal-depth treatment (no "A in 5 lines, B in 1 line"). Each option needs concrete approach, quantitative impact, trade-off, reversibility (two-way vs one-way door), downstream implications. Banned: "simpler" / "modern" / "industry standard".
- **My take** — explicit lean (A / B / C), reasoning chain ≥3 causal steps, conditional reversal ("but if X holds, I'd switch to Y"). Banned: "either works" / "your call" / "no preference" (agent read the code; pretending neutrality is a lie).
- **Open ends** — context agent lacks (info user holds), conditions that would flip the answer, value judgments needing the user. Banned: "need more context" (vague), fake questions agent could answer itself, disclaimer fluff.

### Mental Model First (the load-bearing insight)

The block everyone wants to skip. The block that makes everything
else land. The "before" failure mode looks like:

> ❌ "OrderService has a race condition under high concurrency and needs idempotency."
> (Three jargon terms, zero plain English, no system location.)

The "after" looks like:

> ✅ "This is the async 'deduct inventory after checkout' flow: once an order is written, a message is sent to InventoryService to deduct stock. Problem: the same message sometimes gets processed twice, causing the same order to deduct stock twice (oversells)."
> (Business semantics, no jargon, consequence is graspable.)

The agent still has to talk about the race condition, the saga
pattern, and the idempotency key — but those land in Situation /
Options / My take, after the user holds the map.

---

## A worked example (Mode A, compressed)

**Setup**: agent is about to ask the user about an index-vs-pagination
refactor on a slow orders-list endpoint.

> **Mental Model**: Our orders-list page is slow because the database scans every row instead of jumping to recent pending ones.
>
> **Situation**: `OrderRepository.findRecentPending` (orders.ts:142) p95 = 12s in prod; orders table 4.2M rows; only PK index; `EXPLAIN` shows Seq Scan.
>
> **Why-this-fork**: Deploy window tomorrow; index choice constrains 2 mirror tables we'll add Q2.
>
> **Options**:
> - **A.** Composite index `(status, created_at DESC)` — 320 MB storage / read p95 → <100 ms / two-way door.
> - **B.** Cursor pagination on `created_at` — query rewrite ~40 lines / 0 storage / one-way door (API contract change).
>
> **My take**: Lean **A**. (1) Deploy pressure favors low-blast-radius; (2) read-heavy access pattern stable 6+ months per usage logs; (3) 320 MB storage cost is negligible vs API contract churn. **But if** the orders-list endpoint is being deprecated Q3 anyway, B's one-way-door cost vanishes — switch to B.
>
> **Open ends**: Q3 deprecation timeline confirmed? Dev DB storage ceiling? Your call on contract-stability vs storage trade-off.

The user can now (a) confirm A, (b) supply the deprecation timeline
and flip to B, or (c) push back on a specific number — three
responses, all faster than reverse-engineering the question.

A worked Mode C example (saga / outbox, ELI5) lives in
[`references/EXAMPLES.md`](references/EXAMPLES.md).

---

## When should you use it?

### Triggers (agent-side)

- **Mode A — Proactive**: agent is about to ask user about a
  non-trivial decision: race condition, perf bottleneck, service
  boundary change, refactor direction, tech selection, bug root
  cause.
- **Mode B — Reactive on Question**: user says 「我不懂」「看不懂」
  「不理解」「什麼意思」「你在問什麼」「沒頭沒尾」「資訊太少」
  「給我完整脈絡」 / "I don't understand" / "clarify" / "what?".
- **Mode C — Reactive on Explanation**: user says 「我跟不上」
  「太多術語」「能不能簡單講」「降低 level」「我需要 mental
  model」 / "I'm lost" / "ELI5" / "in plain English" / "too much
  jargon" / "where in the system are we".

Ambiguous "more context" / 「補充一下」 after a long explanation
defaults to **Mode C** (safer, because Mode C pauses).

### Don't use when…

- **Trivial decisions** — private-code naming, formatting, log
  level, ≤5 lines, reversible, no public-API surface change. Just
  do it; note the choice.
- **Pure factual queries** — "what is X" / 「X 是什麼」. Just
  answer.
- **User explicitly said "just decide, don't ask"** — trivial-ize,
  do it, note the choice in commit/response.
- **Already in cross-team architecture review mode** — escalate to
  a heavier framework (Minto SCQA / formal RFC). brief-before-asking
  is the **daily middleweight** for individual complex decisions,
  not the heavyweight for cross-team consultation.

---

## Differentiation

### vs SCQA / Minto Pyramid

SCQA opens with Situation → Complication → Question → Answer.
Strong for consulting reports. Weak for engineering decisions where
the user may not have the prerequisite context to parse Situation.
**brief-before-asking prepends Mental Model** — plain-English
abstraction bridge that makes Situation land. Otherwise
structurally similar. SCQA-style heavyweight review still has its
place; brief-before-asking is the middleweight default and escalates
to SCQA on user request ("give me the full analysis").

### vs simple "ask before doing"

Plain "ask before doing" produces zero-context yes/no questions
("Should we proceed?" / "OK to refactor?"). The user is forced to
reverse-engineer the agent's reasoning before answering. The 6-block
structure forces agent to surface what it already knows — the user
gets a briefing-grounded ask, not a guessing game.

### vs `superpowers:brainstorming`

Brainstorming is **task-start ideation** — open the option space
when you don't know what to build. brief-before-asking is
**task-progress decision** — narrow the option space when you've
done the work and need a fork resolution. Different phases, different
shapes.

### vs `dev-workflow:proposal-critique`

Proposal-critique is a one-shot KEEP / DEFER / DROP triage on an
existing list or plan. brief-before-asking opens a decision; it
doesn't critique one. They compose: agent uses brief-before-asking
to surface a decision, user uses proposal-critique on the resulting
options list if it's too long.

---

## Anti-patterns

Cross-block / cross-mode failure modes (per-block anti-patterns
live in [`SKILL.md`](SKILL.md) under each block):

- **Skipping Mental Model and jumping straight to Situation** —
  kills the abstraction bridge. Most fatal failure mode.
- **Zero-context yes/no**: "Should we proceed?" / "OK?" — no block
  carries the load.
- **Conclusion-first with no reasoning**: "I recommend Redis, OK?"
  — collapses 6 blocks into one ask.
- **Multiple forks bundled into one briefing** — one fork per
  briefing; if there are three forks, deliver three briefings.
- **Mode C trigger but agent dumps full 6 blocks instead of
  pausing** — re-drowns the user. Mode C is structurally different
  on purpose.
- **Performative objectivity**: "Both options have merit" — agent
  read the code and has a lean; pretending neutrality is a lie.
  The "My take" block exists precisely to force honesty.

---

## How does it relate to other skills?

- **`dev-workflow:complexity-critique`** — one-shot deletion-first
  gate. Orthogonal — critique on a single proposal, not a briefing
  on a decision.
- **`dev-workflow:proposal-critique`** — triage of an existing
  list / plan. Composes downstream of brief-before-asking when the
  resulting Options list is itself too long.
- **`skill-dev-toolkit:skill-creator-advance`** — used to iterate this
  skill (test-prompts.json + eval loop).
- **`superpowers:brainstorming`** — task-start ideation;
  brief-before-asking is task-progress decision.
- **`superpowers:verification-before-completion`** — task-finish
  evidence; brief-before-asking is task-progress decision.

---

## Pre-shipped — this is v1.0 draft

| Phase | Status |
|---|---|
| **Phase 1 — Design** | Complete. 4 iterations documented in [`references/DESIGN.md`](references/DESIGN.md). |
| **Phase 2 — SKILL.md authoring** | Complete. 6-block + 3-mode structure, depth rules per block, Mode Detection Heuristics table. |
| **Phase 3 — Description optimization** | **Pending.** Will run through `skill-creator-advance` description-A/B loop to tune router triggering accuracy. |
| **Phase 6 — Worked examples + tests** | Complete. [`references/EXAMPLES.md`](references/EXAMPLES.md), [`test-prompts.json`](test-prompts.json), [`trigger-eval.json`](trigger-eval.json). |
| **Phase 7 — Output-quality A/B** | **Pending.** Will run through `skill-dev-toolkit:skill-tuning` once Phase 3 is done. Mode A briefing style is taste-sensitive (terseness, lean assertiveness, jargon-flagging strategy) — pure rule-following won't surface the best version. |

The skill is shippable as v1.0 and improves under feedback. Mode C
in particular is the youngest design surface; expect refinement
once it sees real-session use.

---

## Files

```
brief-before-asking/
├── README.md           ← English (this file)
├── README.ja.md        ← 日本語
├── README.zh-TW.md     ← 繁體中文
├── SKILL.md            ← operational file (for Claude)
├── test-prompts.json   ← Phase 6 — Mode A/B/C eval prompts
├── trigger-eval.json   ← router-trigger accuracy probes
└── references/
    ├── DESIGN.md                  ← 4-iteration design rationale (author-only)
    ├── EXAMPLES.md                ← worked bad-vs-good per block (conditional runtime load)
    └── IMPLEMENTATION-CHECKLIST.md ← author phase checklist (author-only)
```

---

## Bottom line

```
Briefing depth = decision speed.
The value is the abstraction bridge (Mental Model) plus the depth
rules that force agent to surface what it already knows — not
structure for its own sake.
```
