# Skill `description` writing — industry research (verified)

> deep-research, 2026-06-19. 6 angles · 15 sources fetched · 9 load-bearing/contested
> claims adversarially verified (3 voters each). Basis for a house skill-description standard.
> **Several popular claims were REFUTED on verification — see §Refuted.** Confidence tags per finding.

## Bottom line

Write descriptions **short, positive, and front-loaded**: `what it does + when to use it`
(specific real-user trigger phrases), one line, procedures left to the body. The two things
that are *officially confirmed* to matter: **(1) there is a shared skill-listing budget that
silently drops skills at scale → short descriptions are load-bearing when you have many skills**;
**(2) the description is the primary selection signal, so it must be specific and distinct.**
Several community "power tips" (when-only, "ALWAYS invoke" directives, "Do NOT use for X"
negative boundaries) did **not** survive verification.

## CONFIRMED (high confidence)

- **Shared skill-listing budget is real and official.** Claude Code loads all skill
  name+descriptions into a budget that scales at ~1% of the context window (~15k chars), caps
  each entry's description+when_to_use at **1536 chars**, and on overflow **silently drops the
  least-invoked skills** (still directly invocable, not auto-triggered). Knobs:
  `SLASH_COMMAND_TOOL_CHAR_BUDGET`, `skillListingBudgetFraction`, `maxSkillDescriptionChars`.
  → With many skills, **short descriptions are not cosmetic — long ones can evict other skills.**
  (official Claude Code docs; GitHub issue #13099 "Showing 42 of 63 skills due to token limits")
- **Real shipped skills are short.** A measured 63-skill corpus averaged **263 chars**; guides
  shipping 20+ production skills run **110–150 chars** and recommend ≤130–150 for 60+ collections.
  superpowers' 14 skills average **140 chars**. Anthropic's own examples are ~150–250.
- **The description is the primary selection signal; specific + distinct beats vague.** Anthropic
  "writing tools for agents": distinct purpose per tool, names reflecting natural task
  subdivisions reduce mis-selection; fewer well-scoped tools beat many thin ones.
- **Anthropic official norm:** description = **what + when**, third person, concise, ≤1024 chars,
  front-load specific positive trigger terms (incl. "even if the user doesn't name the domain").
- **Many skills degrade selection/performance** (corroborated) — via BOTH wrong-selection AND
  context bloat (e.g. GitHub-MCP 95%→71% attributed to context bloat; ~9.5% avg MCP decline).
  → favor curation + distinct descriptions; archive unused skills.

## REFUTED / don't rely on (verification overturned these)

- **❌ "WHEN-only; never summarize what — a workflow summary makes the agent skip the body."**
  REFUTED 3/3. Traces to a single obra/superpowers anecdote ("one review instead of two"),
  unreplicated, and **contradicted by Anthropic's progressive-disclosure model** (the description
  gates *activation*; the full body loads as a unit once relevant). Anthropic explicitly says
  include **what + when**. ✅ Correct rule: include what+when+triggers; keep the *step-by-step
  procedure* out of the description (that part is fair) — but "when-only" is overstated.
- **❌ "'ALWAYS invoke' directive descriptions are good."** REFUTED. They raise true-positives in
  isolated tests (Seleznov 650-trial, OR≈20) but **increase over-triggering at scale** and are
  **not Anthropic-endorsed** (Anthropic's skill-creator optimizer exists to cut the false-positives
  that broad/aggressive descriptions cause). Tested mostly with few skills — not the many-skill
  collision regime.
- **❌ "Negative boundaries ('Do NOT use for X') reduce false activation."** CONTESTED / leans
  refuted. Anthropic recommends disambiguation via **specific positive triggers**, never "do not"
  clauses; LLMs reliably **mishandle negation** (MIT 2025; "negative constraints backfire" work).
  Mild *positive* scoping ("for image work, use image-processor") is fine; behavioral negation is unreliable.
- **❌ "+18.4pp selection accuracy from rewriting descriptions" (arXiv 2510.14453).** REFUTED —
  that gain is from a tool-calling **architecture** change (natural-language vs JSON outputs),
  **not** description-wording refinement. Don't cite it for "wording matters."
- **❌ "Skill shadowing degrades accuracy up to 21% at 202 skills" (arXiv 2605.24050).** REFUTED
  high — the arXiv id is **future-dated and unverifiable (likely fabricated by a search agent)**.
  Do NOT cite. (The general many-skills-hurt effect is real; this specific paper/number is not.)

## REPORTED but unverified (treat with caution / self-check)

- **Multi-line YAML block-scalar descriptions may parse as first-line-only** (~40% of activation
  failures, per one blog). NOT separately verified, and our own multi-line descriptions DO load —
  so it may be version/parser-specific or overstated. **Self-check our YAML before acting on it.**
- **"wording matters for activation"** is supported only at blog/qualitative level (Seleznov
  50→100%; philschmid 66.7→100% from a description rewrite; Anthropic's qualitative "small
  refinements → dramatic improvements"). Directionally true, not a hard number.
- **CJK / non-English trigger keywords are redundant** for clear non-English prompts — our own
  12-probe A/B (identical triggering with/without CJK) + the JP finding that truncation happens
  **from the end** (so appended CJK disappears first anyway). Drop CJK redundancy.

## Cross-ecosystem (for comparison)

- **Cursor rules**: `description` + `globs` + `alwaysApply`; if not always-applied, the agent reads
  the **description** to decide relevance (same pure-reasoning model). Keep rules focused, <500 lines.
- **Windsurf**: activation modes always_on / glob / model_decision / manual; reserve always_on for
  universal rules to avoid context pollution.
- **Codex AGENTS.md**: short, specific, commands early, one real snippet beats prose.
- **MCP tool descriptions**: distinct purpose, action-verb naming; a 2025 audit found 97.1% have a
  quality issue → the metadata-quality problem is industry-wide, not skill-specific.

## Synthesized guidance (what survived) → house standard

1. **Length: target ~150–250 chars; with a large collection (we have 184) lean ~150.** Hard ceiling
   1024 (spec/Codex). Short isn't cosmetic — the shared budget silently evicts skills.
2. **Structure: `what + when`, positive specific triggers, front-loaded** (most important trigger
   words first — truncation is from the end). Use real user phrasings, not formal jargon.
3. **Keep the step-by-step procedure / grounding citations OUT of the description** → body. (This is
   the defensible core of the "don't summarize workflow" idea.)
4. **Prefer one-line descriptions; verify our multi-line YAML still parses fully.**
5. **Disambiguate by being specific + distinct, NOT by "Do NOT use" negation or "ALWAYS invoke"
   directives.** Positive, precise scope.
6. **Drop CJK redundancy** (A/B-proven redundant; also first-to-be-truncated).
7. **Curate skill count** — many overlapping skills hurt selection regardless of description.

## Pipeline stats / caveats

- 6 angles, 15 sources fetched (~70 claims), 9 load-bearing/contested claims verified (3 voters each).
- Most measured numbers are blog-tier self-experiments (Seleznov, philschmid, the 63-skill gist) —
  directional, not peer-reviewed. The budget/limit facts are official-doc-confirmed. Two cited
  "papers" (2510.14453 misattributed; 2605.24050 likely fabricated) were caught by verification.
