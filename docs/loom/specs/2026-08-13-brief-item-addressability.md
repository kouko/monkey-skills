# Brief: make brief items addressable, and stop the coverage checker failing open

Date: 2026-08-13
Stage: brainstorming output → writing-plans input
Design-side on-ramp: no criteria row fired (increment to shipped loom-code
mechanisms; no UI surface, no new multi-state behavior) — no detour offered.
Axis 0 queue check: `## Now` now carries
`2026-08-13-requirement-identity-splits-between-birthplace-and-living-spec`,
which the user bet as the arc to run **immediately after this one**. It is the
follow-on to this arc's convention, not a competitor: this arc establishes the
hybrid-identity convention on the path every arc walks; that one repairs the
same convention's absence on the more durable, less-travelled path. One
adjacent OPEN entry (`2026-07-06-anti-copy-acceptance-greps-pass-paraphrase-copies`)
names `writing-plans/SKILL.md` in its start condition and does not strictly
fire here — carried in Open Questions.

**Supersedes the 2026-08-13 authoring-form brief** (same file, renamed; the
prior content is in git history at `ad579edd`). That brief proposed a worked
example for the brief schema plus a blinded panel measuring an
imperative/placement rule. Three research arms retired it: the
stability benefit of worked examples is uncited vendor assertion while the
measured literature shows examples ADD a variance axis (format/order/choice
swings of up to 76 accuracy points, 54%→93% on permutation alone); the
demonstration literature that would justify it is entirely closed-label
classification, never open-ended document generation; and the pattern we
called a hole — bracketed placeholder glosses — is what Anthropic's own skill
guide presents as the STRICT end of its template scale. What survived the
research is below, and it is a different thing.

## Problem

The plan cites the brief by **quoting its prose**. `plan-format.md:93-94`
defines referent kind (a) as a verbatim quote of brief text, and the plan
header carries only `Source brief: <path>` (`plan-format.md:31`). Nothing
joins a task back to a brief item mechanically — the crossing is lossy by
construction.

That matters because it is the one place in this design space where a
measurement exists. *Citation Discipline in Spec-Driven Development*
(arXiv 2606.30689 — pre-registered, 840 implementations, two frontier models)
compared per-line addressable citations against artifact-level traceability
and post-hoc trace maps: addressable citations enabled **86–88% automated
detection of implementations claiming a requirement they did not satisfy, at
0% false-positive rate; both alternatives scored 0%**. Our `Brief item
covered` is the artifact-level tier — the 0% one. The paper also measured a
**determinism cost (d≈−0.7)**, so this is a trade, not a free win.

Second, the checker that validates the *other* input path **fails open**.
`check_scenario_coverage.py` parses the field (`:67-68`), tries the
change-folder join-key grammar (`:72-75`), and **silently skips any value that
does not match** (`:135-137`), counting it as zero coverage. A malformed or
mistyped citation therefore reads as "this requirement has no task" rather
than "this citation is broken" — two very different repairs, one message.
This is the same failure shape as OpenSpec issue #1112, where a header that
did not exist in the base spec passed `validate --strict` and surfaced only at
archive, undetected for six days and recurring twice on one project.

The job: **give brief items an identity a task can cite and a script can
resolve, and make an unresolvable citation an error instead of a silence.**

## Users

- **`plan-document-reviewer`** — its Check 3 verifies the `Brief item covered`
  field is PRESENT. It cannot verify the referent resolves, because today
  there is nothing to resolve against. It currently passes plans whose
  citations point at nothing.
- **The whole-branch reviewers** — coverage checking is done by reading, by
  agents, at review time. That is the expensive path this arc makes cheaper.
- **kouko** — signs off the brief's scope, then reads a plan whose tasks claim
  to cover it. Works in 繁體中文 / 日本語 / English.

Job story: *when I approve a brief and later read the plan, I want to know
mechanically that every item I approved has a task and every task traces to
something I approved, so that a dropped item surfaces before implementation
rather than in review.*

