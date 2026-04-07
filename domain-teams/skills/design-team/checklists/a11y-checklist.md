# Accessibility Checklist Gate

## Evaluation Instructions

You are a strict accessibility auditor. Check each item below against the
design output or frontend code. You MUST give `PASS`, `FAIL_FATAL`, or
`FAIL_FIXABLE` for each item, with specific evidence.
The failure type for each item is defined below — use the type specified.

## Checklist

- [ ] **CHK-A11Y-001 (Alt Text)** [FIXABLE]: All meaningful images have descriptive alt text. Decorative images have `alt=""` or `role="presentation"`.
- [ ] **CHK-A11Y-002 (Contrast)** [FATAL]: Text contrast ratio meets WCAG AA — ≥ 4.5:1 for normal text, ≥ 3:1 for large text (≥18pt or ≥14pt bold).
- [ ] **CHK-A11Y-003 (Keyboard)** [FATAL]: All interactive elements are reachable and operable via keyboard. No focus traps exist.
- [ ] **CHK-A11Y-004 (Focus Indicator)** [FIXABLE]: Visible focus indicator exists on all focusable elements.
- [ ] **CHK-A11Y-005 (Touch Targets)** [FIXABLE]: Interactive touch targets are ≥ 44×44 CSS pixels.
- [ ] **CHK-A11Y-006 (Landmarks)** [FIXABLE]: Page has semantic landmark structure (main, nav, header, footer). Not all-divs.
- [ ] **CHK-A11Y-007 (ARIA Hygiene)** [FATAL]: ARIA attributes are used only when native HTML is insufficient. No invalid or conflicting ARIA roles.
- [ ] **CHK-A11Y-008 (Form Labels)** [FIXABLE]: All form inputs have properly associated labels (explicit `for` or wrapping `<label>`).

## Verdict Rules

- Any **1 item** is `FAIL_FATAL` → final verdict is `NEEDS_REVISION` (escalate to user)
- Only `FAIL_FIXABLE` items (no FATALs) → final verdict is `PASS_WITH_NOTES` (trigger auto-revise)
- All items are `PASS` → final verdict is `PASS`

## Output Format

```json
{
  "verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "checklist_results": [
    {
      "id": "CHK-A11Y-001",
      "status": "PASS | FAIL_FATAL | FAIL_FIXABLE",
      "evidence": "Specific element reference or WCAG criterion",
      "fix_instruction": "How to resolve (for FAIL_FIXABLE items)"
    }
  ]
}
```

Reference `standards/wcag-baseline.md` for the full WCAG rules these checks derive from.
