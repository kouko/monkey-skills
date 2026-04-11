# Accessibility Checklist Gate

## Primary Sources

All checks derive their rules from `standards/wcag-baseline.md` (W3C
*Web Content Accessibility Guidelines (WCAG) 2.2*, W3C Recommendation
republished 2024-12-12, https://www.w3.org/TR/WCAG22/). SC numbers
and conformance levels below are pulled from that baseline's AA
Success Criteria table and §Touch Target Disambiguation.

**Critical attribution correction (v4.8.0).** CHK-A11Y-005 (Touch
Targets) previously claimed a `≥ 44×44 CSS pixels` threshold at the
WCAG AA level. That conflates two separate WCAG success criteria
with Apple / Material platform conventions. The correct partition
(per `standards/wcag-baseline.md` §Critical Attribution Corrections
and §Touch Target Disambiguation):

- **SC 2.5.8 Target Size (Minimum) = 24 × 24 CSS px at level AA** —
  the universal cross-platform WCAG baseline.
- **SC 2.5.5 Target Size (Enhanced) = 44 × 44 CSS px at level AAA** —
  an enhanced level, not the AA floor.
- Apple HIG 44 pt (iOS / iPadOS) and Material Design 3 48 dp (Android)
  are **platform conventions** stricter than WCAG AA, not WCAG values
  themselves; see `standards/platform-conventions.md`.

CHK-A11Y-005 is now written against the WCAG AA floor (24 × 24 CSS px)
and flags platform-specific obligations separately.

## Evaluation Instructions

You are a strict accessibility auditor. Check each item below against the
design output or frontend code. You MUST give `PASS`, `FAIL_FATAL`, or
`FAIL_FIXABLE` for each item, with specific evidence.
The failure type for each item is defined below — use the type specified.

## Checklist

- [ ] **CHK-A11Y-001 (Alt Text)** [FIXABLE] `[WCAG 2.2 SC 1.1.1 Non-text Content, A]`: All meaningful images have descriptive alt text. Decorative images have `alt=""` or `role="presentation"`.
- [ ] **CHK-A11Y-002 (Contrast)** [FATAL] `[WCAG 2.2 SC 1.4.3 Contrast (Minimum), AA]`: Text contrast ratio meets WCAG AA — ≥ 4.5:1 for normal text, ≥ 3:1 for large text (≥ 18 pt or ≥ 14 pt bold). For UI components and meaningful graphics, also meet `[SC 1.4.11 Non-text Contrast, AA]` (≥ 3:1).
- [ ] **CHK-A11Y-003 (Keyboard)** [FATAL] `[WCAG 2.2 SC 2.1.1 Keyboard, A + SC 2.1.2 No Keyboard Trap, A]`: All interactive elements are reachable and operable via keyboard. No focus traps exist.
- [ ] **CHK-A11Y-004 (Focus Indicator)** [FIXABLE] `[WCAG 2.2 SC 2.4.7 Focus Visible, AA + SC 2.4.11 Focus Not Obscured (Minimum), AA (new in 2.2)]`: Visible focus indicator exists on all focusable elements and is not entirely hidden by author-created overlays.
- [ ] **CHK-A11Y-005 (Touch Targets)** [FIXABLE] `[WCAG 2.2 SC 2.5.8 Target Size (Minimum), AA — 24 × 24 CSS px]`: Interactive touch targets meet the WCAG 2.2 AA floor of 24 × 24 CSS pixels. **SC 2.5.5 Target Size (Enhanced) AAA (44 × 44 CSS px) is opportunistic, not the AA baseline.** For iOS, additionally meet Apple HIG 44 × 44 pt; for Android, additionally meet Material Design 3 48 × 48 dp — these are platform conventions stricter than WCAG AA (see `standards/platform-conventions.md`).
- [ ] **CHK-A11Y-006 (Landmarks)** [FIXABLE] `[WCAG 2.2 SC 1.3.1 Info and Relationships, A + SC 2.4.1 Bypass Blocks, A]`: Page has semantic landmark structure (main, nav, header, footer). Not all-divs.
- [ ] **CHK-A11Y-007 (ARIA Hygiene)** [FATAL] `[WCAG 2.2 SC 4.1.2 Name, Role, Value, A]`: ARIA attributes are used only when native HTML is insufficient. No invalid or conflicting ARIA roles; never override native semantics.
- [ ] **CHK-A11Y-008 (Form Labels)** [FIXABLE] `[WCAG 2.2 SC 3.3.2 Labels or Instructions, A + SC 1.3.1 Info and Relationships, A + SC 4.1.2 Name, Role, Value, A]`: All form inputs have properly associated labels (explicit `for`/`id` or wrapping `<label>`).

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
