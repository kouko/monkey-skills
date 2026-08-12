# Brief: adjudication reading layer — conversation-language views of artifacts under adjudication

Date: 2026-08-12 (rev 2 — scope corrected at sign-off: document-view is the core object, not only verdict findings)
Stage: brainstorming output → writing-plans input
Design-side on-ramp: no criteria row fired (increment to loom-code's own workflow, not product-shaped new work; queue layer exists) — no detour offered.

## Problem

The human adjudicator must READ full English artifacts — the plan at
the plan review gate, the brief at sign-off — and the review findings
at verdict presentation, and judge them; but they read Traditional
Chinese natively. The artifacts serve three readers — validators
(exact string match), downstream agents (unambiguous, greppable
English), and the human — and the current format optimizes the first
two at the third's expense. The job to be done: **let the adjudicator
read and judge every artifact they must approve in their language,
without weakening the machine-contract or agent layers.** Scope
correction (2026-08-12 sign-off): the primary object is the
**document under review itself** (plan / brief full text); verdict
findings are the secondary object riding the same machinery.

## Users

kouko — sole adjudicator, reads 繁體中文/日本語 natively, mixed-script
Chinese convention (technical nouns stay English verbatim). Reads in
the Claude Code chat/terminal; long documents read better as a styled
HTML page (side-panel render) than as chat scroll.

## Smallest End State

v1 = **document-view (plan + brief) as core, verdict digest included**,
four deliverables:

1. **Protocol file** (SSOT): `adjudication-digest` protocol under
   `using-loom-code` — shared rules for both objects: unit 1:1 with
   source structure (sections/tasks for documents, findings for
   verdicts; omissions must be marked, compression only within a
   unit), fixed modality mapping (must→必須 / should→應 / may→可),
   technical nouns + enum tokens verbatim, translator additions
   provenance-tagged, every rendition regenerated from the artifact
   (never digest-of-digest), severity emoji carried verbatim.
2. **Renderer + lint scripts** shipped in `loom-code/scripts/`
   (plugin-shipped, NOT repo-root-only — a-documented-fallback
   memory). Architecture: **script splits the English artifact by
   section/task → LLM translates per unit → script reassembles**:
   - Document view: **EN/ZH side-by-side HTML** (original collapsible
     beside each translated unit) → unit-1:1 and anchoring hold **by
     construction** (the split is mechanical); written to scratchpad,
     never committed; side-panel render.
   - Verdict digest: markdown table inline in chat (編號 assigned |
     severity verbatim emoji | 中文摘述 | `where` anchor verbatim);
     HTML rendition of the same structured rows via the same template
     when findings are numerous or on request.
   - Zero-token lint on the structured intermediate: unit count ==
     source unit count; every number / enum / English term from each
     unit appears verbatim in its rendition; negation-marker presence
     check; modality mapping check in **warning mode** (observed, not
     blocking, until dogfood measures coverage). Lint failure →
     regenerate once, no revision loop; second failure surfaces to
     user.
3. **Touchpoint wiring** — pointer lines at the presentation moments,
   not copied rules:
   - `brainstorming/SKILL.md` sign-off checkpoint (:219)
   - `writing-plans/SKILL.md` plan-presentation moments (kickoff
     briefing :123-129, post-PASS card :130-142)
   - `requesting-code-review/SKILL.md` Step 5 (:118) +
     `references/relay-phrasing.md`
   - `requesting-docs-review/SKILL.md` (:52, :125)
   The machine-precise verdict-block fence
   (`requesting-code-review/SKILL.md:16-22`) stays untouched — views
   are additive beside the record.
4. **Conditions**: fires only when live conversation language is not
   English; verdict digest fires only when findings ≥ 1 (PASS headline
   is already localized by the family rollup card).

Finding identity key = `where` + `dimension` (findings carry no ID
field — recon Task B); document unit key = section heading / task ID
(plans carry task IDs and structured fields).

## Trigger occasions (v1)

| # | Moment | Path | Rendition |
|---|---|---|---|
| 1 | Plan review gate — user approves the plan | writing-plans presentation moments | EN/ZH side-by-side HTML (+ inline pointer) |
| 2 | Brief sign-off checkpoint | brainstorming :219 | EN/ZH side-by-side HTML (+ inline summary as today) |
| 3 | Whole-branch review verdict presentation | requesting-code-review Step 5; inherited by finishing Step 3 via delegation | inline markdown findings table; HTML on volume/request |
| 4 | Docs-review verdict + delta-confirmation + STILL_BLOCKING / out_of_scope | requesting-docs-review :52/:69/:125 | same as #3 |

## Current State Evidence

- **Forward**: 26 adjudication touchpoints across 9 files, 4 artifact
  classes — brief (1), plan (5), verdict (11), close-out (9). Document
  presentation flows: `brainstorming/SKILL.md:219` (sign-off
  checkpoint "surface … require explicit user sign-off"),
  `writing-plans/SKILL.md:123-142` (kickoff briefing + post-PASS plan
  card), `requesting-code-review/SKILL.md:118` (Step 5 "Print the
  verdict + findings … let user decide"),
  `finishing-a-development-branch/SKILL.md:118-130` (Step 3 surfaces
  findings), `requesting-docs-review/SKILL.md:52`.
- **Reverse (SSOT ownership)**: ask-phrasing SSOT =
  `subagent-driven-development/SKILL.md:23-58` (①②③ gates); clone
  `requesting-code-review/references/relay-phrasing.md:26-44`; card
  form SSOT = `loom-pipeline/hooks/family-relay.md:13-15,25-27,81-88`.
  family-relay §(d) (:109-118) already points cross-plugin at the
  loom-code ③ gate — the new protocol lives in loom-code; family-relay
  needs no edit in v1.
- **Error (today's failure mode)**: no rule mandates rendering artifact
  BODY content in the user's language — existing rules cover card slot
  content (`family-relay.md:15`), jargon translation
  (`subagent-driven-development/SKILL.md:45-47`), and "don't dump the
  raw verdict block" (`relay-phrasing.md:27-28`); the plan/brief body
  reaches the user in English; ad-hoc partial translation is unguarded
  (error classes catalogued in the research notes).
- **Data (schemas)**: finding shape
  `requesting-code-review/SKILL.md:141-148` — severity 🔴🟡🟢 /
  dimension / `where` (required) / source / note / origin / class; no
  ID field. Docs variant `requesting-docs-review/SKILL.md:75-120` adds
  `quote:` + `reviewed_sha`. Plan task fields
  `writing-plans/SKILL.md:166-187` (schema SSOT
  `references/plan-format.md`): Description / Module / Files touched /
  Acceptance RED-GREEN / Dependencies / Independent / `Gloss: <one
  line, user's conversation language>` (:186) — the existing per-task
  Gloss is a headline, not a body rendition; the document view
  supersedes reading-by-Gloss at the review gate.
- **Boundary**: (a) machine-precise fence — verdict block and plan
  file on disk are never rewritten
  (`requesting-code-review/SKILL.md:16-22`, `family-relay.md:25-27`);
  views are disposable, scratchpad-only, never committed; (b) naming —
  finishing uses "digest silently" = suppress iterations
  (`finishing-a-development-branch/SKILL.md:139-142`); mechanism name
  must avoid bare "digest" in that vocabulary; (c) stale-scan stdout
  relays VERBATIM (`finishing-a-development-branch/SKILL.md:203`) —
  duty explicitly does not apply; (d) ScheduleWakeup/loop prompts and
  machine artifacts (brief/verdict/commit) stay English per repo
  language policy.

Evidence paths appendix: loom-code/skills/{brainstorming,writing-plans,requesting-code-review,requesting-docs-review,subagent-driven-development,finishing-a-development-branch,dispatching-parallel-agents}/SKILL.md; loom-code/skills/requesting-code-review/references/relay-phrasing.md; loom-code/skills/writing-plans/references/plan-format.md; loom-pipeline/hooks/family-relay.md.

## Decision

Build: protocol file + split/translate/reassemble renderer with EN/ZH
side-by-side HTML for documents + findings-table rendition for
verdicts + zero-token lint (modality warning-mode) + wiring at four
skills' presentation moments. Structured intermediate is the canonical
digest form; markdown and HTML are renderings of it. One loom-code
version bump + `.codex-plugin` mirror sync.

NOT build (v1): SDD per-task verdict wiring (own SSOT, untouched);
close-out/spec-class views; back-translation spot-check tier (no cheap
scorer — QE omission blind spot; re-evaluate v2); verdict-schema ID
field; enforcement hook (legislate only if dogfood shows the prose
duty skipped); sibling-plugin wiring; Japanese variant.

Grounding: three research notes (Obsidian vault, research/,
2026-08-12) — error taxonomy w/ literature anchors, industry precedent
table (JTF severity, 法務省 modality lock, Xbench lint prior art, ICH
back-translation independence), implementation-absence survey.

## Out of Scope

- Any change to verdict block schema, plan schema, or gate marker
  formats (machine layer untouched)
- family-relay.md edits (loom-pipeline)
- loom plugin consolidation (parked:
  `docs/loom/backlog/2026-08-12-loom-plugin-consolidation-needs-sync-cost-data.md`)
- Global (non-loom) duty; dev-workflow:brief-before-asking
  cross-reference (revisit v2)
- Committing any rendered view to git (disposable by design)

## What Becomes Obsolete

- Ad-hoc unguarded translation at presentation moments (replaced by
  protocol-governed renditions) — behavioral replacement, no file
  deletion.
- Reading-by-Gloss as the de-facto plan-review aid (Gloss stays as the
  card headline; the review gate now gets a full body view).
- Flag: otherwise purely additive — accepted because the addition
  closes a documented contract gap (recon Task C: zero existing
  artifact-body localization mandate).

## Open Questions

1. Mechanism name — avoid bare "digest" (finishing collision). Decide
   at writing-plans; grep-verify.
2. Rider backlog items now triggered: anti-copy acceptance greps
   (start: next writing-plans SKILL.md touch — **now triggered**, v1
   touches it); change-binding chain integration test (next loom-code
   touch — triggered). Bundle-or-defer decision at plan stage.
3. DIRECTION bet: `## Now` empty — promotion to COMMITTED-NEXT is the
   user's call at close-out.
4. Dogfood metrics: modality-mapping coverage on real prose; lint
   false-positive rate (number formats, term variants); whether the
   prose duty gets skipped (enforcement-hook trigger).
5. Section-split granularity for briefs (H2 vs H3) — decide at plan
   with a real brief as fixture (this file is a candidate fixture).
