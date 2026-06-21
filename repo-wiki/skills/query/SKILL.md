---
name: query
description: |
  Answer any question about repo implementation, behavior, symbol location, data flow, or design — from the knowledge base, before reading src/. Use for 'why did we', 'how does X work', 'where is Y'. Setup → init; update → ingest.
---

# Repo Wiki — Query Workflow

Read-only knowledge base query. `.repo-wiki/` is a *best-effort
implementation cache*; `src/**` is the authoritative source of current
behavior. This skill verifies cached current-behavior claims against
`src/` at key moments via the verification trigger system below.

## Prerequisite Check

Read `.repo-wiki/index.md`. If it does not exist:
> Knowledge base not initialized. Run `/repo-wiki:init` first.

Exit cleanly.

## Step 1: Read Index

Load `.repo-wiki/index.md` to see all available entity, concept, source,
and synthesis pages.

## Step 2: Find Relevant Pages

Match the question to page categories:
- About a specific module → `entities/`
- About a pattern, ADR, or "why" decision → `concepts/`
- About recent changes / what happened when → `sources/` (most recent first)
- Already answered before (similar question) → `syntheses/`

Load ONLY the relevant pages — do not load all entities or all concepts.
If unsure which pages are relevant, scan titles + one-line descriptions
in `index.md`, then pick.

## Step 3: Draft Answer from `.repo-wiki/`

Draft the answer using only the `.repo-wiki/` pages loaded in Step 2.
Do NOT yet present to user — Step 3.5 will decide whether to verify
against `src/`.

Identify in the draft, for the verification stage:
- **current-behavior claims** (e.g., "AuthModule uses JWT")
- **past-decision claims** (e.g., "we switched from jsonwebtoken to jose in 2026-04-20")
- **pointer claims** (e.g., "Auth lives in src/auth/")

Decisions and pointers don't need verification (decisions don't change
retroactively; pointers can rot but are quick to verify if needed).
Current-behavior claims are verification candidates.

## Step 3.5: Verification Trigger Evaluation

`.repo-wiki/` is a cache, not the authority. Evaluate these triggers;
any positive trigger initiates `src/` verification of current-behavior
claims:

| ID | Trigger | If positive, verify by |
|---|---|---|
| **T1** | Any loaded page has `last_updated > 60 days` | Reading files in that entity's `paths:` to spot-check current-behavior claims |
| **T2** | Question contains current-state keyword (see list below) | Spot-checking current-behavior claims against `src/` |
| **T3** | Answer will inform code the user is about to write or modify | Verifying entry-point files mentioned in the answer still exist + match described shape |
| **T4** | Loaded source page contains TODO / "subject to change" / "待確認" markers | Reading the corresponding `src/` area and updating the answer |
| **T5** | Multiple loaded pages contradict each other | Reading `src/` to arbitrate |
| **T6** | Question is purely about past decisions ("why did we", "rejected alternative") | **Negative trigger — DO NOT verify** (trust `.repo-wiki/`) |
| **T7** | User explicitly requests verification ("verify against src/", "make sure this is still true") | Verifying every claim against `src/` |

**Eager policy**: T1, T2, T3, T4, T5, T7 all trigger verification when
positive. Only T6 (pure decision question) skips verification entirely.

**Detection priority**: T7 > T6 > {T1, T2, T3, T4, T5}.
- T7 (user explicit) overrides everything.
- T6 (pure decision) blocks verification when no T2/T3 keyword is present.
- Otherwise any positive T1-T5 triggers segmented output.

For each verifiable claim, locate the relevant `src/` file via the
loaded entity's `paths:` frontmatter. If `paths:` is missing on an
entity:
- Log warning: "Entity `<name>` missing `paths:` frontmatter — falling back to grep-based discovery (slower)"
- Use grep to find candidate files

Verification depth: read the relevant function / file region; compare
key facts to the claim. Don't read entire files unless necessary.

### Trigger Detection Specification

Each trigger has a concrete detection rule. False positives are
acceptable (Eager policy) — false negatives let stale answers through.

#### T1 — Stale page (mechanical)

**Rule**: For each page loaded in Step 2, parse `last_updated` from
frontmatter as `YYYY-MM-DD`. Compute days between that date and today.
If `days > 60`, T1 fires for that page.

**Edge cases**:
- Missing `last_updated` → treat as T1 positive (assume stale)
- Malformed date → log error, treat as T1 positive
- Future date (clock skew) → log warning, treat as T1 negative

