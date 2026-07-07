# Loom user-communication overhaul — brief + plan (2026-07-07)

## Problem (upstream artifacts)

The user cannot reliably understand the implementation choices loom-*
asks them to decide, despite 8 documented fix attempts since 2026-05
(brief-before-asking v1.0→Mode D, the 7 plain-language rules → 3-gate
redesign, ascii-graph-toolkit v1-v3, three dotfiles rule edits, #475
complex-fork escalation). Every attempt shipped without measuring user
comprehension; same failure classes recur.

Transcript baseline (11 real sessions / 8 project dirs, method + all
citations in `docs/loom/audits/2026-07-06-loom-comms-transcript-baseline.md`):

- **B1 language drift**: English skill bodies flip 繁中 conversations to
  English narration — worst session 70% EN assistant turns; user now
  pins a standing 「請以繁體中文回覆」 in handoff prompts (workaround
  institutionalized = recurring failure).
- **B2 jargon pass-through at sign-offs**: seam test / dangling tag /
  PASS_WITH_NOTES reach the user raw; canonical case ends with 「我還是
  不知道你要我決定的東西的意義與影響」, resolved in ONE turn once plain
  metaphor + table finally produced — capability exists, trigger doesn't.
- **B3 menu-before-brief**: AskUserQuestion fires with no chat-visible
  brief; verdict walls (8 findings at once) force the user to impose
  pacing (「一個一個來 請先用視覺化說明」).
- **B4 visuals miss the fork**: 54 asks quantified → 39% had any
  table/ASCII nearby; **9% (1/11) in real-app projects**. Visuals
  decorate research reports, skip decisions; two were defective
  (English labels in a 繁中 session; factually wrong 🔒 diagram).
- **B5 SDD narration = orchestrator console**: Wave/impl-t3/PASS traffic
  with no rollup in user terms.

