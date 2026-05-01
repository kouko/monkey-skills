# Protocol: audit-mode — Audit existing WIG drafts against 4DX rules

> Loaded by SKILL.md orchestrator when the user provides a WIG artifact
> (draft sentence / candidate list / inherited team WIG) and asks for
> diagnostic / revision, OR when the user provides a WIG plus a
> stakeholder critique ("boss says it's too abstract", 「上司がダメ
> 出ししてる」, 「老闆說 WIG 不行」). Agent voice = **consultant-mode**:
> structured per-rule verdict, evidence-cited, terse. Distinct from
> coach-mode protocols (personal-define / team-select / member-comprehend),
> which run Socratic dialogue from zero. Audit-mode assumes the user is
> already 4DX-committed (no fit-check) and stays inside D1 only.

## R — Reading (verbatim source quote)

> All WIGs must have a finish line in the form of *From X to Y by When*.
>
> — McChesney/Covey/Huling, *4DX* 2nd ed., Ch. 7 (Rule 4)

## I — Interpretation (mode-specific)

The user has already drafted a WIG (or has been handed candidates) and
wants the agent to *diagnose against 4DX rules*, not coach from scratch.
Three things differ from coach-mode:

1. **Posture is consultant, not coach.** Output is a per-rule verdict
   table with PASS/FAIL + cite, followed by a recommended revision —
   not a Socratic dialogue. Be terse, evidence-cited, decisive.
2. **Single-layer focus.** Audit-mode here is D1-only — WIG grammar +
   WIG-discipline + ladder-up. For cross-layer (lead measures /
   scoreboard / cadence / substrate), route to `4dx-audit`.
3. **4DX-committed premise.** The user has already decided to use 4DX;
   skip strategy-fit triage. If the artifact reveals the situation is
   actually stroke-of-pen / whirlwind / habit-shaped, flag it once and
   route to `4dx-meta-strategy-triage` — but do not re-litigate fit by
   default.

When a stakeholder critique is provided ("boss says X", 「上司が…」,
「老闆說…」), the consultant translates the everyday complaint into the
4DX rule the stakeholder is implicitly invoking, then issues per-rule
verdicts. "Too abstract" usually maps to Ch 2 grammar (no measurable Y
/ no deadline) and/or Ch 6 Trap 2 (too broad). "Not measurable" maps
to Ch 7 Rule 4. "Covers too much" maps to Ch 7 Rule 1 (one-WIG-per-
individual) and/or Ch 6 Trap 2.

Voice contrast vs sibling protocols: personal-define / team-select /
member-comprehend extract a WIG via Socratic question. Audit-mode reads
a finished artifact and returns a structured verdict. The user is not
being coached — they are being graded, and given a revision.

## A1 — Past Application

### Case 1: Younkers WIG before-vs-after (Ch 6)
- Department-store leadership initially landed on "improve customer
  loyalty" as the team's Primary WIG. Run as audit input:
  - Ch 7 Rule 4 / Ch 2 grammar: **FAIL** — no X, no Y, no When.
  - Ch 6 Trap 2 (too broad): **FAIL** — "loyalty" spans dozens of
    metrics, not separable from whirlwind.
  - Ch 6 Trap 3 (aspirational but unmeasurable): **FAIL** — fails
    stranger test.
- Recommended revision: rewrite as a measurable, scoped lag — e.g. a
  specific repeat-purchase / NPS / loyalty-program-enrolment number
  with X baseline + Y target + fixed deadline. The leadership team
  ultimately re-narrowed to a measurable lag. Lesson: an audit
  surfaces three rule failures in one minute; the same diagnosis via
  coach-mode would take an hour.

### Case 2: Sydney accounting firm — "go smaller" rescue (Ch 6 follow-on)
- Firm's Primary WIG was "total revenue" — high importance, presumed
  high feasibility. After a quarter of zero traction the leader
  brought it for diagnosis. Audit verdict:
  - Ch 7 Rule 4: PARTIAL — Y and When present, but X mixed with
    whirlwind activity (every revenue line counted).
  - Ch 6 Trap 2 (too broad): **FAIL** — "total revenue" is the war,
    not a Battle. Cannot ladder cleanly to one team's daily action.
  - Ch 7 Rule 2 (Battles must win the war): **inverted** — this WIG
    *is* the war.
- Recommended revision: demote "total revenue" to a strategy-line
  (monitored metric); pick a narrower segment / service-line growth
  Battle the team can actually own. Lesson: when a WIG is too broad,
  the audit fix is **go smaller** — not adjust the deadline.

## A2 — Future Trigger

When the user needs this protocol:

1. User pastes a written WIG (or candidate list) and asks "is this
   right?" / "what's wrong?" / "diagnose" / "audit".
2. User provides a WIG plus a stakeholder complaint ("boss says…",
   「上司が…」, 「老闆說…」) and wants the complaint translated to 4DX
   rules.
3. User has an inherited team WIG and wants a 4DX-rule diagnostic
   before deciding whether to ask the leader for revision.
