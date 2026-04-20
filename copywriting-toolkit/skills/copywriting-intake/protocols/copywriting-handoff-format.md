# Copywriting Handoff Format Protocol

Standard output format for copywriting-team candidates and finished copy + pipeline
progress reporting. Defines candidate presentation methods and user intervention points.

## Primary Sources

- `copy-ideation-parallel.md` §Phase 3 Handoff — already defines the candidate
  output format (3-5 winners + "なぜ良いか" 3 items + 3-5 runner-ups +
  A-type diagram). This protocol generalizes that into a common format
  applicable beyond ideation to long / mid / short / audit workflows.
- `copywriting-brainstorming.md` §Task 9 Understanding Summary —
  structured spec from the intake phase. Re-present it at handoff to
  show correspondence between the spec and the candidates.
- `../standards/ideation-taniyama-discipline.md` §「なんかいいよね
  禁止」— basis for the mandatory 3-item rationale.
- `../standards/short-form-catchcopy-canon.md` §5 種切入点決策樹 +
  `../standards/long-form-pasona-canon.md` — vocabulary source for
  approach / framework labels.

## Section 1: Candidate Output Format

When presenting candidates (short-form headlines / long-form drafts /
mid-form BEAF blocks), always include the following 6 elements:

```
Candidate #N: [copy body]
├─ voice reference: [糸井 / 岩崎 / 眞木 / 谷山 / Ogilvy / default]
├─ approach / framework:
│   - short-form: one of the 5 approaches (利益 / 恐懼 / 顛覆 / 呼喚 / 提問)
│   - mid-form: BEAF order + channel tag (楽天 / Amazon / POP / briefing)
│   - long-form: PASONA series framework name (旧 / 新 / PASBECONA) + per-stage
│   - ideation: Mandal-Art direction + VS probability
├─ VS probability (only for ideation Phase 1 output): p = 0.xx
├─ Why it works (3 items, mandatory, 「なんかいいよね」禁止):
│   1. What is conveyed to whom
│   2. What is new relative to existing similar copy
│   3. What resonates in the target's life / context
└─ ethics self-check: [pass / concern + explanation]
    - Self-scan result for risky expressions under 景品表示法 / FTC / ステマ告示
    - If concern exists, note that it will be escalated to the ethics-checklist.md MUST gate
```

### Long-form draft presentation variation

Long-form drafts (2,000+ chars) often present only 1 full-text candidate.
In that case:

- Present the 6-element block above as opening metadata
- Add subsection headings per stage (Affinity / Problem / Offer /
  Narrowing / Action, etc.), annotating the voice / psychology technique
  used in each stage
- Include word count at the end (`{actual} / {target range}` format)

### Audit variant rewrite format

When presenting rewrite variants in `copy-audit.md` Phase 3, display the
6-element block side by side for each variant. Add a 1-sentence "diff from
original" summary at the top of each variant.

## Section 2: Progress Reporting Templates

When the pipeline enters multi-phase operation, maintain user transparency
using the following templates.

### Phase start message

```
[Claude] Phase {X}-{Y} started: {protocol_name}
  Input: {input summary, 1 line}
  Plan: {step sequence within the phase}
```

Example:
```
[Claude] Phase 1-3 started: copy-ideation-parallel.md Phase 1 divergence
  Input: product=X, audience=Y, form=short
  Plan: Mandal-Art 8-direction dispatch → VS candidate generation → 64-candidate aggregation
```

### Step-by-step progress indicator

```
 Step 1/8: Mandal-Art direction decision — selecting 8 directions
 Step 1/8: Mandal-Art direction decision — {情感觸發 / 掛詞 / 逆説 / ...}
 Step 2/8: subagent dispatch — launching 8 parallel agents
 Step 2/8: subagent dispatch — 8 agents running in parallel
...
```

Incomplete is ` `, complete is ` `. Failure is ` ` + 1-line cause. Skipped
step is `—` + 1-line skip reason.

### Phase completion checkpoint message

