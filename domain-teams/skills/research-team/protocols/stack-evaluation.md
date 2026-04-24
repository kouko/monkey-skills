# Tech Stack Evaluation Protocol

## Primary Sources

- `standards/oss-safety.md` — OpenSSF Scorecard 18 checks + NIST SSDF v1.1 + SLSA v1.1 levels + CVSS v4.0 severity ratings + SPDX v3.0 license identifiers
- `standards/citation-standards.md` — citation discipline for version numbers, CVEs, and benchmark data
- `standards/source-quality-and-evidence.md` — official registries (npm, PyPI, crates.io, GitHub) as primary; blog posts and "awesome" lists as secondary

## Phase 0: Mode Detection and Budget Setup

**MUST run before Step 1.** Read the `mode:` field from the worker
launch `### Input` section. If absent, default to `quick`.

| Mode | Default budget | Source cap | Search cap | Token cap |
|---|---|---|---|---|
| **quick** (default) | single-pass triangulation | 5 sources | 5 web searches | ~15k tokens |
| **deep** (opt-in) | full audit trail | 15 sources | 20 web searches | ~150k tokens |

User-overridable via `### Input` fields: `max_sources`, `max_web_searches`,
`max_tokens`. Reject budgets below quick floor (15k tokens / 5 sources)
with `BLOCKED: budget below minimum viable quick mode`.

In **quick mode**, this protocol runs in a stripped-down form per the
mode-specific exit rule defined in `standards/confidence-and-claim-language.md`
§Cost-Aware Early-Exit Rule:
- Skip cross-language (EN+JP) parallel search unless natural
- ≥1 primary source per key claim is sufficient (vs ≥2 for deep)
- Exit immediately when all key claims reach Medium confidence
  (medium evidence × medium agreement on the IPCC 3×3 grid)
- Skip MUST `source-citation-checklist` gate (SELF check applies)
- Quick-mode reduction: skip full CHAOSS multi-signal evaluation —
  use 3 core signals only (stars trend, last commit date, weekly
  downloads); skip OpenSSF Scorecard 18-check enumeration — use
  the top 5 most load-bearing checks (code review, CI, dependency
  update tool, pinned dependencies, vulnerabilities); skip SLSA
  build-level audit entirely; skip SBOM deep-dive

In **deep mode**, run the protocol per the existing v4.9.0 grounding:
- Cross-language parallel search REQUIRED
- ≥2 sources per key claim REQUIRED
- Exit at Very high confidence (robust evidence × high agreement)
  per the early-exit rule
- All MUST and SHOULD gates trigger
- Retry on PASS_WITH_NOTES per gate-system.md
- Deep-mode rigor: full OpenSSF Scorecard 18-check enumeration +
  NIST SSDF v1.1 4 practice groups + SLSA v1.1 build levels L0-L3
  + CVSS v4.0 4 metric groups on known CVEs + SPDX v3.0 license
  identifier verification + license deep-dive (compatibility +
  copyleft exposure)

**Budget enforcement**: track source count, search count, token
estimate. On overrun, finish current source verification (atomic),
then return BLOCKED with summary: `"budget overrun: collected N
sources, M searches, ~Tk tokens. Partial result attached. Reply
'expand budget to X' or 'accept partial'."`

See `standards/confidence-and-claim-language.md` §Cost-Aware
Early-Exit Rule for the mode-specific exit thresholds and the
per-claim (not per-deliverable) policy.

**Deep-mode hooks**: load per the trigger map in
`protocols/research.md` §Deep-Mode Hooks (multi-perspective at
end of scope-definition Step 1-2; parallel-fanout at candidate
discovery Step 3 when ≥3 independent candidates; self-critique
at end of Step 7 / Synthesize recommendation). Quick mode skips.

## Protocol

### Step 1. Define evaluation scope

Clarify the decision context before any research:
- What problem does the new technology solve?
- What are the current alternatives already in use?
- What are the hard constraints (license, language, runtime, team skill)?

**Detect current baseline from manifest files**:
- Node.js: `package.json`, `package-lock.json`
- Python: `requirements.txt`, `pyproject.toml`, `setup.cfg`
- iOS: `Podfile`, `Package.swift`
- Android: `build.gradle`, `build.gradle.kts`
- Rust: `Cargo.toml`
- Go: `go.mod`

Extract exact current versions — never assume. If manifest is ambiguous, grep for import statements to confirm actual usage.

### Step 2. Classify evaluation type

Different evaluation types require different methodologies:

| Type | Trigger | Focus |
|:---|:---|:---|
| **Platform version upgrade** | "iOS 16 → 17", "Python 3.11 → 3.12" | Removable availability checks, deprecated APIs, new platform capabilities |
| **SDK/compiler upgrade** | "Xcode 16", "TypeScript 5.5" | Compilation warnings, new syntax, toolchain compatibility |
| **Major library upgrade** | "React 17 → 18", "pandas 1.x → 2.x" | Breaking API changes, deprecated patterns, new idioms |
| **New adoption / replacement** | "compare X vs Y", "should we use X" | Full comparative evaluation (Steps 3-6 below) |
| **Usage inventory** | "how do we use X" (no target version) | List all usage points by category; no migration plan |

