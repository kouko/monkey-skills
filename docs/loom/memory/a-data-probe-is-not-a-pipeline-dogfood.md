---
name: a-data-probe-is-not-a-pipeline-dogfood
description: A probe that samples the DATA answers "does the shape I need exist?" — it never answers "does the pipeline survive this input?". An 8-filer fact-level probe cleared every filer, and the first end-to-end run against one of them aborted the whole ingest. Run the real producers into the real consumer, per filer, before believing coverage; and run ALL the filers before concluding from the first two, in either direction.
type: practice
origin: company total (top-line) revenue arc (branch feat-total-revenue-lane, investing-toolkit 2.36.0, 2026-07-25) — the arc's only shipping blocker, and three more findings, came from the live run rather than from 1075 tests, 11 task-review triads, or 5 whole-branch reviews
---

The arc opened with a live 8-filer probe that answered its design question well:
does a flat top-line revenue fact exist in each filer's XBRL, and which concept
wins? It did. That evidence was captured into a committed fixture and every
later task tested against it.

Then the whole thing shipped green — 1075 tests, eleven per-task review triads,
five whole-branch review rounds — and the first genuine end-to-end run against
one of those same eight filers **aborted the entire ingest**: zero of 473 facts
landed. The probe had sampled the data; nothing had ever run the real producer
into the real consumer.

**Why the gap is structural, not an oversight.** A data probe answers a question
about the WORLD ("does this shape exist?"). A pipeline dogfood answers a
question about the CODE ("does every stage survive what the previous one
actually emits?"). The probe's own output becomes the fixture, so every
downstream test inherits exactly the slice the probe thought to look at — and
agreement between a fixture and the code that was written against it is not
evidence. The four defects this run surfaced were each invisible to that loop:

- an envelope key the producer never emitted and the consumer required, where
  both sides' tests hand-built the envelope;
- a collision guard keyed finer than its own consumer, firing on a legitimate pair;
- a filer whose tagging habit CHANGED mid-history, so one signature arrives two ways;
- a launcher whose dependency declaration omits what its own imports need.

None is a logic error. Each is a seam that no single component's tests can see.

**Filer-specific shapes make one success prove nothing.** Seven filers, run end
to end: five clean, two aborting for two DIFFERENT root causes. Had the run
stopped at the first two, the conclusion would have been "two of three fail —
this is broadly broken"; had it stopped at the five clean ones, "works
everywhere". Both wrong. The shapes that break are properties of individual
filers — a segment reporting eliminations alongside its operating view, a
concept tagged with inconsistent capitalization across two filings — so
coverage is a denominator question, not an existence question.

**How to apply:**
1. Treat "the probe found the data" and "the pipeline handles the data" as two
   separate claims needing two separate runs. A captured probe fixture is the
   right input for unit tests and the wrong evidence for coverage.
2. Before claiming a capability works, run the REAL producers into the REAL
   consumer, per case, and read what lands in the durable artifact — not the
   summary the driver prints. An exit 0 with an inflated count is a passing run.
3. Run the whole sample before concluding, in either direction. Stop early only
   when every remaining case would be redundant, and say why you believe that.
4. When the pipeline writes to an append-only store, this ordering is not
   optional: a defect found before real history accumulates costs a commit,
   after it costs a migration.
5. Verify the values that land against an independent oracle, and check the
   oracle's own filter first — a comparison that silently compares a quarter
   against a fiscal year reports a false alarm just as confidently as a real one.

Relates to [[a-test-can-pin-behaviour-with-a-false-rationale]] (both are cases
of evidence that looks conclusive because nobody asked what it excluded),
[[hand-authored-fixture-is-a-fabrication-risk]] and
[[fixtures-mirror-producer-shape]].