```
[Claude] Phase {X} complete: {phase_name}
  Artifact: {artifact summary}
  Steps: {step count}, {duration if relevant}

Next options:
   continue — proceed directly to Phase {X+1}
   adjust — adjust Phase {X} results before proceeding
   retry — re-run Phase {X} (with changed inputs)
   stop — stop here and return to user

If no user input, {default option} will be adopted.
```

Default option selection rules:

- ideation Phase 1 → Phase 2: default is `continue` (if 64-100 candidate
  mode collapse check passed)
- ideation Phase 2 complete: default is `adjust` (user selection
  checkpoint for 3-5 winners)
- long-form draft complete: default is `adjust` (word count / voice /
  per-stage adjustment confirmation)
- after gate failure: default is `stop` (NEEDS_REVISION always waits
  for user judgment)

## Section 3: Mid-Pipeline Checkpoint Rules

The following checkpoints are non-skippable. Silent proceed is an anti-pattern.

### After ideation Phase 2 (KJ convergence) completes

Immediately after `copy-ideation-parallel.md` §Phase 2 §Narrativization + 谷山 review:

- **Always present the 3-5 winning angles to the user** for selection
  - (a) `accept all` → adopt all 3-5 as seeds for subsequent protocol
  - (b) `pick subset` → manually select 1-3 as a subset
  - (c) `reject, redo` → return to Phase 1 divergence with changed directions
- Also present the 3-5 runner-ups as an appendix (for A/B variants)
- Skipping and immediately proceeding to the next phase is an anti-pattern

### After long-form draft (> 2,000 chars) completes

Default is **staged presentation**:

1. Present the draft's outline first (per-stage heading + 1-sentence summary per stage)
2. User specifies which stage to view → present that stage's full text only
3. After per-stage adjustments are complete, present the full final text

Present all at once only when the user explicitly says "show me everything at once".
All-at-once presentation for 2,000+ chars is **not the default behavior**.

### When Gate NEEDS_REVISION occurs

When any MUST / SHOULD gate returns `NEEDS_REVISION`:

