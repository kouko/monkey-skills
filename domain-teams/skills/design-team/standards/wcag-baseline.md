---
title: WCAG 2.2 Baseline
tier: 2
---

# WCAG 2.2 Baseline

Single source of truth for web accessibility rules. Worker references this
file when building; evaluator references it when reviewing.
`checklists/a11y-checklist.md` derives its checks from these rules.

## Primary Sources

- W3C (2024) *Web Content Accessibility Guidelines (WCAG) 2.2*. https://www.w3.org/TR/WCAG22/. W3C Recommendation republished 2024-12-12; canonical source for all SC numbers and levels.
- W3C WAI *What's New in WCAG 2.2*. https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/. Summary of SC additions relative to WCAG 2.1.

## Critical Attribution Corrections

- **Touch target 44×24 AA / AAA conflation.** Earlier ungrounded
  `wcag-baseline.md` (v4.7.x pre-grounding) listed `Touch targets ≥ 44×44
  CSS pixels` as a core rule and `Target size ≥ 24×24 CSS pixels` as an
  AAA opportunity — inverting WCAG reality. Correct attribution:
  - **SC 2.5.8 Target Size (Minimum) = 24×24 CSS pixels at level AA**
  - **SC 2.5.5 Target Size (Enhanced) = 44×44 CSS pixels at level AAA**
  - Apple HIG 44 pt and Material 3 48 dp are **platform conventions**
    stricter than WCAG AA, not WCAG values.
  Grounded in W3C WCAG 2.2 SC 2.5.5 and SC 2.5.8 definitions.

## The Four Principles (POUR)

**Perceivable** — information and UI components must be presentable to
users in ways they can perceive: text alternatives, captions, sufficient
contrast, resizable text, reflow.

**Operable** — UI components and navigation must be operable: keyboard
accessibility, no traps, sufficient time, no seizure triggers, navigable
structure, sufficient target size.

**Understandable** — information and UI operation must be understandable:
readable language, predictable behaviour, input assistance.

**Robust** — content must be robust enough to be interpreted reliably by
user agents including assistive technologies: valid parsing, name/role/
value exposed via accessibility APIs.

## AA Success Criteria (load-bearing subset)

| SC | Name | Level | Threshold |
|---|---|---|---|
| 1.1.1 | Non-text Content | A | text alternatives present for all meaningful non-text content |
| 1.4.3 | Contrast (Minimum) | AA | ≥ 4.5:1 normal text, ≥ 3:1 large text |
| 1.4.4 | Resize Text | AA | text resizable to 200% without loss of content or function |
| 1.4.10 | Reflow | AA | content reflows at 320 CSS px width without horizontal scroll |
| 1.4.11 | Non-text Contrast | AA | ≥ 3:1 for UI components and meaningful graphics |
| 2.1.1 | Keyboard | A | all functionality operable via keyboard |
| 2.4.3 | Focus Order | A | logical focus sequence preserves meaning and operability |
| 2.4.7 | Focus Visible | AA | visible focus indicator on all focusable elements |
| 2.5.8 | Target Size (Minimum) | AA | ≥ 24×24 CSS pixels |
| 2.5.5 | Target Size (Enhanced) | AAA | ≥ 44×44 CSS pixels |
| 3.3.1 | Error Identification | A | errors identified and described in text |
| 4.1.2 | Name, Role, Value | A | name / role / state / value programmatically exposed |

## Touch Target Disambiguation (load-bearing)

Cold-query LLMs frequently conflate the WCAG AA baseline with Apple /
Google platform conventions. The correct partition:

| Source | Value | Scope |
|---|---|---|
| WCAG 2.2 SC 2.5.8 Target Size (Minimum) | 24×24 CSS px | **AA** — universal cross-platform baseline |
| WCAG 2.2 SC 2.5.5 Target Size (Enhanced) | 44×44 CSS px | **AAA** — enhanced level |
| Apple HIG (iOS / iPadOS) | 44 × 44 pt | platform convention, stricter than WCAG AA |
| Material Design 3 (Android) | 48 × 48 dp | platform convention, stricter than WCAG AA |

Rule of thumb: ship to WCAG AA (24×24 CSS px) as the universal floor.
On iOS, meet 44 pt. On Android, meet 48 dp. These are additive
obligations, not alternatives to WCAG AA.

## Contrast Ratios

- **Normal text**: ≥ 4.5:1 against background (SC 1.4.3 AA).
- **Large text**: ≥ 3:1 against background. Large = ≥ 18 pt or
  ≥ 14 pt bold (SC 1.4.3 AA).
- **Non-text content**: ≥ 3:1 for UI components (borders, icons carrying
  meaning, active state indicators) and meaningful graphics (SC 1.4.11
  AA).

## Keyboard & Focus

- **SC 2.1.1 Keyboard (A)** — every interaction must be operable from the
  keyboard alone. No keyboard traps (SC 2.1.2 A). Skip navigation link
  for repetitive content (SC 2.4.1 A).
- **SC 2.4.7 Focus Visible (AA)** — the currently focused element must
  have a visible focus indicator. Do NOT suppress browser focus outlines
  without providing an equivalent custom indicator.
- **SC 2.4.3 Focus Order (A)** — focus sequence must preserve meaning
  and operability. DOM order generally drives focus order; use `tabindex`
  sparingly and never with positive values except for well-justified
  exceptions.

## Reflow & Resize

- **SC 1.4.10 Reflow (AA)** — content and functionality reflow at
  320 CSS px viewport width without requiring horizontal scrolling
  (except for data tables, complex images, maps, and toolbars).
- **SC 1.4.4 Resize Text (AA)** — users can resize text up to 200%
  without loss of content or functionality. Build layouts that tolerate
  text zoom without clipping or truncation.

## Semantic / Robust

- Prefer semantic HTML (`<button>`, `<nav>`, `<main>`, `<label>`, native
  form controls) over div soup. Native elements carry default role /
  state / name exposure required by SC 4.1.2 (A).
- Add ARIA only when native HTML is insufficient; never override native
  semantics. Use landmark structure (header, nav, main, footer) and
  associate form labels via `for`/`id` or wrapping.
- `lang` attribute on `<html>` (SC 3.1.1 A) and on inline foreign-language
  passages (SC 3.1.2 AA).

## Motion, Timing, and Other Operable Guarantees

- Respect `prefers-reduced-motion`; provide a non-motion alternative for
  any essential motion (SC 2.3.3 AAA is opportunistic, but reduced-motion
  respect is table stakes).
- No time limits without user control (SC 2.2.1 A).
- Avoid three-flashes-or-below-threshold content (SC 2.3.1 A).
- SC 2.4.11 Focus Not Obscured (Minimum) (AA, new in 2.2) — focused
  element must not be entirely hidden by author-created overlays.
- SC 2.5.7 Dragging Movements (AA, new in 2.2) — any drag interaction
  must have a single-pointer alternative.

## WCAG 3.0 Status

WCAG 3.0 (working title: *Silver*) remains a Working Draft as of
2026-04. Earliest Recommendation status is not expected before 2028.
Continue grounding all accessibility decisions on WCAG 2.2 AA; treat
3.0 as informational only until it reaches CR.
