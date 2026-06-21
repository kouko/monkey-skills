# Proposal — markdown frontmatter parser (spec-toolkit→code-toolkit E2E dogfood)

> **Seed (verbatim):** A small stdlib-only markdown frontmatter parser.
> `parse_frontmatter(text: str) -> tuple[dict[str, str], str]` — parse a leading
> `---` … `---` block of simple `key: value` lines into a dict, return the remaining
> body. No third-party deps (simple key:value, NOT full YAML).
> **Coverage statement:** coverage relative to seed + 6 lenses; single-object-failure
> regime (the critic's sweet spot); blind spots listed below. NOT complete.
>
> **Proportionality note (dogfood finding P-1):** this is a one-function pure utility.
> The full ceremony (OOUX multi-agent fan-out, L2 cross-object, L3 journey-nav) is
> mostly N/A here — the value is concentrated in Phase ③'s BVA + empty/error/state
> lenses. A "Lite" tier (skip ③b/③c, collapse OOUX) would fit. Recorded for the
> parked proportional-rigor tiering question.

— Phase ① USM backbone —

## USM backbone

**Single-surface collapse (v0.2.1):** a pure parse function has no sequential user
journey — one caller invokes one function. The backbone **collapses to ~1 node**.

Actors: **Caller** (a program passing text to parse) `seeded`.
Objects: **Document** (the raw input text) `seeded`; **Frontmatter block** (the
delimited `---`…`---` region) `seeded`; **Body** (text after the block) `seeded`;
**key-value pair** (one parsed entry) `inferred`.

Spine (1 node): `S1 — parse(text) → (metadata, body)`.

### Navigation graph (Phase ③c input)

Single-node; the only non-forward edge is `error_escape` (malformed input → raise).
No back/skip/resume edges exist for a synchronous pure function.

— Phase ② OOUX object model —

## OOUX object model

*(Single-surface utility — OOUX multi-agent fan-out collapsed to inline; only the
parse-outcome lifecycle is load-bearing. Dogfood finding P-1.)*

| Object | Provenance | State machine (outcome lifecycle) |
|---|---|---|
| **Document** | `seeded` | `raw → {has-frontmatter, no-frontmatter}` |
| **Frontmatter block** | `seeded` | `absent → opened → {closed (valid), unclosed (malformed)}`; `closed → {empty, non-empty}` |
| **key-value pair** | `inferred` | `line → {well-formed (has ':'), malformed (no ':')}`; on duplicate key → last-wins |
| **Body** | `seeded` | `= everything after the closing delimiter line` (verbatim, may be empty) |

— Phase ③ auto-expansion matrix —

## Path × edge matrix

Grid `parse × {Document, Frontmatter, key-value} × {valid, edge}` pruned through the
6 lenses. The parser is **BVA- and error-state-dominated** (no CRUD/permissions/NFR
surface to speak of — honestly marked):

| Lens (dominant) | KEEP (path) | FLAG (edge) | provenance |
|---|---|---|---|
| state-transition | text opens `---` and closes `---` → parse block | **opened but never closed → malformed → raise ValueError** | `inferred` (seed doesn't state error policy) |
| empty/error/loading | well-formed `key: value` lines → dict | **a frontmatter line with no `:` → malformed → raise ValueError** | `inferred` |
| empty/error/loading | — | **empty frontmatter (`---\n---\n`) → `({}, body)`** (valid, not error) | `inferred` |
| BVA | nominal multi-key block | **no frontmatter at all (text doesn't start with `---`) → `({}, text)`** | `seeded` |
| BVA | — | **empty string input `""` → `({}, "")`** | `inferred` |
| BVA | value parsed by first `:` | **value containing `:` (`url: http://x`) → split on FIRST colon → `{"url": "http://x"}`** | `inferred` |
| BVA | keys/values stripped | **leading/trailing whitespace on key or value → stripped** | `inferred` |
| BVA | — | **duplicate key → last value wins** | `inferred` (decision; flagged) |
| BVA | — | **blank line inside the frontmatter block → skipped, not an error** | `inferred` |
| state-transition | LF line endings | **CRLF (`\r\n`) line endings → handled the same as LF** | `inferred` |
| CRUD / permissions / NFR | — | **N/A** — pure synchronous function, single caller, no persistence/auth; large-input perf is a 🟢 non-obligation. Honestly marked, not padded. | — |

**Sparse-output honesty:** the matrix is genuinely BVA/error-heavy and that is correct
for a parser — not padded. No CRUD/permissions/NFR cells invented.

— Phase ③b cross-object combinations —

## Cross-object combinations

**Interaction-density gate applied → no interaction-dense stage.** A parser's reaction
to (Frontmatter-state × key-value-state) is the **union** of the per-object reactions
(an unclosed block raises regardless of key well-formedness; a malformed line raises
regardless of block size) — no joint reaction ≠ union of individuals. So ③b is
**N/A** here; the per-object grid (③) + the critic cover it. Not padded. (Dogfood
finding P-1: ③b correctly self-skips on a separable single-object feature.)

— Phase ③c journey navigation —

## Journey navigation

**Single-stage flow → no inter-stage navigation edges.** The only typed edge is
`error_escape` (malformed input → raise ValueError), already captured as a FLAG in the
matrix. No `back / skip / abandon / resume_reenter / retry_self` edges exist for a
synchronous pure function. ③c is structurally emitted but minimal — honest, not padded.

## Provenance

- `seeded`: the `---`…`---` delimiter model, `key: value` lines, the
  `(dict, body)` return shape, no-frontmatter→passthrough, stdlib-only.
- `inferred`: **error policy** (unclosed block → raise; malformed line → raise),
  empty-frontmatter→`({}, body)`, first-colon split, whitespace stripping,
  duplicate-key→last-wins, blank-line skipping, CRLF handling. These are design
  decisions the seed does not state — flagged below.
- `critic-found`: (completeness-critic 3-lens panel, 2026-06-13) **empty-key-after-strip
  → ValueError** (3-lens convergence: BVA + error + contract — the flagship catch the
  draft's "colon-less → raise" missed); **non-str input → TypeError**; **values stay
  strings, no YAML coercion** (`8080`/`true`/`[a,b]` all literal strings — the
  negative-space boundary); **fence-line exactness** (`---extra` on line 1 ≠ a fence →
  passthrough); **empty body when text ends at the closing fence**.

## Blind spots — needs human/field input

1. **Error vs silent-passthrough on malformed input** — the seed does not say whether
   an unclosed `---` block or a colon-less line should **raise** or be treated as
   plain body. This draft chose **raise ValueError** (fail-loud); a caller who wants
   lenient parsing would disagree. **Decision needed.** (Highest-impact unknown.)
2. **Duplicate-key policy** — last-wins is chosen; first-wins or raise-on-duplicate
   are equally defensible product decisions.
3. **Value typing** — this draft keeps all values as **strings** (stdlib, no YAML).
   Whether `true`/`42`/lists should coerce is a scope decision deferred to the seed's
   "NOT full YAML" constraint, but the boundary (does `key:` with empty value give
   `""` or is it malformed?) needs confirming — this draft gives `""`.

**Critic-found tail (un-re-seeded — ranked below the load-bearing set, per the v0.2.1
consolidation discipline; recorded here, NOT padded into the spec):**

4. **Error-message quality** — the draft raises a bare `ValueError`; an on-call reader
   wants the line number + offending content + reason. Worth pinning, but a message
   format is an implementation refinement, not a load-bearing acceptance criterion.
5. **Lenient-vs-raise refinement** — the contract critic proposed a sharper split:
   *degrade* (→ no-frontmatter) on a missing/unterminated fence, *raise* only on a
   fence-present-but-line-malformed. This draft uses the simpler uniform "raise on any
   malformation"; the split is a defensible alternative needing author sign-off.
6. **Leading BOM / leading blank line before the fence**, **pathological-input DoS
   guards**, **idempotence guarantee** (body never starts with a fence → safe re-parse),
   **returned-dict mutability**, **CRLF mixed mid-block** — all 🟢/🟡 clarifications;
   left as residue, not scenarios.
