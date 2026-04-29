# Write How-to Guide Protocol (Diátaxis: How-to Quadrant)

Write a **task-oriented** document. Recipe for a specific problem. The reader
is a competent user who already knows the fundamentals and needs to accomplish
a concrete goal.

**Vocabulary reference**: `standards/diataxis-taxonomy.md` §How-to Guide
**Style reference**: `standards/style-conventions.md`
**Pre-writing reference**: `standards/pre-writing-checklist.md` — apply before Phase 0

## How-to vs Other Modes

| This mode | NOT this mode |
|-----------|---------------|
| Solves one specific problem | Teaches fundamentals (→ Tutorial) |
| Assumes competence | Hand-holds beginners (→ Tutorial) |
| Goal-statement-first | Exhaustive option reference (→ Reference) |
| Efficient | Discursive explanation (→ Explanation) |

## Phase 0: Context Discovery

1. **Identify the specific goal** — "Rotate an API key", "Migrate from v1 to v2",
   "Set up CI for deployment". Goals should be concrete and verifiable.
2. **Confirm the reader's baseline** — what can they already do? A how-to guide
   on "migrate to v2" assumes they can run v1; if they can't, they need a
   tutorial first.
3. **Identify the success criterion** — how does the reader know the goal is
   achieved? ("The new key works; the old key returns 401")
4. **Check for existing Tutorial** — is there a related tutorial that teaches
   the fundamentals this how-to depends on? Link to it once in prerequisites.

## Phase 1: Goal-Statement-First

The **first line** of a how-to guide states the goal. No introduction, no
background, no history. The competent reader wants to know immediately
whether this doc solves their problem.

Example:

```markdown
# Rotate an API key without downtime

This guide shows you how to rotate a production API key while keeping
all services running.
```

If the reader is on this page by mistake (their problem is different), they
should realize it within 3 seconds.

## Phase 2: List Prerequisites

Before the steps, list:

- **Required access** (admin console, CLI, credentials)
- **Required tools** (specific versions)
- **Required knowledge** (link to tutorial or reference for fundamentals)
- **Required state** (what must be true of the system before starting)

If a prerequisite is missing, the reader should be able to find what they
need without starting the how-to.

## Phase 3: Steps to Solve the Problem

How-to steps differ from tutorial steps in one critical way: **they solve
the reader's problem, not introduce the feature**.

Compare:

| Tutorial step (wrong for how-to) | How-to step (correct) |
|----------------------------------|------------------------|
| "Let's create our first config" | "Update the config to point to the new key" |
| "Now we'll explore the API" | "Send a test request to verify the new key works" |
| "Next, we'll learn about roles" | "Grant the deployment role to the new key" |

Steps can branch based on the reader's situation:
- "If you're using Kubernetes, do X. If you're using bare metal, do Y."
- "If the service uses the old SDK, first update to v2."

Branching is **allowed and expected** in how-to guides. Unlike tutorials,
how-to readers know their own context.

## Phase 4: Verify the Result

The last step should verify the goal is achieved. Don't end on "run this
command and trust it worked." Provide an observable check:

- A status code, a log line, a UI change, a file's presence
- A command to run that returns expected output
- A URL to visit that should show expected content

## Phase 5: Troubleshooting

Optionally, list common failure modes and their fixes:

```markdown
## Troubleshooting

**Error: `401 Unauthorized` after rotation**
The old key is still cached. Wait 60 seconds and retry, or flush the cache
with `service flush-cache`.

**Error: `key not found` in new region**
Keys are region-scoped. Ensure the rotation ran in the correct region.
```

Keep troubleshooting focused on problems related to this specific goal.
General troubleshooting belongs in a separate Reference or Explanation doc.

## Rules

- **One goal per how-to.** If you're tempted to cover two related goals,
  write two how-to guides.
- **No teaching fundamentals.** Link to a tutorial if the reader needs to
  learn them.
- **No exhaustive option coverage.** How-to shows the path, not all paths.
  Link to Reference for exhaustive options.
- **No design discussion.** "Why we chose to rotate this way" belongs in
  Explanation or ADR.
- **Branching allowed.** Unlike tutorials, how-to guides can branch based on
  reader context.
- **Second person, imperative, present tense** per `standards/style-conventions.md`.

## Output Structure

```markdown
---
title: {How to <goal>}
last_reviewed: {YYYY-MM-DD}
applies_to: {version}
owner: {team}
mode: how-to
---

# How to {goal}

{Goal statement — one sentence confirming what this doc solves}

## Before you begin

- Required access: {...}
- Required tools: {...}
- Required knowledge: {link to tutorial or reference if needed}

## Steps

1. {Action with branching if needed}
2. {Action}
...

## Verify the result

{Observable check}

## Troubleshooting (optional)

{Common failures and fixes, scoped to this goal}
```

## Example

```markdown
---
title: How to rotate an API key without downtime
last_reviewed: 2026-04-29
applies_to: v3.x
owner: platform
mode: how-to
---

# How to rotate an API key without downtime

This guide shows you how to rotate a production API key while keeping all
services running.

## Before you begin

- Required access: admin console, kubectl access to the production cluster
- Required tools: `myapp-cli` v3.2 or later
- Required knowledge: see the [Authentication concepts](../explanation/auth.md)
  if API keys are unfamiliar
- Required state: existing API key visible in the admin console

## Steps

1. **Generate the new key** in the admin console:
   `Settings → API keys → Create new`. Copy the value.

2. **Add the new key to the application**, alongside the old one. Two
   keys can be active simultaneously during rotation:

   ​```bash
   myapp-cli secrets set api_key_secondary "<new-key>"
   ​```

3. **Roll the deployment** so all pods read the new secret:

   ​```bash
   kubectl rollout restart deployment/myapp -n production
   ​```

4. **Switch the primary key** in the admin console:
   `Settings → API keys → Promote secondary to primary`.

5. **Wait 60 seconds**, then revoke the old key in the admin console.

## Verify the result

Send a test request with the old key. It should return 401 Unauthorized:

```bash
curl -H "Authorization: Bearer <old-key>" https://api.example.com/v1/health
# Expected: HTTP/1.1 401 Unauthorized
```

Send a test request with the new key. It should return 200 OK.

## Troubleshooting

**Old key still works after revocation**
Cache propagation takes up to 60 seconds. Wait and retry.

**New key returns 403 instead of 200**
The new key has fewer permissions than the old one. Check role assignment
in `Settings → API keys → <key> → Permissions`.
```

**Why this works**: Goal stated in the first line. Prerequisites listed
before steps. Steps solve the goal (not introduce features). Branching
acceptable because reader knows their context. Verification step gives an
observable check. Troubleshooting scoped to this specific goal.

## Mode Clarity Check

This how-to passes the Diátaxis Mode Clarity gate if:

- The goal is stated in the first line
- Steps solve the goal (not introduce features)
- No teaching of fundamentals
- No exhaustive option listing
- No design rationale beyond 1 sentence
