# Brief Before Asking — Design Rationale

This document captures **why** the skill is designed this way. It exists to prevent the next iteration from reverting to mistakes already made.

## Origin

The skill emerged from a Grok conversation (2026-05-07 ~ 05-09) discussing "how to explain a problem well" frameworks (SCQA, PREP, STAR, Pyramid Principle, MECE). The user then asked specifically: how to make Claude Code agents better at explaining problems so the user can decide quickly.

The design went through **4 iterations** before landing on the current 6-block + 3-mode structure. Each iteration corrected a different failure mode.

The full research narrative lives in the user's Obsidian vault:
- `research/2026-05-13 SCQA 框架與 LLM·人類雙向偏見防禦——技術決策溝通框架深度研究.md` (v1, scope-corrected)
- `research/2026-05-13 briefing-first Skill 設計——複雜工程問題的結構化提問前簡報.md` (v4, current; file in vault retains original draft name)

## Iteration History (must read before redesigning)

### Iteration 1 — SCQA + MECE + dual bias defense (over-engineered)

**Design**: Stack SCQA framework + MECE check + LLM bias mitigation + human bias alert + 8 procedural steps.

**Why it failed**: Ceremony dominated value. Each invocation produced ~1500 tokens of structural overhead before reaching actual content. The "framework stack" felt rigorous but added decoration, not signal.

**Root cause of misdirection**: Followed the Grok conversation's framework-additive pattern (SCQA → +PREP → +STAR → +Pyramid → +MECE → +Bias Defense). Assumed "more frameworks = more complete." Wrong — more frameworks just bury the actual content beneath ritual.

**Lesson kept**: Some structural rigor IS needed for complex decisions. Don't go back to free-form prose.
**Lesson rejected**: Don't stack frameworks. One coherent structure beats many overlapping ones.

### Iteration 2 — MVQ + stakes calibration (over-corrected, deleted)

**Design**: 5-field "Minimum Viable Question" (Where / Fork / Options / Default / Escape) + 4-tier stakes calibration (trivial / low / mid / high). Lightweight default, escalate to SCQA on high stakes.

**Why it failed**: **Misread the user's actual scenario**. Assumed the pain was "agent asks too many small questions about trivial decisions." Designed for high-frequency low-stakes forks.

But the user's real pain is **complex problems with insufficient explanation** — high-stakes situations where the agent's question is the right question, just under-explained. MVQ's 5 short fields cannot carry that load.

