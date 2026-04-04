# Codebase Assessment Protocol

## Protocol

### Step 1. Scope definition

Confirm assessment boundaries before scanning:
- **Target**: entire repo, specific module, or specific concern area
- **Depth**: overview (structure + entry points) or deep (data flow + side effects)
- If not specified, default to overview of the entire repo

### Step 2. Scale-aware scanning plan

Determine repo scale and set scanning budget. The goal is to read <5% of files to achieve 70-80% structural understanding.

| Scale | File Count | Scan Budget | Max % |
|:---|:---|:---|:---|
| TINY | <5 | 1-2 files | 50% |
| SMALL | 5-15 | 2-3 files | 20% |
| MEDIUM | 15-50 | 4-6 files | 12% |
| LARGE | 50-150 | 6-10 files | 7% |
| VERY_LARGE | >150 | 10-15 files | 5% |

**High-entropy file prioritization** — read in this order, stopping when budget is reached:
1. Documentation (README.md, CLAUDE.md, docs/) — project intent and conventions
2. Configuration (package.json, docker-compose.yml, tsconfig.json, Makefile) — tech stack and build
3. Core models/domain (models/, entities/, domain/) — pick 2-3 representative files
4. Entry points (main.ts, app.py, routes/, cmd/) — pick 1-2 examples
5. Tests — pick 1-2 to understand testing patterns

Rationale: high-entropy files contain disproportionate information about the system. Documentation and configuration reveal intent; models reveal domain; entry points reveal architecture.

### Step 3. Structural analysis

From scanned files, extract:
- **Module boundaries**: top-level directories, package structure, internal vs public API surfaces
- **Entry points**: CLI entrypoints, API routes, event handlers, scheduled tasks
- **Shared infrastructure**: utilities, base classes, middleware, cross-cutting concerns
- **Build & CI**: build system, test framework, linting, deployment pipeline

### Step 4. Git history analysis (if git available)

Use git log to extract temporal signals:

```
git log --all --numstat --date=short \
    --pretty=format:'--%h--%ad--%aN' \
    --after="YYYY-MM-DD"
```
- Default window: last 12 months (min 3 months for meaningful patterns, max 24 months)

**Hotspot detection**:
- Complexity Score = LOC × Revision Count
- Rank files by complexity score, top 10 are hotspots
- Hotspots with low test coverage are the highest-priority risks

**Temporal coupling**:
- Files that change together >50% of the time are temporally coupled
- Categorize as Expected (same module, related logic) or Suspicious (cross-module, unrelated)
- Suspicious coupling often indicates hidden dependencies or leaking abstractions

**Bus factor**:
- Count distinct contributors per module/directory
- Healthy: 2-3 contributors per module
- Risk: single contributor on a critical-path module

**Composite risk score** per module:
```
Risk = (Revision_Count × Coupling_Count) / Contributor_Count
```

### Step 5. Code health indicators

These are NOT derivable from structure or git history alone — requires code inspection:

- **Test coverage distribution**: which modules have tests, which don't (focus on critical paths)
- **TODO/FIXME/HACK markers**: count and distribution; orphaned markers without issue refs
- **Complexity**: functions exceeding cyclomatic complexity of 15; nesting >3 levels
- **Dead code**: unused exports, unreachable branches, orphaned modules with no importers
- **Dependency hygiene**: unused dependencies in manifest, pinned versions with known CVEs
- **Duplication**: copy-pasted logic blocks (3+ substantially identical lines across files)

Reference `checklists/tech-debt-checklist.md` for the formal evaluation gate.

### Step 6. Risk synthesis

Cross-reference all findings into a unified risk register:

| Risk Pattern | Detection Method | Severity |
|:---|:---|:---|
| Hotspot with no tests | Step 4 hotspots × Step 5 test coverage | High |
| Single-contributor critical module | Step 4 bus factor × Step 3 entry points | High |
| Suspicious temporal coupling | Step 4 coupling (cross-module, >50%) | Medium |
| High complexity + high churn | Step 4 hotspots × Step 5 complexity | High |
| Unused dependencies with CVEs | Step 5 dependency hygiene | Medium-High |
| Dead code in critical path | Step 5 dead code × Step 3 entry points | Medium |

**Impact risk thresholds** (for individual modules):
- **HIGH**: >30 internal dependents, OR on critical path (auth, payment, data pipeline), OR test coverage <25%
- **MEDIUM**: 10-30 dependents, OR 25-50% test coverage, OR contains breaking API
- **LOW**: ≤10 dependents, not on critical path, test coverage >50%

### Step 7. Synthesize report

Produce the final assessment with verification.

**Self-verification before output**:
1. Verify all referenced file paths actually exist
2. Verify file/module counts are within ±10% of actual
3. Verify git-derived claims match actual git log
4. If 3+ verifications fail, re-execute the failing steps

## Rules

- This protocol produces a REPORT, not code changes
- Do NOT attempt to fix issues found — only identify and prioritize them
- If the repo is too large for single-pass analysis, use `context-compressor` between phases
- Reference `standards/code-conventions.md` for evaluating naming and style compliance
- Every claim must reference a specific file path or git evidence — no unsupported assertions

## Output Format

1. **Overview**: Tech stack, repo scale, module count, AI collaboration tier (2-3 sentences)
2. **Architecture diagram**: ASCII or Mermaid showing module relationships and boundaries
3. **Module health table**:

| Module | Test Coverage | Complexity | Hotspot Rank | Bus Factor | Risk Level |
|:---|:---|:---|:---|:---|:---|
| module-a | High | Low | — | 3 contributors | Low |
| module-b | None | High | #2 | 1 contributor | High |

4. **Risk register**: Prioritized list with severity, detection method, and evidence
5. **Recommendations**: Ordered list of suggested actions with effort estimates (Low/Medium/High)
