# UX Strategy Review Gate

Design philosophy: おもてなし — solve problems before users
encounter them; notice needs users haven't articulated.

## Evaluation: 安藤期間モデル × Garrett 戦略・要件

Each temporal phase is evaluated through two strategic lenses:
- **戦略 (Strategy)**: user needs × business objectives alignment
- **要件 (Scope)**: feature × content requirements coverage

Leave 構造/骨格/表層 to ui-interaction-gate and visual-gate.

## Flag Definitions

### 予期的UX (Anticipated — 利用前)
- 🔴 **Fatal**: Pre-use messaging promises features that do not exist (expectation debt leading to guaranteed churn)
- 🟡 **Warning**: Value proposition is clear to users but not aligned with business positioning (or vice versa)
- 🟢 **Clear**: Both user and business perspectives are addressed in pre-use touchpoints

### 一時的UX (Momentary — 利用中)
- 🔴 **Fatal**: Core task flow does NOT serve the primary user need (solving wrong problem)
- 🔴 **Fatal**: Feature bloat — KPI-serving features actively degrade core usability
- 🟡 **Warning**: Must-have features are complete but Should-have features have noticeable gaps
- 🟢 **Clear**: Core experience is friction-free and serves both user and business value

### エピソード的UX (Episodic — 利用後)
- 🟡 **Warning**: No post-use touchpoint exists (users have no reason to return)
- 🟡 **Warning**: Feedback loops or progress tracking are undefined
- 🟢 **Clear**: Post-use reflection reinforces value proposition and drives re-engagement

### 累積的UX (Cumulative — 利用期間全体)
- 🔴 **Fatal**: Short-term business extraction actively erodes long-term user trust
- 🟡 **Warning**: No habit-forming or evolution features — product is static
- 🟡 **Warning**: Product does not grow with the user (same experience at month 1 and month 12)
- 🟢 **Clear**: Sustained use builds durable value for both user and business

## Supplementary: 黒須 3D Quality Check

Flag ONLY if these reveal issues NOT already caught above:
- 品質 (Quality): Reliability or usability gaps across phases
- 感性 (Kansei): Emotional friction undermining strategic goals
- 意味性 (Meaningfulness): Hollow experience despite feature completeness

## Verdict Rules

1. **NEEDS_REVISION**: Any 1 🔴 fatal flag
2. **NEEDS_REVISION**: 2 or more 🟡 warning flags
3. **PASS_WITH_NOTES**: Exactly 1 🟡 warning flag, no 🔴
4. **PASS**: All 🟢 clear

## Output Format

1. **Journey Assessment**: Flags across the 4 temporal phases
2. **Gap Analysis**: Where the experience breaks down and why
3. **Recommendations**: Prioritized by user impact (these become the revision spec)
4. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

PASS_WITH_NOTES issues will be auto-revised without human review.
Be specific and actionable.
