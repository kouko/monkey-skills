---
name: 2026-07-25-investing-toolkit-source-kind-naming-debt-endpoint-name-axis-vs-shape-ax
description: investing-toolkit `source_kind` naming debt — endpoint-name axis vs shape axis
status: open
origin: company total (top-line) revenue lane arc (branch feat-total-revenue-lane, 2026-07-25); plan `docs/loom/plans/2026-07-25-company-total-revenue.md` §Notes "Known naming debt, deliberately NOT fixed in this arc" + Task 11's RFC 6648 / BCP 178 evaluation (uniform "ours" prefixes carry zero discriminating information and must be renamed once a value becomes de facto standard — exactly the situation a durable-store rename creates).
start: the next rename/migration touch of a `source_kind` stored value — NOT a plain next-touch of the two named files, since either rename is a durable-store migration (existing points already carry the value), not a code edit.
---

- Start: the next rename/migration touch of a `source_kind` stored value —
  NOT a plain next-touch of the two named files, since either rename is a
  durable-store migration (existing points already carry the value), not a
  code edit.
- Origin: company total (top-line) revenue lane arc (branch
  feat-total-revenue-lane, 2026-07-25); plan
  `docs/loom/plans/2026-07-25-company-total-revenue.md` §Notes "Known naming
  debt, deliberately NOT fixed in this arc" + Task 11's RFC 6648 / BCP 178
  evaluation (uniform "ours" prefixes carry zero discriminating information
  and must be renamed once a value becomes de facto standard — exactly the
  situation a durable-store rename creates).
- What: this arc pinned the `source_kind` vocabulary shape mechanically
  (`kpi_gate.TRUSTED_SOURCE_KINDS` now asserts every trusted member starts
  with the trust-class segment `xbrl-`), but two pre-existing values already
  violate the `<trust-class>-<lane>` shape and were deliberately left unfixed:
  (a) 🟢 `xbrl-companyfacts` names a specific SEC REST endpoint
  (`data.sec.gov/api/xbrl/companyconcept/...`), yet
  `kpi_tw_ingest.py:54` reuses the identical literal for TW MOPS iXBRL
  ingestion, where no such endpoint exists at all — its second segment mixes
  an endpoint-name axis with the shape axis the other trusted values
  (`xbrl-dimensional`, `xbrl-topline`) use.
  (b) 🟢 `kpi_prose_candidates.py:433,697` mints a bare `"prose"` value with
  no trust-class segment at all. It sits OUTSIDE `TRUSTED_SOURCE_KINDS` (an
  untrusted lane), so this arc's convention-pin test does not touch it, but
  it is the same naming inconsistency one axis over.
  Both are cheap to rename in code but expensive to rename live — either
  change requires a durable-store migration (backfill already-stored points
  under the old literal) rather than an edit, which is why this arc shipped
  them as documented debt instead of silent drift. Revisit when a
  TW-specific or prose-specific trust class is introduced (the natural
  rename point) or when a store migration is separately budgeted.
