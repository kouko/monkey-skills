# WCAG 2.2 AA Baseline (Shared Standard)

This file is the single source of truth for accessibility rules.
Both worker (when building) and evaluator (when reviewing) reference this file.
The `checklists/a11y-checklist.md` derives its checks from these rules.

## Perceivable

- Text alternatives for all meaningful non-text content
- Captions for pre-recorded and live audio/video
- Color is NOT the sole means of conveying information
- Contrast: ≥ 4.5:1 for normal text, ≥ 3:1 for large text (≥18pt or ≥14pt bold)
- Text can be resized to 200% without loss of content
- Content reflows at 320px viewport width without horizontal scrolling

## Operable

- All functionality available via keyboard
- No keyboard traps
- Skip navigation link for repetitive content
- Touch targets ≥ 44×44 CSS pixels
- No time limits without user controls
- Motion/animation respects `prefers-reduced-motion`
- Visible focus indicator on all focusable elements

## Understandable

- `lang` attribute set on `<html>` element
- Consistent navigation across pages
- Error identification with clear fix suggestions
- No unexpected context changes on input

## Robust

- Semantic HTML over div soup
- ARIA roles/states only when native HTML is insufficient
- Landmark structure: header, main, nav, footer
- Form labels properly associated (`for` attribute or wrapping)
- Live regions for dynamic content updates (`aria-live`)

## AAA Opportunities (Flag but Don't Block)

- Enhanced contrast ≥ 7:1
- Sign language for video content
- Extended audio descriptions
- Target size ≥ 24×24 CSS pixels
