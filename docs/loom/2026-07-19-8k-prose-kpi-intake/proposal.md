# Change: 8-K EX-99 prose KPI intake (Slice A — "Route B for prose")

Status: GENERATE draft (spec-expansion). Coverage relative to seed + 6 lenses;
blind spots listed below. **NOT a completeness claim.**

## Governance caveat (fail-loud)

**No product `PRINCIPLES.md` exists** for the investing product — this expansion
is **UNGOVERNED by a product constitution** (user chose PRINCIPLES option B on
2026-07-19). De-facto constraints applied instead: the shipped Route B trust model
(three-layer mechanical/LLM/human), the anti-fabrication rails in
`docs/loom/memory/falsy-guard-rejects-legitimate-zero-provenance.md` +
`match-kpi-on-full-dimensional-signature-not-one-axis.md`, and the byte-unchanged
`kpi_store.py`/`kpi_validate.py` Do-Not-Touch line. If product-level priorities
later conflict with this spec, the constitution wins — re-open then.

## Seed & scope

**Intent (seeded, user 2026-07-19):** extract a specific operational-KPI datum
stated in an 8-K EX-99 earnings-release PROSE sentence (non-table) — the
Family-DAP / MAU / deliveries class that Route B (tables only) and the narrative
layer (bulk text blob) both drop — with a **verbatim quote + character-offset
anchor**, through the existing three-layer trust intake into the unchanged
tier-① `kpi_store`.

**In scope (Slice A):** a NEW mechanical prose-scanning candidate producer that
plugs into the existing socket (input `exhibit_raw_{accession}_{document}`; output
`kpi_store.append` with per-point provenance). Value + quote + offset are
MECHANICAL, never LLM. LLM proposes semantic slots only. Human confirm-all commits.

**Out of scope (later slices / other owners):**
- Slice B — curated narrative *passages* to the memo (relevance/taste layer).
- Slice C — longitudinal coverage file, retention-years, tearsheet/tracker.
- Table KPI extraction (Route B `exhibit_tables.py` owns it — unchanged).
- Non-8-K sources (10-K MD&A, transcripts, decks).
- Memo rendering — unchanged; the existing quarterly feed reads the store as-is.

**Reuses (existing, from recon 2026-07-19):** Route B fetch + `exhibit_raw_` cache
(`sec_edgar_client.py:1718`); `kpi_8k_candidates.py` propose/commit three-layer
pattern; `kpi_store.append` provenance requirement; the earnings-8-K item-2.02
resolver (`sec_edgar_client.py:496-574`). New anchor shape only.

## USM backbone

*(— Phase ① USM backbone —)* Multi-stage producer pipeline (not single-surface):

| # | Stage | Actor | Object touched |
|---|---|---|---|
| 1 | Request prose intake for ticker/quarter | analyst | — |
| 2 | Resolve earnings 8-K (item 2.02) → EX-99, load raw HTML (reuse Route B; cached `exhibit_raw_`) | system | RawExhibit |
| 3 | MECHANICAL scan prose → candidate {value, verbatim_quote, char-offset span, sentence} | system (mechanical) | ProseKpiCandidate |
| 4 | LLM proposes {kpi_id, unit, period}; mark `needs_semantic` if unfilled | system (LLM) | ProseKpiCandidate |
| 5 | Human reviews candidates — confirm / edit / reject (confirm-all gate) | analyst | ProseKpiCandidate |
| 6 | Commit confirmed → `kpi_store.append` (byte-compatible, `source_kind="prose"` + quote/offset anchor) | system | KpiPoint |
| 7 | Downstream: existing quarterly memo feed reads store (no change) | system | — |

Navigation graph edges (input to Phase ③c): `forward` (1→7); `back` (reject at
5 → not committed); `skip` (no prose KPI found → honest empty); `abandon`
(≥2 exhibits → gap per Route B LOOM-SIMPLIFY ceiling; exhibit not cached);
`error_escape` (fetch/parse fail); `retry_self` (re-scan after cache fill).

## OOUX object model

*(— Phase ② OOUX object model —)* Inline expansion (grounded by 2026-07-19 recon;
adversarial recall delegated to completeness-critic). Three objects:

### RawExhibit (input)
- **Attributes:** accession, document, `disclosure_status` (filed|furnished),
  raw_html (`exhibit_raw_` cache), flattened text.
