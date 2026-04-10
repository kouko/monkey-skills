# Test Viewpoint Extraction Protocol

Extract **test viewpoints (テスト観点)** — lenses or angles for thinking about
what to test — before writing test cases. This is a first-class upstream
activity per the Japanese QA tradition (see `standards/test-viewpoints-ja.md`).

Can be invoked standalone or as **Phase 2b** of `test-plan-writing.md`.

## When to Use

- Before authoring TEST-PLAN.md for any non-trivial system
- When reviewing an existing TEST-PLAN.md for coverage gaps
- During 設計レビュー (design review) as an upstream verification step
- When the team needs a shared, non-author-readable coverage map

## When NOT to Use

- Single bug-fix test cases with obvious scope
- Pure automation script writing (not coverage decision-making)
- When a viewpoint list already exists and hasn't meaningfully changed

## Phase 0: Context Discovery

1. Understand what already exists:
   - Read TECH-SPEC.md and/or PRODUCT-SPEC.md if present
   - Check for prior viewpoint lists, test plans, or DR documents
   - Identify whether this is a greenfield or brownfield project
2. Identify stakeholders:
   - Who will review the viewpoint list in DR?
   - Are there non-QA stakeholders (PM, designer, security, SRE)?
3. Document constraints:
   - Time budget for extraction
   - Required methodologies (some organizations mandate VSTeP or HAYST)
   - Output format expectations

## Phase 1: Methodology Selection

Choose one primary methodology from `standards/test-viewpoints-ja.md`.
Consult the selection decision tree:

| Situation | Methodology |
|-----------|-------------|
| Enterprise system, cross-cutting quality concerns | **VSTeP / NGT** (西康晴) |
| Configuration/factor-interaction dominant | **HAYST法** (秋山浩一) |
| Greenfield, specs evolving, QA in requirements | **ゆもつよメソッド** (湯本剛) |
| Early discovery, cross-functional brainstorming | **Mind map** (池田暁, 鈴木三紀夫) |
| Unsure / simple project | **6W2H** (universal starting point) |

Document the choice and rationale. State assumptions explicitly.

## Phase 2: Viewpoint Extraction

Execute the chosen methodology:

### If VSTeP / NGT
1. Build an NGT tree rooted at the system-under-test
2. Branch by concern axis (functional, non-functional, structural, change-related)
3. Annotate cross-cutting relationships using `<<affects>>`, `<<depends>>`
4. Verify MECE (Mutually Exclusive, Collectively Exhaustive) at each level

### If HAYST法
1. Build 6W2H tree (when/where/who/whom/what/why/how/how-much)
2. Produce FV表 (Function × Verification matrix)
3. Draw ラルフチャート for input/output/state/noise if applicable
4. Produce FL表 (final factor-level table)

### If ゆもつよメソッド
1. Decompose system into 論理的機能構造 (logical function structure)
2. Identify テストカテゴリ (orthogonal concerns)
3. Build テスト分析マトリクス (function × category grid)
4. Map 仕様項目 (spec items) into the matrix

### If Mind Map
1. Divergent brainstorming: put system at center, radiate concern branches
2. Continue until convergence (new additions repeat existing ideas)
3. **Convert to NGT** for MECE verification — this step is mandatory, not optional

### If 6W2H
1. For each of When/Where/Who/Whom/What/Why/How/How-much, enumerate applicable viewpoints
2. Flag axes that don't apply with explicit rationale

## Phase 3: DR-Style Self-Review

Before handoff, verify the viewpoint list can survive 設計レビュー:

1. **Readability by non-authors** — can a peer who didn't participate in extraction
   understand what each viewpoint covers?
2. **Breadth check** — at least 3 concern axes represented (e.g., functional +
   non-functional + change-related at minimum)
3. **Traceability prep** — each viewpoint has a stable ID that test cases can reference
4. **Methodology consistency** — no mixing of methodologies mid-document without explicit rationale

## Phase 4: Handoff

Produce a structured viewpoint list for downstream test case writing:

```
# Test Viewpoints for {System Name}

Methodology: {VSTeP | HAYST | ゆもつよ | Mind Map | 6W2H}
Extraction date: {YYYY-MM-DD}

## Viewpoint V-01: {Short name}
- Axis: {functional | non-functional | structural | change-related | ...}
- Scope: {what this viewpoint covers}
- Rationale: {why it matters}
- MECE note: {what it does NOT cover, pointing to adjacent viewpoints}

## Viewpoint V-02: ...
```

IDs start with `V-NN`. The list feeds into `test-plan-writing.md` Phase 3,
where each test case will cite one or more viewpoints.

## Rules

- **One methodology per extraction session** — don't mix VSTeP trees with HAYST tables
  in the same document. Use separate sessions if needed.
- **Cite the methodology authority** — reference `standards/test-viewpoints-ja.md`
  and the original practitioner (西康晴 / 秋山浩一 / 湯本剛 / 池田暁) in the output.
- **No execution detail** — viewpoints describe *what to test*, not *how to run*.
  Test case design comes later.
- **Flat viewpoint IDs** — even if the underlying NGT/mind map is hierarchical,
  the handoff list uses flat V-NN IDs for traceability.
- **MECE over completeness** — a smaller MECE list beats a bloated overlapping list.
