---
name: 2026-08-13-requirement-identity-splits-between-birthplace-and-living-spec
description: a requirement is born in a change-folder as a prose NAME and lives forever in the living spec as REQ-N, with nothing joining the two — one concept, two vocabularies, across the longest-lived identifier in the repo
status: COMMITTED-NEXT
origin: 2026-08-13 identifier-design recon for the brief-addressability arc — the inventory of every identifier in the loom pipeline surfaced this split as an existing defect rather than as a design choice anyone made
start: user bet it at the 2026-08-13 close-out — run immediately after the brief-item addressability arc ships
---

- Start: user bet it at the 2026-08-13 close-out — run immediately after
  the brief-item addressability arc ships

- Origin: 2026-08-13 identifier-design recon for the brief-addressability
  arc — the inventory of every identifier in the loom pipeline surfaced
  this split as an existing defect rather than as a design choice anyone
  made

- **The defect**: `loom-spec`'s change-folder names a requirement in prose
  (`### Requirement: <name>`, enforced at
  `loom-spec/scripts/validate_spec_output.py:46-47`). The living spec
  gives the same concept a numeric identity
  (`### Requirement: REQ-N [active|deferred]`,
  `loom-code/scripts/living_spec_index.py:14-20`), and code tags join
  against THAT (`# @req: REQ-1`, `living_spec_tags.py:39`; a dangling id
  fails rc=1). Nothing maps a birth name to its REQ-N. `REQ-N` is the
  longest-lived, most cross-arc identifier in the repo — and the one
  place its subject was first written down uses a different vocabulary.

- **Why it is worth an arc rather than a note**: this is the exact defect
  class the 2026-08-12 arcs kept finding (one concept, two vocabularies,
  no join). It also blocks the useful half of the citation research — the
  measured 86–88% automated hallucination detection needs a citation that
  resolves end to end, and today the chain breaks at the change-folder →
  living-spec seam.

- **The convention to apply, decided 2026-08-13**: hybrid — an immutable
  short ID carries identity, a human-readable name carries meaning.
  Evidence: every long-lived system surveyed converges there (DOI+title,
  MediaWiki `page_id`+title, git SHA+ref, Jira id+key); spec-kit states it
  outright ("use the explicit FR-/SC- identifier as the primary key when
  present, and optionally also derive an imperative-phrase slug for
  readability"); and loom's own plan layer already IS a hybrid
  (`## Task 3 — <short name>` with a `T3` ledger key), which is the
  in-repo proof the shape works.

- **What the pure-name design costs, measured elsewhere**: OpenSpec
  (github.com/Fission-AI/OpenSpec issue #1112) addresses requirements by
  exact normalized header text — the same shape as our change-folder — and
  a header that does not exist in the base spec passes
  `validate --strict`, with the failure surfacing only at archive. It sat
  undetected for six days and recurred twice on one project. Supporting
  that design also required a dedicated `RENAMED` verb with FROM/TO, a
  normalization rule, a duplicate-header error class, and an
  archive algorithm that applies renames first — and the hole shipped
  anyway.

- **Already paying part of this bill**: `check_scenario_coverage.py:104-112`
  records that duplicate change-folder requirement names cannot be
  disambiguated because "the join-key grammar is fixed… occurrence indices
  can't be added" — the script warns and continues. That is the
  names-only choice charging rent today.

- **Scope note**: the change-folder path is lightly exercised (two
  non-archived folders at filing time, both July investing arcs), which is
  why the brief-item arc was sequenced first — it lands on the path every
  arc actually walks. This entry is the follow-on, not the lower-value
  work: it repairs an existing defect on the more durable artifact.

- **Related**: `docs/loom/specs/2026-08-13-brief-item-addressability.md`
  (the arc that ships first and establishes the hybrid convention in the
  brief→plan crossing).