## Smallest End State

Items 1, 5 and 6 below were rewritten after the pre-ship experiment recorded
in §Experiment; each names the finding that forced it.

1. **Brief items carry hybrid identity** — an immutable short ID plus the
   human-readable text. The ID is what resolves; the text is what a reader
   reads. **Scope: every brief section that declares an outcome a task could
   deliver** — not only `## Smallest End State`. The experiment measured 5 of
   9 real tasks citing outcomes declared OUTSIDE that section (four in
   `## What Becomes Obsolete`, one against `## Decision` as an umbrella), so
   an ID scheme confined to Smallest End State would leave the majority of
   tasks with nothing honest to cite. Form and prefix stay an Open Question;
   the *hybrid* and the *scope* are decided.
2. **`Brief item covered` accepts the ID as a third referent form.** It must
   ride INSIDE the existing field — `test_traceability_generalization.py:62-70`
   asserts `plan-format.md` contains no second traceability field name, by
   design. The prose-quote form stays accepted (briefs authored before this
   change have no IDs).
3. **The coverage checker gains a brief mode** — every task cites a referent
   that resolves against the brief's declared IDs, and every declared ID is
   covered. This mirrors what the change-folder path already gets, on the path
   every arc actually uses.
   > **Shipped narrower than this sentence reads — annotation added at
   > close-out, original wording left intact.** The two halves ship with
   > different force. An unresolvable citation is an ERROR (exit 1). An id that
   > no task cites is **reported, not gated** — it is named in a warning and the
   > run still exits 0. So "every declared ID is covered" is an outcome this
   > mode makes *visible*, not one it *enforces*. The ruling and its reasoning
   > are in the plan's Decision Log under Task 6 (report-vs-gate); this note
   > exists because a later arc will read this item as the convention's origin
   > and would otherwise inherit the stronger reading.
4. **The fail-open closes.** A `Brief item covered` value matching no known
   referent grammar is an ERROR naming the malformed value, never a silent
   zero-coverage contribution. This fix applies to the existing change-folder
   path too — the defect is in shared code.
5. **A legal no-requirement value: `none — <reason>`, reason mandatory.**
   Some tasks deliver no brief outcome at all: the experiment's T9 was version
   bump + CHANGELOG + mirror sync, and all three independent probes called it
   unmappable without being offered that option. Without a legal escape the
   checker forces a false citation, which is worse than no citation because it
   looks satisfied. The mandatory reason is what stops it becoming a silent
   opt-out — an empty or generic reason is a checker error like any other.
