# Plan: escalation interface / decision log / acceptance-surface / appetite contracts

**Source brief**: docs/loom/specs/2026-07-11-escalation-interface-contracts.md
**Total tasks**: 6
**Critical-path depth**: 3 (≤5 ✓) — longest chain: Task 1 → Task 2 → Task 6 (Task 3 joins at Task 2's level feeding Task 6; Tasks 4, 5 are leaves feeding Task 6)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-07-11, round 2, 14/14 checks; fresh-context evaluator)

## Task 1 — Decision Log section spec in plan-format.md

- **Description**: Add a `## Decision Log` optional-section spec to writing-plans' plan schema, alongside the existing optional sections (§Optional sections, plan-format.md:136): one entry per agent-decided engineering choice, single physical line per entry in the shared deviation-ledger record shape — `N. chose <X> because <Y> — cost-of-change: the day you want <Z>, this choice costs <W>` (product language, no jargon); entries are RUNTIME content maintained by the SDD orchestrator (like the `Status` field — plan-document-reviewer accepts and ignores them; state this explicitly, mirroring the Status field's reviewer-ignores note); a fresh plan has no Decision Log section. Include the placement rationale pointer (brief §Alternatives — plan-embedded, reversal conditions: >15-20 entries/arc or cross-arc lookup need → standalone docs/loom/decisions/). Commit trailers remain the engineer-facing index (two views, one format — cite the architecture doc merge decision, point don't copy).
- **Module**: `loom-code/skills/writing-plans/references/plan-format.md`
- **Files touched**: `loom-code/skills/writing-plans/references/plan-format.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-11-escalation-interface-contracts.md (§Smallest End State item 2 + §Alternatives)
  - /Users/kouko/GitHub/monkey-skills/loom-code/skills/writing-plans/references/plan-format.md (§Optional sections :136; §Progress ledger Status precedent :88-113)
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/skills/product-principles/references/principles-rules.md (:212-235 deviation-ledger record shape — the sibling format)
- **Acceptance**:
  - **RED**: diagnostic — `grep -c '## Decision Log' loom-code/skills/writing-plans/references/plan-format.md` returns 0 today
  - **GREEN**: section spec present under §Optional sections with entry format, single-line rule, SDD-maintains/reviewer-ignores statement, reversal conditions; reference file is uncapped (no word-budget risk); `python3 scripts/check-skill-structure.py loom-code` passes
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: §Smallest End State 2 — "a `## Decision Log` section in the PLAN document … record shape shared with the deviation ledger … Commit trailers stay the engineer-facing greppable index"

## Task 2 — Kickoff briefing: new reference + minimal writing-plans pointer

- **Description**: Create `loom-code/skills/writing-plans/references/kickoff-briefing.md` carrying the escalation interface's kickoff firing point: (a) the two-axis test verbatim-by-citation (product consequence × reversal cost; one-way/two-way door; the invisible×one-way-door bottom-right cell IS briefed — user decision 2026-07-10; cite the architecture doc as design SSOT, do not restate its rationale); (b) the collection step — after plan-document-reviewer PASS, sweep the plan's tasks for one-way-door engineering decisions, expect 1-3 per round; (c) the briefing format — ONE batched product-stakes briefing: per decision plain-language stakes → 2-3 options with product consequences → recommendation; format authority = `dev-workflow:brief-before-asking` (pointer, not copy); derivation-for-confirmation framing when PRINCIPLES.md already locks the choice; (d) the appetite read — before briefing, grep the target repo's `docs/loom/PRINCIPLES.md` Engineering Principles for an escalation-appetite entry (landing shape per Task 5's rule) and apply its dial; read once, never re-ask (judgment-rubrics §3(c) cite); no PRINCIPLES.md → default = brief all two-axis hits; (e) decisions the user delegates back + all below-threshold decisions route to the plan's `## Decision Log` (Task 1's spec — pointer); (f) mid-implementation escalation is the SAME interface's exception firing point, owned by SDD (pointer to its section, added in Task 3). Then add the MINIMAL pointer into writing-plans SKILL.md's pipeline (insertion seam: after §Self-review PASS, before SDD handoff — SKILL.md:117/119): ≤40 words, imperative ("After PASS, run the kickoff briefing — read references/kickoff-briefing.md"), because SKILL.md has only 95 words of headroom (4,405/4,500).
- **Module**: `loom-code/skills/writing-plans/references/kickoff-briefing.md` (new)
- **Files touched**: `loom-code/skills/writing-plans/references/kickoff-briefing.md`, `loom-code/skills/writing-plans/SKILL.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/design/2026-07-10-designer-pm-loop-architecture.md (§2 two-axis rubric :64-97 — design SSOT)
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-11-escalation-interface-contracts.md (§Smallest End State 1)
  - /Users/kouko/GitHub/monkey-skills/loom-code/skills/writing-plans/SKILL.md (:103-119 insertion seam; current pipeline diagram :28-29)
  - /Users/kouko/GitHub/monkey-skills/dev-workflow/skills/brief-before-asking/SKILL.md (format authority to point at — read for the pointer's anchor name only)
- **Acceptance**:
  - **RED**: diagnostic — `ls loom-code/skills/writing-plans/references/kickoff-briefing.md` fails; `grep -c 'kickoff' loom-code/skills/writing-plans/SKILL.md` returns 0
  - **GREEN**: reference exists with (a)-(f); SKILL.md pointer ≤40 added words; `wc -w` SKILL.md ≤4,500; `python3 scripts/check-skill-structure.py loom-code` passes; no copied doctrine (two-axis rationale, briefing block format, appetite presets all by pointer/citation)
- **Dependencies**: Tasks 1, 5 complete first
- **Independent**: false
- **Brief item covered**: §Smallest End State 1 — "writing-plans gains a §Kickoff briefing step … batch the 1-3 of them into ONE product-stakes briefing … Composition, not duplication"

## Task 3 — SDD: exception firing point + Decision Log maintenance

- **Description**: Two additions to `subagent-driven-development/SKILL.md`, both compact: (a) in §Asking the user gate ① (SKILL.md:27) add the product-consequence refinement — an implementation-discovered decision that passes the two-axis test (pointer to references/kickoff-briefing.md as the interface SSOT) is escalated in the SAME briefing format as the kickoff (one interface, two firing points — cite the architecture merge decision); below-threshold decisions are NOT asked, they are LOGGED; (b) a **Decision Log maintenance** paragraph mirroring the Progress-ledger paragraph (:117-125): when the orchestrator (or an implementer report) records an agent-decided engineering choice with product relevance, append a Decision Log entry to the plan per plan-format.md's spec, commit with the task's ledger update; NEEDS_CONTEXT surfacing (:101, :183) gains one line: NEEDS_CONTEXT questions with product stakes go through the same two-axis framing. Word budget: 718 headroom — keep total addition ≤250 words.
- **Module**: `loom-code/skills/subagent-driven-development/SKILL.md`
- **Files touched**: `loom-code/skills/subagent-driven-development/SKILL.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-code/skills/subagent-driven-development/SKILL.md (:23-49 asking gates; :101/:183 NEEDS_CONTEXT; :117-125 Status ledger paragraph — the mirror)
  - /Users/kouko/GitHub/monkey-skills/loom-code/skills/writing-plans/references/plan-format.md (Task 1's Decision Log spec)
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-11-escalation-interface-contracts.md (§Smallest End State 1-2)
- **Acceptance**:
  - **RED**: diagnostic — `grep -c 'Decision Log' loom-code/skills/subagent-driven-development/SKILL.md` returns 0 today
  - **GREEN**: both additions present, all cross-references are pointers (no copied two-axis table, no copied entry format); `wc -w` ≤4,500; structure check passes
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: §Smallest End State 1 ("mid-implementation ask paths point at the SAME two-axis test") + 2 ("maintained by the SDD orchestrator during execution")

## Task 4 — Acceptance-surface promotion in finishing + ui-verification

- **Description**: Promote the product-perceivable surface to the user's main acceptance stage: in `finishing-a-development-branch/SKILL.md` — (a) Step 5b (:123) and the Phase 2b diagram/table rows (:26, :84) reframed from side-gate wording to the user's acceptance stage (ui-verification result = what the user judges "done" by; unchanged N/A-loud contract for no-UI branches); (b) Step 13's final report (:235) becomes a product-language completion report (what the product now does, in user terms; test counts and review verdicts sink to sub-lines) — cite family-relay's rollup discipline as format authority (pointer); (c) one explicit line: NEEDS_REVISION review loops digest silently inside SDD/finishing (they already do behaviorally — make the contract explicit; the PASS_WITH_NOTES user-ask gate is UNCHANGED). In `ui-verification/SKILL.md` — reframe the role line(s) (:4, :24 area) from "side gate" to "the user's main acceptance surface when a UI exists" (conditional contract and N/A-loud behavior unchanged). Word budgets: 1,453 / 3,295 headroom — comfortably fits.
- **Module**: `loom-code/skills/finishing-a-development-branch/SKILL.md`
- **Files touched**: `loom-code/skills/finishing-a-development-branch/SKILL.md`, `loom-code/skills/ui-verification/SKILL.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-code/skills/finishing-a-development-branch/SKILL.md (:26, :84, :123, :235)
  - /Users/kouko/GitHub/monkey-skills/loom-code/skills/ui-verification/SKILL.md (:4, :24-39 conditional + N/A contract)
  - /Users/kouko/GitHub/monkey-skills/docs/loom/design/2026-07-10-designer-pm-loop-architecture.md (§1 #4 :58-62)
- **Acceptance**:
  - **RED**: diagnostic — `grep -c 'main acceptance' loom-code/skills/ui-verification/SKILL.md` returns 0 today (and the same grep on finishing-a-development-branch/SKILL.md returns 0)
  - **GREEN**: both files reframed; N/A-loud + conditional contracts byte-preserved in behavior; PASS_WITH_NOTES ask unchanged; both `wc -w` ≤4,500; structure check passes
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: §Smallest End State 3 — "ui-verification promoted from side gate to the user's main acceptance stage … NEEDS_REVISION review loops digest silently"

## Task 5 — Appetite landing shape in product-principles rules

- **Description**: Question-sets already asks the appetite question (Q5 "Escalation appetite", question-sets.md:81-89) — what is missing is the LANDING SHAPE. Add to `principles-rules.md`'s Engineering Principles section (:129-161): the Q5 answer lands as a normal Engineering Principles ordered entry whose text contains the greppable phrase `escalation appetite` and carries the standard `— check:` marker (so validator check 4 passes with NO validator change — verified: entries outside the two jurisdiction headings are ignored, entries inside need only the marker); consumers (loom-code's kickoff briefing) locate it by grepping `escalation appetite` under `## Engineering Principles`; the entry is optional (products may omit it → consumers default to briefing all two-axis hits); read once, never re-asked. Update question-sets.md Q5 only if it lacks a "lands as an Engineering Principles entry" pointer line (verify; add ≤2 lines if missing). NO validator edit, NO SKILL.md edit (word budgets untouched), presets stay DEFERRED.
- **Module**: `loom-product-principles/skills/product-principles/references/principles-rules.md`
- **Files touched**: `loom-product-principles/skills/product-principles/references/principles-rules.md`, `loom-product-principles/skills/product-principles/references/question-sets.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/skills/product-principles/references/principles-rules.md (:129-161 Engineering Principles rules)
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/skills/product-principles/references/question-sets.md (:57-89 Engineering section, Q5)
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/scripts/validate_principles_output.py (:177-213 check 4 — confirm no change needed)
- **Acceptance**:
  - **RED**: diagnostic — `grep -c 'escalation appetite' loom-product-principles/skills/product-principles/references/principles-rules.md` returns 0 today
  - **GREEN**: landing-shape rule present; a synthetic Engineering Principles entry carrying `escalation appetite … — check: …` passes `validate_principles_output.py` unchanged (spot-run on a tmp fixture); full suite `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest loom-product-principles/scripts/ -q` green (211 baseline); `python3 scripts/check-skill-structure.py loom-product-principles` passes
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: §Smallest End State 4 — "an optional appetite declaration slot in the Engineering Principles section … read once by the escalation interface, never re-asked"

## Task 6 — Cold-reader dogfood gate + version bumps

- **Description**: Ship gate for the four behavioral contracts, per the repo's process-mechanism-dogfood pattern: dispatch fresh-context cold-reader agents, ONE per contract, each given ONLY the shipped text (the file(s) that contract landed in) plus one realistic case, and check they execute the contract correctly: (1) kickoff briefing — a synthetic 3-task plan containing one one-way-door + one two-way-door decision → does the reader brief exactly the one-way-door (incl. a bottom-right-cell case) and log the other?; (2) SDD exception + Decision Log — a mid-implementation NEEDS_CONTEXT with product stakes → same-format escalation + a correctly-shaped log entry?; (3) acceptance surface — a finished branch with UI → does the reader present the product-language report with ui-verification as the acceptance stage?; (4) appetite — a PRINCIPLES.md with an appetite entry → does the kickoff reader apply the dial without re-asking, and default correctly when absent? Findings fold back (fix-first) before ship. Record the dogfood report at `docs/loom/dogfood/2026-07-11-escalation-contracts/report.md`. Then version bumps: loom-code plugin.json minor bump + loom-product-principles plugin.json minor bump (+ marketplace.json description sync if those files' shared fields changed — verify with the repo's sync check).
- **Module**: `docs/loom/dogfood/2026-07-11-escalation-contracts/report.md`
- **Files touched**: `docs/loom/dogfood/2026-07-11-escalation-contracts/report.md`, `loom-code/.claude-plugin/plugin.json`, `loom-product-principles/.claude-plugin/plugin.json`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/memory/process-mechanism-dogfood-via-coldreader-real-commits.md (the dogfood pattern)
  - all four contracts' shipped files (Tasks 1-5 outputs)
- **Acceptance**:
  - **RED**: diagnostic — dogfood report path does not exist
  - **GREEN**: 4 cold-reader probes run with recorded PASS/FAIL + fold-backs applied; report committed; both plugin versions bumped; `python3 scripts/check-skill-structure.py loom-code` and `… loom-product-principles` pass; product-principles suite still green
- **Dependencies**: Tasks 2, 3, 4, 5 complete first
- **Independent**: false
- **Brief item covered**: §Smallest End State ship gate — "cold-reader behavioral dogfood on the contracts … plus each touched SKILL.md under its word cap"

## Notes

- Sync-set Open Question RESOLVED (recon 2026-07-11): all touch targets are direct edits — no file is a distribute.py functional copy (sync set = SDD standards/rubrics/checklists + tdd-standard only).
- Word-budget hard constraint: writing-plans SKILL.md is at 4,405/4,500 — Task 2's SKILL.md pointer is capped at ≤40 words by design; the briefing body lives in the uncapped reference file.
- plan-document-reviewer tolerance verified: no closed-set section check — a runtime `## Decision Log` section in future plans trips nothing (checks are required-field-presence only).
- Tasks 1, 4, 5 are parallel-eligible leaves (disjoint files, no shared symbol). Task 2 consumes Task 1's section spec + Task 5's landing shape; Task 3 consumes Task 1's spec. Task 6 gates on all contracts.
- Tasks 2 and 3 stay `Independent: false` DELIBERATELY despite disjoint files (reviewer Check-15 advisory considered): Task 3's text writes a pointer naming Task 2's new file (`references/kickoff-briefing.md`) — a doc-mirrors-doc semantic dependency. The pointer NAME is fixed by this plan so Task 3 does not hard-block on Task 2's completion, but they are not certified parallel-safe; SDD may run them sequentially in either order after their declared upstreams.
- Design decisions (two-axis content, bottom-right cell, merges, DEFER on presets) live in the architecture doc — every task cites by pointer; any task found copying doctrine is a review finding.
