# Description Design

Guidelines for writing skill descriptions that drive adoption and correct usage.

## Purpose
A skill description answers: "What does this do and when should I use it?"
It appears in skill lists, tooltips, and the skill catalog — it's the first
thing users read.

## Principles

### Principle 1: Intent-First
Lead with what the skill enables, not how it works.
- ✅ "Convert CSV to JSONL for streaming processing"
- ❌ "Reads lines, parses commas, handles quotes, writes newline-delimited JSON"

### Principle 2: When to Use
Include clear triggers and negative triggers.
- **Do use for**: X, Y, Z (positive triggers)
- **Do NOT use for**: A, B — use other-skill instead (negative triggers)
- **Disambiguate by positive specificity** — prefer naming what triggers the skill. When multiple skills could match similar queries, add explicit negative triggers to prevent mis-routing. **Limit to 2-3 negative triggers** — a long exclusion list buries the positives. A light positive redirect ("for X, use skill-Y") is also fine.
- Third person, no XML tags — the description is injected into the system prompt, so it must read as neutral third-person text without markup.

### Principle 3: Concrete Over Abstract
Use specific verbs and nouns users recognize from their work.
- ✅ "Extract speaker IDs from diarization JSON"
- ❌ "Process audio metadata"

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

For repos with mixed-language prompts, append a short keyword belt (≤50 chars) at the end of the description: `Triggers: commit / PR / merge / コミット / 決定記録`. Zero of 14 superpowers skills use this pattern; include it if the repo's prompts are routinely non-English, skip it otherwise.

### Context-listing budget note

Descriptions share a context-listing budget — over-long ones silently evict OTHER skills from what Claude sees. This is why Principle 4's numbers are hard rules, not style preferences.

## Validation Checklist
Rendered length per Principle 4 two-tier standard:
- Normal skills: target ≤150, soft lint line 250 (with YAML justification comment if needed)
- Router/CONDITIONAL skills: exception band ≤500 only with firing evidence (a NEW router/conditional with no evidence yet stays in the normal band; audit via YAML parse, not source lines)
- Do NOT count YAML justification comments toward length — they are metadata
- Subjective preferences OK if paired with deterministic checks (e.g., "Prefer dark mode" + "Checks for @media prefers-color-scheme")

## Examples
### Good (Normal skill, ≤150)
"Generate idempotent API keys with collision detection"

### Good (Normal skill, justified >250)
"# KEEP: Retains complex AWS auth trigger surfaces for cross-account roles
Generate IAM roles with least-privilege policies for cross-account access"

### Good (Router skill, with firing evidence)
"# Firing evidence: 87% match rate on production logs from Jan 2026 A/B test
Classify customer intent from support tickets into 12 categories"

### Bad (Unjustified >250)
"Does many things related to data processing and transformation and formatting"