- **CTAs:** fetch (reuse Route B), scan_prose.
- **Relationships:** yields `ProseKpiCandidate[]`; sibling to Route B table candidates on the same exhibit.
- **State machine:** `not_cached → cached`; and `single_exhibit` vs
  `multi_exhibit(≥2) → GAP` (inherit Route B ceiling — do not silently pick one).

### ProseKpiCandidate (CORE)
- **Attributes (MECHANICAL):** value, verbatim_quote, char_offset_span[start,end],
  sentence_context, unit_hint (from quote caption/token), period_hint.
  **(LLM):** kpi_id, unit, period. **(derived):** `source_kind="prose"`,
  `needs_semantic`.
- **CTAs:** locate (mechanical), propose (LLM), confirm (human), reject, commit.
- **INVARIANT (load-bearing):** value AND verbatim_quote MUST be a verbatim
  substring of `RawExhibit.text` — else REJECT (anti-fabrication). Value/quote/
  offset are NEVER produced or altered by the LLM.
- **State machine:**
  `located → proposed → (needs_semantic ↺ | complete) → confirmed → committed`;
  terminal `rejected` reachable from any pre-commit state (non-substring, human
  reject, or "not an operational KPI").

### KpiPoint / StoreCommit (output)
- **Attributes:** existing `kpi_store` point shape + `source_kind="prose"` +
  anchor `source_cell_ref` analog = `"prose:{start}-{end}"` + `verbatim_quote`
  in provenance.
- **CTAs:** append (existing `kpi_store.append`, requires provenance).
- **Constraints:** `kpi_store.py`/`kpi_validate.py` BYTE-UNCHANGED; dedup vs a
  table-sourced point for the same {kpi_id, period, signature}.
- **State machine:** `pending → appended`; or `pending → deduped` (table wins).

## Path × edge matrix

*(— Phase ③ auto-expansion matrix —)* Grid `backbone × object × CTA × state`
pruned through lenses. Surviving high-value paths/edges:

**BVA lens (dominates — number-in-prose parsing is the crux):**
- KEEP: plain integer; decimal; **word-scale** ("3.56 billion" → 3,560,000,000);
  percentage ("+19%"); explicit range ("40,000–45,000" → capture both bounds or flag).
- FLAG (bug-prone): multiple numbers in one sentence (which is the KPI?);
  negative/parenthesised; unit-ambiguous token.
- **FLAG — false-positive class (biggest risk):** a number that is a **date/period
  label** ("Q1 2026", "fiscal 2025", "third quarter") or an ordinal — MUST NOT be
  emitted as a KPI value. Discrimination rule needed (blind spot).
- DROP: currency-prefixed `$` amounts in prose → out of scope (monetary; Route B /
  XBRL own financials) — skip, do not emit.

**empty/error lens (dominates — async fetch + possibly-absent data):**
- KEEP: no prose KPI found → **honest empty result** (skip), never fabricate.
- KEEP: fetch/parse failure → error escape, loud.
- KEEP: `furnished` (8-K EX-99) status carried on the point (not blocked).

**state-legality lens (dominates — rich lifecycle):**
- FLAG illegal: `located → committed` bypassing human confirm = FORBIDDEN.
- FLAG illegal: `propose` before `locate`; `commit` a `rejected` candidate.
- KEEP: `needs_semantic` self-loop until LLM/human fills slots.

**permissions lens (multiple actors):**
- KEEP: only the human `confirm`s and triggers `commit` (confirm-all gate).
- DROP: mechanical/LLM actor × commit — never reachable.

**anti-fabrication (NFR, load-bearing):**
- KEEP: substring-verification gate on {value, quote} vs source before propose/commit.
- FLAG: LLM returns a value not in source → REJECT + log (never coerce).

## Cross-object combinations

*(— Phase ③b cross-object combinations —)* One interaction-dense stage (Stage 3–6):
**ProseKpiCandidate × table-sourced Candidate (Route B)** co-active on the SAME
exhibit. Joint reaction ≠ union:

| Joint state | Required reaction (NOT the union) |
|---|---|
| Same {kpi_id, period, signature} in BOTH table and prose | **Dedup — table wins** (more structured); prose kept only as corroboration flag, not a second point (blind spot: confirm policy) |
| KPI in prose only (Family DAP) | Emit prose candidate (the target case) |
| KPI in table only | Route B handles; prose producer emits nothing |
| Conflicting values (table 3.55B vs prose 3.56B) | RAISE / flag for human — never auto-pick (mirrors dimensional-signature >1-value refusal) |

