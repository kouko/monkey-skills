# UI & Interaction Review Gate

Scope: Garrett's 構造 (Structure) and 骨格 (Skeleton) layers
(`standards/garrett-elements-of-ux.md` §Gate Scope Partition).
Layout aesthetics and visual polish belong to visual-gate.

Informed by 深澤直人's "Without Thought" philosophy:
design should emerge from unconscious human behavior (無意識の行為).
Good UI is invisible.

Structure informed by OOUI (上野学『オブジェクト指向UIデザイン』)
and OOUX (Sophia Prater, ORCA process): objects (名詞) before
actions (動詞). Evaluate using the ORCA lens:
Objects → Relationships → CTAs → Attributes.

## Primary Sources

Each dimension's flag criteria derive from a tier-classified standard.
Consult the listed standard for load-bearing definitions; numeric
thresholds in this gate are house heuristics, not primary-source rules.

- **Object Modeling dimension** → `standards/ooui-and-object-modeling.md`
  (上野学他 2020 『オブジェクト指向 UI デザイン』技術評論社; Sophia V.
  Prater 2015 "Object-Oriented UX" *A List Apart* + ooux.com for the
  full ORCA 4-step framework). The ALA 2015 and 2016 articles **do
  not** contain full ORCA — cite ooux.com for the 4-step spell-out.
- **Interaction Patterns dimension (supplementary)** →
  `standards/nielsen-norman-heuristics.md` (Nielsen heuristics #1
  Visibility of System Status, #5 Error Prevention, #9 Help Users
  Recognize / Diagnose / Recover from Errors; Norman 2013 *Design of
  Everyday Things: Revised and Expanded Edition* Ch.2 gulfs of
  execution / evaluation for interaction feedback framing).
- **Without Thought framing (gate preamble)** →
  `standards/japanese-design-aesthetics.md` §6 無意識のデザイン /
  Without Thought (深澤直人 2005 『デザインの輪郭』TOTO 出版).
- **Platform Conventions dimension** → `standards/platform-conventions.md`
  (Apple HIG 44 × 44 pt iOS; Material Design 3 48 × 48 dp Android;
  Material 3 canonical 8-state component enum). These are additive
  obligations on top of WCAG 2.2 SC 2.5.8 24 × 24 CSS px AA, not
  alternatives — see `standards/wcag-baseline.md` §Touch Target
  Disambiguation.
- **Scope partition (Structure + Skeleton, not Surface or Strategy)** →
  `standards/garrett-elements-of-ux.md` §The 5 Planes + §Gate Scope
  Partition.

## Flag Definitions

### Object Modeling (OOUI/OOUX)

Grounded in `standards/ooui-and-object-modeling.md`.

- 🔴 **Fatal**: Core domain objects lack dedicated views — users cannot see/browse objects before acting on them (violates the noun-before-verb principle; see that standard §Philosophy).
- 🔴 **Fatal**: Object relationships are invisible — users must memorize connections between entities (violates §Object Relationships: relationships should surface as navigable links).
- 🟡 **Warning**: Collection → Single Object → Detail flow feels unnatural or requires backtracking (violates §Object Views Lifecycle).
- 🟡 **Warning**: Task UI is used where OOUI would better match user mental model (or vice versa), and the choice appears accidental (see §OOUI vs Task-Based UI Contrast — task UI is legitimate for one-shot operations).
- 🟢 **Clear**: Objects are clearly identified; OOUI vs task UI balance is intentional.

### Navigation & IA

- 🔴 **Fatal**: Navigation depth exceeds 4 levels (users get lost) — *house heuristic, not a primary-source rule*.
- 🟡 **Warning**: Navigation depth is 3+ levels (borderline) — *house heuristic, not a primary-source rule*.
- 🟡 **Warning**: Entry points are organized in a way that contradicts user mental models (violates Nielsen heuristic #2 Match Between System and the Real World, see `standards/nielsen-norman-heuristics.md`).
- 🟢 **Clear**: Hierarchy is logical; wayfinding is intuitive; deep linking supported.

### Interaction Patterns

Grounded in `standards/nielsen-norman-heuristics.md`.

- 🔴 **Fatal**: Error states are completely undefined (users hit dead ends with no guidance — violates Nielsen heuristics #5 Error Prevention + #9 Help Users Recognize, Diagnose, and Recover from Errors).
- 🟡 **Warning**: Missing component states — hover, active, disabled, error, or loading not all defined (see `standards/platform-conventions.md` §Material 3 Component States for the canonical 8-state enum).
- 🟡 **Warning**: Actions lack visible feedback (violates Nielsen heuristic #1 Visibility of System Status; Norman 2013 Ch.2 gulf of evaluation widens without feedback).
- 🟢 **Clear**: All interactive states defined; feedback on every action; empty states handled.

### Platform Conventions

Grounded in `standards/platform-conventions.md` and
`standards/wcag-baseline.md` §Touch Target Disambiguation.

- 🟡 **Warning**: Touch targets fall below platform convention — iOS < 44 × 44 pt (Apple HIG) or Android < 48 × 48 dp (Material Design 3). WCAG 2.2 SC 2.5.8 AA requires 24 × 24 CSS px as the universal floor; 44 pt / 48 dp are platform-specific additive obligations on top of that floor, not alternatives.
- 🟡 **Warning**: Deviates from platform conventions (iOS HIG / Material Design 3 / Web standards) without justification — violates Nielsen heuristic #4 Consistency and Standards.
- 🟡 **Warning**: Design system tokens/naming not followed consistently.
- 🟢 **Clear**: Platform-native feel; responsive breakpoints handled.

## Review Checklist (Quick Scan)

1. Are core objects identified and given dedicated views? (`standards/ooui-and-object-modeling.md`)
2. Does Collection → Single Object flow feel natural?
3. Are object relationships visible without extra navigation?
4. Where task UI is used, is it deliberate for linear flows?
5. Is navigation ≤ 3 levels deep? *(house heuristic)*
6. Does every action have visible feedback? (Nielsen #1)
7. Are error states helpful (what went wrong + how to fix)? (Nielsen #5, #9)
8. Are all component states defined? (`standards/platform-conventions.md` §Material 3 Component States)
9. Are touch targets ≥ WCAG SC 2.5.8 AA 24 × 24 CSS px universal floor, plus iOS 44 pt / Android 48 dp where platform-appropriate? (`standards/wcag-baseline.md` + `standards/platform-conventions.md`)

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
