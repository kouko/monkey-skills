# Primary Source Grounding Gate

Grounds on: `standards/grounding-principle.md`.

## Scope Boundary

Review the **grounding depth** of a skill's standards files.
Do NOT review structural completeness (that's the completeness
checklist's job), prose quality (that's coherence's job), or
workflow correctness.

Run this rubric against each `standards/*.md` file individually, then
combine into a per-skill verdict.

## Flag Definitions

### Source Authority

- :red_circle: **Fatal**: Standard has no "Primary Sources" section, OR the sources listed are all non-primary (blog posts, Medium articles, Stack Overflow, dev.to, personal tutorials).
- :yellow_circle: **Warning**: Mix of primary and non-primary sources. At least 1 non-primary source is used as a load-bearing citation.
- :green_circle: **Clear**: All sources are primary — published books, official project sites, ISO/IEEE standards, peer-reviewed papers, or authoritative institutional documentation (e.g. Google Cloud Architecture Center, AWS Well-Architected).

### Citation Density

- :red_circle: **Fatal**: Zero citations in the body. The "Primary Sources" section lists sources but the body content doesn't reference them.
- :yellow_circle: **Warning**: Fewer than 3 citations per standard, OR citations cluster in one section while others are uncited.
- :green_circle: **Clear**: At least 3 citations distributed through the body, each tied to a specific load-bearing claim.

### Load-Bearing Claim Coverage

- :red_circle: **Fatal**: Key taxonomies, definitions, thresholds, or frameworks are invented (no citation) or cite sources that don't actually support the claim.
- :yellow_circle: **Warning**: Most load-bearing claims are cited but 1-2 slip through uncited, OR the match between claim and source is loose (the source mentions the topic but doesn't define the specific claim).
- :green_circle: **Clear**: Every load-bearing claim traces to a primary source that specifically supports it. A skeptical reader can follow each cite and verify the claim.

### Japanese Integration Consistency

- :red_circle: **Fatal**: Synthetic / forced JP content — JP sections added without evidence of a real Japanese tradition in this domain. OR JP content contradicts the content-density rule from `standards/grounding-principle.md`.
- :yellow_circle: **Warning**: JP content is present but the decision (full / preamble / none) isn't clearly justified, OR the decision was made without research backing.
- :green_circle: **Clear**: JP strategy matches the content-density rule, backed by research evidence, AND documented in the skill (either in a JP-integrated section or an explicit "no overlay" note).

## Verdict Rules

1. **NEEDS_REVISION**: Any 1 :red_circle: fatal flag on any dimension
2. **NEEDS_REVISION**: 2 or more :yellow_circle: warning flags total (across all dimensions)
3. **PASS_WITH_NOTES**: Exactly 1 :yellow_circle: warning flag, no :red_circle:
4. **PASS**: All :green_circle: clear

## Rules

- Evaluate against what the skill actually claims, not what it should
  have claimed. If a skill correctly refrains from making a load-
  bearing claim, that's fine — no citation needed.
- Don't demand citations for editorial prose, examples, or
  transitions. Only load-bearing claims need grounding.
- When issuing NEEDS_REVISION for source authority, you MUST include
  a list of the non-primary sources found and suggest specific
  primary-source replacements.
- The Japanese Integration dimension is NOT_APPLICABLE if the skill
  explicitly declares no JP overlay AND the declaration is
  justified — mark as :green_circle: in that case.

## Output Format

1. **Per-standard flags**: For each `standards/*.md` file, list the four dimensions and their flag
2. **Evidence**: Specific file line or cited source (or lack thereof)
3. **Alternatives Considered** (NEEDS_REVISION only): For fatal source authority failures, list at least 2 primary source candidates the skill could use instead
4. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION (per standard AND per skill overall)

PASS_WITH_NOTES issues will be auto-revised without human review.
Be specific about which citation is missing and what primary source
should fill it.