<3 co-active objects → inline enumeration; `pairwise.py` not required (wide-stage
ban is ≥4 objects only).

## Journey navigation

*(— Phase ③c journey navigation —)* 0-switch walk of the navigation graph (each typed edge once):
- `forward` 1→7: nominal producer flow.
- `back` (reject @5): candidate dropped, NOT committed, no store mutation; other candidates unaffected.
- `skip` (no prose KPI): emit empty result + honest "0 prose candidates" note; pipeline succeeds, memo feed unaffected.
- `abandon` (≥2 exhibits): emit GAP marker (Route B ceiling), extract nothing from that filing; loud, not silent.
- `error_escape` (fetch/parse fail): loud error, no partial commit.
- `retry_self` (re-scan after cache fill): idempotent — same input yields same candidates (no dup append; dedup on {kpi_id, period, anchor}).
- `resume_reenter` (analyst returns to a half-confirmed batch): confirm-all is all-or-nothing per batch; uncommitted candidates persist as `proposed`, none partially committed.

## Provenance

- `seeded`: intent + scope (user 2026-07-19); the two existing layers + the exact
  gap + the reused sockets (recon 2026-07-19, file:line in Seed & scope).
- `inferred`: the object state machines, the BVA/false-positive edge classes, the
  dedup joint-reaction table, the navigation reactions (OOUX/lens priors + recon).
- `critic-found` (completeness-critic 5-lens panel, 2026-07-19; lens count = convergence signal):
  - **Canonical text surface + anchor durability** (lens 1/3/4/5 — 4 lenses, sev 3, top rank): offsets+gate operate over one named canonical flattened text; gate checks the matched TOKEN not the normalized value; content-hash + flattener/edgartools version stored; re-verify quote==text[start:end] on read. → new Requirement + 4 scenarios.
  - **Consistent text normalization** (lens 1/4, sev 3): nbsp/entity/smart-quote/full-width digits. → new Requirement.
  - **Legitimate zero value** (lens 4, sev 3, repo-history-backed): → scenario on anti-fabrication gate.
  - **Human edit re-gates + per-field provenance** (lens 2/3, sev 3): → 2 scenarios on three-layer trust.
  - **Slice-A concurrency scope + batch atomicity** (lens 1/3/5, sev 3): honesty fix of the over-claimed "atomic all-or-nothing"/"idempotent" assertions → new Requirement.
  - **Resource bounds / ReDoS** (lens 1, sev 3): → new Requirement.
  - **Prompt injection** (lens 1, sev 2), **propose infra-failure ≠ needs_semantic** (lens 5, sev 2), **filing attribution + confirmer identity** (lens 2, sev 2/3): → new Requirements.
  - **Prose-vs-prose collision + order-independent dedup** (lens 4/5, sev 2), **bounding qualifiers** (lens 4, sev 2): → scenarios on dedup / number-semantics.

## Blind spots — needs human/field input

1. **Capture taxonomy (domain-convention, `evidence_needed`):** WHICH prose numbers
   count as trackable operational KPIs (DAU/MAU/subscribers/deliveries/units/…)?
   Slice-A default proposal: *no fixed taxonomy* — LLM proposes a `kpi_id` for any
   candidate, human confirm-all is the filter. A curated taxonomy is a later
   hardening. **Blocks nothing if the default is accepted; flag for user ratify.**
2. **Date/period false-positive discrimination:** the exact rule that stops "Q1
   2026" / "fiscal 2025" being emitted as a KPI value. Needs a concrete heuristic
   + RED tests (candidate: reject numbers inside a recognized period/date token or
   whose sentence role is temporal).
3. **Table-vs-prose dedup & conflict policy:** confirm "table wins; prose =
   corroboration; conflict → human raise." Needs user/domain ratify.
4. **Word-scale + range normalization:** canonical rule for "3.56 billion",
   "40,000–45,000" (emit both bounds? midpoint? flag range) — needs decision.
5. Retention / coverage-file / longitudinal (Slice C) — deferred, not this change.

### Decisions ratified (user 2026-07-19 — "全部照預設", all defaults)

- **#6 memo read-contract → RESOLVED by architecture** (code-checked): the memo
  feed reads `build_quarterly_series` output, NOT `kpi_store` (`kpi_memo_feed.py:13`,
  decoupled). Prose points land in `kpi_store` and are naturally absent from the
  memo — no filter needed. Slice B owns any prose→memo wiring. → new Requirement.