#### T2 — Current-state keyword (lexical)

**Rule**: Check the user's question (case-insensitive, word-boundary
aware) against this keyword list. Any match → T2 positive.

| Lang | Keywords |
|---|---|
| EN | `currently`, `now`, `today`, `right now`, `at the moment`, `still`, `as of`, `these days`, `is…still`, `does…still`, `is the current` |
| JP | `今`, `現在`, `現状`, `今でも`, `今も`, `依然として`, `今のところ` |
| ZH | `現在`, `目前`, `如今`, `還有沒有`, `還是`, `現行的`, `如今還`, `目前還` |

**Positive examples**:
- "How does AuthModule **currently** work?"
- "Is JWT validation **still** at middleware?"
- "**現在**的 Payment flow 是什麼？"
- "**目前**還有沒有用 jsonwebtoken？"

**Negative examples**:
- "How was AuthModule **originally** designed?" — past-tense, no match
- "What's the **history** of this module?" — historical, no match
- "Why did we choose JWT?" — pure why, no current-state keyword

**Edge case**: "currently" embedded in compound like "concurrently" —
word-boundary regex `\b(currently|now|...)\b` prevents false match.

#### T3 — High-stakes / informs new code (contextual)

**Rule**: T3 fires if EITHER condition holds:

(a) **Action-imperative keyword in question**:

| Lang | Keywords |
|---|---|
| EN | `help me implement`, `I want to add`, `I need to refactor`, `where should I put`, `how should I write`, `where do I add`, `where should I modify`, `I'm about to change`, `I'm going to add`, `should I add`, `where to put` |
| JP | `実装したい`, `追加したい`, `リファクタしたい`, `どこに追加`, `どう書けば`, `これから変更` |
| ZH | `請幫我寫`, `我要加`, `我需要改`, `我想 implement`, `要怎麼寫`, `應該加在哪`, `準備改` |

(b) **Active code work in session** — Write / Edit / MultiEdit tool was
called within the last 10 turns on a path that overlaps with the
question's subject

**Positive examples**:
- "How should I **refactor** PaymentService to handle retries?" → T3 (a)
- "**Where should I add** the new auth middleware?" → T3 (a)
- "**I'm about to change** AuthModule to use jose, what do I need to know?" → T3 (a)
- (User just edited `src/auth/jwt.ts`) "How does the JWT validation flow work?" → T3 (b)

**Negative examples**:
- "Why did we choose Postgres?" — pure why, no action verb, no recent edits
- "What does AuthModule do?" — descriptive, no action verb
- "How does auth flow currently work?" — T2 fires, but T3 alone wouldn't

#### T4 — TODO / subject-to-change marker (mechanical grep)

**Rule**: For each loaded page (entity OR source OR concept), search
the body text (case-insensitive) for any of:

- `TODO`
- `subject to change`
- `待確認`
- `tentative`
- `暫定`
- `(WIP)`
- `FIXME`
- `要確認`
- `not finalized`

Any match → T4 positive. Verify the area the marker pertains to.

(Markers in code blocks within the page body still count — docs often
quote code with TODOs.)

#### T5 — Page contradiction (LLM judgment, bounded)

**Rule**: After loading pages in Step 2, do a focused LLM-judgment pass
restricted to:

- Same module mentioned in 2+ loaded pages with **different stated
  responsibilities or entry points**
- Same concept/pattern mentioned with **different application scope**
- Decision in source page that **directly negates** a claim in entity
  page (e.g., source says "removed JWT validation from middleware",
  entity says "validates at middleware layer")

