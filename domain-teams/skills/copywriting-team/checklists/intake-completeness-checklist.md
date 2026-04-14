# Checklist: Intake Completeness

MUST gate (binary pass/fail). Trigger: after
`copywriting-brainstorming.md` §Task 9 Understanding Summary output,
before loading the next-phase protocol. This gate is a prerequisite
gate common to all copywriting-team workflows (long / mid / short /
ideation / audit); it blocks next-phase progress when Level 1 fields
are incomplete.

## Primary Sources

- `../protocols/copywriting-brainstorming.md` — Intake source for this
  gate. Verifies fields collected in Tasks 2-5.
- `../standards/persuasion-psychology-anchor.md` §Schwartz 5 Levels
  of Awareness — basis for the long-form awareness level field.
- `../standards/short-form-catchcopy-canon.md` §5 種切入点決策樹 —
  prerequisite for mapping target emotion / pain → approach in
  short-form.
- `../standards/long-form-pasona-canon.md` §PASONA 系列使い分け表 —
  prerequisite for long-form framework selection.
- `../standards/mid-form-beaf-canon.md` — Mid-form BEAF prerequisite
  (benefits list required).

## Evaluation Instructions

You are a strict auditor. Check each item below against the worker's
Understanding Summary output. Give `PASS`, `FAIL_FATAL`,
`FAIL_FIXABLE`, or `N/A` for each item, with specific evidence
(quoted line or artifact reference).

Failure type for each item is defined below — use the type specified.

`N/A` is permitted **only for items that do not apply to the relevant
form type**. Example: CHK-CTW-INTAKE-L01 (long-form word count range)
is `N/A` for form_type = short.

## Checklist

### Common items (all form types)

- [ ] **CHK-CTW-INTAKE-001 (Form type declared)** [FATAL]: Understanding
  Summary §Form Type explicitly specifies one of `long / mid / short /
  ideation / audit`. Ambiguous expressions such as "something like a
  catch" or "various copy" → FATAL. **Grounded in**:
  `../protocols/copywriting-brainstorming.md` §Task 2.
- [ ] **CHK-CTW-INTAKE-002 (Product / service)** [FATAL]: Understanding
  Summary §Product / Value Proposition explicitly states the product /
  service name + main value proposition (1 sentence). Abstract labels
  such as "some good product" or "services in general" → FATAL. A
  reference to PRODUCT-SPEC.md or planning-team output that
  concretizes the proposition → PASS. **Grounded in**:
  `../protocols/copywriting-brainstorming.md` §Task 3.
- [ ] **CHK-CTW-INTAKE-003 (Target audience)** [FATAL]: Understanding
  Summary §Target Audience explicitly contains at least 1 concrete
  piece of information (demographic / persona / segment / role).
  Unbounded labels such as "general consumers" or "broadly everyone"
  → FATAL. **Grounded in**:
  `../protocols/copywriting-brainstorming.md` §Task 4.
- [ ] **CHK-CTW-INTAKE-004 (Understanding Summary structure)**
  [FIXABLE]: The Understanding Summary block contains the 9
  subsections defined in `copywriting-brainstorming.md` §Task 9
  (Request / Form Type / Product / Target Audience / Form-Specific
  Spec / Voice Reference / Framework / Confirmed Assumptions /
  Resolved Ambiguities / Level 2/3 Defaults Accepted). Missing
  subsections → FIXABLE. **Grounded in**:
  `../protocols/copywriting-brainstorming.md` §Task 9.

### Long-form items (form_type = long)

- [ ] **CHK-CTW-INTAKE-L01 (Word count range)** [FATAL]: Understanding
  Summary §Form-Specific Spec explicitly states a word-count range
  (e.g., 800-1200 / 2000-3000 / 5000+). This is a prerequisite for
  framework selection and stage composition. Not specified → FATAL.
  form_type ≠ long → `N/A`. **Grounded in**:
  `../protocols/copywriting-brainstorming.md` §Task 5 Long-form +
  `../standards/long-form-pasona-canon.md` §使い分け表.