**Lesson kept**: Scannable structure matters. Stakes calibration is real (don't apply brief-before-asking to trivial decisions).
**Lesson rejected**: "Default for everything" assumed simple forks. Real complex forks don't have a clean default — they have real trade-offs.

### Iteration 3 — 5-block briefing (Situation-first, missed mental model)

**Design**: 5 blocks (Situation / Why-this-fork / Options / My take / Open ends) with strict depth requirements (code refs, quantification, ban abstract adjectives, force explicit lean).

**Why it failed**: **Started at the wrong abstraction level**. Situation block required code refs and quantification — but those land only if the user already knows where in the system those refs live and what those numbers measure.

User clarified: their actual experience is "agent explains a lot, but I still don't follow because I lack prerequisite context." More technical depth doesn't fix that — it deepens the gap.

**Lesson kept**: Depth rules per block are the core value (anti-pattern: skipping depth in favor of structure-talk).
**Lesson rejected**: Starting from Situation. Situation needs prerequisites the user may not have.

### Iteration 4 (current) — 6-block + 3 modes + Mental Model First

**Design**:
- **6 blocks** with Mental Model leading: plain-English abstraction bridge before technical content
- **3 modes**: Proactive (A), Reactive on Question (B), Reactive on Explanation (C)
- **Mode C is structurally different** — only delivers Mental Model + jargon defs, then pauses for user-directed drill

**Why it works (so far)**:
- Mental Model addresses the abstraction-level mismatch directly
- Depth rules (from iteration 3) are preserved for blocks 2-6
- Mode C closes the "long explanation but still confused" failure that iterations 1-3 all missed
- 3 modes acknowledge that **how** to deliver depends on the failure mode being addressed

**Open questions** (see IMPLEMENTATION-CHECKLIST.md):
- Mode B vs Mode C disambiguation when user signal is ambiguous
- Whether Mode C should ever auto-expand all blocks without user direction
- How agent should know its own previous turn was "long explanation" vs "short question"

## Key Insight Per Iteration

| Iteration | Insight kept | Insight added |
|-----------|-------------|---------------|
| 1 | Complex problems need structure | (none net positive) |
| 2 | Stakes calibration is real | Scannable structure matters |
| 3 | Depth rules per block | Force agent to surface what it already knows |
| 4 | **Abstraction-level matching > word count** | **Mental Model First; Mode C pauses** |

## Why This Design Beats Alternatives

### vs SCQA (Minto Pyramid)

SCQA opens with Situation → Complication → Question → Answer. Strong for consulting reports. Weak for engineering decisions where the user may not have the prerequisite context to parse Situation.

**brief-before-asking prepends Mental Model** — plain-English abstraction bridge that makes Situation land. Otherwise structurally similar.

### vs PREP / STAR

PREP and STAR are answer-side frameworks. They're good for delivering a conclusion, not for opening a decision. brief-before-asking is decision-opening.

### vs MECE check

MECE is useful but ceremonial when applied to every decision. It assumes the problem space is known and partitionable. Many real engineering forks have fuzzy boundaries where MECE produces fake partitions.

brief-before-asking folds MECE-like rigor into Options (forced equal-depth, forced concrete diffs) without the ceremony of explicit MECE verification.

### vs Always-on Anti-Bias Checks (Iteration 1)

Iteration 1 stacked LLM-bias-defense and human-bias-alert blocks on every output. The result was performative objectivity — agent used "neutral" language to mask its preference instead of stating it openly.

**brief-before-asking requires Agent to state its lean explicitly** in the "My take" block, with conditional reversal. This is more honest than fake neutrality and gives the user a clean target to push back on.

### vs MVQ (Iteration 2)

MVQ's "Default" field offloads thinking to the agent. Works for trivial decisions; fails for genuinely complex ones where a "default" would be misleading.

brief-before-asking replaces "Default" with "My take + Open ends": agent commits a position WITH reasoning AND surfaces what would change its mind. User can confirm, push back, or supply missing context — three responses, all faster than reading code from scratch.

## Open Design Questions

1. **Mode disambiguation**: When user says "more context," is that Mode B (didn't understand question) or Mode C (didn't understand explanation)? Current heuristic: default to Mode C (safer because Mode C pauses).

2. **Mode A self-detection accuracy**: Can agent reliably self-detect "I'm about to ask a complex question"? Risk: agent self-judges that its question is clear when it isn't. Mitigation: Mode B/C exists as user-side safety valve.

3. **Mental Model length**: 1-2 sentences feels right for code-level decisions. For larger architecture forks, may need 3-4 sentences. Current rule keeps it short to force agent to compress; may need calibration.

4. **Jargon flagging vs inline definition**: When does each strategy apply? Current rule: inline if term is essential to the briefing, flag-list if term is incidental. May need refinement.

5. **Glossary / decision-history accumulation**: Across sessions, the same project may produce many briefings. A potential v2 feature is cross-session memory ("we already established the mental model for OrderService earlier").

6. **Interaction with `scqa-decision`-equivalent heavyweight mode**: When user explicitly requests "full analysis" or topic crosses team boundaries, brief-before-asking should escalate. Current rule: defer to "see scqa-decision-style references" but no concrete escalation hook is implemented yet.

## Non-Goals (explicit)

- brief-before-asking is **not** a brainstorming or ideation skill. Use `superpowers:brainstorming` for task-start ideation.
- brief-before-asking is **not** a verification skill. Use `superpowers:verification-before-completion` for task-finish.
- brief-before-asking is **not** a critique skill for proposals. Use `dev-workflow:proposal-critique` / `complexity-critique`.
- brief-before-asking does **not** enforce MECE rigor on Options. It enforces concrete diffs + equal depth, which is the practical equivalent without the ceremony.
- brief-before-asking does **not** police bias defense ceremony. It enforces agent stating its lean openly, which is the honesty mode of bias handling.

## Maintenance Heuristics

- If a future iteration adds blocks, ask: does this serve abstraction-level matching, or is it ceremony?
- If a future iteration removes Mental Model, refer to Iteration 3's failure.
- If a future iteration drops Mode C, refer to the user's stated pain ("explained a lot but I lack prerequisites").
- If a future iteration drops "My take" lean requirement, refer to Iteration 1's failure (performative objectivity).