**NOT a contradiction** (don't trigger T5):
- Different entities listing different paths (different scope, not conflict)
- One page silent on a topic another mentions (gap, not conflict)
- Phrasing variation describing the same thing

**Positive example**:
- entity `AuthModule.md` says "uses jose for JWT signing"
- source `2026-05-01-jwt-revert.md` says "reverted from jose back to jsonwebtoken"
- → T5 positive; verify against `src/auth/jwt.ts` to determine truth

**Negative example**:
- `AuthModule.md` mentions `src/auth/jwt.ts` as entry point
- `PaymentService.md` doesn't mention auth at all
- → not a contradiction; T5 negative

#### T6 — Pure decision question (negative trigger)

**Rule**: T6 fires (skipping verification) ONLY when ALL of these hold:

1. Question contains historical/decision keywords:
   - EN: `why did we`, `rejected alternative`, `what was the reason`,
     `what was considered`, `why was X chosen`, `historical reason`
   - JP: `なぜ`, `当時の判断`, `却下された`, `検討した`, `決定理由`
   - ZH: `為什麼當初`, `當時為什麼`, `什麼原因`, `為什麼選`, `決定的原因`, `考慮過什麼`, `歷史原因`

2. Question does NOT contain T2 (current-state) keywords

3. Question does NOT contain T3 (action-imperative) keywords

If ANY of (2) or (3) is violated, T6 does NOT fire — verification proceeds.

**Positive examples (T6 fires, no verification)**:
- "**Why did we** choose Postgres over MongoDB?"
- "What **alternatives were considered** for auth?"
- "**為什麼當初**選 JWT？"

**Negative examples (T6 does NOT fire)**:
- "Why does AuthModule **currently** throw JwtError?" — T2 keyword "currently" present → T6 blocked
- "Why is X used **and how should I extend it**?" — T3 keyword "how should I" present → T6 blocked

#### T7 — Explicit verification request (lexical)

**Rule**: Question contains any of:

| Lang | Keywords |
|---|---|
| EN | `verify`, `verify against`, `check against`, `make sure`, `is this still true`, `validate`, `confirm against the code`, `against current src` |
| JP | `確認`, `検証`, `本当に`, `今のコードで` |
| ZH | `確認`, `驗證`, `對照原始碼`, `現在的 code 還是這樣嗎`, `比對程式碼` |

Any match → T7 positive → verify EVERY claim against `src/`, even pointers.

### Verification Budget (applies when ANY trigger fires)

Verification reads `src/` — the budget caps how many files get opened so a
single query stays bounded and the user knows the verification depth.

**Budget formula**:

```
total_paths = sum(len(entity.paths)) across all loaded entities
            (expand globs to concrete file count; if `paths:` missing,
             use grep candidate count)

budget = max(1, min(10, ceil(0.05 × total_paths)))
```

Examples:
- 1 entity, 12 paths → ceil(0.6) = 1 → budget = 1 file
- 1 entity, 80 paths → ceil(4.0) = 4 → budget = 4 files
- 2 entities, 220 total paths → ceil(11.0) = 11 → cap → budget = 10 files
- T7 (explicit verify) → budget remains capped at 10; T7 verifies *every claim* but file reads still cap at 10. If 10 < claim count, prioritize current-behavior claims and report uncovered claims under Unverified.

**File selection priority within budget** (deterministic, reportable):

1. **Claim-mentioned files** — files explicitly named in the verifiable claim
2. **Entry points** — files in the entity's `Common Entry Points` section
3. **Most-recently-modified** — newest `git log` mtime among remaining `paths:`
4. **Stop when budget exhausted**

When a path resolves to a directory or glob, expand to files via `git ls-files`
restricted to that prefix; count expanded files toward `total_paths`.

**Reporting**: every triggered query MUST emit a `## Verification Coverage`
section in the segmented output (Step 4). This makes the verification depth
visible — "I checked 3 of 80 paths" is honest; silent partial-verification is
the failure mode this guards against.

## Step 3.6: Stale Feedback Loop

If verification reveals `.repo-wiki/` has stale or wrong claims, after
presenting the answer (Step 4) suggest a corrective ingest:

> Found stale claim in [AuthModule](.repo-wiki/entities/AuthModule.md):
> page says "throws AuthError" but `src/auth/jwt.ts:42` throws `JwtError`.
> Suggest: `/repo-wiki:ingest "AuthError was renamed to JwtError"`

This makes verification an active feedback loop into the ingest
cycle — not just a one-shot warning.

## Step 4: Present Answer

If NO trigger fired (T6 hit, or no triggers positive), present in the
standard inline-citation format:

```
[Answer with inline citations like [AuthModule](.repo-wiki/entities/AuthModule.md).]

**Sources**:
- [AuthModule](.repo-wiki/entities/AuthModule.md)
- [2026-04-20 jwt refactor](.repo-wiki/sources/2026-04-20-jwt-refactor.md)
```

If ANY trigger fired, present in **segmented format**:

```markdown
[Brief introduction sentence.]

## Verified Claims (against src/)
- <Claim> — verified at `src/<path>:<line>` on <today>
- <Claim> — verified at `src/<path>` on <today>

## Unverified Claims (from .repo-wiki/ cache)
- <Claim> — sourced from [PageName](.repo-wiki/<path>); not verified this query
  (reason: pure decision claim / outside trigger scope / over verification budget)

## Discrepancies Found
- `.repo-wiki/<page>` says X but `src/<path>:<line>` shows Y
  → Suggest: `/repo-wiki:ingest "<correction context>"`

## Verification Coverage
- Triggers fired: <e.g. T2, T4>
- Files read: <N> of <total_paths> candidate paths (<percent>%)
- Selection: <claim-mentioned + entry-points + most-recent | grep-fallback>
- Uncovered paths in scope: <up-to-3 examples>, … (<remainder> more)

**Sources consulted**:
- [PageName](.repo-wiki/<path>)
```

If no discrepancies, omit the Discrepancies section.
If no unverified claims, omit the Unverified section.
The Verified section always appears when triggers fire — even if
empty, it tells the user "I checked but had nothing to verify".
The Verification Coverage section is **mandatory** when triggers fire;
omit "Uncovered paths" line only when files-read equals total_paths.

(Use repo-root-relative paths in the answer so links are clickable from
any IDE / GitHub view.)

## Step 5: Offer to Save as Synthesis

Ask:
> Would you like me to save this answer to `.repo-wiki/syntheses/` so it's available for future queries?

If yes, write `.repo-wiki/syntheses/<question-slug>.md`:

```markdown
---
title: "<Question asked>"
type: synthesis
date: YYYY-MM-DD
sources: ["entities/X", "concepts/Y", "sources/Z"]
verification_run: <yes if triggers fired, no if T6>
verified_paths: [<src/ paths spot-checked>]            # only if verification_run: yes
verification_budget: <N>                                # files allowed by budget formula
verification_coverage_pct: <0-100>                      # files-read / total-paths
---

## Question
<exact question asked>

## Answer
<full answer — preserve segmented format and verification markers if any>

---

> Answered on <date>. Verification status preserved above. For current
> behavior, re-verify against src/ if more than 30 days have passed
> since this synthesis was saved.
```

Append to `.repo-wiki/log.md`:

```
## [YYYY-MM-DD] query | <question-slug>
- Pages consulted: <list>
- Triggers fired: <list of trigger IDs, or "none">
- Verification: <files_read>/<total_paths> (<pct>%)   # omit if no triggers fired
- Synthesis saved: .repo-wiki/syntheses/<slug>.md
  (or: not saved)
```

(Append the log entry whether or not the synthesis was saved — the
query itself is the operation worth recording.)

## If No Relevant Pages Exist (Gap Handling)

Be explicit — do not silently fall back. Say:
> The knowledge base doesn't have a page for this topic yet.

Then offer ONE of:

> **Option A**: I can read `src/<module>/` directly to answer this, but the answer won't be saved to the knowledge base.
>
> **Option B**: Run `/repo-wiki:ingest <scope>` to build the knowledge base for this area first, then re-ask.
>
> **Option C**: If you have context I can capture, run `/repo-wiki:ingest "<the context>"` to seed it.

Do not guess or hallucinate. An explicit gap is more useful than a
confident wrong answer — and it tells the user exactly which channel
to use to fill it.

## Rules

NEVER:
- Hallucinate knowledge not present in `.repo-wiki/` pages
- Present current-behavior claims as authoritative without running
  verification triggers
- Skip verification when T1-T5 or T7 fires (Eager policy)
- Open more `src/` files than the verification budget allows
  (`max(1, min(10, ceil(0.05 × total_paths)))`)
- Emit segmented output without the `## Verification Coverage` section
  when any trigger fired
- Auto-trigger `/repo-wiki:ingest` from query (only suggest)
- Use `[[wikilinks]]` — only standard markdown links: `[Name](path)`
- Cross-check git log per query in v1 (full git-aware staleness ships
  in v2 `/repo-wiki:lint`)

ALWAYS:
- Cite every claim with a standard markdown link
- Run Step 3.5 trigger evaluation on every query (it's cheap)
- Use segmented output (Verified / Unverified / Discrepancies /
  Verification Coverage) when any trigger fires
- Compute and respect the verification budget before opening any `src/` file
- Report files-read / total-paths in `## Verification Coverage` so users
  see the actual depth, not just "verification ran"
- Suggest `/repo-wiki:ingest` when verification finds a discrepancy
- Be explicit when the knowledge base has a gap — gaps are feedback
  for the next `/repo-wiki:ingest` run
- Append to `log.md` whether or not the synthesis was saved
- Record `verification_run` and `verified_paths` in saved syntheses