- [ ] **CHK-CTW-INTAKE-L02 (Schwartz awareness level)** [FATAL]:
  Understanding Summary §Target Audience or §Form-Specific Spec
  explicitly states one of the Schwartz 5 levels (Unaware /
  Problem-Aware / Solution-Aware / Product-Aware / Most-Aware).
  Silently adopting an AI recommendation without disclosure → FATAL
  (risks violating the Schwartz core rule "no direct Offer to
  Unaware"). If an AI recommendation is explicitly approved by the
  user, disclosure in §Level 2/3 Defaults Accepted is required; with
  disclosure → PASS. form_type ≠ long → `N/A`. **Grounded in**:
  `../standards/persuasion-psychology-anchor.md` §Schwartz 5 Levels
  of Awareness.
- [ ] **CHK-CTW-INTAKE-L03 (Framework choice)** [FIXABLE]: Understanding
  Summary §Framework explicitly states 旧 PASONA / 新 PASONA /
  PASBECONA, or user approval of an AI recommendation (auto-pick) is
  disclosed in §Level 2/3 Defaults Accepted. Not specified + no
  disclosure → FIXABLE (can be finalized in `write-long-form-copy.md`
  §Phase 1, but the omission at intake must be noted). form_type ≠
  long → `N/A`. **Grounded in**:
  `../standards/long-form-pasona-canon.md` §使い分け表 +
  `../protocols/copywriting-brainstorming.md` §Task 7 Long-form.

### Mid-form items (form_type = mid)

- [ ] **CHK-CTW-INTAKE-M01 (Benefits list)** [FATAL]: Understanding
  Summary §Form-Specific Spec explicitly lists **3 or more concrete
  benefits**. An abstract single item like "various benefits" or
  "good quality" → FATAL (BEAF's Benefit stage cannot function).
  form_type ≠ mid → `N/A`. **Grounded in**:
  `../protocols/copywriting-brainstorming.md` §Task 5 Mid-form +
  `../standards/mid-form-beaf-canon.md`.
- [ ] **CHK-CTW-INTAKE-M02 (Channel)** [FIXABLE]: Understanding Summary
  §Form-Specific Spec explicitly states the channel (Rakuten / Amazon
  JP / in-store POP / seminar, etc.). Not specified → FIXABLE (BEAF
  ordering tweaks depend on channel, but the default order can
  proceed). form_type ≠ mid → `N/A`. **Grounded in**:
  `../protocols/copywriting-brainstorming.md` §Task 5 Mid-form.

### Short-form items (form_type = short)

- [ ] **CHK-CTW-INTAKE-S01 (Target emotion / pain)** [FATAL]:
  Understanding Summary §Target Audience or §Form-Specific Spec
  explicitly states the target emotion / pain (e.g., "aspiration,"
  "anxiety," "curiosity," "anger" — 1 word + concrete context). Not
  specified → FATAL (cannot map to the 5 切入点 → approach selection
  impossible). form_type ≠ short → `N/A`. **Grounded in**:
  `../standards/short-form-catchcopy-canon.md` §5 種切入点決策樹 +
  `../protocols/copywriting-brainstorming.md` §Task 4 Short-form.
- [ ] **CHK-CTW-INTAKE-S02 (Intended channel)** [FATAL]: Understanding
  Summary §Form-Specific Spec explicitly states the intended channel
  (SNS / banner / tagline / CM / in-store / station ad, etc.). Not
  specified → FATAL (prerequisite for character-count ceiling + voice
  selection). form_type ≠ short → `N/A`. **Grounded in**:
  `../protocols/copywriting-brainstorming.md` §Task 5 Short-form.

### Audit items (form_type = audit)

- [ ] **CHK-CTW-INTAKE-A01 (Existing copy full text)** [FATAL]:
  Understanding Summary §Form-Specific Spec includes the **full text**
  of the existing copy (summary / excerpt is not acceptable). Summary
  only → FATAL (`copy-audit.md` Phase 1 Type ID cannot function).
  form_type ≠ audit → `N/A`. **Grounded in**:
  `../protocols/copywriting-brainstorming.md` §Task 5 Audit +
  `../protocols/copy-audit.md`.
- [ ] **CHK-CTW-INTAKE-A02 (Review focus)** [FIXABLE]: Understanding
  Summary §Form-Specific Spec explicitly states the review focus
  (framework / ethics / voice / form-appropriate / overall). Not
  specified → FIXABLE (proceeds with default = overall, but scope
  widens). form_type ≠ audit → `N/A`. **Grounded in**:
  `../protocols/copywriting-brainstorming.md` §Task 5 Audit.

### Ideation items (form_type = ideation)

- [ ] **CHK-CTW-INTAKE-I01 (Value proposition source)** [FATAL]:
  Understanding Summary §Product / Value Proposition explicitly states
  the value prop source (user-supplied / planning-team output /
  PRODUCT-SPEC.md reference / other). If source is unknown + value
  prop remains abstract → FATAL (cannot function as input for
  divergent subagents). If user-supplied with a concrete 1-sentence
  value prop → PASS. form_type ≠ ideation → `N/A`. **Grounded in**:
  `../protocols/copywriting-brainstorming.md` §Task 5 Ideation +
  `../protocols/copy-ideation-parallel.md` §Phase 1 §入力確認.

### Level 2 disclosure item (all form types)

- [ ] **CHK-CTW-INTAKE-D01 (Level 2 defaults disclosed)** [FIXABLE]:
  Any items from Task 6 voice / Task 7 framework & approach where the
  user did not explicitly choose and AI recommendation was adopted are
  disclosed in Understanding Summary §Level 2/3 Defaults Accepted.
  Silent default (no user approval + no disclosure) → FIXABLE.
  **Grounded in**: `../protocols/copywriting-brainstorming.md` §Rules
  §Level 2 default adoption must be stated in Summary.

## Verdict Rules

- Any single item `FAIL_FATAL` → `NEEDS_REVISION` (return BLOCKED to
  main agent, go back to brainstorming phase)
- Only `FAIL_FIXABLE` (no FATAL) with **≤ 2 items** → `PASS_WITH_NOTES`
  (auto-revise trigger; supplement brainstorming Task 9 Summary once
  and re-evaluate)
- `FAIL_FIXABLE` in **≥ 3 items** → `NEEDS_REVISION` (return to entire
  brainstorming)
- All items `PASS` or `N/A` → `PASS` (permit loading next-phase
  protocol)
- `N/A` is permitted **only for items that do not apply to the form
  type**. form_type = long means L01-L03 are evaluated, M/S/A/I-prefix
  items are `N/A`. form_type = mid means M01-M02 are evaluated,
  L/S/A/I-prefix items are `N/A`. And so on.

## Output Format

```json
{
  "verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "form_type": "long | mid | short | ideation | audit",
  "items": [
    {
      "id": "CHK-CTW-INTAKE-001",
      "status": "PASS | FAIL_FATAL | FAIL_FIXABLE | N/A",
      "evidence": "Specific Summary section reference or quoted line",
      "fix_instruction": "How to resolve (for FAIL_FIXABLE items); which brainstorming task to revisit (for FAIL_FATAL items)"
    }
  ],
  "summary": "1-3 sentence overall assessment + which Level 1 fields are missing if NEEDS_REVISION",
  "next_action": "load {protocol_name} | return to brainstorming Task {N} | auto-revise Summary"
}
```