- Present the gate name + the failed checklist item / rubric dimension
- Present a concrete fix direction (evaluator's fix_instruction)
- Offer the user these options:
  - `auto-retry` → restart worker for automatic fix (max 2 rounds as a rule)
  - `manual` → user writes fix instructions and re-dispatches
  - `override` → user accepts this gate failure (not recommended; must record reason)

Silent auto-retry is prohibited. Always show the gate failure to the user.

### When Gate PASS_WITH_NOTES occurs

Present the feedback, then auto-revise runs. However, **report what was
fixed** to the user in 1 line after completion:

```
[Claude] auto-revise complete (PASS_WITH_NOTES feedback addressed)
  Fix: {diff summary, 1-2 lines}
```

A second PASS_WITH_NOTES triggering re-revise is **escalated to
NEEDS_REVISION** (`SKILL.md §Gate Protocol §Max 2 rounds before escalating`).

## Section 4: Audit Report Format

Final deliverable format for `copy-audit.md`:

### Type ID block

```
## Audit Type ID

- Form type detected: {long / mid / short}
- Framework detected: {新 PASONA / BEAF / 利益切入 / unknown / etc.}
- Voice pattern detected: {糸井系 / 岩崎系 / Ogilvy系 / mixed / etc.}
- Channel (inferred): {LP / EC / SNS / CM / etc.}
```

### Issues by severity

Issues sorted by severity; within the same severity, by artifact appearance order:

```
## Issues

### HIGH — {count} items
1. **{issue title}**
   - Location: {quoted line / paragraph reference}
   - Problem: {what's wrong, 1-2 sentences}
   - Grounded in: {standard file or checklist item id}
   - Fix suggestion: {concrete before → after proposal}

### MEDIUM — {count} items
...

### LOW — {count} items
...
```

Severity definitions:

- **HIGH** — Legal risk / fatal framework violation / 景品表示法 or
  FTC risk (ethics-checklist.md FATAL equivalent)
- **MEDIUM** — Framework order deviation / voice drift / form mismatch
  (SHOULD gate equivalent)
- **LOW** — Minor word-count overshoot / inconsistent notation / polish
  deficiency (stylistic concern)

### Overall verdict + next actions

```
## Verdict

- Legal layer: {pass / risky / fatal} (景品表示法 / FTC / ステマ告示)
- Framework layer: {canonical / deviated / unclear}
- Voice layer: {consistent / drift / abstract}
- Form layer: {appropriate / overflow / underflow}

## Recommended Next Steps

- [ ] Fix HIGH items (blocker)
- [ ] Consider MEDIUM items (strongly recommend)
- [ ] Optional LOW items (polish)
- [ ] Generate rewrite variants if needed (→ Phase 4 ethics gate subject)
```

User options:

- `fix-and-redeliver` → worker consumes the checklist above, re-handoff
  including rewrite variants
- `deliver-as-is` → user accepts current state (record reason if not
  recommended)
- `manual-only` → user fixes themselves, this team does not intervene

## Rules

- **Every candidate must have 3-item rationale**. 「なんかいいよね」禁止
  (谷山 2007 + `ideation-taniyama-discipline.md` §「なんかいいよね禁止」
  ルール). Candidates where 3 items cannot be written are deleted.
- **Label fields must not be blank**. Handing off with voice reference /
  approach / framework / channel as "unknown" is prohibited. If not
  confirmed during brainstorming phase, return to brainstorming.
- **Progress must be transparent**. Do not skip phase start / each step /
  phase completion reports. Silent multi-phase execution is an anti-pattern.
- **Mid-pipeline checkpoint skipping prohibited**. Presenting winning angles
  after ideation Phase 2, staged presentation for 2,000+ char long-form,
  and waiting for user judgment on gate NEEDS_REVISION are **mandatory
  checkpoints**.
- **Gate failure visibility**. When NEEDS_REVISION / PASS_WITH_NOTES occurs,
  always notify the user. Silent retry is prohibited.
- **Do not omit VS probability**. Ideation Phase 1 candidates are handed
  off with the VS probability field (`verbalized-sampling.md` §Anti-Patterns).
- **3-item rationale perspective discipline**. Write on the 3 axes: "what
  is conveyed / what is new / what resonates"
  (`ideation-taniyama-discipline.md` §3 項理由書テンプレート).

## Anti-Patterns

- **Presenting candidates without rationale**: "Candidate A / B / C — which
  do you prefer?" without attaching 3-item rationale. The canonical
  "なんかいいよね" anti-pattern (谷山 2007). The user ends up choosing by
  impression, and downstream quality is not guaranteed.
- **Hidden gate issues**: MUST gate returned NEEDS_REVISION but the user is
  not informed and silent retry runs. Not showing ethics gate failure to the
  user is dangerous (risk of papering over 景品表示法 violations with auto-fix).
- **Dumping 2,000+ char long-form output at once**: Ignoring the staged
  presentation default and outputting a 5,000-char LP all at once. Review
  cost for the user is enormous, and per-stage voice adjustment becomes
  impossible.
- **Silent retry on NEEDS_REVISION**: Gate demands revision but worker is
  restarted without user judgment. Max 2-rounds rule violation + user
  control is taken away.
- **Blank label fields**: Handing off with `voice reference: (undecided)`.
  Result of skipping voice selection in brainstorming phase. Violates
  intake gate PASS_WITH_NOTES disclosure obligation.
- **Progress reporting with only status markers and no context**: Just a
  check mark with no indication of which phase completed. Always include
  phase name / step name / artifact summary in 1 line.
- **Making default option a silent proceed**: Automatically adopting
  "continue" without waiting for user input at a checkpoint. The purpose of
  checkpoints is creating opportunities for user intervention — wait for at
  least one user acknowledgment.
- **Mixing severity levels in audit reports**: Listing HIGH and MEDIUM issues
  in the same sort. User misses blockers. Always section-separate by severity.
