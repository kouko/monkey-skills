# Description Design

Guidelines for writing skill descriptions that drive adoption and correct usage.

## Purpose
A skill description answers: "What does this do and when should I use it?"
Write what it does + when to use it; procedure / workflow / grounding belongs in the body, not the description.
It appears in skill lists, tooltips, and the skill catalog — it's the first
thing users read.

## Principles

### Principle 1: Intent-First
Lead with what the skill enables, not how it works.
- ✅ "Converts CSV to JSONL when streaming output is needed"
- ❌ "Reads lines, parses commas, handles quotes, writes newline-delimited JSON"

### Principle 2: When to Use
Lead with positive specific triggers; add exclusions only to disambiguate adjacent skills.
- **Do use for**: X, Y, Z (positive triggers)
- **Do NOT use for**: A, B — use other-skill instead (negative triggers)
- **Disambiguate by positive specificity** — prefer naming what triggers the skill. When adjacent skills could match similar queries, limit exclusions to **2-3 negative triggers** to prevent mis-routing; a long exclusion list buries the positives. A light positive redirect ("for X, use skill-Y") is also fine.
- Avoid "ALWAYS invoke" directives — they over-trigger at scale.
- Third person, no XML tags — the description is injected into the system prompt, so it must read as neutral third-person text without markup.

### Principle 3: Concrete Over Abstract
Use specific verbs and nouns users recognize from their work.
- ✅ "Extracts speaker IDs when diarization JSON needs speaker attribution"
- ❌ "Processes audio metadata"

### Principle 4: Length Discipline
**Length: two-tier standard**

This section is the repo's number authority for description length.

#### Normal skills: target ≤150 chars; 250 is a SOFT lint line
- **Target**: Aim for ≤150 characters for scannability in lists/tooltips
- **Soft lint line**: 250 characters is a warning (not failure) — exceeds ideal but acceptable
- **YAML justification**: Normal skills MAY exceed 250 chars when a colocated YAML justification comment directly above the description:
  - Names the retained trigger surfaces that make ≤250 unachievable
  - Example: "# KEEP: Complex trigger surfaces for [X], [Y], [Z] workflows"
  - Unjustified >250 remains a violation

#### Router/CONDITIONAL skills: exception band ≤500
- **Exception band**: Router and CONDITIONAL skills may use ≤500 chars
- **Admission REQUIRES**: A firing-evidence note in the YAML justification:
  - "Firing evidence: [specific metric] from [corpus/live A/B test]"
  - A NEW router/CONDITIONAL skill with no evidence yet stays in the normal band (≤250 with YAML justification if needed)
  - Audit via YAML parse, not source lines

### Multilingual keyword belt (optional)

For repos with mixed-language prompts, an optional short keyword belt (≤50 chars) may appear at the end of the description: `Triggers: commit / PR / merge / コミット / 決定記録`. Zero of 14 superpowers skills use this pattern; include it if the repo's prompts are routinely non-English, skip it otherwise.

### Context-listing budget note

Descriptions share a context-listing budget — over-long ones can crowd other skills out of what Claude sees. Principle 4 distinguishes the 150-character target, the 250-character soft lint line with contextual justification, and the evidence-gated 500-character router exception. The platform's separate absolute ceiling is 1024 characters; it does not replace these authoring rules.

## Validation Checklist
Rendered length per Principle 4 two-tier standard:
- Normal skills: target ≤150, soft lint line 250 (with YAML justification comment if needed)
- Router/CONDITIONAL skills: exception band ≤500 only with firing evidence (a NEW router/conditional with no evidence yet stays in the normal band; audit via YAML parse, not source lines)
- Do NOT count YAML justification comments toward length — they are metadata
- Subjective preferences OK if paired with deterministic checks (e.g., "Prefer dark mode" + "Checks for @media prefers-color-scheme")

## Examples
### Good (Normal skill, ≤150)
"Generates idempotent API keys when collision detection is needed"

### Normal skill justification format (for a description that needs >250)
```yaml
# KEEP: Retains AWS auth trigger surfaces for cross-account role workflows.
description: Generates least-privilege IAM roles when cross-account access is needed
```

### Good (Router skill, with firing evidence)
Illustrative evidence format (replace with actual measurements before admission):

```yaml
# Firing evidence: 87% match rate from Jan 2026 support-ticket A/B corpus.
description: Classifies customer intent when support tickets need routing into 12 categories
```

### Bad (Vague description)
"Does many things related to data processing and transformation and formatting"
