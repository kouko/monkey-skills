# UI & Interaction Review Gate

Scope: Garrett's 構造 (Structure) and 骨格 (Skeleton) layers.
Layout aesthetics and visual polish belong to visual-gate.

Informed by 深澤直人's "Without Thought" philosophy:
design should emerge from unconscious human behavior (無意識の行為).
Good UI is invisible.

Structure informed by OOUI (上野学『オブジェクト指向UIデザイン』)
and OOUX (Sophia Prater, ORCA process): objects (名詞) before
actions (動詞). Evaluate using the ORCA lens:
Objects → Relationships → CTAs → Attributes.

## Flag Definitions

### Object Modeling (OOUI/OOUX)
- 🔴 **Fatal**: Core domain objects lack dedicated views — users cannot see/browse objects before acting on them
- 🔴 **Fatal**: Object relationships are invisible — users must memorize connections between entities
- 🟡 **Warning**: Collection → Single Object → Detail flow feels unnatural or requires backtracking
- 🟡 **Warning**: Task UI is used where OOUI would better match user mental model (or vice versa), and the choice appears accidental
- 🟢 **Clear**: Objects are clearly identified; OOUI vs task UI balance is intentional

### Navigation & IA
- 🔴 **Fatal**: Navigation depth exceeds 4 levels (users get lost)
- 🟡 **Warning**: Navigation depth is 3+ levels (borderline)
- 🟡 **Warning**: Entry points are organized in a way that contradicts user mental models
- 🟢 **Clear**: Hierarchy is logical; wayfinding is intuitive; deep linking supported

### Interaction Patterns
- 🔴 **Fatal**: Error states are completely undefined (users hit dead ends with no guidance)
- 🟡 **Warning**: Missing component states — hover, active, disabled, error, or loading not all defined
- 🟡 **Warning**: Actions lack visible feedback (user doesn't know if click registered)
- 🟢 **Clear**: All interactive states defined; feedback on every action; empty states handled

### Platform Conventions
- 🟡 **Warning**: Touch targets < 44pt (iOS) / 48dp (Android)
- 🟡 **Warning**: Deviates from platform conventions (iOS HIG / Material Design / Web standards) without justification
- 🟡 **Warning**: Design system tokens/naming not followed consistently
- 🟢 **Clear**: Platform-native feel; responsive breakpoints handled

## Review Checklist (Quick Scan)

1. Are core objects identified and given dedicated views?
2. Does Collection → Single Object flow feel natural?
3. Are object relationships visible without extra navigation?
4. Where task UI is used, is it deliberate for linear flows?
5. Is navigation ≤ 3 levels deep?
6. Does every action have visible feedback?
7. Are error states helpful (what went wrong + how to fix)?
8. Are all component states defined?
9. Are touch targets ≥ 44pt (iOS) / 48dp (Android)?

## Verdict Rules

1. **NEEDS_REVISION**: Any 1 🔴 fatal flag
2. **NEEDS_REVISION**: 2 or more 🟡 warning flags
3. **PASS_WITH_NOTES**: Exactly 1 🟡 warning flag, no 🔴
4. **PASS**: All 🟢 clear

## Output Format

1. **Flags**: `[🔴 Dimension]` or `[🟡 Dimension]` with evidence
2. **Fix Instruction**: Concrete alternative (not "improve this")
3. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

Be specific — "increase padding between X and Y to 16px" not "improve spacing".