Skill-source survey (2026-07-06 agent sweep): plain-language relay rules
exist and are strong in loom-code (brainstorming, SDD,
requesting-code-review) + dev-workflow:brief-before-asking, but are
ABSENT from loom-spec / loom-interface-design / loom-product-principles
(BACKLOG: loom-spec briefing gate OPEN); the visual catalog is
Mermaid-only (doesn't render in terminal); ascii-graph-toolkit is
referenced nowhere in the loom family.

## Root causes

1. **Prose rules lose to context register.** Failures cluster deep in
   execution where thousands of English skill/verdict/report lines
   dominate context. Machine-facing templates are followed exactly;
   distant prose rules are not. Templates beat rules.
2. **Rules gate asking, not narrating.** The three-gate discipline covers
   AskUserQuestion moments; execution narration and checkpoint sign-offs
   have no gate at all. Design-side plugins have no relay rules.
3. **No executable visual path.** Prescribed form (Mermaid) doesn't
   render in the actual channel; the tool that does (ascii-graph-toolkit,
   markdown tables) is wired to nothing.
4. **Acceptance never measured comprehension.** All 8 attempts verified
   "rule text exists" / "skill contract passes"; the loop is open —
   regressions invisible.

## Industry evidence (deep-research 2026-07-07; 28 sources fetched, 25 claims 3-vote verified, 0 refuted)

- **Language drift is mechanical surface statistics** — script
  proportion + strong recency bias toward the FINAL tokens of context
  (p<0.001); the bottleneck is *inferring* the expected language, and
  explicit directives are the right lever but model-fragile
  (OLA, KAIST 2026, arxiv.org/pdf/2601.03589).
  → deterministic language detection + tail-of-context anchor.
- **"The model forgot" is folklore** — models violate constraints they
  can restate at 97.3% accuracy (knows-but-violates up to 99%); per-turn
  critic reminders give only marginal gains (DriftBench,
  arxiv.org/pdf/2604.28031). → output-side deterministic validation over
  more prose. (Direction supported; no production-measured numbers
  survived verification — measure ourselves.)
- **Reminder re-injection reliably reduces drift** but is partial and
  model-dependent (arxiv.org/abs/2510.07777).
- **Multi-turn degrades all top models ~39%** (−15% aptitude, +112%
  unreliability); models don't recover once lost → early cheap
  alignment checkpoints (Laban et al., ICLR 2026 oral,
  arxiv.org/abs/2505.06120).
- **Product convergence: layered plain-language checkpoints** — Copilot
  Workspace (restated topic as cheap first checkpoint; current-state
  spec in plain bullets; proposed spec as natural-language success
  criteria; editable checkpoints; per-item progress) and Devin
  (plan-approval gate) — all plain text, terminal-portable
  (github.com/githubnext/copilot-workspace-user-manual;
  cognition.com/blog/dec-24-product-update). Peer-reviewed backing:
  HAX G11 (CHI 2019). NOTE: the strongest exemplars are layered plain
  TEXT, not diagrams — visuals are secondary, on-pattern (comparison
  tables at option forks), not decoration.
- **Evidence gaps (honest)**: guardrails-framework production effects
  and user-comprehension telemetry produced ZERO surviving claims —
  homegrown simple metrics are justified; nothing to copy.

## Smallest end state

Four cuts, each independently shippable, ordered by leverage:

1. **Language-consistency mechanics (dynamic — never a hardcoded
   language)** [decision 2026-07-07: follow the user's CURRENT
   conversation language 中/日/英, not fixed zh]:
   a. Shared detection helper: infer conversation language from recent
      user main-chain turns (kana → ja; Han without kana → zh-TW;
      mostly-ASCII → en; mixed → most recent wins). Pure code, no model
      judgment.
   b. Tail anchor: hook injects a one-line directive in (and naming)
      the detected language after large English context loads.
   c. Stop-hook validator: detected conversation language vs reply body
      (code fences stripped, technical-term allowance via ratio
      threshold); mismatch → block with corrective reminder.
2. **User-rollup card** at the narration seams (SDD per-wave report,
   checkpoint sign-offs, review relay): mandatory template slots with
   fixed semantics — task restated / current state / what changed /
   impact on you / next + decision — content in the conversation
   language (supplied by 1b, structure by the template). ≥2 options →
   markdown comparison table; flow/state shape → ascii-graph-toolkit
   (CJK width-aware); replace the Mermaid-only catalog with
   channel-aware degradation (terminal → table/ASCII).
3. **Family relay SSOT**: extract the relay discipline (translate
   jargon, stakes-first, brief-then-ask, visual defaults) into ONE
   shared reference; loom-code skills and loom-spec /
   loom-interface-design / loom-product-principles point to it
   (point-never-copy). Closes BACKLOG "loom-spec briefing gate". Fold in
   the buried-briefing fix (briefing ends the turn; ask comes inline or
   next turn — memory: briefing-buried-by-askuserquestion-same-turn).
4. **Comms metrics recipe**: repeatable audit (script or distill recipe)
   computing (a) confusion-signal rate per fork (re-asks, 「什麼意思」,
   ？？, ESC), (b) wrong-language turn ratio, (c) visual-at-fork rate.
   Baseline = the 2026-07-06 audit doc. Acceptance for ANY future comms
   change = these numbers move, not "rule text exists".

## Non-goals

- No hardcoded output language anywhere (中文 included) — language is
  always resolved from the live conversation.
- Machine-facing artifacts unchanged: briefs, verdict blocks, gate
  markers, commits stay English/project-convention; only the user-relay
  layer is dynamic (matches dotfiles conversation-vs-artifacts contract).
- No new plugin; changes land in loom-code, dev-workflow, and family
  shared references.
- Not relitigating brief-before-asking's core design (Modes A–D stay);
  only the buried-briefing turn-ordering and the anti-diagram wording.
- No attempt to fix Mermaid rendering in terminals; degrade instead.

## Acceptance

1. Cut 1: RED→GREEN unit tests for detection + validator edge cases
   (ja/zh/en, mixed, code-fence stripping, term allowance). Live probe:
   in a zh session load an English skill → next narration zh; en session
   stays en; ja session → ja. No false block on English-only sessions.
2. Cut 2: cold-reader dogfood — fresh-context agent runs an SDD
   checkpoint + a review relay with the template on a real repo; output
   is in the conversation language, every internal term translated or
   defined, option forks carry a comparison table.
3. Cut 3: grep proves pointers-not-copies; loom-spec briefing-gate
   BACKLOG item closed; buried-briefing regression covered by a test or
   documented probe.
4. Cut 4: recipe re-run reproduces the baseline numbers from the audit
   doc; report lands in docs/loom/audits/.
5. Post-ship (deferred, after ~10 real sessions): re-run the audit —
   targets: wrong-language turn ratio <10%, visual-at-fork ≥50% where
   ≥2 options compared, zero undefined internal terms at sign-offs.

## Provenance

- Diagnosis: 3-agent sweep 2026-07-06 (skill sources / cross-repo
  attempts / transcript mining) — baseline audit doc cited above.
- Industry research: deep-research workflow 2026-07-07, 111 agents,
  findings 3-vote adversarially verified; full result in session
  workflow output (key claims + URLs inlined above).
- User decisions this thread: dynamic conversation language (not fixed
  zh); plain-language layering is the load-bearing fix, visuals
  repositioned as secondary; write docs first, then implement.
