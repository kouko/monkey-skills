# Knowledge triage: three-bucket research routing across loom-* (2026-07-18)

## Problem (upstream artifacts)

Incident (2026-07-16→17, worktree `finacial-analytics-r2`, branch
`feat-operational-kpi-quarterly`, findings committed `ab65a0d9` on that
branch; domain gotcha in `docs/loom/memory/`): the agent spun 4 review
rounds on "how should fiscal_year be labeled" — a **business-domain
convention question** (answer owned by industry authorities: Compustat
DATADATE/DATACQTR pattern, SEC `dei:DocumentFiscalYearFocus`) — while
treating it as an **engineering question** (kept re-deriving year from
`period_end` in code). Direction was found only after the user manually
prompted "search how the industry does it". A remediation patch made it
worse (mislabeled all comparative-period facts); the branch was
abandoned.

Root cause, mechanism-level: loom-* has research-escalation in exactly
two places — `brainstorming` Axis 4 (before *asking the user*, brainstorm
stage) and `systematic-debugging` Phase 4 ("WebSearch mandatory before
Hypothesis #3"). Autonomous mid-pipeline stalls hit neither. The SDD
3-round review cap escalates straight to the user with no research step
(`subagent-driven-development/SKILL.md:150`), and no station upstream of
code classifies or intercepts domain-convention questions at all.

## Research grounding (2026-07-18 session; keep, do not re-derive)

- **Trigger design**: LLMs are systematically overconfident about
  parametric knowledge — self-confidence probes alone are unreliable
  (arxiv 2402.00367, 2502.11028). Portable trigger signals are
  structural: retry/round counters, verifier verdicts, question-type
  classification (Adaptive-RAG arxiv/2024.naacl-long.389; SKR arxiv
  2310.05002; Reflexion arxiv 2303.11366; Loop-Breaker strategy-SWITCH
  arxiv 2604.21375). Model-internal signals (Self-RAG, FLARE logprob
  thresholds) are NOT portable to prompt-level skills.
- **The knowledge-type split is canonical SE theory**, three independent
  traditions converging on "who can overrule the fact": Brooks
  essential/accidental; DDD subdomain vs bounded context + ubiquitous
  language (Evans 2003, Fowler); Zave & Jackson 1997 R/S/**D** — the
  third bucket (domain assumptions / environment facts) is theirs.
- **Harness-engineering discourse (2024–2026) has vocabulary but no
  routing mechanism**: Meta "tribal knowledge" context files, DDD
  UBIQUITOUS_LANGUAGE.md-for-agents, Spec-Kit constitution.md, Devin
  Knowledge Base — all *preventive artifacts* on the domain side.
  Closest analog routes verification, not research (Galileo:
  code-checks for mechanical correctness vs expert-calibrated judge for
  business semantics). **Research-time routing by knowledge type has no
  prior art** — this plan is first-mover, not adoption.
- **Timing doctrine** (process archaeology): front-load
  domain-of-discourse knowledge (RUP business modeling; Zave & Jackson
  "the environment is the only thing"; continuous discovery; DDD
  knowledge crunching "intensive at the beginning, continuous after");
  defer technical knowledge behind explicit stall triggers (XP spike =
  "cannot estimate", timeboxed 1–3 days; lean Last Responsible Moment =
  imminent option-foreclosure). Reconcile by decision reversibility
  (Bezos one-way/two-way doors). Do NOT cite Boehm's 100x curve as
  justification — contested empirics (Bossavit; 171-project study).

## The doctrine

**Three buckets** — a question's bucket decides where its answer lives:

| Bucket | Test ("who overrules this fact?") | Research route |
|---|---|---|
| craft (engineering practice) | Same answer in any industry → technology-neutral literature | Axis 4 protocol / frozen canon refs |
| domain convention | Owned by an authority outside the code (industry standard, regulator, data vendor) | Search domain sources, in domain language |
| project-local fact | Not on the web at all | repo docs / `docs/loom/memory` / ask the user |

**Triage, not checklist**: one stuck question → classify once → walk ONE
route. Never "research all three then synthesize" per decision.

**Contract surface vs per-station freedom**: family-wide fixed = the
three bucket names + semantics + finding-tag format
(`evidence_needed: domain-convention` shape). Per-station free = the
classification question's wording, mount point, worked example, and
post-classification action. No shared files between plugins — each
skill restates its own minimal copy (precedent: per-plugin
`references/{claude-code,codex}-tools.md`); cross-station flow rides
repo artifacts consumed via the conditional-lens pattern (read if
present / loud no-op if absent / never invent). Drift guard: grep-level
CI check on bucket-name spelling.

**Uniform station pattern, per-station parameters**:

> draft closed-world → tag domain questions → triage (shaping vs
> deferrable) → shaping: resolve by ROUTED research before this
> station's gate; deferrable: write tagged open question into the
> artifact, flows downstream.

| Station | Mount point | Posture | "Shaping" bar |
|---|---|---|---|
| discovery | evidence intake | standing (already researches) — add source-type column to evidence.md | n/a (produces, doesn't defer) |
| product-principles | a principle's `— check:` won't write | standing classify-and-punt (domain → discovery; no in-station research) | constitution = one-way door |
| interface-design | critic finding / flow drafting | tag + two-tier triage, HIGH bar | alters flow structure, state machine, or semantic display conventions (color semantics, sign conventions, period definitions) |
| spec | edge-case expansion hits a fact not in seed/PRINCIPLES | tag + two-tier triage, LOW bar | alters acceptance criteria, data semantics, or state machine |
| code | structural stall signal (2nd same-question review failure / BLOCKED / hypothesis count) | reactive safety net | n/a (last net, catches what upstream missed or misclassified) |

Bar heights are priced by remaining downstream nets: design defers more
(spec's gate still catches), spec defers least (only the expensive code
net remains). Gate rule at design/spec: a shaping-class tag unresolved →
artifact cannot PASS unless explicitly deferred with a written reason.
Research runs OUTSIDE the closed-world drafting skills — the
orchestrator routes collected shaping tags to research (discovery
delegation or Axis 4 protocol) between draft and gate, mirroring
user-insights → deep-deep-research delegation. Critics never search;
they flag.

**Backstop (classification is fallible)**: the code-station round cap
still forces one research pass before any user escalation, even when
classification erred or never fired.

## Rollout

**v1** (direct incident coverage, cheapest):
1. loom-code reactive trigger: generalize the systematic-debugging
   research gate to the SDD review-cap point (2nd same-question failure
   → classify → routed research → 3rd round with evidence or escalate).
   Text goes in a `references/` file — SDD SKILL.md (~7.6k tokens) and
   requesting-code-review (~6.8k) are over the ~6k cap; body gets a
   one-line pointer only.
2. spec tagging + gate-front research: spec-expansion mounts the
   classification question during edge-case expansion; shaping-tag
   resolution step before VERIFY. (spec-expansion 24 KB,
   completeness-critic 26 KB → new text in references/.)
3. discovery evidence.md source-type column (craft / domain-convention
   / project-local). Headroom exists (8.4 KB).

**v2** (REVISED 2026-07-18, user decision post-v1-merge: build now in one
arc rather than riding later revisions — v2 completes the already-ratified
architecture; the recurrence gate moves to the DOMAIN.md prevention layer
only. Entry gate = the synthetic firing dogfood below, PASSED 3/3):
4. product-principles classify-and-punt clause (21 KB, references/
   placement).
5. interface-design two-tier triage + tagged open questions written
   into ui-flows.md/DESIGN.md so spec's tag intake inherits them.
6. `evidence_needed: domain-convention` finding tag in critic schemas
   (design-critic, loom-code reviewers).

Real-world acceptance for the whole mechanism: the financial-analytics
rebuild (the incident's native workload) exercises the spec + code legs
live; its interception/recurrence data also decides the DOMAIN.md layer.

### v2 firing dogfood (2026-07-18, pre-v2 gate — all haiku, SKILL.md-only
input, mounts must self-route)

- S1 SDD leg: 2nd same-question round (settlement-date convention — a
  NON-fiscal-year domain question, generalization check) → self-routed to
  research-escalation.md, classified domain-convention, EN+JA route,
  evidence rides round 3, cap intact. PASS.
- S2 spec leg: trade-date vs settlement-date month attribution → self-
  routed to domain-tag-triage.md, wrote tagged open question
  (`evidence_needed: domain-convention`, SHAPING), gate + backstop cited.
  PASS.
- S3 negative control: round-1 off-by-one with in-spec answer → correctly
  did NOT read the escalation reference, mechanical re-dispatch. PASS
  (no over-firing).

## Non-goals

- No live WebSearch inside closed-world drafting/critic skills
  (reproducibility + decorrelation + token caps stay intact).
- No family-wide verdict-vocabulary unification (four existing enums
  stay; only the finding tag is added).
- No shared physical files across plugins.
- No per-decision three-way parallel research (triage only).
- No preventive DOMAIN.md glossary artifact yet — revisit after v2
  recurrence data (Meta/DDD-style prevention layer, deferred).

## Acceptance

1. Cold-reader test per edited rule text (institution convention): a
   fresh-context agent, given only the edited references/ file + one
   realistic stall case, classifies bucket and picks the route
   correctly — including one deliberately project-local case (must NOT
   trigger web research).
2. Incident replay (spec leg): feeding the operational-KPI seed through
   spec-expansion with the v1 text produces a shaping-class
   domain-convention tag on fiscal-period labeling (would have
   intercepted the 07-16 incident one station early).
3. Incident replay (code leg): a simulated 2nd-round same-question
   NEEDS_REVISION triggers classification + routed research BEFORE user
   escalation; a pure code-regression case does NOT trigger it.
4. Token check: every touched SKILL.md stays within its current size
   class (new content in references/ only).
5. Plugin version bumps per touched plugin (marketplace convention);
   per-repo CI green; whole-branch review PASS before PR.

## Notes

### §Pinned bucket vocabulary (transcribe VERBATIM into each plugin's references/ file; supplements go AFTER this block, never inside it)

```
Three buckets — a stuck question's bucket decides where its answer
lives. Classify ONCE, walk ONE route (triage, not checklist):

- **craft** — engineering practice. The answer is the same in any
  industry; it is overruled by technology-neutral literature
  (patterns, framework docs). Route: the Axis 4 research protocol.
- **domain-convention** — the business domain's rule. The answer is
  owned by an authority OUTSIDE the code (industry standard,
  regulator, data-vendor convention). Route: search domain sources,
  phrased in the domain's own language (EN + JA minimum), cite the
  owning authority.
- **project-local** — a fact of this repo/product only. It is not on
  the web at all. Route: repo docs / `docs/loom/memory` / ask the
  user. Never WebSearch this bucket.

Classification question: "Who can overrule this fact — engineering
literature (craft), a domain authority outside the code
(domain-convention), or only this project's own docs and people
(project-local)?"

Tag format for findings and open questions:
`evidence_needed: craft | domain-convention | project-local`.

Classification is itself fallible — structural backstops (round caps,
gate rules) still apply when it errs.
```

### §Pin usage rules

- Each consuming task transcribes the fenced block above VERBATIM into
  its plugin's new references/ file, then ADDS its station-specific
  mount text after it (mount wording is per-station, deliberately NOT
  pinned).
- Reviewers verify pin copies character-level against this block.
- Mount lines in SKILL.md bodies are imperative and anchored to the
  acting moment ("before X → do Y FIRST" shape), per
  `docs/loom/memory/imperative-trigger-cards-beat-descriptive-preloads.md`.
- Cross-reference severing guard: each references/ file must itself
  restate the structural backstop it depends on (code: the round cap
  still forces research before user escalation; spec: the VERIFY gate
  rule), and the body pointer names the reference file — per
  `docs/loom/memory/extraction-severing-cross-ref-needs-weak-model-test.md`.

## Acceptance results (2026-07-18 run)

- Cold-reader probes (haiku, blind, single-file): code-leg fiscal-year
  scenario → trigger/bucket/EN+JA-route/evidence-rides-round-3/cap-unchanged
  all correct with citations; project-local control → NO WebSearch, correct
  lookup path; spec-leg → tagged open question (no invented answer), SHAPING,
  VERIFY blocked unless deferred, drafting-never-searches; craft control →
  normal expansion, no tag. 4/4 PASS.
- Suites: loom-code 305 / loom-spec 103 / loom-discovery 68 / repo scripts 36
  (CI-equivalent line 359) — all green.
- Token check: SDD SKILL.md wc -w 4215/4500; spec-expansion 3663/4500.

## Tasks (v1 only; v2 rides later revisions)

1. ~~Write shared-wording master copy~~ DONE — pinned above in §Notes.
2. loom-code: `references/research-escalation.md` + one-line mounts at
   SDD review-cap and BLOCKED paths; reuse Axis 4 protocol by pointer.
3. loom-spec: `references/domain-tag-triage.md` + mount in
   spec-expansion expansion loop + VERIFY-gate rule line.
4. loom-discovery: evidence.md template source-type column.
5. CI: bucket-name spelling grep across the three touched plugins.
6. Cold-reader + replay acceptance runs (items 1–3 above).
7. Version bumps, whole-branch review, PR. No auto-merge.

## Tasks (v2 — branch feat-knowledge-triage-v2, base 55cded40)

All v1 conventions carry over: pin transcribed VERBATIM into each new
references/ file, imperative action-moment mounts, neighborhood-scoped
grep tests proven RED via `git show HEAD:`, owning-plugin suite as the
resolved test command, references/ placement for near-cap SKILL.md files.

8. loom-product-principles (0.9.1 → 0.10.0): new
   `skills/product-principles/references/knowledge-triage.md` (pin +
   station doctrine: when a principle's `— check:` cannot be written,
   classify; domain-convention → punt to `using-loom-discovery` via the
   skill's existing punt channel with the tag attached; craft → the
   canon-*.md refs already cover it; project-local → repo docs/user).
   One imperative mount in SKILL.md at the falsifiability/`— check:`
   drafting moment. Standing posture (constitution = one-way door), not
   stall-triggered.
9. loom-interface-design (0.5.0 → 0.6.0): new
   `skills/interaction-flows/references/knowledge-triage.md` (pin +
   HIGH-bar two-tier: SHAPING = alters flow structure, state machine, or
   semantic display conventions — color semantics, sign conventions,
   period definitions; everything else deferrable). Mounts: one in
   interaction-flows at the flow/state drafting moment, one in
   design-system at the token/convention drafting moment (both point at
   the interaction-flows references file's twin copy — NO: each skill
   carries its own copy per no-shared-files; design-system gets its own
   references/knowledge-triage.md with identical pin). Deferrable-class
   items are written into ui-flows.md / DESIGN.md as tagged open
   questions (`evidence_needed:` format) so spec-expansion's Phase ③
   intake inherits them. design-critic: findings schema gains the
   optional `evidence_needed:` tag (critic flags, never searches).
10. loom-code (0.32.0 → 0.33.0): reviewer agents
    (`agents/code-quality-reviewer.md`, `agents/code-reviewer.md`) gain
    the optional `evidence_needed: craft|domain-convention|project-local`
    finding tag (flag-don't-search, one schema line + one sentence each);
    SDD SKILL.md one-line mount: a reviewer finding carrying the tag
    triggers the research-escalation triage IMMEDIATELY (no waiting for
    the 2nd round) — the tag is the Loop-Breaker SWITCH signal.
11. CI: extend `scripts/test_bucket_vocabulary_consistency.py` carrier
    lists with the new pin copies; add the new foreign carrier paths to
    `loom-code-ci.yml` BOTH trigger blocks (per
    `docs/loom/memory/cross-plugin-guard-tests-need-foreign-carrier-trigger-paths.md`).
12. Firing dogfood for v2 legs (haiku, SKILL.md-only, mounts self-route):
    principles leg, design leg (SHAPING display-semantics case), critic-tag
    leg (reviewer tags → orchestrator immediate triage), plus one negative
    control (craft-derivable design case must NOT tag). Record results
    in-file.
13. Version bumps, whole-branch review, PR. No auto-merge.