- **#7 8-K/A supersession → default A (minimal raise now)**; full policy → Slice C. → new Requirement.
- **#8 PII → default A (minimal token span + bounded context window)**. → new Requirement.
- **#9 separation of duties → same actor OK for Slice A** (single-analyst tool); revisit for multi-user.
- **#10 post-commit correction → deferred** (interim: manual store edit + git history).
- **#11 store-level uniqueness → deferred**; Slice A = single-process serial + app-layer guard (captured in the concurrency-scope Requirement).
- **capture taxonomy → open (no fixed taxonomy)**, human confirm-all is the filter; spec marks it `[deferred]`.

### critic-found blind spots — status after ratification

6. **8-K/A amendment supersession policy** (lens 2/3/5, sev 2-3): a restated prose
   point vs the original — Slice-A minimal proposal = RAISE on a same-period
   cross-accession conflict; full supersession/versioning policy aligns with the
   Slice C longitudinal store. **Needs user: minimal-raise now, or full policy now?**
7. **Memo-reader read contract** (lens 3, sev 2): does the EXISTING quarterly memo
   feed surface `source_kind="prose"` rows NOW (before Slice B)? Needs a code check
   of the feed's query + user intent — Slice A must not unintentionally surface
   prose in the memo before the Slice B curation layer exists. **Needs code-check + user.**
8. **PII / sensitive text in verbatim_quote / sentence_context** (lens 1, sev 2):
   a captured sentence can carry an exec name or comp figure. **Needs user/field:
   store full sentence vs minimal token span; any redaction?**
9. **Separation of duties** (lens 2, sev 1): may the same actor run intake AND
   confirm-all for Slice A, or is a distinct reviewer required? **Needs user ratify.**
10. **Post-commit correction / deletion governance** (lens 2, sev 2): the sanctioned
    route to retract/correct a confirmed-but-wrong point (actor + reason + no silent
    overwrite). **Needs user; defer candidate.**
11. **Store-level uniqueness backstop** (lens 5, sev 1): the byte-unchanged store
    enforces provenance, not uniqueness — every concurrency gap is unrecoverable at
    the data layer. **Design decision deferred** (external commit-serialization vs a
    store schema change that would violate byte-unchanged).
12. **Malformed / CSS-`display:table` HTML boundary** (lens 1/4, sev 2): the
    prose/table boundary under broken markup / `<div>`-styled tables — needs a
    concrete detection heuristic + RED tests (else table numbers leak into prose,
    defeating dedup). **Flag for implementer.**

### Named residue (sev-1, note-and-defer — NOT padded into requirements)

Spelled-out numbers ("three million"); empty/whitespace-only exhibit distinct from
"0 KPIs found"; ranges via "to"/"between"/"~" (vs en-dash); negative/parenthesised
+ footnote-marker digit discrimination; period genuinely absent → human entry;
`furnished` status flip on amendment; which EX-99.x is scanned; half-confirmed
batch durability across restart; anti-fabrication rejection-rate observability metric.

## Round summary — completeness-critic

- **Rounds run: 1** (5-lens panel; principles lens N/A — no PRINCIPLES.md). Gaps
  found: ~26 raw → consolidated ~20 (12 re-seeded, ~8 blind-spots + residue).
- **Overlap-rate judgment: LOW (~25–35%) — panel diverse enough**, no added lens
  needed. Convergence concentrated on 3 gaps (canonical-text-surface ×4 lenses;
  concurrency/atomicity ×3; supersession ×3; human-edit ×2) while each lens
  contributed a distinct unique class (lens1 text-integrity/resource/injection/PII;
  lens2 audit/legal/supersession; lens3 structural objects; lens4 number-format
  states; lens5 concurrency/durability). High per-finding convergence = rank
  confidence, NOT completeness.
- **Loop termination:** no re-seed opened a NEW defect CLASS (the classes are all
  covered by the 5 lenses); a 2nd round would re-find INSTANCES within covered
  classes at N-subagent cost. Terminated per the targeted-re-seed rule — this is a
  cost/class-coverage judgment, **NOT** a completeness claim.

Coverage statement: **coverage relative to seed + 5 lenses, 1 round; 12 open
blind spots + named residue. NOT complete.**