6. **Coverage is directional both ways.** A task may cover several items and
   an item may need several tasks: the experiment found SES-1 ("`--lang` on
   **both** scripts") delivered half by one task and half by another, with
   neither alone satisfying it. The checker must therefore treat an item as
   covered by the UNION of citing tasks, and must not assume one citation
   discharges an item.
7. **A written tie-break rule for the primary referent.** All three probes
   independently flagged the same task as tied between two items, for the same
   reason (its description centres one item, its RED test the other) — a
   convergent, rule-able seam rather than noise. The rule is stated in
   `plan-format.md` so authors do not re-litigate it per plan.

## Current State Evidence

- **Forward** (what fires today): `plan-format.md:93-94` defines the
  quote-referent; `:95-99` defines the change-folder join key
  `<change-id> / Requirement: <name> / Scenario: <name>`; `:31` carries only
  the brief's path. `plan_card.py:423` reads the field as an opaque string for
  the card's `why` line and is tolerant of any form.
- **Reverse** (who owns the identity): nobody. The brief schema
  (`handoff-brief-format.md`) declares no item identifiers at all; its
  `## Alternatives Considered` (`:86`) and `## Open Questions` (`:96`) are
  numbered lists whose numbers are never declared addressable. By contrast the
  living spec owns `REQ-N` (`living_spec_index.py:14-20`) and the change-folder
  owns prose requirement names (`validate_spec_output.py:46-47`).
- **Error** (today's failure mode, verified): `check_scenario_coverage.py`
  silently skips a non-matching referent (`:135-137`). Separately at
  `:104-112` it records that duplicate change-folder requirement names cannot
  be disambiguated because "the join-key grammar is fixed… occurrence indices
  can't be added" — it warns and continues. And at `:148` the change-id is
  inferred from the directory name rather than declared in the spec file: an
  undeclared implicit identifier.
- **Data**: no schema field is added or removed. Item 1 adds identity to text
  that already exists; item 2 widens an accepted value grammar; items 3-4
  change script behavior. `plan_card.py` needs no change (opaque read).
- **Boundary**: `test_traceability_generalization.py:62-70` forbids a sibling
  traceability field — the constraint that keeps this change small.
  `test_check_scenario_coverage.py:102` pins the prose-referent case as
  contributing zero keys; an identifier-shaped brief referent must not collide
  with that expectation. `check-living-spec-index.py` and
  `check_doc_citations.py` are untouched (neither reads briefs).

Evidence paths appendix:
loom-code/skills/writing-plans/references/plan-format.md;
loom-code/skills/brainstorming/references/handoff-brief-format.md;
loom-code/scripts/check_scenario_coverage.py;
loom-code/scripts/test_traceability_generalization.py;
loom-code/scripts/test_check_scenario_coverage.py;
loom-code/scripts/plan_card.py; loom-code/scripts/living_spec_index.py;
loom-spec/scripts/validate_spec_output.py.

## Alternatives Considered (research-grounded)

Four arms ran across this design space: a defect classification over this
repo's own corpora, a bilingual literature sweep on instruction form, a survey
of shipped spec→plan formats, and an identifier-design study. Sources are
labelled by language.

| Option | What it means | Evidence |
|---|---|---|
| **Pure names** (OpenSpec-shaped: `### Requirement: <name>`, matched by normalized header text) | What loom's change-folder path already does | **Rejected.** OpenSpec issue #1112 is this exact design failing open: a header absent from the base spec passes `validate --strict`, surfacing only at archive — undetected six days, twice on one project. Supporting names also required a dedicated `RENAMED` verb with FROM/TO, a normalization rule, a duplicate-header error class, and an archive algorithm applying renames first — and the hole shipped anyway. loom already pays part of this bill (`check_scenario_coverage.py:104-112`). |
| **Pure numbers** (`REQ-4`, `FR-003`) | What Kiro, spec-kit and cc-sdd ship; what loom's living spec uses | **Rejected as the whole answer.** A bare token is not a link, so no off-the-shelf tool resolves it — you write the validator yourself (loom already did, for `REQ-N`). Numbers do buy one thing names cannot: a dense ordinal sequence makes OMISSION arithmetically detectable, whereas deleting a named heading leaves no hole. Insertion/renumbering is the documented cost (ISO requires dated clause references "because these elements are sometimes renumbered"; CVE's widening pushed migration onto every downstream consumer). |
| **Hybrid — immutable ID + human name (CHOSEN)** | The ID resolves; the name is read | Every long-lived system surveyed converges here: DOI + title ("no definitive information can be inferred about a referent from a DOI name alone"), MediaWiki `page_id` "preserved across edits and renames" + title, git SHA + ref, Jira internal id + display key. spec-kit states it outright: "Use the explicit FR-/SC- identifier as the primary key when present, and optionally also derive an imperative-phrase slug for readability." **The in-repo proof is loom's own plan layer** — `## Task 3 — <short name>` with a `T3` ledger key, already hybrid, already working. Documented hole to respect: hybrids fail when the two halves desync (Jira keeps stale key aliases resolving after a rename). |
| **Worked example + authoring-rule panel** (the superseded brief) | Add a filled example to the brief schema; measure an imperative/placement rule | **Rejected on research** — see the supersession note above. |
| **Do nothing** | Keep quoting prose | Leaves the measured 0%-detection tier in place on the path every arc uses, and leaves a fail-open in shared code we have already located. |

**What the literature does NOT support, stated so nobody re-imports it**: no
one has measured whether an LLM cites a numeric ID more reliably than a slug
(fifth unmeasured axis found this session). No one has measured LLM
implementer correctness from a controlled notation (EARS, Gherkin) versus
well-written prose — EARS's own strongest study (N=10, no prose control)
found practitioners applied it *inconsistently*, i.e. the notation relocated
the judgment into template selection rather than removing it. Structure is not
monotonically good for LLM inputs: requiring JSON output **doubled**
misalignment in one measurement (0.96% vs 0.42%), and removing prompt detail
sometimes *improved* code correctness.

**My take:** ship the hybrid on the brief→plan crossing and close the
fail-open. Conditional reversal: if authoring IDs turns out to require the
same judgment EARS relocated — if the recurring question becomes "is this one
item or two?" rather than "what is this item's ID" — then the ID scheme is
carrying complexity without buying resolution, and the honest response is to
stop at the fail-open fix and record the attempt.

Sources (EN): [Citation Discipline in SDD, arXiv 2606.30689](https://arxiv.org/abs/2606.30689);
[OpenSpec issue #1112](https://github.com/Fission-AI/OpenSpec/issues/1112);
[spec-kit analyze.md](https://github.com/github/spec-kit/blob/main/templates/commands/analyze.md);
[DOI Handbook 2025](https://www.doi.org/doi-handbook/DOIHandbook_2025.pdf);
[MediaWiki Manual:Page table](https://www.mediawiki.org/wiki/Manual:Page_table);
[CVE ID syntax change](https://web.archive.org/web/20250603135137/https://cve.mitre.org/cve/identifiers/syntaxchange.html);
[EARS experiment, ICSTW 2023](https://www.ipr.mdu.se/pdf_publications/6673.pdf);
[When Prompt Under-Specification Improves Code Correctness, arXiv 2604.24712](https://arxiv.org/abs/2604.24712);
[The Devil in the Details, arXiv 2511.20104](https://arxiv.org/abs/2511.20104).
Sources (JA-origin): [WordPress 日本語スラッグを連番化](https://qiita.com/takumi-19/items/abebcca91081faf71fcb)
(Japanese-text slugs percent-encode into unreadable identifiers; the shipped
workaround is a numeric fallback — direct evidence on names in a non-English
authoring language).

## Decision

Give brief items hybrid identity (immutable short ID + human-readable text) in
**every section that declares an outcome a task could deliver** — the scope
corrected by the experiment, which found 5 of 9 real tasks citing outcomes
declared outside `## Smallest End State`; widen `Brief item covered` to accept
that ID as a third referent form inside the existing field; extend the coverage
checker with a brief mode; and make an unresolvable referent an error rather
than a silent zero-coverage contribution.

Do NOT build: a sibling traceability field; a controlled notation (EARS,
Gherkin) for acceptance criteria; identifiers for product principles or
interface-design screens; a worked example for the brief schema; any authoring
rule about mood, placement, word choice, or register; the change-folder →
living-spec join (that is the COMMITTED-NEXT arc, deliberately sequenced
after this one).

## Out of Scope

- The `REQ-N` ↔ change-folder-name split (the next arc, already bet)
- The memory store's two undocumented cross-reference vocabularies
  (`[[slug]]` alongside markdown links, with no schema defining `[[`)
- The undeclared implicit change-id inferred from directory name
  (`check_scenario_coverage.py:148`)
- Automating hallucination detection end-to-end — this arc buys the
  addressability that would make it possible, not the detection itself
- Identifiers for product principles or interface-design screens (both
  currently have none)

## What Becomes Obsolete

Honestly: almost nothing, and the reason is a cost worth naming rather than
hiding. The prose-quote referent CANNOT be retired — every brief authored
before this change lacks IDs, so the checker must keep accepting quotes
indefinitely. That leaves a permanent two-form referent surface, which is
exactly the "one concept, two vocabularies" shape this repo keeps finding
defects in. The mitigation is that both forms live in one field with one
grammar list and one error path; the risk is that the quote form becomes a
silent downgrade an author can always fall back to.

## Experiment — run before planning, results binding

Two pre-registered probes ran against a real shipped brief/plan pair
(`docs/loom/specs/2026-08-12-adjudication-view-japanese.md` and its 9-task
plan), chosen because ground truth exists: that plan's `Brief item covered`
values were authored by a human at the time, so accuracy is checkable and not
only self-consistency.

**Probe 1 — can independent readers derive the same partition?** Criterion
registered in advance: differing item COUNTS = hard fail. Result: three
independent agents produced **6, 6, 7** — a hard fail as registered, and all
three located the SAME seam (whether tuple-valued modality is its own
deliverable), with two cutting it one way and one the other. Two also found
further defensible cuts yielding 8 or 9.

**The criterion was then judged mis-specified, and this is recorded rather
than quietly repaired.** The workflow never asks two authors to derive the
same partition: the brief author partitions ONCE, and downstream agents cite
existing IDs. Probe 1 measured partition-derivation; the design requires
partition-matching. Changing a criterion after seeing a failure is exactly
what invalidates pre-registration, so probe 1's failure stands on the record
and probe 2 was registered afresh before running.

**Probe 2 — given a FIXED partition, is task→ID assignment determinate?**
Criteria registered in advance: 9/9 unanimous PRIMARY = pass; 7-8/9 = marginal,
proceed ONLY if disagreements are convergent and rule-able; ≤6/9 = fail.
Result: **8/9 unanimous**, with the single disagreement flagged as TIED by all
three probes for an identical reason — convergent and rule-able, so the
marginal-pass condition held as written.

Findings that changed the design (each confirmed by ≥2 independent sources):
scope (5 of 9 tasks cite outcomes outside `## Smallest End State`);
unmappable-by-design tasks (all three probes independently called the release
task unmappable); bidirectional coverage (one item split across two tasks).
These became Smallest End State items 1, 5, 6 and 7.

**Method limitation, disclosed by the probes themselves:** all three read the
plan whole-file, so its existing `Brief item covered` values entered their
context. Each said so unprompted. The contamination is bounded by their
outputs diverging from those values on exactly the tasks where ground truth
differs (they called the release task unmappable and forced the four pointer
tasks onto an item the author had not used), which is evidence the leaked
field did not drive the answers. A future run of this shape should extract
task blocks with `sed` rather than reading the file whole.

## Open Questions

1. **The ID scheme's form** — prefix, and whether it is hierarchical (the
   measured citation study used `REQ-XXX.Y.Z`). Resolve at plan time. The
   scope question that sat here is RESOLVED by the experiment (Smallest End
   State item 1).
2. **How the checker distinguishes a legacy brief from an ID-bearing one.**
   A brief with zero declared IDs must not fail every task's citation; a brief
   WITH IDs should probably require them. The transition rule is a plan-time
   decision with a real fail-open risk of its own.
3. **Whether the ID is authored or derived.** A derived ID (slugified heading)
   desyncs on rename — the documented hybrid hole. An authored ID is one more
   thing to get right. Resolve at plan time.
4. **What the tie-break rule actually says.** The experiment proves the seam
   is convergent; it does not say which side wins. Two candidates: the item
   the RED test asserts, or the item the bulk of `Files touched` serves.
   Resolve at plan time and write it into `plan-format.md`.
5. The adjacent OPEN backlog entry
   `2026-07-06-anti-copy-acceptance-greps-pass-paraphrase-copies` names
   `writing-plans/SKILL.md` in its start condition; this arc edits
   `plan-format.md` and `check_scenario_coverage.py`. If plan work requires a
   SKILL.md mirror edit, the condition fires and the entry rides along.
