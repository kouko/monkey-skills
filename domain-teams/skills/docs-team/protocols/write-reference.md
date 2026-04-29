# Write Reference Protocol (Diátaxis: Reference Quadrant)

Write an **information-oriented** document. Austere, authoritative,
exhaustive. The reader looks up exact facts quickly. Reference mirrors the
structure of what it describes (API, CLI, config schema).

**Vocabulary reference**: `standards/diataxis-taxonomy.md` §Reference
**Style reference**: `standards/style-conventions.md`
**API sub-case**: `standards/api-reference-structure.md`
**Pre-writing reference**: `standards/pre-writing-checklist.md` — apply before Phase 0

## Reference vs Other Modes

| This mode | NOT this mode |
|-----------|---------------|
| Lookup table / catalog | Sequential lesson (→ Tutorial) |
| Exhaustive, mechanically consistent | Selective recipe (→ How-to) |
| Neutral, descriptive | Discursive rationale (→ Explanation) |
| Structure mirrors the thing | Structure mirrors a journey |

## Phase 0: Context Discovery

1. **Identify what is being referenced** — an API, a CLI, a config schema, a
   protocol, a file format, a constant list. Reference docs describe **things**,
   not processes.
2. **Determine the source of truth** — where does the canonical description
   live? Code? Protocol buffer? OpenAPI spec? Config schema?
3. **Decide: auto-generate or hand-write?**
   - If OpenAPI / protobuf / similar schema exists → auto-generate and add
     descriptions; hand-writing is wasteful and drifts from source of truth
   - If no machine-readable spec → hand-write, but follow the same structure
     as if it were auto-generated
4. **API sub-case**: if describing an HTTP API, also load
   `standards/api-reference-structure.md` for required fields per operation.

## Phase 1: Structure Mirrors the Thing

Reference structure should match the structure of what is being described:

| Subject | Structural mirror |
|---------|-------------------|
| HTTP API | Paths → operations → parameters → responses |
| CLI | Commands → subcommands → flags → arguments |
| Config schema | Sections → keys → types → defaults |
| Library | Modules → classes → methods → parameters |
| Protocol | Messages → fields → types → constraints |

Do not impose a narrative structure on reference material. The reader navigates
by looking up a specific thing; they do not read linearly.

## Phase 2: Document Every Entry Consistently

For each entry (endpoint, command, option, field, method), document:

1. **Name** (the canonical identifier)
2. **Signature or prototype** (how it appears in code)
3. **Type** (return type, parameter type, field type)
4. **Description** (1-2 sentences, descriptive not discursive)
5. **Constraints** (valid values, range, format, required/optional)
6. **Default** (if optional)
7. **Example** (minimal, runnable if possible)

**Consistency is the #1 reference quality.** If one entry has a "Since version"
field, all entries must have it. Inconsistent templates force readers to guess.

## Phase 3: Cross-Cutting Concerns

Some things apply to many entries — document them **once** at the top of the
reference, not repeated per entry:

- Authentication / authorization rules (HTTP APIs)
- Rate limiting (HTTP APIs)
- Pagination conventions (HTTP APIs)
- Error codes and error response shapes
- Versioning policy
- Naming conventions (casing, prefixes)
- Units (byte, millisecond, UTC, etc.)

Individual entries then link back to these cross-cutting docs instead of
restating them.

## Phase 4: Examples

Reference examples are **minimal** — they show the shape, not a realistic
workflow. Compare:

| Reference example (correct) | Tutorial example (wrong for reference) |
|-----------------------------|-----------------------------------------|
| `GET /users/{id}` → `{"id": "u_1", "name": "Alice"}` | "Let's fetch Alice's profile to see..." |
| `myapp deploy --env prod` | "First, let's deploy to staging, then..." |
| `config.log_level = "debug"` | "You might want to enable debug logging if..." |

One minimal example per entry is usually enough. For complex entries (multiple
valid parameter combinations), show 2-3 distinct shapes.

## Phase 5: Consistency Pass

Before finalizing:

1. **Template consistency** — every entry has the same sections in the same order
2. **Terminology consistency** — same name for same concept throughout
3. **Link consistency** — cross-references use the same format
4. **Example consistency** — all examples use the same placeholder conventions
   (`u_1` or `user_123`, not both)

## Rules

- **No narrative.** Reference describes; it does not tell stories.
- **No teaching.** If a concept needs explaining, link to an Explanation doc.
- **No tutorials.** "How to use this" links to a How-to guide.
- **No opinions.** Reference is neutral. Design rationale belongs in Explanation
  or ADR.
- **Exhaustive.** Every parameter, every field, every error code documented.
  "Rarely used" is not an excuse — rarely used fields are the hardest to
  remember and the first place readers look.
- **Scannable.** Tables, consistent headings, monospace for literal values.
- **Present tense.** "Returns the user object", not "Will return" or "Returned".

## Output Structure

```markdown
---
title: {Subject} Reference
last_reviewed: {YYYY-MM-DD}
applies_to: {version}
owner: {team}
mode: reference
---

# {Subject} Reference

{1-sentence scope: what this reference covers}

## Cross-cutting concerns

### Authentication
### Rate limiting
### Error codes
### Versioning
{...}

## {Category 1}

### {Entry 1}

**Signature**: `{signature}`
**Type**: `{type}`

{1-2 sentence description}

**Parameters**:

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
{...}

**Returns**: {...}

**Example**:
​```
{minimal example}
​```

### {Entry 2}
...
```

For **API reference** specifically, also cover the required fields from
`standards/api-reference-structure.md` (request body schema, error responses,
authentication per operation, runnable example).

## Example

```markdown
---
title: myapp-cli Reference
last_reviewed: 2026-04-29
applies_to: v3.5.x
owner: platform
mode: reference
---

# myapp-cli Reference

Command-line interface for managing myapp deployments.

## Cross-cutting concerns

### Authentication

All commands require `MYAPP_TOKEN` to be set. Generate a token in
`Settings → CLI tokens`.

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Generic failure |
| 2 | Authentication error |
| 3 | Network error |
| 4 | Validation error |

## Commands

### `secrets set`

**Signature**: `myapp-cli secrets set <name> <value>`

Sets a named secret in the current environment.

**Parameters**:

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `name` | string | yes | — | Secret name. Must match `[a-zA-Z_][a-zA-Z0-9_]*` |
| `value` | string | yes | — | Secret value. Quoted to preserve whitespace. |
| `--env` | string | no | `production` | Target environment |

**Returns**: 0 on success; 4 if name is invalid; 2 if not authenticated.

**Example**:

​```bash
myapp-cli secrets set api_key "sk-abc123"
​```

### `secrets list`

**Signature**: `myapp-cli secrets list [--env=<environment>]`

Lists secret names (values are never printed).

**Parameters**:

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--env` | string | no | `production` | Target environment |

**Returns**: 0 on success; 2 if not authenticated.

**Example**:

​```bash
myapp-cli secrets list --env=staging
​```
```

**Why this works**: Structure mirrors the CLI itself (commands → flags →
exit codes). Every entry follows the same template. Cross-cutting concerns
documented once at the top, linked from individual entries. Examples are
minimal — they show shape, not workflow.

## Mode Clarity Check

This reference passes the Diátaxis Mode Clarity gate if:

- Structure mirrors the subject (no imposed narrative)
- Every entry follows the same template
- No "how to use" or "when to use" beyond 1 sentence per entry
- No design rationale or historical context
- Examples are minimal shape demonstrations, not workflows
- Cross-cutting concerns documented once at the top
