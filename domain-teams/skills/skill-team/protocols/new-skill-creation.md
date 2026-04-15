# Protocol: New Skill Creation

**When to use**: creating a brand-new domain-team skill for a domain
not yet covered. E.g. adding `security-team`, `data-team`, or
`finance-team`.

**Output**: a complete skill directory with SKILL.md + standards +
protocols + gates, registered in the `using-domain-teams` router, in
3 atomic commits ready for PR.

Grounds on: all 6 `../standards/*.md`.

## Phase 1: Brainstorm (optional)

If the scope is unclear → run `skill-brainstorming.md` first. Skip
this phase if the user's request is already precise (e.g. "build a
security-team grounded in OWASP ASVS and NIST SSDF").

## Phase 2: Grounding Research

Run `grounding-research.md` to identify primary sources. This is
required for new teams — no skipping.

Output: a grounding plan listing standards files to create.

## Phase 3: Standards Drafting

For each standard identified in the grounding plan:

1. Create `standards/{name}.md`
2. Open with a "Primary Sources" section (2–5 sources with URLs / book
   citations)
3. Write the standard content — rules, definitions, taxonomies
4. Close with an "Anti-Patterns" section listing what NOT to do
5. Keep length 60–150 lines (see `../standards/skill-md-structure.md`)

Apply the grounding rule ruthlessly: every load-bearing claim cites a
primary source. If you catch yourself inventing a taxonomy, stop and
re-consult the research report.

## Phase 4: Protocols Drafting

For each workflow the skill will support, create one protocol file:

1. Create `protocols/{verb-noun}.md` (e.g. `threat-modeling.md`)
2. Open with "**When to use**" and "**Output**" lines
3. List the phases as numbered sections (`## Phase 1: ...`)
4. Each phase specifies: what to do, what to produce, reference to
   standards files
5. Close with "Rules" and "Anti-Patterns" sections
6. Keep length 60–150 lines

Protocol count guideline:
- Brand-new team: 2–4 protocols initially (core workflows only)
- Don't over-plan — add more protocols in future commits as workflows
  emerge
- Avoid one mega-protocol that covers everything; split by intent

## Phase 5: Gates Drafting

For each quality dimension the skill enforces, create one gate file
(checklist OR rubric — see `../standards/gate-system.md` for when to
use which).

### MUST gates (1–3)

Cover:
- Structural completeness of the main artifact
- Correctness of output format
- Critical safety checks (security, data privacy, deployment safety)

### SHOULD gates (1–3)

Cover:
- Quality dimensions (depth, coherence, style)
- Primary-source grounding (where applicable)

### MAY gates (0–3)

Cover:
- Audits or specialist checks that aren't always needed

Each gate file has:
- For checklists: per-item ID (`CHK-{SCOPE}-{NNN}`), failure type, verdict rules, JSON output schema
- For rubrics: dimension definitions with 🔴/🟡/🟢, verdict rules, output format

## Phase 6: SKILL.md Writing

Write the SKILL.md following `../standards/skill-md-structure.md` exactly:

1. **Frontmatter**: name, description (with Use when / Do NOT use for / Delivers), optional CJK suffix
2. **Persona**: opening stance, primary-source anchors, Mission / Delivers / Done when lines
3. **When to Use** / **When NOT to Use**
4. **Language** (standard output_language clause)
5. **Context Discovery**
6. **Quality Gates** (4-tier table)
7. **Gate Protocol**
8. **Resource Manifest**
9. **Behavioral Rules** + **Agents** table
10. **Agent Launch Protocol** (worker + evaluator templates)
11. **Workflows** (one sub-section per workflow, with phase table)
12. **Cross-Domain Awareness**
13. **Worker BLOCKED Handling**

Token budget: aim ~3,000–4,500, hard cap ~6,000 (see `standards/skill-md-structure.md` §Token Budget).

## Phase 7: Router Integration

MODIFY `domain-teams/skills/using-domain-teams/SKILL.md`:

1. Add a row to the **Available Teams** table:
   ```
   | `{team-name}` | {mission line} | {delivers} |
   ```
2. Add 1–3 rows to the **Intent Routing** table:
   ```
   | {intent phrase} | `{team-name}` |
   ```
3. If this team has ordering relationships with other teams, add an
   entry to **Ambiguous Cases**

## Phase 8: Version Bump

MODIFY `domain-teams/.claude-plugin/plugin.json`:
- Increment MINOR version (`x.y.0 → x.(y+1).0`) because adding a new
  team is additive
- Do NOT bump PATCH — this is a structural addition

## Phase 9: Commit Split

Execute the 3-commit split per `../standards/commit-convention.md`:

1. **Commit 1/3**: all new `standards/*.md` files
2. **Commit 2/3**: all new `protocols/*.md`, `checklists/*.md`,
   `rubrics/*.md` files
3. **Commit 3/3**: new `SKILL.md`, modified `using-domain-teams/SKILL.md`,
   modified `.claude-plugin/plugin.json`

## Phase 10: Dogfood Verification

Before opening the PR:
1. Run `checklists/skill-completeness-checklist.md` on the new SKILL.md
2. Run `checklists/commit-split-checklist.md` on the 3 commits
3. Run `rubrics/primary-source-grounding.md` on the new standards
4. Run `rubrics/skill-coherence.md` on the complete skill

Fix any issues before pushing.

## Rules

- New team skill files always go under
  `domain-teams/skills/{team-name}/` — never directly in
  `domain-teams/`
- One PR per new team creation, not one PR per commit
- If any phase produces zero files (e.g. no MAY gates needed), that's
  fine — don't invent files for completeness
- Workers launched during this protocol must follow
  `../standards/agent-interface.md` Resource Paths format

## Anti-Patterns

- ❌ Skipping grounding research for "obvious" domains — every domain
  has surprises
- ❌ Copying another team's SKILL.md and editing in place — leads to
  residual references
- ❌ Creating empty skeleton files for "future" protocols or gates
- ❌ Running dogfood verification after opening PR instead of before
