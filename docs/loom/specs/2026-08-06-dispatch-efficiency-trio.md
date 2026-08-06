# Brief: dispatch-efficiency trio — packet discipline, scoped inner-loop tests, lane usage

Date: 2026-08-06
Status: FROZEN, amended post-plan-round-2 (user-directed: rule (b)
action-type provenance + four-leg adversarial probe + file-map
context valve) (user: 「先跑實驗驗證 ② 然後把 ①③④ 收成 arc」 —
endpoint = PR per the session's standing arc pattern, continuous.
Lever ② [same-type batch cache sharing] is EXCLUDED from this arc:
its local experiment runs alongside; its disposition — gotchas line
if confirmed, backlog entry with data if inconclusive — rides T5's
research note, not plugin legislation)
Consumer: writing-plans → SDD; ships as loom-code 0.64.0

## Problem

A cross-project scan (10,054 subagent records, 13 projects) measured
a ~10s-per-tool-call floor: subagent wall-clock ≈ tool round-trips ×
~10s. Three levers survived an industry-evidence check (Anthropic
multi-agent system, LangGraph handoff docs, Claude Code official
caching/subagent docs; EN+JP, URLs in the session record):

1. Discovery round-trips are reducible: an implementer spends 5-10 of
   its ~25 calls locating things the orchestrator already knows.
   Anthropic's own system prescribes curated task packets (objective /
   output format / tool guidance / boundaries) and measured that vague
   packets cause duplicated work. Local evidence both ways: site-list
   packets saved whole scan phases (0.62.0 T1), but a wrong guess in a
   packet cost a verification call, and line numbers rotted within one
   branch (:326-328 → :335-339 twice).
2. Implementers re-run the full 3-lane suite (~52s) 2-3× inside one
   task; only the final pre-commit run needs to be package-level.
3. The Review-weight mechanical/prose lanes exist and are trusted
   (Check 16-gated) but plans rarely declare them — the 0.63.0 bump
   task ran a full triad on a literal-target edit, ~6-8 min of
   reviewer wall-clock a mechanical self-check would have replaced.

## Smallest End State

1. **Packet-context discipline** — new §Dispatch-packet context in
   subagent-driven-development/references/dispatch-hygiene-notes.md
   (uncapped reference), four rules, each its own sentence:
   (a) site inventories and exact target strings ride the packet;
   anchor by verbatim string or stable heading, never by line number
   alone (line numbers rot within a branch — two live incidents);
   (b) every fact in a packet carries its source — the file read or
   the command run, named inline; a statement without a named source
   is a guess and must be labeled as one (action-type formulation per
   the weak-model-caveat lesson; open-form, explicitly not governing
   plan-format §Reuse-adequacy's closed vocabulary);
   (c) when ≥3 downstream dispatches will consume the same map,
   dispatch a locate arm first and amortize; below that, use knowledge
   already in hand — never Read files into the main conversation just
   to quote them (commander-stays-home); a many-consumer or large map
   may live in a file the locate arm writes, packets carrying only
   the path (main-context cost bounded at one path);
   (d) reviewer packets carry claims-to-verify, never
   conclusions-to-adopt — worker packets optimize for trust, reviewer
   packets for independence.
   Plus ONE pointer sentence in SDD SKILL.md's dispatch area (ceiling
   4015, margin 18 — the sentence must fit or the ceiling rises
   deliberately). Pins: new test in test_sdd_extraction_pointers.py
   asserting the four rules' load-bearing phrases in the notes file +
   the pointer in SKILL.md.
2. **Scoped inner-loop tests** — one rule appended to
   loom-code/agents/implementer.md's role contract: during the
   RED→GREEN inner loop, run the touched test file(s); run the full
   resolved package suite exactly once, after the last edit and before
   the commit — the per-task GREEN acceptance still requires that full
   run (verification-before-completion unchanged; this governs only
   the inner iterations). Pin in test_implementer_req_tag_guard.py.
3. **Lane-usage guidance** — one authoring-guidance sentence in
   writing-plans/references/plan-format.md's Review-weight area: when
   a task's Description already names an exact-spec target (Check 16's
   own eligibility), declare `Review-weight: mechanical`; when every
   touched file is .md authored prose, consider `Review-weight:
   prose` — an eligible task left undeclared costs a full triad
   (~6-8 min) for zero marginal defect yield. Non-gating guidance;
   Check 16 stays the gate. Pin in test_plan_format_prose_weight.py
   (the Review-weight section's own pin file).
4. loom-code → 0.64.0 (both manifests + CHANGELOG + shipping-version
   pin rewrite, four sites).
5. **Probe + research note** — (a) FOUR adversarial haiku cold-read
   legs, one per rule, each fresh-context with T1's shipped text plus
   one baited scenario (line-number temptation / unsourced-belief
   self-certification / consumer counting / ready-conclusion for a
   reviewer packet); any failed leg = T1 wording defect, fix and
   re-probe; (b) research note at
   docs/loom/research/2026-08-06-subagent-latency-and-cache-research.md
   recording the cross-project scan numbers, the industry-source
   verdict table (C1-C7), and the lever-② experiment data + verdict;
   (c) lever ②'s disposition per its data (gotchas line only if the
   experiment showed a clear win; otherwise backlog entry with the
   data attached). Dogfood report under docs/loom/dogfood/.

## Out of scope

- Lever ② legislation (experiment-gated, see Status).
- pytest-xdist / suite parallelization (new dependency, marginal).
- Any change to Check 16's eligibility rules or the mechanical
  self-check's two parts.
- Model-tier changes for reviewer arms (model-dispatch rules are
  dotfiles-owned, propose-only from this repo).

## Decisions

- Packet discipline lives in dispatch-hygiene-notes (reference, no
  ceiling) with a one-sentence SKILL pointer — not in SKILL.md bodies
  (ceilings tight) and not in implementer.md (it is orchestrator-side
  discipline; the worker's counterpart duty is the existing rule 12).
- String-anchor-over-line-number is rule (a)'s core: two same-branch
  incidents of line-number rot this session; repo memory already
  teaches position-anchoring is fragile for self-referential prose —
  this extends it to dispatch packets.
- Scoped inner-loop wording must not weaken
  verification-before-completion: the full-suite-once-pre-commit run
  IS the package-level gate; only redundant intermediate full runs
  are eliminated.
- Counting convention len(text.split()); verified at plan time: SDD
  4015 ceiling / current measured at task time; implementer.md and
  plan-format.md and dispatch-hygiene-notes.md uncapped.
