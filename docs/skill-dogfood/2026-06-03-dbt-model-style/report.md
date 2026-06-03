# Dogfood report — dbt-model-style (external triangulation)

| field | value |
|---|---|
| Skill under test | `dev-workflow/skills/dbt-model-style` (merged via #374 — NOT authored this session) |
| Date | 2026-06-03 |
| Why this target | external triangulation — controls for the meta-dogfood familiarity bias of self-dogfooding |
| Passes run | Probe A (activation, injection-fallback) · Probe C (cold-reader) |
| Pass deferred | Probe B (executor + auditor) — would run dbt-model-style on a real `.sql` model + run `validate_header.py`; deferred |
| Fidelity | activation = `fidelity:approximate` (injection — nested `claude -p` auth unavailable) |
| Meta-validation | the dogfood-skill-testing skill (merged, dev-workflow 2.16.0) triggered + ran end-to-end in the live harness for the first time |

## Severity summary

| Critical | High | Medium | Low | Total |
|---|---|---|---|---|
| 0 | 1 | 3 | 2 | 6 |

## Triggering (Probe A) — clean
7/7 should-fire routed to dbt-model-style; 6/6 should-NOT-fire avoided it (no over-trigger, no
trigger-miss). The disclaimer "Do NOT use for calculation logic / metric formulas" is
**load-bearing** — it correctly keeps Q8 (AOV formula + NULL denominator) and Q9 (JOIN fan-out /
grain) OUT. **Watch-item (not a finding):** Q9 is medium-confidence — an aggressive router could
rationalize "still a dbt `.sql` model" and misfire; only the anti-trigger clause prevents it.

---

### FINDING-001: the two-block header rests on invisible, unverifiable project tooling
- severity: **High** · category: Cold-start / Progressive-disclosure · pass: cold-reader
- actual: §5's two-block header — the most novel, most-emphasized structural rule — exists *only*
  because "the first `/* */` reaches the table comment" via `persist_docs` + a sql→yml regex
  (L239). A cold user cannot tell whether that machinery is wired up in their project, cannot set
  it up from this doc, and `validate_header.py` checks the header's *shape* but never that the
  block actually *persists*. → maintaining a precise two-block + 3-site-comment-sync discipline on
  faith, payoff unobservable.
- why static review missed it: structure/lint checks the header FORMAT is present; they can't tell
  the format reaches anything.
- location: SKILL.md §5 / §5.1 (L235–278)
- suggested fix: add a "Prerequisites — is this wired up?" check at the top of §5 (e.g. confirm
  `persist_docs` in `dbt_project.yml`; after `dbt run`, verify with `\d+ <table>` or the
  redshift-comment MCP `get_table_comment`; if absent, §5 degrades to readability-only).

### FINDING-002: load-bearing jargon used undefined
- severity: **Medium** · category: Jargon-leak · pass: cold-reader
- actual: `MCP` (load-bearing — the whole header-discoverability argument rests on it; never
  expanded), `grain` (glossed only at L276, long after first use L34/L86), **"dotstar"** (the
  bundle file is `dotstar-passthrough.md` but the word never appears in SKILL.md — §2 calls it
  "`.*` passthrough", so a reader pointed at the file can't connect them), `FDW` / `persist_docs` /
  `BU` / `expt_` / `T+1` (in examples, unglossed), `(adapt)` used at L8/L19 before its L32 definition.
- location: SKILL.md §2, §5.1, frontmatter; `references/dotstar-passthrough.md` (filename)
- suggested fix: inline-gloss MCP + grain on first use; rename or cross-reference "dotstar" ↔ "`.*`
  passthrough"; move the `(adapt)` definition above first use.

### FINDING-003: the style-vs-calculation boundary has real, not just fuzzy, leakage
- severity: **Medium** · category: Convention-violation / Workflow-drift · pass: cold-reader
- actual: the in-scope/out-of-scope split is clean at the poles but real edits mix them: (a) "fix
  the COALESCE fallback direction AND clean up the `final` CTE" touches a business rule (out) and
  the zero-logic iron law (in) in the *same edit*; (b) the naming MUST — a `__paid` column "must
  not smuggle trial rows" (L181) — **requires reasoning about the computation to verify the name
  matches content**, so the style rule cannot be checked without crossing into the excluded
  calculation territory. This is an internal tension, not a fuzzy edge.
- why static review missed it: a scope sentence reads consistent in isolation; the conflict only
  shows when you simulate a real mixed edit.
- location: SKILL.md §Purpose (L23) vs §3 naming (L180–181) vs §1.2 final-CTE
- suggested fix: add a one-paragraph "when a request mixes style + logic" rule (do the style part,
  name the logic part as out-of-scope and hand back) + acknowledge the naming MUST needs a
  content check.

### FINDING-004: several rules are unactionable without a guess
- severity: **Medium** · category: Workflow-drift (underspecified) · pass: cold-reader
- actual: "inline `--` comments aligned" (L191) — aligned to *what* column? · "one concern per CTE"
  (L128) — "concern" undefined (is `DATE_TRUNC` + `CASE` one or two?) · the `(adapt)` variant-suffix
  MUST (L181) depends on a per-project suffix list that may not exist yet → a MUST gated on an
  undefined `(adapt)`.
- location: SKILL.md §1 (L128), §3 (L181), §4 (L191)
- suggested fix: name the alignment target; give a one-line test for "concern"; state the fallback
  when no `(adapt)` suffix vocabulary is defined.

### FINDING-005: `validate_header.py` doesn't state the working directory
- severity: **Low** · category: Workflow-drift · pass: cold-reader
- actual: §"After writing" explains when/how/what `validate_header.py` checks, but not *where to run
  it from* — a first-timer may `cd` wrong (skill dir vs project root).
- location: SKILL.md §After writing (L358–368)
- suggested fix: one line — "run from the dbt project root: `python <skill>/scripts/validate_header.py models/`".

### FINDING-006: SKILL.md narrative example ≠ the canonical example file
- severity: **Low** · category: Convention-violation (consistency) · pass: cold-reader
- actual: §5.1 shows the header narrative as **one line** (L259); `references/example-model.sql`
  splits the same narrative across **two lines** (L16–17). A literal-minded user copying the
  canonical example sees a different form than the rule's example.
- location: SKILL.md §5.1 vs `references/example-model.sql`
- suggested fix: make the two render identically (pick one form).

## Raw outputs appendix
- **Probe A transcript** (blind router, description-only, 5 distractors): 13/13 routed correctly;
  tally 7/7 fire + 6/6 avoid; load-bearing-disclaimer note on Q9 — agent `ab592bf6d26da0102`.
- **Probe C transcript** (blind cold-reader, full SKILL.md + bundle): 5-question adversarial read —
  agent `a59b81ffebd2c31fa`. Key line: "the two-block header's value proposition rests entirely on
  invisible, unverifiable project tooling — and there's no way to confirm it's working."

> Findings are **advisory** — they localize + point; the dbt-model-style author decides and applies.
> These are for a DIFFERENT skill (#374), surfaced here as external-triangulation evidence that
> dogfood-skill-testing finds real defects in skills it did not author.