4. User has 5-15 candidate Battles and wants per-candidate verdicts
   (not a coached 2x2 walk-through).

EN: "Here's our WIG draft — what's wrong?", "Boss says our WIG is too
abstract — diagnose it", "Audit my Primary WIG against 4DX",
"Is this WIG well-formed?"

JP: 「うちの WIG を診断して」「上司が WIG ダメ出ししてるけど何が原因？」
「この WIG、4DX 的に OK？」「Primary WIG をチェックして」

zh-TW: 「我們的 WIG 你看一下哪裡有問題」「老闆說 WIG 不行，幫我診斷」
「幫我審核這個 WIG 有沒有過 4DX 規則」「這個 WIG 寫得對嗎？」

## E — Execution

When this protocol activates, the agent runs a structured audit. **Do
not Socratically rebuild the WIG — diagnose, then recommend.**

1. **Read the WIG artifact(s).**
   - Extract X / Y / When / scope (personal vs team vs member-inherited)
     verbatim from the user's draft. If multiple candidates are
     provided, list each with an ID.
   - If the artifact is too vague to extract any of X / Y / When, mark
     each missing field "ABSENT" — do not invent values.

2. **Read stakeholder critique (if provided).**
   - Note the verbatim complaint ("too abstract" / "not measurable" /
     "covers too much" / 「ダメ」/「不行」).
   - Hold it aside for step 4 — the per-rule check runs first
     unbiased, then critique gets mapped after.

3. **Apply the rule-check matrix.** Per artifact (or per candidate),
   issue PASS / FAIL / PARTIAL with one-line evidence cite:
   - **Rule 1 (Ch 7) — one WIG per individual.** Does this artifact
     split focus across multiple lag-measures? Two-or-more independent
     numeric targets bundled = FAIL. See `../standards/wig-discipline.md`.
   - **Rule 2 (Ch 7) — Battles must win the war.** Does this WIG, if
     won, demonstrably move the larger mission/org outcome? If the
     artifact *is* the war (e.g. "total revenue"), inverted-FAIL.
   - **Rule 3 (Ch 7) — leaders veto-not-dictate.** Only audit if scope
     is team-select. Was this dictated top-down (FAIL) or earned via
     leadership-team brainstorm + 2x2 (PASS)? For personal / member
     scope, mark N/A.
   - **Rule 4 (Ch 7) + Ch 2 — *From X to Y by When* grammar.** X
     explicit + numeric? Y explicit + numeric + same-units? When fixed
     calendar date? Stranger test passes? See
     `../standards/from-x-to-y-by-when-grammar.md`.
   - **Bonus — ladder-up.** Does this WIG demonstrably ladder to org /
     team mission? See `../standards/ladder-up-test.md`. For purely
     solo-personal WIGs with no org context, mark N/A.

4. **Map stakeholder critique to rules** (if step 2 captured one).
   - Translate the verbatim complaint to the rule it implicitly
     invokes:
     - "too abstract" / 「曖昧」/ 「太空泛」 → Ch 2 grammar (Y or When
       absent) AND/OR Ch 6 Trap 2 (too broad).
     - "not measurable" / 「測れない」/「無法衡量」 → Ch 7 Rule 4 / Ch 2.
     - "covers too much" / 「広すぎ」/「太大」 → Ch 7 Rule 1 / Ch 6 Trap 2.
     - "that's just our job" / "BAU dressed as WIG" / 「日常業務じゃん」/「本業でしょ」
       → Ch 6 breakthrough-not-BAU. **Verbatim anchor (Cindrich,
       FranklinCovey insider, LinkedIn 2018-2019)**: *"Hitting your sales
       number is your job — it is not a WIG."* Cite this phrasing directly
       in the audit verdict when the artifact is a job-already-being-done
       rather than a breakthrough goal.
     - "we'll never hit it by then" / 「無理」/「來不及」 → Feasibility
       (Ch 6 2x2) — flag for re-scoping.
   - Cite the rule explicitly in the audit output so the user can
     bring the diagnosis back to the stakeholder with the book
     reference.

5. **Recommend revision.**
   - For each FAIL / PARTIAL, write a one-line fix.
   - Output a revised WIG draft in *From X to Y by When* form that
     clears the failed rules.
   - Flag any assumption you had to make (e.g. "I assumed your X
     baseline is the Q3 number — confirm" or "I inferred deadline =
     fiscal year-end — confirm"). Do **not** silently invent X / Y /
     When if absent in the artifact; surface them as "needs input."

6. **Offer next steps.**
   - "If revising this draft is enough, the recommendations above
     suffice."
   - "If you want a guided WIG rebuild from scratch, run coach-mode:
     `personal-define` for solo, `team-select` for leader, or
     `member-comprehend` for inherited."
   - "If the audit reveals issues at lead-measure / scoreboard /
     cadence / substrate layers, route to `4dx-audit` (full-stack)."
   - "If the audit reveals 4DX may be the wrong tool entirely (stroke-
     of-pen / whirlwind-as-strategic-value), route to
     `4dx-meta-strategy-triage`."