For upgrades (types 1-3): search for official migration guides FIRST (web search in EN + JP). The migration guide defines the checklist — do not invent rules beyond what the guide specifies.

### Step 3. Candidate discovery

**Mode discipline**: in quick mode, cap collection per Phase 0
budget; in deep mode, follow existing collection workflow.

Identify 2-5 candidates (for new adoption / replacement type):
- Search in English AND Japanese for candidates and comparisons
  - EN: "best {category} libraries 2025", "{tool A} vs {tool B}"
  - JP: 「〇〇 比較」「〇〇 おすすめ」「〇〇 代替」
- ALWAYS include the incumbent (current solution) as a baseline candidate
- If no incumbent exists, the baseline is "build from scratch"

### Step 4. Quantitative signals (per candidate)

Cross-reference `standards/oss-safety.md` for the grounded
framework: OpenSSF Scorecard provides the 18-check production
readiness model, NIST SSDF v1.1 defines the 4 secure-development
practice groups, SLSA v1.1 defines build-integrity levels L0-L3,
CVSS v4.0 defines severity bands, and SPDX v3.0 is the license
identifier standard.

| Signal | Source | Red Flag Threshold |
|:---|:---|:---|
| GitHub stars trend | GitHub | Declining over 12 months |
| Last commit date | GitHub | >12 months ago |
| Open issues count | GitHub | >500 unresolved |
| Release frequency | GitHub releases | No release in 12 months |
| Weekly downloads | npm/PyPI/crates.io | <1000 for production use |
| Breaking change frequency | CHANGELOG | >2 major versions/year |
| Known CVEs | NVD, GitHub Advisories, Snyk | Any unpatched Critical/High per CVSS v4.0 (≥7.0) |
| License (SPDX) | Repository | See `standards/oss-safety.md` §Acceptable Licenses |

**Note on threshold values**: The numeric thresholds above
(>500 issues, <1000 weekly downloads, >2 major versions/year,
>12 months without commits) are research-team **internal
operational heuristics**, not primary-source citations. They
are disclosed as such per `standards/oss-safety.md` §Critical
Attribution Corrections. OpenSSF Scorecard's own checks and
CVSS severity bands are grounded citations; the count / frequency
thresholds in this table are the team's convention.

### Step 5. Qualitative signals (per candidate)

- **Documentation**: completeness, quality, up-to-date with current version
- **Community**: active maintainer count, issue response time, Stack Overflow/Discord presence
- **Production adoption**: used by notable projects, corporate backing, case studies
- **Maturity**: has 1.0+ stable release, has upgrade/migration guides for major versions
- **Integration cost**: API surface compatibility with current codebase patterns

### Step 6. Integration cost assessment

**Estimate migration effort using usage inventory**:

1. Grep all import/require statements for the incumbent library
2. Categorize usage points (hooks, components, utilities, types, etc.)
3. Count total usage points and affected files

| Effort Level | Usage Points | Affected Files | Breaking Changes | Characteristics |
|:---|:---|:---|:---|:---|
| **Low** | <20 | <5 | 0 | Straightforward API mapping, drop-in replacement |
| **Medium** | 20-50 | 5-15 | 1-3 types | Some API pattern changes, moderate refactoring |
| **High** | >50 | >15 | >3 types | Significant architectural changes, new patterns |

Additionally assess:
- Compatibility with current dependency tree (version conflicts)
- Learning curve for the team (new paradigms vs familiar patterns)
- Rollback difficulty if adoption fails

### Step 7. Synthesize recommendation

- Comparison table with all signals from Steps 4-6
- Explicit trade-offs between top 2 candidates
- Confidence level (高/中/低) on recommendation
- Risk factors and mitigation strategies

**Self-verification before output**:
1. Verify all cited version numbers match actual registry data
2. Verify usage point counts are within ±5% of actual grep results
3. Verify all file paths referenced actually exist
4. If discrepancies found, correct before presenting

## Rules

- NEVER recommend based on popularity alone — integration cost and maintenance burden matter more
- ALWAYS include the incumbent as a baseline for comparison
- Flag any candidate with no release in the last 12 months as high risk
- Flag any candidate with a license incompatible with the project (reference `standards/oss-safety.md`)
- Cite every factual claim with source (reference `standards/citation-standards.md`)
- Disclose whether migration rules came from official guide (web search) or built-in knowledge
- Every usage point must have a file:line reference — no vague counts

## Output Format

1. **Decision context**: Problem statement + constraints + evaluation type (2-3 sentences)
2. **Current baseline**: Detected versions, usage point count, affected file count
3. **Comparison table**: Candidates × signals matrix
4. **Integration cost summary**: Per candidate, effort level with evidence
5. **Recommendation**: Top pick with confidence level (高/中/低) and reasoning
6. **Risk register**: What could go wrong, how to mitigate
