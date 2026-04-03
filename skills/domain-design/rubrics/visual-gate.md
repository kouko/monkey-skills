# Visual Design Review Gate

Informed by Japanese aesthetic philosophy:
- **感性工学** (Kansei Engineering, 長町三生): Translate emotional
  responses into measurable design parameters. "What does it make
  the user FEEL?"
- **引き算のデザイン** (Subtractive Design): Every element must earn
  its place. Perfection is when there is nothing left to take away.
- **わびさび** (Wabi-Sabi): Beauty in imperfection, impermanence,
  incompleteness. Not everything needs sterile polish.

## Flag Definitions

### Composition & Layout
- 🔴 **Fatal**: No visual hierarchy — reader cannot determine what to look at first
- 🟡 **Warning**: Grid system inconsistent; elements feel randomly placed
- 🟡 **Warning**: Whitespace (余白) is either cramped or wasteful — no intentional 間 (Ma)
- 🟢 **Clear**: Layout is balanced; visual flow guides the eye naturally

### Typography
- 🔴 **Fatal**: Body text is unreadable (wrong size, weight, or line height for medium)
- 🟡 **Warning**: Type hierarchy unclear — headings, body, and captions not visually distinct
- 🟡 **Warning**: Font pairing creates visual friction (incompatible styles or weights)
- 🟢 **Clear**: Typography is harmonious; hierarchy is scannable

### Color
- 🔴 **Fatal**: Text fails WCAG AA contrast and is NOT marked as decorative (reference `standards/wcag-baseline.md`)
- 🔴 **Fatal**: Color is the ONLY way to convey critical information (no icon, pattern, or label backup)
- 🟡 **Warning**: Emotional tone (感性特性) does not align with brand/product intention
- 🟡 **Warning**: Dark/light mode not considered for a product that will be used in both
- 🟢 **Clear**: Palette is harmonious; contrast passes; emotional tone aligns

### Brand Consistency
- 🔴 **Fatal**: Directly contradicts existing brand style guide (wrong logo, wrong colors, wrong voice)
- 🟡 **Warning**: Inconsistent asset usage across screens or deliverables
- 🟢 **Clear**: Brand guidelines followed; cross-medium consistency maintained

### Craft
- 🟡 **Warning**: Visible alignment errors or pixel-level inconsistencies
- 🟡 **Warning**: Export quality insufficient for target medium
- 🟢 **Clear**: Production-ready; details reward closer inspection

## 感性チェック (Kansei Check)

Beyond the flags, evaluate the emotional response:
- What feeling does this design evoke at first glance?
- Does that feeling align with the product/brand intention?
- Is there 品格 (dignity/elegance) in the restraint?

## Context-Aware Review

Adapt flag severity to the medium:
- **App UI**: Platform conventions matter; system fonts and dynamic type
- **Poster / Print**: Viewing distance, CMYK, bleed and margin
- **Brand Asset**: Scalability (favicon to billboard), format versatility
- **Marketing**: Target audience, conversion intent, cultural appropriateness
- **Icon / Illustration**: Consistency within set, metaphor clarity

## Verdict Rules

1. **NEEDS_REVISION**: Any 1 🔴 fatal flag
2. **NEEDS_REVISION**: 2 or more 🟡 warning flags
3. **PASS_WITH_NOTES**: Exactly 1 🟡 warning flag, no 🔴
4. **PASS**: All 🟢 clear

## Output Format

1. **Flags**: `[🔴 Dimension]` or `[🟡 Dimension]` with evidence
2. **感性レポート** (Kansei Report): Emotional impression summary
3. **Fix Instruction**: Concrete visual change with rationale
4. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

Note: Visual assets require human creation — your feedback will be
presented to the user, not auto-revised. Be clear about what to change.
