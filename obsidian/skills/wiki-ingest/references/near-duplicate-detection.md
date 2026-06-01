# Near-Duplicate Detection Method

Shared detection method for finding two wiki pages that describe the **same real-world entity** under different filenames (e.g. `Thompson-Sampling` and `Thompson-Sampling-MAB`). Exact-slug equality already catches identical names; this method catches the *near*-duplicate gap that exact matching misses.

This is a **prose method the executing LLM follows**, not a function library — same instruction style as [lint-checks.md](../../wiki-lint/references/lint-checks.md) L07 ("Levenshtein distance ≤2") and L12 (inline heuristic). There is no scoring engine, no pytest, no compiled code path.

**Two consumers share this method** (both wired by this change — neither exists yet; the wiring lands in sibling edits on this branch). See [§Consumer usage](#consumer-usage):
- `wiki-ingest` STEP 4c (the Filename uniqueness check block) — **prevent-new**: compare ONE incoming/just-written page against existing pages; prompt only on HIGH.
- `wiki-lint` L15 — **sweep-existing**: all-pairs scan over existing pages; report as warning with confidence.

The method has three stages — **Normalization → Blocking → LLM-as-judge confirm** — applied in order.

> [!important] obsidian-native — no ML infrastructure
> Detection is **string-similarity + the executing LLM's own judgment only**. NO embeddings, NO vector DB, NO external ML model, NO similarity-scoring service. This is consistent with how [wiki-cross-linker](../../wiki-cross-linker/SKILL.md) already works (conservative string matching). obsidian has no such infra and adding it would break determinism; see [§obsidian-native note](#obsidian-native-note).

## Stage 1 — Normalization

Before comparing two page identities, normalize each one to a canonical comparison key. Apply these rules **in order** to the page's `title`, each `aliases` entry, and the filename slug:

1. **Lowercase** everything (`Thompson-Sampling` → `thompson-sampling`).
2. **Replace hyphens and underscores with single spaces** (`thompson-sampling` → `thompson sampling`).
3. **Collapse runs of whitespace** to a single space, then **trim** leading/trailing space.
4. **Drop trailing qualifier tokens** — domain-suffix acronyms or category words appended to disambiguate. Strip a trailing token when it is one of:
   - A short all-caps acronym in the original slug (e.g. `-MAB`, `-LLM`, `-RAG`, `-API`).
   - A generic category word: `algorithm`, `algorithms`, `method`, `methods`, `model`, `models`, `concept`, `framework`, `approach`, `technique`, `entity`, `company`, `inc`, `corp`, `ltd`.
   - A repository disambiguation qualifier of the `name-qualifier` form documented in [page-format.md §Filename rules](page-format.md) (e.g. `qlib-microsoft` vs `qlib-language` — strip the qualifier only when comparing for same-entity candidacy; keep it for display).

   Strip only **trailing** qualifiers, and strip at most the run of trailing qualifier tokens (do not strip an interior word that happens to match the list).

**Worked examples**:

| Original slug / title | Normalized comparison key |
|---|---|
| `Thompson-Sampling-MAB` | `thompson sampling` |
| `thompson_sampling` | `thompson sampling` |
| `qlib-Microsoft` | `qlib` |
| `Alpha-Factor-Model` | `alpha factor` |
| `Magnificent-Seven` | `magnificent seven` (no qualifier to strip) |

Normalization is a **candidate-surfacing aid only** — it deliberately over-collapses (e.g. it would also collapse `transformer-model` and `transformer-architecture` toward `transformer`). Over-collapsing is acceptable here because Stage 3 (the LLM judge) is the authority on same-vs-different; Stage 1+2 only decide what gets *looked at*.

## Stage 2 — Blocking (candidate generation)

**Goal**: cheaply surface a small set of candidate pairs worth the LLM's attention, **without** running an O(n²) LLM comparison over every page pair.

For each pair of pages, compute string similarity between their normalized keys (from Stage 1) across `title`, each `aliases` entry, and slug. Use two complementary string metrics — the executing LLM computes these as a prose instruction, the same way L07 instructs "Levenshtein distance ≤2":

- **Levenshtein (edit distance)** — catches typos, plural/singular, minor spelling drift.
- **Jaro-Winkler (0–1 similarity, prefix-weighted)** — catches shared-prefix names where one is a longer variant of the other (`thompson sampling` vs `thompson sampling bandit`).

**Surfacing threshold** — surface a pair as a candidate when **any** of the following holds on the best-matching field pair (title↔title, title↔alias, alias↔alias, or slug↔slug):

| Signal | Surface as candidate when |
|---|---|
| Normalized keys equal | exact match after Stage 1 → **always surface** (highest-priority candidate) |
| Levenshtein on normalized keys | distance **≤2** (mirrors L07's broken-link suggestion threshold) |
| Jaro-Winkler on normalized keys | similarity **≥0.92** |
| Substring / prefix containment | one normalized key is a whole-word prefix of the other (e.g. `thompson sampling` ⊂ `thompson sampling mab`) |

Pairs that clear **none** of these are NOT surfaced — they never reach the LLM judge. This is the cost-control step: blocking keeps the LLM-as-judge calls to the handful of genuinely-similar pairs.

**Cross-field matching**: an incoming page's `title` may match an existing page's `aliases` entry (the alias was minted from a prior merge or cross-language slug per [page-format.md §Field rules](page-format.md)). Always include `aliases` on **both** sides of the comparison, not just `title`.

## Stage 3 — LLM-as-judge confirm

Blocking surfaces *lexically* similar pairs; lexical similarity is necessary but not sufficient (`John-Doe` the person vs `Doe-Corp` the company can be lexically close yet distinct entities). For **each** surfaced candidate pair, the executing LLM makes the same-entity decision by reading content, not strings.

**Inputs the judge reads** — for both pages:
- `title` (from frontmatter)
- `## Summary` body section
- `## Key Facts` body section

(These are the highest-signal, bounded sections per [page-format.md §Body Structure](page-format.md); the judge does NOT need to read full bodies, `## Connections`, or `## Sources`.)

**Output the judge returns** — per candidate pair:

1. **Verdict** — `same` or `different` (is this the same real-world entity?).
2. **One-line reason** — the deciding evidence, e.g. *"both describe the Bayesian MAB algorithm; aliases and Key Facts overlap on Beta-posterior sampling"* or *"`John-Doe` is a person, `Doe-Corp` is the company he founded — distinct entities"*.
3. **Self-reported confidence** — `HIGH` / `MID` / `LOW`:

| Confidence | Meaning | Disposition |
|---|---|---|
| **HIGH** | Clearly the **same** real-world entity — titles/aliases and `## Key Facts` corroborate; no contradicting facts. | Strong duplicate signal — drives the ingest prompt (see consumer usage). |
| **MID** | **Plausibly** the same, but evidence is thin or partially conflicting — needs human eyes to confirm. | Surface for human review; never auto-act. |
| **LOW** | **Probably distinct** — lexically close but content diverges (different entity class, contradictory key facts, coincidental name overlap). | Treat as different; do not prompt/merge. |

Confidence is the judge's **self-report**, not a computed score — there is no calibration model behind it, consistent with the no-ML constraint. When unsure between two tiers, the judge picks the **lower** tier (bias toward not over-merging, mirroring the brief's "human gates whether to merge, to block over-merge").

## Consumer usage

The same three stages run for both consumers; only the **comparison frame** and **disposition** differ.

**Consumers (both added by this change):** the wiki-ingest STEP 4c hook and the wiki-lint L15 check are introduced by sibling edits on this branch — they are not pre-existing call sites. The frames below describe how each newly-wired consumer invokes this method.

| Consumer | Frame | Disposition |
|---|---|---|
| **wiki-ingest STEP 4c** (prevent-new) | Compare the **one** incoming / just-written page against existing pages (1×N, not all-pairs). | Prompt the user **only on HIGH** — *"near-duplicate of [[existing-page]], merge with `/wiki-merge`?"*. Stays as conservative as STEP 4c's existing "only ask on multi/no-match" discipline; MID/LOW do not interrupt ingest. |
| **wiki-lint L15** (sweep-existing) | All-pairs sweep over existing wiki pages (read-only audit). | Report each `same`-verdict pair as a **warning**, annotated with the confidence tier (HIGH / MID), so the user can batch-review and trigger `/wiki-merge` per pair. Read-only — never auto-merges. |

## obsidian-native note

This method uses **only** obsidian-native primitives:

- **String similarity** (Levenshtein + Jaro-Winkler on normalized markdown frontmatter / slugs) for blocking.
- **The executing LLM's own judgment** (reading `## Summary` + `## Key Facts`) for the same-entity decision.

Explicitly **NOT** used, and why:

- ❌ **No embeddings / no vector database** — obsidian has no embedding infra; introducing one would be a new heavyweight dependency for a single-user vault.
- ❌ **No external ML model / no similarity-scoring service** — confidence is the LLM's self-report, not a calibrated classifier output.
- ❌ **No nondeterministic similarity ranking** — string metrics are deterministic and inspectable; the only judgment call is the LLM's, which is exactly where same-vs-different ambiguity belongs.

This matches [wiki-cross-linker](../../wiki-cross-linker/SKILL.md)'s existing **conservative string-matching** posture (whole-word match, case-sensitive primary, skip-ambiguous). Embedding-based blocking is explicitly deferred as a future enhancement, out of scope for this version.
