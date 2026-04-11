---
title: Platform Conventions (iOS & Android)
tier: 1
---

# Platform Conventions (iOS & Android)

Canonical anchors for Apple Human Interface Guidelines and Material
Design 3. Tier 1: both are well-known to cold-query LLMs; the body
anchors the load-bearing cross-references with WCAG and spells out the
Material 3 state enum because that enum is frequently partially
recalled.

## Primary Sources

- Apple (ongoing) *Human Interface Guidelines*. https://developer.apple.com/design/human-interface-guidelines/. Canonical iOS / iPadOS touch target (44 × 44 pt) and platform idioms.
- Google (ongoing) *Material Design 3 Foundations*. https://m3.material.io/foundations/designing/structure. Canonical Android touch target (48 × 48 dp) and Material 3 component state model.

## Touch Targets (cross-reference with WCAG)

| Standard | Minimum | Notes |
|---|---|---|
| WCAG 2.2 SC 2.5.8 (AA) | 24 × 24 CSS px | universal cross-platform baseline — see `wcag-baseline.md` |
| WCAG 2.2 SC 2.5.5 (AAA) | 44 × 44 CSS px | enhanced level |
| Apple HIG (iOS / iPadOS) | 44 × 44 pt | platform convention, stricter than WCAG AA |
| Material Design 3 (Android) | 48 × 48 dp | platform convention, stricter than WCAG AA |

Rule of thumb: WCAG AA is the universal floor; on iOS meet 44 pt; on
Android meet 48 dp. These are additive obligations, not alternatives.

## Material 3 Component States (canonical enum)

Material 3 defines exactly 8 component states — cold-query recall
often drops `Dragged`, `Activated`, or conflates `Focused` with
`Selected`. The authoritative list:

- **Enabled** — default interactive state.
- **Hovered** — pointer hovering over the component.
- **Focused** — keyboard focus; accessibility-critical.
- **Pressed** — tap / click ripple active.
- **Dragged** — the component is being dragged.
- **Disabled** — not interactive; must remain perceivable per WCAG.
- **Selected** — the component is part of a selection group.
- **Activated** — persistently active (e.g., the current nav item).

Every interactive Material 3 component should have visual treatments
for all states it supports; missing states (especially `Focused` and
`Disabled`) are common accessibility regressions.

## iOS Idioms

- **Edge-swipe back navigation** — swipe from the left edge goes back
  in the navigation stack; never break this gesture in a navigation
  controller.
- **Bottom sheet presentation** — modal and non-modal sheets slide
  from the bottom; use for secondary context, not primary navigation.
- **SF Symbols** — the system icon library; prefer SF Symbols for
  system-aligned visual language and automatic tint/weight adaptation.
- **Haptic feedback** — `UIFeedbackGenerator` for tactile confirmation
  of discrete events; use sparingly and match the semantic weight.

## Android Idioms

- **System back** — gesture (Android 10+) or button; your app must
  handle back navigation consistently with the system model.
- **Bottom navigation bar** — primary top-level destinations (3-5
  items); do not nest a bottom nav inside a bottom nav.
- **Material ripple** — tap feedback for every interactive surface;
  do not suppress without replacement.
- **Floating action button (FAB)** — the primary action for a screen,
  elevated above content.

## Multi-Platform Crossover

Modern apps on both platforms increasingly borrow idioms — bottom
sheets appear on iOS, edge-swipe back appears on Android 10+ — but the
primary touch-target, motion, and navigation conventions remain
platform-anchored. Do not force one platform's idioms onto the other:
iOS users expect 44 pt targets, SF Symbols, and edge-swipe; Android
users expect 48 dp targets, Material ripple, and system back. When in
doubt, meet the host platform's convention and only deviate for a
documented, user-researched reason.