7. **Run the book's official Did-You-Get-It-Right self-check.**
   - Load `../references/book-self-check.md` — the verbatim 7-item
     checklist from McChesney et al. 2021 p 220 ("Did You Get It
     Right?"). This is the canonical FranklinCovey D1 verification gate
     and runs as the last act of the audit, after the rule-check (step
     3), critique-mapping (step 4), and revision (step 5) have produced
     a candidate revised WIG.
   - For team-select / member-inherited scope, apply the verbatim
     Team-WIG version. For personal scope, apply the personal-scope
     lens documented in the same file.
   - Issue PASS / FAIL per item with a one-line evidence cite, citing
     book p 220 in the audit card. Any item failing routes the user
     back to step 5 (recommend revision) before commit.

### Output format (audit card)

```markdown
# WIG Audit — [scope: personal / team-select / member-inherited]

## Artifact
> [verbatim WIG draft]

## Stakeholder critique (if provided)
> [verbatim complaint] → maps to **[rule]**

## Rule-check
| Rule | Verdict | Evidence |
|---|---|---|
| Ch 7 Rule 1 — one per individual | PASS / FAIL | … |
| Ch 7 Rule 2 — Battles win the war | PASS / FAIL | … |
| Ch 7 Rule 3 — veto not dictate | PASS / FAIL / N/A | … |
| Ch 7 Rule 4 + Ch 2 — From X to Y by When | PASS / FAIL / PARTIAL | … |
| Ladder-up | PASS / FAIL / N/A | … |

## Revised WIG (recommendation)
**From [X] to [Y] by [When]**

## Assumptions to confirm
- …

## Next steps
- …
```

## B — Boundary (mode-specific)

### Do NOT use this protocol for:
- **First-time WIG creation without artifact** — no draft, no
  critique → coach-mode protocols (`personal-define` / `team-select` /
  `member-comprehend`).
- **Cross-layer audit** — if the user provides lead measures /
  scoreboard / cadence / substrate context alongside the WIG and wants
  a full diagnostic → `4dx-audit` (full-stack).
- **Strategy-fit questions** — "should we even use 4DX for this?" →
  `4dx-meta-strategy-triage`. Audit-mode assumes 4DX is committed.
- **Cascade audit** — auditing how a Primary WIG was translated to N
  sub-team Battles → `4dx-d1-wig-cascade` audit-mode (when available).
- **Pure venting** — "boss is unreasonable" without an artifact → not
  this skill.

### Author-warned failure modes
- **Verdict-without-evidence** — every PASS / FAIL must cite the
  specific chapter rule. "FAIL because it's too abstract" is not
  evidence; "FAIL Ch 2 — Y absent, fails stranger test" is.
- **Inventing X / Y / When** — when the artifact is missing a field,
  the audit must mark it ABSENT and surface it under "Assumptions to
  confirm," not silently fill it in.
- **Over-translating critique** — if the stakeholder complaint is
  vague ("just doesn't feel right"), do not force-fit a rule. Note
  the ambiguity and run the rule-check independently.
- **Re-litigating 4DX fit by default** — audit-mode is post-commitment.
  Only flag fit-mismatch if the artifact reveals the goal is clearly
  non-4DX-shaped (habit / stroke-of-pen / pure-whirlwind).
- **Coaching drift** — if the agent finds itself asking "what would
  transform your situation?" Socratically, it has slipped into
  personal-define mode. Stop, return to the verdict table.

### Easily-confused neighbours
- **`4dx-audit` (full-stack)** — covers all 5 layers (WIG / lead /
  scoreboard / cadence / substrate). This protocol is D1-only.
- **Coach-mode protocols** — Socratic from zero; this protocol is
  consultant on existing artifact.
- **`4dx-meta-strategy-triage`** — gate for "is 4DX the right tool";
  this protocol assumes that gate has cleared.

## Standards used

- `../standards/from-x-to-y-by-when-grammar.md` — Step 3 Rule 4 /
  Ch 2 grammar check + stranger test.
- `../standards/wig-discipline.md` — Step 3 Rule 1 one-per-individual
  + Approach A vs B for team-select scope.
- `../standards/ladder-up-test.md` — Step 3 ladder-up bonus check.
- `../references/book-self-check.md` — Step 7 final SHOULD-gate; verbatim
  7-item "Did You Get It Right?" checklist from book p 220.

## References

See `../references/industry-grounding.md` for grounding. Most relevant
for audit-mode:
- **Rumelt** (kernel-of-strategy, *Good Strategy / Bad Strategy*) —
  diagnosis-of-strategy frame: a WIG that cannot be paired with a
  one-sentence diagnosis is a goal masquerading as strategy. Use when
  Rule 2 (Battles win the war) verdict is borderline.
- **Christensen / March / Dweck** — single-bet downside literature;
  flag when audit reveals over-focus risk on a possibly-obsoleting
  target.
- **Porter** (*"What Is Strategy?"*) — NOT-do test; use when Rule 1
  borderline (artifact technically names one WIG but team is "still
  doing all of it" alongside).
