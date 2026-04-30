# Protocol: audit-mode — Diagnose an existing cascade map

> Loaded by SKILL.md orchestrator when the user provides an **existing
> cascade artifact** (org Primary WIG → Battles → Team WIGs) and asks
> for diagnostic / revision, OR when the user provides a cascade map
> plus sub-leader / sub-team critique ("imposed on us", "doesn't ladder
> up", "we don't own this", 「押し付け」, 「硬塞」, 「不接受」). Agent
> voice = **consultant-from-artifact**: structured per-rule verdict
> table, evidence-cited, terse. Distinct from coach-mode, which builds
> a cascade from scratch via Socratic dialogue. Audit-mode assumes the
> user is already 4DX-committed (no fit-check) and stays inside D1
> cascade only (no lead / scoreboard / cadence audit — route to
> `4dx-audit` for cross-layer).

## R — Reading

> Rule 3. Leaders of leaders can veto, but not dictate.
>
> — McChesney/Covey/Huling, *4DX* 2nd ed., Ch. 7

> The battles you choose must win the war.
>
> — *Ibid.*, Ch. 7 (Rule 2)

## I — Interpretation

The user has a cascade already drafted (often running) and wants the
agent to *diagnose against the Ch 7 four rules*, not coach the build
from zero. Three things differ from coach-mode:

1. **Posture is consultant-from-artifact, not coach-build.** Output is
   a per-rule verdict table with PASS / FAIL / PARTIAL + evidence cite,
   followed by per-rule revision recommendations and conversation
   scripts for re-negotiating with sub-leaders — not a Socratic 10-step
   walk.
2. **Sub-leader critique is a translation problem.** "Imposed on us"
   ≈ Rule 3 violation. "Doesn't ladder up" ≈ Rule 2 violation. "Have
   to do many things" ≈ Rule 1 violation. "Can't tell whether we won"
   ≈ Rule 4 violation. The audit translates everyday complaint into
   the rule the stakeholder is implicitly invoking, then issues
   per-rule verdicts.
3. **Targets-vs-Plans + Battles-count are first-class checks.** Beyond
   the four rules, the audit also runs (a) a Targets-not-Plans check —
   are Team WIGs target-shaped (X→Y→When result) or plan-shaped (action
   list)? — and (b) a Battles-count check — ≤3 Battles? if 5+, narrowing
   incomplete.

Voice contrast vs coach-mode: coach-mode extracts a cascade through
Socratic question. Audit-mode reads a finished cascade and returns a
structured verdict + per-rule revisions + conversation scripts for sub-
leader re-negotiation.

## A1 — Past Application

### Case 1: Sydney accounting firm initial cascade — too-many-Battles audit (Ch 7)
- Firm initially proposed 9 Battle WIGs across 2 teams to chase "total revenue". Run as audit input:
  - **Battles-count check**: FAIL — 9 Battles, far above the ≤3 typical landing zone.
  - **Rule 2 (Battles win the war)**: PARTIAL — Battles existed, but "total revenue" was the war, not a battle, so the cascade was inverted.
  - **Rule 1 (one WIG per individual)**: FAIL — with only 2 teams to absorb 9 Battles, individuals would carry multiple.
- Recommended revision: demote "total revenue" to a strategy line; re-pick a narrower Primary WIG (advisory services); collapse 9 Battles into 0 intermediate Battles and cascade directly to 2 Team WIGs (sales: new-account advisory; delivery: existing-account advisory). Lesson: an audit surfaces three rule failures in one minute; the same diagnosis via coach-mode would take an hour.

### Case 2: Hypothetical retailer cascade — "imposed" complaint audit (Ch 7-derived)
- Region leader hands district leaders fixed From-X-to-Y-by-When numbers; district leaders complain "these were imposed, we don't own them". Run as audit input:
  - **Rule 3 (veto, don't dictate)**: FAIL — sub-leaders did not propose; leader-of-leaders authored the numbers.
  - **Rule 4 (X→Y→When grammar)**: PASS — numbers are well-formed.
  - **Targets-not-Plans**: PASS — outcome-shaped, not action-list.
- Recommended revision: keep the Battle structure; have each district leader re-propose their own X→Y→When numbers. Region leader retains veto, may "ask for adjustments", but does not author. Conversation script: *"I'm pulling back the numbers. Each of you, propose your district's From-X-to-Y-by-When for the same three Battles. I may push back if the math doesn't close, but I won't author yours."* Lesson: Rule 3 violations are diagnosable from the artifact pattern (uniform numbers across units) plus the verbatim complaint, even before talking to sub-leaders.

## A2 — Future Trigger

### When will the leader need this protocol?

1. Leader pastes a cascade map (Primary WIG → Battles → Team WIGs) and asks "is this right?" / "what's wrong?" / "diagnose" / "audit".
2. Leader provides a cascade map plus sub-leader / sub-team complaints ("imposed", "doesn't ladder", "we don't own this", "we have to do many things") and wants the complaints translated to 4DX rules.
3. Leader has inherited a cascade from a predecessor and wants a 4DX-rule diagnostic before deciding what to revise.
4. Cascade is running but not producing engagement — sub-leaders going through motions; leader wants to know which rule is breaking before re-negotiating.

### Language signals (multilingual — match any)

- EN: "Audit our cascade — sub-leaders complaining", "Boss says cascade is wrong, here's the map", "Diagnose this cascade", "Sub-team says the WIG was imposed", "Here's our cascade map — what's broken?"
- JP: 「うちの cascade を診断して、下のリーダー達が文句言ってる」「cascade map 見て何がダメか」「cascade を audit して、現場が押し付けって言ってる」「cascade map の診断お願い」
- zh-TW: 「幫我看 cascade 哪裡有問題，下面的 leader 都在抱怨」「上面說 cascade 不對，這是 map」「cascade map 給你看，下面說是硬塞下來的」「幫我診斷 cascade」

### Distinction from neighboring protocols / skills

- vs. `coach-mode.md`: that protocol builds from scratch with Socratic dialogue; this protocol diagnoses an existing artifact with verdict tables.
- vs. `4dx-d1-wig-formulation` audit-mode: that audits a *single Team WIG* (or candidate list); this audits the *full cascade map* (Primary → Battles → N Team WIGs). If only one WIG is being audited, route there.
- vs. `4dx-audit`: that runs full-stack diagnosis (WIG / lead / scoreboard / cadence / substrate). This protocol is D1-cascade-only.
- vs. `using-four-dx-coach`: that handles OKR-cascade audit, hoshin catchball, balanced-scorecard cascade audit. This protocol assumes 4DX is committed.

## E — Execution

When this protocol activates, the agent runs a structured cascade audit. **Do not Socratically rebuild the cascade — diagnose, then recommend.**

1. **Read the cascade artifact(s).**
   - Extract the org Primary WIG (X / Y / When), each Battle (X / Y / When), and each Team WIG (X / Y / When + named owner + which Battle it ladders to). Verbatim from the user's input.
   - Mark any missing field "ABSENT" — do not invent values.
   - Count: number of Battles, number of Team WIGs, span of control (N sub-team-leaders).

2. **Read sub-leader / sub-team critique (if provided).**
   - Note the verbatim complaint ("imposed on us", "doesn't ladder", "we don't own this", "have to do many things", 「押し付け」, 「硬塞」, 「不接受」, 「沒辦法達成」).
   - Hold it aside for step 6 — the per-rule check runs first unbiased, then critique gets mapped after.

3. **Apply the Ch 7 four-rule check matrix.** Per artifact, issue PASS / FAIL / PARTIAL with one-line evidence cite:
   - **Rule 1 — one WIG per individual.** Does any individual on any team end up carrying multiple Team WIGs? If unclear from artifact, mark PARTIAL and surface as "needs input." If evidence shows N Team WIGs landing on the same person, FAIL.
   - **Rule 2 — Battles must win the war.** Does the Battle structure ladder to the Primary WIG? Apply the arithmetic test: if every Battle wins, does the Primary WIG hit? If not, FAIL. If only some Battles ladder up (others are decorative), PARTIAL. If "total revenue"-style war-not-battle inversion, FAIL with note.
   - **Rule 3 — leaders veto-not-dictate.** Were Team WIGs *proposed by sub-leaders* or *imposed by the leader-of-leaders*? Pattern signals: uniform numbers across units (suggests dictation); identical phrasing across diverse functions (suggests dictation); "imposed" / 「押し付け」 / 「硬塞」 in critique (direct evidence). If proposed: PASS. If imposed: FAIL.
   - **Rule 4 — From X to Y by When grammar.** For each Team WIG: X explicit + numeric? Y explicit + numeric + same units? When fixed calendar date? Stranger test passes (could a stranger tell on the deadline whether the team won)? Per-WIG verdict.

4. **Apply the Targets-not-Plans check.**
   - Per Team WIG: is it an outcome (X→Y→When result) or an action list ("execute project A, run program B, deliver C")?
   - Plan-shaped → FAIL with note: "smuggles HOW into the cascade; restate as result."
   - Target-shaped → PASS.

5. **Apply the Battles-to-win-the-war count check.**
   - ≤3 Battles → PASS (typical landing zone).
   - 4 Battles → PARTIAL (acceptable but borderline).
   - 5+ Battles → FAIL with note: "strategic narrowing incomplete; apply the 'if every battle won EXCEPT one, would Primary WIG still hit?' test to cut."

6. **Map sub-leader critique to rules** (if step 2 captured one).
   - Translate verbatim complaints to the rule they implicitly invoke:
     - "imposed on us" / "we don't own this" / 「押し付け」/「硬塞」/「不接受」 → **Rule 3 violation** (dictate-not-veto).
     - "doesn't ladder up" / "doesn't connect to strategy" / 「上に繋がらない」/「跟戰略沒關係」 → **Rule 2 violation** (Battles don't win the war, OR Team WIG doesn't ladder to a Battle).
     - "have to do many things" / "we're stretched" / 「色々やらされる」/「太多事要做」 → **Rule 1 violation** (one-WIG-per-individual).
     - "can't tell whether we won" / "too vague" / 「達成判定できない」/「沒辦法判斷」 → **Rule 4 violation** (X→Y→When grammar).
     - "this is just our work, not a strategic bet" / 「ただの業務」/「就只是日常」 → **Targets-not-Plans violation** OR strategy-fit issue (route to `4dx-meta-strategy-triage` if pattern persists).
   - Cite the rule explicitly so the leader can bring the diagnosis back to sub-leaders with the book reference.

7. **Recommend per-rule cascade revisions + conversation scripts.**
   - For each FAIL / PARTIAL, write a one-line cascade fix AND a conversation script for re-negotiation with sub-leaders.
   - Examples:
     - Rule 3 FAIL: *Fix*: "Pull back the numbers; have each sub-leader re-propose their own X→Y→When." *Script*: "I authored these and that was wrong. Each of you, take the same Battles and propose your team's From-X-to-Y-by-When. I keep veto, you keep authorship."
     - Rule 2 FAIL: *Fix*: "Re-derive Battles from the Primary WIG using the 'fewest possible' test." *Script*: "We can't show how today's Battles win the war. I'm taking the leadership team back to the drawing board on Battles before locking Team WIGs."
     - Rule 1 FAIL: *Fix*: "Identify each individual carrying >1 WIG; drop or split." *Script*: "We over-loaded individuals. Each person owns at most one Team WIG; we'll collapse or split where needed."
     - Battles-count FAIL: *Fix*: "Cut to ≤3 Battles via the 'if every battle won EXCEPT one' test." *Script*: "We have N Battles; that's a plan list, not strategic narrowing. We're cutting to 2-3."
   - Flag any assumption you had to make (e.g. "I assumed 'Battle 4' is decorative because no Team WIG ladders to it — confirm").

8. **Offer next steps.**
   - "If revising specific rule failures is enough, the recommendations + scripts above suffice."
   - "For full cascade rebuild from scratch, run **coach-mode**: `protocols/coach-mode.md` runs the 10-step Socratic build."
   - "If the audit reveals issues at lead-measure / scoreboard / cadence layers, route to `4dx-audit` (full-stack)."
   - "If the audit reveals 4DX may be the wrong tool entirely (stroke-of-pen / whirlwind-as-strategic-value), route to `4dx-meta-strategy-triage`."

### Output format (cascade audit card)

```markdown
# Cascade Audit

## Artifact
- **Primary WIG**: From [X] to [Y] by [When]
- **Battles** (N=…): [list, each X→Y→When]
- **Team WIGs** (N=…): [list, each owner / X→Y→When / Battle it ladders to]

## Sub-leader critique (if provided)
> [verbatim complaint] → maps to **[rule]**

## Rule-check
| Check | Verdict | Evidence |
|---|---|---|
| Ch 7 Rule 1 — one WIG per individual | PASS / FAIL / PARTIAL | … |
| Ch 7 Rule 2 — Battles win the war | PASS / FAIL / PARTIAL | … |
| Ch 7 Rule 3 — veto, not dictate | PASS / FAIL | … |
| Ch 7 Rule 4 — From X to Y by When | PASS / FAIL / PARTIAL | per-WIG |
| Targets-not-Plans | PASS / FAIL | … |
| Battles-count (≤3 typical) | PASS / FAIL / PARTIAL | N=… |

## Per-rule revision + conversation script
- Rule X (FAIL): *Fix* — … *Script* — …

## Assumptions to confirm
- …

## Next steps
- …
```

## B — Boundary (mode-specific)

### Do NOT use this protocol for:

- **First-time cascade design without artifact** — no draft, no critique → coach-mode (`protocols/coach-mode.md`).
- **Cross-layer audit** — if the user provides lead measures / scoreboard / cadence / substrate context alongside the cascade and wants a full diagnostic → `4dx-audit` (full-stack).
- **Single-team WIG selection / audit** — auditing a single Team WIG (no cascade involved) → `4dx-d1-wig-formulation` audit-mode.
- **OKR cascade audit without 4DX framing** — out of 4DX scope → `using-four-dx-coach`.
- **Strategy-fit questions** — "should we even use 4DX for this?" → `4dx-meta-strategy-triage`. Audit-mode assumes 4DX is committed.
- **Pure venting** — "sub-leaders are unreasonable" without an artifact → not this protocol.

### Author-warned failure modes

- **Verdict-without-evidence** — every PASS / FAIL must cite the specific Ch 7 rule and a one-line artifact reference. "FAIL because it's wrong" is not evidence; "FAIL Rule 3 — uniform numbers across districts is dictation pattern" is.
- **Inventing X / Y / When for absent fields** — the audit must mark missing fields ABSENT and surface under "Assumptions to confirm," not silently fill in.
- **Over-translating critique** — if the sub-leader complaint is vague ("just doesn't feel right"), don't force-fit a rule. Note the ambiguity and run the rule-check independently.
- **Coaching drift** — if the agent finds itself asking "what would your team commit to?" Socratically, it has slipped into coach-mode. Stop, return to the verdict table.
- **Author-the-fix temptation** — recommendations should be cascade-revision shape (e.g. "pull back the numbers"), not Team-WIG-author shape ("write 'from 100 to 50 by Q3' for District A"). Rule 3 applies to the audit-mode advice itself: the agent vetoes patterns, but doesn't author replacements.
- **Scope creep into D2/D3/D4** — audit-mode here is **D1-cascade-only**. If the cascade looks fine but cadence is broken, the diagnosis isn't this protocol's job — route to `4dx-audit` or D4.

### Easily-confused neighbours

- **`4dx-audit` (full-stack)** — covers all 5 layers (WIG / lead / scoreboard / cadence / substrate). This protocol is cascade-only.
- **`coach-mode.md`** — Socratic build from zero; this protocol is consultant on existing cascade.
- **`4dx-d1-wig-formulation` audit-mode** — single-WIG audit; this protocol is multi-WIG cascade audit.
- **`4dx-meta-strategy-triage`** — gate for "is 4DX the right tool"; this protocol assumes that gate has cleared.

## References

See `../references/industry-grounding.md` for grounding. Most relevant for audit-mode:
- **Hoshin Kanri (catchball)** — when "imposed" complaints surface, distinguish between Rule 3 violation (4DX-internal) vs leader genuinely operating in catchball mode (hoshin import). Both want sub-leader proposal-shape; only Rule 3 is veto-only.
- **OKR cascade** — when the artifact shows 3+ Battle WIGs per team or 3-5 KR-style sub-targets per Team WIG, flag as OKR-cascade-pattern bleed; 4DX is firm one-WIG-per-team.
- **Balanced Scorecard** — when every team's WIG is a miniature copy of the Primary WIG with smaller numbers, flag as BSC replication pattern; 4DX requires differentiated contribution.
